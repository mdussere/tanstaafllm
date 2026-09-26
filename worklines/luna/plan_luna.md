---
**Status**: 📋 Draft
**Date**: 2026-09-25
**Priority**: High
**Maintained**: Yes
---

# Luna — Pi hardware and virtual-display setup (workline `luna`)

## Overview

`luna-pi` is the practical first test machine. We will make a quick inventory, including Bluetooth, then configure a VNC-accessible virtual display because the Pi has no physical display.

The goal is a useful Luna-like development environment, not a deep hardware study or a claim that the Pi is Luna. We will match known Luna-facing choices where they are known—such as display shape, a lightweight graphical session, controller-style input, and the eventual Wyoh direction—and mark everything else as a Pi approximation.

Done means: basic Pi facts are recorded, Bluetooth is checked, a lightweight virtual display is reachable by VNC, and its setup/removal path is documented.

## Workline directory layout

- Plan (this file): `worklines/luna/plan_luna.md`
- Produced docs: `worklines/luna/docs/`
- Scripts: `worklines/luna/scripts/` only when useful

## Goals ✅

- Quickly identify the Pi's board, OS, CPU, RAM, storage, graphics/display support, and Bluetooth state.
- Provide a lightweight VNC virtual display for graphical experiments without a physical monitor.
- Make the Pi environment resemble the intended Luna experience where the evidence supports that choice.

## Non-goals ❌

- A comprehensive benchmark, thermal study, or hardware certification.
- Treating Pi behaviour as proof of Luna compatibility or performance.
- Changing the real Luna, flashing images, or implementing Mycroft, Wyoh, Mike, Adam, or Mannie.

## Key decisions / assumptions

- `luna-pi` is dedicated to TANSTAAFLLM experiments and the user has authorised its administration.
- The Pi has no display; the graphical environment must use a virtual display accessed over VNC.
- Bluetooth presence is an explicit first-pass check.
- Use a small graphical stack and a display profile based on verified Luna facts. Until those facts exist, label the profile as a Pi approximation.

## Risks / constraints

- VNC and a virtual display cannot reproduce Luna's physical screen, controls, battery, or graphics drivers. Record the difference rather than hiding it.
- Remote graphical configuration can make recovery awkward. Keep SSH usable and document how to stop or remove the graphical service.
- Package installation and service configuration are allowed only in the explicitly green-lit setup step.

## 🚦 Green light protocol

- Default: planning and documentation only until you explicitly say **🟩 go Step N**.
- The user has authorised administration of `luna-pi`; that authority applies within a green-lit plan step.
- SSH and read-only inspection start at **🟩 go Step 1**. Installation and VNC configuration start at **🟩 go Step 2**.
- Record material setup choices and results in this workline and the project logbook.

## Plan steps (no execution until green light)

### Step 1 — Quick Pi check
**Status**: ✅ Done

- [x] 1.1 Connected through the existing `luna-pi` SSH entry and recorded basic board, OS, kernel, CPU, RAM, and storage facts.
- [x] 1.2 Checked Bluetooth hardware and service state: the adapter is present but off-blocked and could not power on.
- [x] 1.3 Checked available graphics/display support and the current graphical-session state.
- [x] 1.4 Wrote a short fact sheet with Pi-only findings and the few Luna-facing choices they can inform.
- [x] 1.5 Acceptance: the fact sheet answers whether Bluetooth exists and whether the Pi can host a virtual graphical session.

### Step 2 — Create the VNC virtual display
**Status**: 🧪 In progress — VNC transport works, but fresh screenshot evidence is still a uniform blank frame

- [x] 2.1 Selected the existing Labwc and WayVNC stack; no desktop environment or package installation was added.
- [x] 2.2 Configured a resizable headless virtual output and labelled it a provisional Pi profile.
- [x] 2.3 Configured a user service bound only to loopback; SSH remains the recovery and access path, with start/stop/disable commands documented.
- [x] 2.4 Verified the VNC endpoint from this development machine through a temporary SSH tunnel; it returned `RFB 003.008`.
- [ ] 2.5 Acceptance: run the live pytest VNC capture in `test/luna/`, inspect its saved screenshot, and confirm visual/input behaviour.

### Step 3 — Simple Luna-like smoke check
**Status**: 🧪 In progress — fresh screenshot evidence is blank; visual/input use remains blocked

- [ ] 3.1 Capture and inspect the VNC session's screen shape and input path with the live `test/luna/` diagnostic; the service is intentionally bare and headless.
- [x] 3.2 Recorded host-side Bluetooth: the adapter exists, but its radio is off-blocked and no external device was paired.
- [x] 3.3 Recorded the remaining differences between the Pi environment and real Luna for Mycroft and Wyoh.
- [x] 3.4 The workline states what can now be tried on the Pi and what must wait for Luna.

### Step 4 — Recheck on real Luna when available
**Status**: ⏳ Pending

- [ ] 4.1 Inspect Luna read-only before making any change.
- [ ] 4.2 Replace Pi assumptions with direct Luna facts where they differ.
- [ ] 4.3 Acceptance: later implementation work has a short, direct target baseline.

---

## Progress tracking ✅

- ✅ Step 1 — Quick Pi check.
- 🧪 Step 2 — VNC transport verified; fresh framebuffer remains blank.
- 🧪 Step 3 — Host-side smoke check complete; visible desktop remains blocked.
- ⏳ Step 4 — Recheck on real Luna when available.

---

## Time tracking (use `date`) ⏱️

```bash
date
```

### Time log

| Timestamp (`date`) | Update |
|---|---|
| 2026-09-25 | Workline created; no target access or hardware action performed. |
| 2026-09-25 | Plan simplified by user direction: add Bluetooth to the quick check and make a VNC virtual display the next setup task. No target action performed. |
| 2026-09-25T22:54:51+02:00 | Steps 1–3 green-lit. Step 1 completed: Pi 4B / Debian 13 / 8 GiB baseline recorded; Bluetooth is present but off-blocked. Created a separate user-level, local-only Labwc + WayVNC headless session. Its VNC protocol was verified locally and through a temporary SSH tunnel; graphical viewer/input validation remains open. |
| 2026-09-25 | Added a live pytest VNC screenshot diagnostic under `test/luna/` to resolve the reported black screen with persisted visual evidence. |
| 2026-09-25 | Live pytest VNC screenshot diagnostic ran through fresh SSH tunnels. It correctly fails on the uniform blank framebuffer; visible-session configuration remains open. |

---

## Workline artifacts

- `worklines/luna/docs/0000_01_luna-hardware-discovery-brief.md` — original scope record.
- `worklines/luna/docs/0000_02_vnc-and-bluetooth-revision.md` — current simplified scope and environment decision.
- `worklines/luna/docs/0101_01_luna-pi-quick-check.md` — completed Pi fact sheet and Bluetooth result.
- `worklines/luna/docs/0201_01_vnc-virtual-display.md` — VNC transport, recovery, and visible-desktop status.
- `test/luna/` — live VNC diagnostic, readable scenario, and captured screenshot evidence.
- `worklines/luna/docs/0202_01_vnc-screenshot-diagnostic.md` — persisted visual evidence and current blank-frame block.

## Input affordance amendment — 2026-09-25

The later real-Luna inventory must include physical buttons/sticks and available visible feedback affordances for Mycroft composition input. `luna-pi` remains only a graphical approximation; this creates no Pi or Luna action.
