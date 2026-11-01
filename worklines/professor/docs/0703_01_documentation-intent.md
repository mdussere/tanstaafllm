# Intent — the TANSTAAFLLM documentation (Professor Step 7)

> **Freshness:** ⚪ draft · **Written:** 2026-10-13 · **Checked:** 2026-10-31 · **Step:** professor 7.3 ⏳

**Status:** draft for the user's approval (sub-step 7.3). Nothing is written before `🟩 go Step 7`.
**Date:** 2026-10-11
**Author:** Professor

## 1. The user's choices (7.2, 2026-10-11)

| Option | Choice |
|---|---|
| Audience | The user first, then very capable friends or colleagues the user shows the project to. They care about the architecture, the choices, the models and the reasons for them, not about line-by-line code. |
| Layers | All five: architecture overview, component reference, operations, user guide, decision records. Decision records stay at a high level. |
| Readability | Everything must stay readable by a person. Nobody should need two hours, or need to hand the docs to an AI. |
| Form and place | Markdown in `docs/`. Diagrams in **SVG**, not Mermaid. Each SVG is converted to PNG and inspected visually before it counts as done. |
| Tone | Lightly tinted by *The Moon Is a Harsh Mistress* (the cell, the Loonies, the vocabulary), with our running joke about the cell of agents, and a retro-gaming look, like Luna's wallpaper. The flavour must never hide the technical content. |
| Staying true | No formal tests. When a step is finished, each workline reads the pages about its own software and reports errors. |
| Who writes | Professor writes the first version, so the whole has one voice and one vision. Later corrections may come from the worklines. |
| Order | In stages. First the architecture and the components, then the rest. The full inventory (7.1) is done later, as part of each stage. |

## 2. Reading budget

| Page | Target length | Reading time |
|---|---|---|
| Index ("Welcome to Luna") | 1 screen | 2 min |
| Architecture overview | about 2 pages, plus 2 or 3 diagrams | 10 min |
| One component page | 1 page, plus at most 1 diagram | 3–5 min |
| Operations | 2 pages | 10 min |
| User guide | 1–2 pages, plus the controls cheat sheet | 5 min |
| Decision records | 1 line of decision and 2–4 lines of why, per decision; about 15 decisions | 10 min |

The total is about an hour for everything, and 15 minutes for the index plus the architecture. A reader can stop after any page.

## 3. Structure

*Amended 2026-10-11 at the user's request: no separate `docs/guide/`. The new pages join the existing ones in `docs/` under one numbering, and `docs/README.md` is the way in and the navigation.*

```
docs/
  README.md                  the way in: what Luna is, the cell, reading order for everything
  01_principles.md           (existing) idea, vocabulary, design rules, documentation conventions
  02_testing.md              (existing) test conventions
  03_r36-ultra-bring-up-story.md   (existing)
  04_architecture.md         the big picture
  10_wyoh.md                 desktop: Sway, gamepad daemon, Slate, keyboard, layout, apps, MCP
  11_mycroft.md              voice to text: console, dictation provider, models
  12_mike.md                 local brain: small model, tool contract
  13_mannie.md               frontier model: Claude Code on the device
  14_luna.md                 the R36 Ultra itself, the card, the bring-up
  15_the-cell.md             how the agent cell builds all this
  20_operations.md           set up, deploy, share Luna, reboot rule, troubleshooting
  21_user-guide.md           controls, apps, Slate, dictation
  30_decisions.md            the decisions that shape the system, with their reasons
  LOGBOOK.md                 (existing)
  img/                       SVG diagrams, each with its PNG render
```

### Each component page has the same frame

1. **In one sentence:** what it is for.
2. **Where it lives:** the code, where it is deployed, and who starts it.
3. **How it talks to the others:** interfaces, with one small diagram if useful.
4. **What it costs:** memory, CPU and start time on Luna, measured, with the source.
5. **Why it is like this:** two to four choices and their reasons, linking to `30_decisions.md`.
6. **Status:** live on Luna, or desk/`luna-pi` only, or planned. Known limits.
7. **Sources:** the plan, intents and results it is drawn from.

## 4. Diagrams (SVG)

- **Planned for stage 1:**
  1. **Luna, the whole machine:** hardware (RK3326, 1 GiB, 720×720, gamepad, Wi-Fi), the system (ArchR, Sway), the components, and Mannie reached remotely.
  2. **The path of a request:** a button or voice goes to Mycroft, then the Slate or Mike, then Wyoh, then an app, with escalation to Mannie and the cost shown.
  3. **The 1 GiB budget:** a bar of what is resident, what runs on demand, and what is free. Every figure comes from measured results.
  4. **The cell:** the user, Professor and the worklines, with notes, messages, plans and the Luna token.
- **Visual style (from Luna's wallpaper):**
  - deep-space navy and violet background, moon grey-blue, chrome titles;
  - amber and orange accents, cyan for "live" signals;
  - pixel-art borders and a pixel or monospaced display font for titles, a plain readable font for labels;
  - every label legible at the PNG size used in the page.
- **Method:**
  - hand-written SVG, kept small and editable;
  - rendered to PNG with ImageMagick and inspected (text overflow, overlaps, contrast);
  - fixed, then rendered again;
  - the page shows the SVG, and the PNG is kept beside it for viewers that cannot show SVG.

## 5. Tone

- **Plain technical sentences first.** The literary layer sits in titles, captions and short asides. For example: "Pressure: the 1 GiB budget", "Tunnel: SSH", "Professor runs the cell; nobody talks to anyone else's comrade directly".
- **The vocabulary of `docs/01_principles.md`** (Tunnel, Pressure, Airlock, Seal, Catapult, Rock, Free Fall) is used where it helps, and always explained once.
- **No in-joke without its meaning.** A colleague who has not read Heinlein must still understand every page.
- **Honest status:** "measured on Luna", "measured on `luna-pi` only", "planned", "rejected". No claim without its source.

## 6. Stages

| Stage | Pages | Then |
|---|---|---|
| 1 | Index, architecture, the six component pages, diagrams 1–4 | The user reviews. Each workline checks its own page and sends corrections to Professor through a note. |
| 2 | Operations and the user guide | The same review. |
| 3 | Decision records | The same review, and a final pass over the whole for consistency and reading time. |

## 7. Out of scope

- API reference or code-level docs.
- Rewriting plans or results: the guide summarises them and links to them.
- Formal doc tests (the user's choice).
- Publishing outside the repository. A published page can come later if the user asks.

## 8. Acceptance (7.5)

- Reading the index and the architecture alone, a capable newcomer can explain what Luna is, which parts exist, how a request flows, and where the memory goes.
- Every component page follows the frame, gives its sources, and states its status honestly.
- Every SVG has been rendered to PNG and inspected.
- Each workline has reviewed its page.
- The reading budget is respected.
