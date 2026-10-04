# Luna Step 5 runbook — archive factory EmuELEC, then stage dArkOSRE R36 Ultra

**Purpose:** a human-executable procedure for preserving the supplied factory card and preparing a separate dArkOSRE proof card. It does not authorise any command by itself. Every block-device command below is destructive when it writes an `of=/dev/...` target.

## Verified source URLs — checked 2026-09-27

- [dArkOSRE-R36 repository and supported-board table](https://github.com/southoz/dArkOSRE-R36) — declares `GR36S-MB V1.4-2025-07-30 R36 Ultra` as a beta-tested clone and says R36 Ultra works in the latest beta.
- [Official beta notes and direct beta image](https://github.com/southoz/dArkOSRE-R36/wiki/Beta-Testing) — the **04262026** beta explicitly adds R36 Ultra support and lists the GR36S board with GPIO speaker/headphone and OTG switching. Direct image: [Mega](https://mega.nz/file/YjYTQSYb#o6bIQWCN_NRtTsJzkt0PgHvLF23cLVtgcz2K27mvCzI).
- [Official latest stable release](https://github.com/southoz/dArkOSRE-R36/releases/latest) — currently 03082026; useful as a release reference, but the project README says the Ultra is supported in the latest **beta**, so it is not the selected proof image.
- [Official firmware-installation guide](https://github.com/southoz/dArkOSRE-R36/wiki/Firmware-Installation) — documents the first-boot cautions and Linux DTB selection workflow.

The beta page supplies a download link but no published checksum. Compute and retain a local SHA-256 after downloading; that detects later local corruption but cannot authenticate the download against a maintainer-provided digest.

## Non-negotiable safety rules

1. The factory EmuELEC card is **read-only source media**. Never use it as a `dd of=` target.
2. Never copy a command containing `/dev/sdX` literally. Replace it only after checking the exact whole-disk device, size, model, serial, and mountpoints.
3. Keep the factory card and experimental card physically apart. Label the latter `TEST — ERASE OK`.
4. Do not connect the charger or a second SD card during the proof card's first boot, per the dArkOSRE guide.
5. Stop at every `STOP` marker if the observed device/path differs from the expected one.

## Part A — archive the factory card

### A1. Prepare archive storage

The archive root is fixed as `/data/michael/tanstaafllm/luna-images` (also available inside the repository as the ignored `data` symlink). The collection check found 371 GiB free on `/data` on 2026-09-28; that is sufficient headroom for the compressed factory-card image and candidate downloads. Do not place images in the repository or home directory.


```bash
ARCHIVE=/data/michael/tanstaafllm/luna-images/golden
mkdir -p "$ARCHIVE"
df -h "$ARCHIVE"
command -v zstd sha256sum lsblk
```

**STOP:** do not proceed if `zstd` is absent or free space is plainly inadequate. Do not store the archive in the Git repository.

### A2. Identify the factory card, then write down the actual disk name

Insert **only the factory EmuELEC card**. Run:

```bash
lsblk -d -o NAME,SIZE,MODEL,SERIAL,TRAN,RM
lsblk -o NAME,SIZE,FSTYPE,LABEL,UUID,MOUNTPOINTS
```

Record the whole-disk name, for example `/dev/sde`, and every mounted partition below it. Confirm it matches the factory card’s expected capacity and labels. Set a shell variable only after that human check:

```bash
SOURCE=/dev/sdX       # replace sdX with the confirmed factory whole disk
```

**STOP:** if any other removable disk makes the choice ambiguous, unplug it and repeat the two commands. Do not infer the source from a stale `/dev/sdX` name.

### A3. Unmount the factory card’s mounted partitions

Use the explicit partitions printed by `lsblk`, for example:

```bash
sudo umount /dev/sdX1
sudo umount /dev/sdX2
sudo umount /dev/sdX3
lsblk -o NAME,MOUNTPOINTS "$SOURCE"
```

The final command must show empty mountpoints for every partition of `SOURCE`.

### A4. Capture a manifest and create the compressed block image

```bash
STAMP=$(date +%Y%m%d_%H%M%S)
MANIFEST="$ARCHIVE/factory-emuelec_${STAMP}.lsblk.txt"
IMAGE="$ARCHIVE/r36-ultra-factory-emuelec_${STAMP}.img.zst"

lsblk -o NAME,SIZE,MODEL,SERIAL,TRAN,RM,FSTYPE,LABEL,UUID,MOUNTPOINTS \
  | tee "$MANIFEST"

sudo dd if="$SOURCE" bs=4M iflag=fullblock status=progress \
  | zstd -T0 -6 -o "$IMAGE"
```

This reads the entire factory card and writes only the archive file. Let it finish; interrupting it produces an unusable image.

### A5. Verify and freeze the archive

```bash
zstd -t "$IMAGE"
sha256sum "$IMAGE" | tee "$IMAGE.sha256"
sha256sum -c "$IMAGE.sha256"
ls -lh "$IMAGE" "$IMAGE.sha256" "$MANIFEST"
```

Record the archive path, SHA-256, and factory-card serial in your notes. Only after all three checks pass, remove the factory card and set it aside. **Do not restore this image now.**

## Part B — download and verify the dArkOSRE candidate

### B1. Download without confusing it with the factory archive

Create a separate immutable-download area, download the official beta URL above, and keep its original archive unchanged:

```bash
CANDIDATES=/data/michael/tanstaafllm/luna-images/darkosre/original
mkdir -p "$CANDIDATES"
cd "$CANDIDATES"
# Download the linked 04262026 beta in your browser, then place it here unchanged.
sha256sum * | tee SHA256SUMS.local.txt
ls -lh
```

Record the source URL, retrieval date, original filename, and the local SHA-256. The local hash is a record, not an official verification because the project has not published a beta digest.

### B2. Extract and inspect before writing anything

Use a separate working directory, not the download directory:

```bash
WORK=/data/michael/tanstaafllm/luna-images/darkosre/working/04262026
mkdir -p "$WORK"
# Replace <download-file> with the original archive name.
7z l "$CANDIDATES/<download-file>"
7z x "$CANDIDATES/<download-file>" -o"$WORK"
find "$WORK" -maxdepth 2 -type f -printf '%P %s bytes\n'
```

**STOP:** identify the extracted `.img` explicitly. If extraction produces unexpected files or no image, do not flash it.

## Part C — write only the disposable proof card

### C1. Positively identify the disposable target

Remove the factory card. Insert **only** the disposable card.

```bash
lsblk -d -o NAME,SIZE,MODEL,SERIAL,TRAN,RM
lsblk -o NAME,SIZE,FSTYPE,LABEL,UUID,MOUNTPOINTS
```

Write the exact target disk name on paper, compare its capacity/model to the physical test card, and set it only after that comparison:

```bash
TARGET=/dev/sdY       # replace sdY with the confirmed disposable whole disk
IMAGE_FILE="$WORK/<extracted-image>.img"
```

**STOP:** `TARGET` must not equal the recorded factory `SOURCE`, any internal disk, or a partition such as `/dev/sdY1`.

### C2. Unmount the target and flash

Unmount every explicit target partition shown by `lsblk`, then recheck it:

```bash
sudo umount /dev/sdY1
sudo umount /dev/sdY2
lsblk -o NAME,MOUNTPOINTS "$TARGET"
```

Only when all target mountpoints are empty:

```bash
sudo dd if="$IMAGE_FILE" of="$TARGET" bs=4M status=progress conv=fsync
sync
```

`dd` overwrites the **entire disposable card**. Do not run a fallback command, resize partitions, or copy the factory DTB at this point.

### C3. Select the image-supplied R36 Ultra DTBs on Linux

Reinsert the freshly written disposable card if the desktop does not mount it automatically. Locate the BOOT mountpoint and the actual Ultra directory inside that image:

```bash
findmnt -rn -S /dev/sdY1 -o TARGET
# Assign the displayed BOOT mountpoint, for example:
BOOT=/run/media/michael/BOOT
find "$BOOT/dtb" -maxdepth 3 -type d -iname '*GR36*' -print
find "$BOOT/dtb" -maxdepth 3 -type d -iname '*Ultra*' -print
```

The official guide says to delete root-level `*.dtb` files and copy the files from the correct device directory to the root of BOOT. For this board, use **only** the path present in the beta image that matches `GR36S-MB V1.4-2025-07-30 R36 Ultra`; do not guess a Panel 8/9 path and do not use the EmuELEC DTB.

After identifying that exact directory, preserve the image defaults and apply the official method:

```bash
MODEL_DTB_DIR="$BOOT/dtb/clone/<exact GR36S-MB V1.4-2025-07-30 R36 Ultra directory>"
mkdir -p "$BOOT/dtb-before-selection"
cp -a "$BOOT"/*.dtb "$BOOT/dtb-before-selection/"
rm -f "$BOOT"/*.dtb
cp -a "$MODEL_DTB_DIR"/*.dtb "$BOOT/"
sync
find "$BOOT" -maxdepth 1 -type f -name '*.dtb' -printf '%f %s bytes\n'
```

**STOP:** if no matching `GR36S`/`Ultra` directory exists, do not choose another model. Record the directory listing; this is a candidate-image failure, not a reason to substitute the factory DTB.

### C4. First boot and narrow proof

1. Safely unmount/eject the disposable card.
2. Ensure the handheld has no charger and no second SD card inserted.
3. Insert the disposable card and power on; the official guide says first boot can take 2–3 minutes.
4. Record only: visible boot/display, built-in controls, presence of internal Wi-Fi/SSID list, and whether SSH becomes reachable. Do not join Wi-Fi or install anything yet.
5. If the screen remains blank after the documented wait, power off, retain the card as evidence, and return it to Termidor. Do not touch the factory card.

## Completion record

Record: factory image path and SHA-256; source-card serial; beta URL and local SHA-256; disposable-card serial; selected in-image DTB path; and each first-boot result. A screen/controls/Wi-Fi/SSH failure is useful evidence and is not a reason to rewrite the factory reference.

### Download record — 2026-09-28

The official beta was retrieved unchanged as `dArkOSRE_R36_trixie_04262026.7z` in `/data/michael/tanstaafllm/luna-images/darkosre/original/` (3,939,259,438 bytes). Its locally computed SHA-256 is:

```
cbeff6e022a958060379894621ff4f84a656ec10a98715b1b2584a270e8cef4d
```

The official beta notes provide no maintainer checksum. This hash detects later local corruption only; it is not independent authentication of the download. A read-only `7z t` test completed with `Everything is Ok` (8,301,576,192-byte uncompressed payload). No archive extraction, SD-card read/write, or device boot was performed.
