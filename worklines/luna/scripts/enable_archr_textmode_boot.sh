#!/usr/bin/env bash
# Reversibly boot a mounted ArchR card into its built-in textmode target.
set -euo pipefail

readonly CONFIG_REL=extlinux/extlinux.conf
readonly BACKUP_NAME=extlinux.conf.tanstaafllm-before-textmode
readonly TEXTMODE_ARG=systemd.unit=textmode.target

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

[[ -d "$boot/extlinux" && -f "$config" ]] || fail "Not an ArchR BOOT mount: $boot"
[[ -w "$config" ]] || fail "Boot configuration is not writable: $config"

if "$restore"; then
  [[ -f "$backup" ]] || fail "No textmode backup exists: $backup"
  tmp=$(mktemp "${config}.tmp.XXXXXX")
  trap 'rm -f -- "${tmp:-}"' EXIT
  cp -- "$backup" "$tmp"
  mv -- "$tmp" "$config"
  tmp=
  sync
  echo "Restored graphical ArchR boot configuration from: $backup"
  exit 0
fi

[[ ! -e "$backup" ]] || fail "Backup already exists; use --restore before enabling again."
grep -q '[[:space:]]systemd\.unit=' "$config" && fail "A systemd.unit override already exists; refusing to replace it."
append_count=$(grep -c '^[[:space:]]*APPEND[[:space:]]' "$config" || true)
[[ "$append_count" == 1 ]] || fail "Expected exactly one APPEND line; found $append_count."

cp -- "$config" "$backup"
tmp=$(mktemp "${config}.tmp.XXXXXX")
trap 'rm -f -- "${tmp:-}"' EXIT
awk -v textmode_arg="$TEXTMODE_ARG" '
  /^[[:space:]]*APPEND[[:space:]]/ { print $0 " " textmode_arg; next }
  { print }
' "$config" > "$tmp"
grep -q "^[[:space:]]*APPEND.* ${TEXTMODE_ARG}$" "$tmp" || fail "Refusing to install an unexpected boot configuration."
mv -- "$tmp" "$config"
tmp=
sync

echo "Configured one-card ArchR textmode boot."
echo "Backup: $backup"
echo "Boot Luna for the tty1 root shell; restore later with: $0 --restore $boot"
