---
**Status**: 📋 Draft
**Date**: 2026-09-25
**Priority**: High
**Maintained**: Yes
---

# Wyoh — controller-first handheld session layer (workline `wyoh`)

## Overview

Wyoh owns Luna’s controller-first session layer: the layer that presents one foreground surface, bounded overlays, finite directional navigation, and the actions available from the current scene. It exposes a Playwright-like **interaction model**, but its product object model is not a conventional desktop or free-floating windows. It describes and operates a handheld frontend for several consumers (eventually Mike and Mycroft) without visual inference. Development starts from the desktop and `luna-pi` over SSH; Luna hardware is not yet available.

The pre-hardware outcome is an approved implementation path and a testable interface proposal—not a compositor installation or upstream fork. Hardware-specific graphics, gamepad, memory, thermal, and power claims remain provisional until Luna is characterised.

## Workline directory layout

- Plan: `worklines/wyoh/plan_wyoh.md`
- Produced docs: `worklines/wyoh/docs/`
- Scripts: `worklines/wyoh/scripts/` only after an explicit green light

## Goals ✅

- Define Wyoh’s Handheld Interaction Object Model (HIOM), observer views, finite controller actions, and synchronisation semantics.
- Compare the delivered frontend, a native full-screen shell, and compositor bases only as needed for a 1-GB-class handheld.
- Select a cheap pre-hardware proof while preserving a credible Wayland product path.
- Make the eventual Luna selection reproducible rather than speculative.

## Non-goals ❌

- Installing a display stack, modifying Luna, or building/forking a compositor before approval.
- Giving any consumer arbitrary shell or code-evaluation capability.
- Inferring application-internal semantics for arbitrary third-party Wayland clients.
- Building a pointer-driven, free-floating, overlapping-window desktop or treating a keyboard/mouse as the default interaction.
- Voice, ASR, local-model, Codex, launcher, theme, emulator, battery, or GPU implementation work.

## Key decisions / assumptions

- “VM candidates” is understood as **WM candidates**, following the source discussion.
- `luna-pi` is a Raspberry Pi 4B reference target. Luna is an unverified RK3326/Mali-G31-class, roughly 1-GB handheld target.
- The reported target profile matches an R36 Ultra–family unit with a likely EmuELEC/EmulationStation-style controller frontend; this is evidence to verify on arrival, not a hardware fact yet.
- Mannie/Codex develops on the desktop and reaches devices through SSH.
- Wyoh is a desktop automation service, not a socket. A Unix socket may later be an efficient local transport, but the product contract is snapshots, locators, interactions, events, and waits.
- Wyoh supplies consumer-scoped views: Mike may later receive read/interaction capabilities; Mycroft is read-only when it eventually consumes state for context. This does not expand Mycroft v0, which remains context-free.
- Wyoh validates interactions and reports structured state, success, failure, and events. It is not a shell proxy.
- The canonical state is a monotonic Wyoh revision plus events. App-published semantics have their own revision and freshness; Wyoh never treats an asynchronous client snapshot as globally atomic.
- The proposed product order is: bridge the stock controller frontend if it supplies sufficient state/actions; otherwise build one native full-screen HIOM shell; consider a custom compositor only if both paths demonstrably fail. Qtile/labwc-like desktop policy is not the default path.

## Risks / constraints

- Target kernel, DRM/KMS, Panfrost, rotation, and gamepad exposure are unknown. **Mitigation:** use desktop/nested checks only for interface logic and gate product selection on Luna characterisation.
- A 1-GB device cannot absorb an accidental desktop environment. **Mitigation:** measure the entire Wyoh-owned session, not a single process.
- The stock UI may expose only rendered menus and controller input, not an API. **Mitigation:** inventory it before replacement and preserve a safe return path; do not infer semantic state from pixels as a product dependency.
- Wayland clients are opaque beyond compositor metadata, and neither desktop nor client state is stable by default. **Mitigation:** distinguish Wyoh-authoritative state from optional client semantic trees; identify every snapshot/event by source, revision, and freshness; wait on observed predicates rather than sleeps.
- An early fork creates upgrade debt. **Mitigation:** start with an adapter/sidecar and fork only after an upstream limitation is demonstrated.

## 🚦 Green light protocol

- Default: planning and documentation only until you explicitly say **“🟩 go Step N”**.
- The web survey and proposal were explicitly requested pre-plan discovery; no runtime, hardware, or source-code change has been made.
- Every green-lit step records exact upstream versions and measurements where relevant.
- Installing on Luna, forking upstream, exposing an interaction, or broadening Wyoh into a launcher/shell requires an explicitly scoped next step.

## Plan steps (no execution until green light)

### Step 1 — Ratify Wyoh’s controller-first interaction model and product path
**Status**: ⏳ Pending

- [ ] 1.1 Approve, amend, or reject `0000_05_controller-first-handheld-model.md`; retain `0000_04` only for revision/capability/error/wait semantics.
- [ ] 1.2 Confirm that the default product path is stock-front-end bridge → native full-screen shell → custom compositor, in that order.
- [ ] 1.3 Confirm HIOM snapshot fields, navigation graph, finite controller action vocabulary, overlay/confirmation rules, consumer scopes, and transport-independent access policy.
- [ ] 1.4 Acceptance: one approved controller-first boundary and a testable HIOM contract.

### Step 2 — Build the pre-hardware HIOM proof
**Status**: ⏳ Pending

- [ ] 2.1 Create the smallest model/fixture that returns a revisioned HIOM snapshot with one foreground surface, bounded overlays, selected node, navigation graph, and action catalogue.
- [ ] 2.2 Implement only controller-shaped interactions: directional navigation, activate, back, menu, confirm/cancel, and advertised shoulder/trigger/page actions.
- [ ] 2.3 Emit state-change events and support `wait_for` predicates tied to revisions or operation IDs; never use fixed sleeps as correctness synchronisation.
- [ ] 2.4 Acceptance: a fixture snapshots a scene, selects an advertised finite action, waits for its observed result, and proves an unavailable/stale action changes nothing.

### Step 3 — Validate on `luna-pi`
**Status**: ⏳ Pending

- [ ] 3.1 Record board/RAM/OS/kernel/graphics/input facts before interpreting results.
- [ ] 3.2 Run the approved proof if the required session stack is available; measure readiness, steady memory, idle CPU, and action latency.
- [ ] 3.3 Document gaps without extrapolating Pi results to Luna.
- [ ] 3.4 Acceptance: a versioned result separates portable evidence from Pi-only evidence.

### Step 4 — Characterise Luna and choose the production base
**Status**: ⏳ Pending

- [ ] 4.1 Inventory OS, RAM, display mode/rotation, DRM/KMS, Mesa/Panfrost/Vulkan, inputs, and build options.
- [ ] 4.2 Before any flashing or replacement, identify the stock frontend/version, boot path, process/display stack, controller mapping, overlays, launch/return flow, SSH status, and recovery route.
- [ ] 4.3 Run the HIOM fixture where safely possible; compare stock-front-end bridge, native full-screen shell, and custom-compositor cost on memory, action completeness, recovery, ordering, and latency.
- [ ] 4.4 Acceptance: an evidence-backed record chooses a stock bridge, native full-screen shell, custom compositor, or defers.

### Step 5 — Productise only the selected controller-first path
**Status**: ⏳ Pending

- [ ] 5.1 Fork/pin only the selected upstream; retain licence, provenance, and upgrade strategy.
- [ ] 5.2 Implement the approved HIOM, controller mapping, startup, and deterministic recovery.
- [ ] 5.3 Add contract tests and target smoke tests for snapshot, navigation, finite action, overlay confirmation, wait, process exit, malformed/stale request, and restart.
- [ ] 5.4 Acceptance: Luna boots a recoverable controller-first Wyoh session and passes the HIOM contract suite inside its measured budget.

---

## Progress tracking ✅

- ✅ Full discussion reviewed for Wyoh’s mandate and constraints.
- ✅ Upstream survey and requirements/solution proposal recorded.
- ⏳ Step 1 — Ratify controller-first interaction model and product path.
- ⏳ Step 2 — Build the pre-hardware HIOM proof.
- ⏳ Step 3 — Validate on `luna-pi`.
- ⏳ Step 4 — Characterise Luna and choose the production base.
- ⏳ Step 5 — Fork or productise the selected base.

---

## Time tracking (use `date`) ⏱️

```bash
date
```

### Time log

| Timestamp (`date`) | Update |
|---|---|
| 2026-09-25 | Workline opened by explicit user direction. Full discussion reviewed; web-backed survey and requirements proposal recorded. No code, runtime, target, or hardware changes were made. |
| 2026-09-25 | Reframed the draft as a Playwright-like desktop automation model: revisioned snapshots, locators, native/emulated interactors, events, and predicate-based waits. No implementation started. |
| 2026-09-25 | Replaced the conventional-WM assumption with the controller-first HIOM after target-profile research. The likely stock EmuELEC/EmulationStation shell is now the first path to inventory and bridge; no runtime change was made. |

---

## Workline artifacts

- `worklines/wyoh/docs/0000_01_wyoh-mandate.md` — source-discussion decisions and unresolved facts.
- `worklines/wyoh/docs/0000_02_wm-candidate-survey.md` — current upstream survey and selection rationale.
- `worklines/wyoh/docs/0000_03_wyoh-requirements-and-solutions.md` — draft contract, resource envelope, and solution paths.
- `worklines/wyoh/docs/0000_05_controller-first-handheld-model.md` — primary product model: finite controller state, HIOM, and stock-frontend-first decision path.
- `worklines/wyoh/docs/0000_04_desktop-automation-model.md` — transport-independent model for state, locators, interactions, and synchronisation.
- `worklines/professor/docs/0001_01_initial_discussion.md` — complete source discussion.
