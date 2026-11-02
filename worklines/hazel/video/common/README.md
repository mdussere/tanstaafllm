# common/: the script-to-video pipeline

An AI writes a short **episode script** (about 150 lines of YAML); the CPU builds the video: timeline, picture, score, reading audit, layout lint, `NOTES.md`, MP4. Design: `worklines/hazel/docs/0601_01_token-lean-video-pipeline.md` (§2, §5). First target: Story 2, rebuilt from `episodes/story2-ask-the-desktop.yaml` with the same picture and sound as `story2-ask-the-desktop/`.

## Build

```bash
cd worklines/hazel/video
uv run --project <repo> python common/build.py episodes/story2-ask-the-desktop.yaml --preview   # 640x360 @ 10 fps, seconds
uv run --project <repo> python common/build.py episodes/story2-ask-the-desktop.yaml --full      # 1920x1080 @ 30 fps, ~7 min
# options: --out DIR (default <repo>/results/hazel/<episode>/<timestamp>/)  --no-video  --lint-step 0.5
```

It writes, into the output directory: `index.html` (runtime + templates + the generated timeline; open it with `?t=12.5` for one frame or `?play`), `fonts/`, `art/`, `music.wav`, `hits.json`, `audit.md` (reading audit), `lint.txt`, `NOTES.md` (structure table, facts with sources, audit, lint), `contact.png` (12 thumbnails, 960 px wide), `stills/`, and the MP4. The preview is the same picture scaled down, so a preview that is clean is clean at full size. The model's loop: write the script, read `lint.txt` and `audit.md`, look at `contact.png` once.

Check the pipeline against a hand-written page: `common/diff_stills.py PAGE_A PAGE_B OUTDIR t1 t2 ...` prints the mean absolute pixel difference per still (0 = identical).

## Files

| File | Role |
|---|---|
| `runtime.js` | the shared renderer head (palette, `txt`, `box`, backgrounds, sprites, device, agent, post layer), the player (`renderFrame`, holds) and the lint recorder |
| `templates.js` | `TPL[id](t, p)` scene functions and `KINDS[kind](t, p, item)` content kinds |
| `slots.py` | the text slots of each template, for the reading audit |
| `audit.py` | the reading audit (rules of Story 2's `timing.py`) |
| `cues.py` | the 2A03 score: helpers, `MOODS`, `FX` table, one cue per template |
| `nes.py` | the 2A03 chip emulation |
| `lint.py` | the text layout lint |
| `build.py`, `capture.py`, `contact.py`, `diff_stills.py` | generator, frame capture (Playwright + ffmpeg), contact sheet, regression check |
| `fonts/`, `art/` | Press Start 2P, VT323, the key art (copied once) |

## The script

```yaml
episode: story2-ask-the-desktop     # slug, also the output folder name
title: ASK THE DESKTOP
bpm: 120                            # 4 beats per bar: 120 BPM = 2 s per bar
stages: 7                           # stage pips (HUD, result screen)
boss_stage: 5                       # that stage number is the boss (red sky, no pips)
motif: [[beat, midi, beats], ...]   # the episode's own theme (named `motif` / `motif_head` in events)
riffs: {boss: [[beat, midi, beats], ...]}   # more named note lists
scenes:
- id: stage1
  template: T05                     # a template id (below)
  bars: 3                           # length: start times follow from the bars, so cuts always fall on bar lines
  ...template parameters...
  mood: uneasy                      # chord progression of the groove (cues.MOODS)
  events: [...]                     # T05 only: ordered score events (below)
  picture: "..."                    # one line each, for the NOTES.md structure table
  music_note: "..."
  facts: [{on_screen: "...", source: "...", machine: "luna-pi"}]   # every fact with its source; NOTES.md table
```

All times in a scene are **seconds from the scene start**; x and y are canvas pixels (1920 x 1080, safe margin 120). Colours are palette names (`chrome amber cyan green red dim ink navy violet ...`, see `C` in `runtime.js`) or `"#rrggbb"`.

Reading audit keys: `read: true` on a text item marks a key or secondary message (or `read: "text"` to count another text, `read_at:` to override the moment it is readable); glance text is left unmarked. `screens: [{name, cut}, {name}]` splits a scene into audit screens (a cut inside the scene). `cut_lead:` is how long before the scene end the text starts to disappear (default per template: T01 0.2, T04 0.25, T21 0.25, T23 0.5). `still:` picks the contact-sheet moment of a scene. The generator turns a shortfall of reading time into holds (rounded up to whole beats) and inserts silence in the score at the same points.

## Templates and their parameters

| Id | Name | Parameters (besides `id`, `bars`, `mood`) |
|---|---|---|
| T01 | Series title card | `series`, `title`, `title_at` (stamp time), `sub` (2 lines), optional `series_at`, `sub_at`, `press_at` |
| T04 | Player card | `face` (`wyoh mike mannie prof`), `label`, `name`, `role` (2 lines), `quest_label`, `quest` (2 lines), optional `seed` |
| T05 | Stage frame | `stage`, `title`, `content` (items), `clear` (time of the CLEAR! stamp), `flashes` ([[at, up, down, colour]], default one white flash down at 0), `stage_start` (false to skip the jingle), `arp`, `roll` ([v0, v1]), `events` |
| T21 | Payoff reprise + tree reveal | `call`, `tree` ([[depth, label], ...]), `stamp`, `aside`, optional `stamp_at`, `aside_at`, `seed` |
| T22 | Result screen | `headline`, `lesson` (2 lines), `sub` (2 lines), optional `lesson_at`, `sub_at` |
| T23 | End card | `motto`, `url`, `credit` |

T05 content kinds (each item: `kind`, its parameters, optional `from` / `until` to show it only in a window of the scene):

| Kind | Library | Parameters |
|---|---|---|
| `text` | | `lines` (strings, or `{s, at}`), `x`, `y`, `dy`, `font` (`P` or `V`), `size` (P 28 default), `color`, `at`, `fade` (0.2; 0 = no fade), `align`, `maxW`, `shadow`, `blink` |
| `runs` | | `parts` ([[text, colour], ...]), `x`, `y`, `size`, `at`, `fade` |
| `stamp` | T08 | `lines`, `x`, `y`, `dy`, `size`, `color`, `at`, `align`, `rot`, `from` (start scale) |
| `box`, `rects`, `minidesk`, `agent`, `face`, `packet`, `flash` | | primitives: boxes, rectangles, a miniature desktop (`focus`: number, `cycle` or `[[from, n]]`), the robot (`mode`: look, squint, ask), key-art faces, a travelling packet, a flash |
| `pixel_grid_guess` | T18 | `at`, `agent_at`, `guesses` ([[at, text]]), optional `block` |
| `scene_spill` | T06 | `label`, `at`, `gone_at`, `spill_at`, `spill_step` |
| `tiles` | T13 | `tiles` ([[at, caption, figure]]), `x`, `y`, `badge` |
| `pipe` | T14 | `x0`, `x1`, `y`, `labels` ([{s, dy, color, at}]) |
| `handheld` | T12 | `x`, `y`, `s`, `bob`, `states` ([[from, black/flash/desk/slate/mike/moon/none]]), `focus`, `ws`, `answer_at`, `presses` |
| `actions`, `key_combo` | | button chips and a keycap combination with its answering face |
| `layers` | T19 | `names`, `ok` (time per layer), `fail`, `highlight`, `unknown_from`, `x`, `y`, `w` |
| `boss_hud` | T11 | `hit1`, `fix`, `labels` |

### Score events (T05 `events:`)

The cue for T05 plays the stage-start jingle, the mood groove, then your events in the order written (order matters when two sounds use one channel: a later write wins), then the CLEAR! jingle at `clear` and a noise roll into the next scene. An event is `{fx, at, ...arguments}`; `at` may be a list, or `at` + `step` + `n` with `each: {arg: [value per step]}`. Effects (`cues.FX`): `blip coin ding buzz tri_drop stamp hit_all key tick nz boom melody groove chord_arp note bass8 hats ostinato double_time roll noise_sweep` and the composites `guess_coin key_blip`. `melody` takes `notes` as a list or a named riff (`motif`, `motif_head`, or a key of `riffs`). Frame templates (T01, T04, T21, T22, T23) have a fixed cue, tuned by `mood`.

Moods (`cues.MOODS`): `opener driving uneasy wary resolve bright climb agent layers stoptime lift theme calm`; an event `groove` may also give `prog: [[Am, 2], [F, 1]]`.

## Adding a template (the one new template of an episode)

1. **Picture.** In `templates.js`, add `TPL.T24 = (t, p) => {...}` for a whole scene (frame templates), or `KINDS.my_kind = (t, p, it) => {...}` for a T05 content kind. Rules: event times are relative (`const A = x => p.t0 + x`); animations that depend on the phase of `t` use the absolute `t`; draw text through `txt`, `V`, `tag`, `runs` or `stampTxt` so the lint sees it; use `C` tokens, never new colours without a reason.
2. **Audit.** In `slots.py`, add the text slots (`SLOTS['T24']`, or a branch in `item_slots` for a kind) with their readable times, and `LEAD` if it ends with a dissolve or flash.
3. **Music.** In `cues.py`, add `cue_T24(sc, ctx)` to `CUES` (stage kinds need nothing: use `events:`).
4. Use it in the script, run `--preview`, read `lint.txt`, then give the template a card in `video/library/` (see its README).
5. Regression: `diff_stills.py` against the previous page must still print 0 for the old episodes.

## Layout lint (`lint.txt`)

Every `txt()`/`runs()` call records its box (font, size, glyph height from the cap height, bounding box including rotation and scale) per frame. `build.py` samples every 0.5 s and reports overflow outside the frame, text in the outer 5 %, overlaps between texts, text inside the CLEAR! zone, and the phone rule: key >= 50 px glyph height (VT323 >= 90, Press Start 2P >= 56), secondary >= 35 px, everything smaller listed as glance text. Texts fading in (alpha < 0.5) or sliding in (scale > 1.02) are skipped.

## Known limits

- Overlaps are text against text; text over a drawn shape is not checked.
- The lint samples every 0.5 s: a 0.2 s overlap between samples can be missed (use `--lint-step 0.1`).
- Only the templates Story 2 uses are converted (T01, T04, T05 with its kinds, T06, T08, T11, T12, T13, T14, T18, T19, T20, T21, T22, T23). T02, T03, T07, T09, T10, T15, T17 are converted when an episode needs them.
