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

Intent (behaviour, states, failure modes, budget, tests): [`docs/0500_01_gamepad-input-intent.md`](docs/0500_01_gamepad-input-intent.md). Sub-steps run in this order; each ends with its tests passing and, where it has a visible effect, inspected screenshots.

- [x] 5.0 Intent written before any code (2026-10-07); four open points listed in it for the user.
- [x] 5.1 **Calibration from the device tree (read-only, 2026-10-07).** `/proc/device-tree/joypad/sw*` labels every button: A = `BTN_EAST`, B = `BTN_SOUTH`, X = `BTN_NORTH`, Y = `BTN_WEST`, FN = `BTN_MODE`, L1/L2/R1/R2 = `BTN_TL/TL2/TR/TR2`. The intent was corrected (it had assumed A = `BTN_SOUTH`). Stick polarity and the physical labels are confirmed in 5.7.
- [x] 5.2 **Core state machine, offline.** Mapping, zone states, recovery timer and pointer curve as pure code with deterministic tests (every mapping row in both modes, zone validate/discard/empty/target-gone/re-entrance, recovery timing, invalid config). No device access.
- [x] 5.3 **Device adapters.** Gamepad discovery, read and grab; persistent uinput keyboard and mouse; select() loop with zero CPU at rest. Live check against a virtual gamepad on Luna: keys and pointer reach Sway; stopping the daemon releases the grab.
- [x] 5.4 **Input zone.** fuzzel one-line zone, Sway target capture and refocus, paced `wtype` delivery; status file. Live check with marker-file side effects for deliver-once and discard.
- [x] 5.5 **Service and deployment.** `wyoh-gamepad.service` (PartOf the Sway unit), `gamepad.toml`, Make targets; measure RSS and CPU at rest and with the stick deflected.
- [x] 5.6 **Button-only scenario through MCP.** Development MCP tools create a virtual gamepad and keyboard (the person); the daemon serves it alongside the real gamepad. Gherkin + pytest end to end on Luna's panel with inspected MCP screenshots, as in the intent's testing policy.
- [ ] 5.7 **User check** on the physical controls, panel in view; record the result in `docs/0507_01_gamepad-input-result.md`. *Pending: the only open item.*
- [x] 5.8 **Boot into the session (user requirement, 2026-10-07: "we must stop landing on terminal on boot").** Enable `wyoh-sway.service` and `wyoh-gamepad.service` in the boot target the card uses today (`textmode.target`, set by the Luna workline in `extlinux.conf`), through `[Install]` sections and links under `/storage/.config/system.d`, without touching the boot partition. The Mali driver step runs before Sway; the tty1 shell stays underneath as a fallback. Verified by a real reboot: the panel shows the session with no SSH action. Removing the links restores the text-console boot.
- [ ] 5.9 Acceptance as in the intent, plus booting straight into the session: every control works through the real gamepad; the zone delivers once and discards cleanly; recovery works; stopping the daemon returns the gamepad to ArchR; tests pass; budget holds.

### Step 6 — Productise only the selected agent-native workspace path
**Status**: ⏳ Pending

- [ ] 6.1 Fork/pin only the selected upstream; retain licence, provenance, and upgrade strategy.
- [ ] 6.2 Implement only the approved Sway configuration, capability mediator, and/or Wyoh adapter; retain the Step 5 controller mapping and recovery and deterministic startup.
- [ ] 6.3 Add contract tests and target smoke tests for state, events, focus/layout operation, capability rejection, focused input fallback, wait, process exit, malformed/stale request, and restart.
- [ ] 6.4 Acceptance: Luna boots a recoverable agent-native Wyoh workspace and passes its selected Sway/adapter contract suite inside its measured budget.

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
- ⏳ Step 6 — Productise the selected agent-native workspace path.

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
- `worklines/wyoh/docs/0506_01_buttons-only-result.md` — Step 5 result: daemon, mapping, button-only scenario (20 inspected steps), boot into the session, cost, findings.
- `worklines/wyoh/docs/0500_01_gamepad-input-intent.md` — Step 5 intent: gamepad mapping, pointer, input zone, recovery, failure modes, budget, tests.
- `worklines/wyoh/docs/0408_01_luna-fuzzel-menu.md` — Step 4.8 fuzzel menu, interactions, evidence, GPU-driver correction.
- `worklines/wyoh/docs/0407_01_luna-real-display-session.md` — Step 4.7: the Step 3.7 session on Luna's panel with ArchR's Sway 1.11, MCP scenario, cost, and findings.
- `worklines/wyoh/docs/0405_02_luna-reachability-recheck.md` — failed read-only recheck and the resulting Step 4 boundary.

Code and tests:

- `src/wyoh/wyoh_mcp_server.py` — development-only full-IPC MCP stdio bridge; not a product server.
- `src/wyoh/deploy/luna-pi/` and `Makefile` (`wyoh-*` targets) — shared Sway + WayVNC service and its preview/deploy/activate/rollback path.
- `test/wyoh/` — deterministic capability/bridge tests, live `luna-pi` proofs, and Gherkin contracts. Run with `uv run pytest` (see `docs/02_testing.md`).
