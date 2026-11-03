#!/bin/sh
# swaybar status line: the dictation indicator (6.14), gamepad hints, the Wi-Fi
# network (Step 7, from iwd) and a clock. Refreshed every second for the
# indicator; the Wi-Fi line every 20 seconds.
n=0
while :; do
    if [ $((n % 20)) -eq 0 ]; then
        wifi=$(/usr/bin/python3 /storage/.local/share/tanstfaafllm/wyoh/wyoh_wifi.py --bar 2>/dev/null)
    fi
    rec=$(sed -n 's/.*"direct": "\([a-z]*\)".*/\1/p' /run/wyoh/gamepad.json 2>/dev/null)
    case "$rec" in
        listening) mark="● DICTATION   " ;;
        loading|stopping) mark="○ dictation…   " ;;
        *) mark="" ;;
    esac
    printf '%s%s   %s   %s\n' "$mark" "Start menu | L1 dictate | L2 Slate | FN+B close" "$wifi" "$(date +%H:%M)"
    n=$((n + 1))
    sleep 1
done
