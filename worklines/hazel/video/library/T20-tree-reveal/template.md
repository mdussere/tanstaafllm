# T20 Tree reveal

| Field | Value |
|---|---|
| Family | reveal |
| Energy | build |
| Length | 1 bar inside the payoff |
| First used | Story 2, S2 sub-agent, 2026-11-01 |
| Used in | Story 2 payoff, 72–74 s |
| Status | optional |

## Concept
A query goes out, and a structured tree grows back line by line. It shows the data an agent gets instead of pixels: names and structure, not an image.

## When to use / not
- Use: any structured answer (a tree, a list of windows, a config) worth showing as structure.
- Not: for raw logs or long JSON. Five nodes at most.

## Dynamics
- 0.3 s: the query label (code style) and a packet travel out (0.5 s).
- 0.9 s: the first node; then one node every 0.12 s, each on a rising blip.
- 1.5 s (beat 4): the payoff stamp lands over it (T21).

## Graphic elements
Node chips (`C.violet` for containers, `C.navy2` for leaves), connectors in `C.dim` (vertical 6 px + horizontal 40 px), indent 80 px per depth. `agent(..., 'ask')`, `packet`, `grid` floor. Tokens: `C.cyan` query, `C.green` leaves.

## Text slots (phone rule)
- The tree is glance text (P 28): the key message is the stamp that follows (T21).
- Keep labels short (≤ 15 chars) and real (`window: foot`).

## Music cue
`blip(P2, t, 72, 12, 9, 1, slide=12)` for the query, then one `blip(P1, ...)` per node rising (76, 79, 81, 83, 88). See `cue.py` (shared with T21).

## Variants seen
- Story 2: `sway_get_tree` → root / output DSI-1 / workspace 1 / window: foot / window: mike. ![](still-story2-074.50.jpg)

## Code
- `snippet.js` from Story 2 `index.html`, `TREE` and the first part of `sPayoff`, lines 671–688; commit `1d8f355`.
- Score: Story 2 `payoff()` lines 470–482, commit `1c08176`.
