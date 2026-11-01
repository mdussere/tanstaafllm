# Card storage reshape — design for Step 6

> **Freshness:** 🟡 historical · **Written:** 2026-10-09 · **Checked:** 2026-10-31 · **Step:** luna 6.1 ✅

**Question:** How should the disposable 58.2 GiB ArchR card be repartitioned so that `/` has room for packages, `/home` exists, and `/storage` holds only bulk data, without losing the working boot, panel, Wi-Fi and SSH setup?

**Status:** design only. Nothing has been changed on the card. Execution requires **🟩 go Step 6**.

**Input:** Wyoh's request `0000_07_note-from-wyoh-image-limits-and-storage-layout.md` (at least 20 GB on `/`, a real `/home`, `/storage` only for large data). Geometry and identifiers below were read over `ssh luna` on 2026-10-04.

## Current card

MBR (dos) partition table, 122,138,624 sectors of 512 bytes (62,534,975,488 bytes); card serial `0x280b75ea` (read from `/sys/block/mmcblk1/device/serial`).

| # | Start | Size | Label / UUID | Mounted | Used |
|---|---|---|---|---|---|
| p1 | 32768 | 524288 (256 MiB) | `ARCHR` / `2900-7A2B`, vfat | `/flash` (ro) | 22 MB |
| p2 | 557056 | 9437184 (4.5 GiB) | `ARCHR_ROOT` / `3cf95927-e0f1-4043-ad1d-fe04cae2f642`, ext4, type `0xda` | `/` | 4.2 GB (97%) |
| p3 | 9994240 | 112144384 (53.5 GiB) | `STORAGE` / `a2bafe90-b2fb-47d9-91d8-f78c3090d63d`, ext4 | `/storage`, `/var/log` | 290 MB |

The first 16 MiB (before p1) hold the bootloader and must not move.

## How ArchR finds its partitions

These points decide what may change:

- U-Boot loads `boot.scr` and `extlinux/extlinux.conf` from the partition it booted (p1). `boot.scr` passes the kernel `boot=LABEL=ARCHR root=LABEL=ARCHR_ROOT disk=LABEL=STORAGE`. Every mount is **by label**, not by partition number. (`boot.scr` also computes a `storagepart` variable as "boot partition + 1", but nothing uses it after the `LABEL=` lines.)
- `/var` is a tmpfs from `var.mount`; `/var/log` is bound onto STORAGE. `/etc/fstab` is empty.
- `/etc` is writable on the read-write root; the earlier read-only claim was wrong (corrected in `0508_05`).
- ArchR's first-boot resizer (`fs-resize.service`) acts only when `/storage/.please_resize_me` exists, and it refuses on an initialised system. It won't interfere.
- `/storage/.config/system.d` is in systemd's `UnitPath`; the 5.8i drop-ins live there.

So the boot path keeps working as long as the three labels stay the same and p1 is untouched, whatever the partition numbers.

## Target layout

| # | Start | Size | Filesystem / label | Mount | Purpose |
|---|---|---|---|---|---|
| p1 | 32768 | 524288 (256 MiB) | vfat `ARCHR`, **unchanged** | `/flash` | kernel, DTBs, `overlays/` (`mipi-panel.dtbo`, `wifi-rk915.dtbo`), `extlinux/` |
| p2 | 557056 | 50331648 (**24 GiB**) | ext4 `ARCHR_ROOT`, grown in place, same UUID | `/` | OS and packages |
| p3 | 50888704 | 16777216 (**8 GiB**) | ext4 `LUNA_HOME` (new) | `/home` | user homes |
| p4 | 67665920 | 54472704 (**~26 GiB**, to the end) | ext4 `STORAGE`, recreated with its **old UUID** | `/storage` | ArchR state, models, data, results |

All starts are 1 MiB aligned. The MBR's four primary slots are all used, which is acceptable here. A GPT would risk the bootloader area and isn't needed.

### Deviations from Wyoh's proposal, and why

- **p1 stays at 256 MiB** instead of 512 MiB. It is 9% used, and leaving it byte-for-byte untouched removes the only real boot risk in this step. A later base-system change can revisit it.
- **`/var` stays a tmpfs in this step.** Making it persistent on ArchR means overriding `var.mount`, which works against the appliance design (Wyoh's L3). It belongs to the base-system decision (see below), not to repartitioning.
- **No new users in this step.** ArchR has no `useradd` and runs everything as root (L2). `/home` is created and mounted, ready for whichever base adds users.

## Procedure (offline, on Termidor, user-run root script)

A single gated script, `worklines/luna/scripts/reshape_archr_card_storage.sh`, to be written and statically tested before execution. Like the previous card scripts, it:

1. **Checks the card's identity:** whole removable disk, exactly 62,534,975,488 bytes, the three labels and UUIDs above, the current partition starts and sizes, and not the system disk. It requires typing `RESHAPE-LUNA-CARD`. (The reader's USB serial is shared by every card, so it isn't used.)
2. **Takes a full checkpoint:** a zstd image of the whole card into `luna-images/archr/checkpoints/`, verified by matching raw and decompressed SHA-256, as in the factory archive. This is the rollback.
3. **Backs up STORAGE at file level:** `tar --xattrs --acls --numeric-owner` of p3 (mounted read-only) plus its SHA-256. About 290 MB, including root's home, iwd profile, SSH host keys and authorized keys, and the 5.8i drop-ins.
4. **Repartitions with `sfdisk`** from an explicit table: p1 identical, p2 same start with a new size, new p3 and p4. Old p3 is discarded only after steps 2 and 3 have verified.
5. **Grows p2:** `e2fsck -f`, then `resize2fs` to fill 24 GiB.
6. **Creates the new filesystems:** `mkfs.ext4 -L LUNA_HOME` on p3, `mkfs.ext4 -L STORAGE -U a2bafe90-b2fb-47d9-91d8-f78c3090d63d` on p4, then restores the tar into p4 and compares the file list and checksums against the backup.
7. **Mounts `/home`:**
   - creates the empty `/home` directory on p2;
   - adds `/storage/.config/system.d/home.mount` (`What=/dev/disk/by-label/LUNA_HOME`, `Where=/home`, `Type=ext4`, `Options=noatime`);
   - adds its `local-fs.target.wants` link.

   This follows the 5.8i pattern, so it survives ArchR rootfs updates and is removed by deleting two files.
8. **Checks offline:** `e2fsck -n` on p2, p3 and p4; `sfdisk -d` matches the target; p1 files byte-identical to before.

## Boot verification on Luna (over SSH, after the user boots it)

- `df` shows `/` at about 24 GiB with roughly 19 GiB free, `/home` at about 8 GiB, and `/storage` at about 26 GiB.
- Labels and UUIDs as in the target table; `/var/log` still bound to STORAGE.
- Wi-Fi rejoins without the console, and `ssh luna` connects with strict host-key checking and the **same** ED25519 key (`SHA256:tKesK+3T…GgE`).
- `mipi-panel.dtbo`, `wifi-rk915.dtbo` and `extlinux.conf` are unchanged; the display works.
- `systemctl --failed` lists nothing new compared with before.

## Rollback

Write the step 2 checkpoint back to the card (`zstd -dc … | dd`). This restores the exact pre-reshape state, including Wi-Fi and SSH.

## Risks

| Risk | Mitigation |
|---|---|
| Wrong device written | identity checks on size, labels, UUIDs and geometry, plus the typed confirmation |
| Power or USB-reader loss during `resize2fs` | the checkpoint image is the rollback; p2 is grown only after the checkpoint verifies |
| Something in ArchR depends on STORAGE being partition 3 | only `LABEL=` mounts were found; if this is wrong, the boot check shows it and the rollback restores the card |
| A full-card image takes time and space | about 62 GB read, mostly empty so it compresses well; `/data` has over 300 GiB free |

## What this step does not decide

Wyoh's note asks Luna to choose between reworking ArchR in place (option 1) and building a conventional Arch Linux ARM or Debian root on ArchR's proven boot path (option 2). This layout serves either one:
- **option 1:** ArchR keeps p2 and gains room immediately;
- **option 2:** a new root filesystem would replace p2's contents, and p3 and p4 carry over.

Persistent `/var`, users with `sudo`, the package source and Mesa/Panfrost belong to that later decision, proposed as a separate step.
