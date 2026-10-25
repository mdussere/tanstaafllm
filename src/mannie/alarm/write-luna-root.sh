#!/usr/bin/env bash
# Write the Arch Linux ARM root image onto Luna's card (plan_mannie.md Step 7.3).
# USER-RUN, as root, on the desk host, with the card in a USB reader.
#
#   sudo src/mannie/alarm/write-luna-root.sh /dev/sdX <image> <backup dir>
#
# Only the ARCHR_ROOT partition (p2) is replaced. BOOT (p1), LUNA_HOME (p3) and
# STORAGE (p4) are not touched. Before writing, the current ARCHR_ROOT is saved
# with e2image (used blocks only) into <backup dir>, so it can be put back:
#
#   sudo e2image -ra -p <backup dir>/archr-root-<stamp>.e2i /dev/sdX2
#
# The script refuses a non-removable disk, a disk whose partitions are not
# ARCHR / ARCHR_ROOT / LUNA_HOME / STORAGE, a size mismatch, and asks for
# WRITE-LUNA-ROOT to be typed.
set -euo pipefail

DISK=${1:?disk, e.g. /dev/sde}
IMAGE=${2:?image}
BACKUPS=${3:?backup directory}
[ "$(id -u)" = 0 ] || { echo "run as root (sudo)" >&2; exit 1; }
[ -b "$DISK" ] && [ -f "$IMAGE" ] && [ -d "$BACKUPS" ] || { echo "bad arguments" >&2; exit 1; }
[ "$(lsblk -dno RM "$DISK")" = 1 ] || { echo "$DISK is not removable" >&2; exit 1; }
part() { lsblk -lnpo NAME "$DISK" | sed -n "$(( $1 + 1 ))p"; }
for n in 1 2 3 4; do
  want=(x ARCHR ARCHR_ROOT LUNA_HOME STORAGE)
  got=$(lsblk -no LABEL "$(part $n)")
  [ "$got" = "${want[$n]}" ] || { echo "partition $n is '$got', expected ${want[$n]}" >&2; exit 1; }
done
ROOTPART=$(part 2)
[ "$(blockdev --getsize64 "$ROOTPART")" = "$(stat -c %s "$IMAGE")" ] || { echo "image size differs from $ROOTPART" >&2; exit 1; }
[ "$(e2label "$IMAGE")" = ARCHR_ROOT ] || { echo "image label is not ARCHR_ROOT" >&2; exit 1; }
e2fsck -fn "$IMAGE" >/dev/null

lsblk -o NAME,SIZE,LABEL,MOUNTPOINTS "$DISK"
echo "About to replace $ROOTPART (ARCHR_ROOT) with $IMAGE."
read -r -p "Type WRITE-LUNA-ROOT to continue: " answer
[ "$answer" = WRITE-LUNA-ROOT ] || { echo "stopped"; exit 1; }

for n in 1 2 3 4; do umount "$(part $n)" 2>/dev/null || true; done
# backup-luna-card.sh leaves the card kernel read-only until it is unplugged;
# make only the disk and ARCHR_ROOT writable again (BOOT, LUNA_HOME, STORAGE stay read-only).
blockdev --setrw "$DISK" "$ROOTPART"
STAMP=$(date +%Y%m%d_%H%M%S)
BACKUP=$BACKUPS/archr-root-$STAMP.e2i
echo "== backup of the current ARCHR_ROOT: $BACKUP"
e2fsck -fn "$ROOTPART" > "$BACKUP.e2fsck-before.txt" 2>&1 || true
e2image -ra -p "$ROOTPART" "$BACKUP"
e2fsck -fn "$BACKUP" > "$BACKUP.e2fsck.txt" 2>&1
echo "== writing the new root"
e2image -ra -p "$IMAGE" "$ROOTPART"
sync
e2fsck -fn "$ROOTPART"
echo "label: $(e2label "$ROOTPART")"
echo "done. Backup: $BACKUP. Put the card back in Luna and boot."
