# Step 4 re-entry — preserved Luna stock-image inventory

> **Freshness:** 🟡 historical · **Written:** 2026-09-27 · **Checked:** 2026-10-31 · **Step:** wyoh 4.5 ✅

**Status:** read-only baseline captured 2026-09-27

Luna is reachable as `root` through the configured SSH key. The preserved card boots **EmuELEC 4.7 Nexus devel** (`20260811180851`), arm64 Linux `5.10.160`, with `LIBREELEC_ARCH=OdroidGoAdvance.aarch64` and `COREELEC_PROJECT=Rockchip`.

The boot command line enables `fbcon=rotate:3`, serial console `ttyFIQ0`, and SSH. `/` is a 1,008 MiB read-only SquashFS loop mount; `/flash` is a read-only 1.2 GiB VFAT partition; `/storage` is a 506 MiB writable ext4 partition; and `/storage/roms` is a 47 GiB writable VFAT partition. This explains the non-classical SD-card layout and makes the current image a useful recovery baseline.

The target reports `MemTotal: 1,000,004 kB`, no swap, four ARM Cortex-A35-class CPU entries, and framebuffer `rockchipdrmfb`. The SSH view exposed neither `/dev/dri` nor `/dev/input/event*`; this is an absence in this observed interface, not proof that the physical display or controls are unavailable. The process name is truncated by Linux to `emulationstatio`; its sampled RSS was 352,472 KiB (about 34% of physical RAM). The stock `sshd` listener was active.

The test did not alter the target. It did not test controller mapping, rendered display, GPU APIs, Sway, boot recovery, or a replacement image. The preserved card should remain the retrogaming recovery path; any experiment belongs on the new card.

Evidence: `results/wyoh/luna-stock-inventory/20260926T230317Z/`; execution: `LUNA_STOCK_LIVE=1 python3 -m pytest -m live test/wyoh/test_luna_stock_inventory.py -q` passed.
