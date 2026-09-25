# Project logbook

## 2026-09-25

- Created the draft coordinating-workline plan, now `worklines/professor/plan_professor.md`.
- Translated the existing initial-discussion analysis into English and archived its French source in the Professor workline.
- Recorded that the earlier analysis was based on an incomplete extract; the complete 155-message transcript must be reconciled before specialised worklines are initiated.
- No code, hardware configuration, or automated tests were run.

- Revised `worklines/mycroft/plan_mycroft.md` after reviewing the initial discussion and Mycroft handoff. The plan now applies TANSTAAFL through a resource ledger, CPU-first/on-demand runtime, two-candidate limit, and explicit 1 GiB shared-memory/GPU validation gates; no code, model downloads, device changes, or tests were run.
- Opened the explicitly authorised `mycroft` workline for pre-hardware French ASR v0 planning. Its v0 is audio-to-text without context, commands, text-to-speech, or Luna-specific hardware work.

- Opened the explicitly authorised `wyoh` workline for the window-management/compositor boundary. Reviewed the full discussion, surveyed current upstream candidates, and recorded a draft semantic contract, resource envelope, and staged solution paths.
- The recommended pre-hardware path is an upstream Qtile/X11 adapter; permanent Qtile, dwl, or Cagebreak work remains pending user approval and Luna hardware characterisation.
- No code, runtime, target-device configuration, hardware operation, or automated tests were run for Wyoh.

- Reframed Wyoh after user feedback as a Playwright-like desktop automation service rather than a narrow action socket. Added its transport-independent Desktop/Window Object Model (DWOM): revisioned snapshots, locators, native and emulated interactors, events, and predicate-based waits.
- This resolves the stated synchronisation concern by making compositor state authoritative and revisioned while marking application semantic trees as separately-versioned, potentially stale reports. No runtime or hardware changes were made.

- Reframed Wyoh as a controller-first handheld session layer after target-profile research identified a likely R36 Ultra–family EmuELEC/EmulationStation frontend rather than a conventional desktop WM. The active model is now HIOM: one foreground surface, bounded overlays, explicit directional navigation, and a finite action catalogue.

- Renamed the coordinating workline from `general` to `professor` (Professor de la Paz), preserving its plan and artifacts under `worklines/professor/`. Updated repository guidance, principles, plans, README, and references so Professor is responsible for cross-workline coordination and isolation. No implementation or tests were run.
- Superseded the conventional-WM candidate ranking and desktop requirements as product-selection documents. They remain implementation references only; stock-front-end bridge, then native full-screen shell, then custom compositor is the approved draft decision order pending device inventory.
- No hardware, runtime, firmware, or source-code changes were made.
