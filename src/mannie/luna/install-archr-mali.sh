#!/bin/sh
# Put ArchR's Mali GPU stack back in place on Luna's Arch Linux ARM root
# (plan_mannie.md Step 7.4). Run as root on Luna. The image keeps it, inactive, in
# /usr/local/lib/archr-mali with ArchR's own layout; this copies it to ArchR's paths.
# Nothing here replaces a pacman-owned file: ArchR's gpudriver bind-mounts
# /usr/lib/mali/* over Mesa's libEGL/libGLESv2/libgbm at run time only.
set -eu
M=/usr/local/lib/archr-mali
install -d /usr/lib/archr
cp -a "$M/usr/lib/mali" "$M/usr/lib/glesonly" /usr/lib/
cp -a "$M"/usr/lib/libmali* /usr/lib/
cp -a "$M/usr/lib/archr/gpudriver" "$M/usr/lib/archr/functions" /usr/lib/archr/
cp -a "$M/etc/profile.d/001-functions" /etc/profile.d/
ldconfig
for f in /usr/lib/mali /usr/lib/glesonly /usr/lib/libmali.so.1.9.0 /usr/lib/archr/gpudriver /etc/profile.d/001-functions; do
  pacman -Qo "$f" >/dev/null 2>&1 && echo "warning: $f is owned by a package" >&2
  ls -ld "$f"
done
