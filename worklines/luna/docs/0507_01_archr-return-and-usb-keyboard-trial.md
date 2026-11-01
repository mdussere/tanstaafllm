# Return to ArchR with a preserved dArkOS checkpoint and USB-keyboard trial

> **Freshness:** 🟡 historical · **Written:** 2026-10-04 · **Checked:** 2026-10-31 · **Step:** luna 5.7 ✅

**Question:** How do we preserve the corrected dArkOS experiment before replacing the disposable card with ArchR, then test whether a USB keyboard exposes an interruption path?

## Confirmed inputs

- Disposable card: `/dev/sde`, removable USB MassStorageClass, serial
  `000000002964`, 58.2 GiB. Its mounted labels are dArkOS `BOOT`, `ROOTFS`,
  and `EASYROMS`.
- Preserved source image: `/data/michael/tanstaafllm/luna-images/archr/original/ArchR-R36S.aarch64-20260709-clone.img.gz`.
- Selected ArchR SHA-256:
  `3ea0b970595e0086bd7478e0d17acf71adf1368499b45f1bba21ef6ab63660e2`.
  It passed `sha256sum -c LOCAL-SHA256SUMS` and `gzip -t` on 2026-10-02.
- The vendor `SHA256SUMS` also lists an uncollected `original` variant, so
  checking that complete file reports its expected missing-file error. This
  does not affect the independently recorded clone-image checksum.

## User-run root procedure

Run this from the repository after confirming that only the disposable test
card is connected:

```bash
sudo ./worklines/luna/scripts/archive_darkos_and_flash_archr.sh /dev/sde
```

The script shows the target identity, requires the exact phrase
`ERASE-TEST-CARD`, unmounts only partitions under that target, creates and
verifies the compressed dArkOS checkpoint, verifies ArchR again, and only then
writes the whole target. It refuses non-disks, non-removable targets, a
non-USB transport, or any serial other than `000000002964`.

A successful checkpoint contains the dArkOS image, its GR36 720×720 BOOT
correction, and its ROOTFS changes. It stays outside Git.

## Required panel-overlay stage

The write script deliberately writes only the verified base ArchR clone. Unlike
Arch R Flasher, it does not select or generate a panel overlay. Before booting
Luna, return the card to Termidor and use **Arch R Flasher → Overlay → Import
DTB** with `worklines/luna/data/r36-ultra.dtb`. The Flasher installs the result
as `overlays/mipi-panel.dtbo` on the existing ArchR BOOT partition.

Do not reflash, copy the vendor DTB directly, or choose an arbitrary panel.
See `0507_02_archr-flasher-panel-overlay-gap.md` for the evidence and
restricted next action.

## After the overlay is applied

1. Safely eject the card; do not copy the dArkOS DTBs into ArchR.
2. Connect the new USB adapter and keyboard to Luna’s appropriate data/OTG
   path, then boot ArchR.
3. Record only observable input behaviour: whether a keyboard interrupts the
   boot/frontend loop, opens a console, or produces visible key feedback. Do
   not alter ArchR networking or install software until an input route is
   demonstrated.

If ArchR fails, the dArkOS checkpoint can be restored later only after a new
explicit target-identification check. The factory EmuELEc card remains outside
this procedure.
