> **Current status (2026-09-25):** This DWOM model is again the active conceptual basis for the agent-native workspace. Sway IPC supplies its initial observable desktop tree, events, and window-management operations; a Wyoh adapter is deferred until it earns its existence.
>
> Controller input is no longer the exclusive v0 vocabulary. The human normally instructs Mike through Mycroft; buttons are attention/recovery controls, while target-scoped keyboard or pointer injection remains a permitted fallback for Mike.

# Wyoh as Playwright for the desktop

## Question answered

What is Wyoh’s actual abstraction if it should let agents interact with a desktop as Playwright lets them interact with a browser, without relying on rendering?

## Core decision

Wyoh is a **desktop automation service**. A Unix socket, D-Bus service, in-process bridge, or another local IPC mechanism can carry its messages, but none is the product concept.

| Playwright | Wyoh |
|---|---|
| DOM | Desktop/Window Object Model (**DWOM**) |
| page locator | output, application, window, and optional semantic-node locator |
| click/type/keyboard | native compositor interaction or target-scoped standard-input emulation |
| page snapshot | revisioned desktop snapshot |
| browser events / `waitFor…` | Wyoh event stream / `wait_for` predicate |
| browser protocol transport | local IPC transport, selected separately |

The objective is not “send a command over a socket.” It is to give consumers a structured, inspectable, synchronisable desktop they can observe and operate without pixels.

## Two kinds of interaction

1. **Native interactions** act on state Wyoh owns: focus a known window, activate an app, switch task/screen, close a Wyoh-owned surface, select a launcher entry, or change an output/input mode. They are semantic and resilient to layout changes.
2. **Standard-interactor emulation** supplies a virtual keyboard, pointer, touch, or controller seat for an explicitly selected target. This is the fallback for an ordinary client whose internals Wyoh cannot see. It is never presented as semantic understanding of that client.

Coordinates are last-resort arguments to the standard interactor, not the principal API. A request must name its target and be authorised by the consumer’s capability scope. There is no arbitrary shell or code-evaluation primitive.

## DWOM state model

Wyoh is authoritative for compositor/session facts and assigns every state transition a strictly increasing `wyoh_revision`:

```json
{
  "schema": "wyoh.dwom.v1",
  "wyoh_revision": 417,
  "captured_at": "monotonic-time",
  "outputs": [{"id": "main", "width": 720, "height": 720}],
  "focus": {"window": "win:17"},
  "windows": [{"id": "win:17", "app_id": "terminal", "title": "TANSTAAFLLM", "state": "focused"}],
  "interactions": ["window.focus", "input.key", "input.text"],
  "semantic_trees": [{"window": "win:17", "source_revision": 51, "freshness": "reported"}]
}
```

An optional semantic tree comes from an application and has its **own** revision, timestamp, and freshness. It is a last known report, not globally atomic truth. The compositor can atomically order its own state; it cannot stop arbitrary clients changing between their report and the next frame.

## Locator model

Locators choose a target from a snapshot, rather than guessing a pixel.

```text
window[id="win:17"]
app[id="terminal"]
window[focused]
semantic[role="button", name="Save"]   # only within an app-provided tree
```

- Every resolved object has a stable Wyoh ID for its lifetime.
- A locator can resolve to zero, one, or many objects; an interaction requiring one fails explicitly if ambiguous.
- Semantic-node locators are allowed only when an application registered that tree and reports its revision/freshness.
- The client supplies an expected Wyoh revision or freshness tolerance when correctness depends on its observation.

## Synchronisation model

There is no permanently stable desktop snapshot. The answer is not to promise one; it is to make races observable and waitable.

1. `snapshot()` returns coherent **Wyoh-owned** state with revision `r`.
2. The consumer resolves a locator against `r` and requests an interaction, optionally declaring `expected_revision: r`.
3. Wyoh rejects it as stale/ambiguous/unauthorised, or accepts it with `operation_id` and `accepted_revision`.
4. The consumer calls `wait_for(predicate, after_revision | operation_id, timeout)` or subscribes to events.
5. Completion means an observed state predicate is true, the operation fails, the target disappears, or timeout expires—not that an arbitrary delay elapsed.

Useful predicates: `focused(window)`, `exists(locator)`, `gone(locator)`, `window.title_matches`, `semantic.revision_at_least`, and `operation.completed`.

## Consumer model

- **Mike:** eventually receives a policy-scoped read view plus allowed interactions, grounded in DWOM rather than pixels.
- **Mycroft:** later receives a read-only, privacy-minimised view for contextual ASR biasing. Mycroft v0 does not consume it; its existing plan remains context-free.
- **Developer tooling/tests:** gets explicit test scope and richer diagnostics; it does not silently inherit Mike’s end-user permissions.

## Acceptance criteria for a first proof

- A fixture obtains a revisioned snapshot, locates an application/window, and focuses it using a native interaction.
- The fixture uses `wait_for(focused(locator))` rather than sleeping.
- A target-scoped emulated key/text interaction is delivered only after the target is resolved and focused.
- Stale revision, ambiguous locator, missing target, and unauthorised interaction yield typed errors and leave desktop state unchanged.
- A simulated client semantic tree carries source revision and freshness; Wyoh never merges it into compositor-authoritative state.

## Design consequence

Transport is replaceable. A local Unix socket remains plausible low-overhead plumbing for request/reply and events, but the stable asset is the DWOM contract and synchronisation rules.
