# Uses: every scene of every video

Times are seconds of the final cut. The trailer's cut includes its reading holds (`trailer/src/holds.json`), so its renderer's source times are shorter (source 0–60 s). Story 1's renderer plays the scenes after 26 s with their original times + 6 s (`SHIFT`). "Made by" comes from `docs/0501_01_sequence-library-analysis.md` §1.

| Video | Time (s) | Scene function | Template(s) | Variant | Made by |
|---|---|---|---|---|---|
| Trailer | 0–7 | `scene1` | T02 (+ T09 typing) | INSERT COIN; LUNCH struck, LLM stamped | trailer sub-agent; opening revised by Professor |
| Trailer | 7–12 | `scene2` | T03 | key art from big pixels, conspiracy line | trailer sub-agent |
| Trailer | 12–22 | `scene3` | T04, T12, T13 | Luna: six stat rows, MISSION box | trailer sub-agent |
| Trailer | 22–27.5 | `scene4` (part 1) | T08 | three stop-time slams: the price list | trailer sub-agent |
| Trailer | 27.5–32 | `scene4` (part 2) | T09, T13, T08 | `> pong`, ≈17,700 tokens, NO FREE LLM. | trailer sub-agent |
| Trailer | 32–44 | `scene5` | T10, T12 | four intelligences, cheapest first; banner | trailer sub-agent |
| Trailer | 44–57.5 | `scene6` | T11, T13 | 4 GB VS 983 MiB; segmented memory bar | trailer sub-agent |
| Trailer | 57.5–73 | `scene7` | T15, T07 | six tiles, bubbles, five rules stamped | trailer sub-agent |
| Trailer | 73–79 | `scene8` | T17 | THE ADVENTURE BEGINS., the cell on the Moon | Professor (replaced T16, 2026-10-31) |
| Trailer (first cut) | 48–54 (source) | `scene8` @ `7a76cc0` | T16 | six one-second stages | trailer sub-agent; retired |
| Trailer | 79–82.5 | `scene9` (part 1) | T03, T08 | doctrine over the key art | trailer sub-agent |
| Trailer | 82.5–86.5 | `scene9` (part 2) | T23 | the original end card | trailer sub-agent |
| Story 1 | 0–5 | `sTitle` | T01 | HELLO, LUNA; subtitle VT 52 | S1 sub-agent |
| Story 1 | 5–12 | `sPlayer` | T04, T12 | R36 Ultra, three stat rows | S1 sub-agent |
| Story 1 | 12–20 | `s1` | T05, T07, T13, T14 | secure the card: 48.8 GiB → safe on disk, checks | S1 sub-agent; rewritten by Hazel 2026-10-31 |
| Story 1 | 20–26 | `sChoose` | T05, T06, T07, T08 | another system (SET ASIDE) vs ArchR; WE CHOOSE ArchR. | Hazel, 2026-10-31 |
| Story 1 | 26–34 | `s2` | T05, T12, T08 | black screen "?", then the screen comes alive | S1 sub-agent |
| Story 1 | 34–40 | `s3` | T05, T06 | hub ✗ / adapter ✓ | S1 sub-agent |
| Story 1 | 40–48 | `s4` | T05, T12, T09 | CTRL ALT F2, TEXT MODE, QWERTY → AZERTY | S1 sub-agent |
| Story 1 | 48–66 | `s5` | T05, T11, T09, T06, T08 | Wi-Fi chip: interfaces, pin 2, three patches | S1 sub-agent |
| Story 1 | 66–74 | `s6` | T05, T09, T08 | router error typed; AUTO struck, 11 stamped | S1 sub-agent |
| Story 1 | 74–82 | `s7` | T05, T09, T14, T12, T21 | `$ ssh luna`, signal to Luna, HELLO, LUNA. | S1 sub-agent |
| Story 1 | 82–88 | `sResult` | T22 | eight pips; lesson at P 40 | S1 sub-agent |
| Story 1 | 88–94 | `sEnd` | T23 | the trailer's end card | S1 sub-agent |
| Story 2 | 0–6 | `sTitle` | T01 | ASK THE DESKTOP; subtitle VT 90 | S2 sub-agents |
| Story 2 | 6–14 | `sPlayer` | T04 | Wyoh's face, quest VT 90, no stat rows | S2 sub-agents |
| Story 2 | 14–20 | `s1` | T05, T18 | screenshot trap: pixelated desktop, three paid guesses | S2 sub-agents |
| Story 2 | 20–28 | `s2` | T05, T06, T08 | HIOM, windows spill, REOPENED; lesson stamp | S2 sub-agents |
| Story 2 | 28–36 | `s3` | T05, T13 | unmodified Sway, four IPC tiles on luna-pi | S2 sub-agents |
| Story 2 | 36–44 | `s4` | T05, T14, T08 | agent ↔ Sway over MCP; 26 TOOLS | S2 sub-agents |
| Story 2 | 44–48.5 | `s5` (phase a) | T05, T11, T12, T08 | the real panel black; BLACK. | S2 sub-agents |
| Story 2 | 48.5–52 | `s5` (phase b) | T11, T12 | GPU driver loaded, panel lit, 1 passed | S2 sub-agents |
| Story 2 | 52–57.5 | `s6` (phase a) | T05, T12 | FN+button chips, the Slate (L1) | S2 sub-agents |
| Story 2 | 57.5–62 | `s6` (phase b) | T14, T12 | the agent presses FN+B; Mike answers in 13 s | S2 sub-agents |
| Story 2 | 62–72 | `s7` | T05, T19, T07, T08 | seven layers; only the last proves the fix | S2 sub-agents |
| Story 2 | 72–78 | `sPayoff` | T20, T09, T21 | `sway_get_tree`, the tree, ASK THE DESKTOP. | S2 sub-agents |
| Story 2 | 78–84 | `sResult` | T22 | seven pips; lesson at P 64 | S2 sub-agents |
| Story 2 | 84–90 | `sEnd` | T23 | motto VT 64, PRESS START P 40 | S2 sub-agents |

Note: the analysis counts 13 scenes in Story 1; its renderer has 12 scene functions (the boss's three phases live in one function). Story 2's NOTES table has 13 rows (stage 6 in two); here the boss's two phases are split too.
