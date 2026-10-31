# The series template

**Workline:** hazel · **Step:** 1.3 · **Date:** 2026-10-31 · **Status:** draft for the user's review

Every TANSTAAFLLM video follows this template: the trailer, and then one episode per story. It is based on the trailer (`worklines/hazel/video/trailer/`) and on the list of elements shared with the trailer in the bring-up's `NOTES.md` (`/data/michael/tanstaafllm/video/bringup-v1/`). An episode may break a rule only when its notes say why.

## 1. What a video is

- It tells one story from the project, together with its vision. It is not a status report (see the plan's non-goals).
- **Framing:** the project played as a retro arcade game in which every bit of intelligence costs coins. The jokes are in the framing, never in the numbers.
- **Facts:** every figure and every claim on screen comes from a project page, and the episode's `NOTES.md` has a table that gives the source of each one. A figure shows the machine it was measured on (`luna-pi`, Luna, the desk host). Anything staged (sprites, icons, a generic prompt) is drawn, never captured, and the notes say so.
- **No screenshots or photos of real screens** (user, 2026-10-25). Use no third-party art, music or fonts unless their licence allows reuse.

## 2. Length and format

- **Trailer:** about 90 s (86.5 s on 2026-10-31). **Episode:** 60–90 s, and never more than 90 s unless the user agrees.
- **Format:** 1920 × 1080, 30 fps, H.264 high profile yuv420p, CRF 16, AAC 48 kHz. The file is `<slug>.mp4`.
- **Time grid:** 120 BPM, so 1 beat = 0.5 s = 15 frames and 1 bar = 2 s. Cuts fall on bar lines, and stamps fall on beats.

## 3. Episode frame

| Part | Length | Content |
|---|---|---|
| Title card | about 5 s | A black starfield with a pixel moon rising. "TANSTAAFLLM · STORY n" in amber Press Start 2P, then a large chrome stamp with the story title (for example "HELLO, LUNA"), then a cyan VT323 subtitle. Coin blips and the trailer theme. |
| Player / setting | 6–8 s | Who or what this story is about, with its stats or its quest. |
| Stages | the body | One obstacle per stage, each with its hit and a green **CLEAR!** stamp. Pips at the top right show progress. A boss is optional: use one for the hardest problem. |
| Payoff | 4–8 s | The title stamp comes back as the answer to the story. |
| "STORY n CLEAR" | about 6 s | A result screen that states the lesson in one or two sentences an engineer would recognise. |
| End card | about 6 s | The trailer's end card, unchanged: the chrome title from the key art, the motto, `github.com/mdussere/tanstaafllm`, "A personal engineering project by Michael Dussere", a blinking PRESS START, and a fade to black over the last 0.5 s. |

The trailer has the same open and close but no "STORY n" (it opens on INSERT COIN and ends on the doctrine, then the end card).

## 4. Look

- **Palette:** the trailer's `C` tokens (`src/index.html`). Do not add new colours: an episode reuses these tokens.

  | Token | Hex | Use |
  |---|---|---|
  | `ink`, `navy`, `navy2` | `#05060f` `#070b24` `#0f1645` | backgrounds, sky |
  | `violet`, `violet2` | `#2b1660` `#4a2a8c` | sky gradients, box fills |
  | `amber`, `amber2` | `#ffb43c` `#ff8a1e` | labels, emphasis, "STORY n" |
  | `cyan` | `#3ee8ff` | secondary lines, what is live |
  | `chrome` | `#eef3ff` | main text, stamps |
  | `dim`, `moon` | `#8e97cc` `#a9b3d8` | quiet text, the moon |
  | `red` | `#ff4d5e` | failure |
  | `green` | `#57ff8f` | success, CLEAR! |
  | `shadow` | `#0a0420` | the hard drop shadow |

- **Type:** Press Start 2P for capitals (labels 28–44 px, stamps 64–112 px). VT323 for sentences (48–56 px). Both cast the same hard drop shadow. Both fonts are under the SIL OFL 1.1, and their licence texts ship with the fonts.
- **Surfaces:** the double-border RPG `box`. Pixel sprites are drawn in code (the handheld, the microphone, the coin…) and are icons, not drawings of the real devices. Character faces are crops of the key art.
- **Post layer:** faint scanlines and a vignette on every frame.
- **Transitions:** a white flash on cuts and stamps, and the 60 px block dissolve. Do not use other transitions.
- **Stamps:** they scale in with a shake and land on a music hit.

## 5. Sound

- **Chip:** an emulated NES 2A03 (`nes.py`, shared unchanged): two pulses, one triangle and noise; mono; 60 Hz frames; no reverb, no samples ("plus années 80", user, 2026-10-30).
- **Key and tempo:** A minor, 120 BPM. The trailer theme (score A, kept by the user on 2026-10-30) opens each episode and returns at the payoff. The end-card cadence and the A-minor chord fading in 4-bit steps belong to the trailer and are reused as they are.
- **Sound effects:**
  - coin, blip;
  - failure buzz (a 12.5 % pulse sliding down, plus a noise rasp) and success ding;
  - the CLEAR! jingle (a coin, then a major arpeggio) and the level-clear fanfare.
  - An episode can add new effects, built from the same helpers.
- **Loudness:** about −15 LUFS integrated, peaks at −1 dBFS or below (trailer −15.6 LUFS, bring-up −15.3 LUFS).

## 6. Reading and captions on a phone

- **Reading model** (`timing.py`), the same for every video:
  - the viewer needs 0.4 s to notice a new text;
  - then 0.25 s per VT323 word or 0.30 s per Press Start 2P word;
  - a screen stays at least 1.0 s after its last text appears.
- Holds (`holds.json`) freeze the choreography, but the stars and blinks keep moving. Prefer writing the timeline so that no hold is needed (the bring-up needed none).
- **Phone:** the video is watched on a phone held sideways. That gives the minimum sizes above: nothing smaller than 28 px Press Start 2P or 48 px VT323 on the 1080-line canvas. The text should not fill the screen: give each screen one new element at a time, so that the eye can follow it. Keep text out of the outer 5 % of the frame.
- There are no voice-over and no burnt-in subtitles: the on-screen text is the narration. A video must be understandable with the sound off.
- **Check:** before an episode goes on the private page, Hazel inspects the contact sheets (`contact.py`) and at least one still per screen at phone scale.

## 7. Thumbnails

- Each video has a YouTube thumbnail in the series' fonts and palette:
  - 1280 × 720 JPEG, named `<video-file>-thumbnail.jpg`, next to the video in `~/Videos/TANSTAAFLLM/`;
  - a tag in amber Press Start 2P ("TRAILER", "STORY n"), the title in chrome, one green or cyan line;
  - one picture: the key art, or the episode's sprite.
- Professor made the first two with Pillow (2026-10-31): `tanstaafllm-trailer-thumbnail.jpg` (the key art, an "EVERY TOKEN COSTS." band and a TRAILER tag) and `tanstaafllm-story1-hello-luna-thumbnail.jpg` (the handheld, "STORY 1", "HELLO, LUNA", `$ ssh luna`, a subtitle).
- From now on, Hazel makes the thumbnails. Ideally each one is a still from the video's own renderer (a `thumbnail` scene in `index.html`, captured by `capture.py`), so that it stays in the series' look and can be rebuilt from Git.

## 8. Sources and build

- **Layout:** each video lives in `worklines/hazel/video/<slug>/`. That directory holds:
  - `README.md` (how to rebuild);
  - `NOTES.md` (the concept, the structure table, a source for every fact, the simplifications, the reading audit, the sound);
  - `src/`.
- **Pipeline:** `src/build.sh` is the one-command rebuild. It runs these steps:
  - `score.py` + `nes.py` → the WAV file;
  - ffmpeg softens the top end and limits the peaks;
  - `capture.py` (Playwright and Chromium call `renderFrame(t)` for each frame, and the frames are piped to ffmpeg).
- **Frames:** each frame is a pure function of time.
- **Where things go:**
  - renders go to `results/hazel/<slug>/<timestamp>/` (not in Git);
  - large working files go to `/data/michael/tanstaafllm/video/`.
- **Shared code:** `index.html`'s head (the utilities, backgrounds, key art, `device` sprite and `POST` layer), `nes.py`, `capture.py`, `contact.py` and `timing.py` are copied from the trailer, verbatim. Moving them into a shared `worklines/hazel/video/common/` is a later choice, to be made when the third video exists.

## 9. Making an episode

1. Hazel writes a short brief: the story page(s) and this template, without the cell's context. The brief goes to a sub-agent (user, 2026-10-25).
2. Hazel checks the cut against this template and the reading audit, and checks each fact against its source page. For a fact Hazel is not sure of, she asks the workline that owns it.
3. The cut goes on the private phone page for the user. Only then does it go to a public channel, and only after the user says go.
