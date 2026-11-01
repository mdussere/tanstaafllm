# T03 Key-art reveal

| Field | Value |
|---|---|
| Family | reveal |
| Energy | build (the drop) |
| Length | 2 bars (4 s), 5 s with hold; doctrine 1.5 bars |
| First used | Trailer, trailer sub-agent, 2026-10-25 |
| Used in | Trailer 7–12 s (open) and 79–82.5 s (doctrine), output times |
| Status | optional (unused in the stories) |

## Concept
The project's key art resolves from big pixels to full detail as the music drops. It is the "world" shot: the cast and the Moon, before any detail. Over a darkened key art, it also carries the doctrine lines.

## When to use / not
- Use: after a cold open; before a manifesto or a doctrine; a season opener.
- Not: as a background behind data. Not more than twice per video.

## Dynamics
- Cut on the downbeat with a white flash (0.35 s fade).
- 0–0.7 s: block size 64 → 1 px (quadratic), the art pans slowly (`srcY` 20 → 75).
- Beats 2, 3, 5: three text lines fade in. Last 0.25 s: block dissolve.
- Doctrine variant: art at 62 % black; three lines slam one every 0.75 s (see T08).

## Graphic elements
`artCover(srcY, zoom, block)`, a bottom gradient to `C.ink`, `dissolve`. Tokens: `C.chrome`, `C.amber` for the key phrase, `C.cyan` for the aside.

## Text slots (phone rule)
- Key: one manifesto line, PS2P ≥ 56 or VT323 ≥ 90 (the trailer used P 32: too small).
- Secondary: the aside, VT323 64 (trailer: 44).
- Doctrine: three lines at P 64 each; count as one key message in three beats.

## Music cue
`liftoff()`: the drop, `crash` + kick, the trailer THEME at full voice over Am F G, `bass8`, `hats`; a fill and `tri_drop` into the next scene. Doctrine: three `hit_all` stabs in `finale()`.

## Variants seen
- Trailer open: the conspiracy line. ![](still-trailer-009.80.jpg)
- Trailer doctrine: NO FREE LLMS / NO INVISIBLE MASTERS / NO SURRENDER TO THE DESKTOP. ![](still-trailer-080.80.jpg)

## Code
- `snippet.js` from `trailer/src/index.html`, `scene2` lines 301–313 and `scene9` 608–621; commit `3039e69`.
- Helper `artCover` lines 174–184 of the shared head. Score: `liftoff()` lines 242–263.
