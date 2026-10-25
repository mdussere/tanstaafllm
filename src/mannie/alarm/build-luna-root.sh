#!/usr/bin/env bash
# Build an Arch Linux ARM root filesystem image for Luna (plan_mannie.md Step 7).
#
# Runs on the desk host as an ordinary user: fakeroot records ownership, and
# mke2fs -d writes the ext4 image. Nothing here writes to a card. The image is
# meant for Luna's ARCHR_ROOT partition: ArchR's BOOT partition, kernel 6.12.94
# and initramfs stay, and so do LUNA_HOME and STORAGE.
#
#   build-luna-root.sh <work dir>
#
# Inputs, in <work dir>:
#   dl/ArchLinuxARM-aarch64-latest.tar.gz   official tarball; check it first with
#       gpg --verify ….sig … against archlinuxarm-builder.asc
#   pkg/                                    from: fetch_packages.py --root <base> --out pkg $(grep -v '^#' packages.txt)
# and ArchR's root mounted read-only at $ARCHR_ROOT (default: the udisks mount).
# Output: <work dir>/luna-alarm-root.ext4 and a manifest beside it.
set -euo pipefail
umask 022

WORK=$(realpath "$1")
HERE=$(dirname "$(realpath "$0")")
ARCHR_ROOT=${ARCHR_ROOT:-/run/media/michael/ARCHR_ROOT}
KVER=6.12.94
SIZE_BYTES=${SIZE_BYTES:-25769803776}   # Luna's ARCHR_ROOT partition (24 GiB)
DESK_KEY=${DESK_KEY:-$HOME/.ssh/id_rsa_local.pub}
ROOT=$WORK/root
STATE=$WORK/fakeroot.state
IMAGE=$WORK/luna-alarm-root.ext4

fr() { fakeroot -i "$STATE" -s "$STATE" -- "$@"; }

[ -d "$ARCHR_ROOT/usr/lib/kernel-overlays/base/lib/modules/$KVER" ] || { echo "ArchR root not found at $ARCHR_ROOT" >&2; exit 1; }
rm -rf "$ROOT" "$STATE" "$IMAGE"
mkdir -p "$ROOT"
touch "$STATE"

echo "== 1. Arch Linux ARM base"
fr tar -xpf "$WORK/dl/ArchLinuxARM-aarch64-latest.tar.gz" -C "$ROOT"

echo "== 2. ArchR's kernel modules and firmware (the kernel itself stays on BOOT)"
fr cp -a "$ARCHR_ROOT/usr/lib/kernel-overlays/base/lib/modules/$KVER" "$ROOT/usr/lib/modules/$KVER"
fr chown -R 0:0 "$ROOT/usr/lib/modules/$KVER"
# ArchR's initramfs waits 60 s unless this path exists; point it at the real tree.
fr mkdir -p "$ROOT/usr/lib/kernel-overlays/base/lib/modules"
fr ln -s "../../../../modules/$KVER" "$ROOT/usr/lib/kernel-overlays/base/lib/modules/$KVER"
# Add ArchR's firmware (rk915, …) without replacing linux-firmware's files.
fr cp -an "$ARCHR_ROOT/usr/lib/kernel-overlays/base/lib/firmware/." "$ROOT/usr/lib/firmware/"
fr chown -R 0:0 "$ROOT/usr/lib/firmware"

echo "== 2b. ArchR's Mali GPU stack, kept inactive for the Sway repair (docs/0702_01)"
# Panfrost failed on Luna (Wyoh, 2026-10-11); Sway ran on ArchR's libmali.
# Copied with ArchR's layout under /usr/local/lib/archr-mali; nothing loads it.
MALI=$ROOT/usr/local/lib/archr-mali
fr mkdir -p "$MALI/usr/lib/archr" "$MALI/etc/profile.d"
fr cp -a "$ARCHR_ROOT/usr/lib/mali" "$ARCHR_ROOT/usr/lib/glesonly" "$MALI/usr/lib/"
fr cp -a "$ARCHR_ROOT"/usr/lib/libmali* "$MALI/usr/lib/"
fr cp -a "$ARCHR_ROOT/usr/lib/archr/gpudriver" "$ARCHR_ROOT/usr/lib/archr/functions" "$MALI/usr/lib/archr/"
fr cp -a "$ARCHR_ROOT/etc/profile.d/001-functions" "$MALI/etc/profile.d/"
fr chown -R 0:0 "$MALI"

echo "== 3. Mount points and files ArchR's initramfs and command line expect"
fr mkdir -p "$ROOT/flash" "$ROOT/storage"
fr install -m 644 "$HERE/files/textmode.target" "$ROOT/etc/systemd/system/textmode.target"
fr install -m 644 "$HERE/files/fstab" "$ROOT/etc/fstab"

echo "== 4. Identity, users and SSH"
echo luna | fr tee "$ROOT/etc/hostname" >/dev/null
fr ln -sf ../usr/share/zoneinfo/Europe/Paris "$ROOT/etc/localtime"
fr sed -i -e 's/^#\(en_US.UTF-8 UTF-8\)/\1/' -e 's/^#\(fr_FR.UTF-8 UTF-8\)/\1/' "$ROOT/etc/locale.gen"
echo LANG=en_US.UTF-8 | fr tee "$ROOT/etc/locale.conf" >/dev/null
# Remove Arch Linux ARM's default "alarm" account (uid 1000) and give uid 1000 to
# michael, whose files on LUNA_HOME are already owned by 1000:1000.
fr python3 "$HERE/accounts.py" "$ROOT/etc"
fr rm -rf "$ROOT/home/alarm"
fr install -d -m 700 "$ROOT/root/.ssh"
fr install -m 600 "$DESK_KEY" "$ROOT/root/.ssh/authorized_keys"
fr install -m 644 "$HERE/files/sshd-luna.conf" "$ROOT/etc/ssh/sshd_config.d/10-luna.conf"
fr install -d -m 750 "$ROOT/etc/sudoers.d"
fr install -m 440 "$HERE/files/sudoers-michael" "$ROOT/etc/sudoers.d/10-michael"

echo "== 5. Network: iwd, with the known networks already on STORAGE"
fr install -d "$ROOT/etc/iwd" "$ROOT/etc/systemd/system/iwd.service.d"
fr install -m 644 "$HERE/files/iwd-main.conf" "$ROOT/etc/iwd/main.conf"
fr install -m 644 "$HERE/files/iwd-luna-state.conf" "$ROOT/etc/systemd/system/iwd.service.d/10-luna-state.conf"

# No wired network on Luna: wait-online would only delay the boot.
fr rm -f "$ROOT/etc/systemd/system/network-online.target.wants/systemd-networkd-wait-online.service"

echo "== 5b. Memory, GPU, console, boot journal"
fr install -m 644 "$HERE/files/zram-generator.conf" "$ROOT/etc/systemd/zram-generator.conf"
fr install -m 644 "$HERE/files/mali-gpu-noauto.conf" "$ROOT/etc/modprobe.d/mali-gpu-noauto.conf"
fr install -d "$ROOT/etc/systemd/system/getty@tty1.service.d"
fr install -m 644 "$HERE/files/getty-autologin.conf" "$ROOT/etc/systemd/system/getty@tty1.service.d/10-autologin.conf"
fr install -m 644 "$HERE/files/luna-boot-journal.service" "$ROOT/etc/systemd/system/luna-boot-journal.service"
fr ln -sf ../luna-boot-journal.service "$ROOT/etc/systemd/system/multi-user.target.wants/luna-boot-journal.service"

echo "== 6. Pacman: never replace ArchR's kernel; first-boot packages from the cache"
fr sed -i 's/^#IgnorePkg *=.*/IgnorePkg   = linux-aarch64 linux-aarch64-headers/' "$ROOT/etc/pacman.conf"
fr install -d "$ROOT/var/cache/luna-firstboot"
fr cp "$WORK"/pkg/*.pkg.tar.* "$ROOT/var/cache/luna-firstboot/"
fr cp "$WORK/pkg/luna-firstboot-packages.txt" "$ROOT/var/cache/luna-firstboot/"
fr chown -R 0:0 "$ROOT/var/cache/luna-firstboot"
date +%s | fr tee "$ROOT/var/lib/luna-build-time" >/dev/null
fr install -m 755 "$HERE/files/luna-firstboot" "$ROOT/usr/local/sbin/luna-firstboot"
fr install -m 644 "$HERE/files/luna-firstboot.service" "$ROOT/etc/systemd/system/luna-firstboot.service"
fr ln -sf ../luna-firstboot.service "$ROOT/etc/systemd/system/multi-user.target.wants/luna-firstboot.service"
fr install -m 644 "$HERE/README-luna.md" "$ROOT/etc/luna-README.md"

echo "== 7. ext4 image (label ARCHR_ROOT, as ArchR's boot path expects)"
truncate -s "$SIZE_BYTES" "$IMAGE"
fakeroot -i "$STATE" -- mke2fs -q -t ext4 -L ARCHR_ROOT -d "$ROOT" "$IMAGE"
e2fsck -fn "$IMAGE"
{
  echo "built: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "tarball: $(sha256sum "$WORK/dl/ArchLinuxARM-aarch64-latest.tar.gz")"
  echo "image apparent size: $SIZE_BYTES"
  echo "first-boot packages: $(tr '\n' ' ' < "$WORK/pkg/luna-firstboot-packages.txt")"
} > "$IMAGE.manifest"
echo "done: $IMAGE"
