#!/usr/bin/env bash
# Reversibly add the proposed RK915 Wi-Fi power overlay to a mounted ArchR BOOT.
# It copies wifi-rk915.dtbo into overlays/ and appends it to the single
# FDTOVERLAYS line after mipi-panel.dtbo; nothing else changes. If an earlier
# revision is already installed, only the overlay file is replaced.
set -euo pipefail

readonly CONFIG_REL=extlinux/extlinux.conf
readonly BACKUP_NAME=extlinux.conf.tanstaafllm-before-wifi-overlay
readonly OVERLAY_NAME=wifi-rk915.dtbo
readonly OVERLAY_SHA256=423feb4eb598b3a9fb706ba0a7cd35f7f168e26313d8103e58896670a9e5ca4a
readonly PANEL_LINE='FDTOVERLAYS /overlays/mipi-panel.dtbo'
readonly WIFI_LINE="FDTOVERLAYS /overlays/mipi-panel.dtbo /overlays/$OVERLAY_NAME"

script_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
source_overlay="$script_dir/../data/$OVERLAY_NAME"

usage() {
  echo "Usage: $0 [--restore] <mounted-ArchR-BOOT>" >&2
  exit 64
}

fail() {
  echo "$*" >&2
  exit 65
}

restore=false
if [[ ${1:-} == --restore ]]; then
  restore=true
  shift
fi
[[ $# -eq 1 ]] || usage

boot=${1%/}
config="$boot/$CONFIG_REL"
backup="$boot/extlinux/$BACKUP_NAME"
target_overlay="$boot/overlays/$OVERLAY_NAME"

[[ -d "$boot/extlinux" && -d "$boot/overlays" && -f "$config" ]] || fail "Not an ArchR BOOT mount: $boot"
[[ -w "$config" ]] || fail "Boot configuration is not writable: $config"

if "$restore"; then
  [[ -f "$backup" ]] || fail "No Wi-Fi overlay backup exists: $backup"
  tmp=$(mktemp "${config}.tmp.XXXXXX")
  trap 'rm -f -- "${tmp:-}"' EXIT
  cp -- "$backup" "$tmp"
  mv -- "$tmp" "$config"
  tmp=
  sync
  echo "Restored boot configuration without the Wi-Fi overlay from: $backup"
  echo "The inert $target_overlay file is left in place."
  exit 0
fi

[[ -f "$source_overlay" ]] || fail "Missing source overlay: $source_overlay"
[[ $(sha256sum "$source_overlay" | awk '{print $1}') == "$OVERLAY_SHA256" ]] \
  || fail "Source overlay checksum differs from the reviewed build; refusing."

if [[ -e "$backup" ]]; then
  grep -q "^[[:space:]]*${WIFI_LINE}\$" "$config" \
    || fail "Backup exists but FDTOVERLAYS is not the installed form; refusing."
  [[ -f "$target_overlay" ]] || fail "Backup exists but $target_overlay is missing; refusing."
  tmp=$(mktemp "${target_overlay}.tmp.XXXXXX")
  trap 'rm -f -- "${tmp:-}"' EXIT
  cp -- "$source_overlay" "$tmp"
  [[ $(sha256sum "$tmp" | awk '{print $1}') == "$OVERLAY_SHA256" ]] || fail "Copied overlay does not verify."
  mv -- "$tmp" "$target_overlay"
  tmp=
  sync
  echo "Updated $target_overlay to the current revision; boot configuration unchanged."
  echo "Restore later with: $0 --restore $boot"
  exit 0
fi
[[ -f "$boot/overlays/mipi-panel.dtbo" ]] || fail "Panel overlay is missing; refusing."
grep -q "$OVERLAY_NAME" "$config" && fail "Wi-Fi overlay is already referenced; refusing."
overlay_count=$(grep -c '^[[:space:]]*FDTOVERLAYS[[:space:]]' "$config" || true)
[[ "$overlay_count" == 1 ]] || fail "Expected exactly one FDTOVERLAYS line; found $overlay_count."
grep -q "^[[:space:]]*${PANEL_LINE}\$" "$config" || fail "Unexpected FDTOVERLAYS line; refusing to edit it."

cp -- "$config" "$backup"
cp -- "$source_overlay" "$target_overlay"
[[ $(sha256sum "$target_overlay" | awk '{print $1}') == "$OVERLAY_SHA256" ]] \
  || fail "Copied overlay does not verify."

tmp=$(mktemp "${config}.tmp.XXXXXX")
trap 'rm -f -- "${tmp:-}"' EXIT
awk -v panel="$PANEL_LINE" -v wifi="$WIFI_LINE" '
  $0 ~ "^[[:space:]]*" panel "$" { sub(panel, wifi); print; next }
  { print }
' "$config" > "$tmp"
grep -q "^[[:space:]]*${WIFI_LINE}\$" "$tmp" || fail "Refusing to install an unexpected boot configuration."
[[ $(diff "$config" "$tmp" | grep -c '^[<>]') == 2 ]] || fail "Edit changed more than the FDTOVERLAYS line."
mv -- "$tmp" "$config"
tmp=
sync

echo "Installed $OVERLAY_NAME and added it to FDTOVERLAYS."
echo "Backup: $backup"
echo "Restore later with: $0 --restore $boot"
