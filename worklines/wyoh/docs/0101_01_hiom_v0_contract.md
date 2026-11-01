> **Status changed (2026-09-25):** This is the historical outcome of the original Step 1 green light, not the active Wyoh v0 contract. Step 1 is reopened because the subsequent discussion changes the v0 engine, product path, and interaction boundary.
>
> Retained principles: revisions, typed rejection, events, waits, confirmation, consumer scopes, and the distinction between Wyoh-owned state and separately fresh application state. Superseded v0 assumptions: one foreground scene only, finite controller actions only, no focused text/pointer fallback, and stock-front-end-first product selection. The proposed replacement is Sway IPC v0 with a mediated capability boundary; see [0101_03](0101_03_followup_discussion.md).

# HIOM v0 contract — approved controller-first boundary

> **Freshness:** 🟡 historical · **Written:** 2026-09-26 · **Checked:** 2026-10-31 · **Step:** wyoh 1.1 ✅

## Question answered

What exact state and interaction contract does Wyoh expose to a constrained consumer without assuming a conventional desktop, pointer, keyboard, or free-floating windows?

## Decision record

**Status:** Approved for Wyoh Step 1 on 2026-09-25 by the user’s `go §1` green light.

Wyoh v0 is a controller-first **Handheld Interaction Object Model (HIOM)**. It represents a single active handheld scene and allows only finite interactions that are advertised for that scene. The default product order is:

```text
stock EmuELEC / EmulationStation bridge
          ↓ if insufficient state or controllability
native full-screen HIOM shell
          ↓ only if both paths fail
custom compositor
```

`0000_04_desktop-automation-model.md` remains applicable only for transport independence, revisioning, typed errors, capability scopes, events, and predicate-based waiting. It is not a desktop/window API for Luna.

## Scene ownership

Wyoh owns a session scene rather than a set of windows:

```text
scene
├── mode: launcher | app | system-overlay | suspended | recovery
├── foreground: exactly one foreground surface/application
├── overlays: bounded ordered stack
├── focus: exactly one selectable node, or null when no selection exists
├── nodes: currently exposed selectable nodes
├── navigation: directional edges between nodes
└── actions: finite actions currently valid for this scene
```

An emulator, port, or other foreground application is opaque unless it deliberately publishes a separate HIOM-compatible tree. Wyoh must label such application-published state with its own revision and freshness; it must not present it as compositor/session-authoritative state.

## Snapshot contract

Every snapshot is a self-contained view of Wyoh-owned state:

```json
{
  "schema": "wyoh.hiom.v1",
  "wyoh_revision": 1,
  "captured_at": "monotonic timestamp",
  "mode": "launcher",
  "foreground": {"id": "frontend", "kind": "stock-frontend"},
  "overlays": [],
  "focus": "entry:ports",
  "nodes": [{
    "id": "entry:ports",
    "role": "entry",
    "label": "Ports",
    "enabled": true,
    "visible": true,
    "nav": {"left": "entry:arcade", "right": "entry:settings"}
  }],
  "actions": [
    {"id": "navigate.right", "risk": "none"},
    {"id": "activate", "target": "entry:ports", "risk": "none"},
    {"id": "open.system-menu", "risk": "none"}
  ]
}
```

Required fields are `schema`, `wyoh_revision`, `mode`, `foreground`, `overlays`, `focus`, `nodes`, and `actions`. IDs are stable only for an object’s current lifetime. A consumer must re-resolve state after a scene revision instead of caching a node as permanently valid.

## Finite action vocabulary

The only default v0 action families are:

| Family | Meaning |
|---|---|
| `navigate.up`, `navigate.down`, `navigate.left`, `navigate.right` | Follow an advertised directional edge from the current focus. |
| `activate` | Activate the focused node or an explicitly advertised target. |
| `back` | Return from the current level or close the top eligible overlay. |
| `open.system-menu` | Open the system overlay only when advertised. |
| `page.previous`, `page.next` | Change list/page only when advertised. |
| named shoulder/trigger action | Execute only when advertised with its hold/repeat semantics. |
| `confirm`, `cancel` | Resolve an already-present confirmation overlay. |

No v0 action creates a pointer, submits arbitrary text, moves/resizes/raises a window, injects raw keys, runs a command, or evaluates code. Text entry is a future dedicated semantic surface—such as a visible on-screen keyboard or a validated Mycroft handoff—not an emulated typing escape hatch.

## Interact, events, and waits

The transport is deliberately unspecified. Whatever local transport is later selected exposes these semantics:

1. A consumer reads a snapshot at revision `r`.
2. It requests one advertised action, optionally declaring `expected_revision: r`.
3. Wyoh returns a typed rejection (`stale_revision`, `unknown_action`, `unavailable_action`, `ambiguous_target`, `unauthorised`) or accepts it with an `operation_id` and `accepted_revision`.
4. Wyoh emits revisioned events for state transitions and operation completion/failure.
5. The consumer waits for a named predicate or its operation result; it never treats a fixed delay as completion.

Useful predicates include `focused(node)`, `mode_is(value)`, `overlay_present(kind)`, `overlay_absent(kind)`, `node_exists(id)`, `node_selected(id)`, and `operation.completed(id)`.

An action with a risk requiring confirmation creates or selects a confirmation overlay; it does not perform the risky effect until a later `confirm` action resolves that visible overlay. A stale, unavailable, ambiguous, or unauthorised action has no state-side effect.

## Consumer scopes

| Consumer | HIOM scope in this phase |
|---|---|
| Mike | Read snapshots/events and request only policy-allowed advertised actions. |
| Mycroft | No live integration in Mycroft v0. A later context feature is read-only and privacy-minimised. |
| Developer fixture | Explicit test-only read/interaction scope; no inherited end-user authority. |
| Adam | Presentation of state, outcomes, confirmations, failures, and degraded conditions; not a separate authority. |

## Deferred questions

- Exact stock EmuELEC/EmulationStation observability and controllability on the delivered device.
- Exact mapping from physical D-pad, face, shoulder, and trigger controls to HIOM action families.
- Which actions require confirmation and whether a voice confirmation can share the same overlay contract.
- Wire encoding and local transport choice.
- Any application-specific semantic tree or text-entry surface.

## Step 1 acceptance result

- HIOM is the approved v0 product boundary.
- The stock-front-end bridge → native full-screen shell → custom compositor order is approved as the draft product path.
- The finite controller action catalogue, revisioned state, overlay confirmations, consumer scopes, and transport-independent synchronisation contract are defined.
- Step 2 remains pending. No hardware, runtime, firmware, compositor, or UI implementation is authorised by this record.
