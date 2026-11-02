# How the video generator works, and what it saves

> **Freshness:** 🟢 current · **Written:** 2026-11-02 · **Checked:** 2026-11-02 · **Step:** hazel 6.6

**Question:** how does a video come out of a script, and how many Claude Code tokens does that save compared with writing the video's HTML by hand (user, 2026-11-02)?

## 1. The principle in one paragraph

A video is a pure function of time: frame `t` shows exactly what `renderFrame(t)` draws, and the music is a list of notes on the same clock. Writing that function by hand for each episode costs the model hundreds of lines of canvas and music code. The generator splits the work differently. **The model writes what a writer decides**: the scenes, their order, their length in bars, the texts, the facts and their sources, and the mood. **Code that is already written decides everything else**: positions, sizes, colours, the choreography on the beat, the sound effects, the reading audit and the checks. That code runs on the CPU, so it costs no tokens, however often it runs.

## 2. The script

An episode is one YAML file in `worklines/hazel/video/episodes/`. Story 2 is 144 lines. One scene:

```yaml
- id: stage1
  template: guess              # which sequence template (from the library)
  bars: 3                      # length: 3 bars = 6 s at 120 BPM
  mood: tense                  # picks the chords and the energy of the cues
  title: "THE SCREENSHOT TRAP"
  guesses: ["A BUTTON?", "A WINDOW?", "WHICH ONE?"]      # template-specific content
  key: ["An agent guesses from pixels", "and pays for every image."]   # THE message (big)
  secondary: "ON PAPER: A DESKTOP DOM."                  # at most one smaller message
  clear_text: NO GO!           # the stage's end stamp (CLEAR! by default)
  clear_color: red             # red = a refusal: red stamp and a failure buzz
  sources: ["Note beat 1 …"]   # where each fact comes from
```

There are no coordinates, font sizes, times or notes. The episode header gives the slug, the title, the tempo and an optional **motif**, a few notes that some templates reuse (Wyoh's rising E A B C).

## 3. From the script to the MP4

One command, `uv run python common/build.py episodes/<episode>.yaml --preview | --full`, runs the whole chain on the CPU:

```
episode.yaml
   │
   ├─ 1. timeline (build.py)     bars → start and end seconds, cuts on bar lines
   ├─ 2. layout (layout.py)      each template turns the scene into concrete items:
   │                              key / secondary / glance slots placed and sized by the phone
   │                              rule, entries spread on the beat, stamp time, cue marks
   ├─ 3. reading audit (audit.py, slots.py)   from the slots: is the last text readable before the
   │                              cut? If not, a hold is added (Story 2: +0.0 s)
   ├─ 4. page (build.py)         index.html = runtime.js (shared drawing helpers, sprites,
   │                              palette) + templates.js (one draw function per template)
   │                              + the scenes as data
   ├─ 5. music (cues.py, nes.py) the cue marks + the mood → notes and effects → the emulated
   │                              NES chip → WAV → two-pass loudness normalisation (−15 LUFS,
   │                              true peak ≤ −1.5 dBTP)
   ├─ 6. lint (capture.py, lint.py)   the page records every text box it draws; frames are
   │                              sampled every 0.5 s and the boxes are checked: overflow,
   │                              5 % margins, overlaps, the stamp zone, one key ≥ 50 px per scene
   ├─ 7. render (capture.py)     headless Chromium calls renderFrame(t) for each frame,
   │                              piped to ffmpeg with the WAV → MP4
   └─ 8. reports                 audit.md, lint.txt, NOTES.md (structure and fact tables from the
                                  script), hits.json, one small contact sheet
```

- **`--preview`:** 640 × 360 at 10 fps, about 1 minute. Used while working.
- **`--full`:** 1920 × 1080 at 30 fps, about 7 minutes. Run once at the end.
- **Output folders:** `results/hazel/<episode>/<timestamp>-preview|-full/`.

## 4. Where the model still spends tokens

| Task | Model work | Notes |
|---|---|---|
| A new episode | the story with its owner, then a script of about 150 lines | the biggest remaining item |
| A visual idea the library lacks | **one new template**: a layout function and a draw function | the series rule asks for one per episode; it is then reusable |
| Checking | reading `lint.txt` and the audit (text), then **one** small contact sheet | images are the expensive input; the lint replaces most of them |
| A revision | editing a few lines of the script | example: swapping two stages, changing a stamp |
| A generic improvement | a few lines in `common/` | example: `clear_text`, `clear_color`, loudness |

## 5. The token balance

**Measured** (sub-agent counts from the harness, 2026-11-01 and 2026-11-02):

| Work | Way | Tokens |
|---|---|---|
| Story 2, first composition (finishing it) | HTML by hand | ≈ 160 k (plus the first try stopped during the pause, not counted) |
| Story 2, phone-size rework | HTML by hand | ≈ 129 k |
| **Story 2 by hand, total** | | **≈ 290 k** at least |
| Building the pipeline (6.2–6.5) | once | ≈ 215 k (Sonnet) |
| Making the script high level (6.4b) | once | ≈ 193 k (Sonnet) |
| Story 2 revision: new Playwright stage with a new `compare_table` template, seven layers removed | script | **≈ 54 k** (Sonnet) |
| Swapping two stages, LET'S DO IT!, NO GO!, loudness and folder fixes | script, by Hazel directly | not measured: done in Hazel's main session, which the harness does not count per task; a few short edits and three image checks |

**What this shows:**

- **A revision:** 54 k through the script against 129 k by hand, so **about 2.4 times less**. That is although the 54 k include creating a new template, which a plain revision does not need.
- **The small changes** (reorder, a stamp text) no longer need a sub-agent at all: a few script lines and one preview.
- **The one-time cost** (≈ 408 k) is paid back after about **two episodes**, if a new episode by script costs about 60–100 k against ≈ 290 k by hand. This figure for a new episode is an **estimate**. It will be measured on the next episode: the plan records the sub-agent tokens per episode.
- **The models differ.** The pipeline was built and used by Sonnet sub-agents, and the hand-made Story 2 by Opus sub-agents. Sonnet costs less per token, so the saving in cost and in quota is larger than the token ratio.

## 6. What still costs the most

- **Long conversations.** Hazel's main session re-reads its whole context at every turn. A short session per episode, with a handoff note, saves more than any change to the code.
- **Images.** One full-size contact sheet costs as much as a page of code. Use the lint first, look at small sheets, and only at the end.
- **New templates.** They are the right place to be creative, but each one is real code. One per episode is the rule.

## 7. How to make the next episode

1. Get the story and its facts from the workline that owns them (a note, as Wyoh did).
2. Write `episodes/<slug>.yaml` from the library (`video/library/README.md`): templates, bars, key and secondary messages, sources, moods, and at most one new template.
3. `build.py … --preview` until `lint.txt` is clean and the audit shows +0.0 s.
4. Look at the contact sheet once, then run `--full` once.
5. Deliver to `~/Videos/TANSTAAFLLM/` and the private page, commit, and record the tokens spent in the plan.
