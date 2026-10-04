#!/usr/bin/env bash
# Create the immutable golden archive of the factory EmuELEC card (Step 5.2).
# The card is only read: it is unmounted, marked kernel read-only, imaged once
# while its raw SHA-256 is computed, and the decompressed image is re-hashed.
# The reader serial is shared by every card, so identity is pinned on the
# factory card's exact size and filesystem UUIDs instead.
set -euo pipefail

EXPECTED_SIZE=52428800000
EXPECTED_PARTITIONS='EMUELEC vfat 1108-1231
STORAGE ext4 b101033c-7e9b-4403-be0f-fa3cc86905e4
EEROMS vfat 1B3C-489F'
GOLDEN=/data/michael/tanstaafllm/luna-images/golden
OWNER=michael

if [[ ${EUID} -ne 0 || $# -ne 1 ]]; then
  echo "Usage: sudo $0 <whole-factory-disk>" >&2
  exit 64
fi

source_disk=$1
[[ -b $source_disk ]] || { echo "Not a block device: $source_disk" >&2; exit 66; }
[[ $(lsblk -dn -o TYPE "$source_disk") == disk ]] || {
  echo "Source must be a whole disk, not a partition: $source_disk" >&2
  exit 66
}
[[ $(lsblk -dn -o RM "$source_disk") == 1 ]] || {
  echo "Source is not removable: $source_disk" >&2
  exit 66
}
[[ $(lsblk -bdn -o SIZE "$source_disk") == "$EXPECTED_SIZE" ]] || {
  echo "Unexpected size for $source_disk; not the factory card." >&2
  exit 66
}
[[ $(lsblk -nr -o LABEL,FSTYPE,UUID "$source_disk" | sed '/^ *$/d') == "$EXPECTED_PARTITIONS" ]] || {
  echo "Unexpected partition labels/UUIDs for $source_disk; not the factory card." >&2
  exit 66
}

root_source=$(findmnt -n -o SOURCE /)
[[ $root_source != "$source_disk"* ]] || {
  echo "Refusing to operate on the system-root disk: $source_disk" >&2
  exit 66
}

stamp=$(date +%Y%m%d_%H%M%S)
base="$GOLDEN/r36-ultra-factory-emuelec_${stamp}"
image="$base.img.zst"
manifest="$base.lsblk.txt"
sums="$base.sha256"
raw_sum="$base.raw-sha256.tmp"

install -d -m 755 "$GOLDEN"
[[ ! -e $image && ! -e $manifest && ! -e $sums ]] || {
  echo "Archive name unexpectedly already exists; refusing to overwrite." >&2
  exit 73
}
avail=$(df --output=avail -B1 "$GOLDEN" | tail -1)
(( avail > EXPECTED_SIZE )) || { echo "Insufficient free space in $GOLDEN." >&2; exit 73; }

while read -r partition mountpoint; do
  [[ -z ${mountpoint:-} ]] || umount "$partition"
done < <(lsblk -nrpo NAME,MOUNTPOINT "$source_disk")

if lsblk -nrpo MOUNTPOINT "$source_disk" | grep -q '[^[:space:]]'; then
  echo "A factory-card partition is still mounted; refusing to continue." >&2
  exit 69
fi

# Kernel-level write protection for the rest of this attachment.
for device in $(lsblk -nrpo NAME "$source_disk"); do
  blockdev --setro "$device"
done

{
  lsblk -o NAME,SIZE,TYPE,TRAN,RM,RO,MODEL,SERIAL,LABEL,FSTYPE,UUID "$source_disk"
  echo
  sfdisk -d "$source_disk"
} | tee "$manifest"

echo "Imaging $source_disk -> $image"
dd if="$source_disk" bs=4M iflag=fullblock status=progress \
  | tee >(sha256sum | awk '{print $1}' > "$raw_sum") \
  | zstd -T0 -10 -q -o "$image"
wait $!
[[ -s $raw_sum ]] || { echo "Raw-card checksum was not produced." >&2; exit 70; }

echo "Verifying compressed archive"
zstd -t "$image"
decompressed=$(zstd -dc "$image" | sha256sum | awk '{print $1}')
raw=$(<"$raw_sum")
[[ $raw == "$decompressed" ]] || {
  echo "MISMATCH: raw card $raw != decompressed image $decompressed" >&2
  exit 70
}

{
  echo "$raw  raw-card-and-decompressed-image"
  (cd "$GOLDEN" && sha256sum "$(basename "$image")")
} > "$sums"
mv "$raw_sum" "$base.raw-sha256.verified"
chown "$OWNER": "$image" "$manifest" "$sums" "$base.raw-sha256.verified"
chmod 444 "$image" "$manifest" "$sums" "$base.raw-sha256.verified"

ls -l "$image"
cat "$sums"
echo "Golden archive verified: raw card and decompressed image SHA-256 match."
echo "The card remains kernel read-only until unplugged; remove it and set it aside."
