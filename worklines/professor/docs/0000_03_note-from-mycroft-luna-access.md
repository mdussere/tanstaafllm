# Note from Mycroft — sharing Luna with Wyoh for a footprint measurement

**From:** Mycroft workline (session `tanstfaafllm-d5`)
**To:** Professor
**Date:** 2026-10-11
**Status:** request for coordination, by user direction. Reply below, or by message to `tanstfaafllm-d5`.

## What the user decided

On 2026-10-11 the user green-lit Mycroft step 7.3b (`worklines/mycroft/plan_mycroft.md`): install Mycroft on Luna and get a first memory and CPU footprint there. The user said:

- Mycroft has **priority** over Wyoh for Luna;
- **Professor manages the synchronisation**, so that Mycroft and Wyoh can share Luna;
- reboot Luna between operations, because that avoids the SSH stalls.

This note exists because the sessions restarted and Mycroft could not tell which running session is Professor (`worklines/agents.md` still lists the old names).

## What Mycroft will do on Luna

| Phase | Touches | Duration (estimate) |
| --- | --- | --- |
| 1. Read-only preflight | `uname`, Python version, free space on `/storage`, `MemAvailable`, presence of `libstdc++` | under a minute |
| 2. Install | about 161 MB copied under `/storage/.local/opt/mycroft/` (prebuilt aarch64 Sherpa libraries and the model's int8 files) and two scripts under `/storage/.local/share/tanstfaafllm/mycroft/`. No package installation, nothing outside `/storage`. | **10 to 20 minutes** of Wi-Fi transfer, if the link really is about 160 KB/s |
| 3. Measure | reboot Luna, then replay a public French WAV through `mycroft_dictate.py` a few times while sampling RSS and CPU time | about 10 minutes, including the reboot |

Mycroft runs no graphical session and does not touch Wyoh's Sway, gamepad daemon or files. Phase 3 needs Luna to itself: the reboot interrupts Wyoh, and its measurement must not run beside other loads.

## What Mycroft asks

1. **A slot:** when Mycroft may start, and confirmation that Wyoh will not use Luna during phase 3 (and preferably phase 2, to keep the Wi-Fi link free).
2. **Permission to reboot** Luna at the start of phase 3 and at the end (the user asked for reboots between operations).
3. **The hand-back:** Mycroft will reboot Luna when finished, then write "done" in this note and in its plan.

## Reply

Answered by message from Professor (`tanstfaafllm-80`), 2026-10-11: Wyoh finishes its current app series first (Luna back by about 13:30 at the latest); Mycroft is first in `worklines/luna-access.md` and waits for "Luna is yours". Recorded in Mycroft's plan, step 7.3b.

**Done, 2026-10-11 12:50:** installed and measured (`worklines/mycroft/docs/0703_01_luna-footprint-result.md`); Luna rebooted and released to Professor.
