# Luna: an Arch Linux ARM root on ArchR's boot path

Built by Mannie (Claude Code) on the desk host. Record: `worklines/mannie/plan_mannie.md`, Step 7, in the TANSTAAFLLM repository. Build script: `src/mannie/alarm/build-luna-root.sh`.

## What comes from where

| Part | Source |
|---|---|
| Boot partition (`LABEL=ARCHR`, mounted read-only on `/flash`): U-Boot script, `KERNEL` 6.12.94 with its built-in initramfs, DTBs, the cell's overlays | ArchR, unchanged |
| This root (`LABEL=ARCHR_ROOT`) | the official `ArchLinuxARM-aarch64-latest` tarball (signature checked), plus the changes below |
| Kernel modules `/usr/lib/modules/6.12.94` (including `rk915`, `mali-bifrost`, `archr-joypad`) and extra firmware | copied from ArchR's `/usr/lib/kernel-overlays/base` |
| `/home` (`LABEL=LUNA_HOME`) and `/storage` (`LABEL=STORAGE`) | the existing partitions, unchanged |

## Changes to the Arch Linux ARM base

- `/usr/lib/kernel-overlays/base/lib/modules/6.12.94` is a relative link to `/usr/lib/modules/6.12.94`. Without it, ArchR's initramfs warns and waits 60 s.
- `/flash` and `/storage` exist: ArchR's initramfs moves those mounts into the root.
- `textmode.target` exists, because the kernel command line asks for it.
- The `alarm` account is removed. `michael` has uid 1000, belongs to the `wheel`, `video`, `audio`, `input` and `render` groups, and has passwordless `sudo` (`/etc/sudoers.d/10-michael`).
- root's password is locked. root logs in over SSH with the desk host's key only.
- SSH uses the host keys on `/storage/.cache/ssh`, so Luna's fingerprint is unchanged. Password login is off.
- iwd uses ArchR's `main.conf` and the known networks on `/storage/.cache/iwd`.
- `pacman` never installs Arch Linux ARM's kernel (`IgnorePkg = linux-aarch64`). The kernel is ArchR's, on the boot partition.
- Hostname `luna`, time zone Europe/Paris, locales `en_US.UTF-8` and `fr_FR.UTF-8`.
- Compressed swap in RAM with `zram-generator` (at most 512 MiB, zstd, priority 100), as ArchR's memory manager did.
- ArchR's `mali-gpu-noauto.conf`: neither GPU driver (`mali_kbase`, `panfrost`) loads by itself.
- tty1 logs `michael` in automatically: the rescue path when the network is down. ArchR gave a root shell there.
- `luna-boot-journal.service` copies each boot's journal to `/storage/.cache/luna-last-boot.journal`, two minutes after boot.

## First boot

`luna-firstboot.service` runs once:
1. It sets the clock forward to the build time if needed.
2. It initialises the pacman keyring.
3. It installs, offline, the packages cached in `/var/cache/luna-firstboot` (`src/mannie/alarm/packages.txt`: `sudo`, `iwd`, `git`, `github-cli`, `tmux`, `python`, everyday tools, and their dependencies).
4. It generates the locales, restores two file capabilities, then enables iwd and sshd.

The log is in `/storage/.cache/luna-firstboot.log`, and the boot journal in `/storage/.cache/luna-firstboot.journal`. Both are readable from a card reader.

## Kept for later

- `/usr/local/lib/archr-mali/` holds ArchR's Mali GPU stack, with ArchR's own layout: `libmali`, the libraries it bind-mounts over Mesa's (`usr/lib/mali`), its GLES-only SDL2 (`usr/lib/glesonly`), and the `gpudriver` script with its functions. Nothing loads it. Panfrost failed on Luna (Wyoh, 2026-10-11), so the Sway repair starts from here.
- Wyoh's and Mycroft's packages are installed (Sway, seatd, foot, grim, fonts, SDL2, `alsa-utils`, …), but no graphical unit is enabled.

## Not done yet

- Wyoh's graphical session. Its units live in `/storage/.config/system.d`, which this root does not read. Luna boots to text mode, and Mannie repairs Sway from Luna over SSH (user, 2026-10-25).
- File capabilities: the desk build cannot keep them. Only `newuidmap` and `newgidmap` have any in the base, and first boot restores both.
