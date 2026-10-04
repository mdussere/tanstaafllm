#!/usr/bin/env bash
# Archive the corrected disposable dArkOS card, then flash the base ArchR clone.
# The Arch R Flasher (or its equivalent) must subsequently install the specific
# R36 Ultra panel overlay; this script deliberately does not guess one.
set -euo pipefail

EXPECTED_SERIAL=000000002964
EXPECTED_TRAN=usb
ARCHIVE_ROOT=/data/michael/tanstaafllm/luna-images
ARCHR_DIR="$ARCHIVE_ROOT/archr/original"
ARCHR_IMAGE="$ARCHR_DIR/ArchR-R36S.aarch64-20260709-clone.img.gz"
ARCHR_SUM="$ARCHR_DIR/LOCAL-SHA256SUMS"

if [[ ${EUID} -ne 0 || $# -ne 1 ]]; then
  echo "Usage: sudo $0 <whole-disposable-disk>" >&2
  exit 64
fi

target=$1
[[ -b $target ]] || { echo "Not a block device: $target" >&2; exit 66; }
[[ $(lsblk -dn -o TYPE "$target") == disk ]] || {
  echo "Target must be a whole disk, not a partition: $target" >&2
  exit 66
}
[[ $(lsblk -dn -o RM "$target") == 1 ]] || {
  echo "Target is not removable: $target" >&2
  exit 66
}
[[ $(lsblk -dn -o TRAN "$target") == "$EXPECTED_TRAN" ]] || {
  echo "Unexpected transport for $target" >&2
  exit 66
}
[[ $(lsblk -dn -o SERIAL "$target") == "$EXPECTED_SERIAL" ]] || {
  echo "Unexpected serial for $target; refusing to write." >&2
  exit 66
}
[[ -f $ARCHR_IMAGE && -f $ARCHR_SUM ]] || {
  echo "Required ArchR image or checksum file is missing." >&2
  exit 66
}

root_source=$(findmnt -n -o SOURCE /)
[[ $root_source != "$target"* ]] || {
  echo "Refusing to operate on the system-root disk: $target" >&2
  exit 66
}

lsblk -d -o NAME,SIZE,MODEL,SERIAL,TRAN,RM "$target"
read -r -p 'Archive corrected dArkOS, then erase this TEST card with ArchR? [type ERASE-TEST-CARD] ' answer
[[ $answer == ERASE-TEST-CARD ]] || { echo "Aborted." >&2; exit 65; }

stamp=$(date +%Y%m%d_%H%M%S)
checkpoint_dir="$ARCHIVE_ROOT/darkosre/checkpoints"
snapshot="$checkpoint_dir/luna-r36-ultra-darkosre-720x720_${stamp}.img.zst"
manifest="$checkpoint_dir/luna-r36-ultra-darkosre-720x720_${stamp}.lsblk.txt"

install -d -m 755 "$checkpoint_dir"
[[ ! -e $snapshot && ! -e $manifest ]] || {
  echo "Checkpoint name unexpectedly already exists; refusing to overwrite." >&2
  exit 73
}

while read -r partition mountpoint; do
  [[ -z ${mountpoint:-} ]] || umount "$partition"
done < <(lsblk -nrpo NAME,MOUNTPOINT "$target")

if lsblk -nrpo MOUNTPOINT "$target" | grep -q '[^[:space:]]'; then
  echo "A target partition is still mounted; refusing to continue." >&2
  exit 69
fi

lsblk -o NAME,SIZE,FSTYPE,LABEL,UUID,MOUNTPOINTS "$target" | tee "$manifest"
dd if="$target" bs=4M iflag=fullblock status=progress \
  | zstd -T0 -6 -o "$snapshot"
zstd -t "$snapshot"
sha256sum "$snapshot" | tee "$snapshot.sha256"
sha256sum -c "$snapshot.sha256"

(
  cd "$ARCHR_DIR"
  sha256sum -c "$ARCHR_SUM"
)
gzip -t "$ARCHR_IMAGE"

gzip -dc "$ARCHR_IMAGE" \
  | dd of="$target" bs=4M status=progress conv=fsync
sync

echo "Base ArchR clone write completed: $target"
echo "Preserved corrected dArkOS checkpoint: $snapshot"
echo "Do not boot Luna yet: install the R36 Ultra mipi-panel.dtbo with Arch R Flasher."
echo "Use the Overlay tab and import: worklines/luna/data/r36-ultra.dtb"
