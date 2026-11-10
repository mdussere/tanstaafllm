#!/bin/sh
# Luna sound defaults (Luna Step 9.3, Adam 2026-11-10).
# Runs on Luna as root: ssh michael@luna 'sudo sh -s -- <mode>' < luna_sound_defaults.sh
#
#   --apply  speaker volume to 255, USB headset to 90/120, card 0's Playback
#            Mux follows the headphone jack (luna-jack-switch.service), and the
#            mixer state is saved so alsa-restore brings it back at boot
#   --undo   remove the service and restore the saved state from before --apply
#
# LUNA_ROOT prefixes the installed paths (tests).
set -eu

readonly R=${LUNA_ROOT:-}
readonly SWITCH="$R/usr/local/bin/luna-jack-switch"
readonly UNIT="$R/etc/systemd/system/luna-jack-switch.service"
readonly STATE="$R/var/lib/alsa/asound.state"
readonly BEFORE="$STATE.before-luna-sound"

write_switch() {
  mkdir -p "$(dirname "$SWITCH")"
  cat > "$SWITCH" <<'SWITCH'
#!/bin/sh
# Follow the headphone jack on card 0 (RK817): HP when plugged, SPK otherwise.
set_mux() {
  if amixer -c0 cget name='Headphones Jack' | grep -q ': values=on'; then
    mux=HP
  else
    mux=SPK
  fi
  amixer -q -c0 cset name='Playback Mux' "$mux"
}
set_mux
[ "${1:-}" = --once ] && exit 0
stdbuf -oL amixer -c0 events | while read -r line; do
  case $line in
    *"Headphones Jack"*) set_mux ;;
  esac
done
SWITCH
  chmod 755 "$SWITCH"
}

write_unit() {
  mkdir -p "$(dirname "$UNIT")"
  cat > "$UNIT" <<'UNIT'
[Unit]
Description=Luna: route card 0 to the speaker or the headphone jack
After=sound.target alsa-restore.service

[Service]
ExecStart=/usr/local/bin/luna-jack-switch
Restart=always
RestartSec=2

[Install]
WantedBy=multi-user.target
UNIT
}

apply() {
  [ -f "$BEFORE" ] || cp -p "$STATE" "$BEFORE"
  write_switch
  write_unit
  [ -n "$R" ] && { echo "applied (test root)"; return; }
  amixer -q -c0 cset name='Master Playback Volume' 255,255
  amixer -q -c0 cset name='Internal Speakers Switch' on
  amixer -q -c Earphones cset name='Headset Playback Volume' 90 2>/dev/null \
    || echo "warning: USB headset not present; its volume was not set"
  "$SWITCH" --once
  systemctl daemon-reload
  systemctl enable --now luna-jack-switch.service
  alsactl store
  echo "applied"
}

undo() {
  [ -z "$R" ] && systemctl disable --now luna-jack-switch.service 2>/dev/null || true
  rm -f "$SWITCH" "$UNIT"
  if [ -f "$BEFORE" ]; then
    cp -p "$BEFORE" "$STATE"
    rm -f "$BEFORE"
    [ -z "$R" ] && alsactl restore
  fi
  [ -z "$R" ] && systemctl daemon-reload
  echo "undone"
}

case ${1:-} in
  --apply) apply ;;
  --undo) undo ;;
  *) echo "usage: $0 --apply|--undo" >&2; exit 64 ;;
esac
