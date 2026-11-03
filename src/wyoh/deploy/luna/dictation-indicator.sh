#!/bin/sh
# Dictation indicator (Step 6.14, Adam 2026-11-03: "in front of everything, even
# full screen, clearly visible: an ear or a microphone"). Drives an overlay swaybar
# (sway.conf, bar "dictation"): empty and transparent at rest, a big red mark while
# L1's dictation listens. Luna has no emoji font, so the mark is text.
while :; do
    rec=$(sed -n 's/.*"direct": "\([a-z]*\)".*/\1/p' /run/wyoh/gamepad.json 2>/dev/null)
    case "$rec" in
        listening) echo "◉ MIC  " ;;
        loading|stopping) echo "○ mic…  " ;;
        *) echo "" ;;
    esac
    sleep 0.3
done
