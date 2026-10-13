#!/bin/sh
# swaybar status line: gamepad hints (Steps 5–6) and a clock, refreshed every 20 seconds.
while :; do
    printf '%s   %s\n' "Start menu | L1 Slate | Select next | FN+B close" "$(date +%H:%M)"
    sleep 20
done
