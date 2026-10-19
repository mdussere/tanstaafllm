#!/bin/sh
# swaybar status line: gamepad hints (Steps 5–6), the Wi-Fi network and its
# signal (Step 7, from iwd), and a clock, refreshed every 20 seconds.
while :; do
    wifi=$(/usr/bin/python3 /storage/.local/share/tanstfaafllm/wyoh/wyoh_wifi.py --bar 2>/dev/null)
    printf '%s   %s   %s\n' "Start menu | L1 Slate | Select next | FN+B close" "$wifi" "$(date +%H:%M)"
    sleep 20
done
