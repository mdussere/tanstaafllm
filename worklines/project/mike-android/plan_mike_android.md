---
**Status**: 📋 Planning — separate project workline, user decision 2026-11-01; implementation not green-lit
**Date**: 2026-11-01
**Priority**: Exploratory
**Maintained**: Yes
---

# Mike on Android — voice companion (project workline)

## Mandate
Create a **separate cross-component project workline**, not a new step in Mike's agent workline. User explicitly requested that no Android-specific scope be added to `worklines/mike/` yet.

**Product concept:** a small Android app that the user opens and talks to: Mycroft handles speech input, Mike provides local intelligence and routing, and a compact Android-native interface makes the conversation visible. This is the *complete voice interaction experience*, not merely running Mike's model on Android.

## Boundaries
- **Do not modify the Mike or Mycroft workline plans** until a later explicit coordination decision.
- Keep this project independent of **Camp Currie L-CAT**, the offline language training game. They may eventually share portable speech components and assets.
- Same Mike and Mycroft **model identities, weights, versions, and behaviour** as Luna, not larger Android-specific substitutes (portability target). Platform bindings may differ; verify equivalence.
- Offline-first, user-initiated, permission-respecting interactions. No assumption of system-wide Android control or background always-listening service.
- Android is not Wyoh: a platform adapter must expose only supported and authorised actions, with an appropriate UI and clear confirmation.
- No implementation, downloads or deployment without an explicit project-step green light.

## Proposed steps
### Step 1 — Experience and boundaries
**Status:** 📋 Proposed
- [ ] Draw the open-app → speak → transcript → Mike response loop, including editing and confirming actions.
- [ ] Decide which features are common with Luna and which are Android-specific.
- [ ] Define resource, privacy and permission budgets and offline failure modes.
**Exit:** reviewed UX and component contract.

### Step 2 — Portable runtime research
**Status:** ⏳ Pending
- [ ] Inventory the pinned Luna Mike and Mycroft models and runtime dependencies.
- [ ] Check Android feasibility without changing the model assets, using identical test fixtures.
- [ ] Compare Android audio integrations and Android UI packaging approaches.
**Exit:** evidence-backed architecture and compatibility table, no implementation.

### Step 3 — Android prototype
**Status:** ⏳ Pending
- [ ] Build a minimal native interface with tap-to-talk and visible transcript.
- [ ] Integrate shared offline model runtimes and a narrow, permitted action adapter.
- [ ] Validate model asset parity, latency, memory and user-controlled permissions.
**Exit:** opt-in local prototype, reproducible tests and measured constraints.

## Notes
The application name **Mike on Android** is a working descriptor, not a final product name. This is a project workline because it involves Mike, Mycroft and interface integration; ownership of their existing components remains unchanged.
