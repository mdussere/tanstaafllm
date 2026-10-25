#!/usr/bin/env bash
# Back up Luna's whole ArchR card before it is rewritten (plan_mannie.md Step 7.2).
# USER-RUN as root on the desk host, card in a USB reader. The card is only read:
# its partitions are unmounted, every device is set kernel read-only, the raw card
# is imaged once while its SHA-256 is computed, and the decompressed image is
# re-hashed. STORAGE and LUNA_HOME are also saved as tar files (read-only mounts,
# numeric owners, ACLs and xattrs kept), to feed the next image without root.
#
#   sudo src/mannie/luna/backup-luna-card.sh /dev/sdX
#
# Identity is pinned on the card's exact size and its four filesystem UUIDs.
set -euo pipefail

EXPECTED_SIZE=62534975488
EXPECTED_PARTITIONS='ARCHR vfat 2900-7A2B
ARCHR_ROOT ext4 3cf95927-e0f1-4043-ad1d-fe04cae2f642
LUNA_HOME ext4 27afae0b-7cbb-4e80-b91f-f46b9fde0a6e
STORAGE ext4 a2bafe90-b2fb-47d9-91d8-f78c3090d63d'
ARCHIVE=/data/michael/tanstaafllm/luna-images/archr
OWNER=michael
PATH=/usr/sbin:/usr/bin:/sbin:/bin

if [[ ${EUID} -ne 0 || $# -ne 1 ]]; then
  echo "Usage: sudo $0 <whole Luna card disk, e.g. /dev/sde>" >&2
  exit 64
fi

source_disk=$1
[[ -b $source_disk ]] || { echo "Not a block device: $source_disk" >&2; exit 66; }
[[ $(lsblk -dn -o TYPE "$source_disk") == disk ]] || {
  echo "Source must be a whole disk, not a partition: $source_disk" >&2
  exit 66
}
[[ $(lsblk -dn -o RM "$source_disk") == 1 ]] || { echo "Source is not removable: $source_disk" >&2; exit 66; }
[[ $(lsblk -bdn -o SIZE "$source_disk") == "$EXPECTED_SIZE" ]] || {
  echo "Unexpected size for $source_disk; not Luna's card." >&2
  exit 66
}
[[ $(lsblk -nr -o LABEL,FSTYPE,UUID "$source_disk" | sed '/^ *$/d') == "$EXPECTED_PARTITIONS" ]] || {
  echo "Unexpected partition labels/UUIDs for $source_disk; not Luna's card." >&2
  exit 66
}
root_source=$(findmnt -n -o SOURCE /)
[[ $root_source != "$source_disk"* ]] || { echo "Refusing to operate on the system-root disk: $source_disk" >&2; exit 66; }

stamp=$(date +%Y%m%d_%H%M%S)
base="$ARCHIVE/luna-archr-before-alarm_${stamp}"
image="$base.img.zst"
manifest="$base.manifest.txt"
sums="$base.sha256"
raw_sum="$base.raw-sha256.tmp"

install -d -m 755 "$ARCHIVE"
[[ ! -e $image && ! -e $manifest && ! -e $sums ]] || { echo "Archive name already exists; refusing to overwrite." >&2; exit 73; }
avail=$(df --output=avail -B1 "$ARCHIVE" | tail -1)
(( avail > EXPECTED_SIZE )) || { echo "Insufficient free space in $ARCHIVE." >&2; exit 73; }

while read -r partition mountpoint; do
  [[ -z ${mountpoint:-} ]] || umount "$partition"
done < <(lsblk -nrpo NAME,MOUNTPOINT "$source_disk")
if lsblk -nrpo MOUNTPOINT "$source_disk" | grep -q '[^[:space:]]'; then
  echo "A card partition is still mounted; refusing to continue." >&2
  exit 69
fi

# Kernel-level write protection for the rest of this attachment.
for device in $(lsblk -nrpo NAME "$source_disk"); do
  blockdev --setro "$device"
done

{
  date -Is
  lsblk -o NAME,SIZE,TYPE,TRAN,RM,RO,MODEL,SERIAL,LABEL,FSTYPE,UUID "$source_disk"
  echo
  sfdisk -d "$source_disk"
  for device in $(lsblk -nrpo NAME,FSTYPE "$source_disk" | awk '$2 == "ext4" {print $1}'); do
    echo
    echo "== $device"
    dumpe2fs -h "$device" 2>/dev/null | grep -E "volume name|UUID|Block count|Free blocks|Inode count|Free inodes|features|Last mount time|Last write time"
  done
} | tee "$manifest"

echo "Imaging $source_disk -> $image"
dd if="$source_disk" bs=4M iflag=fullblock status=progress \
  | tee >(sha256sum | awk '{print $1}' > "$raw_sum") \
  | zstd -T0 -6 -q -o "$image"
wait $!
[[ -s $raw_sum ]] || { echo "Raw-card checksum was not produced." >&2; exit 70; }

echo "Verifying compressed archive"
zstd -t "$image"
decompressed=$(zstd -dc "$image" | sha256sum | awk '{print $1}')
raw=$(<"$raw_sum")
[[ $raw == "$decompressed" ]] || { echo "MISMATCH: raw card $raw != decompressed image $decompressed" >&2; exit 70; }

# File-level copies of the two data partitions, from read-only, no-journal-replay mounts.
mnt=$(mktemp -d)
for label in STORAGE LUNA_HOME; do
  device=$(lsblk -nrpo NAME,LABEL "$source_disk" | awk -v l="$label" '$2 == l {print $1}')
  tarball="$base.$label.tar.zst"
  mount -o ro,noload "$device" "$mnt"
  tar --numeric-owner --acls --xattrs -C "$mnt" -cf - . | zstd -T0 -6 -q -o "$tarball"
  umount "$mnt"
  zstd -t "$tarball"
done
rmdir "$mnt"

{
  echo "$raw  raw-card-and-decompressed-image"
  (cd "$ARCHIVE" && sha256sum "$(basename "$image")" "$(basename "$base").STORAGE.tar.zst" "$(basename "$base").LUNA_HOME.tar.zst")
} > "$sums"
mv "$raw_sum" "$base.raw-sha256.verified"
for f in "$image" "$manifest" "$sums" "$base.raw-sha256.verified" "$base.STORAGE.tar.zst" "$base.LUNA_HOME.tar.zst"; do
  chown "$OWNER": "$f"
  chmod 444 "$f"
done
# The tar files hold Luna's SSH host keys and Wi-Fi passphrases: owner only.
chmod 400 "$base.STORAGE.tar.zst" "$base.LUNA_HOME.tar.zst"

ls -l "$base".*
cat "$sums"
echo "Backup verified: raw card and decompressed image SHA-256 match."
echo "The card stays kernel read-only until it is unplugged."
