# Sequence template library

A box of sequence templates for the series' pixel-art videos, like a slide-template box. It has two jobs (user, 2026-11-01):

- **Unity:** each video reuses known sequences, so the series looks like one game.
- **Variety:** each video adds at least one new template or a clearly new variant, so episodes stop copying each other.

The analysis behind it: [`../../docs/0501_01_sequence-library-analysis.md`](../../docs/0501_01_sequence-library-analysis.md). The series rules: [`../../docs/0103_01_series-template.md`](../../docs/0103_01_series-template.md). Every scene of every video, with its templates: [`uses.md`](uses.md).

## Index

Uses = number of scenes using the template (trailer / Story 1 / Story 2). Family: frame, stage, reveal, data, transition. Energy: calm, build, hit.

| Id | Name | Family | Energy | Trailer | S1 | S2 | Status | Card |
|---|---|---|---|---|---|---|---|---|
| T01 | Series title card | frame | build | (T02) | 1 | 1 | core | [T01](T01-series-title-card/template.md) |
| T02 | Insert coin | reveal | calm → hit | 1 | – | – | optional | [T02](T02-insert-coin/template.md) |
| T03 | Key-art reveal | reveal | build | 2 | – | – | optional | [T03](T03-key-art-reveal/template.md) |
| T04 | Player card | reveal | build | 1 | 1 | 1 | core | [T04](T04-player-card/template.md) |
| T05 | Stage frame | frame | build | – | 8 | 7 | core, capped | [T05](T05-stage-frame/template.md) |
| T06 | Two boxes: fails / works | stage | build | – | 3 | 1 | optional | [T06](T06-two-boxes/template.md) |
| T07 | Checklist on the beat | stage | calm | (1) | 2 | 1 | optional | [T07](T07-checklist-on-the-beat/template.md) |
| T08 | Stamp slam | stage | hit | 3 | 6 | 5 | core | [T08](T08-stamp-slam/template.md) |
| T09 | Terminal typing | data | calm | 1 | 3 | 1 | optional | [T09](T09-terminal-typing/template.md) |
| T10 | Character select | data | build | 1 | (echo) | – | optional | [T10](T10-character-select/template.md) |
| T11 | Boss fight | stage | hit | 1 | 1 | 1 | core | [T11](T11-boss-fight/template.md) |
| T12 | Handheld with screen states | data | calm | 2 | 4 | 2 | core | [T12](T12-handheld-screen-states/template.md) |
| T13 | Metric tiles / gauge | data | build | 2 | 1 | 1 | optional | [T13](T13-metric-tiles/template.md) |
| T14 | Flow / pipe | data | build | – | 2 | 2 | optional | [T14](T14-flow-pipe/template.md) |
| T15 | Roster | reveal | build | 1 | – | – | optional | [T15](T15-roster/template.md) |
| T16 | Speedrun | transition | hit | 1 (first cut) | – | – | retired | [T16](T16-speedrun/template.md) |
| T17 | Opening / to be continued | transition | build | 1 | – | – | optional | [T17](T17-opening/template.md) |
| T18 | Pixel-grid guess | reveal | calm | – | – | 1 | optional | [T18](T18-pixel-grid-guess/template.md) |
| T19 | Layer stack | data | build | – | – | 1 | optional | [T19](T19-layer-stack/template.md) |
| T20 | Tree reveal | reveal | build | – | – | 1 | optional | [T20](T20-tree-reveal/template.md) |
| T21 | Payoff reprise | frame | hit | – | 1 | 1 | core (with a payoff) | [T21](T21-payoff-reprise/template.md) |
| T22 | Result screen | frame | calm | – | 1 | 1 | core | [T22](T22-result-screen/template.md) |
| T23 | End card | frame | calm | 1 | 1 | 1 | core | [T23](T23-end-card/template.md) |

**Shared by every scene** (not templates): the sound effects (coin, blip, buzz, ding, CLEAR! jingle, level-clear fanfare), the white flash on a cut, the 60-px block dissolve, the scanlines and vignette (`POST`), the hard drop shadow, the `C` palette tokens.

## What each template folder holds

- `template.md`: the card. Header, concept, when to use, dynamics in beats and bars, graphic elements and palette tokens, text slots with phone sizes, music cue, variants seen (with stills), code pointer (file, function, lines, commit).
- `still-<video>-<t>.jpg`: 960-px stills rendered by the video's own code (`t` = seconds of the cut).
- `snippet.js`: the render code cut from the `index.html` that does it best, with its parameters named in a header. It does not run alone: it needs the shared renderer head (lines 32–252 of every `index.html`) and the episode's staging helpers named in the header.
- `cue.py` (most templates): the matching `score.py` code. It calls the score's helpers and `nes.py`.

## Rules for an episode

From §4 of the analysis; to be copied into the series template.

1. The **frame** templates are mandatory: T01, T22 and T23, plus T21 when there is a payoff.
2. The body uses **at least three library templates**, and no single body template fills more than half of the scenes.
3. Each episode brings **at least one new template**, or a clearly new variant. After the user's review, it enters the library with its card.
4. The brief to a sub-agent names the templates to use, their slots and the new one to invent. The sub-agent picks from this menu instead of copying the previous video.

**Phone rule for every text slot** (user, 2026-11-01; `story2-ask-the-desktop/NOTES.md`): per screen ONE key message at ≥ 50 px glyph height (VT323 ≥ 90 or Press Start 2P ≥ 56), at most one secondary at ≥ 35 px (PS2P ≥ 40 or VT323 ≥ 64); everything else is glance text (PS2P 28–32, VT323 48) the story does not depend on, or is cut. Key lines ≤ ~6 words, 2 lines max. The stage HUD keeps P 28 / P 44.

## How to add a template

1. Give it the next free id (`T24`, …) and a short slug: `T24-<slug>/`. Never reuse a retired id.
2. Write `template.md` with the same sections as the other cards, under ~60 lines. Status starts as `optional`.
3. Cut `snippet.js` from the video that does it best: a header naming the parameters and the helpers it needs, then the source lines with their path and line range. Add `cue.py` if the music cue is specific.
4. Take 1–2 stills from the render code (`src/capture.py stills <dir> <t…>`; the trailer's times include its holds), resize to 960 px wide, JPEG quality ~80.
5. Add a row to the index above and the scenes to `uses.md`. Add one line to the card's "Variants seen" each time a video reuses it.
6. Change a status (core / optional / retired) only after the user's review, and write the date and reason in the card.
