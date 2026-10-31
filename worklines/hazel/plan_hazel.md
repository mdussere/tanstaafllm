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
**Status**: 🧪 In progress (3.2 Wyoh green-lit by the user, 2026-10-31)
- [ ] 3.1 Text-to-shell (`docs/05`), the cell at work (Professor's Step 10 log), the principles.
- [ ] 3.2 **Story 2, Wyoh: touching the desktop without screenshots** (user, 2026-10-31: "c'est ton premier travail"). The story: Wyoh's goal from the start is to interact with the desktop natively, not through screenshots; to take hold of it directly and get feedback. First version, then the user judges.
  - [x] 3.2a Build the story with Wyoh (session `tanstfaafllm-8e`): ask for the arc, the turning points and the facts. Wyoh answered with seven beats, sources and a must-not-say list: `docs/0302_02_note-from-wyoh-story.md`. Sentence to remember: "Don't look at the desktop, ask it: the compositor already knows what a screenshot can only guess."
  - [ ] 3.2b Write the episode brief (series template, Story 2 frame) and have it composed, by a sub-agent with the brief and the project texts (as for Story 1) or by Hazel. Brief: `docs/0302_01_wyoh-story-brief.md` ("ASK THE DESKTOP", seven stages, ≤ 90 s). A sub-agent composes it in `/data/michael/tanstaafllm/video/story2-wyoh/`, starting from Story 1's sources.
  - [ ] 3.2c Review against the template and the reading audit; check each fact against its source (and with Wyoh); render; deliver `~/Videos/TANSTAAFLLM/tanstaafllm-story2-<slug>.mp4`; sources in `worklines/hazel/video/story2-<slug>/`; tell Professor for the private page; commit and push.

### Step 4 — A public page
**Status**: ⏳ Pending
- [ ] 4.1 A public page presenting the trailer and the episodes, after the user's go on its content and links (LinkedIn, YouTube).

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

## Workline artifacts

- **Published on YouTube by the user (2026-10-31):**
  - Trailer, "TANSTAAFLLM: insert coin, every token costs 🕹️": https://youtu.be/nUeNgyUc01k
  - Story 1, first cut (88 s, with "62 BYTES"), "TANSTAAFLLM · Story 1: Hello, Luna 🌕": https://youtu.be/HcUA7_bRu-8. The revised cut (94 s, secure the card, choose ArchR) needs a new upload by the user.
- Private phone page (Professor's): https://claude.ai/artifact/Wqpg9wD9Ew5MunsYFhxqLn, links both videos.
- `worklines/hazel/video/trailer/` — the trailer's sources (moved from Professor, 2026-10-31).
- `docs/0103_01_series-template.md` — the series template (draft).
- `docs/0302_01_wyoh-story-brief.md` — Story 2 brief; `docs/0302_02_note-from-wyoh-story.md` — Wyoh's story (from Wyoh).
- `worklines/hazel/video/story1-hello-luna/` — Story 1 "Hello, Luna" sources (from the sub-agent's `bringup-v1`, revised 2026-10-31).
- `/data/michael/tanstaafllm/video/` — packages, briefs and renders of the sub-agents (music A, story A/B, bring-up).
