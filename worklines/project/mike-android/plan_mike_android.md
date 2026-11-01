---
**Status**: 📋 Planning — separate project workline, user decision 2026-11-01; implementation not green-lit
**Date**: 2026-11-01
**Priority**: Exploratory
**Maintained**: Yes
---

# Mike companion — retro conversational shell (project workline)

## Mandate
Create a **separate cross-component project workline**, not a new step in Mike's agent workline. User explicitly requested that no Android-specific scope be added to `worklines/mike/` yet.

**Product concept (refined by user 2026-11-01):** a portable, minimal retro-RPG-like **conversational skin around Mike**, first relevant to Luna and later Android. Mike remains the existing intelligence; Mycroft supplies STT and TTS; the game-like shell gives Mike a more embodied, enjoyable presence through a character, animated portrait, dialogue windows, spoken responses and clear interaction states. This is not a request to replace Mike's current text UI or change Mike's implementation.

## Proposed experience — character, not another brain
- A distinctive original Mike portrait/avatar with restrained pixel animations: idle, listening, thinking, speaking, uncertain.
- Dialogue panel inspired by classic RPG presentation, but using the project's **Luna / Hazel retro sci-fi** visual system; do not copy existing RPG intellectual property.
- Push-to-talk or tap-to-talk → Mycroft STT → editable transcript → Mike → text display and optional Mycroft TTS. Distinguish spoken text, proposed action, and verified outcome.
- No forced gamification for everyday help: no experience points or artificial quests in the assistant; the RPG influence is the **presentation language**.
- Native, low-memory scene rendering, gamepad friendly on Luna and touch friendly on Android. Reuse graphic assets/conventions with Camp Currie when useful, not the language-learning rules.
- Preserve the text-only Mike application as a fallback and benchmarking reference; this project is an optional alternative UI.
- Separate **visual persona** from intelligence: the avatar expresses Mike's real state, never pretends to feel or know what cannot be observed.

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
- [ ] Storyboard Luna and Android screens: avatar, listen, transcribe/edit, reason, speak, action confirmation and failure states.
- [ ] Specify a portable presentation/voice contract and reusable retro sci-fi assets, preserving the existing text Mike as fallback.
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
- [ ] Build a minimal native retro-RPG dialogue interface with an original Mike avatar, tap/push-to-talk, visible transcript and spoken reply.
- [ ] Integrate shared offline model runtimes and a narrow, permitted action adapter.
- [ ] Validate model asset parity, latency, memory and user-controlled permissions.
**Exit:** opt-in local prototype, reproducible tests and measured constraints.

## Notes
The application name **Mike on Android** is a working descriptor, not a final product name. This is a project workline because it involves Mike, Mycroft and interface integration; ownership of their existing components remains unchanged.
