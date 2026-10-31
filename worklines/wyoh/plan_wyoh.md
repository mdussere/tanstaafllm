> **Current plan status (2026-10-04):** Steps 1–3.6 are done and re-run green on `luna-pi` under the uv-managed environment ([0400_01](docs/0400_01_takeover-review-and-luna-pi-revalidation.md)), but visual inspection showed that Step 3.6's rendered-client VNC proof was invalid and that the shared session is unusable by a person (no bindings, bar, or launcher). Step 3.7 fixed both on 2026-10-04 ([result](docs/0307_01_minimal-environment-result.md)). Step 4 is in progress: the factory EmuELEC card is archived and set aside, and the Luna workline's disposable ArchR card boots a Sway + EmulationStation session on the physical device, but Luna has no network yet, so no Wyoh check has run against it. The production base remains unselected.
>
> Wyoh v0 is unmodified Sway plus its existing IPC; a thin Wyoh adapter/capability mediator follows only when Sway cannot safely express a required Luna semantic or operation; extension or fork only on demonstrated need. The intended human path is instruction through Mycroft to Mike. Mike performs simple offline system actions; Mannie retains development/code/build/test work. Buttons are attention/recovery controls; an external keyboard/touchpad is development/recovery support (Bluetooth is unusable on the stock image, a USB keyboard works on ArchR).
>
> Sway fit on Luna, version pinning, memory/graphics/input cost, capability mediation, and any live Mycroft context remain later validation or cross-workline decisions.

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
- Source: `src/wyoh/`; produced workline evidence remains under `worklines/wyoh/docs/`

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
- Stronger, still indirect evidence (2026-10-03, Luna workline): the disposable ArchR card's default `archr.target` starts a Sway + EmulationStation session on physical Luna's RK3326 and 720×720 panel. Its Sway version, configuration, IPC socket, and memory cost are not yet recorded, and no Wyoh test has run against it. Luna delivered EmuELEC 4.7 (no Sway); that card is now archived and set aside.
- Mannie/Codex develops on the desktop and reaches devices through SSH.
- **Decision (user, 2026-10-07): Luna's Wyoh session stays root for now.** Luna is single-user and has no keyboard by default, so a password login before the session makes no sense. Consequence, accepted: everything launched from the session (terminal, menu, `exec` over IPC) runs as root, and only root can reach the Sway IPC socket. A non-root session user (auto-login, no password, seatd/logind) stays a later option, not a requirement.
- The initial and follow-up discussion records establish the current proposal: unmodified Sway plus its existing IPC as v0; an adapter/capability mediator only on demonstrated need. This reopens Step 1 and does not green-light Step 2.
- Wyoh is a desktop automation service, not a socket. A Unix socket may later be an efficient local transport, but the product contract is snapshots, locators, interactions, events, and waits.
- Wyoh supplies consumer-scoped views: Mike may receive policy-allowed simple actions; Mycroft v0 remains context-free. Any later live Mycroft context needs a separately authorised Mycroft-workline change.
- Wyoh validates interactions and reports structured state, success, failure, and events. It is not a shell proxy.
- The canonical state is a monotonic Wyoh revision plus events. App-published semantics have their own revision and freshness; Wyoh never treats an asynchronous client snapshot as globally atomic.
- The development-only MCP validation is a Python stdio server launched through `ssh -T luna-pi`, not a port-forward or resident service. Its completed full-IPC-development proof maps every documented Sway IPC request and event only to an owned, disposable headless child; it is neither a consumer nor a product capability.
- The proposed product order is: unmodified Sway IPC → thin Wyoh adapter/capability mediator → Sway IPC extension or fork only if evidence requires it. The stock frontend remains a reference/recovery baseline, not the intended agent-native workspace.

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
**Status**: ✅ Done — validated 2026-09-28; development-only evidence, not Luna or product evidence

- [x] 3.5.1 Pinned MCP SDK 2.2.0 / protocol 2026-07-28, Sway 1.10.1, and its 1.10 IPC manual; recorded local and remote Python environments and used only SSH-carried stdio.
- [x] 3.5.2 In explicit `--full-ipc-development` mode, owned a disposable headless session and mapped all 15 documented requests plus all 10 subscription event names while preserving decoded raw replies.
- [x] 3.5.3 Rejected ambient `SWAYSOCK`/`I3SOCK` before child/socket creation; `RUN_COMMAND` reached only the owned child. Raw results remain ignored development evidence.
- [x] 3.5.4 Added deterministic mapping/discovery/isolation/cleanup tests, a Gherkin contract, and a full event matrix in `docs/0305_01_mcp-over-ssh-validation-result.md`.
- [x] 3.5.5 Ran the explicit `@pytest.mark.live` SSH stdio client test and retained complete stderr/JSON evidence under ignored `results/wyoh/mcp-over-ssh/20260928T063829Z/`.
- [x] 3.5.6 Used an official Python MCP client here to discover and exercise all advertised request, subscription, event-read, event-close, and lifecycle tools across SSH; host-tool registration remains deferred.
- [x] 3.5.7 Acceptance: real MCP lifecycle passed; all requests/events are mapped and the seven headless-untriggerable event producers are explicitly recorded; no live socket attachment, listener, port, or service was used, and orderly child shutdown was observed.

### Step 3.6 — Share one owned Sway session with MCP and WayVNC
**Status**: ⚠️ Done with a corrected claim — service, deploy, descriptor-bound MCP, and screenshot-to-file hold; the rendered-client VNC proof was invalid (corrected 2026-10-04, see 3.6.5 and Step 3.7)

- [x] 3.6.1 Moved all executable Wyoh source and its pinned development requirements to `src/wyoh/`; updated references while preserving tests under `test/wyoh/`.
- [x] 3.6.2 Added and exercised a reproducible, non-destructive `Makefile` deployment and preview path using `rsync` into a user-owned Pi directory. Deployment does not start, stop, enable, or disable a service.
- [x] 3.6.3 Added and exercised the named loopback shared-session service. Its MCP reads only the fixed owner-written descriptor and continues to reject ambient and caller-supplied sockets.
- [x] 3.6.4 Added and exercised server-side screenshot-to-file. It chooses an ignored result location and returns metadata/path only, never image bytes over MCP.
- [x] 3.6.5 Added deterministic and `@pytest.mark.live` Gherkin-described checks. Preview is transport-only; MCP and WayVNC identify the same session. **Correction (2026-10-04):** the "MCP-launched client changes an independently captured VNC frame" proof is invalid. Visual inspection shows its `terminal-visible.png` is wallpaper only (captured on the `window` `new` event, before the client's first frame) and its `before-terminal.png` shows a terminal left by the preceding test; the frame-difference assertion passed for the wrong reason. Direct grim and VNC captures taken on 2026-10-04 show that Sway, `lxterminal`, and WayVNC do render correctly. Replaced by Step 3.7.
- [x] 3.6.6 Acceptance: the session is loopback plus SSH only; the retained Labwc VNC unit is a documented recovery path; and MCP attachment is restricted to the fixed owned descriptor.

### Step 3.7 — Minimal workable Sway environment on `luna-pi`, operated through MCP
**Status**: ✅ Done — green-lit and completed 2026-10-04; development-only, not Luna/product evidence ([result](docs/0307_01_minimal-environment-result.md))

The shared session was an empty Sway: its `--config` replaced Sway's defaults and defined no key binding, bar, or launcher, so a VNC user could not do anything. This step made it usable by a person over VNC, then proved with inspected screenshots that the MCP operates the same environment.

Environment:

- [x] 3.7.1 Rewrote `src/wyoh/deploy/luna-pi/sway-vnc.conf` from Sway 1.10's default config: `$mod` = Alt; terminal, launcher, close, focus/move, workspaces 1–4, fullscreen, layout, and reload bindings; no `exit` binding. All bindings are `--to-code` with `xkb_layout fr`, so the AZERTY number row switches workspaces.
- [x] 3.7.2 Added the built-in `swaybar` with workspaces and `deploy/luna-pi/status.sh` (key hints and clock). An inline `status_command` failed under Sway's config quoting; the script avoids it.
- [x] 3.7.3 Headless output is 720×720; WayVNC stays loopback-only with `--keyboard=fr`; plain background.
- [x] 3.7.4 Installed `foot 1.21.0-2`, `wmenu 0.1.9-2+b1`, `wtype 0.4-3+b1` with `apt` as root, after the user granted root SSH on 2026-10-04. (A temporary rootless unpacked prefix was used first and then removed.)
- [x] 3.7.5 Deployed with the Make path and a service restart; `make wyoh-rollback` and `make wyoh-activate` were both exercised. Session memory about 95 MB after the scenario (108 MB for the previous wallpaper session).

MCP proof:

- [x] 3.7.6 Replaced the racy VNC test with `test/wyoh/test_minimal_env.py`: empty-session precondition, discarded WayVNC placeholder frame, wait for the first drawn frame, close by `con_id` only. The shared MCP test in `test_mcp_over_ssh.py` also closes by `con_id` now. Fixed the screenshot tool's same-second directory collision.
- [x] 3.7.7 Scenario in `test/wyoh/minimal_env.feature`: MCP opens and types into `foot` (marker file verified), switches workspace, moves and fullscreens the editor, closes by `con_id`; a person at VNC uses Alt+d (launcher → `mousepad`), Alt+Enter, and Alt+Shift+q. Launcher typing is by VNC, not `wtype`, because `wmenu` 0.1.9 aborts on the keymap change a transient virtual keyboard causes.
- [x] 3.7.8 MCP and VNC images for all nine steps of two passing runs (`20261003T232316Z`, `20261003T232433Z`) were inspected visually; each showed the expected state.
- [x] 3.7.9 Acceptance: a person on VNC can use the bindings, bar, terminal, and launcher; the MCP scenario passes; every screenshot claimed as evidence was inspected and shows the expected window; the session returns to empty; access stays loopback + SSH only; rollback works.

### Step 4 — Characterise Luna and choose the production base

**Status**: 🧪 In progress — stock baseline captured; the factory card is archived and set aside (Luna 5.2); the disposable ArchR card boots Sway + EmulationStation on Luna but has no network yet (Luna 5.8), so 4.2/4.3 cannot run

- [x] 4.1 Recorded OS, RAM, framebuffer/DRM-visible nodes, input-node visibility, build identity, MMC/eMMC visibility, and Bluetooth exposure in `docs/0405_01_luna-stock-image-inventory.md` and `docs/0401_02_luna-storage-and-bluetooth.md`.
- [ ] 4.2 Before any flashing or replacement, identify the stock frontend/version, boot path, process/display stack, controller mapping, overlays, launch/return flow, SSH status, and recovery route.
- [ ] 4.3 Run the Sway-IPC fixture where safely possible; compare unmodified Sway, a thin Wyoh adapter, and any necessary custom/fork path on memory, action completeness, recovery, ordering, input, and latency.
- [x] 4.4 Historical (2026-09-26, before Luna was reachable; superseded by the Step 4 re-entry and 4.6): selected **defer** because physical Luna was unavailable; `docs/0404_01_luna-production-base-deferred.md` records the evidence boundary and required re-entry checks.
- [x] 4.5 Completed the read-only stock-image inventory and retained live pytest evidence; no Luna state was changed.
- [ ] 4.6 Acceptance: an evidence record distinguishes the preserved EmuELEC baseline from the future experimental card, then selects or defers the production base without modifying the stock card.

#### Step 4.7 — Reproduce the Step 3.7 session on Luna's real display
**Status**: ✅ Reproduced on the panel 2026-10-05, after Luna's Step 6 reshape: the nine steps of `luna-pi` run `20261003T232433Z` passed through MCP with a uinput "person" and inspected MCP screenshots ([result](docs/0407_01_luna-real-display-session.md)). Still root-only on ArchR; a normal-user rerun waits for Luna's Step 7. Development-only

Target: the disposable ArchR card (ArchR 20260709, kernel 6.12.94, root SSH `luna`), not the archived factory card. ArchR's own `sway.service`/`essway.service` and its files are not modified.

- [x] 4.7.1 Read-only inventory: ArchR ships unmodified Sway 1.11, swaybar, swaybg, grim, foot 1.19.0, bemenu 0.6.15, Python 3.13.5; no `wtype`, WayVNC, or `wmenu`. Panel `DSI-1` 720×720 connected; USB keyboard and `r36s_Gamepad` present; root ext4 97% full, `/storage` 54 GB. ArchR runs Sway as root through seatd, with EmulationStation inside it; it ships `config.kiosk` and `config.desktop`.
- [x] 4.7.2 Wyoh-owned files only on `/storage`: MCP 2.2.0 venv `/storage/.local/opt/wyoh-mcp-2.2.0` (pip needed `--no-compile`), Debian 13 `wtype 0.4-3+b1` arm64 binary (SHA-256 `d1133fae…c0cb6d`) in `/storage/.local/opt/wyoh-tools/bin`.
- [x] 4.7.3 Deploy `src/wyoh/deploy/luna/` with `make wyoh-luna-deploy`: a `wyoh-sway.service` drop-in unit in `/storage/.config/system.d` (not enabled at boot; conflicts with ArchR's Sway/EmulationStation units) running ArchR's Sway 1.11 on DRM with the Step 3.7 bindings, `fr` keyboard, swaybar, `foot`, and `bemenu`. Recovery: `make wyoh-luna-stop` returns to the tty1 text shell; deleting the unit and `/storage/.local/{share,opt}/…wyoh*` removes everything.
- [x] 4.7.4 Ran the Step 3.7 MCP scenario against it (`test/wyoh/test_luna_minimal_env.py`, passed; run `20261004T204916Z`); the agent inspected every grim screenshot (Sway's own composited output of `DSI-1`). There is no VNC on Luna, so the independent observer is the user looking at the physical panel and keyboard.
- [x] 4.7.5 Recorded session memory (≈ 46 MiB, no GPU driver: software compositing) against the 150/200 MiB budget, Sway 1.11 vs. the pinned 1.10.1 difference, and the result in `docs/0407_01_luna-real-display-session.md`. The MCP drove `bemenu` itself; `wtype` needs `-s 200 -d 20` pacing for it.
- [x] 4.7.6 Done 2026-10-05 on the reshaped card, as root (no users yet), with `vim` instead of `nano` (ArchR's `nano` ignores resizes). Originally: after Luna's reworked image: redeploy as a normal user and rerun the full Step 3.7 scenario (terminal, typing, launcher, editor as `nano` in `foot`, not a GTK app, split, fullscreen, a person-at-keyboard step through a kernel `uinput` keyboard, empty), with every screenshot inspected and the user confirming the physical panel.
- [ ] 4.7.7 Acceptance: the session shows on Luna's panel, a person can use it with the USB keyboard, the MCP scenario passes with inspected screenshots, and stopping the unit returns Luna to its text console.

#### Step 4.8 — Application menu with icons (fuzzel) on Luna's panel
**Status**: ✅ Done 2026-10-05, by user direction ("let's test fuzzel… many interactions… evidence images") — [result](docs/0408_01_luna-fuzzel-menu.md); development-only

- [x] 4.8.1 Shortlisted Windows 3.x-like options (labwc, Sway + fuzzel, tileWin, sfwbar, others); the user chose to test fuzzel, keeping Sway and its IPC.
- [x] 4.8.2 Installed Debian's fuzzel 1.12.0 (Arch Linux ARM's needs glibc 2.43), a 12-icon Papirus subset, a Windows 3.x-palette `fuzzel.ini`, and five Wyoh app entries; Alt+d opens it.
- [x] 4.8.3 Found and fixed: the Mali GPU driver wasn't loaded under text-mode boot (black panel, software rendering); focus-follows-mouse closed the menu; launch history reordered it; swayimg floated transparently.
- [x] 4.8.4 `test/wyoh/test_luna_fuzzel.py` (+ feature): keyboard filter, arrows, Escape, keyboard launch, mouse-click launch, MCP-driven dmenu answered by the person, cleanup. Passed; 19 screenshots inspected (`results/wyoh/luna-fuzzel/20261005T145737Z/`).
- [ ] 4.8.5 The user confirms the menu and windows on the physical panel now that Sway renders through Mali.

### Step 5 — Device interactors: drive Luna with its own controls
**Status**: 🧪 Built and proven in simulation 2026-10-07 — the button-only scenario passes through MCP after a cold boot into the session ([result](docs/0506_01_buttons-only-result.md)); awaiting the user's physical check (5.7). Green-lit 2026-10-07 ("work in full autonomy; use Gherkin tests and MCP to simulate the human operations"). **Acceptance set by the user: Luna can be operated with only the buttons and the input zone, and boots into the session.** Development-only

**Contract change:** the ratified Step 1 boundary treated buttons as attention/recovery controls only. By user direction, the device's controls become the primary interaction on Luna, and keyboard text later moves to voice through an input zone.

**User decisions (2026-10-07):** Wyoh owns the input zone for now (later a Mycroft dictation/correction surface; see `../mycroft/docs/0106_02_note-from-wyoh-input-zone.md`). The mapper is a small Wyoh daemon, not `gptokeyb`, so that L1/L2 and the pointer are intercepted at the lowest level and can later be prepared or supplemented by AI. Y = Backspace. R1/R2 = quick linear navigation between focus zones, first approximated by Tab / Shift+Tab.

Hardware facts (read-only, `r36s_Gamepad`, `/dev/input/event7`): 17 buttons (`BTN_DPAD_UP/DOWN/LEFT/RIGHT`, `BTN_SOUTH/EAST/NORTH/WEST`, `BTN_TL/TR/TL2/TR2`, `BTN_SELECT/START/MODE`, `BTN_THUMBL/THUMBR`) and 4 axes (`ABS_X/Y`, `ABS_RX/RY`, −1800…1800, flat 32). ArchR's `input_sense` also reads this device: L1/Select/Start hotkeys, FN+D-pad brightness, FN+B LED.

| Control | Action |
| --- | --- |
| D-pad | arrow keys (held = key repeat) |
| Left stick | pointer, speed proportional to deflection (dead zone, power curve), ~100 Hz |
| Left stick click (L3) | left click |
| Right stick, R3 | unassigned |
| A / B / Y / X | Return / Escape / Backspace / Delete |
| L1 | open or close the input zone (close = discard) |
| L2 | validate the input zone: its text is delivered once to the window that had focus |
| R1 / R2 | Tab / Shift+Tab (quick linear navigation, first approximation) |
| Select, Start, FN | unassigned (later: major modes such as terminal, Mannie, desktop, menu) |
| FN + Start held 2 s | **proposed recovery:** release every key and button, close the input zone, return focus to the workspace |

> **Controls superseded (2026-10-09):** the mapping described in this step (left-stick pointer, L1 open/discard, L2 validate) is out of date. The current reference, checked against the code by a test, is [`docs/0512_01_luna-controls-reference.md`](docs/0512_01_luna-controls-reference.md).

Intent (behaviour, states, failure modes, budget, tests): [`docs/0500_01_gamepad-input-intent.md`](docs/0500_01_gamepad-input-intent.md). Sub-steps run in this order; each ends with its tests passing and, where it has a visible effect, inspected screenshots.

- [x] 5.0 Intent written before any code (2026-10-07); four open points listed in it for the user.
- [x] 5.1 **Calibration from the device tree (read-only, 2026-10-07).** `/proc/device-tree/joypad/sw*` labels every button: A = `BTN_EAST`, B = `BTN_SOUTH`, X = `BTN_NORTH`, Y = `BTN_WEST`, FN = `BTN_MODE`, L1/L2/R1/R2 = `BTN_TL/TL2/TR/TR2`. The intent was corrected (it had assumed A = `BTN_SOUTH`). Stick polarity and the physical labels are confirmed in 5.7.
- [x] 5.2 **Core state machine, offline.** Mapping, zone states, recovery timer and pointer curve as pure code with deterministic tests (every mapping row in both modes, zone validate/discard/empty/target-gone/re-entrance, recovery timing, invalid config). No device access.
- [x] 5.3 **Device adapters.** Gamepad discovery, read and grab; persistent uinput keyboard and mouse; select() loop with zero CPU at rest. Live check against a virtual gamepad on Luna: keys and pointer reach Sway; stopping the daemon releases the grab.
- [x] 5.4 **Input zone.** fuzzel one-line zone, Sway target capture and refocus, paced `wtype` delivery; status file. Live check with marker-file side effects for deliver-once and discard.
- [x] 5.5 **Service and deployment.** `wyoh-gamepad.service` (PartOf the Sway unit), `gamepad.toml`, Make targets; measure RSS and CPU at rest and with the stick deflected.
- [x] 5.6 **Button-only scenario through MCP.** Development MCP tools create a virtual gamepad and keyboard (the person); the daemon serves it alongside the real gamepad. Gherkin + pytest end to end on Luna's panel with inspected MCP screenshots, as in the intent's testing policy.
- [ ] 5.10 **User feedback (2026-10-08), deployed; full re-run pending.** (a) Pointer on the **right stick**, click on **R3**, left stick unassigned (51 core tests pass). (b) The user's `TANSTAAF-LLM_background.png` (updated with a blond Wyoh) is the wallpaper, pre-scaled to 720×720; it needed GIO's MIME database, which ArchR lacks (`share/mime/mime.cache` from shared-mime-info 2.4, deployed only). A capture matches the image exactly. **Not done:** the full button-only scenario has not passed again since these changes. Its re-runs failed on Wi-Fi stalls at different steps, not on a demonstrated Wyoh fault, and the user asked to stop rerunning it after every change.
- [x] 5.11 **Four tiles per workspace (user requirement 2026-10-08).** `wyoh_layout.py` + `wyoh-layout.service` (wanted by the Sway unit): 2nd window on top (vertical split), 3rd top-right, 4th bottom-right, 5th closed with a "Too many tiles" pop-up dismissed by B. 11 policy tests pass; the layout scenario passed twice on Luna (`results/wyoh/luna-layout/20261008T215715Z`, inspected; `20261008T220831Z`, not yet inspected).
- [x] 5.12 🟩 **Green-lit by Professor on the user's behalf (D4, 2026-10-09).** *Done:*
  - [`docs/0512_01_luna-controls-reference.md`](docs/0512_01_luna-controls-reference.md), one table per mode, with "live" or "core only" per row;
  - `test/wyoh/test_luna_controls_reference.py`: 24 checks against the deployed `Config`; a deliberate mismatch fails it;
  - Step 5 and `0500_01` marked superseded;
  - the four cheat-sheet fixes: Y = selection; 6.9 marked "bientôt"; brightness not adjustable (proposal FN+L1/FN+L2, not implemented); volume to verify; arrow repeat and Start closing the menu.

  Original request: **Controls reference in Markdown (requested by the user through Professor, 2026-10-09).** Write `docs/0512_01_luna-controls-reference.md`, one current description of every interactor, in English. Today the controls are described only by the cheat sheet (`0609_01`). The Step 5 table above and the intent `0500_01` are out of date: they still say left stick = pointer, L1 opens/discards, L2 validates.
  - One table per mode (desktop, Slate open, with FN, menu, gamepad-raw app), plus recovery, the four-tile rule and the two-thumb keyboard. Each row names the physical control, the evdev code and the resulting key, Sway command or Slate operation.
  - Generated from, or checked against, `wyoh_gamepad.Config`, with a deterministic test that fails when the document and the code disagree. Each row says whether it is live on Luna or only in the core (6.9's daemon side is not live yet).
  - Mark the Step 5 table and `0500_01`'s mapping as superseded by the reference.
  - Professor's review of the cheat sheet, to fix in the SVG/PNG at the same time:
    1. **Y in the Slate** reads "Majuscule". It is Shift held for selection, not capitals; write "Sélection : maintenir Y + croix".
    2. The sheet shows 6.9 (L1 hide with text kept, FN+A send, FN+X clear) as working, but only the core is done. Mark these as "bientôt" until the daemon side is live, as already done for L2.
    3. **Brightness and LED.** The exclusive grab stops ArchR's `input_sense` hotkeys (FN+D-pad brightness, FN+B LED), and Wyoh now uses FN+cross and FN+B itself. The sheet does not say how to change brightness, or say that it cannot be changed. Add it, and propose a mapping to the user if needed. Also state where volume is, if the volume keys are a separate device.
    4. D-pad and key repeat when held, and "Start: application menu" while the menu is open (does Start close it?), are worth one line each.
- [ ] 5.7 **User check** on the physical controls, panel in view; record the result in `docs/0507_01_gamepad-input-result.md`. *Pending: the only open item.*
- [x] 5.8 **Boot into the session (user requirement, 2026-10-07: "we must stop landing on terminal on boot").** Enable `wyoh-sway.service` and `wyoh-gamepad.service` in the boot target the card uses today (`textmode.target`, set by the Luna workline in `extlinux.conf`), through `[Install]` sections and links under `/storage/.config/system.d`, without touching the boot partition. The Mali driver step runs before Sway; the tty1 shell stays underneath as a fallback. Verified by a real reboot: the panel shows the session with no SSH action. Removing the links restores the text-console boot.
- [ ] 5.9 Acceptance as in the intent, plus booting straight into the session: every control works through the real gamepad; the zone delivers once and discards cleanly; recovery works; stopping the daemon returns the gamepad to ArchR; tests pass; budget holds.

### Step 6 — Slate (multi-line input) and backup on-screen keyboard
**Status**: 🧪 In progress — green-lit 2026-10-09; built and passing on Luna in simulation ([result](docs/0605_01_slate-result.md)); the user's check (6.6) and the whole-cross calibration are open

Proposal (name, layout, build options, controls, passwords, risks, budget, tests): [`docs/0600_01_slate-and-keyboard-proposal.md`](docs/0600_01_slate-and-keyboard-proposal.md). The ChatGPT discussion behind it is kept raw in [`docs/0500_02_input-widget-discussion-raw.md`](docs/0500_02_input-widget-discussion-raw.md). The user confirmed the name Slate.

- [x] 6.0 User decisions recorded (2026-10-09), and the proposal now serves as the intent:
  - name Slate;
  - in the Slate, A Return, B Backspace, X Delete, Y Shift for selection; the cross pressed as a whole selects the word, twice selects the line;
  - the keyboard is shown whenever the Slate is open;
  - black Slate with a white 2 px border and white half-size text; the keyboard has the same look, sized to 720 px;
  - L1 discards with no confirmation;
  - R1/R2 move to the next/previous word.
- [ ] 6.1 **Calibration and wvkbd fit on Luna.** *Done except the whole-cross calibration, which needs the user's hands (see 6.6):* wvkbd 0.15 from Debian runs on Luna; an AZERTY build (`src/wyoh/wvkbd/`, built on `luna-pi`) is deployed; zone font measured (capitals 17 px, so the Slate uses 12 px); landscape-mode and sizing findings in the result. Record what pressing the whole cross reports (`evtest`, with the user); stop and report if it isn't distinct. Measure the zone font's rendered height. Check wvkbd: Provenance (aarch64 build or Debian arm64, versions and checksums recorded, deployed under `/storage`, not committed). Measure RSS and CPU while hidden. Check show/hide by signal, key clicks with the right-stick pointer and R3, and AZERTY and accented letters with Sway's `xkb fr`. Check wvkbd's colour and font options for the black-and-white look. Build a compact Luna layout (letters, digits and symbols, about 240 px high, font fitted to 720 px).
- [x] 6.2 **Slate core offline.** (`wyoh_slate.py`; 107 Slate and gamepad tests pass) Deterministic tests, and text is never written to disk or logs:
  - pure editor: buffer, cursor, wrap, Return, Backspace, Delete, Shift selection, word toggle, line select, typing over a selection, empty send;
  - whole-cross detection with timing, in the gamepad core.
- [x] 6.3 **Slate replaces the fuzzel zone.** Floating `foot` window at the top, Python standard library; the daemon keeps target capture, delivery once, discard, and the status file (state and length only). Multi-line delivery to terminals as specified in the proposal's risks.
- [x] 6.4 **Keyboard and look.** wvkbd is shown and hidden together with the Slate (L1 / L2). The Slate has its white border: the daemon switches `client.focused` while it's open and restores it afterwards. Font sizes are set from 6.1.
- [x] 6.5 **Live scenario** — passed, 20 screenshots inspected (`results/wyoh/luna-slate/20261008T232237Z`, stock QWERTY build; re-run with the AZERTY two-selection build and an `é`: `20261009T155843Z`). Budget: Slate 22.3 MB and wvkbd 13.0 MB, both over the proposal's targets (recorded). (Gherkin + pytest, MCP person, inspected screenshots): two lines sent once to a terminal; multi-line discard; keyboard keys clicked with the stick; selection by word and line with the cross; the look checked on screenshots; a dummy password sent through the Slate leaves no trace in status, logs or results. Budget measured.
- [x] 6.8 **Two-cursor keyboard (user request, 2026-10-09; replaces the pointer clicks and the planned V1).** Done: `luna-cursors.patch` and the core; the live scenario passed with the final AZERTY build (`results/wyoh/luna-slate/20261009T155843Z`, 22 frames inspected). While the Slate is open:
  - the left stick moves a **pastel green** selection over the on-screen keyboard and L3 types its key;
  - the right stick moves a **pastel red** selection and R3 types its key;
  - so two thumbs can type ("tap with 2 fingers"), and each selection can stay on its half of the keyboard;
  - the pointer is off while the Slate is open.

  Implementation: a small wvkbd patch (two selections drawn in pastel, commands `move`/`press` on its standard input), and stick-to-step logic with repeat in the gamepad core. Tests: deterministic core tests plus the live scenario typing with both selections.
- [ ] 6.9 **Slate controls redefined (user, 2026-10-09).**
  - **L1** shows or hides the Slate. Hiding keeps the text: the window goes to Sway's scratchpad and the keyboard is hidden by signal.
  - **L2** starts or stops dictation. It is a no-op with a note until Step 12 brings Mycroft.
  - **FN+X** clears the Slate.
  - **FN+A** sends the text into the window that had focus, then clears and hides the Slate.

  **Verified live 2026-10-11** (Slate scenario `20261011T104403Z`): L1 hide keeps the text, L1 show brings it back, FN+X clears, and FN+A sends once. L2 dictation waits for Step 12. This replaces "L1 open/discard, L2 send". The target window is captured each time the Slate is shown. Implementation, core tests and live re-run.
  *Progress:*
  - Core done (show/hide, dictate, FN+X clear, FN+A send).
  - Daemon side done offline (Professor D5): L1 hides the Slate in Sway's scratchpad and wvkbd gets SIGUSR1/SIGUSR2; the Slate's `clear` operation; the hint line "FN+A send · FN+X clear · L1 hide"; L2 records "dictation unavailable (Step 12)".
  - The live scenario is updated (hide keeps text, show, FN+X clear, FN+A send). 192 Wyoh offline tests pass.
  - The live re-run waits for Luna (D8). User cheat sheet (French, front and top views, every button in each mode): [`docs/0609_01_luna-cheat-sheet.svg`](docs/0609_01_luna-cheat-sheet.svg) (PNG export next to it).
- [ ] 6.10 **Slate destinations and history (user, 2026-10-15).** FN+X clear and FN+A send to the focused window stay. New: **FN+Y** sends to Mannie's window (lines joined, then Return; if Mannie is not open the text stays, "ignored for now" per the user); **FN+B** is reserved for Mike (a notice until Mike runs on Luna; note to Mike `worklines/mike/docs/1204_02`); **FN+↑ / FN+↓** walk the sent texts like a shell, the draft kept. History on the card (user's choice): last 50, mode 600, `/storage/.local/state/tanstfaafllm/wyoh/slate-history.jsonl`; texts sent to the Wi-Fi password window are never kept. *Core and tests done (334 offline); not yet deployed or run live.* **Request from Mike (2026-10-31, Mike Step 12, green-lit by the user):** make FN+B deliver to Mike's chat on Luna. Wyoh's answer: the easiest shape is Mannie's path with app_id `mike` (Mike's own window, a foot terminal or GTK window with app_id `mike`, reads one line per message; FN+B types the joined text, then Return). Mike's alternative, a Unix socket taking `{"text": ...}`, is possible but needs a new delivery path. **Mike chose the window path (2026-10-31):** app dir `/storage/.local/opt/mike/` (foot, app_id `mike`); FN+B starts it when it is not open, waits until it is ready, then types the text and Return (fallback: start it and keep the text with a notice). Readiness key agreed: the window title (Sway tree `name`) becomes `Mike — ready`, set by Mike's client with OSC 2; wait at most 90 s with a notice "Mike is starting", then keep the text. Waiting for the user's go; not started.
- [ ] 6.6 **User check** on the panel: readability of the half-size font, the whole-cross press (does the real cross report two directions at once?), and how two-thumb typing feels (step size, repeat speed, start positions).
- [ ] 6.7 Acceptance: multi-line text composed and sent with buttons alone; the keyboard usable as a backup, including for a password; tests pass; budget holds.

### Step 7 — Wi-Fi network selection from the buttons
**Status**: 🔄 In progress (7.0–7.2 done, 7.3–7.4 partly) — the user's priority (2026-10-15: "the most urgent now is to allow discovering and configuring a Wi-Fi network"), decisions 7.0 recorded; depends on Step 6 for password entry

Proposal (ownership, candidates, design, risks, tests): [`docs/0700_01_wifi-settings-proposal.md`](docs/0700_01_wifi-settings-proposal.md). **Boundary:** the network stack (iwd, ConnMan, persistence, DHCP) belongs to the Luna workline; Wyoh owns only the screen and the button flow, and writes a note to Luna rather than changing the stack.

- [x] 7.0 **User decisions (2026-10-15):** a fuzzel panel on iwd (not NetworkManager); entry from the Start menu only; the office network uses a password only (WPA2/WPA3-Personal, so v0 is enough); the user's phone hotspot is the test access point.
- [ ] 6.11 **Mike's chat window on Luna (request from Mike Step 12.4, 2026-10-31; the user told Mike "Wyoh is there for that").** Wyoh builds the interface around Mike's client `src/mike/smalltalk.py` (stdin one line per question, streamed answer, OSC 2 titles `Mike — starting` / `Mike — ready` / `Mike — thinking`, `/new`, `/quit`; it starts its own llama-server). Mike owns the model, llama-server and their path on Luna. Wyoh's part: (1) app dir `src/wyoh/apps/mike/` (`wyoh-app.toml` + `run`) deployed to `/storage/.local/opt/wyoh-mike/` (only the manifest and launcher; Mike's own files stay in its `MIKE_HOME`): a foot window, app_id `mike`, menu entry "Mike", run as `michael` like Mannie (`runuser -l michael`) so its state lands in michael's home; (2) FN+B as recorded in 6.10 (start if absent, wait for `Mike — ready` up to 90 s, type, Return); (3) readability on 720x720: foot font size and wrapping, a short first line saying how to talk (L2 dictate, FN+B send). Acceptance: offline tests for the manifest and the FN+B wait; on Luna, FN+B from the desktop with Mike closed starts it and the question is answered, screenshots inspected; Mannie on Luna's go before any SSH. Mike's answer (2026-10-31): `MIKE_HOME=/home/michael/.local/opt/mike` (smalltalk.py, llama/llama-server, the gguf), pending Mannie on Luna's agreement; `wyoh-mike` accepted. Mike relayed the user's words in its console (work independently, "we can even ask Prof", "Wyoh is there for that"); Mike's files on Luna (2026-10-31, Mike commit 19c81ca, `worklines/mike/docs/1205_01`): `MIKE_HOME/smalltalk.py`, `llama-b11429/llama-server` and the model; title `Mike — ready` 3.7 s after start with the saved prompt, 8–11 s on a first start (more after a reboot). The client holds `/tmp/luna-brain.lock`; while Mannie runs it sets `Mike — busy` and waits for Enter, so FN+B must show "Mike cannot start while Mannie runs" and keep the text (Mannie and Mike, about 300 MiB each, cannot run together today). per the cell rule only the user green-lights a Wyoh step, so *Waiting for the user's `🟩 go Step 6.11`.*
- [x] 7.1 **Done (2026-10-15):** iwd 3.10 owns Wi-Fi and its addresses (`EnableNetworkConfiguration=true`); ConnMan 1.43 runs but has no Wi-Fi technology, so no conflict. Profiles in `/storage/.cache/iwd` (literal SSID names; the `=20` file is ArchR's, ignored by iwd). No Python D-Bus library on Luna: `busctl --json=short` is used. Evidence `results/wyoh/wifi-inventory/20261015/managed-objects.json`. The phone hotspot was not seen (probably 5 GHz). Original item: **Read-only inventory on Luna:** iwd version and D-Bus objects via `busctl`; whether iwd or ConnMan configures `wlan0`'s addresses; profile directory and file encoding. Any conflict goes to Luna as a note, and the step stops.
- [x] 7.2 **Done (2026-10-15):** `src/wyoh/wyoh_wifi.py`, 33 tests (`test/wyoh/test_wyoh_wifi.py`), including no password on any command line or screen. Original item: **Panel core offline.** Parse `busctl` JSON, menu text and ordering, profile file content and name encoding, failure messages; deterministic tests, including that no secret appears in any log or status.
- [ ] 7.3 *Deployed (2026-10-15): Start menu entry "Wi-Fi" (Papirus `network-wireless`, copied to Luna's icon subset), fuzzel list, a foot window for the masked password (typed with the Slate), bar text "SSID ▮▮▮▮". The first list was wider than the panel (user report); fixed to the Start menu's width and shorter lines; the user's own check is pending.* **Panel on Luna.** fuzzel list (connected mark, SSID, security, signal; Rescan, Forget, Disconnect), connect to known networks, new WPA-PSK networks through the Step 6 keyboard (iwd profile written with mode 600, removed after a failed attempt), honest result pop-ups, SSID and signal in the bar.
- [ ] 7.4 *Join done (2026-10-15): `test_luna_wifi.py` passed; Luna joined Freebox-1E23B6 (the user's second network) with a new profile in 5.4 s, got 192.168.1.109, came home (one retry) and left no profile (`results/wyoh/luna-wifi/`). The screen scenario added to `test_luna_apps.py` has not passed yet: its first run failed at the calculator, not investigated, while the user was using Luna.* **Live scenario** (Gherkin + pytest, MCP person, inspected screenshots, user-provided test access point): connected network shown; rescan; join the test access point with a dummy password; a wrong password is refused and leaves no profile; return home. The home network is never forgotten by tests.
- [ ] 7.5 **User check:** join the office network (WPA-Enterprise is out of v0 and becomes its own step if needed).
- [ ] 7.6 Acceptance: a person joins, switches and forgets PSK and open networks with buttons alone; no secret in Git, logs, results or screenshots; tests pass.

### Step 9 — Graphical applications and menu clean-up (Professor's note)
**Status**: 🧪 In progress — green-lit by the user on 2026-10-09 ("vas-y, branche les applications que professeur a sélectionnées"). Request and Wyoh's reply: [`docs/0900_01_note-from-professor-graphical-apps.md`](docs/0900_01_note-from-professor-graphical-apps.md).

**Ownership (interpretation, recorded):** the user asked Wyoh to plug the apps in, and Professor's plan does not allow it to build subsystems. So Wyoh both assembles (fetches or builds) and integrates the apps. Recipes live in `src/wyoh/apps/<app>/` (build script, patches, checksums); binaries are deployed under `/storage/.local/opt/<app>-<version>/` and never committed.

**Apps (the user's choice via Professor):** a Windows 3.1-style calculator (new), Wolfenstein 3D (PortMaster `wolf3d`), chess (pygameUCI + Stockfish), files (Commander), the Dino game (white on black), and the NetSurf browser (images off; Google if it works without JavaScript, otherwise FrogFind, then DuckDuckGo Lite).

- [ ] 9.0 **Blocked (2026-10-09):** Luna first answered ping but timed out at the SSH banner, then stopped answering ping. `luna-pi.local` no longer resolves either, so the build host is unavailable too. Every device-side sub-step waits; the question is with the user. Debian 13 already packages `stockfish` 17 and `love` 11.5 (checked on sources.debian.org); `netsurf-fb` and `python3-pygame` arm64 are to be confirmed with `apt` on `luna-pi`.
- [ ] 9.1 Read-only runtime check on Luna (partly done, 2026-10-09, after the user's reboot):
  - **Present:** SDL2 2.32.10 (KMSDRM **and Wayland** back ends), SDL2_image/ttf/mixer/gfx/net, LuaJIT, OpenAL, libmodplug, EGL/GLES (`libmali`), Python 3.13.5; `/` has 20 GB free. **No pygame.**
  - **pacman:** only ArchR's own repository; its sync failed (GitHub returned 500).
  - **Already installed by ArchR:** **Commander** (`/usr/bin/commander`; ArchR runs it under Sway with `sway_fullscreen`), RetroArch with the **`ecwolf` (Wolfenstein 3D)** and `tyrquake` cores, gzdoom, ScummVM, TIC-80, mpv, gmu, VLC, PortMaster and `gptokeyb`.
  - **Finding:** Commander starts under Wyoh's Sway (app_id `commander`; it goes full screen with a 320 × 240 surface), but every `grim` capture is entirely black, with SDL's software and GLES renderers alike. Unknown whether the panel shows it or `grim` cannot read Mali (EGL) buffers; a GLES demo (`glmark2`) was started to tell them apart, and Luna then dropped off the network. **Question to the user:** what does the panel show?
- [x] 9.1b **GPU apps under Wyoh's Sway — solved 2026-10-11 ("essaie en gpu").**
  - **Cause:** Mali clients send their buffers through Mali's own `mali_buffer_sharing` protocol (seen with `WAYLAND_DEBUG`), which Sway cannot import (`eglCreateImageKHR failed`).
  - **Fix:** `libmali` has `MALI_WAYLAND_DMABUF_PROTOCOL`. Set to 1, clients use the standard `zwp_linux_dmabuf_v1` (XBGR8888, Mali modifier), Sway imports them with zero errors, and `grim` captures them.
  - **Evidence (inspected):** `results/wyoh/apps-probe/20261011/`: `calculator-dmabuf-before.png` (Windows 3.1 calculator in a window), `calculator-dmabuf-typed.png` ("75" typed through a uinput keyboard), `commander-dmabuf.png` (Commander's two panes, full screen).
  - **Made permanent:** `Environment=MALI_WAYLAND_DMABUF_PROTOCOL=1` in `wyoh-sway.service` and `wyoh-gamepad.service`, and in the apps' `run`. Commander has its own manifest (`src/wyoh/apps/commander`, menu name "Files", full screen).
  - **Fix verified live (2026-10-11):** the Slate scenario passed with `deliver_path: uinput` (`results/wyoh/luna-slate/20261011T104403Z`, 25 frames inspected, "echo aé" typed correctly). Written offline: `type_events()` and the shared `AZERTY` table (Shift and AltGr) in `wyoh_gamepad.py`; `deliver()` types through the daemon's uinput keyboard and records `deliver_path` in the status; 6 new tests, 245 Wyoh offline tests pass. Earlier wording: the daemon types Slate text itself through its uinput keyboard (an AZERTY table with Shift and AltGr, shared with the test keyboard), falling back to `wtype` only for characters the layout cannot produce.
  - **Known issue:** SDL2 apps segfault inside `SDL_WaitEvent` on keys sent by `wtype` (a virtual-keyboard keymap per key), while uinput keys work. **The Slate's delivery uses `wtype`, so sending Slate text to an SDL app would crash it.** To fix: deliver through the daemon's uinput keyboard for SDL targets.
  - **Superseded:** the GPU-free route (experiments 1 and 2) is no longer needed. The history below is kept.

  History, superseded by the fix above:
  - **Finding:** Sway logs `eglCreateImageKHR failed` / `Failed to upload buffer` for each frame of an SDL2 window (calculator, Commander). It cannot import Mali client buffers, so composed windows show only their border. Sway loads `libmali` with ArchR's `libmali-hook`.
  - **Hypothesis:** ArchR runs its apps full screen, where wlroots can scan the client buffer out directly without an EGL import. That would explain why ArchR's EmulationStation works and our floating calculator does not.
  - **Not verifiable by capture:** `grim` composes through the same failing import, so full-screen GPU apps capture black whatever the panel shows. The user is asked to look at the panel (the calculator is left running full screen).
  - **If confirmed:** GPU apps must run full screen (`window = "fullscreen"`), and the capture evidence for them must come from another path.
  - **If not:** this is a GPU-stack question (libmali and wlroots dmabuf import), to note to Luna.
  - **D14 test (2026-10-09):** `SDL_RENDER_DRIVER=software SDL_FRAMEBUFFER_ACCELERATION=0` does not avoid EGL. Under Wayland, SDL2 has no wl_shm framebuffer: the calculator still maps `libmali`, and Sway logs the same import errors (12 in 5 s). So the software route is closed inside SDL's Wayland back end.
  - **Options, blocked on the user (asked in the Wyoh console):**
    1. The panel check (does a full-screen GPU app show?). If yes, GPU apps go full screen.
    2. Enable Xwayland **without glamor** (`XWAYLAND_NO_GLAMOR=1` in Sway's environment, `xwayland enable`), and run SDL apps with `SDL_VIDEODRIVER=x11` and the software renderer. X11 apps then pass shared-memory buffers, and Commander and the calculator could run in windows. This changes `wyoh-sway.service` (`/storage/.config/system.d`, outside D14's `/storage/.local` limit), needs a Sway restart, and costs Xwayland's memory while an X app runs.
    3. A Luna-workline note about libmali and wlroots dmabuf import (the GPU stack is Luna's).
    4. The calculator only: draw it without SDL's window (a small Wayland shared-memory client in Python), which does not help Commander.
  - **User decisions (2026-10-11):**
    - **No app needs the GPU.** The heaviest target is a Wolfenstein 3D-style shooter, whose sprite and raycast rendering needs no GPU. Policy: applications draw on the CPU and hand Sway shared-memory buffers; GPU paths are avoided rather than repaired.
    - **Window policy:** the four-tile split stays for now and gets adapted. A **full-screen-only policy**, where every app is full screen and a quick key combination switches between open apps, is the likely simpler future (to propose as its own step).
  - **Order of experiments (CPU only, no GPU stress):**
    1. Point SDL apps at Mesa's software EGL (llvmpipe, wl_shm) instead of `libmali`, per app in its `run`: no Xwayland, no session restart.
    2. Otherwise, Xwayland without glamor with `SDL_VIDEODRIVER=x11` and the software renderer.
  - **Experiment 1 (2026-10-11), Mesa software EGL:**
    - Mesa 26.1.3 (llvmpipe/swrast) and libglvnd 1.7.0 are on Luna, but `libmali` is bind-mounted over glvnd's `libEGL.so.1.1.0`/`libGLESv2.so.2.1.0`.
    - The original dispatchers were copied, read-only, through a temporary non-recursive bind mount of `/` to `/storage/.local/opt/wyoh-cpu-gl/lib/`; nothing of ArchR's was changed.
    - The calculator was run with `LD_LIBRARY_PATH` set to that directory, `__EGL_VENDOR_LIBRARY_FILENAMES=…/50_mesa.json`, `LIBGL_ALWAYS_SOFTWARE=1` and `GALLIUM_DRIVER=llvmpipe`. Sway logged no import error, but the calculator exited at once: `libEGL warning: egl: failed to create dri2 screen`.
    - **Correction (user, 2026-10-11):** Luna was not blocked. Only SSH from the desk stalled; Luna's interface and the user's own SSH worked. Wyoh's claim was wrong. The Mesa failure is just the DRI2 error above. **New practice (user):** reboot Luna preventively after each test or small series (`ssh luna reboot`, about 30 s).
    - **Diagnosis after the reboot:** with `EGL_LOG_LEVEL=debug`, Mesa does choose a CPU renderer, then rejects every config (`DRI2: failed to validate config` / `conflicting surface type and native visual`), and `eglInitialize` fails (`EGL_NOT_INITIALIZED`). **Experiment 1 is a dead end** short of debugging Mesa's Wayland software path.
    - The calculator now exits with a clear message instead of a segfault when SDL has no renderer.
    - Luna rebooted preventively by Wyoh after the series (user rule).
    - **Next: experiment 2 (Xwayland without glamor).** Wyoh asks the user before changing `wyoh-sway.service` and restarting the session.
  - Done meanwhile: `make wyoh-luna-apps` ran on Luna. The menu set was confirmed: gmu and mupen64plus are in `/usr/local/share/applications`, swayimg/wine/Xwayland are already NoDisplay, and mupen64plus is now hidden too.
- [ ] 9.2 *Done offline (Professor D10):*
  - `src/wyoh/wyoh_apps.py` validates `wyoh-app.toml` (required keys; `input`, `window` and `gpu` checked; launcher, icon and SHA-256 checked) and generates:
    - one `wyoh-app-<id>.desktop` per app (Exec = the app's `run`);
    - `Hidden=true` overrides;
    - `generated/sway-apps.conf`, included by `sway.conf`;
    - `generated/app-profiles.toml`, merged by the daemon through `app_profiles_file`.
  - `make wyoh-luna-apps` runs it on Luna and reports menu IDs it doesn't find there.
  - The calculator has its manifest and `run` (`SDL_VIDEO_WAYLAND_WMCLASS=wyoh-calculator`).
  - 18 tests.

  Not yet run on Luna. Original item: App convention: the `wyoh-app.toml` manifest (as in the reply to Professor), a `run` launcher, and Wyoh-generated `.desktop` entries; deploy and Make targets.
- [ ] 9.3 *Offline part done: `Config.app_profiles`, `GamepadCore.focus()`, the `Grab` action, raw mode (FN+B and recovery still ours; recovery takes the gamepad back), and the daemon's Sway focus subscription; 7 new tests, 188 Wyoh offline tests pass. Live check pending.* Per-app gamepad profiles in the daemon, keyed by Wayland app_id: `keys`, `pointer`, or `gamepad-raw`. With `gamepad-raw`, the grab is released while the app has focus, and recovery and FN+B are still read. Deterministic tests.
- [ ] 9.4 *Prepared offline (D10):*
  - `deploy/luna/menu.toml` hides htop, nvtop, cups (Manage Printing), mpv, gmu and Wyoh's old `bc` calculator.
  - A test builds the menu as fuzzel would see it (Wyoh's directory first) and checks it holds exactly Calculator, Image Viewer, Task Manager, Terminal and Text Editor, plus any other system entry. ArchR's VLC, for example, is not hidden; nobody asked for that.
  - ArchR's real desktop-file IDs (gmu especially) are verified at deploy time.

  Original item: Menu clean-up: hide ArchR's duplicate Htop, Manage Printing and nvtop with `Hidden=true` overrides; replace the `bc` calculator. **mpv and Gmu: hidden** (Professor D6, confirming the user's default; reversible).
- [ ] 9.5 *Desk check skipped (D10 item 4): this desk has no Sway, so `wyoh_calc.py` has not run anywhere yet.* *Window written: `wyoh_calc.py`, SDL2 and SDL2_ttf through ctypes (no pygame needed), Windows 3.1 look, gamepad selection, keyboard and pointer input; not yet run on Luna.* *Core done: `src/wyoh/apps/calculator/calc_core.py` (Decimal arithmetic, left to right, repeated `=`, 12 digits, Error; 4 × 5 keypad with wide 0 and tall =, and gamepad selection moves), 32 tests. The window waits for the runtime check (pygame or SDL2).* Calculator: pure core with deterministic tests, plus a flat-grey window with 18 keys (Windows 3.1), gamepad-driven.
- [ ] 9.6 Files: Commander (SDL2), built on `luna-pi`.
- [ ] 9.7 **Chess (in progress, 2026-10-11).** pygameUCI needs pygame, which Luna lacks (9.1). So Wyoh writes a small chess app the same way as the calculator, keeping what the user chose pygameUCI for: a flat 2D board, a gamepad cursor, and PGN files.
  - **Built from:** SDL2 and SDL2_ttf through ctypes (shared with the calculator), python-chess 1.11.2 (pure Python, GPL-3.0+) for the rules and PGN, and Stockfish 17 from Debian arm64 (`stockfish_17-1_arm64.deb`, SHA-256 `114c2280…69881`; needs glibc 2.38 and libstdc++ 13, and Luna has 2.40 and GCC 14) with threads and hash capped.
  - **Controls:** cross = cursor, A = take/place, B = cancel, Y = undo the last move pair, X = new game.
  - **Process:** a pure core with tests, the window, an assembly script for Stockfish and python-chess under `/storage/.local/opt/`, then a live scenario.

  Original item: Chess: pygameUCI with Stockfish (threads and hash capped).
- [x] 9.8b **Wolfenstein controls — done 2026-10-13.**
  - New `gamepad-virtual` profile: `app_pad` in the core, `PadButton`/`PadAxis`, the daemon's uinput joystick "wyoh-game-pad" (16 buttons, analog sticks, created at start), and a `[pad]` table in manifests. The launcher keeps SDL to that joystick (`SDL_GAMECONTROLLER_IGNORE_DEVICES_EXCEPT=0x1209/0x0012`).
  - **Mapping:** A and R1 fire/validate; B and L1 open doors/back; Y run; X strafe; L2/R2 change weapon; cross and Start are keys.
  - **Icon:** BJ's face cropped from the port's cover (`fetch_wolf3d.py`), seen in the menu (`results/wyoh/wolf3d-probe/20261013/menu-with-icon.png`).
  - **Evidence:** live scenario passed (`results/wyoh/luna-apps/20261013T203744Z`, inspected). A through the menus to Floor 1; left stick forward; R1 fired (ammo 8 → 7); L1 opened the door; FN+B closed.
  - **Tests:** 7 new core tests; 276 Wyoh offline tests pass.
  - **Accepted by the user (2026-10-13):** controls and icon are right.
  - Controls added to the reference `0512_01` (checked by `test_luna_controls_reference.py`). **To do:** the cheat sheet (its language is still the user's choice).

  Original feedback:
  - **Regression:** in an earlier session the user played with both sticks (the game read the real gamepad, `gamepad-raw`). The 9.8 key profile moved the sticks to the pointer and left the game on the cross.
  - **Wanted:** both sticks back. R1 fires (right hand), L1 opens doors (left hand). A also fires and validates; B also says "no" (back) and opens doors. The user felt A and B were swapped (on the R36, B is SDL button 0).
  - **Design (Wyoh):** a `gamepad-virtual` profile. The daemon keeps the real gamepad and feeds the focused game a remapped uinput joystick: sticks passed through as analog; A and R1 → game button 0 (fire / select); B and L1 → game button 1 (use / back). ECWolf's config binds attack to 0 and use to 1, and nothing else on the shoulders. FN+B and recovery stay Wyoh's.
  - **Also:** the menu icon (the `./wolf3d.png` fix was never deployed).
- [x] 9.8 **Wolfenstein 3D works on Luna (2026-10-11).**
  - The live scenario passed (`results/wyoh/luna-apps/20261011T190536Z`, inspected). From the menu ("wolf"), X goes through the menus to Floor 1; the cross held up, R1 (fire: ammo 8 → 7) and A (open) move through the first door; FN+B closes it.
  - Per-app key map in its manifest; `app_keys` in the core, `wyoh_apps` and the generated profiles; 8 new tests, 253 offline tests pass.
  - Icon fixed to `./wolf3d.png` after the run, so the menu shows the cover (to see at the next deploy).

  Preparation history:
  - `src/wyoh/apps/wolf3d/`: `wyoh-app.toml` (gamepad-raw, full screen), `run` and `fetch_wolf3d.py`. The script takes ECWolf (aarch64, glibc 2.17), `ecwolf.pk3`, the 8 shareware `.WL1` files, a libjpeg and the cover from PortMaster's wolf3d port at commit `d36a1c22…`, and writes the manifest with each file's SHA-256.
  - Assembled in `results/wyoh/wolf3d-build/20261011` (12 files verified by `wyoh_apps.load`).
  - `make wyoh-luna-app APP_DIR=… APP_NAME=wolf3d-ecwolf` copies it to Luna.
  - **On Luna (2026-10-11):**
    - ECWolf 1.4.1 runs: zero import errors, the daemon releases the gamepad when it takes focus (`raw_app`), about 66 MB RSS.
    - **Display:** ECWolf only takes 4:3 sizes, so 720 × 720 became 960 × 720 and was cropped, and SDL's own full screen shifts the image. Fix: a 720 × 540 window (its own `--config` and `--savedir` in the app directory), made full screen by Sway; the whole image shows, with a black band at the bottom.
    - **Startup:** 32 s with SDL's default audio (it waits for the absent PulseAudio), 3 s with `SDL_AUDIODRIVER=alsa`, now in `run`.
    - **Gamepad:** with `gamepad-raw`, ECWolf does not react to the virtual gamepad (it is not in SDL's controller database, or SDL does not open it). A **uinput keyboard works fully**: Enter goes through the main menu, the episode, the difficulty and **Floor 1 in play** (`results/wyoh/wolf3d-probe/20261011/kb-sequence.png`, inspected).
    - **Decision (Wyoh, recorded for the user):** Wolfenstein uses a **per-app key profile** instead of `gamepad-raw`. The daemon keeps the gamepad and maps: cross = arrows, A = Space (open/select), X = Enter, B = Escape, R1 = Ctrl (fire), R2 = Alt (strafe), Y held = Shift (run), L1 = Slate. To build in 9.3: `[keys]` in the manifest, `app_keys` in the generated profiles and in the daemon.
    - `make wyoh-luna-apps` now also reloads Sway, so new window rules apply.
    - Next: rebuild and redeploy with ALSA, then the gamepad test (virtual gamepad created before launch), then a live scenario.

  Original item: Wolfenstein 3D: engine from PortMaster `wolf3d` (shareware data), under Sway.
- [ ] 9.9 *Prepared offline (D10):*
  - `src/wyoh/apps/dino/make_night.py` builds Dino Love2D white on black: pinned commit `b4fbaa44…` with its source SHA-256 checked; sprite colours inverted with alpha kept and the levels stretched, so Chrome grey becomes white; `main.lua` clears to black.
  - The `.love` build is reproducible: `09e068c9…`. Provenance and a preview on black are in `results/wyoh/dino-night/20261009/`, inspected.
  - 3 tests.
  - **Needs Love2D 11.5 on Luna:** PortMaster's runtime is not checked yet.

  Original item: Dino: Dino Love2D white on black (sprite sheet inverted); fallback pygame-dino if Love2D's GL path fails under Sway.
- [ ] 9.10 *In progress (user, 2026-10-15 "a very, very simple browser", again 2026-10-30 "we have no browser… something very simple that can reach the Internet a minimum").* Assembled 2026-10-15 by `src/wyoh/apps/netsurf/fetch_netsurf.py` (PortMaster netsurf port at d36a1c2: `nsfb`, `libs.aarch64` with sdl12-compat on the system SDL2, resources; Wyoh's Choices: images, backgrounds, animations and JavaScript off, DuckDuckGo Lite as home and search, 16 MiB disc cache) into `results/wyoh/netsurf-build/20261015T001447Z`; manifest "Browser", fullscreen, pointer profile; `run` launcher. Not yet run on Luna: the first install failed when Luna left the home network (2026-10-15). Luna is now on Arch Linux ARM: the libraries must be checked again. Asked Mannie from Luna for its go (2026-10-30). **First run on luna-pi (2026-10-31, the user: "test locally, not on Luna")**: in luna-pi's 720x720 headless Sway, nsfb opens DuckDuckGo Lite (Done 0.2 s), a DuckDuckGo search (0.2 s) and fr.wikipedia.org/wiki/Lune (Done 15–23 s, about 200 MB RSS), screenshots inspected (`results/wyoh/luna-pi-netsurf/20261030T232646Z/`, `test/wyoh/test_luna_pi_netsurf.py` + `.feature`). Two library findings: the port's `libwayland-client` is too old for the system EGL (`wl_display_create_queue_with_name`), so `fetch_netsurf.py` no longer takes it; Debian 13 lacks `libjpeg.so.8`, which Arch Linux ARM has, so luna-pi used Ubuntu's libjpeg-turbo8 beside the test bundle only. By hand, without the test: Google search stops on its cookie-consent page (no JavaScript), so DuckDuckGo Lite stays home and search. Text is a small bitmap font; no gamepad or Slate input checked yet. Next: Luna (Mannie's go), with its memory beside Kroko. Original item: Browser: NetSurf with images off. Test Google without JavaScript on Luna; fall back to FrogFind, then DuckDuckGo Lite. Record the evidence.
- [ ] 9.11 *Calculator and Files done (2026-10-11):*
  - `test/wyoh/test_luna_apps.py` + `luna_apps.feature` passed in 45 s (`results/wyoh/luna-apps/20261011T103418Z`, 10 frames + overview inspected);
  - the menu holds exactly Calculator, Files, Image Viewer, Task Manager, Terminal and Text Editor;
  - the calculator computes 3 × 7 = 21 with the cross and A; Files opens full screen and its selection moves; FN+B closes each.
  - Files icon: Commander's own `folder-open.svg`, verified in the menu (`results/wyoh/luna-apps/20261011T104611Z/04-files-menu.jpg`).
  - Open: Wolfenstein, chess, Dino and NetSurf are still to do.

  Original item: Per-app live scenario (launch from the menu with the buttons, use, close with FN+B; inspected screenshots; RSS) and acceptance.
- [x] 9.12 **Mannie in the menu, larger fonts — done 2026-10-13 (user's request and direct Luna grant).**
  - Menu entry "Mannie" (`share/applications/wyoh-mannie.desktop`): Claude Code from `/storage/.local/bin/claude` in foot (app id `mannie`), started in `/storage`. Claude's own first-run question (trust `/storage`) is the user's to answer.
  - Terminal font 50 % larger: Wyoh's `deploy/luna/foot.ini` sets `monospace:size=12` (foot 1.19's default is 8 pt; Luna has no user foot config). Used by Terminal, Text Editor, Mannie and Sway's `$term`.
  - Slate font 20 % larger: 12 px → 14 px (`gamepad.toml`).
  - **Evidence:** `test_luna_apps.py` with a new Mannie and Terminal scenario passed (`results/wyoh/luna-apps/20261013T212939Z`, menu, Mannie and Terminal frames inspected); `test_luna_slate.py` passed (`results/wyoh/luna-slate/20261014T225613Z`, 14 px text inspected). A first Slate run right after the deployment failed and was not investigated; the two reruns passed. Luna rebooted and released.

### Step 10 — Icons on the desktop
**Status**: ⏳ Pending — proposal written ([`docs/1000_01_desktop-icons-proposal.md`](docs/1000_01_desktop-icons-proposal.md)). Professor (D7, 2026-10-09): **not green-lit tonight**. Wyoh's recommendations (FN+Select, a "Pin to desktop…" entry, default icons) are noted as provisional; the GPL-3.0 question stays with the user.

- [ ] 10.1 Survey existing wlroots desktop-icon programs without GTK; record the result.
- [ ] 10.2 `wyoh-desk`: a bottom-layer surface with icons on a grid, positions kept in `/storage/.config/wyoh/desktop.toml`, observable state.
- [ ] 10.3 Gamepad: enter the desktop (FN+Select proposed), move the selection, A launch, X + D-pad move an icon, Y unpin; the pointer drags.
- [ ] 10.4 Pin from the menu ("Pin to desktop…" entry proposed).
- [ ] 10.5 Deterministic and live tests with inspected screenshots; budget.

### Step 12 — Mycroft in the Slate
**Status**: 🧪 In progress — green-lit by the user on 2026-10-11 ("je voudrais que tu travailles un peu sur le step 12… branche-le, fais tous les branchements et je ferai les tests"). Wyoh wires everything and tests with Mycroft's `--fake` mode; the user does the real voice test. Earlier: requested on 2026-10-09 ("et après tu intégreras Mycroft à Slate"), to follow Step 9. Mycroft proposed the interface in [`docs/0600_02_note-from-mycroft-dictation-in-slate.md`](docs/0600_02_note-from-mycroft-dictation-in-slate.md) (its Step 7); Wyoh replied in section 6 of that note

Goal: speech becomes text in the Slate, where the person corrects it with the buttons and sends it with L2, as the intent of Step 5 already foresaw.

- [x] 12.1 Boundary agreed in principle (Wyoh's reply to Mycroft's note):
  - Mycroft provides a separate `mycroft_dictate` process that emits `ready`, `partial`, `final` and `error` JSON lines and stops when its stdin closes; Mycroft's side needs its own green light;
  - the gamepad daemon starts the process and passes its lines to the Slate as `provisional` and `insert` operations;
  - the Slate owns the text, shows provisional text underlined, and ends dictation on any edit;
  - **Control (user, 2026-10-09):** L2 starts and stops dictation (see 6.9).
- [x] 12.2 **Wiring done and verified with the fake provider (2026-10-11).**
  - **Daemon:** `dictate_command` (the real command deployed); L2 starts or stops the provider; its lines become Slate operations (`split_lines`, `slate_operations`: ready → listening, partial → provisional, final → insert, error → shown); the Slate's `stop-dictation` (any key) closes its stdin; hiding stops it, and closing or sending kills it; `dictation` and `dictation_exit` in the status; stderr goes to `/run/wyoh/dictation.log`.
  - **Slate:** provisional text underlined at the cursor (not part of the text); "dictation: loading… / listening (L2 stops)" in the hint; `insert_dictated` adds a separating space.
  - **Tests:** 13 new deterministic tests (266 Wyoh offline tests pass). Live: `WYOH_LUNA_LIVE=1 uv run pytest -m live test/wyoh/test_luna_slate_dictation.py` passed (`results/wyoh/luna-slate-dictation/20261011T201903Z`, 4 frames inspected). It switches the daemon to `mycroft_dictate.py --fake "bonjour luna"` and restores the real command afterwards: provisional "bonjour" underlined, then "bonjour luna" inserted after "echo ", sent with FN+A, and the terminal wrote it to the file.

  Original wiring notes:
  - **Provider on Luna:** `mycroft_dictate.py` (Mycroft Step 7.4, contract `worklines/mycroft/docs/0704_01`), installed by Mycroft under `/storage/.local/share/tanstfaafllm/mycroft/`, assets under `/storage/.local/opt/mycroft/`.
  - **Daemon command:** `--input /dev/snd/pcmC0D0c --assets /storage/.local/opt/mycroft --threads 2` (Mycroft 8.2: 2 threads is best).
  - **Expect on Luna (Mycroft 8.1–8.3):** about 17 s to load the model, decoding slightly slower than real time, about 250 MiB while dictating. The microphone path is unproven (Luna Step 8).
  - **Behaviour:** L2 starts dictation; the Slate shows "loading…", then "listening", and provisional text underlined at the cursor. L2 again, or any key, stops it; the final text is inserted at the cursor. Hiding, sending or clearing the Slate stops it too.

  Original item: Wyoh side: the control, the daemon's process handling, the Slate's `provisional`/`insert` operations and "loading…/listening" hint; deterministic tests and a live test against a fake dictation process.
- [x] 12.4 **Kroko, resident (user decisions 2026-10-13) — closed 2026-10-25 at Professor's request (for the user): resident Kroko deployed 2026-10-15, the user's voice tests worked. What remains is 12.5.**
  - Switch dictation to Kroko (`kroko-fr-2025`; ~160 MiB on `luna-pi` against ~252 MiB on Luna for the current model) and test it on Luna.
  - The model stays loaded: hiding and showing the Slate must not cost a reload.
  - **Mycroft's part** (note `worklines/mycroft/docs/0903_03_note-from-wyoh-kroko-resident-in-slate.md`): Kroko files and current scripts on Luna, a Luna measurement, the licence, and a resident mode (proposed: `--resident`, stdin `start`/`stop`, idle between utterances).
  - **Wyoh's part:** start the provider at the first Slate opening and keep it alive while hidden; FN+A keeps the Slate process (send, clear, hide); L2 → `start`/`stop`; `--model kroko-fr-2025` once installed.
  - ~~Blocked on Mycroft's resident mode~~: Mycroft delivered it (0903_03 reply, note `docs/1204_01`); the user asked for Kroko in the Slate "as soon as possible" (2026-10-15).
  - **Done (2026-10-15):** `ResidentDictation` in the daemon (pure state machine, 9 tests): the provider is launched when the Slate opens, kept while hidden or closed, L2 sends `start`/`stop`, a start asked during loading runs once ready. `gamepad.toml` uses `--resident --model kroko-fr-2025`. FN+A still ends the Slate process; the provider survives it, so the Slate process did not need to stay. Live with the fake resident provider: same process after hide/show, L2 listening again at once (`results/wyoh/luna-slate-dictation/20261014T232841Z`); the full scenario still fails on its own timing (it stops before the fake has spoken; fix written but not run, interrupted by the user). An interrupted run left the fake command on Luna; restored by hand.
  - **User test (2026-10-15):** Kroko works by voice. Feedback: B during dictation behaves well; A put the new line before the dictated words. Fixed (`KeyHold` in the Slate, 5 tests): a key while listening stops dictation and acts once the text is inserted. Not yet deployed: Luna was rebooting.
  - **Second user test (2026-10-15):** A still put new lines before the dictation (fix not yet deployed), and FN+A while dictating sent nothing. Fixed: FN+A / FN+Y while listening stop dictation, insert the text, then send (3 s fallback). The user also asked for **L2 on the desktop** to open the Slate straight into dictation (L1 stays the keyboard way in), and for **no wait at the first opening**: the daemon now opens the Slate hidden when the session starts (`zone_preload`) and Kroko loads then.
  - **Deployed (2026-10-15, after Luna came back from the user's Wi-Fi test):** 30 s after the daemon restart, the Slate was hidden (screenshot `results/wyoh/wifi-probe/20261015/after-preload.png`: desktop only), Kroko loaded and idle on the USB-C headset (`/dev/snd/pcmC1D0c`), the real resident Kroko command in place. 340 offline tests pass. The user's check follows.
  - **Every send ends with Return (user, 2026-10-15):** FN+A (and FN+Y) type the text, then Return, so a terminal runs it and Mannie answers; Mike's FN+B will do the same. Deployed; Slate hidden and Kroko idle again after the restart. The live Slate scenarios still press A after sending: they must be updated (an extra empty Return).
  - **X types "/" in the Slate (user, 2026-10-15; was Delete):** for agents' commands. Dictation right after a word-starting "/" is joined, lower case, end punctuation dropped ("/" + "Usage." → "/usage"). Deployed; 345 offline tests pass. Delete is no longer on a button in the Slate.
- [x] 12.3 **Closed 2026-10-25 at Professor's request (for the user): the USB-C headset settled it (2026-10-13), and the user's voice tests on 2026-10-15 used it.** Earlier: **Blocked on a microphone (2026-10-11).**
  - The user tested through the interface: no dictation with a 4-pole jack headset or a microphone-only jack.
  - The user thinks the jack is output only. Luna's `0802_01` suggests the line is wired but not enabled by ArchR. Note to Luna: `worklines/luna/docs/0800_01_note-from-wyoh-jack-microphone-user-test.md`.
  - **Settled by Luna's 8.2c (2026-10-11):** with the codec set at runtime to the factory driver's capture values, the jack still gave no signal. The jack's microphone contact very probably doesn't reach the codec. **Dictation needs a USB-C microphone.**
  - The daemon picks a USB capture device when one is present (`{capture}`, deployed 2026-10-11). Luna records the device names (its 8.2d) when one is plugged in.
  - **2026-10-13: a USB-C headset works** (Luna's note `0800_01`: TTGK "LUDOS Earphones", ALSA card 1 `Earphones`, `/dev/snd/pcmC1D0c`, S16_LE stereo, 48 kHz only). Mycroft's capture opens `plughw:C,D` at 16 kHz mono, so ALSA converts. The user asked Wyoh to continue the integration ("continuez l'intégration"): check the device choice and a real provider start on Luna, then hand over the voice test.
  - **Checked on Luna (2026-10-13):** the headset is card 1 with `usbid 3302:3b77`. The deployed daemon's `choose_capture()` returns `/dev/snd/pcmC1D0c`. A real `mycroft_dictate.py --input /dev/snd/pcmC1D0c --threads 2` sent `ready` after 19.7 s, then an empty `final` when stdin closed (silence) and exit 0. Luna rebooted. **Handed to the user for the voice test.**

  Earlier: The user's real voice test (handed over 2026-10-11): L1, L2, speak French, L2. The microphone path (`/dev/snd/pcmC0D0c`, rk817) is unproven (Luna Step 8): if nothing is recognised, `/run/wyoh/dictation.log` and the `dictation` status say why. Expect about 17 s of "loading…" before "listening".
- [ ] 12.5 **Open after 12.4 (Professor, 2026-10-25, for the user):**
  - the user's final check of dictation in the Slate (Mycroft closes its side, 7.5, 8.7, 8.8, at the same time);
  - the live Slate scenarios (`test_luna_slate.py`, `test_luna_slate_dictation.py`) still press A after a send, which now adds an empty Return: update them;
  - the timing fix for `test_luna_slate_dictation.py` (wait for the fake's words after hide/show) was written but never run, interrupted by the user;
  - not run on Luna since: 6.10 (FN+Y, FN+B, history) beyond deployment, and the NetSurf probe (9.10).
  - Luna is off and held by Mannie (2026-10-25): no Luna work until it is given back.

### Step 13 — Wyoh's session on a new Luna root (note only)
**Status**: 📝 Noted 2026-10-25 at Professor's request, for the user's decisions of that day (`worklines/mannie/plan_mannie.md` Steps 6 and 7): Mannie operates Luna, and ARCHR_ROOT may be replaced by an Arch Linux ARM root, keeping BOOT, LUNA_HOME and STORAGE. A user `michael` exists (Luna's note `worklines/professor/docs/0000_04`). No change is asked of Wyoh now. The list below is also a note to Mannie: [`worklines/mannie/docs/0702_01_note-from-wyoh-session-needs-on-a-new-root.md`](../mannie/docs/0702_01_note-from-wyoh-session-needs-on-a-new-root.md).

- **Luna access rule (user, 2026-10-25, relayed by Professor; in `skills/cell-coordination`, AGENTS.md and `worklines/luna-access.md`):** Mannie runs on Luna as a Claude session ("Mannie from Luna" in ListAgents) and is Luna's operator. Wyoh may message it directly about Luna operations. **No SSH to Luna without first telling Mannie from Luna what will run and getting its "go". Never reboot Luna while Mannie runs there:** ask it to save and stop first, and tell it when done. Mannie's open checks of Wyoh's session on the new root are `plan_mannie.md` 7.6: the calculator and Wolfenstein fail there (Arch Linux ARM's GLES SDL2 file name differs), a "focus subscription" error in `wyoh-gamepad`'s journal, the MCP harness with `HOME=/storage`, the Mannie entry still starts root's Claude.
- **Messaging (user, 2026-10-30, relayed by Professor):** the ban on cell members messaging each other is lifted; any session may be messaged directly (roster `worklines/agents.md`; Mannie from Luna is [32d5e1]). Still in force: requests land in the plan; no SSH to Luna without Mannie on Luna's go; never ask a peer to do what Wyoh's own permissions blocked.
- [x] 13.0 **Wolfenstein's buttons dead since the Slate preload (reported by Mannie from Luna through Professor, 2026-10-30).** Cause: `gamepad-virtual` routing required `zone_state == "closed"`, but `zone_preload` (525bce8) keeps the Slate `hidden` from session start, so buttons and sticks went to the desktop path. Fixed in the core: the game keeps its joystick while the Slate is closed or hidden. 1 new test; 346 offline tests pass. **Deployed and verified live by Mannie from Luna (2026-10-30 21:34):** the same two conditions applied on Luna (backup `.bak-20261030`); with ECWolf focused, L1 → 0x131, R1 → 0x130, L2 → 0x134, R2 → 0x135, both sticks on the virtual pad, Slate hidden. Mannie asks Wyoh to commit its version; the commit waits for the user's authorisation.
- [x] 13.0b **Wolfenstein's keys dead on the new root (user, 2026-10-30: "connect to Luna and fix Wolfenstein").** Root cause found by Mannie from Luna: ECWolf uses SDL's GameController API, and Arch Linux ARM's SDL2 is sdl2-compat on SDL3, which auto-maps wyoh-game-pad (index 0 → A, 1 → B, 3 → X, 4 → Y, 6/7 → shoulders 9/10; 2 and 5 reach nothing). Fix (repo and Luna, Mannie told before each step): `[pad]` Y=3 (run), X=4 (strafe), L2=6, R2=7; `ecwolf.cfg` and `ecwolf.default.cfg` Next weapon 9, Prev 10. Mannie's suggestion to move turning to 36/37 was wrong: measured on Luna, 36/37 is the right stick's **Y** in ECWolf's numbering, so turning stays on 38/39 (right stick X). Checked live with Wyoh's virtual gamepad (after the daemon's 5 s hotplug scan): A through the menus to Floor 1, L2 → knife, R2 → pistol, right stick X turns, right stick Y does nothing (`results/wyoh/wolf3d-probe/20261030/`, frames inspected). Backups on Luna: `wyoh-app.toml.bak-20261030b`, `ecwolf.cfg.bak-20261030b`; `ecwolf.cfg` root 0644. Daemon restarted once (Kroko reloaded). Not yet checked by the user's hands: Y run, X strafe. Also seen: Commander's icon (`/usr/share/commander/...`) is missing on the new root, so `wyoh_apps.py` reports an error for Files. **Mannie's account (2026-10-30, at the user's request):** on 10-29 ECWolf needed `sdl2_mixer` on the new root (installed by Mannie with `pacman -Syu`, Landlock-less kernel so `DisableSandboxFilesystem`); sdl2-compat on SDL3 dates from the root's build on 10-25. `ecwolf.cfg` was only rewritten by ECWolf's own exits (10-29 19:30, 10-30 21:51), never edited by hand. The floating window came from Mannie's focus commands or from L1 opening the Slate while bug 13.0 was live (not established). Mannie accepted the three mistakes in the how-to's section 8 as rules. Add `sdl2_mixer` to Step 13's package list.
- **Menu tidied by Mannie from Luna (user's request "tidy the menu", 2026-10-30):** `foot.desktop`, `footclient.desktop`, `foot-server.desktop` and `vim.desktop` (from the new root's packages, duplicates of Terminal and Text Editor) added to `deploy/luna/menu.toml`'s hide list, deployed and regenerated on Luna (8 entries on one page, screenshot checked by Mannie); reaches `main` through Mannie's PR from `cell/mannie`. Open on Wyoh's side: **Files (Commander) is missing from the menu** (its icon, and probably the `commander` package, are absent on the new root; see 13.0b), and **Mannie and Terminal share the same icon**.
- [x] 13.0c **The Mannie menu entry opens Mannie's running session** (Mannie's note `docs/0000_09`, user's request 2026-10-25): `wyoh-mannie.desktop` now runs `runuser -l michael -c '/home/michael/.local/bin/mannie open'` in foot (app id `mannie` kept, so FN+Y still finds it), as Mannie already deployed on Luna. Repository copy updated 2026-10-30; not yet committed.
- [ ] 13.1 What Wyoh's session needs on a new root: packages, the session user, services, devices, the GPU path (the note holds the list).
- [ ] 13.2 Move the session from root to `michael` (Luna's 0000_04 asks Wyoh to check it): needs its own green light.

### Step 11 — Productise only the selected agent-native workspace path
**Status**: ⏳ Pending

- [ ] 11.1 Fork/pin only the selected upstream; retain licence, provenance, and upgrade strategy.
- [ ] 11.2 Implement only the approved Sway configuration, capability mediator, and/or Wyoh adapter; retain the Step 5 controller mapping and recovery and deterministic startup.
- [ ] 11.3 Add contract tests and target smoke tests for state, events, focus/layout operation, capability rejection, focused input fallback, wait, process exit, malformed/stale request, and restart.
- [ ] 11.4 Acceptance: Luna boots a recoverable agent-native Wyoh workspace and passes its selected Sway/adapter contract suite inside its measured budget.

---

## Progress tracking ✅

- ✅ Full discussion reviewed for Wyoh’s mandate and constraints.
- ✅ Upstream survey and requirements/solution proposal recorded.
- ✅ Step 1 — Sway-v0 contract and product path ratified.
- ✅ Step 2 — Pre-hardware Sway-IPC proof passed.
- ✅ Step 3 — Pi-specific Sway validation recorded.
- ✅ Step 3.5 — Development-only full Sway-IPC MCP bridge validated over SSH.
- ⚠️ Step 3.6 — Shared owned Sway, MCP, and WayVNC session; rendered-client proof invalid (corrected 2026-10-04).
- ✅ Step 3.7 — Minimal workable Sway environment operated through MCP, with inspected screenshots.
- 🧪 Step 4 — Physical Luna stock-image inventory in progress; production base remains unselected.
- 🧪 Step 5 — Device interactors: built, proven in simulation, boots into the session; awaiting the user's physical check.
- 🧪 Step 6 — Slate (multi-line input) and backup on-screen keyboard: built, passing on Luna in simulation; user check and whole-cross calibration open.
- ⏳ Step 7 — Wi-Fi network selection from the buttons: proposal, decisions open.
- 🧪 Step 9 — Graphical applications and menu clean-up: green-lit 2026-10-09, Wyoh assembles and integrates; Luna SSH unreachable for now.
- ⏳ Step 10 — Icons on the desktop: proposal, decisions open.
- ⏳ Step 12 — Mycroft in the Slate (after Step 9; boundary note to Mycroft).
- ⏳ Step 11 — Productise the selected agent-native workspace path (was Step 6, then 8).

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
| 2026-09-27T20:29:12+02:00 | Prepared a pending development-only MCP-over-SSH follow-on. It is now a full Sway-IPC mapping, including all documented requests and subscription events, only for an owned disposable headless child in explicit development mode; no dependency, server, SSH configuration, Pi state, or runtime implementation was changed. |
| 2026-09-28T08:38:59+02:00 | Step 3.5 completed after explicit green light: a Python MCP 2.2.0 client used SSH-carried stdio to exercise the complete documented Sway 1.10.1 IPC mapping on an owned headless `luna-pi` child. Deterministic checks and the passing live test record all request/event mappings, observed workspace/tick/shutdown events, headless-fixture event limits, ambient-socket rejection, and cleanup. No listener, persistent service, live desktop attachment, rendered UI, or Luna compatibility claim was made. |
| 2026-09-30 | Step 3.6 completed after explicit green light: a user-owned loopback Sway + WayVNC service was deployed through a previewable Make path; descriptor-bound MCP control, screenshot metadata, and an independent VNC frame change for an MCP-launched terminal passed. The retained Labwc unit remains the recovery path. |
| 2026-10-04T00:34:10+02:00 | Workline taken over by a new agent. Reviewed every record and fixed stale/contradictory statements; introduced the uv-managed project environment (`pyproject.toml`, `uv.lock`, `pytest.ini` `testpaths`); re-ran the deterministic suite (43 passed) and all four Wyoh `luna-pi` live tests (4 passed) without changing `luna-pi`. Conclusions and proposed Step 4 re-scope in `docs/0400_01_takeover-review-and-luna-pi-revalidation.md`. |
| 2026-10-04T00:55:00+02:00 | User reported that the Step 3.6 "terminal-visible" capture shows only the Sway background and that the VNC session is unusable. Visual inspection confirmed it: the VNC test captured on the `window` event before the first frame, and its "before" frame contained a leftover terminal. Direct grim/VNC captures show rendering works. Corrected Step 3.6 and `0306_03`/`0400_01`; proposed Step 3.7 (minimal workable environment plus an inspected MCP proof). No `luna-pi` configuration changed; one diagnostic `lxterminal` was opened and closed. |
| 2026-10-04T01:25:00+02:00 | Step 3.7 completed after explicit green light: usable 720×720 Sway session (Alt/AZERTY bindings, swaybar, foot, wmenu, wtype via apt as root) and an MCP + VNC scenario whose nine steps were visually inspected in two passing runs. Deterministic suite 43 passed; Wyoh live suite 4 passed. Findings: WayVNC placeholder first frame; `wmenu` aborts on transient virtual keyboards; lossy MCP list encoding; screenshot collision fixed. |
| 2026-10-04T22:55:00+02:00 | Step 4.7 by user direction: inventoried ArchR (Sway 1.11, no GPU driver, no wtype/WayVNC), installed a non-enabled `wyoh-sway.service`, MCP 2.2.0 venv, and `wtype` under `/storage` only, and ran the Step 3.7 scenario on Luna's DSI panel through MCP (passed; eight settled screenshots inspected). Session ≈ 46 MiB. Physical-panel check by the user pending. |
| 2026-10-04T23:10:00+02:00 | User stopped further installs on the ArchR card (`/` 97% full) and asked for a Luna-side image rework with ≥ 20 GB `/`, `/home`, and multiple users. Wyoh stopped its session, removed a partial `mousepad`/`gtksourceview4` copy, and wrote the coordination note `worklines/luna/docs/0000_07_note-from-wyoh-image-limits-and-storage-layout.md`. Measured on `luna-pi`: `mousepad` 48 MB RSS vs `foot`+`nano` 15 MB, so Wyoh will use terminal applications, not GTK ones. |
| 2026-10-05T16:15:00+02:00 | Step 4.7 reproduction on the reshaped card: nine-step MCP scenario with a uinput keyboard as the person, `vim` as editor, MCP screenshots only (no VNC, by user direction). Passed (`20261005T141451Z`); all nine screenshots inspected. Fixed a double AZERTY remap in the uinput helper; found ArchR has no terminfo database and its `nano` ignores resizes; addendum sent to Luna. |
| 2026-10-05T17:00:00+02:00 | Step 4.8 fuzzel menu on Luna: installed, Windows 3.x palette, Papirus subset; 19-step interaction test passed and was inspected. The user reported a black panel, traced to the Mali GPU driver not being loaded under text-mode boot; the unit now loads it, and Sway renders on Mali-G31. Corrected 0407_01 and the Luna note. |
| 2026-10-07 | User decision: Luna's session stays root (single-user device, no keyboard, no password login). Recorded in key decisions and in the Luna note. |
| 2026-10-07 | Proposed Step 4.9 (gamepad daemon, mapping table, input zone owned by Wyoh for now) from the user's decisions and a read-only gamepad inventory; awaiting green light. |
| 2026-10-07 | Promoted the device-controls work from sub-step 4.9 to its own **Step 5 — Device interactors** (user request); the former Step 5 (productise) is now Step 6. Intent renamed `0500_01`. |
| 2026-10-07 | Step 5 built autonomously: gamepad daemon (49 core tests), MCP-simulated person, button-only scenario passed with 20 inspected screenshots, budget met after optimisation (17.5 MB, 0 ticks at rest, 3.8% with the stick), boot straight into the session with Mali (PATH bug fixed). User check 5.7 pending. |
| 2026-10-09 | User feedback applied: pointer on the right stick (R3 click), the user's wallpaper (MIME database fix), and a four-tile layout policy with a "Too many tiles" pop-up (layout scenario passed). Luna tests now share one multiplexed SSH connection (OpenSSH 9.8 PerSourcePenalties) and fetch JPEG frames settled by hash (Wi-Fi about 160 KB/s with stalls). The full button-only scenario has not re-passed since; its failures were link stalls. Committed at the user's request. |
| 2026-10-09 | Added Step 6 (Slate multi-line input and wvkbd backup keyboard) and Step 7 (Wi-Fi selection on iwd, stack owned by Luna) at the user's request, with proposals `0600_01` and `0700_01`; the user's ChatGPT discussion is kept raw as `0500_02`. Productise is now Step 8. Planning only; no code. |
| 2026-10-09 | Step 6 green-lit and built: `wyoh_slate.py` (multi-line editor in a floating foot window), Slate mode and whole-cross detection in the gamepad daemon, wvkbd 0.15 (AZERTY build from `luna-pi`) shown with the Slate, white border while open. 107 deterministic tests; the live Slate scenario passed with 20 inspected screenshots. Open: user check, whole-cross calibration, AZERTY re-run, memory slightly over target. |
| 2026-10-09 | 6.8 two-thumb typing (user request): pastel green and red selections on the AZERTY keyboard, steered by the left and right sticks, typed with L3/R3 (wvkbd patch plus core). 124 tests; the live scenario passed with the final build, 22 frames inspected. |
| 2026-10-09 | Added Step 9 (graphical apps and menu clean-up, from Professor's note `0900_01`, with Wyoh's reply in its section 6) and Step 10 (desktop icons, proposal `1000_01`, user request). Productise is now Step 11. Planning only; Luna did not answer SSH, so the runtime check is still to do. |
| 2026-10-09 | Step 9 green-lit by the user; Wyoh assembles and integrates the apps (sub-steps 9.0–9.11). Step 12 added: Mycroft in the Slate, after Step 9, by user request. Luna SSH times out at the banner exchange (ping works), so Luna-side work is blocked; offline work proceeds. |
| 2026-10-09 | Offline progress on Step 9: calculator core (32 tests) and per-app gamepad profiles (7 tests; 188 Wyoh offline tests pass). Step 12: Wyoh replied to Mycroft's dictation note (`0600_02`, section 6). Blocked: Luna and `luna-pi` both unreachable; questions put to the user. |
| 2026-10-09 | User answers: Luna is being rebooted and `luna-pi` is off; mpv and Gmu are hidden by default; new Slate controls (6.9): L1 show/hide, L2 dictation, FN+X clear, FN+A send + clear + hide. |
| 2026-10-09 | 6.9 core done; Luna cheat sheet (SVG and PNG) made at the user's request, because the controls were getting hard to follow. |
| 2026-10-09 | Step 9.1 partial: runtimes inventoried (SDL2 with Wayland, no pygame; Commander and RetroArch ecwolf already installed). Commander's captures are black (panel unknown); Luna dropped off the network after a GLES demo was started. Calculator window written (SDL2 via ctypes). Blocked again on Luna. |
| 2026-10-09 | Professor's delegated decisions for the user (log `worklines/professor/docs/0503_01`): D5 finish 6.9's daemon side offline (done); D4 go 5.12; D6 hide mpv and Gmu; D7 no Step 10 tonight; D8 Luna device work, the black Commander captures and 6.6 wait for the user, and the GLES demo is not repeated. |
| 2026-10-09 | 5.12 done (reference, 24-check test, superseded marks, cheat-sheet fixes). 6.9's daemon side done offline. Stopped as instructed: Luna device work (6.9 and 6.6 live checks, Step 9 deployment, Commander's black captures) waits for the user (D8). |
| 2026-10-09 | Professor D10 (for the user, inside green-lit Step 9; nothing touches Luna), in order: 9.2 manifest schema, validator, launcher convention, `.desktop` generation, Make targets and tests; 9.4 `Hidden=true` overrides and the new menu set, with a test; 9.9 prep: Dino Love2D source and the white-on-black sprites on the desk, with provenance; a headless-Sway check of the calculator on the desk if available. |
| 2026-10-09 | D10 done: 9.2 manifests and generation (18 tests), 9.4 menu set (test of the resulting menu), 9.9 white-on-black Dino build (3 tests, preview inspected); the headless calculator check was skipped (no Sway on the desk). 237 Wyoh offline tests pass. **Only Luna-dependent work remains; stopped** until the user checks Luna (D8). |
| 2026-10-09 | Luna rebooted by the user. Apps generated and the menu deployed on Luna. Found that Sway cannot import Mali client buffers (`eglCreateImageKHR failed`), so SDL/GL windows show nothing when composed; the user is asked to check full screen on the panel (9.1b). |
| 2026-10-09 | Professor D14 (for the user):
  - continue Step 9 on Luna around GL: force SDL's software path (wl_shm, not EGL) for the calculator and Commander, and check with grim;
  - if it works, put the setting in their `run` launchers and do Commander's live scenario (9.11);
  - no glmark2 or other GLES stress tonight; Love2D/Dino and other GL apps wait;
  - only files under `/storage/.local`; no boot, card or ArchR change; no commit;
  - 9.1b (the user's panel check) stays open. |
| 2026-10-09 | D14 test: SDL's software renderer still uses EGL under Wayland (same import errors), so the SDL route is closed. Stopped and asked the user: panel check, Xwayland without glamor (needs a unit change outside D14's limit), a note to Luna, or a shared-memory calculator. |
| 2026-10-11 | User decisions: no app needs the GPU (CPU rendering, shared-memory buffers); the split stays for now; a full-screen-only policy with quick app switching is a likely future step. Next: try Mesa's software EGL per app, then Xwayland without glamor. |
| 2026-10-11 | Experiment 1 (Mesa software EGL for the calculator): Mesa failed to create a DRI2 screen and the app exited; Luna then stopped answering SSH (ping still works), probably after Mesa touched the GPU. Stopped; asked the user to reboot Luna and choose between a safer Mesa retry and Xwayland without glamor. |
| 2026-10-11 | Correction: Luna was not blocked, only the desk's SSH stalled (the user's SSH and the panel worked). User rule: reboot Luna preventively after each test series. The user rebooted it. |
| 2026-10-11 | Experiment 1 dead end: Mesa rejects every software config under this Sway (EGL never initialises). Calculator fails cleanly now. Luna rebooted preventively. Asking the user to confirm experiment 2 (Xwayland without glamor; unit change and session restart). |
| 2026-10-11 | User: "essaie en gpu". Experiment 2 is set aside; Wyoh now tries to make Mali GPU apps display. G1: count Sway's import errors while the calculator redraws, windowed vs full screen (direct-scanout hypothesis). G2: inspect the client's buffer protocol, format and modifier (`WAYLAND_DEBUG`). Reboot after each series. |
| 2026-10-11 | 9.1b solved: `MALI_WAYLAND_DMABUF_PROTOCOL=1` makes Mali clients use linux-dmabuf. Calculator and Commander display and capture correctly. Variable added to both units and the apps' launchers; Commander manifest added. Known issue: `wtype` keys crash SDL2 apps, which affects Slate delivery to SDL apps. |
| 2026-10-11 | Professor (tanstfaafllm-80): Luna access is now arbitrated (`worklines/luna-access.md`). Wyoh holds Luna until the end of the current app series, about 13:30 at the latest, then reboots it, records the state and tells Professor "Luna released"; Mycroft (7.3b, speech-to-text measurements) goes next, and Wyoh resumes after. Offline work in the meantime (for example the wtype/SDL2 crash). Live run 1 of the 9.11 scenario: the calculator computed 21 with the gamepad and Files opened full screen; the Files check was fixed to use Commander's colours. |
| 2026-10-11 12:36 | 9.11 run 2 passed (calculator 21, Files, clean menu; inspected). Luna rebooted and **released** to Professor for Mycroft (7.3b). Wyoh waits for Luna to come back, and does offline work meanwhile (the wtype/SDL2 crash, the Files icon). |
| 2026-10-11 | Offline while Luna is with Mycroft: Slate delivery now types through the daemon's uinput keyboard (AZERTY table with Shift and AltGr; wtype only as a fallback), which avoids the SDL2 crash; 245 offline tests pass. Files icon pointed at Commander's own SVG. Both need a live check when Luna comes back. |
| 2026-10-11 12:43 | Professor: Luna back to Wyoh (Mycroft released it after a reboot; its speech-to-text uses about 250 MiB when running). Same rules. Next series: deploy, then live checks of uinput Slate delivery, the Files icon and the apps scenario. |
| 2026-10-11 12:47 | Verification series passed. Slate scenario: the 6.9 keys work live, and delivery goes through uinput ("echo aé" correct). Apps scenario: calculator 21, Files with its icon, clean menu. The Slate test now filters the menu with "term". Luna rebooted. Next: Wolfenstein 3D (RetroArch ecwolf, shareware data). |
| 2026-10-11 | Professor: Luna paused for Wyoh (the user gave it to Mycroft for about 25 min); no `ssh luna` until "Luna is yours". Not mid-series: Luna had just been rebooted after the verification series. Offline: preparing Wolfenstein 3D (9.8). |
| 2026-10-11 | Offline during the pause: Wolfenstein 3D assembled from PortMaster's wolf3d port (ECWolf + shareware data, checksums in the manifest) and the `wyoh-luna-app` Make target added; waiting for "Luna is yours" to deploy and test. |
| 2026-10-11 | Professor: Luna back to Wyoh (Mycroft finished and rebooted it). Series: deploy Wolfenstein 3D, regenerate the menu, first launch. |
| 2026-10-11 | Wolfenstein series: runs on Luna; display fixed (720 × 540 windowed, Sway full screen); startup cut from 32 s to 3 s with ALSA. Professor's pause (usage limit) was announced and lifted before this was written; resuming with the gamepad test. |
| 2026-10-11 | Wolfenstein: the gamepad is not seen in `gamepad-raw`, but the keyboard drives it fully to Floor 1. Next: per-app key maps (offline). Luna rebooted after the series. |
| 2026-10-11 19:06 | Per-app key maps implemented (`app_keys`); Wolfenstein 3D plays on Luna with the gamepad (scenario passed: Floor 1, fire, door, FN+B). Luna rebooted. Next in Step 9: chess, then Dino and NetSurf; also the controls reference and cheat sheet for Wolfenstein's keys. |
| 2026-10-11 | Professor relays two user rules: (1) language: everything written in English, the user is addressed in French (AGENTS.md); (2) original names restored: Mike = local brain, Mannie = frontier model. Wyoh's files already follow both, except the French cheat sheet `0609_01`, made in French for the user; whether to translate it is asked to the user. |
| 2026-10-11 | Step 12 green-lit by the user: wire Mycroft's `mycroft_dictate.py` into the Slate (daemon process handling, Slate provisional text and state), test with `--fake`, and leave the real voice test to the user. |
| 2026-10-11 20:20 | Step 12 wired: L2 starts and stops Mycroft's dictation, with provisional text underlined and the final text inserted. Live test with the fake provider passed; the real command is deployed. Luna rebooted. 12.3 (real voice) is handed to the user. |
| 2026-10-11 22:34 | Professor: Luna goes to Mycroft for about 20 min (its 9.3); no `ssh luna` until "Luna is yours". Wyoh was not mid-series (Luna rebooted after the dictation test). |
| 2026-10-11 | User: Mycroft now works on `luna-pi` and must not load Luna; Wyoh continues on Luna (Professor informed). Next in Step 9: chess (9.7). |
| 2026-10-11 | Professor confirms Luna is Wyoh's for 9.7 and the rest of Step 9. Chess approach: Wyoh's own SDL2 app with python-chess and Stockfish, since pygame is unavailable (recorded in 9.7). |
| 2026-10-11 | The user stopped the chess work (it was not what they asked: 9.7 paused, nothing written for it beyond the plan entry and the `chess` dev dependency). Then they tested dictation through the interface: no microphone on the jack (headset and microphone-only). Note left for Luna; next: a USB-C microphone, with automatic capture-device choice in the daemon. |
| 2026-10-11 | Luna replied in the note (8.1c recorded; 8.2b read-only register check; 8.2c register test to propose to the user). At Professor's request, Luna rebooted and **released** for Luna's 8.2b (about 10 min). Wyoh is not mid-series. Pending on Luna's return: deploy the `{capture}` choice (USB microphone) when the user has a USB-C headset. |
| 2026-10-11 | Luna back to Wyoh (Luna's 8.2b done). Deployed the `{capture}` choice (USB microphone if present, else RK817). Step 9 chess not resumed: the user had stopped it, so the next Step 9 item waits for the user. |
| 2026-10-11 | Luna **released** to Professor for Luna's 8.2c (codec register test, green-lit by the user, about 20 min). Wyoh is idle; Luna had just been rebooted after the `{capture}` deployment. The next Step 9 item waits for the user's choice. |
| 2026-10-11 | Luna back to Wyoh. Luna's 8.2c: no microphone on the jack, so 12.3 waits for a USB-C microphone (the daemon side is ready). |
| 2026-10-11 | Professor: hold off on Luna for about 10 min (Luna's 8.2d, a USB-C audio adapter tested with the user). Wyoh is idle; it waits for "Luna is yours". |
| 2026-10-11 | Luna back to Wyoh. Luna's 8.2d: the user's USB-C-to-jack adapter is passive (no USB audio device). 12.3 needs a real USB sound card or USB microphone, for example through the USB-C-to-A adapter that worked for the keyboard. Wyoh's daemon side is ready; nothing to change. The next Step 9 item waits for the user's choice. |
| 2026-10-11 | Professor: Mycroft has Luna for about 20 min (its Kroko test, 9.3); no `ssh luna` until "Luna is yours". Wyoh is idle. |
| 2026-10-13 | The user's USB-C headset works. User: continue the Mycroft integration (12.3). Luna was free (`luna-access.md`); Wyoh takes it and tells Professor. |
| 2026-10-13 | 12.3 preparation done on Luna: the daemon picks the USB headset, Mycroft's provider is ready after 19.7 s on it and exits cleanly. Luna rebooted; the voice test is the user's. |
| 2026-10-13 | User decisions: switch to Kroko and test it on Luna; the model must stay loaded (no 20 s wait after hiding the Slate). Note to Mycroft `0903_03` (Kroko on Luna, measurement, licence, resident mode); Wyoh's side recorded as 12.4. |
| 2026-10-13 | User feedback on Wolfenstein (9.8b): both sticks back (regression), R1/A fire, L1/B open doors and back, A/B no longer swapped, and an icon. Wyoh takes the free Luna for it. |
| 2026-10-13 | 9.8b done: Wolfenstein gets a remapped virtual joystick (both sticks analog, A/R1 fire, B/L1 doors) and a BJ-face icon; scenario passed; Luna rebooted and freed in `luna-access.md`. |
| 2026-10-09 | Professor (on the user's request) reviewed the cheat sheet and added sub-step 5.12: a Markdown controls reference checked against the code, plus four fixes to the sheet. Not started; it follows the green-light protocol. |

---

## Mycroft context amendment — 2026-09-25

A later Mycroft composition phase may consume a bounded Wyoh context snapshot. Wyoh remains the owner of observable state and finite advertised actions; it provides neither arbitrary desktop contents, shell authority, nor implicit command execution. The ratified Step 1 contract (`docs/0101_06_sway-v0-contract.md`) records this boundary; the detailed snapshot contract (consumer scope, revision/freshness, safely available labels/actions, truncation, and failure with no side effect) waits for a Mycroft-workline decision. No live Mycroft integration is authorised.

See [the planning-only boundary](docs/0101_04_mycroft-context-boundary.md).

### Amendment log

| Timestamp (`date`) | Update |
|---|---|
| 2026-09-25T23:10:00+02:00 | Added the planning-only Wyoh-to-Mycroft context boundary from the shared discussion. |

---

## Workline artifacts

Source records and superseded models (kept as evidence):

- `worklines/professor/docs/0001_01_initial_discussion.md` — complete source discussion.
- `worklines/wyoh/docs/0000_01_wyoh-mandate.md` — source-discussion decisions and unresolved facts.
- `worklines/wyoh/docs/0000_02_wm-candidate-survey.md` — upstream WM/compositor survey and selection rationale.
- `worklines/wyoh/docs/0000_03_wyoh-requirements-and-solutions.md` — requirements, resource envelope (150/200 MiB), and early solution paths.
- `worklines/wyoh/docs/0000_04_desktop-automation-model.md` — active conceptual model (DWOM): state, locators, interactions, and synchronisation.
- `worklines/wyoh/docs/0000_05_controller-first-handheld-model.md` — historical controller-first HIOM model; reference for stock-console and recovery surfaces.
- `worklines/wyoh/docs/0101_01_hiom_v0_contract.md` — historical original Step 1 HIOM contract.
- `worklines/wyoh/docs/0101_02_controller_first_discussion.md` — initial decision record and preserved French source; controller-only conclusion is historical.
- `worklines/wyoh/docs/0101_03_followup_discussion.md` — cleaned Sway-v0 follow-up discussion: component boundaries and implementation sequence.

Contracts and boundaries:

- `worklines/wyoh/docs/0101_04_mycroft-context-boundary.md` — bounded, revisioned future context snapshot.
- `worklines/wyoh/docs/0101_05_professor-note-on-mycroft-composition.md` — Professor coordination note on bounded Mycroft context.
- `worklines/wyoh/docs/0101_06_sway-v0-contract.md` — active Step 1 Sway v0, authority, component, and deferred-hardware contract.

Pre-hardware evidence (Steps 2–3.6):

- `worklines/wyoh/docs/0201_01_sway-ipc-proof.md` — Step 2 pinned IPC protocol, fixture, passing evidence, and limits.
- `worklines/wyoh/docs/0301_01_luna-pi-sway-result.md` — Pi-only board facts, Sway result, metrics, and limits.
- `worklines/wyoh/docs/0000_08_mcp-over-ssh-validation-proposal.md` — full Sway-IPC manifest, isolation boundary, tests, and acceptance for the development-only MCP bridge.
- `worklines/wyoh/docs/0305_01_mcp-over-ssh-validation-result.md` — Step 3.5 implementation, live evidence, request/event matrix, and limits.
- `worklines/wyoh/docs/0306_01_shared-sway-wayvnc-design.md` — ownership, deploy, attachment, VNC, screenshot, and recovery design for Step 3.6.
- `worklines/wyoh/docs/0306_02_minimal-sway-environment-discussion.md` — cleaned source discussion on WayVNC, Sway, and headless output.
- `worklines/wyoh/docs/0306_03_shared-sway-wayvnc-result.md` — Step 3.6 deployment and same-session MCP evidence; its VNC rendering claim is withdrawn.
- `worklines/wyoh/docs/0307_01_minimal-environment-result.md` — Step 3.7 usable session, MCP + VNC scenario, inspected evidence, and findings.

Luna evidence (Step 4):

- `worklines/wyoh/docs/0400_01_takeover-review-and-luna-pi-revalidation.md` — 2026-10-04 review, uv environment, `luna-pi` re-run, and proposed Step 4 re-scope.
- `worklines/wyoh/docs/0401_02_luna-storage-and-bluetooth.md` — read-only eMMC-controller and Bluetooth-adapter observation on the stock image.
- `worklines/wyoh/docs/0404_01_luna-production-base-deferred.md` — historical Step 4 defer decision and re-entry conditions.
- `worklines/wyoh/docs/0405_01_luna-stock-image-inventory.md` — physical Luna's EmuELEC baseline and explicit evidence gaps.
- `worklines/wyoh/docs/0506_01_buttons-only-result.md` (with a 2026-10-09 addendum: right stick, wallpaper, four-tile layout, link limits) — Step 5 result: daemon, mapping, button-only scenario (20 inspected steps), boot into the session, cost, findings.
- `worklines/wyoh/docs/0500_01_gamepad-input-intent.md` — Step 5 intent: gamepad mapping, pointer, input zone, recovery, failure modes, budget, tests.
- `worklines/wyoh/docs/0500_02_input-widget-discussion-raw.md` — raw export of the user's ChatGPT discussion on the keyboard and Wi-Fi (2026-10-09); source evidence, not verified documentation.
- `worklines/wyoh/docs/0600_01_slate-and-keyboard-proposal.md` — Step 6 proposal: Slate multi-line input, wvkbd backup keyboard, controls, passwords, open decisions.
- `worklines/wyoh/docs/0605_01_slate-result.md` — Step 6 result: the Slate, wvkbd-luna, evidence, cost, findings, whole-cross calibration still open.
- `worklines/wyoh/docs/0700_01_wifi-settings-proposal.md` — Step 7 proposal: Wi-Fi panel on iwd, ownership boundary with Luna, open decisions.
- `worklines/wyoh/docs/0512_01_luna-controls-reference.md` — current controls reference per mode, checked against the code by `test/wyoh/test_luna_controls_reference.py`.
- `worklines/wyoh/docs/0609_01_luna-cheat-sheet.svg` (+ `.png`) — the user's cheat sheet: front and top of the R36 Ultra, every button on the desktop, in the Slate and with FN; menu, windows, games, recovery.
- `src/wyoh/wyoh_apps.py`, `src/wyoh/apps/` (calculator, dino), `src/wyoh/deploy/luna/menu.toml` — Step 9 app convention, menu set, and app recipes.
- `worklines/wyoh/docs/0900_01_note-from-professor-graphical-apps.md` — Professor's request (apps, menu, assembly) with Wyoh's reply (section 6).
- `worklines/wyoh/docs/1000_01_desktop-icons-proposal.md` — Step 10 proposal: desktop icons, gamepad controls, pinning, open decisions.
- `worklines/wyoh/docs/0408_01_luna-fuzzel-menu.md` — Step 4.8 fuzzel menu, interactions, evidence, GPU-driver correction.
- `worklines/wyoh/docs/0407_01_luna-real-display-session.md` — Step 4.7: the Step 3.7 session on Luna's panel with ArchR's Sway 1.11, MCP scenario, cost, and findings.
- `worklines/wyoh/docs/0405_02_luna-reachability-recheck.md` — failed read-only recheck and the resulting Step 4 boundary.

Code and tests:

- `src/wyoh/wyoh_mcp_server.py` — development-only full-IPC MCP stdio bridge; not a product server.
- `src/wyoh/deploy/luna-pi/` and `Makefile` (`wyoh-*` targets) — shared Sway + WayVNC service and its preview/deploy/activate/rollback path.
- `test/wyoh/` — deterministic capability/bridge tests, live `luna-pi` proofs, and Gherkin contracts. Run with `uv run pytest` (see `docs/02_testing.md`).
