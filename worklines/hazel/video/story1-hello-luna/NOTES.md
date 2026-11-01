# Hello, Luna — TANSTAAFLLM story 1 (the bring-up)

94.0 s, 1920×1080, 30 fps, H.264 + AAC. Built on the trailer's renderer, pipeline and NES-chip score. The first cut (88 s) was made by a sub-agent; Hazel revised it on 2026-10-31 (see the next section).

## Revision 2026-10-31 (the user's review, relayed by Professor)

Two changes, and the score refitted. Nothing else changed.

1. **Stage 1 becomes "Secure the original card".** The "62 BYTES" failure is gone: it was an anecdote, a command that did not run, not a real problem. Stage 1 now shows a positive first move. The whole factory card is extracted to disk and checked, and then it is explored. The stage ends on "FIRST, SECURE THE ORIGINAL. THEN EXPLORE IT."
2. **A new stage 2, "Choose a system" (20–26 s).** Several community systems exist for these clones. One looped its interface and was set aside. We chose ArchR. The stage ends on the stamp "WE CHOOSE ArchR."

**Timing.** The new stage lasts 3 bars (6 s). Every scene after it plays 6 s later than in the tables below, so add 6 s to every time in those tables from "Stage 2: a black screen" onwards. There are now 8 stages and 8 pips, and the boss is stage 6. In `index.html` and `score.py`, the old scenes keep their original times and are offset as a whole (`SHIFT` in `renderFrame`, `OFF` in `score.py`). `timing.py` lists the final times: no hold is needed, and the cut lasts 94.0 s.

**Sound.** In stage 1, the failure buzz is replaced by:
- a blip when the size lands;
- eight rising blips while the extraction bar fills;
- a ding when the copy is safe on disk;
- two check blips, a second ding, and three blips for the partitions.

The new stage uses the same helpers:
- a short buzz on the loop and a drop on "SET ASIDE";
- a cursor blip, two check blips;
- a stamp on "WE CHOOSE ArchR.", then CLEAR!

The result screen has eight pip blips.

| On screen (new) | Source |
|---|---|
| FACTORY CARD, 48.8 GiB | `worklines/luna/plan_luna.md` Step 5.1 |
| Extract the whole card; our reference and our way back | `docs/03_r36-ultra-bring-up-story.md` Step 1 (l.17) |
| SAFE ON DISK, 42 GB compressed | `worklines/luna/plan_luna.md` Step 5.2: golden image `.img.zst`, 42,226,178,053 bytes, archived 2026-10-03 |
| Card read-only; verify identical byte for byte | `docs/03` Step 1 (l.19); Luna Step 5.2 (raw card and decompressed image have the same SHA-256) |
| EMUELEC, STORAGE, EEROMS (what is inside, to explore) | `worklines/luna/plan_luna.md` Step 5.1 (the card's partition labels) |
| The original card goes into a drawer, untouched | `docs/03` Step 1 (l.19) |
| Several community Linux systems exist for these clones | `docs/03` Step 2 (l.23) |
| Another system: its interface restarts in a loop; set aside | `docs/03` Step 2 (l.23) |
| ArchR, based on Arch Linux; looks the most like a normal Linux; already has a driver for the Wi-Fi chip | `docs/03` Step 2 (l.23) |

Removed: "COPY #1, 62 BYTES" and "Only an error message: the admin command had failed silently" (l.19). The stage-1 rows of the tables below describe the first cut.

## Concept

The bring-up is played as an **arcade game**. The R36 Ultra is "PLAYER 1". Its quest is to become a Linux computer we can log into. Each obstacle in the story is a **stage** with its own hit and a green **CLEAR!** stamp. A row of eight pips at the top right tracks progress (seven in the first cut). The invisible Wi-Fi chip is the **boss**: its hit-point bar breaks once for each of the three patches, and the chip fades in as it does. The router gets a stop-time scene of its own. The episode ends where the brief ends, on `ssh luna`. The title stamp "HELLO, LUNA" comes back there as the payoff. A "STORY 1 CLEAR" result screen then carries the lesson an engineer will recognise ("every error message pointed at the next problem").

## Structure (seconds of the final cut; no reading holds were needed)

| Time | Scene | Picture | Music (A minor, 120 BPM) |
|---|---|---|---|
| 0.0–5.0 | Title card | "TANSTAAFLLM · STORY 1", stamp "HELLO, LUNA", subtitle, PRESS START, moon | coin blips; stamp hit at 1.0; the trailer theme over Am F G |
| 5.0–12.0 | Player 1 | the handheld slides in; "R36 ULTRA", 3 stat rows, the quest | the groove starts; a new "Luna" tune; stat blips; sweep into the dissolve |
| 12.0–20.0 | Stage 1: save the original card | COPY #1 "62 BYTES" (fail) / COPY #2 checklist; CLEAR at 18.5 | failure buzz at 13.1, four rising check blips, a ding, CLEAR jingle |
| 20.0–28.0 | Stage 2: a black screen | black screen with "?", then Arch R Flasher; the screen lights at 25.0 | dark Dm/Am/E, thud at 20.6; a C-major stamp at 25.0; CLEAR at 26.5 |
| 28.0–34.0 | Stage 3: plug in a keyboard | hub ✗ (29.2) vs plain adapter ✓ (31.3); CLEAR at 32.4 | buzz, ding, CLEAR |
| 34.0–42.0 | Stage 4: find a terminal | CTRL ALT F2 → black (35.0); TEXT MODE (37.0) → prompt; QWERTY → AZERTY; CLEAR at 40.6 | three key clicks; the music drops to a ticking clock; stamp and groove back at 37.0 |
| 42.0–60.0 | Stage 5, the boss: the invisible Wi-Fi chip | red flash; interfaces "lo / wi-fi none"; pin-2 comparison (47.5); "LISTENING ON THE WIRE IT SHOULD BE DRIVING" (50.2); patches at 53.0, 54.8, 56.6; CLEAR at 58.2 | E-phrygian ostinato, double time, boss riff; a stamp on each patch climbing Am → F → G; an A-major victory at 58.2 |
| 60.0–68.0 | Stage 6: the router had a say | typed error "AP is in CSA process, reject auth" (red); AUTO struck, stamp "11" at 64.4; CONNECTED at 65.0; CLEAR at 66.5 | stop-time: typing ticks, an error buzz, a suspended wait (Dsus4); stamp, then C–G–Am groove |
| 68.0–76.0 | Stage 7: log in from the PC | key sent, SSH on; "$ ssh luna" typed on the PC (70.5–71.5); Enter, a signal travels, Luna shows a prompt (72.0); stamp "HELLO, LUNA." at 72.5 | build, key clicks, a rising bass; Enter; the trailer theme in full voice at 72.5 |
| 76.0–82.0 | Story 1 clear | "STORY 1 CLEAR", 7 green pips, the lesson | level-clear fanfare, seven pip blips, a quiet bed for reading |
| 82.0–88.0 | End card | chrome title from the key art, motto, github URL, byline, PRESS START, fade to black 87.5–88.0 | the trailer's end-card cadence; the A-minor chord fades out in 4-bit steps; PRESS START blinks |

## Every on-screen fact and its source

Line numbers refer to `bringup-pkg/story/03_r36-ultra-bring-up-story.md`.

| On screen | Source |
|---|---|
| "a cheap game handheld", "a Linux computer on Wi-Fi" | l.1, l.5 (small and inexpensive game handheld … little Linux computer reachable over Wi-Fi) |
| R36 ULTRA; SCREEN 720 × 720, SQUARE | l.11 |
| CHIP ROCKCHIP RK3326, ARM | l.11 |
| SHIPS WITH A GAMING SYSTEM ON microSD | l.11 |
| QUEST: a Linux computer we can log into; "not a game console: a computer to install things on and build upon" | l.13 |
| COPY #1: 62 BYTES, only an error message, the admin command failed silently | l.19 |
| COPY #2: right card?, read-only, copy, verify identical byte for byte | l.19 |
| The original card goes into a drawer, untouched | l.19 |
| ArchR (label under the handheld) | l.23 |
| First boot: nothing at all | l.27 |
| Clones use many different screens; ArchR needs a description of the right one | l.27 |
| Arch R Flasher builds it from the original card's hardware description file; the screen comes alive | l.27 |
| Multi-port USB-C hub: not even Caps Lock | l.33 |
| Plain USB-C to USB-A adapter: works straight away | l.34 |
| CTRL + ALT + F2 → a black screen; no login waits on the other terminals | l.38, l.45 |
| One boot line: TEXT MODE; an administrator shell on the screen; the prompt | l.43, l.45 |
| QWERTY → AZERTY, French layout built on the PC | l.47 |
| Network interfaces: lo (loopback) only, no Wi-Fi | l.51 |
| The driver is on the card, not running | l.51 |
| Linux sees the slot, nothing is in it; the chip is invisible | l.53 |
| Original card: pin 2 switches the chip on / ArchR (generic): pin 2 says whether a card is inserted | l.59–62 |
| Listening on the wire it should be driving; the chip was never switched on | l.64 |
| Patch 1, switch the chip on: the firmware uploads, then fails on some boots | l.70 |
| Patch 2, keep the clock running: one missing marker, then wlan0 appears | l.71 |
| Patch 3, the right doorbell wire: another wake-up pin, it sees the home network | l.72 |
| Stage title "The router had a say" | l.76 |
| "AP is in CSA process, reject auth" | l.80 |
| Linux thought the router was changing channels and politely refused to connect, indefinitely | l.80 |
| 2.4 GHz channel: AUTO → 11 | l.82 |
| Connected, an address on the home network | l.82 |
| The PC sends its public key over the network; then the SSH service is switched on | l.89 |
| `$ ssh luna` → a shell on the handheld | l.89 |
| Every error message pointed at the next problem | l.74, l.122 |
| Not every problem is on the device | l.123 |
| End card: motto, github.com/mdussere/tanstaafllm, byline | the trailer's end card (as asked by the author) |

Left out on purpose: the boot-looping system set aside (l.23); the password detour (l.88); and step 11, surviving a reboot (l.91–98), which comes after the first `ssh luna`. The brief ends there.

Staging is not a claim. The pixel handheld, hub, adapter, router, chip and monitor are icons, not photos. The "#" prompt is a generic shell sign, not a captured screen. The boss's hit points stand for the three patches, and the stage names are the story's step titles, shortened.

## Reading audit (`src/timing.py`)

This uses the trailer's model: 0.4 s to orient, then 0.30 s per Press Start 2P word and 0.25 s per VT323 word, with a minimum hold of 1.0 s. Holds are rounded up to 0.5 s beats, and a shortfall under 0.1 s is dropped. The timeline was written so that **no hold is needed** (`holds.json` is empty). That keeps every cut on the music as composed. One screen sits within the tolerance: on Player 1, the last line has 3.55 s against the 3.65 s needed, so the 0.10 s shortfall is dropped. In "total" mode the denser screens (stage 1, stage 2, and the boss) ask more than they get, as several trailer screens did. They are built so that the eye can follow the newest element at each step.

## Sound

- The chip is the trailer's `nes.py`, unchanged: an emulated 2A03 with 4 voices (2 pulses, triangle, noise), mono, no reverb, 60 Hz frames. The score is written with the trailer's helpers (`note`, `chord_arp`, `bass8`, `kick`, `snare`, `hit_all`, `coin`, `blip`, `ostinato`, `double_time`…). The tempo is 120 BPM, and the key is A minor.
- New material:
  - the "Luna" tune (Player 1);
  - stage-start arpeggios and the CLEAR! jingle (a coin, then a major arpeggio);
  - the failure buzz (a 12.5 % pulse sliding down, with a noise rasp) and the success ding;
  - the boss riff over the ostinato;
  - the router's stop-time wait;
  - the level-clear fanfare.
- `music.wav`: 88.00 s, 48 kHz, 16-bit, dual mono. Sample peak −1.1 dBFS (true peak −1.0 dBTP). **Integrated −15.3 LUFS, LRA 4.1 LU.** The trailer measures −15.6 LUFS. `hits.json` lists every scored hit.

## Shared with the trailer (series template for later episodes)

- **Renderer:** `index.html` keeps the trailer's head verbatim:
  - utilities (`txt`, `runs`, `box`, `flash`, `dissolve`, `check`);
  - backgrounds (`stars`, `sky`, `grid`, pixel `moon`);
  - key art (`artCover`, `titleLogo`, `face`) and the `device` sprite;
  - the scanline + vignette `POST` layer;
  - the `holds.json` mechanism, where ambient time keeps stars and blinks moving.
- **Palette:** the trailer's `C` tokens: navy/violet skies, amber for labels and emphasis, cyan for secondary lines, chrome for main text, red for failure, green for success.
- **Type:** Press Start 2P for capitals (28–44 px labels, 64–112 px stamps) and VT323 for sentences (48–56 px), with the same hard drop shadow.
- **Boxes:** the double-border RPG `box`.
- **Transitions:** a white flash on cuts and stamps, and the 60 px block dissolve.
- **Stamps:** scale-in with shake, on a music hit. Blinking PRESS START.
- **Reading:** the same `timing.py` model and holds.
- **Episode frame:**
  - **Open:** a black starfield with a moon rising, "TANSTAAFLLM · STORY n" in amber, then a big chrome stamp with the story title and a cyan VT323 subtitle.
  - **Close:** a "STORY n CLEAR" result, then the trailer's end card (logo, motto, URL, byline, PRESS START, fade).
- **Sound:** the same chip emulation, tempo and helpers. The trailer theme opens the episode and returns at the payoff. The end-card cadence and the fading A-minor chord are the trailer's.
- **Pipeline:** `capture.py` (Playwright frame capture piped to ffmpeg, H.264 CRF 16 + AAC 320k), `contact.py`, and the `build.sh` shape.

## Files

- `bringup.mp4`: the video.
- `music.wav`, `hits.json`: the soundtrack and its hit list.
- `stills/`: inspection stills. `contact_*.png`: contact sheets.
- `src/`: `index.html` (renderer), `capture.py`, `timing.py`, `holds.json`, `score.py`, `nes.py`, `contact.py`, `build.sh`, `fonts/`, `art/`.
- Rebuild: `src/build.sh`. It uses `uv run --project /home/michael/git/tanstfaafllm python`.
