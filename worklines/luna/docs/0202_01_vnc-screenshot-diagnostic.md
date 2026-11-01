# VNC screenshot diagnostic

> **Freshness:** 🟡 historical · **Written:** 2026-09-27 · **Checked:** 2026-10-31 · **Step:** luna 2.2 ✅

**Status:** blocked visual-session result<br>
**Question answered:** Does the VNC endpoint render a usable visible desktop?

## Scenario and runner

The readable scenario is `test/luna/vnc_desktop.feature`. The live pytest runner is `test/luna/test_vnc_screenshot.py`, which invokes `test/luna/capture_vnc.py` and persists a PNG plus logs beneath ignored `results/luna/vnc/<timestamp>/`.

## Observed result

- The VNC endpoint answered the RFB protocol through fresh SSH tunnels.
- The first capture was 100% black.
- Later captures were uniform grey or near-black frames; the latest strict live test correctly failed its uniform-frame assertion.
- Therefore the VNC transport is available, but the current headless Labwc session is not a usable visible desktop.

## Current target setup

The user service remains intentionally local-only and recoverable. It runs a headless Labwc session with WayVNC on Pi-local port 5900. Do not call Step 2 or Step 3 complete until a fresh-tunnel screenshot contains a non-uniform visible surface and its input path is checked.
