#!/bin/sh
# swaybar status line: key hints and a clock, refreshed every 20 seconds.
while :; do
    printf '%s   %s\n' "Alt+Enter terminal | Alt+d menu | Alt+Shift+q close | Alt+1-4 workspace" "$(date +%H:%M)"
    sleep 20
done
