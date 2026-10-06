#!/bin/sh
# swaybar status line: key hints and a clock, refreshed every 20 seconds.
while :; do
    printf '%s   %s\n' "Alt+Enter term | Alt+d menu | Alt+Shift+q close" "$(date +%H:%M)"
    sleep 20
done
