---
**Status**: 🧪 Rewritten 2026-11-02 by Wyoh's session at Adam's request ("Codex did it really badly; start again from the beginning, redo the workplan too"); Steps 1–3 green-lit by Adam the same day
**Date**: 2026-11-02
**Priority**: Exploratory
**Maintained**: Yes
---

# Camp Currie L-CAT — Lunar Communication Assessment Training (project workline)

**Name (Adam, 2026-11-01):** workline **Camp Currie**; full program name **Camp Currie L-CAT — Lunar Communication Assessment Training** (Arthur Currie, two r's).

## Objective

A standalone, offline, fullscreen **English listening and pronunciation game on Luna**. It has short deterministic lessons, guided repetition, clear feedback and visible progress. It needs no Mike, Mannie or any LLM at runtime. It is designed for Luna's 720×720 screen and its buttons from the start.

Steps 1–3 build the **game without speech**: a playable shell and a first mission whose results come from a labelled, deterministic simulated evaluator. Speech (Mycroft capture, STT, TTS, pronunciation scoring) arrives later, behind the same evaluator contract, each part with its own green light.

## Ownership and history

- First **project workline**, distinct from the agent worklines: `worklines/project/camp-currie/`. Professor coordinates the dependencies. This plan owns the game, not other worklines' components.
- **2026-11-01:** Codex worked on Steps 1–3. Adam judged the result unusable. Its uncommitted files are kept, out of Git, in `tmp/camp-currie-codex-20261101/`, for reference only. The main problem was a "≤ 6 MiB whole-process RSS" ceiling, logged as Adam's direction. Adam, 2026-11-02: "no, it's an exaggeration". It made Codex reject SDL2 and write a hand-made SDL header, and it ended with no visible, playable program.
- **2026-11-02:** Adam handed the workline to Wyoh's session (tanstfaafllm-37, formerly -8e): "start again from the beginning, redo the workplan, ask Professor to review it, and do Steps 1, 2, 3". Professor reviews this plan.

## Layout

| What | Where |
|---|---|
| Plan and design records | `worklines/project/camp-currie/`, `…/docs/` |
| Game source, fonts, original assets | `src/camp-currie/` |
| Tests (pytest via uv) and `.feature` contracts | `test/camp-currie/` |
| Logs and screenshots (not in Git) | `results/camp-currie/<topic>/<timestamp>/` |

## Adam's decisions this plan keeps (2026-11-01)

- **Look:** TANSTAAFLLM / Luna retro sci-fi, the same universe as Hazel's videos. That means Earth and Moon, the lunar horizon, stars, orbital communications and terminals; navy and violet, with amber, cyan and chrome. Final Fantasy-era RPGs inspire only the dialogue mechanics (portraits, text boxes, turns), never their art, characters or palette. Duolingo inspires short drills, immediate feedback, progress and spaced repetition, not its art or curriculum.
- **Exercise loop:** mission select → a crew member gives the target phrase → your turn → review → reward or retry. Never infer a "bad accent" from an ASR spelling error, especially on names.
- **Levels:**
  - Level 1, **Meet the Crew**: the names Mannie, Mycroft, Wyoh, Mike, Luna, Wolfenstein;
  - Level 2, **Talk to the Crew**: short requests such as "Can you open the browser?";
  - Level 3, **Command Center**: commands such as "Mannie, launch Wolfenstein 3D", simulated in the game and never executed.
- **Spiral progression:** clearing a level never retires its material. Each lesson reuses earlier names, words and constructions inside its own exercises. Mastery is tracked per skill, and a failed or uncertain skill comes back without resetting progress. A first balance of about 70 % new / 30 % earlier is a hypothesis to test.
- **End-of-level field exam:** five spoken checkpoints in an original lunar-base space. Each one is cleared by a validated utterance, and retrying is always allowed. The exam ends on a debrief and a STAGE CLEAR in Luna's look. No real command runs.
- **Same models on Luna and Android:** STT, TTS and pronunciation scoring use the same assets and versions on both, and Luna's limits set the gates.

## Technical direction (Step 1, 2026-11-02)

- **Python 3 + pygame-ce (SDL2), software rendering at 720×720.** This is Wyoh's own language, and SDL2 is what Luna's games already use. A pure core is testable under pytest without a display, and a screenshot is one call.
  - Measured with a 720×720 window and text: peak RSS 28.3 MiB on `luna-pi` (aarch64, Python 3.13, wheel installed by pip), 30.4 MiB on Termidor (x86_64).
  - Luna itself is not measured yet.
- **Memory (Adam, 2026-11-02):** "it must stay small, but if we go up to 50 MiB, we go up to 50 MiB; it's not a problem". There is no fixed limit: smaller is better, and optimisation comes once the look is right.
  - Context: Mike and Mannie are not meant to run beside the game, only small language models.
  - The game reports its peak RSS on every run.
- **An ordinary Wayland client** in Wyoh's Sway: no framebuffer, DRM or evdev access.
  - Input is the **keyboard**: arrows, Return, Escape. On Luna, Wyoh's gamepad daemon turns the buttons into keys through the app's `keys` profile, so the game owns no input device.
  - Fullscreen and launch belong to Wyoh, later.
- **Look (Adam, 2026-11-02):** "look at the videos' rendering: that is the kind of rendering we want; how you get it is not my concern". This means:
  - a navy-to-violet starfield;
  - Press Start 2P titles, amber "STAGE" labels and VT323 body text (SIL OFL fonts, licences shipped next to them);
  - thin violet or amber panel borders;
  - the crew portraits from the series' key art (`worklines/hazel/.../art/wallpaper.png`, cropped once into the game's assets);
  - a green, tilted "CLEAR!".
  - Reference stills: `worklines/hazel/video/library/T06-two-boxes`, `T11-boss-fight`, `T15-roster`.
- **Agent and accessibility protocol (development only):** `--agent` reads named actions on stdin and writes the semantic state as JSON lines on stdout, so a test or an agent never reads pixels. `--shot` saves the frame.

## 🚦 Green-light protocol

Planning and documentation are always allowed. Implementation needs Adam's **"🟩 go Step N"**, given directly or by Professor on his mandate. Steps 1, 2 and 3 have it (2026-11-02). Adding audio capture, STT, TTS, scoring, Luna deployment or a dependency on another workline changes the scope: update this plan first.

## Steps

### Step 1 — Study and design (no game code)
**Status:** 🧪 in progress
- [ ] 1.1 Learner journey and screens: Title → Mission select → Briefing → five checkpoints (prompt → your turn → result) → Debrief, with controls, timing and the error and uncertainty states.
- [ ] 1.2 The simulated evaluator contract (`success`, `retry`, `uncertain`), what each shows the learner, and the boundary a speech evaluator will replace.
- [ ] 1.3 Visual direction: palette, fonts and sizes readable at arm's length on 720×720, and asset provenance.
- [x] 1.4 Stack choice, measured on Termidor and `luna-pi`, with the proposed Luna budget (above).
- [ ] 1.5 Test and evidence plan: pure core tests, rendered screenshots inspected, the agent protocol, memory reports.

**Exit:** `docs/0101_01_design-and-stack.md` covers 1.1–1.5.

### Step 2 — Navigable shell (no speech)
**Status:** ⏳ green-lit, not started
- [ ] 2.1 `src/camp-currie/`: a pure core (scenes, actions, state) and a pygame renderer at 720×720.
- [ ] 2.2 Title, Mission select (Level 1 open, Levels 2–3 shown locked), Briefing, Checkpoint, Your turn, Result and Debrief, navigable with the arrows, Return and Escape.
- [ ] 2.3 An explicit "no microphone, simulated" sign on Your turn; no audio of any kind.
- [ ] 2.4 Development agent protocol (`--agent`, JSON lines) and frame capture (`--shot`).
- [ ] 2.5 Tests under `test/camp-currie/` with a `.feature` contract; every screen rendered and inspected; peak RSS reported for the full run.

**Exit:** the shell runs on Termidor and `luna-pi`, every screen is reached with the keys alone, and the tests pass.

### Step 3 — Simulated first mission (no speech)
**Status:** ⏳ green-lit, not started
- [ ] 3.1 "Meet the Crew": five checkpoints, the names Mannie, Wyoh, Mycroft, Mike and Luna, each with a crew portrait drawn in code and a pronunciation hint.
- [ ] 3.2 The deterministic evaluator drives each attempt (a fixed script, seeded for tests); "listen again" shows the prompt again, since there is no audio.
- [ ] 3.3 Progress (five signal lights), retries, the uncertain state with its reason, and a debrief saying the result is simulated, not a pronunciation score.
- [ ] 3.4 Tests for the success, retry and uncertain paths and for a full mission, with screenshots of the run inspected and the peak RSS on the desk and on `luna-pi`.

**Exit:** a person can play, retry and finish the five-checkpoint mission with the keys alone, and the record is in `docs/0201_01_shell-and-mission-result.md`.

### Step 4 — Speech and pronunciation experiment (later)
**Status:** ⏳ not green-lit
- [ ] 4.1 Mycroft capture, STT and TTS contracts, and an opt-in sample corpus.
- [ ] 4.2 Compare lexical checking, known-word handling, phoneme alignment or GOP scoring, and abstention.
- [ ] 4.3 Latency and peak RSS on Luna; separate transcription errors from phonetic errors.

### Step 5 — Three playable levels with speech, and the field exam (later)
**Status:** ⏳ not green-lit
- [ ] 5.1 Level data for Levels 1–3, with the spiral scheduler and per-skill mastery.
- [ ] 5.2 Speech behind the evaluator contract; original character sprites.
- [ ] 5.3 The field exam's traversal (corridor or tiles: compare legibility and cost on Luna).
- [ ] 5.4 On Luna, with Mannie's agreement and Wyoh's launch: experience, offline run, memory and cold start.

## Non-goals (Steps 1–3)

- No microphone, STT, TTS, scoring, model, network or audio.
- No Luna deployment, Wyoh launch integration or gamepad-daemon change.
- No browser, engine or LLM in the game; no hidden helper process.
- No Final Fantasy assets or identity. The series' key art and OFL fonts are used, with their provenance recorded; Hazel's video sources are not changed.

## Open questions

- Does the teacher character reuse Luna's cast, or is it a new original character?
- How much pronunciation feedback can be trusted for French-accented English (Step 4)?

## Sources

- Codex's archive, for reference only: `tmp/camp-currie-codex-20261101/` (outside Git).
- `docs/01_principles.md`; `worklines/hazel/docs/0103_01_series-template.md`; `worklines/mycroft/plan_mycroft.md`.

## Workline artifacts

- (Step 1) `docs/0101_01_design-and-stack.md`
- (Steps 2–3) `docs/0201_01_shell-and-mission-result.md`

## Time log

| Date | Entry |
|---|---|
| 2026-11-01 | Codex: Steps 1–3 attempted; result rejected by Adam. |
| 2026-11-02 | Wyoh's session: plan rewritten; Codex's uncommitted files archived in `tmp/`; pygame-ce measured on Termidor and `luna-pi`; plan sent to Professor for review. |
