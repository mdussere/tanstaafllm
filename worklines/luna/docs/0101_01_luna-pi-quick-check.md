# Luna Pi quick check

> **Freshness:** 🟡 historical · **Written:** 2026-09-27 · **Checked:** 2026-10-31 · **Step:** luna 1.1 ✅

**Status:** completed<br>
**Question answered:** Is `luna-pi` suitable for the first graphical experiments, and does it have Bluetooth?

## Observed facts

- Raspberry Pi 4 Model B Rev 1.4; Debian GNU/Linux 13.7 (`trixie`), arm64.
- Four ARMv8 CPU entries were reported; installed memory is about 8 GiB (7,995,120 KiB reported by the kernel).
- Storage is a 14.4 GiB microSD device with a 13.9 GiB ext4 root filesystem and 2 GiB zram swap.
- DRM is present (`card0`, `card1`, and `renderD128`); the default target is graphical and Labwc is installed.
- BlueZ and `bluetooth.service` are installed and active. The onboard adapter exists but is `off-blocked`; `bluetoothctl power on` failed. No external device was paired.

## Result

The Pi is suitable for a headless graphical experiment. Its 8 GiB memory makes it a development/reference platform only, not evidence of 1-GiB-class Luna fit. Bluetooth hardware is present, but its radio must be unblocked before it can be used.
