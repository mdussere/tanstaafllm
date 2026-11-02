# common/: the script-to-video pipeline

An AI writes a short **episode script** (about 150 lines of YAML); the CPU builds the video: timeline, picture, score, reading audit, layout lint, `NOTES.md`, MP4. Design: `worklines/hazel/docs/0601_01_token-lean-video-pipeline.md` (§2, §5). First target: Story 2, built from `episodes/story2-ask-the-desktop.yaml` (145 lines). The script is high level: it carries what a writer decides (texts, sources, mood); the templates decide positions, sizes, colours, the entry choreography on the beat and the music cues. It no longer reproduces the hand-written `story2-ask-the-desktop/` pixel for pixel.

## Build

```bash
cd worklines/hazel/video
uv run --project <repo> python common/build.py episodes/story2-ask-the-desktop.yaml --preview   # 640x360 @ 10 fps, seconds
uv run --project <repo> python common/build.py episodes/story2-ask-the-desktop.yaml --full      # 1920x1080 @ 30 fps, ~7 min
# options: --out DIR (default <repo>/results/hazel/<episode>/<timestamp>/)  --no-video  --lint-step 0.5  --strict
```

`--strict` makes the build exit 2 when the layout lint finds a problem (overflow, margin, overlap, CLEAR! zone, a text squeezed below 90 % of its width, the phone rule) or the reading audit adds a hold; every output is written either way. Tests: `uv run pytest test/hazel` (the two integration tests need Playwright's Chromium and ffmpeg; `-m "not integration"` skips them).

It writes, into the output directory: `index.html` (runtime + templates + the generated timeline; open it with `?t=12.5` for one frame or `?play`), `fonts/`, `art/`, `music.wav`, `hits.json`, `audit.md` (reading audit), `lint.txt`, `NOTES.md` (structure table, facts with sources, audit, lint), `contact.png` (12 thumbnails, 960 px wide), `stills/`, and the MP4. The preview is the same picture scaled down, so a preview that is clean is clean at full size. The model's loop: write the script, read `lint.txt` and `audit.md`, look at `contact.png` once.

The script no longer reproduces the hand-written Story 2, so a pixel diff against it is not expected to be 0; use this to compare two builds: `common/diff_stills.py PAGE_A PAGE_B OUTDIR t1 t2 ...` prints the mean absolute pixel difference per still (0 = identical).

## Files

| File | Role |
|---|---|
| `layout.py` | script -> scenes: each template's slots, positions, sizes, colours, entry times (on the beat, from the scene length), cue marks and audit slots |
| `runtime.js` | the shared renderer head (palette, `txt`, `box`, backgrounds, sprites, device, agent, post layer), the player (`renderFrame`, holds) and the lint recorder |
| `templates.js` | the drawing side: `TPL[id](t, p)` frame scenes and `KINDS[kind](t, p, item)` content kinds (what `layout.py` emits) |
| `slots.py` | reads the slots `layout.py` recorded (key, secondary) for the reading audit |
| `audit.py` | the reading audit (rules of Story 2's `timing.py`) |
| `cues.py` | the 2A03 score: helpers, `MOODS` and `STYLE`, one cue per template placed from the layout's marks, `FX` table for raw events |
| `nes.py` | the 2A03 chip emulation |
| `lint.py` | the text layout lint |
| `timemap.py` | source time (the script's) and output time (the video's) around the reading holds; `runtime.js` `sourceTime` mirrors it |
| `build.py`, `capture.py`, `contact.py`, `diff_stills.py` | generator, frame capture (Playwright + ffmpeg), contact sheet, regression check |
| `fonts/`, `art/` | Press Start 2P, VT323, the key art (copied once) |

## The script

```yaml
episode: story2-ask-the-desktop
title: ASK THE DESKTOP
bpm: 120                       # optional, and only 120: layout, page and score are written for 0.5 s beats (2 s per bar)
motif: [[beat, midi, beats], ...]    # optional: the episode's own theme, reused by the player card, the result screen
scenes:
- id: stage1
  template: guess              # a template name (below)
  bars: 3                      # the scene length: cuts always fall on bar lines
  mood: tense                  # the music (below)
  title: "THE SCREENSHOT TRAP"   # stage templates: the HUD title; the stage number and the pips come from the order
  key: ["An agent guesses from pixels", "and pays for every image."]   # the one key message, at most 2 lines
  secondary: "ON PAPER: A DESKTOP DOM."
  ...template slots...
  machine: luna-pi             # NOTES.md "machine shown" column (optional)
  sources: ["Note beat 1 ..."] # NOTES.md facts: every scene lists where its texts come from
```

**Phone rule** (the templates apply it): `key` is the one key message, VT323 90 (default) or Press Start 2P 56 (`key_font: P`), at most 2 lines, and the only text of that size on screen at a time. `secondary` is Press Start 2P 40 or VT323 64. `glance` labels are 28 px and never carry the story. Texts the audit counts are only `key` and `secondary`; the generator turns a shortfall of reading time into holds (rounded up to whole beats) and silence in the score.

**Timing.** Stage scenes put the CLEAR! stamp 1.5 s before the end. Each template spreads its elements on the beat: the visual early, then the key, then the secondary about 3 beats before the stamp. A scene too short for its template is refused: every cue mark and read text must fall between the scene start and its CLEAR! stamp (a frame template: its end), and a missing slot is reported with the scene and the template. Overrides (rare): `at: {name: seconds}` moves a named element (`key`, `secondary`, `visual`, `works`, `tiles`, `victory`, `cut`, `chips`, `claim`, `resume`, `nodes`, `pipe`, `packets`, `first`, `subject`; see `layout.py`), `content: [...]` appends raw stage items (KINDS below), `events: [...]` appends raw score events (below).

### Templates and their slots

Common slots: `key`, `secondary`, `glance`, `title` (HUD title of a stage; the heading of `result`), `mood`.

| Template | Frame | Slots (besides the common ones) |
|---|---|---|
| `title_card` | T01 | `series` (glance line), `key` (the title, stamped), `secondary` (2 lines) |
| `player_card` | T04 | `face` (`wyoh mike mannie prof`), `glance` [label, quest label], `name`, `secondary` (role, 2 lines), `key` (quest, 2 lines) |
| `guess` | stage | `guesses` (chips, each costs a coin), `key`, `secondary` |
| `two_boxes` | stage | `fail: {label, glance: [2], stamp}` (a first idea that failed), `works` (label of the kept box), `key` (in the box, Press Start 2P) |
| `metrics` | stage | `subject: {label, tags, link}`, `tiles` [{label, value, machine}] (up to 4), `glance` (caption), `key`, `machine` (default of the tiles) |
| `flow` | stage | `via` (2 pipe labels), `target`, `key`, `secondary` (stamped), `glance` |
| `boss` | stage | `panel` (caption), `phases` [{key, secondary, glance}, {key, secondary}] (before / after the hit), `states` (HUD labels, default BLACK, LIT) |
| `handheld` | stage | `parts` [A, B]: A `{key, chips [[button, action, device button]], glance [2], secondary, screen}`, B `{key, glance, combo {label, keys, face}, secondary, screen, agent}` (a cut between the parts at about 55 %) |
| `checklist` | stage | `items`, `claim` (item declared done), `fail` (item that did not work), `glance` [2], `secondary` [claim text, fail text], `key` (the lesson) |
| `tree` | T21 | `glance` (the call), `nodes` [[depth, label]] (leaves green), `key` (stamped), `secondary` |
| `result` | T22 | `title` (heading), `key` (2 lines), `secondary` (2 lines); one pip per stage |
| `end_card` | T23 | `key` (motto, 2 lines), `glance` [address, credit] |

### Moods

`mood` picks the chord progression of the groove (`cues.MOODS`) and the character of the cues (`cues.STYLE`: the scale of the entry blips, the pitches of the stamp on the key, the mood a turn leads to, the drums). Moods: `calm bright tense driving climb agent resolve boss victory opener theme layers stoptime lift uneasy wary`. A stage scene always gets: the stage-start jingle, the groove from the first beat, an entry blip per element (rising on the mood's scale), a stamp hit on the key message, a ding on each secondary, the CLEAR! jingle at the stamp and a noise roll into the next scene. Template-specific marks: a coin per guess, a sliding blip per packet, a key click per button press, a buzz and a drop on a failure, a tick per checked item. A **turn** (the working idea in `two_boxes`, the resume in `checklist`) switches the groove to the mood's `after` (`tense` -> `resolve`); `boss` plays an ostinato, a riff and a double-time beat until the victory (a build-up roll, a crash, an arpeggio, a ding), then `victory`. Frame templates have a fixed cue (title: coin, stamp, trailer theme; player: stamp, groove, motif; tree: call blip, one blip per node, theme on the key; result: fanfare, one blip per pip, motif; end: trailer cadence, chord fading in 4-bit steps) tuned by `mood`. `motif` is played by the player card and the result screen.

## Low-level stage content and score events (overrides)

`layout.py` emits stage items that `templates.js` draws; a scene can append its own with `content:`. Each item: `kind`, its parameters, optional `from` / `until` (relative seconds).

| Kind | Parameters |
|---|---|
| `text` | `lines` (strings, or `{s, at}`), `x`, `y`, `dy`, `font` (`P` or `V`), `size`, `color`, `at`, `fade`, `align`, `maxW`, `shadow`, `blink`; `read: true` counts it in the audit |
| `runs` | `parts` ([[text, colour], ...]), `x`, `y`, `size`, `at`, `fade` |
| `stamp` | `lines`, `x`, `y`, `dy`, `size`, `color`, `at`, `align`, `rot`, `from` (start scale) |
| `box`, `rects`, `minidesk`, `agent`, `face`, `packet`, `flash` | primitives: boxes, rectangles, a miniature desktop (`focus`: number, `cycle` or `[[from, n]]`), the robot (`mode`: look, squint, ask), key-art faces, a travelling packet, a flash |
| `pixel_grid_guess` | `at`, `agent_at`, `guesses` ([[at, text]]), `block` |
| `scene_spill` | `label`, `at`, `gone_at`, `spill_at`, `spill_step` |
| `tiles` | `tiles` ([[at, caption, figure, badge]]), `x`, `y` |
| `pipe` | `x0`, `x1`, `y`, `labels` ([{s, dy, color, at}]) |
| `handheld` | `x`, `y`, `s`, `bob`, `states` ([[from, black/flash/desk/slate/mike/moon/none]]), `focus`, `ws`, `answer_at`, `presses` ([{from, to, btns}]) |
| `actions`, `key_combo` | button chips and a keycap combination with its answering face (`y` optional) |
| `layers` | `names`, `ok` (time per layer), `fail`, `highlight`, `unknown_from`, `x`, `y`, `w` |
| `boss_hud` | `hit1`, `fix`, `labels` |

Raw score events (`events:`) play after the generated cues: `{fx, at, ...arguments}`; `at` may be a list, or `at` + `step` + `n` with `each: {arg: [value per step]}`. Effects (`cues.FX`): `blip coin ding buzz tri_drop stamp hit_all key tick nz boom melody groove chord_arp note bass8 hats ostinato double_time roll noise_sweep` and the composites `guess_coin key_blip`; `melody` takes `notes` as a list or a named riff (`motif`, `motif_head`, or a key of `riffs`).

## Adding a template

1. **Layout.** In `layout.py` add `t_<name>(b)` (stage frame) or `f_<name>(b)` (a whole-screen frame, add it to `INTERNAL`): name its slots, place them with `b.key`, `b.second`, `b.glance`, `b.text`, `b.stamp`, `b.add(kind, ...)`, time them on the beat from `b.z` (the CLEAR! time) or `b.len`, put marks (`b.mark('enter', t)` ...) where the music should land. `b.key` / `b.second` record the audit slots; a frame template records them with `b.slot`.
2. **Picture.** Missing drawing? Add `KINDS.my_kind = (t, p, it) => {...}` (or `TPL.T24` for a frame) in `templates.js`: event times relative (`p.t0 + x`), text through `txt`, `V`, `tag`, `runs` or `stampTxt` so the lint sees it, `C` tokens for colours.
3. **Music.** Stage templates need nothing beyond their marks (handled in `cue_T05`); a new mark kind gets a branch there; a frame template gets `cue_T24` in `CUES`.
4. Use it in a script, run `--preview`, read `lint.txt` and `audit.md`, look at `contact.png`, then give the template a card in `video/library/`.

## Layout lint (`lint.txt`)

Every `txt()`/`runs()` call records its box (font, size, glyph height from the cap height, bounding box including rotation and scale) per frame. `build.py` samples every 0.5 s and reports overflow outside the frame, text in the outer 5 %, overlaps between texts, text inside the CLEAR! zone, and the phone rule: key >= 50 px glyph height (VT323 >= 90, Press Start 2P >= 56), secondary >= 35 px, everything smaller listed as glance text. Texts fading in (alpha < 0.5) or sliding in (scale > 1.02) are skipped. The CLEAR! zone follows the stage's label (a longer `clear_text` moves left) and the stamp's rotation. A text that `txt()` narrowed to fit its `maxW` is listed as a squeeze. Texts drawn with the same `group` option count as one message (the metric tiles: one block of figures, every tile an audit slot). Key messages are counted as messages (stacked lines of one font and size are one): a scene must have at least one and never two at once (CLEAR! and the HUD title are not counted).

## Known limits

- Overlaps are text against text; text over a drawn shape is not checked.
- The lint samples every 0.5 s: a 0.2 s overlap between samples can be missed (use `--lint-step 0.1`).
- Only the templates Story 2 uses are converted (the table above; library T01, T04, T05, T06, T08, T11, T12, T13, T14, T18, T19, T20, T21, T22, T23). T02, T03, T07, T09, T10, T15, T17 are converted when an episode needs them.
- `metrics` shows at most 4 tiles; `tree` is laid out for about 8 nodes; `checklist` for about 9 items.

### Stage end stamp

Every stage ends on a green stamp, `CLEAR!` by default. A scene can set `clear_text` to say something else, for example `LET'S DO IT!` when the stage ends on a choice rather than a success. `clear_color` picks its palette token (`green` by default, `red` for a refusal such as `NO GO!`).
