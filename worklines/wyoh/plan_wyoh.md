> **Current plan status (2026-09-25): Step 1 is reopened.** The earlier HIOM-only acceptance remains historical evidence but is no longer the active v0 contract. The proposed replacement is unmodified Sway plus existing IPC as Wyoh v0; a thin Wyoh adapter/capability mediator only when Sway cannot safely express a required Luna semantic or operation; extension or fork only on demonstrated need.
>
> The intended human path is instruction through Mycroft to Mike. Mike performs simple offline system actions; Mannie retains development/code/build/test work. Buttons are attention/recovery controls, and Bluetooth keyboard/touchpad use is development/recovery support.
>
> This revision does not authorise implementation. Sway viability, version pinning, memory/graphics/input cost, capability mediation, and any live Mycroft context remain later validation or cross-workline decisions.

---
**Status**: 📋 Draft
**Date**: 2026-09-25
**Priority**: High
**Maintained**: Yes
---

# Wyoh — agent-native handheld workspace (workline `wyoh`)

## Overview

Wyoh owns Luna’s agent-native graphical workspace: the layer that lets Mike inspect and operate graphical session state without pixels as the principal model. The v0 candidate is unmodified Sway plus existing IPC; a separate Wyoh adapter follows only when it must provide a Luna-specific semantic or safely mediate a consumer capability.

The pre-hardware outcome is a ratified Sway-v0 path and a testable, capability-mediated interface proposal—not a compositor installation or upstream fork. Hardware-specific graphics, gamepad, memory, thermal, and power claims remain provisional until Luna is characterised.

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
- Sway's documented use beneath ROCKNIX's EmulationStation session is positive distribution-family evidence for Wyoh v0: a similar handheld stack already treats Sway as technical infrastructure. It does not establish Luna's delivered distribution or compositor; Step 4 inventory decides that.
- Mannie/Codex develops on the desktop and reaches devices through SSH.
- The initial and follow-up discussion records establish the current proposal: unmodified Sway plus its existing IPC as v0; an adapter/capability mediator only on demonstrated need. This reopens Step 1 and does not green-light Step 2.
- Wyoh is a desktop automation service, not a socket. A Unix socket may later be an efficient local transport, but the product contract is snapshots, locators, interactions, events, and waits.
- Wyoh supplies consumer-scoped views: Mike may receive policy-allowed simple actions; Mycroft v0 remains context-free. Any later live Mycroft context needs a separately authorised Mycroft-workline change.
- Wyoh validates interactions and reports structured state, success, failure, and events. It is not a shell proxy.
- The canonical state is a monotonic Wyoh revision plus events. App-published semantics have their own revision and freshness; Wyoh never treats an asynchronous client snapshot as globally atomic.
- The proposed product order is: unmodified Sway IPC → thin Wyoh adapter/capability mediator → Sway IPC extension or fork only if evidence requires it. The stock frontend remains a reference/recovery baseline, not the intended agent-native workspace.
- The prepared development-only MCP follow-on is a Python stdio server launched through `ssh -T luna-pi`, not a port-forward or resident service. It will expose a redacted Sway snapshot and one fixed proof action only; it remains pending an explicit green light.

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

### Step 1 — Ratify Wyoh’s agent-native Sway-v0 contract and product path
**Status**: ✅ Done — ratified 2026-09-26

- [x] 1.1 Historical: recorded `0000_05_controller-first-handheld-model.md` and retained `0000_04` for revision/capability/error/wait semantics.
- [x] 1.2 Historical: recorded the stock-front-end bridge → native full-screen shell → custom-compositor product order.
- [x] 1.3 Historical: froze the HIOM-only contract in `0101_01_hiom_v0_contract.md`.
- [x] 1.4 Historical acceptance: controller-first boundary recorded; superseded as the active v0 contract.
- [x] 1.5 Ratified unmodified Sway plus its existing IPC as the v0 substrate, with no fork or adapter by default.
- [x] 1.6 Ratified the replacement interaction boundary: Sway state/events plus policy-scoped semantic actions; focused keyboard/pointer fallback only when necessary; buttons for attention/recovery; Bluetooth keyboard/touchpad for development/recovery.
- [x] 1.7 Ratified component boundaries: Mike handles simple offline system tasks; Mannie owns development; Mycroft v0 remains context-free until its workline changes.
- [x] 1.8 Acceptance: replacement contract records Sway v0, capability boundary, deferred hardware criteria, and retained role of HIOM in `docs/0101_06_sway-v0-contract.md`.

### Step 2 — Validate the pre-hardware Sway-IPC proof
**Status**: ✅ Done — passing live proof recorded 2026-09-26

- [x] 2.1 Pinned Sway 1.10.1 and recorded exact queries/events in `docs/0201_01_sway-ipc-proof.md`.
- [x] 2.2 Created the smallest fixture: snapshot, allowlisted workspace focus, and observed target focus event.
- [x] 2.3 Defined a thin test-only consumer capability mediator: exact revision, granted scope, safe selector, and no arbitrary command.
- [x] 2.4 Acceptance: live fixture obtains state, completes its allowlisted operation on an observed predicate, and deterministic checks prove rejected requests make no call.

### Step 3 — Validate on `luna-pi`
**Status**: ✅ Done — Pi-specific evidence recorded 2026-09-26

- [x] 3.1 Recorded board, RAM, OS, kernel, DRM nodes, and input-node facts in `docs/0301_01_luna-pi-sway-result.md`.
- [x] 3.2 Ran the approved headless Sway-IPC proof and recorded readiness, sampled RSS/CPU, event latency, and recovery.
- [x] 3.3 Documented Pi-only limits without extrapolation to Luna.
- [x] 3.4 Acceptance: versioned record separates portable IPC evidence from Pi-only Sway/graphics-process evidence.

### Step 3.5 — Validate a development-only Wyoh MCP bridge over SSH
**Status**: ⏳ Pending — prepared 2026-09-27; no implementation authorised

- [ ] 3.5.1 Pin the Python MCP SDK and protocol version, document the local/remote Python environments, and implement only a stdio entry point launched as `ssh -T luna-pi -- …`; do not open a port or install a resident service.
- [ ] 3.5.2 Start the same disposable headless Sway session as the existing proof and expose exactly `wyoh_snapshot`, `wyoh_focus_proof_workspace`, and `wyoh_server_status`; redact raw tree/window/application data and reject all other authority.
- [ ] 3.5.3 Add deterministic pytest and Gherkin contracts for discovery, schemas, revision/freshness, allowed focus, stale/unauthorised/malformed rejection, client disconnect, and cleanup.
- [ ] 3.5.4 Add an explicit `@pytest.mark.live` SSH-carried-stdio MCP client test. Persist complete client/server stderr and JSON evidence under `results/wyoh/mcp-over-ssh/<timestamp>/`; do not call it a rendered UI test or Luna evidence.
- [ ] 3.5.5 Use the MCP client from this development environment to list and call the server's advertised tools across SSH. Treat dynamic registration as a current-chat tool as a separately scoped host-configuration decision.
- [ ] 3.5.6 Acceptance: the SSH stream carries a real MCP lifecycle; only the three declared tools are discoverable; the fixed action is event-verified; rejections make no Sway call; and closing the stream leaves no server, Sway child, port, or service behind.

### Step 4 — Characterise Luna and choose the production base
**Status**: 🧪 In progress — stock baseline captured; Luna was unreachable on the 2026-09-27 recheck

- [x] 4.1 Recorded OS, RAM, framebuffer/DRM-visible nodes, input-node visibility, build identity, MMC/eMMC visibility, and Bluetooth exposure in `docs/0405_01_luna-stock-image-inventory.md` and `docs/0401_02_luna-storage-and-bluetooth.md`.
- [ ] 4.2 Before any flashing or replacement, identify the stock frontend/version, boot path, process/display stack, controller mapping, overlays, launch/return flow, SSH status, and recovery route.
- [ ] 4.3 Run the Sway-IPC fixture where safely possible; compare unmodified Sway, a thin Wyoh adapter, and any necessary custom/fork path on memory, action completeness, recovery, ordering, input, and latency.
- [x] 4.4 Acceptance: selected **defer** because physical Luna is unavailable; `docs/0404_01_luna-production-base-deferred.md` records the evidence boundary and required re-entry checks.
- [x] 4.5 Completed the read-only stock-image inventory and retained live pytest evidence; no Luna state was changed.
- [ ] 4.6 Acceptance: an evidence record distinguishes the preserved EmuELEC baseline from the future experimental card, then selects or defers the production base without modifying the stock card.

### Step 5 — Productise only the selected agent-native workspace path
**Status**: ⏳ Pending

- [ ] 5.1 Fork/pin only the selected upstream; retain licence, provenance, and upgrade strategy.
- [ ] 5.2 Implement only the approved Sway configuration, capability mediator, and/or Wyoh adapter; retain controller/recovery mapping and deterministic startup.
- [ ] 5.3 Add contract tests and target smoke tests for state, events, focus/layout operation, capability rejection, focused input fallback, wait, process exit, malformed/stale request, and restart.
- [ ] 5.4 Acceptance: Luna boots a recoverable agent-native Wyoh workspace and passes its selected Sway/adapter contract suite inside its measured budget.
- ⏳ Step 3.5 — Validate a development-only Wyoh MCP bridge over SSH.

---

## Progress tracking ✅

- ✅ Full discussion reviewed for Wyoh’s mandate and constraints.
- ✅ Upstream survey and requirements/solution proposal recorded.
- ✅ Step 1 — Sway-v0 contract and product path ratified.
- ✅ Step 2 — Pre-hardware Sway-IPC proof passed.
- ✅ Step 3 — Pi-specific Sway validation recorded.
- 🧪 Step 4 — Physical Luna stock-image inventory in progress; production base remains unselected.
- ⏳ Step 5 — Productise the selected agent-native workspace path.

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
| 2026-09-27T20:29:12+02:00 | Prepared a pending development-only MCP-over-SSH follow-on: a redacted, three-tool Python stdio bridge to the disposable `luna-pi` Sway proof. No dependency, server, SSH configuration, Pi state, or runtime implementation was changed. |
| 2026-09-25 | Replaced the conventional-WM assumption with the controller-first HIOM after target-profile research. The likely stock EmuELEC/EmulationStation shell is now the first path to inventory and bridge; no runtime change was made. |
| 2026-09-25T02:24:10+02:00 | Step 1 green-lit and completed: HIOM v0 contract, finite action vocabulary, synchronisation semantics, consumer scopes, and stock-first product path were ratified. Step 2 remains pending. |
| 2026-09-25T11:22:52+02:00 | Re-scraped the complete shared conversation (155 messages) and added a cleaned, decision-focused Wyoh record. It confirms that Wyoh is controller-first HIOM automation rather than a conventional desktop WM; Step 2 remains pending. |
| 2026-09-25T15:26:26+02:00 | Follow-up discussion reopens Step 1: proposed v0 is unmodified Sway plus existing IPC, with an adapter/capability mediator only on demonstrated need. HIOM remains historical/reference material; no runtime work is authorised. |
| 2026-09-25T16:40:42+02:00 | Recorded Sway's documented ROCKNIX/EmulationStation use as a positive but conditional Wyoh-v0 selection signal. Luna's precise preinstalled distribution and compositor remain Step 4 inventory facts. |
| 2026-09-26T13:22:23+02:00 | Step 1 completed after explicit green light: ratified unmodified, version-pinned Sway plus existing IPC as Wyoh v0; direct IPC is fixture-only and a consumer capability mediator is deferred until evidence requires one. |
| 2026-09-26T13:34:13+02:00 | Step 2 completed: the version-pinned Sway IPC fixture passed a headless live proof on luna-pi. It records queries, workspace focus event, capability rejection, process metrics, and recovery; no Luna claim is made. |
| 2026-09-26T13:38:00+02:00 | Step 3 completed: recorded Pi facts and the isolated headless Sway proof results separately from Luna claims. |
| 2026-09-26T13:40:00+02:00 | Step 4 completed with the plan's defer outcome: physical Luna is unavailable, so no target inventory or production-base selection is claimed. |
| 2026-09-27 | Read-only stock-image follow-up: the microSD is `mmcblk1`; the eMMC controller times out and produces no eMMC block device; Bluetooth has no usable HCI adapter. |
| 2026-09-27T01:59:56+02:00 | Re-ran the pytest-owned, read-only stock inventory. SSH failed before any remote command with `No route to host`; the complete runner log and failed result are retained outside Git. Step 4 remains in progress and the production-base outcome remains defer. |
---

## Workline artifacts

- `worklines/wyoh/docs/0000_01_wyoh-mandate.md` — source-discussion decisions and unresolved facts.
- `worklines/wyoh/docs/0000_02_wm-candidate-survey.md` — current upstream survey and selection rationale.
- `worklines/wyoh/docs/0000_03_wyoh-requirements-and-solutions.md` — draft contract, resource envelope, and solution paths.
- `worklines/wyoh/docs/0000_05_controller-first-handheld-model.md` — primary product model: finite controller state, HIOM, and stock-frontend-first decision path.
- `worklines/wyoh/docs/0101_01_hiom_v0_contract.md` — historical original Step 1 HIOM contract; reopened by the Sway-v0 decision.
- `worklines/wyoh/docs/0101_02_controller_first_discussion.md` — initial decision record and preserved French source; controller-only conclusion is historical.
- `worklines/wyoh/docs/0101_03_followup_discussion.md` — active cleaned decision record: proposed Sway IPC v0, component boundaries, and implementation sequence.
- `worklines/wyoh/docs/0000_04_desktop-automation-model.md` — transport-independent model for state, locators, interactions, and synchronisation.
- `worklines/professor/docs/0001_01_initial_discussion.md` — complete source discussion.

## Mycroft context amendment — 2026-09-25

A later Mycroft composition phase may consume a bounded Wyoh context snapshot. Wyoh remains the owner of observable state and finite advertised actions; it provides neither arbitrary desktop contents, shell authority, nor implicit command execution. Step 1 therefore also needs a reviewable snapshot contract: consumer scope, revision/freshness, safely available labels/actions, truncation, and failure with no side effect. No Sway fixture or live Mycroft integration is authorised.

See [the planning-only boundary](docs/0101_04_mycroft-context-boundary.md).

### Amendment log

- `worklines/wyoh/docs/0000_08_mcp-over-ssh-validation-proposal.md` — prepared boundary, transport, tool surface, tests, and acceptance for the development-only MCP bridge.
| Timestamp (`date`) | Update |
|---|---|
| 2026-09-25T23:10:00+02:00 | Added the planning-only Wyoh-to-Mycroft context boundary from the shared discussion. |

## Additional workline artifact

- `worklines/wyoh/docs/0101_04_mycroft-context-boundary.md` — bounded, revisioned future context snapshot.
- `worklines/wyoh/docs/0101_05_professor-note-on-mycroft-composition.md` — Professor coordination note on bounded Mycroft context.
- `worklines/wyoh/docs/0101_06_sway-v0-contract.md` — active Step 1 Sway v0, authority, component, and deferred-hardware contract.
- `worklines/wyoh/docs/0201_01_sway-ipc-proof.md` — Step 2 pinned IPC protocol, fixture, passing evidence, and limits.
- `test/wyoh/` — deterministic capability tests, live headless Sway proof, and Gherkin contract.
- `worklines/wyoh/docs/0301_01_luna-pi-sway-result.md` — Pi-only board facts, Sway result, metrics, and limits.
- `worklines/wyoh/docs/0404_01_luna-production-base-deferred.md` — honest Step 4 defer decision and re-entry conditions.
- `worklines/wyoh/docs/0405_02_luna-reachability-recheck.md` — failed read-only recheck and the resulting honest Step 4 boundary.
- `worklines/wyoh/docs/0405_01_luna-stock-image-inventory.md` — physical Luna's preserved EmuELEC baseline and explicit evidence gaps.
- `worklines/wyoh/docs/0401_02_luna-storage-and-bluetooth.md` — read-only eMMC-controller and Bluetooth-adapter observation on the preserved image.
