#!/usr/bin/env bash
# Configure the mounted disposable ArchR card to load a French AZERTY map on tty1.
set -euo pipefail

readonly DROPIN_REL=etc/systemd/system/shell.service.d/10-tanstaafllm-azerty.conf
readonly KEYMAP_REL=.config/tanstaafllm/fr.bkeymap
readonly DEFAULT_KEYMAP_SOURCE=/data/michael/tanstaafllm/luna-assets/kbd-keymaps-v2.7.1/keymaps/i386

usage() {
  echo "Usage: sudo $0 [--restore] <mounted-ARCHR_ROOT> <mounted-STORAGE>" >&2
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
[[ ${EUID} -eq 0 && $# -eq 2 ]] || usage

root=${1%/}
storage=${2%/}
keymap_source=${KEYMAP_SOURCE_ROOT:-$DEFAULT_KEYMAP_SOURCE}
dropin="$root/$DROPIN_REL"
keymap="$storage/$KEYMAP_REL"

[[ -d "$root/usr/bin" && -x "$root/usr/bin/busybox" ]] || fail "Not an ArchR root mount: $root"
[[ -d "$storage/.config" ]] || fail "Not an ArchR STORAGE mount: $storage"
grep -aq 'loadkmap' "$root/usr/bin/busybox" || fail "Target BusyBox has no loadkmap applet."

if "$restore"; then
  [[ -f "$dropin" && -f "$keymap" ]] || fail "AZERTY configuration is incomplete or absent."
  rm -f -- "$dropin" "$keymap"
  sync
  echo "Removed the TANSTAAFLLM ArchR AZERTY loader."
  exit 0
fi

[[ ! -e "$dropin" && ! -e "$keymap" ]] || fail "AZERTY configuration already exists; use --restore first."
[[ -f "$keymap_source/azerty/fr.map" ]] || fail "Missing official French map under: $keymap_source"
[[ -f "$keymap_source/include/azerty-layout.inc" ]] || fail "Missing AZERTY map include under: $keymap_source"
[[ -f "$keymap_source/include/linux-with-alt-and-altgr.inc" ]] || fail "Missing Linux map include under: $keymap_source"
[[ -c /dev/tty1 ]] || fail "Surcouf has no usable /dev/tty1 for loadkeys compilation."

mkdir -p "$(dirname "$dropin")" "$(dirname "$keymap")"
tmp_keymap=$(mktemp "${keymap}.tmp.XXXXXX")
tmp_dropin=$(mktemp "${dropin}.tmp.XXXXXX")
trap 'rm -f -- "${tmp_keymap:-}" "${tmp_dropin:-}"' EXIT

LOADKEYS_KEYMAP_PATH="$keymap_source/**" loadkeys --console /dev/tty1 --bkeymap fr > "$tmp_keymap"
grep -aq '^bkeymap' "$tmp_keymap" || fail "Host loadkeys did not emit a BusyBox binary keymap."
printf '%s\n' \
  '[Service]' \
  "ExecStartPre=/bin/sh -c '/usr/bin/busybox loadkmap < /storage/$KEYMAP_REL'" \
  > "$tmp_dropin"

grep -Fqx '[Service]' "$tmp_dropin" || fail "Refusing to install an invalid service drop-in."
grep -Fqx "ExecStartPre=/bin/sh -c '/usr/bin/busybox loadkmap < /storage/$KEYMAP_REL'" "$tmp_dropin" || fail "Refusing to install an invalid loader command."
mv -- "$tmp_keymap" "$keymap"
tmp_keymap=
mv -- "$tmp_dropin" "$dropin"
tmp_dropin=
sync

echo "Configured persistent French AZERTY loading for the ArchR tty1 textmode shell."
echo "Restore later with: sudo $0 --restore $root $storage"
