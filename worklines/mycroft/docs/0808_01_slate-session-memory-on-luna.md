# Slate session memory on Luna (plan step 8.8)

**Date:** 2026-10-28
**Slot:** arranged with Mannie on Luna, Luna's operator. Mannie stopped for the slot, and the user gave the go.
**Root:** the new Arch Linux ARM root.
**Harness:** `test/mycroft/test_luna_footprint.py::test_luna_8_8_slate_session`, which runs `test/mycroft/slate_session_probe.py` on Luna. The probe reads `/proc` and Wyoh's status file and changes nothing. It measures the real session: Wyoh's daemon with the resident Kroko it started, and no second model.
**Evidence:** `results/mycroft/luna-footprint/20261028T222617Z/step-8-8-slate-session.json`

## Result, session at rest (Wyoh's session, Slate preloaded and hidden, Kroko resident and idle)

| Measure | Value |
| --- | --- |
| MemTotal | 983.1 MiB |
| MemAvailable over 180 s | **514.8–525.2 MiB** |
| Kroko provider RSS | 162.6 MiB (VmHWM 165.5 MiB) |
| Swap configured on the new root | 491.5 MiB |
| Provider started | 18.9 s after boot, preloaded by Wyoh at session start |

During a dictation, the provider grows by ~20 MiB (172 MiB measured in step 9.8, `0908_01`). Mannie needs ~180 MiB when it runs. Together, that still leaves ~300 MiB available.

## Not measured: memory during a dictation in the Slate

The user dictated during two sampling windows, but the probe never saw a "listening" state in `/run/wyoh/gamepad.json`. So the probe reads the wrong indicator, or L2 from the desktop does not update that field. This is a probe defect, not a dictation failure: the user confirmed that dictation works. The second run was stopped by the user before it saved anything.

## Harness fix on the way

`_reboot_and_settle()` crashed when an SSH probe timed out while Luna was booting. It now treats the timeout as "still booting" and retries.

## Decision

The user, 2026-10-28: "Ok, we'll say it's good. It will hold." **8.8 accepted** on this evidence.
