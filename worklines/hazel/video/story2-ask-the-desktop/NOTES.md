# Ask the desktop — TANSTAAFLLM story 2 (Wyoh)

90.0 s, 1920×1080, 30 fps, H.264 + AAC 48 kHz. Built on Story 1's renderer head, pipeline and NES-chip score (`nes.py`, `capture.py`, `contact.py`, palette, fonts, title and end-card frame unchanged). A first composer rewrote `index.html` and `score.py` and stopped before checking them; a second sub-agent finished them, wrote `timing.py`, `build.sh` and these notes, and rendered the cut on 2026-11-01.

Brief: `worklines/hazel/docs/0302_01_wyoh-story-brief.md`. Fact authority: `worklines/hazel/docs/0302_02_note-from-wyoh-story.md` (called "the note" below).

## Concept

Wyoh wanted, from the start, to let agents work the desktop natively: take hold of it, act, and get feedback, without guessing from pixels. The episode plays that as seven stages: the screenshot trap, a first idea that was too narrow (HIOM), the turning point (ask the unmodified Sway over its own IPC), the MCP bridge for agents, a boss on the real panel (black, then lit), the 17 buttons that both the human and the agent press, and the seven-layer trap that teaches "only the last layer proves the fix". The payoff: a drawn agent calls `sway_get_tree`, a drawn window tree comes back, and the title stamp "ASK THE DESKTOP." lands on the trailer theme.

## Structure (seconds of the cut; no reading holds were needed)

| Time | Picture | Music |
|---|---|---|
| 0–6 | Title: starfield, moon; "TANSTAAFLLM · STORY 2", stamp "ASK THE DESKTOP", cyan subtitle, PRESS START | Coin, stamp, trailer theme over Am F G E |
| 6–14 | Player 2: Wyoh's key-art face, "THE DESKTOP LAYER OF LUNA", two stat rows, the quest sentence | Groove Am F C G, new Wyoh motif (E A B C rising) |
| 14–20 | Stage 1, the screenshot trap: a drawn desktop pixelated into blocks, a squinting robot, three guesses each costing a coin; "ON PAPER: A DOM FOR THE DESKTOP." | Am Dm E, coin + falling blip per guess, ding |
| 20–28 | Stage 2, HIOM: one scene with A/B/X actions, windows spill out, "REOPENED"; kept lesson stamp "WAIT FOR A NAMED CONDITION, NEVER A FIXED DELAY." | F G, rising blips, buzz + drop, stamp at 23.5 |
| 28–36 | Stage 3: unmodified Sway, IPC socket, four tiles 42 ms / 0.6 ms / ~20 MiB / 7.5 ms, each labelled luna-pi | Bright C G Am F, Wyoh head, four rising blips |
| 36–44 | Stage 4: robot — "MCP OVER SSH" pipe ("DEVELOPMENT ONLY") — Sway; query, tree back, act, confirming event; stamp "26 TOOLS"; structured-output aside | Am F C G, four sliding blips, stamp at 40 |
| 44–52 | Stage 5, boss: the handheld's panel black, "BLACK.", "Sway's own screenshots looked right.", "MALI GPU DRIVER: NOT LOADED" → LOADED, the panel lights, "1 passed" | E phrygian ostinato, boom, two hits, A-major victory at 48.5 |
| 52–57.5 | Stage 6a: FN+button chips (focus, full screen, close, workspace), "BUTTONS ONLY, ON LUNA, 2026-10-07", the Slate opened with L1 | Am F G, key clicks |
| 57.5–62 | Stage 6b: "THE AGENT PRESSES THE SAME BUTTONS" through a virtual gamepad; in the Slate, FN + B → Mike's window; "MIKE ANSWERS IN 13 s", "6.6 s if Mike is already open." | Stamp, C G Am, Wyoh head, ding |
| 62–72 | Stage 7: seven layer rows; layers 1–4 tick, "FIX "VERIFIED"", layer 7 crossed "THE GAME DID NOT MOVE.", then 5–7 tick in turn; "ONLY THE LAST ONE PROVES THE FIX." | Checks, ding, buzz, Dsus4 stop-time, Dm E, stamp |
| 72–78 | Payoff: robot calls `sway_get_tree`, a window tree (root / output DSI-1 / workspace 1 / window: foot / window: mike) comes back, stamp "ASK THE DESKTOP.", "Screenshots stay, as evidence for humans." | Trailer theme at full voice on the stamp (73.5) |
| 78–84 | "STORY 2 CLEAR", seven pips, "DON'T LOOK AT THE DESKTOP, ASK IT.", "The compositor already knows what a screenshot can only guess." | Level-clear fanfare, seven pip blips, quiet Wyoh head |
| 84–90 | End card, the trailer's, unchanged, fade over the last 0.5 s | Trailer cadence, A-minor chord fading in 4-bit steps |

Cuts fall on 2 s bars (6, 14, 20, 28, 36, 44, 52, 62, 72, 78, 84). The in-stage flash at 57.5 (stage 6, phase b) is on a beat, not a bar: it is not a scene cut.

## Phone readability, 2026-11-01

The user watches on a phone held upright: the 1920-px frame spans the phone's width. Rule (user, measured): per screen ONE key message at ≥ 50 px glyph height (VT323 ≥ 90 px or Press Start 2P ≥ 56 px), at most one secondary at ≥ 35 px (PS2P ≥ 40 or VT323 ≥ 64), everything else small glance text the story does not depend on, or cut. Key lines ≤ ~6 words, 2 lines max. Timeline, music and score unchanged (no event time moved; the boss gains an in-stage phase change on its existing 48.5 flash).

| Screen | Key message (size) | Secondary (size) | Small glance text kept | Cut |
|---|---|---|---|---|
| Title 0–6 | stamp ASK THE DESKTOP (P 100); subtitle V 90, two lines (approved, unchanged) | PRESS START (P 40) | TANSTAAFLLM · STORY 2 (P 36) | — |
| Player 6–14 | "Observe and operate / the desktop without pixels." (V 90) | THE DESKTOP LAYER / OF LUNA (P 40) | PLAYER 2, QUEST: | stat rows (ENGINE, MACHINE); long quest quote shortened |
| Stage 1, 14–20 | "An agent guesses from pixels / and pays for every image." (V 90) | ON PAPER: A DESKTOP DOM. (P 40) | three guess bubbles | "on a small handheld" |
| Stage 2, 20–28 | WAIT FOR A NAMED CONDITION, / NEVER A FIXED DELAY. (P 56) | REOPENED (P 48) | FIRST IDEA: ONE SCENE, A DESKTOP DID NOT FIT., HIOM, KEPT FROM IT: | the two VT sentences |
| Stage 3, 28–36 | "Don't build a compositor. / Ask the one that exists." (V 90) | the four figures (P 40), each tagged luna-pi | captions, SWAY / UNMODIFIED / NO FORK, MEASURED ON luna-pi, A RASPBERRY PI | "headless Sway 1.10.1, 2026-09-26" |
| Stage 4, 36–44 | "Query the tree, act, / wait for the event." (V 90) | 26 TOOLS (P 48) | MCP OVER SSH, DEVELOPMENT ONLY, luna-pi, THEN LUNA | numbered step list; the structured-output aside |
| Boss a, 44–48.5 | BLACK. (P 64) | "Sway's own screenshots / looked right." (V 64) | LUNA'S REAL 720 × 720 PANEL, MALI GPU DRIVER: NOT LOADED | "The same agent session…", "Sway was rendering in software." |
| Boss b, 48.5–52 | GPU DRIVER / LOADED. (P 56) | 1 passed (V 64) | panel tag | — |
| Stage 6a, 52–57.5 | "Buttons drive the desktop." (V 90) | THE SLATE TAKES / THE TEXT. (P 40) | button chips, BUTTONS ONLY, ON LUNA, 2026-10-07, L1 OPENS IT | "A daemon turns…", "A floating text zone…" |
| Stage 6b, 57.5–62 | A DEV AGENT PRESSES / THE SAME BUTTONS (P 56) | MIKE STARTS, / ANSWERS IN 13 s (P 40), set apart below the keycaps | VIA A VIRTUAL GAMEPAD, NOT PIXELS, ON LUNA, IN THE SLATE: | "6.6 s if Mike is already open." |
| Stage 7, 62–72 | ONLY THE LAST LAYER / PROVES THE FIX. (P 56) | FIX "VERIFIED". THE GAME DID / NOT MOVE. (P 40) | LUNA, 2026-10-30: A GAME'S BUTTONS DIED., layer rows | "on the new system root", "THE CODES WERE RIGHT.", "Check each layer, in turn." |
| Payoff 72–78 | stamp ASK THE DESKTOP. (P 96) | "Screenshots stay, as evidence for humans." (V 64) | sway_get_tree, tree nodes | — |
| Result 78–84 | DON'T LOOK AT THE DESKTOP, / ASK IT. (P 64; largest after the STORY 2 CLEAR stamp, P 72) | "The compositor already knows / what a screenshot can only guess." (V 64, two lines) | — | — |
| End 84–90 | logo | motto (V 64), PRESS START (P 40) | github URL (P 36), byline (V 48) | — |

Deviations to review: the HUD stage titles stay at P 44 (series look), so a stage screen shows one more ≥ 35 px line; WYOH (P 80) is a one-word name tag beside the key message; the stage-3 secondary is a group of four figures. The facts table above predates this pass; the cut lines are no longer on screen.

Render: `results/hazel/story2-ask-the-desktop/20261101T124410/` — 90.0 s, holds +0.0 s, −15.3 LUFS, true peak −1.1 dBFS; contact sheets inspected (no overflow, nothing on the CLEAR! stamp).

## Every on-screen fact and its source

Updated 2026-11-01 for the phone-readable cut: rows describe what is on screen now; lines cut in that rework are gone from the table.

All paths are in the repository. "Note" = `worklines/hazel/docs/0302_02_note-from-wyoh-story.md`.

| On screen | Source | Machine shown |
|---|---|---|
| Quest: "Observe and operate the desktop without pixels." (shortened from the goal sentence) | Note beat 1; `worklines/wyoh/docs/0000_04_desktop-automation-model.md` | none (design) |
| "An agent guesses from pixels and pays for every image." | Note beat 1 (no cost figure shown, as the brief asks) | — |
| "ON PAPER: A DESKTOP DOM." | Note beat 1 (the DWOM idea); shown as a design only (must-not-say) | none (design) |
| HIOM: first idea, one scene; a desktop did not fit; REOPENED | Note beat 2; `0101_01_hiom_v0_contract.md` (status note 2026-09-25) | none |
| "WAIT FOR A NAMED CONDITION, NEVER A FIXED DELAY." | Note beat 2 ("waits for a named predicate … never a fixed delay") | none |
| "Don't build a compositor. Ask the one that exists." UNMODIFIED, NO FORK, IPC | Note beat 3 | — |
| 42 ms socket ready, 0.6 ms focus event, ~20 MiB, killed → back in 7.5 ms; measured on luna-pi, a Raspberry Pi | Note beat 3; `0201_01_sway-ipc-proof.md`, `0301_01_luna-pi-sway-result.md` | luna-pi, on every tile |
| MCP over SSH; "Query the tree, act, wait for the event." | Note beat 4; `0305_01_mcp-over-ssh-validation-result.md` | — |
| DEVELOPMENT ONLY | Note section 4 (`--full-ipc-development`, no capability policy) | — |
| 26 TOOLS; luna-pi, then Luna | Note beat 4; `src/wyoh/wyoh_mcp_server.py` | luna-pi, then Luna |
| Luna · 720 × 720 panel; BLACK.; GPU DRIVER LOADED.; `1 passed` once loaded | Note beat 5; `0407_01_luna-real-display-session.md`, `plan_wyoh.md` 4.8.3 | Luna |
| "Sway's own screenshots looked right." | `0407_01_luna-real-display-session.md` l.123 (the user saw a black panel while Sway's screenshots were correct), `0408_01`; confirmed by Wyoh 2026-11-01 | Luna |
| "Buttons drive the desktop." FN+pad focus, FN+A full screen, FN+B close, FN+R1 workspace | `0506_01_buttons-only-result.md` (button map) | Luna |
| Buttons only, on Luna, 2026-10-07 | Note beat 6; `0506_01_buttons-only-result.md` | Luna |
| THE SLATE TAKES THE TEXT; L1 OPENS IT | Note beat 6; `0605_01_slate-result.md` (L1 opens it, floating rule) | Luna |
| A DEV AGENT PRESSES THE SAME BUTTONS, via a virtual gamepad, not pixels | Note beat 6 (uinput device); Wyoh's check of 2026-11-01 (a development agent through the dev-only MCP server, not Mike) | — |
| In the Slate, FN + B → MIKE STARTS, ANSWERS IN 13 s (cold start) | Note beat 6; `plan_wyoh.md` 6.11; Wyoh's check of 2026-11-01 | Luna |
| Luna, 2026-10-30, a game's buttons died; FIX "VERIFIED"; THE GAME DID NOT MOVE; seven layers; only the last layer proves the fix | Note beat 7; `docs/howto/01_fix-a-game-gamepad-mapping.md` (layer table, section 8) | Luna |
| Layer names: real pad, Wyoh daemon, app profile, virtual pad, SDL, game bindings, the game moves | `docs/howto/01_fix-a-game-gamepad-mapping.md` section 1; `docs/howto/img/game-input-chain.svg`; confirmed by Wyoh 2026-11-01 | — |
| `sway_get_tree` | `src/wyoh/wyoh_mcp_server.py` (tool name) | — |
| "Screenshots stay, as evidence for humans." | Note section 2 and section 4 | — |
| "DON'T LOOK AT THE DESKTOP, ASK IT." / "The compositor already knows what a screenshot can only guess." | Note section 3 | — |

Must-not-say check: no revision counter or `wyoh_revision` shown as working (the DOM idea is labelled "ON PAPER"); the tree shows windows only, no app contents; the MCP pipe is labelled DEVELOPMENT ONLY and nothing says secure or finished; Mike only answers a question (no desktop action by Mike); screenshots kept as human evidence (payoff line, boss line); the four stage-3 figures carry luna-pi on every tile; "UNMODIFIED" and "NO FORK" on Sway; Adam does not appear; everything is drawn.

## Simplifications (staged, drawn, not captured)

- The robot is a generic agent icon, not any real model or product. Wyoh's and Mike's faces are crops of the key art.
- The pixelated desktop in stage 1, every mini-desktop, the handheld, the Slate and Mike's window are drawn icons, not pictures of real screens. The handheld is the shared `device` sprite (an icon of an R36 Ultra-style console).
- The HIOM scene with A/B/X buttons is illustrative of "finite advertised actions", not its real UI.
- The packets on the IPC and MCP pipes are illustrative; their timing is not measured.
- Stage 6: the four button chips are a subset of the map (FN+R2 also changes workspace; D-pad, sticks, Start, Select are omitted). The agent pressing FN+B is staged: the note says the agent presses the same buttons through a virtual gamepad, and separately that FN+B in the Slate reaches Mike; the scene puts the two together.
- The 13 s / 6.6 s figures: the note gives 13 s end to end and "0.6 s delivery and 6.6 s answer when Mike is already open"; the screen shows only the 6.6 s answer time.
- Stage 7: the layer ticks are staged in two passes (1–4, then 5–7); the real debugging found two bugs in two layers.
- The payoff tree is a drawn, abbreviated example: `DSI-1` is Luna's output name and `foot` a terminal used on Luna, but no real tree dump was copied. No machine is labelled on it.
- The boss's `1 passed` follows the note (2026-10-04, once the GPU driver was loaded); the Wyoh result page adds that some software-rendered runs were never confirmed on the panel. The episode does not go into that detail.

## Reading audit (`src/timing.py`)

`uv run --project /home/michael/git/tanstfaafllm python src/timing.py` → **Holds: +0.0 s, 90.0 s.** Every screen's last text has its orient time plus reading time before the cut (after the 2026-11-01 phone pass, SCREENS lists only key and secondary messages; tightest: boss phase a, 1.90 s for 1.90 s; stage 2, 4.35 s for 4.00 s). The changes made for this: the stage-2 lesson lands at 23.5 instead of 24.0, stage 6 phase b starts at 57.5, the date tag moved up, and the last stage-6 line was shortened.

Known limit: the stricter `--mode total` (all of a screen's text, read one after another) would ask for +34 s; the stages are dense. Stage text is layered so each new element is one line, and the stat tiles, layer rows and tree nodes are glance text. If the user finds a stage too fast on the phone, the first candidates for trimming were the stage-1 sentence and the stage-4 aside (both trimmed or cut on 2026-11-01).

Sizes: see "Phone readability, 2026-11-01"; glance text stays at P 28–32 / V 48. No text in the outer 5 % except the HUD's standard positions (same as Story 1). Nothing overlaps the CLEAR! stamp (bottom right, y≈980): checked on the contact sheets.

## Sound

`score.py` + shared `nes.py`, A minor, 120 BPM, two pulses, triangle, noise, mono. The trailer theme opens (title) and returns at full voice at the payoff (73.5). New: the Wyoh motif (E A B C rising, then settling), under the player screen and quoted as a head in stages 3 and 6 and under the result. Effects all from the shared helpers: coins for each screenshot guess, a buzz and drop on REOPENED and on "THE GAME DID NOT MOVE.", a boom on BLACK., the A-major victory when the panel lights, a Dsus4 stop-time in stage 7. The end card reuses the trailer cadence and fading chord.

Measured on the render (ffmpeg ebur128): **−15.3 LUFS integrated, true peak −1.1 dBFS**, LRA 3.1 LU.

## Files

- `src/index.html` — renderer (`renderFrame(t)`, pure function of time); `?t=12.5` to view a moment.
- `src/score.py` — the chip score; writes `music.wav` and `hits.json`.
- `src/timing.py` — reading audit; `src/holds.json` (empty).
- `src/build.sh` — one-command rebuild; OUT defaults to `/data/michael/tanstaafllm/video/story2-wyoh/render`.
- `src/nes.py`, `src/capture.py`, `src/contact.py`, `src/fonts/`, `src/art/` — shared, unchanged.
- Render: `render/tanstaafllm-story2-ask-the-desktop.mp4`, `render/contact_00.png` … `contact_05.png`, `render/stills/`.
