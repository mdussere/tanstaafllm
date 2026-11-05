---
**Status**: 📋 Planning (session opened by the user, 2026-10-31; no step green-lit yet)
**Date**: 2026-10-31
**Priority**: Medium
**Maintained**: Yes
---

# Hazel — the cell's creative director and video producer (workline `hazel`)

## Overview

Hazel makes the project's videos and pages for the outside world: the trailer, one short video per story, and later a public page. She owns the series' artistic unity (look, type, sound, rhythm, episode structure) and the production pipeline (HTML canvas → Playwright → ffmpeg, NES-chip sound).

In the novel, Hazel Meade is the red-haired twelve-year-old who helps Mannie and Wyoh escape the police raid and then runs the children's network of lookouts and couriers: she gets the messages through. Heinlein's earlier *The Rolling Stones* (1952) shows her as Hazel Stone, the family's gun-toting grandmother and a founder of the free Moon. The user chose her for this role (2026-10-31). See `docs/00_the-moon-is-a-harsh-mistress.md`.

Done means: the trailer and the first story videos are published, they read as one series, each is reproducible from sources in Git, and a public page presents them.

## Workline directory layout

- Plan (this file): `worklines/hazel/plan_hazel.md`
- Produced docs: `worklines/hazel/docs/`
- Video sources: `worklines/professor/video/` today (the trailer); to move under `worklines/hazel/video/` in Step 1.
- Renders: `results/hazel/<topic>/<timestamp>/` (not in Git); large working files in `/data/michael/tanstaafllm/video/`.

## Goals ✅

- One recognisable series: the trailer, then one episode per story (bring-up, text-to-shell, the cell at work, …).
- Every video reproducible from its sources with one build command.
- Every on-screen fact traceable to a project page; every text readable (the `timing.py` reading model).
- Videos the user can watch and save from a phone (private claude.ai page), then a public page.

## Non-goals ❌

- Screenshots or photos of real screens in the videos (the user rejected them, 2026-10-25).
- Copyrighted music, art or covers; anything not licensed for reuse.
- Changing other worklines' code or docs; Hazel asks them for facts.
- Status reports dressed as videos: the videos tell the project's stories and vision.

## Key decisions / assumptions

- **The look** is the trailer's: retro sci-fi pixel-art arcade, Heinlein's Moon; navy/violet with amber, cyan and chrome; Press Start 2P and VT323 (OFL); scanlines and vignette; white flashes and block dissolves; stamps.
- **The sound** is an emulated NES 2A03 chip: two pulses, a triangle, noise; mono; 60 Hz frames; no reverb (user, 2026-10-30: "plus années 80").
- **Reading holds:** the last text before a cut stays long enough to be read (0.4 s + 0.25–0.30 s per word, at least 1 s; `timing.py`).
- **Composition by sub-agents** works well when they get a short brief and the project's own texts, without Professor's context (user, 2026-10-25).
- **Adam is the user**: the human who gives the go.

## Risks / constraints

- **Facts drift:** the story pages change; every on-screen fact carries its source in the video's `NOTES.md`, and a doubtful fact goes to the owning workline before a render.
- **Shared code copied, not shared:** each video holds its own copy of the renderer head, `nes.py`, `capture.py` and `timing.py`; a fix in one is not in the others. Factor into `video/common/` once a third video exists.
- **Renders are slow** (about 7 min each on Termidor) and not in Git; check stills first, render once.
- **Shared index:** other sessions commit from the same worktree; stage only Hazel's files, just before committing (on 2026-10-31 a staged `git mv` was carried into Mike's commit `3039e69`).

## 🚦 Green light protocol

- Default: planning and documentation only until the user says **"🟩 go Step N"** (Professor may give gos on the user's mandate).
- Finished work follows the commit-and-push routine with GitHub links (`skills/commit-prep`).

## Plan steps (no execution until green light)

### Step 1 — Take over the videos
**Status**: ✅ Done (go from Professor on the user's mandate, 2026-10-31)
- [x] 1.1 Read `worklines/professor/plan_professor.md` Steps 9 and 11, `worklines/professor/video/` (README, NOTES), and the private page https://claude.ai/artifact/Wqpg9wD9Ew5MunsYFhxqLn. (Read: README and NOTES; Steps 9 and 11 and the page through Professor's summary of 2026-10-31.)
- [x] 1.2 Move the trailer's sources to `worklines/hazel/video/trailer/` (with Professor), keeping history. Root path in `build.sh` and README fixed, renders in `results/hazel/trailer/`; control render from the new path: 86.5 s, exit 0 (`results/hazel/trailer/20261031T…-move-check/`).
- [x] 1.3 Write the series template (`docs/0103_01_series-template.md`): title and end cards, palette, type scale, transitions, sound palette, length, captions on a phone.

### Step 2 — Story 1: the bring-up
**Status**: 🧪 In progress (2.1 and 2.2 done; 2.3 pending)
- [x] 2.1 Review the sub-agent's cut (`/data/michael/tanstaafllm/video/bringup-v1/`) against the template; fix or redo.
  - The user's review (relayed by Professor, 2026-10-31): "Faites juste ces deux modifications-là, réadapter la musique et on est bon." Exactly fixes A and B, the score refitted, nothing else.
  - ✅ Fix A, Stage 1 "Secure the original card": replace the "62 BYTES" failure in Stage 1 with a positive first move: the whole factory card is extracted and stored safely on disk, then explored. Message: "first, secure the original; then explore it". Sources (Professor, checked): `worklines/luna/plan_luna.md` Step 5.1 (card 48.8 GiB) and 5.2 (golden image archived 2026-10-03, 42,226,178,053 bytes `.img.zst`, raw-card and decompressed-image SHA-256 identical); `docs/03` Step 1 (verified byte for byte, drawer).
  - ✅ Fix B, new Stage 2 "Choose a system" (20–26 s; later scenes 6 s later; 8 stages): say explicitly that we chose ArchR, before the black-screen stage (`docs/03` Step 2: several community systems for these clones; one looped its interface and was set aside; ArchR, based on Arch Linux, looked the most like a normal Linux and already had a Wi-Fi driver).
  - Result: 94.0 s, reading audit +0.0 s of holds, −15.7 LUFS integrated, true peak −0.9 dBTP (0.1 dB above the template's −1, accepted); contact sheets inspected (`results/hazel/story1-hello-luna/20261031T184418/`). Delivered to `~/Videos/TANSTAAFLLM/tanstaafllm-story1-hello-luna.mp4`; the first cut kept beside it as `…-v1-88s.mp4`.
- [x] 2.2 Bring its sources into Git, render, add it to the private page. Sources in `worklines/hazel/video/story1-hello-luna/` (`src/build.sh` → `results/hazel/story1-hello-luna/<timestamp>/`); private page refreshed by Professor.

- [ ] 2.3 Thumbnails from the renderer: a `thumbnail` scene in each video's `index.html`, to replace Professor's Pillow thumbnails (2026-10-31) once the user agrees.

### Step 3 — The next episodes
**Status**: 🧪 In progress (3.2 first version delivered 2026-11-01; waiting for the user's verdict)
- [ ] 3.1 Text-to-shell (`docs/05`), the cell at work (Professor's Step 10 log), the principles.
- [ ] 3.2 **Story 2, Wyoh: touching the desktop without screenshots** (user, 2026-10-31: "c'est ton premier travail"). The story: Wyoh's goal from the start is to interact with the desktop natively, not through screenshots; to take hold of it directly and get feedback. First version, then the user judges.
  - [x] 3.2a Build the story with Wyoh (session `tanstfaafllm-8e`): ask for the arc, the turning points and the facts. Wyoh answered with seven beats, sources and a must-not-say list: `docs/0302_02_note-from-wyoh-story.md`. Sentence to remember: "Don't look at the desktop, ask it: the compositor already knows what a screenshot can only guess."
  - [x] 3.2b Write the episode brief (series template, Story 2 frame) and have it composed, by a sub-agent with the brief and the project texts (as for Story 1) or by Hazel. Brief: `docs/0302_01_wyoh-story-brief.md` ("ASK THE DESKTOP", seven stages, ≤ 90 s). A sub-agent composes it in `/data/michael/tanstaafllm/video/story2-wyoh/`, starting from Story 1's sources.
  - [x] 3.2c Review against the template and the reading audit; check each fact against its source (and with Wyoh); render; deliver; sources in Git; private page; commit and push. **First version, 2026-11-01:** 90.0 s, reading audit +0.0 s, −15.3 LUFS, −1.1 dBTP; contact sheets inspected by Hazel. Delivered to `~/Videos/TANSTAAFLLM/tanstaafllm-story2-ask-the-desktop.mp4`; sources in `worklines/hazel/video/story2-ask-the-desktop/`; added by Hazel to the private page (1280 × 720 copy, 7.4 MB), which also got Story 1's eight-stage blurb and the new sources path. Asked Wyoh to confirm three staged points (Sway's screenshots in the black-panel stage, the seven layer names, the agent pressing FN+B to reach Mike).
  - [ ] 3.2d The user's verdict on the first version; Wyoh's fact check; YouTube upload by the user.
    - Wyoh's check (2026-11-01): points 1 and 2 right; point 3 reworded ("A DEV AGENT PRESSES THE SAME BUTTONS", "MIKE STARTS, ANSWERS IN 13 s") so the agent and Mike don't read as one.
    - The user (2026-11-01, watching on a phone held upright): title subtitle at VT323 90 px "très confortable"; PRESS START (PS2P 28 px) "limite". Hazel's analysis: most key messages sit at or below PRESS START's size (VT323 48 px sentences, PS2P 32 px). Rule proposed: one short key message per screen at ≥ 50 px glyph height (VT323 ≥ 90 / PS2P ≥ 56), one secondary at ≥ 35 px, the rest cut or glance-only.
    - [x] Rework Story 2 with that rule (user: "demande à un sous-agent de reprendre 2"). Done by a sub-agent, reviewed by Hazel: one key message per screen at ≥ 50 px, secondary lines cut; 90.0 s, +0.0 s holds, −15.3 LUFS, −1.1 dBTP (`results/hazel/story2-ask-the-desktop/20261101T124410/`). Delivered to `~/Videos/TANSTAAFLLM/` and the private page. Left: NOTES.md's fact table still lists lines that were cut.
    - [ ] Story 2, second revision (user, 2026-11-02): (a) drop stage 7 "Seven layers": a regression, not part of the story; (b) open with the inspiration: Playwright lets an LLM drive a browser by reading its DOM, not screenshots, and Wyoh wants the same for a desktop. A new stage 1 shows the comparison table, BROWSER | DESKTOP (source `worklines/wyoh/docs/0000_04_desktop-automation-model.md`, the table "Playwright | Wyoh"; on screen, Sway's window tree stands for the DOM, because the DWOM is a design). **⏸️ Postponed (user, 2026-11-02): no new video is generated before the pipeline transformations of Step 6.** The sub-agent was stopped; its partial edits are saved in `/data/michael/tanstaafllm/video/story2-wyoh/patches/20261102-playwright-opening-partial.patch` and the sources are back at their committed state. This revision will be the first test case of the new pipeline (6.6).
    - [x] Then: the rule into the series template (done, §6b). Story 1 stays as it is (user, 2026-11-02). The trailer: not decided.
  - [x] 3.2e **Blind one-second storyboard comprehension check (user go, 2026-11-05):** a reviewer with no project context received only one still per second from the current scripted Story 2 preview. They correctly inferred the core story—do not guess from screenshots; query the desktop's structured tree, act, and wait for events—and identified the remaining uncertainties. Evidence: [`docs/0302_03_blind-storyboard-comprehension.md`](docs/0302_03_blind-storyboard-comprehension.md). A later, separately documented pass may provide minimal context; none was provided in this first pass.
  - [x] 3.2f **Compositor-message correction (user review, 2026-11-05):** Stage 3 now makes the causal chain explicit: “ARCH RUNS SWAY”; “SWAY RUNS LUNA'S DESKTOP. / DON'T REBUILD IT. ASK IT.” The visual tags retain `ALREADY RUNNING / UNMODIFIED / NO FORK` as supporting evidence. Strict preview passed and `t042.90.png` was inspected under `results/hazel/story2-arch-sway-chain-20261105T212428/`.
  - [ ] 3.2g **Story 2 visual and narrative revision (user go, 2026-11-05):** enlarge Wyoh's name on the player card; explain the first single-screen design and its multi-window limitation; explain Sway and make its unmodified/no-fork status more prominent than the measurements; clarify the black physical panel, working screenshots and GPU-driver resolution. Improve the Playwright comparison for legibility. Use GitHub runners for preview, visual inspection and a full video; retrieve results locally for review.

### Step 3.3 — Story 3: Insert coin — how the cell learned to make videos
**Status:** 🟨 V3b PREVIEW READY FOR ADAM REVIEW (2026-11-05): original T01/title and event-driven score are the quality reference; user-approved compact Hazel PNG vignettes remain. SVG V2 was technically rendered but artistically rejected. The low-resolution bitmap preview passed GitHub Actions; no 1080p master/merge/publication before Adam approves the new cut.
- [x] 3.3a Record the user's editorial decision: **this is the next story, and it is deliberately very introspective**. It is Hazel reflecting on how she and the cell produced their own videos and learned to industrialize that production, not simply a tutorial about the rendering stack. Brief: [`docs/0303_01_insert-coin-video-production-story-brief.md`](docs/0303_01_insert-coin-video-production-story-brief.md).
- [ ] 3.3b Validate narrative and sourced facts with Adam: initial sub-agent creativity, deterministic canvas + NES score, self-criticism of readability/repetition/token expense, **first the manual-work rationalization through the 23-template sequence library with the rule that every new video introduces at least one new template; only then instrumentation and automation through YAML episode scripts compiled to frames, music and MP4**, measured cost and caveats. Tie to declarative versus procedural knowledge, without claiming the global memory system already exists.
- [x] 3.3c User's explicit go (2026-11-04): produce the full episode with 1–2 new templates. **First cut produced** by `cell/adam`, using Hazel's existing YAML compiler and NES score: `video/episodes/story3-insert-coin-how-we-made-videos.yaml`, 13 scenes, 112.0 s, 1920×1080/30 fps H.264/AAC; `--strict` audit +0.0 s and lint 0 overflow/margin/overlap/clear zone/squeeze/phone-rule failures. GitHub Actions run [#41813180077](https://github.com/mdussere/tanstaafllm/actions/runs/41813180077), [video + reports artifact](https://github.com/mdussere/tanstaafllm/actions/runs/41813180077/artifacts/13313693124). New candidate templates: **T24 `template_wall`** (manual reuse plus renewal rule), **T25 `payback_meter`** (the video itself is the second build). Their cards are in `video/library/`, pending visual approval.
- [x] 3.3e **Story 3 cinematic revision** (Adam user full-autonomy go, 2026-11-04): the first film's reused HUDs and comparison tables were judged visually inappropriate. A new 13-sequence, 112-s cut uses 20 independently authored SVG assets, a parametric alpha/z-order/timing compositor (`video/common/cinematic.js`) and YAML-defined shots under new T24 `cinema` frame. **Successful 1080p/30-fps MP4 with NES score:** [Actions #41843330999](https://github.com/mdussere/tanstaafllm/actions/runs/41843330999), [master, preview, contact, lint artifact](https://github.com/mdussere/tanstaafllm/actions/runs/41843330999/artifacts/13331140325). Strict layout/reading lint clean (all zero, 0 extra holds). Editorial and implementation note `docs/0303_04_story3_v2_cinematic_implementation.md`. Candidate only; neither merged nor publicly published. Await Adam's visual review; do not claim measured payback.
- [ ] 3.3d Adam and Hazel review the visual cut and its illustrative amortization math. The pipeline build's one-time ~408k tokens and the ~236k saving estimate are NOT a measured like-for-like end-to-end Story 3 token result. Do not publish until approved.
- [x] 3.3f **User review + bitmap art direction, 2026-11-04.** Adam rejected generic recycled comparison/HUD compositions, then rejected the SVG puppet look and flat, continuous music. Original Story 2/trailer provide the *visual and musical* reference. PNG poses, frame-switching animation (pre-drawn rotations/expressions), grounded Hazel feet, a vignette using **no more than half the screen**, readable key text outside, and *varied* shots (prop close-up, vignette, workshop, arcade title/reveal) are the current decisions. Three local layout previews (budget, template library, YAML compile) were approved as balanced, **not** to be repeated mechanically through all scenes. Sources: `docs/0303_05_bitmap_sprite_pipeline.md`, `docs/0303_07_v3b_production_checkpoint.md`.
- [x] 3.3g **Story 2 control experiment (2026-11-04):** both original handmade Story 2 (historical `src/index.html` + `src/score.py`) and generic YAML reconstruction were rebuilt successfully in [Actions #41869289272](https://github.com/mdussere/tanstaafllm/actions/runs/41869289272). The latter differs markedly in plot structure, specific animated actions and event-synchronised score; a strict layout lint pass is *not* artistic equivalence. Evidence `docs/0303_06_story2_reference_regression.md`.
  - [x] 3.3g.i **Private visual comparison page (user request, 2026-11-05):** the two verified 90-s preview MP4s from the control artifact are embedded side by side with synchronized-review controls and an explicit non-equivalence warning: [private review page](https://tanstaafllm-story2-comparison.familiarmotor.chatgpt.site). It is a private review surface, not the public release page and not a new video render.
- [x] 3.3h **Durable transfer checkpoint (2026-11-04):** [`docs/0303_08_note-from-adam-v3b-handoff.md`](docs/0303_08_note-from-adam-v3b-handoff.md). Adam's ChatGPT committed planning, reviews and baseline; it did **not** push the local PNG/MP4 binaries or implement their in-repo frame-based renderer. **Update:** these bytes have now been committed under `video/common/art/sprites-v3/` in `13fde527`; only the local prototype MP4/previews are not committed.
- [x] 3.3i **Next implementation — PREVIEW ONLY (user go):** ✅ source PNG sprite pack and manifest committed directly to `cell/adam` ([`13fde527`](https://github.com/mdussere/tanstaafllm/commit/13fde5270fe96c5d8db32b2ea5829036d8ac7c5b)); SVG visuals replaced with nearest-neighbour PNG frame switching and bottom-anchored Hazel poses; original-style stamps/cut flashes and event-driven score restored; varied 13-scene framing composed. GitHub Actions [#42042702087](https://github.com/mdussere/tanstaafllm/actions/runs/42042702087) generated the **640×360/10-fps, 112-s preview MP4** and passed strict lint, duration/audio verification and artifact upload. Contact sheet inspected locally; handoff record: [`docs/0303_09_story3_v3b_preview_verification.md`](docs/0303_09_story3_v3b_preview_verification.md). **Await Adam's artistic review: do not render 1080p, merge or publish** until Adam explicitly approves this preview.
- [ ] 3.3j After Adam approves the completed V3b preview: only then consider a full 1080p render, fact/accounting review and release decision. The ~408k/~236k/~1.73 figures remain illustrative; prior comparison was full handmade episode vs scripted revision, not matching scope.

**Opening and ending (Adam, 2026-11-04):** TANSTAAFLLM applies to the cell's own method: the project is intended to run on a single **€20/month Claude Pro subscription**. Video production must respect that budget. The retrospective ending is a victory over the investment: **~408k tokens to build the pipeline, indicative savings ~236k per episode (290k − 54k), break-even ~1.73 episodes — amortized by the second pipeline video, Story 3.** **Crucial self-referential reveal:** the audience is watching the second pipeline video, Story 3; producing this very film is what repays the pipeline investment. Save that realization for the final beat: the video proves its own point while it runs. Treat the ~1.73-video break-even as indicative and measure Story 3's full cost before claiming realized savings, because the 54k figure came from a *revision* and the 290k from a *full episode*. “The agent can make a video” becomes “The system has learned to make videos; the agent focuses on what changes.”

### Step 4 — A public page
**Status**: ⏳ Pending
- [ ] 4.1 A public page presenting the trailer and the episodes, after the user's go on its content and links (LinkedIn, YouTube).

### Step 5 — A library of sequence templates
**Status**: ✅ Done (2026-11-01)
- [x] 5.1 Analyse the templates used in the trailer, Story 1 and Story 2: what each does, how often, who made it; propose a plain-file structure (`docs/0501_01_sequence-library-analysis.md`). Reason (user): the sub-agents copy the previous video, so Story 2 reads like Story 1; a template box keeps unity and makes change deliberate.
- [x] 5.2 The user agrees on the structure (2026-11-01: "Vas-y, fais la librairie des templates.").
- [x] 5.3 (built by a sub-agent, reviewed by Hazel, 2026-11-01; 23 template folders, 2.5 MB; the sub-agent hit the session limit during its final checks, Hazel checked every folder has its card, snippet and still) Build `worklines/hazel/video/library/`: one card per template (concept, effect, dynamics in beats, graphic elements, text slots sized for the phone, music cue, variants with stills, code snippet), plus `uses.md` for the three videos.
- [x] 5.4 Put the episode rules into the series template (§6b phone text, §6c library rules, 2026-11-01): frame templates mandatory; at least three library templates in the body, none filling more than half the scenes; at least one new template per episode, added to the library after review; briefs name the templates.

### Step 6 — A token-lean pipeline: the model writes a script, the CPU builds the video
**Status**: 🧪 6.2–6.6 done; 6.7 (assets) in preparation (user, 2026-11-02: `🟩 go` 6.2–6.6, "essaie déjà de reproduire la story 2 avec le pipeline"). Rule kept: no new video until the pipeline is done. Scope: the pipeline is built from Story 2; the trailer and Story 1 stay on their own frozen sources (not migrated). Built by one Sonnet sub-agent, reviewed by Hazel; Rive not used (§4b of the analysis)
- [x] 6.1 Analysis: where the tokens go (≈ 160 k + 129 k sub-agent tokens for Story 2), and what a generator can do instead (`docs/0601_01_token-lean-video-pipeline.md`).
- [x] 6.2 `video/common/`: one shared runtime (renderer head, nes.py, capture, contact), extracted from Story 2. The trailer and Story 1 keep their frozen copies.
- [x] 6.3 Parametric templates with music cues: the frame and the most used body templates first.
- [x] 6.4 The episode script format and the generator (timeline, score cues, reading audit, NOTES.md tables).
- [x] 6.5 The layout lint as a text report (overflow, overlap, margins, phone glyph heights) and a low-resolution preview with one small contact sheet.
- [x] 6.4b Make the script high level. **Done (2026-11-02, Sonnet sub-agent, ≈ 193 k tokens once):** script 358 → 145 lines, 0 overrides; new `common/layout.py` (slots, positions, on-beat entries, cue marks); Story 2 special cases removed from the interpreter; 90.0 s, +0.0 s holds, −14.9 LUFS, −1.0 dBFS; lint 0 overflow / margin / overlap / CLEAR! zone, one key ≥ 50 px per scene; contact sheet reviewed by Hazel. Gaps: stage 3 tiles show several secondaries; stage 6 glance text slightly over the agent sprite (lint does not check text over shapes). Today `episodes/story2-ask-the-desktop.yaml` (358 lines) still carries positions, sizes and notes, because it had to reproduce Story 2 exactly. Templates should place the key and secondary slots by the phone rule and pick music cues from `mood`, so that a scene needs only its template, its texts and its sources; the low-level fields stay as optional overrides. **User (2026-11-02):** reduce the script's detail even if the result is no longer pixel-perfect; the interpreter must hold no code whose only purpose is to imitate the old Story 2. 
- [x] 6.6 Story 2 rebuilt from an episode script through the pipeline: same picture (pixel diff of stills against the current render), same timing, lint clean. **Rebuild done (2026-11-02):** 144 stills pixel-identical (mean abs diff 0.0000), WAV bit-identical, 90.000 s, −15.3 LUFS, 0 s holds; `lint.txt` reports 0 overflow, 0 overlap, 0 in the CLEAR! zone, 1 text in the 5 % margin, no key message on the end card (`results/hazel/story2-ask-the-desktop/20261102T005909/`). One-time building cost: ≈ 215 k tokens (Sonnet sub-agent). Still to do: the token count of an *edit* through the script (the postponed revision). **Target (user, 2026-11-02): at least halve the tokens per episode** compared with Story 2 (≈ 290 k sub-agent tokens), so ≤ ≈ 145 k for an episode or a revision made through the pipeline. **Measured (2026-11-02):** Story 2's revision through the script (seven-layers stage removed, new stage 1 "LIKE PLAYWRIGHT, FOR A DESKTOP" with a new generic `compare_table` template) cost **≈ 54 k tokens** (Sonnet), against 129 k for the previous hand-made rework and ≈ 290 k for the whole episode: the target is met. Render `results/hazel/story2-ask-the-desktop/20261102T013303/`: 90.0 s, +0.0 s holds, lint 0 overflow / margin / overlap / CLEAR! zone, one key ≥ 50 px per scene. Hazel checked the filled table on a still; its rows are glance-size (to watch on a phone). Gap: `compare_table` lacks its README entry text. Building the pipeline cost ≈ 408 k tokens once (6.2–6.5 and 6.4b). Token count recorded and compared with Story 2's ≈ 290 k. Then Story 2's postponed revision (Playwright opening, no seven-layers stage) as script edits.
- [ ] 6.7 Asset pack, prepared once on the CPU (user's idea, 2026-11-02): characters cut out of the key art on a transparent background (Mannie, Wyoh, Mike, Professor), and pixel-art versions quantised to the series palette; the title logo, the moon alone, starfield layers; the code-drawn sprites (handheld with its screens, coin, agent robot, chip, router, SD card, disk, keyboard) rendered to PNG; a sprite sheet and a manifest (name, size, anchor, source, licence). Templates call assets by name. Cut-outs shown to the user before adoption. **Source changed (user, 2026-11-02): the user generates the assets in ChatGPT with `wallpaper.png` as reference;** prompts in `docs/0607_01_chatgpt-asset-prompts.md`. Characters (user, 2026-11-02): Hazel crops them on the CPU (`common/assets/crops/`), ChatGPT only removes the background and the overlapping neighbours and rebuilds hidden parts (prompt A0), then Hazel makes the 64 × 64 sprites on the CPU (a first CPU-only try in `common/assets/sprites-cpu/`). Hazel then checks, snaps to the pixel grid, writes the manifest and wires the templates.

## Progress tracking ✅

- 📋 Plan drafted by Professor.
- 🟢 Session opened on Termidor (`tanstfaafllm-29` [2a2a0c]), 2026-10-31; onboarding questions sent to Professor. Professor answered and gave `🟩 go Step 1` on the user's mandate.
- ✅ Step 1: trailer sources moved to `worklines/hazel/video/trailer/` (`git mv`); series template drafted (`docs/0103_01_series-template.md`, awaiting the user's review). Control render from the new path: see the time log.
- 🧪 Step 2: Story 1 revised (fixes A and B, score refitted), rendered (94.0 s) and delivered; the user re-uploads it to YouTube. 2.3 (thumbnails from the renderer) pending.

## Time tracking (use `date`) ⏱️

### Time log

| Timestamp (`date`) | Update |
|---|---|
| 2026-10-31 | Plan drafted by Professor at the user's request (Hazel chosen as the creative director and video producer). The user will open the Hazel session on Termidor. |
| sam. 31 oct 2026 18:18:14 CET | Session opened by the user (`tanstfaafllm-29` [2a2a0c]); row added to `worklines/agents.md`; Professor asked how the cell works and about Steps 1.2 (trailer move), the trailer's state and the bring-up cut. |
| sam. 31 oct 2026 18:28:02 CET | Professor: `🟩 go Step 1` on the user's mandate. Trailer moved with `git mv`, paths fixed, control render started; series template drafted. Professor relayed the user's review of Story 1 with `🟩 go Step 2`, then asked to hold until the user reviews Story 1 with Hazel; fixes A and B recorded as pending. |
| sam. 31 oct 2026 18:53:33 CET | Step 2 on the user's go (via Professor): Story 1 sources brought into Git, fixes A and B, score refitted (global 6 s offset after the new stage), reading audit +0.0 s, rendered 94.0 s / −15.7 LUFS / −0.9 dBTP; stage-1 text moved up after a CLEAR! overlap seen in the contact sheet; delivered to `~/Videos/TANSTAAFLLM/`. YouTube links of the trailer and the first Story 1 cut recorded. Plan aligned with the `workplan` template (step statuses, risks). |
| sam. 31 oct 2026 19:54:55 CET | User: `🟩 go` for a Wyoh episode (Step 3.2): work Wyoh's story with her into a video, first version. Step 3.2 added. |
| sam. 31 oct 2026 19:57:16 CET | Wyoh's story note received (3.2a done); brief written (`docs/0302_01`); composition handed to a sub-agent in `/data/michael/tanstaafllm/video/story2-wyoh/`. |
| sam. 31 oct 2026 20:10:05 CET | Pause asked by the user via Professor (token limit): Story 2 sub-agent stopped; state recorded under 3.2. Nothing new started. |
| dim. 01 nov 2026 12:01:49 CET | Resume (user via Professor): one lean sub-agent finishes Story 2 from the save point in `/data/michael/tanstaafllm/video/story2-wyoh/`. |
| dim. 01 nov 2026 12:18:42 CET | Story 2 "Ask the desktop" first version: finished by a sub-agent from the save point, reviewed by Hazel, delivered, on the private page, sources committed. |
| dim. 01 nov 2026 12:38:24 CET | Wyoh's fact check applied; title subtitle at 90 px approved by the user; phone readability analysis; sub-agent reworks Story 2's text sizes. |
| dim. 01 nov 2026 12:46:45 CET | User: build a library of sequence templates (Step 5). Analysis and proposed structure written (5.1); waiting for the user's agreement. |
| dim. 01 nov 2026 12:54:10 CET | Story 2 reworked for phone reading (sub-agent), reviewed, delivered, private page updated. |
| dim. 01 nov 2026 13:00:54 CET | User agreed on the library structure (5.2); a sub-agent builds `video/library/` (5.3). |
| dim. 01 nov 2026 17:22:52 CET | Library built (5.3): README index, uses.md, 23 template cards with stills and snippets. 5.4 (episode rules in the series template) next. |
| dim. 01 nov 2026 18:08:49 CET | User: optimise video production for tokens, spend CPU instead. Step 6 proposed, analysis `docs/0601_01`. |
| dim. 01 nov 2026 18:14:09 CET | ⏸️ Pause (user via Professor, tokens low). State: Steps 1, 2.1–2.2, 3.2a–c, 5 done; waiting for the user on 3.2d (verdict on Story 2, YouTube uploads), 2.3 (thumbnails), the phone-rule check of Story 1 and the trailer, and Step 6 (go for the generator). Nothing running. |
| lun. 02 nov 2026 00:31:05 CET | User: Story 1 stays as it is; discussion of Step 6 opened. |
| lun. 02 nov 2026 00:34:18 CET | User: Story 2 revision: drop the seven-layers stage, open on the Playwright/browser parallel with a comparison table. Sonnet sub-agent launched. |
| lun. 02 nov 2026 00:36:40 CET | User: stop; no new video before the pipeline is transformed. Sub-agent stopped, partial edits saved as a patch, Story 2 sources restored. |
| lun. 02 nov 2026 00:45:40 CET | User: `🟩 go` Step 6 (6.2–6.6), first target: reproduce Story 2 with the pipeline. Sonnet sub-agent launched. |
| lun. 02 nov 2026 01:08:15 CET | Pipeline built (6.2–6.5) by a Sonnet sub-agent (≈ 215 k tokens, once); Story 2 rebuilt from its script, pixel-identical. 6.4b added: make the script high level. |
| lun. 02 nov 2026 01:10:28 CET | User: go 6.4b — high-level script, pixel-perfect not required, no Story-2-specific code in the interpreter. Sub-agent launched. |
| lun. 02 nov 2026 01:31:30 CET | 6.4b done: high-level script (145 lines), generic interpreter; reviewed and committed. 6.6 launched: Story 2's revision through the script, tokens measured. |
| lun. 02 nov 2026 01:38:50 CET | User: prepare graphic assets upstream (cut-out characters, logo, moon, starfield, pixel art). Proposed as 6.7; preview/full render folders to be suffixed. |
| lun. 02 nov 2026 01:42:46 CET | 6.6 done: Story 2 revised through the script for ≈ 54 k tokens (target ≤ 145 k met). Character crops and CPU sprites prepared for 6.7; prompts doc gained the crop-and-clean path. |
| lun. 02 nov 2026 02:06:34 CET | User's edits to Story 2, made by Hazel in the script, no sub-agent: screenshot trap first, then the Playwright analogy, which ends on "LET'S DO IT!" (new generic `clear_text`). Pipeline fixes: two-pass loudness normalisation (−15.0 LUFS, −1.5 dBTP), render folders suffixed `-full`/`-preview`, lint reads each stage's stamp text. Full render `20261102T015755-full`, delivered to ~/Videos and the private page. |
| lun. 02 nov 2026 02:24:58 CET | User: the screenshot-trap stage ends on a refusal, "NO GO!" in red with a failure buzz (new generic `clear_color`). Full render `20261102T021609-full`: 90.0 s, −15.0 LUFS, −1.2 dBTP, lint clean; delivered to ~/Videos and the private page. |
| lun. 02 nov 2026 08:08:43 CET | User: code review of the pipeline (Step 6), then `go` for its fixes, on branch `hazel/video-review-fixes` (pull request): PyYAML declared in the `video` group; the lint's CLEAR! zone follows the label and the stamp's rotation; contact stills mapped to output time through the holds (`common/timemap.py`); `bpm` other than 120 refused; scenes too short for their template and missing slots refused with the scene's name; squeezed texts reported; metric tiles one message, every tile an audit slot; `build.py --strict`; `test/hazel/` (25 deterministic, 2 integration). Story 2 rebuilt: stills, score and hits identical, `--strict` clean. |

| 2026-11-04 | Adam selects Story 3, *Insert coin — the video production story*, as Hazel's next episode. Editorial direction: highly introspective, reflecting on how the cell learned from its own video production and turned lessons into reusable procedures. Brief `docs/0303_01`; planning only, production requires separate go. |
| 2026-11-04 (evening) | Adam confirms 3.3 V3b creative direction: compact grounded PNG Hazel vignettes, varied framings and original trailer/Story 2 title, musical accents and stage transitions. Story 2 original-vs-YAML regression [#41869289272] passed and revealed visual/narrative/score drift. V3 asset pack and older local preview remain outside Git; follow-up is an improved **low-res preview only**. Transfer note `docs/0303_08`. |

## Workline artifacts

- **Published on YouTube by the user (2026-10-31):**
  - Trailer, "TANSTAAFLLM: insert coin, every token costs 🕹️": https://youtu.be/nUeNgyUc01k
  - Story 1, first cut (88 s, with "62 BYTES"), "TANSTAAFLLM · Story 1: Hello, Luna 🌕": https://youtu.be/HcUA7_bRu-8. The revised cut (94 s, secure the card, choose ArchR) needs a new upload by the user.
- Private phone page (Professor's): https://claude.ai/artifact/Wqpg9wD9Ew5MunsYFhxqLn, links both videos.
- `worklines/hazel/video/trailer/` — the trailer's sources (moved from Professor, 2026-10-31).
- `docs/0103_01_series-template.md` — the series template (draft).
- `video/common/` (runtime, templates, cues, generator, lint, README) and `video/episodes/` (episode scripts) — the script-to-video pipeline.
- `docs/0606_01_how-the-video-generator-works.md` — how a script becomes a video, and the measured token balance.
- `docs/0601_01_token-lean-video-pipeline.md` — where the tokens go; the script-to-video generator proposal.
- `video/library/` — the sequence template library (index, uses, 23 cards).
- `docs/0501_01_sequence-library-analysis.md` — templates in the three videos, and the proposed library structure.
- `docs/0302_01_wyoh-story-brief.md` — Story 2 brief; `docs/0302_02_note-from-wyoh-story.md` — Wyoh's story (from Wyoh).
- `worklines/hazel/video/story2-ask-the-desktop/` — Story 2 "Ask the desktop" (Wyoh) sources, first version 2026-11-01.
- `worklines/hazel/video/story1-hello-luna/` — Story 1 "Hello, Luna" sources (from the sub-agent's `bringup-v1`, revised 2026-10-31).
- `/data/michael/tanstaafllm/video/` — packages, briefs and renders of the sub-agents (music A, story A/B, bring-up).

<!-- 2026-11-04: Story 3 source sprite assets are now in Git on `cell/adam` (13fde527); GitHub Actions has been constrained to preview-only (29cbbb8). Bitmap renderer integration and full artistic preview remain pending. -->
