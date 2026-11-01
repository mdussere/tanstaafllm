# Luna Pi VNC and Bluetooth revision

> **Freshness:** 🟡 historical · **Written:** 2026-09-27 · **Checked:** 2026-10-31

**Status:** pre-execution decision record<br>
**Question answered:** What is the short first-pass plan for `luna-pi`?

## Decision

The user requested a superficial rather than deep hardware check, with Bluetooth explicitly included. Because the Pi has no physical display, the next setup task is a virtual display accessed through VNC.

## Scope

- Step 1 records only basic Pi facts, Bluetooth state, and graphical-session feasibility.
- Step 2 may install and configure a small virtual-display/VNC environment after its green light.
- The selected display shape and lightweight session should follow verified Luna facts when available; otherwise they are a documented Pi approximation.
- The user has authorised administration of `luna-pi`, but the plan's green-light gates remain in force.

## Guardrails

- Preserve SSH access and write down how to stop or remove the VNC setup.
- Do not call VNC or Pi graphics evidence a substitute for Luna's physical display, controls, or drivers.
- No target connection or change occurred while recording this revision.
