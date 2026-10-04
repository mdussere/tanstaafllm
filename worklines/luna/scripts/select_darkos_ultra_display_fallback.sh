#!/usr/bin/env bash
# Select dArkOSRE's bundled GR36 720x720 fallback on a disposable R36 Ultra
# card. This is experimental: the exact advertised Ultra profile is absent
# from the 04262026 image. It makes a same-partition rollback copy first.
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <mounted-dArkOS-BOOT>" >&2
  exit 64
fi

boot=$1
profile_dir="$boot/dtb/clone/GR36-MB V1.1-20250422"
backup_dir="$boot/tanstaafllm-before-ultra-display"

for required_path in \
  "$boot/boot.ini" \
  "$boot/rg351v-uboot.dtb" \
  "$boot/rk3326-r36s-linux.dtb" \
  "$boot/logo.bmp" \
  "$profile_dir/rg351v-uboot.dtb" \
  "$profile_dir/rk3326-r36s-linux.dtb" \
  "$boot/dtb/logo/logo-720x720.bmp"; do
  [[ -f $required_path ]] || {
    echo "Required file is missing: $required_path" >&2
    exit 66
  }
done

[[ ! -e $backup_dir ]] || {
  echo "Refusing to overwrite existing rollback directory: $backup_dir" >&2
  exit 73
}

mkdir "$backup_dir"
cp "$boot/rg351v-uboot.dtb" "$backup_dir/rg351v-uboot.dtb"
cp "$boot/rk3326-r36s-linux.dtb" "$backup_dir/rk3326-r36s-linux.dtb"
cp "$boot/logo.bmp" "$backup_dir/logo.bmp"

cp "$profile_dir/rg351v-uboot.dtb" "$boot/rg351v-uboot.dtb"
cp "$profile_dir/rk3326-r36s-linux.dtb" "$boot/rk3326-r36s-linux.dtb"
cp "$boot/dtb/logo/logo-720x720.bmp" "$boot/logo.bmp"

cmp --silent "$profile_dir/rg351v-uboot.dtb" "$boot/rg351v-uboot.dtb"
cmp --silent "$profile_dir/rk3326-r36s-linux.dtb" "$boot/rk3326-r36s-linux.dtb"
cmp --silent "$boot/dtb/logo/logo-720x720.bmp" "$boot/logo.bmp"
sync

echo "Installed the bundled GR36 720x720 fallback on this disposable card."
echo "Rollback files: $backup_dir"
