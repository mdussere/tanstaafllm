# Wyoh requirements proposal and solution paths

> **Superseded as the product requirements document:** read `0000_05_controller-first-handheld-model.md` first. This document retains useful transport, revision, capability, error, and wait ideas, but its desktop/window assumptions are not the Wyoh product model.

> The active product shape is a Handheld Interaction Object Model (HIOM): one foreground surface, bounded overlays, explicit directional navigation, and a finite action catalogue.

## Question answered

What must Wyoh do, what must it not do, and how can it be realised without assuming unverified Luna hardware?

## Proposed v0 boundary

Wyoh v0 is a **Playwright-like desktop automation boundary**, not a complete handheld shell. The detailed object, interaction, and synchronisation model is in `0000_04_desktop-automation-model.md`.

```text
Mike / Mycroft / tests ── transport chosen later ──► Wyoh adapter / WM
                         │                                  │
                         │                                  ├─ snapshot and locators
                         │                                  ├─ native/emulated interactors
                         │                                  ├─ events and `wait_for`
                         │                                  └─ consumer-scoped capabilities
                         │
                         └─ no arbitrary shell or code evaluation
```

The local model solves a small symbolic problem: inspect, locate, interact, and wait for observable results. It does not receive arbitrary shell access or claim semantic knowledge of third-party clients. Input emulation is an explicit, target-scoped fallback when native semantics do not exist.

## Functional requirements

| Area | Proposed requirement | v0 acceptance evidence |
|---|---|---|
| State | `snapshot` returns schema version, monotonic Wyoh revision, output/screen, focus, known apps/windows, layout/geometry where applicable, and input mode. | Fixture returns JSON conforming to a checked-in schema. |
| Discovery | Locators resolve apps/windows and optional registered semantic nodes; interactions expose stable IDs, typed arguments, and risk class. | Ambiguous/missing locator yields a typed result. |
| Interaction | Native interaction or target-scoped input emulation validates target, arguments, and consumer capability; it returns an operation ID. | One focus/navigation action and one emulated input action succeed; malformed/unknown interaction changes nothing. |
| Events and waits | Subscribers receive revisioned changes and operation completion/failure; `wait_for` evaluates predicates, not fixed sleeps. | Fixture receives the event and waits for the expected state predicate. |
| Input | Controller-first navigation, keyboard fallback, and pointer/touch only when clients need them. | Mapping documented; target test deferred. |
| Recovery | A session escape/restart path remains independent of Mike. | Manual recovery proof documented; target execution deferred. |
| Privacy | Log protocol errors/state transitions without default application-content capture. | Rejected-action test logs a correlation ID without user data. |

## Security and protocol proposal

Define the desktop automation contract before choosing its IPC. A per-user Unix-domain socket with newline-delimited JSON remains a plausible v0 transport, but it is not the design centre. The initial local client set is limited to processes owned by the session user; consumer capability scopes remain separate from OS identity.

```json
{
  "schema": "wyoh.dwom.v1",
  "wyoh_revision": 417,
  "screen": {"id": "main", "width": 720, "height": 720},
  "focus": "terminal-1",
  "windows": [{"id": "terminal-1", "app_id": "org.wezfurlong.wezterm", "focused": true}],
  "interactions": ["window.focus", "input.key", "input.text"]
}
```

```json
{"id":"7","op":"interact","kind":"window.focus","target":"window[id=win:17]","expected_revision":417}
{"id":"8","op":"wait_for","predicate":"focused(window[id=win:17])","after_operation":"7","timeout_ms":500}
{"id":"9","op":"interact","kind":"shell.run","args":{"text":"rm -rf /"}}
{"id":"9","ok":false,"error":{"code":"unknown_interaction","message":"Interaction is not declared"}}
```

The adapter owns capabilities and interaction policy. v0 includes no `eval`, `spawn`, or shell text. Standard input emulation is allowed only as a target-scoped interaction with explicit focus/seat policy; coordinates are a last resort rather than the principal model.

## Provisional performance/resource envelope

These are planning budgets, not claims about a candidate.

- Tolerate a 1-GB physical-RAM handheld without normal interaction depending on swap.
- Wyoh-owned session (WM/compositor, required shell/adapter, socket service): **target ≤150 MiB resident; investigate/reject above 200 MiB** after session readiness.
- No sustained idle CPU busy loop; record process and total-session CPU separately.
- Local snapshot/interaction target: **p95 under 100 ms**, excluding client launch; record method and machine.
- Invalid requests have zero side effect; a display crash has a documented route to a known-good session.
- X11 is permitted for pre-hardware interface work. A production Wayland choice requires direct KMS/DRM, input, and client tests on Luna.

ASR, Mike, applications, graphics buffers, and OS services are outside Wyoh ownership. Measure the full session before product selection nevertheless.

## Solution paths

### A. Recommended now — Qtile/X11 semantic adapter

Use upstream Qtile on the desktop or `luna-pi` when available. A small adapter/configuration translates Qtile’s inspectable command graph into the DWOM: snapshots, locators, native interactions, events, and waits. Validate the automation model quickly in Python.

- Strength: shortest feedback loop and existing remote-inspection/control concepts.
- Cost: X11 proves only the contract, never Luna compatibility.
- Fork policy: keep upstream as a dependency/configuration until a demonstrated limitation requires a fork.

### B. Future minimal owned product — dwl plus sidecar

After Luna proves wlroots/KMS, fork/pin dwl only if a tiny C core outweighs its lack of runtime control. Add a narrow versioned desktop-automation bridge rather than overloading its status stream.

- Strength: end-to-end ownership and controller-first policy.
- Cost: Wyoh must build runtime controls, gamepad policy, events, and recovery discipline.

### C. Future agent-native fork — Cagebreak extension

After target validation, evaluate Cagebreak as the fastest direct fork. Extend its existing runtime control model to implement the DWOM rather than create a competing control plane.

- Strength: runtime control primitive and task/workspace model.
- Cost: C work plus keyboard-to-gamepad and semantic-API design.

### D. Product simplification — native shell inside Cage

If the product becomes one full-screen native TANSTAAFLLM application, use Cage as kiosk/recovery compositor and put navigation inside that app. This is not a normal multi-application WM path.

## Decisions requested for green light

1. Approve the DWOM and its distinction between native interaction and target-scoped input emulation.
2. Approve Solution A, or direct the proof to Cagebreak/dwl.
3. Confirm the 150/200-MiB Wyoh-owned session budget or set another.
4. Confirm that permanent forking waits for Luna characterisation.
