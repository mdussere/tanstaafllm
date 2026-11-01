---
**Status**: 📋 Planning — initial shell requested by the user, 2026-11-01; implementation not green-lit
**Date**: 2026-11-01
**Priority**: Exploratory
**Maintained**: Yes
---

# Camp Currie L-CAT — Lunar Communication Assessment Training (project workline)

**Name (user decision, 2026-11-01):** workline **Camp Currie**; full program name **Camp Currie L-CAT — Lunar Communication Assessment Training**. The historical reference is **Camp Currie** (Arthur Currie, two r's). No longer a provisional English Quest name.

## Mandate and ownership
First cross-agent **project workline**, distinct from agent worklines: `worklines/project/camp-currie/`. The project may be developed with **Codex** rather than Claude Code; this choice concerns development tooling, not an additional runtime model. Professor coordinates dependencies; this plan owns the application scope, not other agents' components.

**Product:** a standalone, offline, fullscreen English listening and pronunciation game on Luna. No dependency on Mike or a general-purpose LLM at runtime. Short deterministic lessons, guided repetition, measurable feedback, and progression.

**First delivery boundary (user direction, 2026-11-01):** begin with the game shell only. It must be a navigable, playable-looking native application with deterministic simulated exercise results, but it must not capture audio, load or invoke STT/TTS/acoustic models, or depend on a Mycroft, Wyoh, Mike, Mannie or Hazel runtime/API. Speech remains a later replaceable boundary; the first two steps establish the screens, state transitions and control feel that speech will eventually occupy.

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

## End-of-level field exam — playable scenario (user direction, 2026-11-01)

**Every level culminates in a short, staged exam**, separate from ordinary drills. The candidate navigates an original Luna-themed space (lunar base corridor, communications hub, airlock, observatory), encounters NPCs and consoles, and clears **five spoken interactions** to complete the mission. Inspiration from early first-person games such as Wolfenstein concerns *moving through a space and encountering checkpoints*, not copying its art, plot or engine.

- Short exploration between five checkpoints; one spoken phrase or dialogue exchange unlocks each next area.
- Checkpoints integrate the level's new language **and earlier lessons' skills**, following the spiral-learning rule.
- A successful utterance triggers a visible world response (door, terminal, character reply). An uncertain result offers replay/retry and a transparent reason, not an unfair failure.
- **Clear condition:** five validated spoken objectives; attempts need not be perfect on the first try. Progress remains visible and the learner can repeat a checkpoint.
- Reward: mission debrief, rank/skill update, and STAGE CLEAR sequence in Luna's own retro-sci-fi language.
- Level 1 candidate scenario: reach the lunar communications room by addressing or identifying crew members across five encounters; later exams build longer dialogue and system commands.
- **Presentation choices left for a prototype:** simple first-person corridor / raycast, or lightweight tile-based traversal. Neither requires a complete 3D engine. Compare legibility and CPU/RAM costs on Luna before committing.
- No real system commands are executed in exam mode.

**Acceptance criteria for prototype:** the learner can traverse an environment with gamepad controls, trigger five distinct verbal exchanges, retry misunderstood utterances, and reach a final results screen only after five validated interactions. Evaluation uses a simulated scorer first; later Mycroft/phonetic scoring is integrated behind the same contract.

## Cross-platform model parity (user decision, 2026-11-01)

**The same model assets must run on Luna and Android.** Android is a portability target, not a reason to substitute larger or platform-specialised models. This applies to speech-to-text, text-to-speech and pronunciation/acoustic assessment, with identical weights, vocabulary, model revisions and scoring rules. Do not silently substitute another model on Android.

Keep the native game and deterministic pedagogy shared; isolate platform audio, display and packaging code. Backends may be rebuilt per platform, but benchmark output equivalence and regression-test small numerical differences; prefer the same CPU runtime where practical. Record model version, hash, feature pre-processing, and thresholds in a shared manifest. Memory, CPU and latency selection gates are set by Luna, the stricter device; Android must pass the same behaviour tests.

**Acceptance:** given the same fixed audio test corpus, both platforms use the same model asset hashes and yield comparable transcripts, phonetic scores, uncertainty decisions and lesson progress. Report all platform-induced differences rather than concealing them.

## Technical direction (candidate, not yet selected)
- **Native 2D application**, no browser, HTML or DOM in the Luna runtime. Evaluate C + SDL2/SDL3 against C + raylib, on desk first and then through the agreed Luna operator. Python may help prototype tools but need not be the shipping runtime.
- Fixed-timestep or frame-based game loop, scene/state machine, sprite atlas, bitmap text, simple particle and palette effects; avoid unnecessary 3D / Wolfenstein raycasting.
- Mycroft owns speech capture/transcription and investigates TTS; project consumes agreed APIs. Offline acoustic/phoneme scoring is its own experiment, measured for quality, latency, memory and CPU on Cortex-A35 before selection.
- Wyoh launches and manages the fullscreen window and gamepad integration; it does not own pedagogy.
- Hazel advises on the graphic style and reuse of **original shared assets**; no silent changes to Hazel sources.
- Mannie/Codex implements the project under user authorisation, while Mannie remains the sole Luna operator. No device SSH without its agreement.

## Initial-shell isolation

- The shell is a self-contained project artifact. It changes no component workline plan, code, service, asset library or device configuration.
- Use only original placeholder art, generated primitives, or assets already explicitly licensed for this project. Do not copy Hazel assets or request changes from Hazel for Steps 1–2.
- Model the future exercise evaluator behind a local deterministic fake (`success`, `retry`, `uncertain`) so its eventual speech implementation can replace it without changing scene flow.
- Host-only work is sufficient for the initial shell. A Luna deployment, Wyoh launch integration, gamepad daemon integration, microphone access and audio playback are all out of scope unless separately planned and green-lit.
- The implementing worker remains unnamed in project-facing artifacts for now. This does not alter repository traceability, review, green-light, or commit requirements.

## 🚦 Green-light protocol

- Planning and documentation only until the user explicitly says **“🟩 go Step N”**.
- Step 1 and Step 2 are independently gated. A green light for Step 1 does not authorise Step 2.
- A request to add audio capture, STT, TTS, acoustic scoring, device deployment, or a cross-workline dependency is a material scope change: update this plan first and obtain the relevant later green light.

## Green-light steps (planning is allowed; implementation requires explicit go)
### Step 1 — Standalone navigable shell (no speech)
**Status:** ⏳ pending
- [ ] 1.1 Select and document the smallest host-native rendering stack after a bounded comparison of SDL and raylib; do not install or change anything on Luna.
- [ ] 1.2 Create a self-contained application skeleton at the intended 360×360 logical resolution, scaled to 720×720 with nearest-neighbour rendering.
- [ ] 1.3 Implement controller/keyboard-navigable Title, Mission Select, Dialogue, “Your turn” placeholder, Result and Debrief scenes; every state and transition is deterministic and inspectable.
- [ ] 1.4 Use original placeholder visual/audio-free assets and show an explicit no-microphone/no-speech affordance rather than imitating a live recording.
- [ ] 1.5 Add reproducible host tests for the scene state machine and navigation, plus inspected screenshots of each screen.
**Exit:** a local, fullscreen shell can be launched and navigated end-to-end with no microphone permission, audio input/output, model asset, network connection, device access or component-workline integration.

### Step 2 — Simulated first-mission vertical slice (no speech)
**Status:** ⏳ pending
- [ ] 2.1 Add one short “Meet the Crew” mission using the Level 1 names and original placeholder crew/terminal presentation.
- [ ] 2.2 Drive the exercise loop with an explicitly labelled deterministic simulated evaluator: success, retry and uncertain; include replay-equivalent text/prompt controls without audio playback.
- [ ] 2.3 Implement progress, retry and final debrief states, including a visible explanation that a result is simulated rather than a pronunciation judgement.
- [ ] 2.4 Run five simulated checkpoints in the shell and make their completion state visible; this proves the future exam flow without exploration, microphone capture or an STT/TTS dependency.
- [ ] 2.5 Add deterministic tests for success/retry/uncertain paths and an inspected screenshot/evidence set for the complete host run.
**Exit:** a person can complete, retry and review a five-checkpoint first mission entirely through the native shell, while the app remains offline and contains no operational speech or model integration.

### Step 3 — Speech and pronunciation experiment (later)
**Status:** ⏳ pending
- [ ] 3.1 Define Mycroft capture/STT/TTS API contracts and an opt-in sample corpus.
- [ ] 3.2 Compare lexical baseline, known-word handling, phoneme alignment / GOP options, and abstention/uncertainty.
- [ ] 3.3 Measure latency and peak RSS; distinguish transcription errors from actual phonetic errors.
**Exit:** tested scoring contract and fallback for no phonetic model. This step may replace the Step 2 simulated evaluator only after its own green light and contract review.

### Step 4 — Three playable speech-enabled levels (later)
**Status:** ⏳ pending
- [ ] 4.1 Implement the deterministic level data and retry/spaced-practice rules.
- [ ] 4.2 Integrate audio, results and original character sprites.
- [ ] 4.3 Validate user experience, accessibility, offline operation, memory and cold start on Luna.
**Exit:** three fully playable short levels, documented reproducible tests.

## Explicit non-goals
- No speech capture, STT, TTS, acoustic/phonetic scoring, model download, microphone permission or audio playback in Steps 1–2.
- No Luna deployment, Wyoh integration, gamepad-daemon change, or cross-workline implementation in Steps 1–2.
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

## Plan change log

| Date | Change |
| --- | --- |
| 2026-11-01 | Reordered the initial delivery into an isolated native shell (Step 1) and a simulated five-checkpoint vertical slice (Step 2), both deliberately without speech services or other-workline integration. |
