# Step 3 evidence — luna-pi Sway result

**Status:** passed on the reference board, 2026-09-26

`luna-pi` is a Raspberry Pi 4 Model B Rev 1.4, not Luna. At collection it ran Debian 13.7 (Trixie), arm64 kernel `6.18.50+rpt-rpi-v8`, with `MemTotal: 8,007,400 kB`, four Cortex-A72-class CPU entries, `/dev/dri/card0`, `card1`, and `renderD128`, plus four `/dev/input/event*` nodes. Its user-level Labwc/WayVNC reference session remained active.

The Step 2 fixture ran a dedicated user-local Sway 1.10.1 headless child with the Pixman renderer and one 1280×720 `HEADLESS-1` output. It observed no input devices in that child. The retained live evidence at `results/wyoh/sway-ipc/20260926T113413Z/` records 42.106 ms socket readiness, 20,144 KiB sampled RSS, five CPU ticks over a 250.781 ms idle sample, 0.612 ms workspace-focus event latency, and 7.521 ms child recovery.

This establishes that the fixture and extracted Sway/wlroots pair run and recover on this Pi reference environment. It does not establish physical display, controller, GPU/Panfrost, thermal, battery, or memory-budget behaviour for Luna; it does not compare renderers or production configurations.
