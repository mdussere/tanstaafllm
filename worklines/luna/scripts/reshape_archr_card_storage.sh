#!/usr/bin/env bash
# Luna Step 6: reshape the disposable ArchR card's storage, offline on Termidor.
#
#   p1 ARCHR       256 MiB  untouched (boot, DTBs, overlays, extlinux)
#   p2 ARCHR_ROOT  24 GiB   grown in place, same start and UUID
#   p3 LUNA_HOME   8 GiB    new, mounted at /home by a /storage systemd unit
#   p4 STORAGE     ~26 GiB  recreated with its old UUID, contents restored
#
# Nothing is repartitioned before a full-card checkpoint image and a
# file-level STORAGE backup have both been verified. Roll back by writing the
# checkpoint image back to the card. Design: docs/0601_01_card-storage-reshape-design.md
set -euo pipefail

readonly EXPECTED_BYTES=62534975488
readonly EXPECTED_SECTORS=122138624
readonly EXPECTED_PARTITIONS='ARCHR vfat 2900-7A2B
ARCHR_ROOT ext4 3cf95927-e0f1-4043-ad1d-fe04cae2f642
STORAGE ext4 a2bafe90-b2fb-47d9-91d8-f78c3090d63d'
readonly STORAGE_UUID=a2bafe90-b2fb-47d9-91d8-f78c3090d63d

# Current geometry (start size, 512-byte sectors)
readonly OLD_P1='32768 524288'
readonly OLD_P2='557056 9437184'
readonly OLD_P3='9994240 112144384'

# Target geometry
readonly P1_START=32768    P1_SIZE=524288
readonly P2_START=557056   P2_SIZE=50331648
readonly P3_START=50888704 P3_SIZE=16777216
readonly P4_START=67665920 P4_SIZE=54472704

readonly CHECKPOINTS=/data/michael/tanstaafllm/luna-images/archr/checkpoints
readonly OWNER=michael
readonly ZSTD=/usr/bin/zstd
readonly MKFS_EXT4_FEATURES='^orphan_file'   # match ArchR's own ext4 feature set

if [[ ${EUID} -ne 0 || $# -ne 1 ]]; then
  echo "Usage: sudo $0 <whole-ArchR-card-disk, e.g. /dev/sde>" >&2
  exit 64
fi

disk=$1
fail() { echo "ERROR: $*" >&2; exit 65; }

echo "== 1/8 identity checks"
[[ $disk == /dev/sd[a-z] ]] || fail "expected a /dev/sdX whole disk, got $disk"
[[ -b $disk ]] || fail "not a block device: $disk"
[[ $(lsblk -dn -o TYPE "$disk") == disk ]] || fail "not a whole disk: $disk"
[[ $(lsblk -dn -o RM "$disk") == 1 ]] || fail "not removable: $disk"
[[ $(lsblk -bdn -o SIZE "$disk") == "$EXPECTED_BYTES" ]] || fail "unexpected size for $disk; not the ArchR card"
[[ $(lsblk -nr -o LABEL,FSTYPE,UUID "$disk" | sed '/^ *$/d') == "$EXPECTED_PARTITIONS" ]] \
  || fail "unexpected labels/UUIDs on $disk; not the ArchR card (or already reshaped)"
name=${disk#/dev/}
for spec in "1 $OLD_P1" "2 $OLD_P2" "3 $OLD_P3"; do
  read -r n start size <<<"$spec"
  [[ $(cat "/sys/block/$name/$name$n/start") == "$start" && $(cat "/sys/block/$name/$name$n/size") == "$size" ]] \
    || fail "partition $n geometry differs from the recorded layout"
done
[[ ! -e /sys/block/$name/${name}4 ]] || fail "a fourth partition already exists"
root_source=$(findmnt -n -o SOURCE /)
[[ $root_source != "$disk"* ]] || fail "refusing to touch the system disk"
(( P2_START + P2_SIZE == P3_START && P3_START + P3_SIZE == P4_START && P4_START + P4_SIZE == EXPECTED_SECTORS )) \
  || fail "internal target table is inconsistent"
(( $(df --output=avail -B1 "$(dirname "$CHECKPOINTS")" | tail -1) > EXPECTED_BYTES )) \
  || fail "not enough free space for the checkpoint"

p1=${disk}1 p2=${disk}2 p3=${disk}3 p4=${disk}4
lsblk -o NAME,SIZE,LABEL,FSTYPE,UUID,MOUNTPOINTS "$disk"
read -r -p 'Reshape this ArchR card (checkpoint first)? [type RESHAPE-LUNA-CARD] ' answer
[[ $answer == RESHAPE-LUNA-CARD ]] || { echo "Aborted." >&2; exit 65; }

stamp=$(date +%Y%m%d_%H%M%S)
base="$CHECKPOINTS/luna-archr-before-reshape_${stamp}"
image="$base.img.zst"
storage_tar="$base.storage.tar"
work=$(mktemp -d /run/luna-reshape.XXXXXX)
# Keep the desktop automounter away from the card while it is being reshaped.
udev_rule=/run/udev/rules.d/99-luna-reshape-noautomount.rules
cleanup() {
  for m in "$work"/*; do mountpoint -q "$m" 2>/dev/null && umount "$m"; done
  rmdir "$work"/* "$work" 2>/dev/null || true
  rm -f "$udev_rule"
  udevadm control --reload 2>/dev/null || true
}
trap cleanup EXIT
install -d -m 755 /run/udev/rules.d
echo "KERNEL==\"${name}*\", ENV{UDISKS_IGNORE}=\"1\", ENV{UDISKS_AUTO}=\"0\"" > "$udev_rule"
udevadm control --reload
udevadm trigger --action=change --sysname-match="${name}*"
udevadm settle
mkdir -p "$work/old" "$work/root" "$work/storage" "$CHECKPOINTS"
[[ ! -e $image && ! -e $storage_tar ]] || fail "checkpoint name already exists"

while read -r part mountpoint; do
  [[ -z ${mountpoint:-} ]] || umount "$part"
done < <(lsblk -nrpo NAME,MOUNTPOINT "$disk")
lsblk -nrpo MOUNTPOINT "$disk" | grep -q '[^[:space:]]' && fail "a partition is still mounted"

e2fsck -f -n "$p2" || fail "ARCHR_ROOT is not clean; shut ArchR down properly and retry"
e2fsck -f -n "$p3" || fail "STORAGE is not clean; shut ArchR down properly and retry"
sfdisk -d "$disk" > "$base.sfdisk-before.txt"
dumpe2fs -h "$p3" > "$base.storage-dumpe2fs-before.txt" 2>/dev/null
label_id=$(awk '/^label-id:/ {print $2}' "$base.sfdisk-before.txt")
[[ -n $label_id ]] || fail "could not read the disk label-id"

echo "== 2/8 full-card checkpoint: $image"
raw_sum="$base.raw-sha256"
dd if="$disk" bs=4M iflag=fullblock status=progress \
  | tee >(sha256sum | awk '{print $1}' > "$raw_sum") \
  | "$ZSTD" -T0 -10 -q -o "$image"
wait $!
[[ -s $raw_sum ]] || fail "raw-card checksum was not produced"
"$ZSTD" -t -q "$image"
decompressed=$("$ZSTD" -dc "$image" | sha256sum | awk '{print $1}')
[[ $(<"$raw_sum") == "$decompressed" ]] || fail "checkpoint MISMATCH; card left unchanged"
echo "checkpoint verified: $decompressed"

echo "== 3/8 STORAGE file backup: $storage_tar"
mount -o ro "$p3" "$work/old"
tar --xattrs --xattrs-include='*' --acls --numeric-owner -cpf "$storage_tar" -C "$work/old" .
tar --xattrs --xattrs-include='*' --acls --numeric-owner -df "$storage_tar" -C "$work/old" \
  || fail "STORAGE backup does not match the card; card left unchanged"
umount "$work/old"
sha256sum "$storage_tar" > "$storage_tar.sha256"
p1_before=$(sha256sum < "$p1" | awk '{print $1}')

echo "== 4/8 repartition (old p3 discarded now)"
sfdisk --wipe never --wipe-partitions never --no-reread "$disk" <<EOF
label: dos
label-id: $label_id
unit: sectors

${disk}1 : start=$P1_START, size=$P1_SIZE, type=c, bootable
${disk}2 : start=$P2_START, size=$P2_SIZE, type=da
${disk}3 : start=$P3_START, size=$P3_SIZE, type=83
${disk}4 : start=$P4_START, size=$P4_SIZE, type=83
EOF
blockdev --rereadpt "$disk"
udevadm settle
for spec in "1 $P1_START $P1_SIZE" "2 $P2_START $P2_SIZE" "3 $P3_START $P3_SIZE" "4 $P4_START $P4_SIZE"; do
  read -r n start size <<<"$spec"
  [[ $(cat "/sys/block/$name/$name$n/start") == "$start" && $(cat "/sys/block/$name/$name$n/size") == "$size" ]] \
    || fail "partition $n not at the target geometry; restore the checkpoint"
done
[[ $(sha256sum < "$p1" | awk '{print $1}') == "$p1_before" ]] || fail "boot partition changed; restore the checkpoint"
sfdisk -d "$disk" > "$base.sfdisk-after.txt"

echo "== 5/8 grow ARCHR_ROOT to 24 GiB"
e2fsck -f -p "$p2" || [[ $? -eq 1 ]] || fail "e2fsck failed on ARCHR_ROOT; restore the checkpoint"
resize2fs "$p2"

echo "== 6/8 create LUNA_HOME and STORAGE, restore STORAGE"
mkfs.ext4 -F -q -O "$MKFS_EXT4_FEATURES" -L LUNA_HOME "$p3"
mkfs.ext4 -F -q -O "$MKFS_EXT4_FEATURES" -m 0 -L STORAGE -U "$STORAGE_UUID" "$p4"
udevadm settle
mount "$p4" "$work/storage"
tar --xattrs --xattrs-include='*' --acls --numeric-owner -xpf "$storage_tar" -C "$work/storage"
tar --xattrs --xattrs-include='*' --acls --numeric-owner -df "$storage_tar" -C "$work/storage" \
  || fail "restored STORAGE differs from the backup; restore the checkpoint"

echo "== 7/8 /home mount point and unit"
mount "$p2" "$work/root"
install -d -m 755 "$work/root/home"
umount "$work/root"
unitdir="$work/storage/.config/system.d"
install -d -m 755 "$unitdir/multi-user.target.wants"
cat > "$unitdir/home.mount" <<'EOF'
# TANSTAAFLLM Luna Step 6: mount the LUNA_HOME partition at /home.
# Not part of local-fs.target: on ArchR, systemd-udevd is ordered after
# local-fs.target (via tz-data.service and systemd-tmpfiles-setup), so a
# device-backed mount there deadlocks until its 90 s timeout.
# Remove this file and multi-user.target.wants/home.mount to revert.
[Unit]
Description=Luna home partition
DefaultDependencies=no
After=local-fs.target systemd-udevd.service
Conflicts=umount.target
Before=umount.target multi-user.target

[Mount]
What=/dev/disk/by-label/LUNA_HOME
Where=/home
Type=ext4
Options=noatime

[Install]
WantedBy=multi-user.target
EOF
ln -s ../home.mount "$unitdir/multi-user.target.wants/home.mount"
sync
umount "$work/storage"

echo "== 8/8 offline checks"
e2fsck -f -n "$p2"
e2fsck -f -n "$p3"
e2fsck -f -n "$p4"
lsblk -o NAME,SIZE,LABEL,FSTYPE,UUID "$disk" | tee "$base.lsblk-after.txt"
[[ $(blkid -s LABEL -o value "$p3") == LUNA_HOME && $(blkid -s UUID -o value "$p4") == "$STORAGE_UUID" \
   && $(blkid -s LABEL -o value "$p2") == ARCHR_ROOT && $(blkid -s LABEL -o value "$p1") == ARCHR ]] \
  || fail "labels/UUIDs not as designed"
{
  echo "$decompressed  raw-card-and-decompressed-image"
  (cd "$CHECKPOINTS" && sha256sum "$(basename "$image")")
} > "$base.sha256"
chown "$OWNER": "$base".*
sync

echo "Reshape complete. Checkpoint: $image"
echo "Rollback: $ZSTD -dc $image | sudo dd of=$disk bs=4M status=progress conv=fsync"
echo "Next: boot Luna, then verify over SSH (Step 6.4)."
