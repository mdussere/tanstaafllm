# A token-lean video pipeline: spend CPU, not tokens

> **Freshness:** ⚪ draft · **Written:** 2026-11-01 · **Checked:** 2026-11-01 · **Step:** hazel 6.1

**Question:** where does video production spend Claude Code tokens, and what can a generator running on the CPU do instead (user, 2026-11-01: "brûler du CPU plutôt que de brûler du token")?

## 1. Where the tokens go today

Measured in this workline on 2026-11-01. The sub-agent counts come from the harness usage notes.

| Task | Tokens | What the model was doing |
|---|---|---|
| Story 2, finishing the composition (one sub-agent) | ≈ 160 k | reading the brief, the note, the template, Story 1's sources; writing about 700 lines of JS and 500 of Python; looking at stills |
| Story 2, phone-size rework (one sub-agent) | ≈ 129 k | re-reading the same sources; moving text by hand; looking at stills again |
| Template library (one sub-agent) | stopped by the session limit | reading three renderers; writing 23 cards and snippets |
| Hazel's own session | large, not measured | reading 35 kB renderers, writing patch scripts, reading about 20 full-size contact sheets |

The rendering itself, frames and music, already runs on the CPU and costs nothing. The tokens go to five things:

1. **Writing scene code by hand.** Every episode re-writes 600–800 lines of canvas JS and a 500-line score. Output tokens are the most expensive kind.
2. **Re-reading the same context.** Every sub-agent starts cold. It reads the series template, the notes, Story 1's `index.html` and `score.py`: about 30–40 k tokens before it writes a line.
3. **Looking at images.** A 1920 × 1080 contact sheet costs about 2–3 k tokens to look at. We look at 4–6 per render, and render 2–3 times per episode.
4. **Placing things by trial.** Move a line by 40 px, capture a still, look, move again. Each round is reading code plus an image.
5. **Hand-kept tables that drift:** the reading audit's `SCREENS`, the fact table in `NOTES.md`, the stills times in `build.sh`. Each change has to be repeated in three places by hand.

## 2. The idea: the model writes a script, the CPU builds the video

An episode becomes **one short data file** that the model writes, of about 100–150 lines. A **generator**, plain code that runs on the CPU, turns it into everything else.

```yaml
episode: story3-text-to-shell
title: "NO SHELL FOR YOU"
subtitle: ["Why a tiny model", "cannot write a command."]
hero: { template: T04, sprite: mike, name: MIKE, quest: ["Turn a sentence", "into a command."] }
scenes:
  - { template: T05+T06, bars: 4, title: "TOO SMALL TO GUESS",
      key: "350M PARAMETERS", key_source: docs/05 §2,
      fail: "rm -rf ~/ ?", works: "ls ~/Music", mood: tense }
  - { template: T11, bars: 6, boss: "THE GAME BOY DETOUR", phases: [...] }
  - { template: NEW-T24, bars: 4, ... }      # the one new template of the episode
lesson: ["A RULE BEATS", "A MODEL."]
```

The generator does the rest:

| Built by the CPU | Today done by the model |
|---|---|
| The timeline: scene start times on bar lines, from `bars` | computed by hand in JS |
| The picture: each template is a **parametric JS function** from a shared `common/` runtime (`stampSlam({text, t0, color})`, `bossFight({...})`) | 600–800 lines re-written per episode |
| The score: each template has a **music cue** (stage start, hits, CLEAR! jingle, boss ostinato) placed at the scene's event times; `mood` picks the chords | a 500-line score re-written |
| The reading audit: computed from the text slots and their times | the `SCREENS` table kept by hand |
| **A layout check, in text:** the generator measures every text box in the canvas (`measureText`) and reports overflow, overlaps, the CLEAR! zone, the 5 % margins, and glyph heights against the phone rule | the model looks at images to find these |
| `NOTES.md`: the structure table and the fact table, from `key_source:` fields | written by hand, and drifted |
| A **low-resolution preview** (640 × 360, 10 fps) and **one small contact sheet** of 12 thumbnails | full renders and full-size sheets |

The model's work becomes three things: the story, the script, and the one new template per episode. It reads a **text report** (the lint and the audit), and looks at **one small contact sheet** at the end.

## 3. Other savings, independent of the generator

- **Shared runtime, not copies:** a single `worklines/hazel/video/common/`, holding the renderer head, `nes.py`, `capture.py`, the templates and the cues. A sub-agent reads the template **index** (the library README, about 2 k tokens), not three renderers.
- **Short briefs, fixed reading list:** the brief, the owner's note, the library index and the script schema. Nothing else, unless something is missing.
- **The right model for the task:** Opus for the story and the script; a cheaper model (Sonnet, Haiku) for mechanical tasks such as filling a card, fixing a lint error or re-running a build. The Agent tool takes a `model` parameter.
- **Small images:** contact sheets at 960 px wide, about 4 times fewer image tokens. Full-size stills only for one disputed frame.
- **Short sessions:** one fresh session or sub-agent per episode, with a handoff note, rather than one long conversation. A long context is re-read at every turn.

## 4. What it would cost to build, and the expected gain

- **Building it** is a one-time investment: the `common/` runtime, the 23 templates turned into parametric functions with cues, the script parser and the lint. It is about one sub-agent run of the size of Story 2 (about 150 k tokens). That run can be split into small steps with a cheaper model.
- **Expected gain, not yet measured:** an episode built from a script should cost a fraction of today's 160 + 129 k. The model writes about 150 lines of YAML and one new template, and reads a text report and one small sheet. **Measure it** on the next episode: the sub-agent tokens per episode go in the plan.
- **Risk: a pipeline that is too rigid makes every episode look the same,** which is the opposite of the library's goal. Two things guard against it: the one-new-template rule, and template parameters that allow variants.

## 5. Proposed steps (Step 6 of the plan)

1. **6.1** This analysis (done) and the user's choices.
2. **6.2** `video/common/`: one shared runtime extracted from the three videos. The three videos still build, with an identical output checked by a frame hash.
3. **6.3** Parametric templates: start with the frame (T01, T04, T05, T21, T22, T23) and the most used body templates (T06, T07, T08, T11, T13). The rest are converted when an episode needs them.
4. **6.4** The script format and the generator: timeline, score cues, reading audit, `NOTES.md` tables.
5. **6.5** The layout lint (text report) and the low-resolution preview with a small contact sheet.
6. **6.6** The next episode made through the pipeline, with its token count recorded and compared to Story 2.
