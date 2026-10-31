# Wyoh v0 contract — unmodified Sway with scoped IPC authority

> **Freshness:** 🟢 current · **Written:** 2026-09-26 · **Checked:** 2026-10-31 · **Step:** wyoh 1.1 ✅

**Status:** ratified for the green-lit pre-hardware proof, 2026-09-26  
**Question answered:** What is Wyoh v0, and which authority does it expose before Luna hardware evidence exists?

## Decision

Wyoh v0 uses an **unmodified, version-pinned Sway session and its existing IPC** as the session substrate. It does not fork Sway, add an IPC extension, or introduce a resident Wyoh adapter by default. The proof may use a local test fixture that speaks the documented Sway IPC protocol.

## Contract boundary

`consumer request -> capability policy -> Sway IPC -> observed Sway event/state`

- The fixture records Sway version, IPC socket identity, query replies, command result, and relevant events.
- Its observation contains source (`sway`), capture time, an implementation-local monotonic revision, focused container/workspace/output identifiers, and freshness. It does not claim that asynchronous client metadata is globally atomic.
- The first proof reads outputs, tree, workspaces, focus, layout, and lifecycle information through Sway IPC; it performs one explicitly allowlisted focus or layout operation and waits for an observed event or matching state predicate. Fixed delays are not correctness evidence.
- The test fixture may use direct IPC because it is trusted development tooling. A Mike-facing consumer must be constrained to a named allowlist and target selector. It has no arbitrary Sway command, shell, process, filesystem, or input-injection authority.
- A consumer request is rejected without an IPC mutation when its capability is absent, the target is stale, unavailable, ambiguous, malformed, or outside its scope. The rejection is observable and carries no side effect.

## Interaction and component boundaries

- Semantic Sway state and operations are preferred. Focused keyboard or pointer fallback is exceptional, explicitly scoped, and never a substitute for arbitrary pixel guessing.
- Buttons remain attention, confirmation, interruption, and recovery affordances. A Bluetooth keyboard/touchpad is for development and recovery, not the default product grammar.
- Mycroft produces reviewable input composition and remains context-free in its current v0. Any later Wyoh snapshot for Mycroft is bounded, freshness-labelled, non-authoritative, and separately authorised.
- Mike may perform simple offline system actions only through policy-scoped capabilities. Mannie owns code, build, test, diagnosis, and development authority.

## Deferred evidence

This contract does not establish the fit of Sway, wlroots, DRM/KMS, Panfrost, display rotation, controller mapping, or the resource budget on Luna. `luna-pi` can establish only Pi-specific operational evidence. Step 4 decides the delivered Luna stack and whether the final base remains unmodified Sway, requires a thin mediator/adapter, requires another base, or must defer.

The earlier HIOM/controller-first records remain reference material for stock-console and recovery surfaces. They are not the active definition of the agent-native Sway v0 path.

## Acceptance mapping

- Sway v0 substrate, no default fork or adapter: decided above.
- Policy-scoped semantic action boundary and focused fallback: decided above.
