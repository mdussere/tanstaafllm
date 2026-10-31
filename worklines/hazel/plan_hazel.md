---
**Status**: 📋 Draft (prepared by Professor, 2026-10-31; the user opens the session)
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

## 🚦 Green light protocol

- Default: planning and documentation only until the user says **"🟩 go Step N"** (Professor may give gos on the user's mandate).
- Finished work follows the commit-and-push routine with GitHub links (`skills/commit-prep`).

## Plan steps (no execution until green light)

### Step 1 — Take over the videos
- [ ] 1.1 Read `worklines/professor/plan_professor.md` Steps 9 and 11, `worklines/professor/video/` (README, NOTES), and the private page https://claude.ai/artifact/Wqpg9wD9Ew5MunsYFhxqLn.
- [ ] 1.2 Move the trailer's sources to `worklines/hazel/video/trailer/` (with Professor), keeping history.
- [ ] 1.3 Write the series template (`docs/0103_01_series-template.md`): title and end cards, palette, type scale, transitions, sound palette, length, captions on a phone.

### Step 2 — Story 1: the bring-up
- [ ] 2.1 Review the sub-agent's cut (`/data/michael/tanstaafllm/video/bringup-v1/`) against the template; fix or redo.
- [ ] 2.2 Bring its sources into Git, render, add it to the private page.

### Step 3 — The next episodes
- [ ] 3.1 Text-to-shell (`docs/05`), the cell at work (Professor's Step 10 log), the principles.

### Step 4 — A public page
- [ ] 4.1 A public page presenting the trailer and the episodes, after the user's go on its content and links (LinkedIn, YouTube).

## Progress tracking ✅

- 📋 Plan drafted by Professor; the session is not yet opened.

## Time tracking (use `date`) ⏱️

### Time log

| Timestamp (`date`) | Update |
|---|---|
| 2026-10-31 | Plan drafted by Professor at the user's request (Hazel chosen as the creative director and video producer). The user will open the Hazel session on Termidor. |

## Workline artifacts

- `worklines/professor/video/` — the trailer's sources (to move in Step 1.2).
- `/data/michael/tanstaafllm/video/` — packages, briefs and renders of the sub-agents (music A, story A/B, bring-up).
