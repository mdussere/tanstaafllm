# Card storage reshape — result (Step 6)

**Question:** Did the Step 6 reshape give the ArchR card a 24 GiB root, a mounted `/home` and a separate `/storage`, without losing the boot, panel, Wi-Fi and SSH setup?

**Answer:** yes, after one fix to the `/home` mount unit (below). Verified over SSH on 2026-10-05 after two reboots.

## What was run

The user ran `sudo worklines/luna/scripts/reshape_archr_card_storage.sh /dev/sde` on Termidor on 2026-10-05 (12:41–13:02). Artifacts are in `/data/michael/tanstaafllm/luna-images/archr/checkpoints/`, prefix `luna-archr-before-reshape_20261005_124112`:

| Artifact | Value |
|---|---|
| Full-card checkpoint `.img.zst` | 3,619,966,500 bytes; raw card = decompressed image SHA-256 `b6a5f410e27ed31cc10b9c3f124a68170df4e392f158aa632f044bb6552e0f1d` |
| Compressed file SHA-256 | `2042d9a8ea4d500aa199edac40abbf6e970b9d057879b25332c8abfbd6d0ce0a` |
| STORAGE file backup `.storage.tar` | 282,501,120 bytes, SHA-256 `b1825f9b19c5053ad2a6b36db54cd61e0be661a7a9bb3c70a4b5f30ed6a412c5` |
| Partition tables | `.sfdisk-before.txt`, `.sfdisk-after.txt`; old STORAGE superblock in `.storage-dumpe2fs-before.txt` |

Rollback, if ever needed: `zstd -dc <checkpoint>.img.zst | sudo dd of=/dev/sdX bs=4M status=progress conv=fsync`.

## Result on Luna

| Check | Observed |
|---|---|
| Geometry | p1 32768+524288, p2 557056+50331648, p3 50888704+16777216, p4 67665920+54472704, as designed |
| Labels / UUIDs | `ARCHR` `2900-7A2B`; `ARCHR_ROOT` `3cf95927-e0f1-4043-ad1d-fe04cae2f642` (unchanged); `LUNA_HOME` `27afae0b-7cbb-4e80-b91f-f46b9fde0a6e` (new); `STORAGE` `a2bafe90-b2fb-47d9-91d8-f78c3090d63d` (kept) |
| `/` | 24 GiB, 4.2 GiB used, **20 GiB free** (was 136 MB) |
| `/home` | 7.8 GiB ext4, mounted from `LUNA_HOME` |
| `/storage` | 26 GiB, 278 MB used, contents restored; `/var/log` still bound to it |
| Boot partition | `mipi-panel.dtbo` and `wifi-rk915.dtbo` hashes unchanged (`62449b4b…`, `423feb4e…`); `extlinux.conf` unchanged; display works |
| Wi-Fi | rejoined "Mick wifi home" without the console (saved profile restored with STORAGE) |
| SSH | strict host-key check passed with the same ED25519 key `SHA256:tKesK+3T9te7a1ER0ZP4WY2kbRqrxwcpt/l0TrBIGgE` |
| Boot time | 13.3 s (4.9 s kernel + 8.4 s userspace) after the fix below |

## The one problem: a boot deadlock caused by `/home`

On the first boot after the reshape, `home.mount` failed (`Timed out waiting for device dev-disk-by\x2dlabel-LUNA_HOME.device`, `Dependency failed`). Boot took **1 min 41 s**, with userspace stalled for 90 s.

The cause is ArchR's unit ordering. `systemd-udevd.service` is ordered after ArchR's `tz-data.service`, which is ordered after `systemd-tmpfiles-setup.service`, which is ordered after `local-fs.target`. So udev only starts once `local-fs.target` is reached. The first version of `home.mount` was part of `local-fs.target` and needed udev to announce its partition, so each waited for the other until the 90 s device timeout broke the loop. udevd then started at 96 s and the partition appeared at 101 s, too late. ArchR's own partitions avoid the problem because its initramfs mounts them before systemd starts.

**Fix (applied live over SSH, then folded into the script):** `home.mount` now uses `DefaultDependencies=no`, `After=local-fs.target systemd-udevd.service`, `Before=multi-user.target`, the explicit `umount.target` conflict, and `WantedBy=multi-user.target`. Its wants link moved from `local-fs.target.wants/` to `multi-user.target.wants/` under `/storage/.config/system.d/`. After a reboot, `/home` mounted by itself, no "Timed out waiting" messages remained, and boot took 13.3 s.

Lesson for later work on this image: **anything that must wait for a device cannot be part of `local-fs.target` on ArchR.**

## Script and tests

- `worklines/luna/scripts/reshape_archr_card_storage.sh` now writes the corrected unit. Its unit text is byte-identical to the one running on Luna.
- `test/luna/test_reshape_archr_card_storage_script.py` gains a regression test that keeps `home.mount` out of `local-fs.target`.
- `uv run pytest test/luna`: 28 passed, 1 skipped (the live VNC test).

## Not done in this step

- `/home` is empty and owned by root. ArchR still has only `root` (no `useradd`) and a tmpfs `/var`; users, persistent `/var` and packages belong to Step 7.
- The checkpoint stays outside Git. The old STORAGE tar can be deleted once the new layout has been in use for a while.
