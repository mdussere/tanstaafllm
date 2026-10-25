# An Arch Linux ARM root for Luna, on ArchR's boot path: study and first image

**Step:** 7.1 of `plan_mannie.md` (study), with the first image of 7.3 prepared. **Date:** 2026-10-25. **Author:** Mannie (session tanstfaafllm-d3).
**Request (user, 2026-10-25):** "télécharge Arch Linux ARM … commence à préparer l'image Arch Linux ARM pour Luna … regarde la configuration noyau … travaille un peu en autonomie."
**Status:** the image is built and checked on the desk host. **Nothing has been written to a card.** Writing waits for the user's go and the backup question below.

## 1. How Luna boots today

All of this was read from the card in Termidor's reader, mounted read-only.

| Stage | What it does | Source |
|---|---|---|
| U-Boot `boot.scr` | reads the board's ADC, picks `rk3326-gameconsole-eeclone.dtb`, sets `LABEL=ARCHR` / `ARCHR_ROOT` / `STORAGE`, hands over to `extlinux.conf` | `BOOT/boot.scr` |
| `extlinux.conf` | loads `KERNEL` with the cell's overlays (`mipi-panel.dtbo`, `wifi-rk915.dtbo`); the command line ends in `systemd.unit=textmode.target` | `BOOT/extlinux/extlinux.conf` |
| `KERNEL` | an uncompressed arm64 Image, 6.12.94, with a built-in LZO initramfs | md5 matches `KERNEL.md5` |
| initramfs `/init` (busybox) | resolves the labels, runs `fsck -p`, mounts `ARCHR_ROOT` read-write on `/sysroot`, `BOOT` read-only on `/flash` and `STORAGE` on `/storage`, moves both into the root, then `switch_root /sysroot /usr/lib/systemd/systemd` | ArchR `projects/ArchR/packages/sysutils/busybox/scripts/init` |

The initramfs is generic: it hands over to whatever systemd it finds. It asks only four things of the root:
- `/flash` and `/storage` exist;
- `/usr/lib/systemd/systemd` exists;
- `/usr/lib/kernel-overlays/base/lib/modules/$(uname -r)/` exists (otherwise it warns and waits 60 s);
- the unit named on the command line (`textmode.target`) exists.

## 2. Will Arch Linux ARM run on ArchR's kernel?

**Yes: no blocker was found.**

| Check | Result |
|---|---|
| glibc 2.43 (Arch Linux ARM) | needs a far older kernel |
| systemd 262 | needs ≥ 5.10 (≥ 5.14 recommended); Luna runs 6.12.94 |
| Kernel configuration (ArchR commit `2d04170214`, 2026-07-08, matching the 2026-07-09 image) | every option in systemd's README is set: devtmpfs, cgroups, inotify, signalfd, timerfd, epoll, unix, sysfs, proc, fhandle, fanotify, shmem, tmpfs (ACL, xattr), BSG, net/user/pid/ipc/uts namespaces, seccomp filter, cgroup BPF, BPF syscall, autofs, memcg, pids, PSI. Missing: `DMIID` (does not exist on ARM) and the optional `CFS_BANDWIDTH`. `FW_LOADER_USER_HELPER` and `SYSFS_DEPRECATED` are off, as systemd wants |
| Live on Luna | cgroup2, fanotify, every namespace, bpf and seccomp are present. ArchR runs systemd 255 in hybrid cgroup mode; 262 uses cgroup2 only, which the kernel has |
| ext4 | built in; ArchR's own `e2fsck` is 1.47.3, so the image's `orphan_file` feature is understood at boot |
| Modules | 317, uncompressed, built for this kernel; they move as they are |

## 3. What the image is

Built by `src/mannie/alarm/build-luna-root.sh` without root (fakeroot, then `mke2fs -d`). Evidence: `results/mannie/alarm-root/`.

- **Base:** the official `ArchLinuxARM-aarch64-latest.tar.gz` (829 MB, 2026-08-05; good signature from the Arch Linux ARM Build System key `68B3537F39A313B3E574D06777193F152BDBE6A6`; MD5 as published).
- **From ArchR:**
  - the 6.12.94 modules, including `rk915`, `mali-bifrost` and `archr-joypad`, in `/usr/lib/modules`, with a relative link at the kernel-overlays path;
  - the extra firmware, added without replacing `linux-firmware`'s files;
  - `textmode.target`;
  - iwd's `main.conf` (`UseDefaultInterface`, which the rk915 driver needs);
  - the GPU blacklist (`mali-gpu-noauto.conf`).
- **Changed from Arch Linux ARM's defaults:**
  - the `alarm` account is removed, and `michael` gets uid 1000 (its files on `LUNA_HOME` are already 1000:1000), in wheel, video, audio, input and render, with passwordless `sudo`;
  - root's password is locked; root keeps SSH by the desk host's key;
  - SSH accepts keys only and uses the host keys already on `STORAGE`, so Luna's fingerprint does not change;
  - iwd reads the known networks on `STORAGE`, with write access to that directory only (its unit is `ProtectSystem=strict`);
  - `pacman` ignores `linux-aarch64`;
  - `systemd-networkd-wait-online` is removed, because Luna has no wired network;
  - zram swap as ArchR set it (zstd, at most 512 MiB, priority 100);
  - tty1 logs `michael` in automatically, the rescue path; ArchR gave a root shell there;
  - each boot's journal is copied to `STORAGE`.
- **First boot (`luna-firstboot.service`, once):**
  1. moves the clock forward to the build time if needed, so signatures are not "from the future";
  2. initialises the pacman keyring;
  3. installs **offline**, with Luna's own pacman, 21 packages cached on the desk (44 MB, each checked against the database's SHA-256 and its signature): `sudo`, `iwd`, `git`, `tmux`, `less`, `rsync`, `htop`, `python`, `iw`, `usbutils`, `zram-generator` and their dependencies;
  4. generates the locales and restores the two file capabilities the desk build cannot keep (`newuidmap` and `newgidmap`);
  5. starts iwd and zram, and enables sshd.
  Logs: `/storage/.cache/luna-firstboot.log` and `.journal`.
- **Size:** 24 GiB apparent (exactly the `ARCHR_ROOT` partition), 2.2 GB used. `e2fsck -fn` is clean.
- **Tests:** `test/mannie/test_alarm_root.py` (+ `alarm_root.feature`): account edits and the resolver run by default; the image check reads the built image with `debugfs` (label, owners and modes, links, modules and firmware, pacman, SSH, fstab, units, cached packages beside their signatures). All pass.

## 4. What it does not do yet

- **Wyoh's graphical session.** Its units live in `STORAGE/.config/system.d`, which only ArchR reads. The new root boots to text mode with Wi-Fi and SSH. The GPU route has to be chosen with Wyoh:
  - ArchR's Mali stack (`mali_kbase` and `libmali` would have to be carried over);
  - or Mesa with Panfrost (`panfrost.ko` is there, and Mesa comes from `pacman`).
  Wyoh's `wyoh-sway.service` also sets `HOME=/storage` and runs as root.
- **Mycroft** (Kroko in `/storage/.local`) and the audio routing (RK817; the USB-C microphone) are untested on the new root.
- **ArchR's extras** are dropped: EmulationStation, ArchR's own Sway session, `headphones.service`, the battery LED, `archr-hotkey`, the `fancontrol` and `powerstate` services, and others. Each can return if it is missed.

## 5. Risks and how they are covered

| Risk | Cover |
|---|---|
| Boot fails before SSH | tty1 autologin on the screen (a USB keyboard works); `/storage/.cache/luna-firstboot.log` and `luna-last-boot.journal` can be read from the card reader |
| The first boot cannot install the packages (keyring, clock) | the clock guard; the log says which step failed; `/var/lib/luna-firstboot.done` is written only on success, so the next boot retries |
| Wi-Fi does not come up | the same driver and firmware, and iwd's configuration and known networks as ArchR; checked first in the log |
| The root breaks | the write script saves the current `ARCHR_ROOT` with `e2image` before writing; putting it back is one command |

## 6. To write it (7.3, not done)

`sudo src/mannie/alarm/write-luna-root.sh /dev/sdX /data/michael/tanstaafllm/tmp/mannie-alarm/luna-alarm-root.ext4 <backup dir>`

Run by the user. The script:
- refuses a non-removable disk;
- checks the four labels and the exact size;
- asks for `WRITE-LUNA-ROOT` to be typed;
- saves the current `ARCHR_ROOT` (used blocks only);
- writes only `ARCHR_ROOT`, then checks it.

**Open questions for the user:**
- **The backup (answered 2026-10-25):** none exists, and there is only one card. A whole-card backup comes first, with `src/mannie/luna/backup-luna-card.sh` (plan 7.2).
- **Same card or a second card (answered):** the same card, once it is backed up.
