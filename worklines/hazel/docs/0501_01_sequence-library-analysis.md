# Sequence templates in the first three videos, and a library to keep them

> **Freshness:** ⚪ draft · **Written:** 2026-11-01 · **Checked:** 2026-11-01 · **Step:** hazel 5.1

**Question:** which sequence templates do the trailer, Story 1 and Story 2 use, how often, and who made them? And how should a library of these templates be organised?

**Why (user, 2026-11-01):** the composing sub-agents copy whatever the previous video did, so Story 2 reads like Story 1. A library of sequence templates, like a slide-template box, should do two things. It should keep the series unified, since each video reuses known sequences. It should also make change deliberate: each video brings at least one new sequence.

## 1. The three videos

| Video | Length | Scenes | Made by |
|---|---|---|---|
| Trailer | 86.5 s | 11 | A sub-agent briefed by Professor (2026-10-25). Professor revised the timing (reading holds), the score (version A) and the opening. |
| Story 1 "Hello, Luna" | 94 s | 13 | A sub-agent briefed by Professor (2026-10-31). Hazel revised it the same day: stage 1 rewritten, "Choose a system" added. |
| Story 2 "Ask the desktop" | 90 s | 13 | Two sub-agents briefed by Hazel (2026-11-01). The first stopped during the token pause. A third sub-agent is reworking the text sizes. |

## 2. The templates found

The count is the number of scenes that use the template. ⭐ marks a template used only once.

| # | Template | What it does (effect) | Trailer | S1 | S2 | First by |
|---|---|---|---|---|---|---|
| T01 | **Series title card** | A black starfield and a rising moon. An amber "TANSTAAFLLM · STORY n", then a large chrome stamp with the title, then a cyan subtitle and a blinking PRESS START. It announces the episode and its promise. | (variant: INSERT COIN) | 1 | 1 | S1 sub-agent |
| T02 | **Insert coin** | A coin drops, a sentence is typed, a word is struck out and corrected by a stamp. The joke of the title, told in one gesture. | 1 ⭐ | – | – | trailer sub-agent |
| T03 | **Key-art reveal** | The key art resolves from big pixels to full detail as the music drops. It is the "world" shot. | 2 (open, doctrine) | – | – | trailer sub-agent |
| T04 | **Player card** | A sprite or a key-art face, a name, 2–3 stat rows on blips, and a QUEST box. It introduces the hero of the episode. | 1 (Luna) | 1 (R36 Ultra) | 1 (Wyoh) | trailer sub-agent |
| T05 | **Stage frame** | "STAGE n" + title, pips at the top right, and a green CLEAR! stamp on a jingle at the end. It is a container, not content. | – | 8 | 7 | S1 sub-agent |
| T06 | **Two boxes: fails / works** | A red ✗ box against a green ✓ box, appearing one after the other. Before and after, or the wrong choice and the right one. | – | 3 (copy #1/#2 first cut, hub/adapter, other system/ArchR) | 1 (HIOM reopened, partial) | S1 sub-agent |
| T07 | **Checklist on the beat** | Lines with ✓ appear one per beat, with rising blips. Shows a procedure that holds. | (cell rules, as stamps) | 2 (card copy, ArchR) | 1 (seven layers, ticks) | S1 sub-agent |
| T08 | **Stamp slam** | One to three big words slam in on music hits, with a shake and a flash. It is the punchline of a screen. | 3 (price list, NO FREE LLM, doctrine) | 6 (SET ASIDE, WE CHOOSE, BLACK SCREEN ALIVE, AUTO→11, HELLO LUNA…) | 5 (REOPENED, 26 TOOLS, BLACK., lesson, payoff) | trailer sub-agent |
| T09 | **Terminal typing** | Text typed in a terminal box with a cursor, sometimes a counter rolling. Shows real commands and real messages. | 1 (`> pong`, ≈17,700 tokens) | 3 (terminal, router error, `ssh luna`) | 1 (`sway_get_tree`) | trailer sub-agent |
| T10 | **Character select** | Cards in a row, cheapest first, each with a price meter, and a cursor that walks across them. Compares options. | 1 ⭐ | (S1 "choose" is a two-card echo) | – | trailer sub-agent |
| T11 | **Boss fight** | A red title, a phase change (HP bar breaking, a flash), and a victory in A major. The hardest problem of the story. | 1 (1-GiB wall) | 1 (Wi-Fi chip, 3 hits) | 1 (black panel) | trailer sub-agent |
| T12 | **Handheld with screen states** | The pixel handheld whose screen goes black, "?", moon, prompt or Sway. Shows the device's state. | 2 | 4 | 2 | trailer sub-agent |
| T13 | **Metric tiles / gauge** | Numbers in tiles, each labelled with its machine, or a segmented memory bar. Measured facts made visible. | 2 (stats, memory bar) | 1 (48.8 GiB / 42 GB) | 1 (four IPC tiles) | trailer sub-agent |
| T14 | **Flow / pipe** | A → link → B with packets travelling, such as the PC to Luna, the card to the disk, the agent to Sway, or FN+B to Mike. Shows who talks to whom. | – | 2 | 2 | S1 sub-agent |
| T15 | **Roster** | Six agent tiles with faces and jobs, then rules stamped one per second. The cell as a team. | 1 ⭐ | – | – | trailer sub-agent |
| T16 | **Speedrun** | Six one-second stages, with a small handheld hopping along. A whole story in six beats. | 1 ⭐ (first cut, later replaced) | – | – | trailer sub-agent |
| T17 | **Opening / to be continued** | "THE CELL IS READY. THE ADVENTURE BEGINS." A promise of the next episodes. | 1 ⭐ | – | – | Professor |
| T18 | **Pixel-grid guess** | A desktop turned into big blocks, a squinting robot, and guess bubbles that each cost a coin. Shows the problem as it looks from the outside. | – | – | 1 ⭐ | S2 sub-agent |
| T19 | **Layer stack** | Numbered rows from cause to effect, ticked in turn. One row fails, and the stage ends on the lesson. | – | – | 1 ⭐ | S2 sub-agent |
| T20 | **Tree reveal** | A query, then a structured tree that grows line by line. The data the agent gets instead of pixels. | – | – | 1 ⭐ | S2 sub-agent |
| T21 | **Payoff reprise** | The title stamp returns on a dark band, with the trailer theme at full voice. It closes the loop of the episode. | – | 1 | 1 | S1 sub-agent |
| T22 | **Result screen** | "STORY n CLEAR", the stage pips filling up, and the lesson in two sizes. The takeaway. | – | 1 | 1 | S1 sub-agent |
| T23 | **End card** | The chrome logo from the key art, the motto, the URL, the byline, PRESS START, and a fade. The signature. | 1 | 1 | 1 | trailer sub-agent |

**Shared by every scene:** the sound effects (coin, blip, buzz, ding, CLEAR! jingle, level-clear fanfare), the white flash on a cut, the 60-px block dissolve, the scanlines and vignette, and the hard drop shadow.

## 3. What the count shows

- **The stories repeat one recipe.** In S1 and S2, 15 of 26 scenes are the **stage frame** (T05) filled with a **stamp** (T08) and a **checklist or two boxes** (T06, T07). That is why S2 reads like S1: the same frame, the same rhythm, and a CLEAR! every 6–8 s.
- **The trailer was the most varied.** It has 11 scenes and 8 different templates, 5 of them used only there: insert coin, key-art reveal, character select, roster, speedrun. None of them has come back.
- **S2 did invent something:** the pixel-grid guess, the layer stack and the tree reveal (T18–T20). But these new pieces sit inside the same stage frame, so they don't change the feel.
- **The frame (T01, T21, T22, T23) is right to repeat.** It is the series' signature.
- **Text size is not a property of any template yet.** Every template carries small VT323 sentences. The phone rule of 2026-11-01 (one key message per screen at about 50 px glyph height) should become a slot rule in each template.

## 4. Proposed structure for the library

A plain-file library, in Git, beside the videos:

```
worklines/hazel/video/library/
  README.md                 the index: one row per template, plus the rules for using the library
  uses.md                   one row per scene of every video: video, time, template, variant, who made it
  T08-stamp-slam/
    template.md             the template's card (below)
    still-<video>-<t>.jpg   one still per notable use (≤ 960 px wide, a few dozen KB)
    snippet.js              the render code, cut out of the video's index.html, with its parameters named
    cue.py                  the matching score helper calls (optional)
  T11-boss-fight/
  …
```

**`template.md`**, one card per template:

- **Header:** id, name, family (frame / stage / reveal / data / transition), energy (calm / build / hit), length in bars, first used (video, author, date), used in (videos and times), status (core / optional / retired).
- **Concept:** what the sequence says, and the effect on the viewer, in two or three sentences.
- **When to use it, and when not to.**
- **Dynamics:** the beat plan. For example: "bar 1: title slides in; beat 3: first element on a blip; bar 3: stamp on the hit; last beat: CLEAR!".
- **Graphic elements:** sprites, boxes, palette tokens, and transitions in and out.
- **Text slots, with their sizes under the phone rule:** the key message (≥ 50 px glyph height), one secondary (≥ 35 px), glance labels.
- **Music cue:** the chord or tension, the hits, the sound effects, and the score helpers to call.
- **Variants seen:** one line per use, with a still. This gives the "template with variations".
- **Code:** `snippet.js` plus a link to the source function and the commit it came from.

**Rules for an episode**, to go into the series template:

1. The **frame** templates are mandatory: T01, T22 and T23, plus T21 when there is a payoff.
2. The body uses **at least three library templates**, and no single body template fills more than half of the scenes.
3. Each episode brings **at least one new template**, or a clearly new variant. After the user's review, it enters the library with its card.
4. The brief to a sub-agent names the templates to use, their slots and the new one to invent. Then the sub-agent picks from a menu instead of copying the previous video.

## 5. What happens after we agree

1. Build `library/`. For each of the 23 templates: cut the snippet out of the video that does it best, write the card, and take one or two stills from the existing renders (stills from the render code, not screenshots of a screen).
2. Fill `uses.md` for the three videos.
3. Add the episode rules and the phone text slots to the series template.
4. Use the library for the next brief.
