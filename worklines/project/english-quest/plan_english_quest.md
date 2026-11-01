---
**Status**: 📋 Planning — project workline requested by the user, 2026-11-01; implementation not green-lit
**Date**: 2026-11-01
**Priority**: Exploratory
**Maintained**: Yes
---

# English Quest — Luna pronunciation trainer (project workline)

## Mandate and ownership
First cross-agent **project workline**, distinct from agent worklines: `worklines/project/english-quest/`. The project may be developed with **Codex** rather than Claude Code; this choice concerns development tooling, not an additional runtime model. Professor coordinates dependencies; this plan owns the application scope, not other agents' components.

**Product:** a standalone, offline, fullscreen English listening and pronunciation game on Luna. No dependency on Mike or a general-purpose LLM at runtime. Short deterministic lessons, guided repetition, measurable feedback, and progression.

## Visual identity — a firm constraint
The look belongs to **TANSTAAFLLM / Luna**, not to Final Fantasy. Final Fantasy-era RPGs inspire only the **dialogue interaction mechanics** (portraits, text boxes, transitions, turns), not their characters, world, assets, UI art or palette.

The established Luna/Hazel visual language is **retro sci-fi**: Earth and Moon, lunar horizon, stars, orbital communications and terminals; navy/violet, amber, cyan, chrome; pixel sprites, readable bitmap fonts, scanlines, block dissolves and restrained NES-style audio. Use original or suitably licensed assets. Source: `worklines/hazel/docs/0501_01_sequence-library-analysis.md` (23 identified video sequence patterns, library still draft) and `worklines/hazel/docs/0103_01_series-template.md`. Video assets are references, not an automatic permission to copy code or move Hazel's work.

A game screen should feel as if it belongs to the same universe as the videos. Use Luna's **720×720 square display**, large readable text and gamepad-first controls. Proposed internal pixel resolution: 360×360 scaled 2× with nearest-neighbour; test readability on the device.

## Exercise loop (proposed)
1. **Mission select**: choose a short lesson from a lunar mission map / terminal.
2. **Meet / prompt**: a Luna crew portrait speaks a target phrase through offline TTS; the written target is shown.
3. **Your turn**: microphone indication; capture via Mycroft audio interface; replay is available.
4. **Review**: transcription checks word identity and, if an appropriate model is available, separate phoneme-level scoring checks pronunciation. Do not infer 'bad accent' from an ASR spelling error, especially for names.
5. **Reward or retry**: success animation, neutral 'uncertain, try again' state, or specific phoneme exercise. Save only necessary scores; keep raw audio private and opt-in.

## First three levels (proposed)
- **Level 1 — Meet the Crew:** pronunciation and ASR calibration for *Mannie, Mycroft, Wyoh, Mike, Luna, Wolfenstein*. Isolate name-recognition failures from demonstrated pronunciation errors. Several samples per name.
- **Level 2 — Talk to the Crew:** short utterances such as “Can you open the browser?”; word- and (when validated) phoneme-level feedback, replay and targeted practice. Mix new words with previously practised character names rather than leaving Level 1 behind.
- **Level 3 — Command Center:** spoken Luna commands, e.g. “Mannie, launch Wolfenstein 3D”; simulate the resulting actions in the game (no actual system command execution). Progressive variety and difficulty.

Duolingo inspires short drills, immediate feedback, progress and spaced repetition; these are mechanics, not copied art or curricula.

## Spiral progression — continuous consolidation (user direction, 2026-11-01)

**Clearing a level never retires its material.** Each lesson introduces a small amount of new content while naturally reusing knowledge from earlier lessons; recall is embedded **inside** current exercises, not only in a separate review mode.

- Level 1: practise names individually, e.g. “Mannie”, “Wyoh”, “Wolfenstein”.
- Level 2: reuse those names in new dialogue patterns: “Mannie, can you open the browser?”
- Level 3: reuse both names and dialogue vocabulary in longer commands: “Mannie, launch Wolfenstein 3D.”
- Later lessons deliberately revisit earlier sounds, expressions and names, with varied contexts rather than rote repetition.
- Track mastery **per skill** (phonemes, words/names, constructions), not only per cleared level. Keep a compact local progress record with last attempt, confidence/quality, error type and next due review.
- Proposed deterministic scheduler: choose new content plus a few due older skills, weighted toward recent difficulty and elapsed time; avoid repeatedly punishing uncertain acoustic estimates. Graduation is provisional and reversible.
- Suggested first balancing experiment: roughly 70% current lesson / 30% prior material; **hypothesis to test**, not a fixed rule. The important guarantee is always some earlier material woven into each lesson.
- Show the continuity diegetically: former crew members return, names recur in missions, and the lunar command centre builds on previous radio conversations.

**Acceptance criterion:** clearing Level 1 then playing Levels 2 and 3 demonstrably produces exercises invoking Level 1 names; a failed or uncertain older skill can recur later without resetting progress. Deterministic test fixtures cover selection and review scheduling.

## Technical direction (candidate, not yet selected)
- **Native 2D application**, no browser, HTML or DOM in the Luna runtime. Evaluate C + SDL2/SDL3 against C + raylib, on desk first and then through the agreed Luna operator. Python may help prototype tools but need not be the shipping runtime.
- Fixed-timestep or frame-based game loop, scene/state machine, sprite atlas, bitmap text, simple particle and palette effects; avoid unnecessary 3D / Wolfenstein raycasting.
- Mycroft owns speech capture/transcription and investigates TTS; project consumes agreed APIs. Offline acoustic/phoneme scoring is its own experiment, measured for quality, latency, memory and CPU on Cortex-A35 before selection.
- Wyoh launches and manages the fullscreen window and gamepad integration; it does not own pedagogy.
- Hazel advises on the graphic style and reuse of **original shared assets**; no silent changes to Hazel sources.
- Mannie/Codex implements the project under user authorisation, while Mannie remains the sole Luna operator. No device SSH without its agreement.

## Green-light steps (planning is allowed; implementation requires explicit go)
### Step 1 — Game design and visual storyboard
**Status:** 📝 proposed
- [ ] 1.1 Detail screen-by-screen sequence, timings, buttons, accessibility and error/uncertainty states.
- [ ] 1.2 Create 3–5 original stills/mockups in Luna's retro-sci-fi style, with asset licences/provenance.
- [ ] 1.3 Agree on an interface/animation vocabulary with Hazel without changing her workline.
**Exit:** reviewed storyboard and visual acceptance criteria.

### Step 2 — Native rendering spike
**Status:** ⏳ pending
- [ ] 2.1 Compare SDL and raylib by implementation size, packaging, measured FPS, memory and gamepad control.
- [ ] 2.2 Render one interactive dialogue scene at 720×720, test on host, then Luna with Mannie's permission.
**Exit:** evidence-backed choice of native stack and screenshot proof.

### Step 3 — Speech and pronunciation experiment
**Status:** ⏳ pending
- [ ] 3.1 Define Mycroft capture/STT/TTS API contracts and an opt-in sample corpus.
- [ ] 3.2 Compare lexical baseline, known-word handling, phoneme alignment / GOP options, and abstention/uncertainty.
- [ ] 3.3 Measure latency and peak RSS; distinguish transcription errors from actual phonetic errors.
**Exit:** tested scoring contract and fallback for no phonetic model.

### Step 4 — Three playable levels
**Status:** ⏳ pending
- [ ] 4.1 Implement the deterministic level data and retry/spaced-practice rules.
- [ ] 4.2 Integrate audio, results and original character sprites.
- [ ] 4.3 Validate user experience, accessibility, offline operation, memory and cold start on Luna.
**Exit:** three fully playable short levels, documented reproducible tests.

## Explicit non-goals
- No Mike dependence, mandatory cloud service, or LLM in the game loop.
- No claims of pronunciation proficiency based solely on Kroko recognition.
- No imported Final Fantasy assets, characters or graphical identity.
- No automatic publication of user voice recordings in the public Git repository.
- No premature commitment to a particular phonetic model or graphics library.

## Open design questions
- Does the optional teacher character reuse Luna's existing cast or become an original sprite?
- How much explicit pronunciation feedback can be trusted with French-accented English?
- Can one shared, versioned asset format serve both Hazel's videos and this native game without coupling implementations?

## Sources
- `worklines/hazel/docs/0501_01_sequence-library-analysis.md`
- `worklines/hazel/plan_hazel.md`
- `worklines/mycroft/plan_mycroft.md` Step 11
- `docs/01_principles.md`

**Coordination:** This plan is a cross-agent proposal; no task is assigned to another agent until its own plan and approvals are updated.