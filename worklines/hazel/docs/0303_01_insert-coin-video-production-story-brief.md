# Story 3 brief — Insert coin: how the cell learned to make videos

> **Freshness:** ⚪ draft · **Written:** 2026-11-04 · **Checked:** 2026-11-04 · **Step:** hazel 3.3

**From:** Adam via ChatGPT
**To:** Hazel
**Date:** 2026-11-04
**Status:** User-selected **next story**, planning only; no production green light.

## Editorial decision

Adam calls this the next Hazel story and stresses that it is **very introspective**.

This is not a promotional tour of rendering tools or a generic making-of. It is **Hazel and the cell looking at how they themselves learned to tell the project’s stories**: creating the first trailer, discovering the repeated mistakes and costs, reflecting on them, then turning experience into reusable craft. The story is about the maker becoming aware of its own method, then changing that method.

**Working title:** *Insert coin — the video production story*.
**Period:** October–November 2026.

## Narrative arc

1. **The first commission:** a retro-sci-fi trailer, a deliberately small sub-agent context, and the unexpected *INSERT COIN* framing: every intelligence has a cost.
2. **The first toolchain:** deterministic HTML canvas frames from `renderFrame(t)`; Playwright screenshots into ffmpeg; synthesized and NES-2A03-style music aligned to a common clock.
3. **The first self-criticism:** the original soundtrack was not '80s enough, on-screen text was too small for a phone, cuts needed reading time, and successive episodes reused too many nearly identical scenes.
4. **Learning by measurement:** readability audits, contact sheets, verified on-screen facts, music maps, hit alignment and loudness checks. Measure against the real user’s feedback rather than the agent congratulating itself.
5. **The costly habit:** an agent hand-writes hundreds of lines of visual code and score for each episode (approximately 290k tokens for one); copying earlier episodes preserves its weaknesses.
6. **The turning point:** Hazel extracts 23 sequence templates, sets variation rules, and makes the model author a ~145-line YAML script rather than the entire video. Deterministic code does the layout, score, lint, capture and rendering.
7. **The measurable change:** the scripted Story 2 revision used ~54k tokens, compared with ~290k for a previous whole hand-made episode (different scopes: avoid overstating a like-for-like production saving). Building the pipeline itself cost ~408k tokens once and must be amortized.
8. **The introspective ending:** the cell learns that accumulating transcripts is not enough. When a mistake recurs, turn the lesson into a test, a contract, a template, or a tool. The human still decides what deserves creative judgment.

## Core thesis

> The interesting change is not “an agent can produce a video,” but “the system has learned how to produce videos, and the agent can focus on what is new.”

This connects to TANSTAAFLLM’s least-sufficient-intelligence principle and to future cross-agent memory consolidation. Distinguish **declarative memory** (what Hazel learned) from **procedural memory** (the validation and generation code that embodies it). Do **not** claim an automated global memory service already exists.

## Tone and visual framing

Self-aware, playful and reflective, never self-congratulatory. Hazel narrates her own trial and error: the first handmade video, its technical debt, the time and token bill, the moment she recognizes repetitive scene patterns, and the decision to teach the *machine* the repeatable parts. The NES/arcade world turns inward: **who pays the coins to build the game about paying coins?**

Use Hazel’s series template and script-to-video pipeline. Invent a new sequence template rather than repeating the stage/stamp/checklist formula. Preserve phone readability, traceability of claims, and music/visual alignment.

## Evidence and checks before production

- `worklines/hazel/video/trailer/NOTES.md` and `README.md`; trailer and Stories 1–2 build sources
- `worklines/hazel/docs/0501_01_sequence-library-analysis.md`
- `worklines/hazel/docs/0601_01_token-lean-video-pipeline.md`
- `worklines/hazel/docs/0606_01_how-the-video-generator-works.md`
- `worklines/hazel/docs/0103_01_series-template.md`
- `worklines/hazel/plan_hazel.md` and `worklines/professor/plan_professor.md` Steps 9 and 11

Keep distinct: the trailer's ~86.5-s control render versus Story 1's ~94-s revised cut; video execution spends CPU and time even when it spends no LLM tokens; and the ~54k-token revision is not directly equivalent to a full ~290k-token new episode. The end-to-end new-episode cost remains to be measured.

## Boundary

Adam has approved **the topic and its position as the next story**, not writing an episode, generating media, deploying artifacts, or publishing. Hazel plans it in her own workline and asks for an explicit green light before production.
