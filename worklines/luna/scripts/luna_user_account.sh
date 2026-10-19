#!/bin/sh
# Add (or remove) the single user account on Luna's ArchR (Step 7.0).
# Runs on Luna as root: ssh luna 'sh -s -- <mode>' < luna_user_account.sh
#
#   --check   read only: what exists, groups and devices, sudo, sshd
#   --apply   add `michael`: passwd, group memberships, shadow, /home/michael
#             with root's SSH key, and a passwordless sudo drop-in for wheel
#   --undo    remove what --apply added, keeping /home/michael
#
# ArchR has no useradd, and /etc/shadow links to /storage/.cache/shadow, so the
# files are edited directly (and ArchR's boot template /usr/cache/shadow);
# their real paths are backed up first, under
# /storage/.local/share/luna-accounts/. LUNA_ROOT prefixes every path (tests).
set -eu

readonly NAME=michael
readonly ID=1000
readonly GROUPS_WANTED="wheel input video audio render"
readonly R=${LUNA_ROOT:-}
readonly SUDOERS="$R/etc/sudoers.d/10-luna-wheel"
readonly HOME_DIR="$R/home/$NAME"
readonly BACKUPS="$R/storage/.local/share/luna-accounts"

fail() { echo "error: $*" >&2; exit 65; }
real() { readlink -f "$1"; }

do_chown() {
  # Tests run unprivileged on a fake root.
  [ -n "$R" ] && return 0
  chown "$@"
}

check() {
  echo "== account"
  grep "^$NAME:" "$R/etc/passwd" || echo "no $NAME in passwd"
  grep "^root:" "$R/etc/passwd"
  echo "== uid/gid $ID in use"
  awk -F: -v id="$ID" '$3 == id' "$R/etc/passwd" "$R/etc/group"
  echo "== files"
  for f in /etc/passwd /etc/group /etc/shadow; do
    ls -l "$R$f"
  done
  echo "== groups"
  for g in $GROUPS_WANTED; do
    grep "^$g:" "$R/etc/group" || echo "missing group $g"
  done
  echo "== shells"
  ls -l "$R/bin/sh" "$R/bin/bash" "$R/usr/bin/bash" 2>&1 || true
  echo "== sudo"
  ls -l "$R/usr/bin/sudo" "$R/usr/bin/visudo" 2>&1 || true
  [ -u "$R/usr/bin/sudo" ] && echo "sudo is setuid" || echo "sudo is not setuid (shim)"
  ls -l "$R/etc/sudoers" "$R/etc/sudoers.d" 2>&1 || true
  [ -f "$SUDOERS" ] && cat "$SUDOERS"
  echo "== sshd"
  grep -iE '^\s*(UsePAM|PermitRootLogin|AuthorizedKeysFile|AllowUsers|PasswordAuthentication)' \
    "$R/etc/ssh/sshd_config" 2>&1 || true
  echo "== devices"
  ls -l "$R/dev/mali0" "$R/dev/dri" "$R/dev/snd" "$R/dev/input" 2>&1 || true
  ls -ld "$R/home" "$HOME_DIR" 2>&1 || true
}

backup() {
  dest="$BACKUPS/$(date +%Y%m%dT%H%M%S)-before-$1"
  [ -e "$dest" ] && fail "backup $dest exists"
  mkdir -p "$dest"
  for f in passwd group shadow; do
    cp -p "$(real "$R/etc/$f")" "$dest/$f"
  done
  echo "backup: $dest"
}

# Add $NAME to the member list of group $1, if not already there.
add_member() {
  file=$(real "$R/etc/group")
  awk -F: -v OFS=: -v g="$1" -v u="$NAME" '
    $1 == g {
      n = split($4, m, ",")
      for (i = 1; i <= n; i++) if (m[i] == u) { print; next }
      $4 = ($4 == "" ? u : $4 "," u)
    }
    { print }' "$file" > "$file.new"
  cat "$file.new" > "$file"
  rm -f "$file.new"
}

# Remove $NAME from every group's member list.
remove_member() {
  file=$(real "$R/etc/group")
  awk -F: -v OFS=: -v u="$NAME" '
    NF >= 4 {
      n = split($4, m, ","); out = ""
      for (i = 1; i <= n; i++) if (m[i] != u) out = (out == "" ? m[i] : out "," m[i])
      $4 = out
    }
    { print }' "$file" > "$file.new"
  cat "$file.new" > "$file"
  rm -f "$file.new"
}

# Delete lines starting with "$NAME:" from file $1, writing through links.
drop_line() {
  file=$(real "$1")
  grep -v "^$NAME:" "$file" > "$file.new" || true
  cat "$file.new" > "$file"
  rm -f "$file.new"
}

apply() {
  [ -z "$R" ] && [ "$(id -u)" != 0 ] && fail "run as root"
  grep -q "^$NAME:" "$R/etc/passwd" && fail "$NAME already exists; --undo first"
  awk -F: -v id="$ID" '$3 == id { found = 1 } END { exit !found }' \
    "$R/etc/passwd" "$R/etc/group" && fail "id $ID already in use"
  shell=/bin/sh
  [ -x "$R/bin/bash" ] || [ -x "$R/usr/bin/bash" ] && shell=/bin/bash
  [ -x "$R$shell" ] || fail "no shell at $shell"

  backup "$mode"
  echo "$NAME:x:$ID:$ID:Michael:/home/$NAME:$shell" >> "$(real "$R/etc/passwd")"
  echo "$NAME:x:$ID:" >> "$(real "$R/etc/group")"
  for g in $GROUPS_WANTED; do
    if grep -q "^$g:" "$R/etc/group"; then
      add_member "$g"
    else
      echo "warning: no group $g, skipped"
    fi
  done
  # "*": no password, but not locked, so OpenSSH still accepts the key.
  days=$(( $(date +%s) / 86400 ))
  echo "$NAME:*:$days:0:99999:7:::" >> "$(real "$R/etc/shadow")"
  # ArchR's usercache-setup rebuilds the shadow file from this template at
  # every boot, keeping only root's line.
  if [ -f "$R/usr/cache/shadow" ]; then
    cp -p "$R/usr/cache/shadow" "$dest/usr-cache-shadow"
    echo "$NAME:*:$days:0:99999:7:::" >> "$R/usr/cache/shadow"
  fi

  mkdir -p "$HOME_DIR/.ssh"
  cp "$R/storage/.ssh/authorized_keys" "$HOME_DIR/.ssh/authorized_keys"
  chmod 700 "$HOME_DIR" "$HOME_DIR/.ssh"
  chmod 600 "$HOME_DIR/.ssh/authorized_keys"
  do_chown -R "$ID:$ID" "$HOME_DIR"

  # ArchR ships a shim that just execs the command; only a setuid sudo elevates.
  if [ -u "$R/usr/bin/sudo" ]; then
    mkdir -p "$(dirname "$SUDOERS")"
    echo '%wheel ALL=(ALL:ALL) NOPASSWD: ALL' > "$SUDOERS"
    chmod 440 "$SUDOERS"
    if [ -z "$R" ] && [ -x /usr/bin/visudo ]; then
      visudo -c -f "$SUDOERS" || { rm -f "$SUDOERS"; fail "sudoers drop-in rejected"; }
    fi
  else
    echo "warning: no setuid sudo (ArchR ships a shim); no sudoers drop-in written"
  fi
  echo "applied"
}

undo() {
  [ -z "$R" ] && [ "$(id -u)" != 0 ] && fail "run as root"
  backup "$mode"
  drop_line "$R/etc/passwd"
  drop_line "$R/etc/shadow"
  [ -f "$R/usr/cache/shadow" ] && drop_line "$R/usr/cache/shadow"
  drop_line "$R/etc/group"
  remove_member
  rm -f "$SUDOERS"
  echo "undone; $HOME_DIR kept"
}

mode=${1:-}
mode=${mode#--}
case ${1:-} in
  --check) check ;;
  --apply) apply ;;
  --undo) undo ;;
  *) echo "usage: $0 --check|--apply|--undo" >&2; exit 64 ;;
esac
