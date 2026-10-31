# Notes: concept, structure, sources

## Concept

**"Insert coin": the project played as an arcade game in which every bit of intelligence costs coins.**
Heinlein's line becomes the game's rule. The video opens on an arcade cabinet's INSERT COIN screen, and "There ain't no such thing as a free lunch" is typed and then corrected to *LLM*. From there, it uses familiar retro-game screens: Luna's player stats, a price list, a character-select screen of the intelligences (cheapest first, each with a price meter), a boss fight against the 1-GiB wall, the cell's roster, and a speedrun of the bring-up. It ends on the project's doctrine and a PRESS START end card. The key art and its chrome title open and close the video. All the figures are real, and each one says where it was measured. The jokes are in the framing, never in the numbers.

Look: pixel fonts, a deep navy and violet palette with amber accents and cyan for what is live (the house diagram style from the principles page), hard drop shadows, faint scanlines, and pixel sprites drawn in code (the handheld, a microphone, a coin). Sound: an original 120-BPM chiptune in A minor, built from square, triangle and noise channels. Cuts fall on bar lines, and each stamp, blip and stage-clear jingle is placed on the same timeline as the picture.

## Structure (120 BPM, 1 bar = 2 s)

| Time | Scene | What happens |
|---|---|---|
| 0–4 s | Insert coin | A coin drops, and "THERE AIN'T NO SUCH THING AS A FREE LUNCH." is typed. LUNCH is struck out and "LLM" is stamped under it. Credit to Heinlein. Then a riser and a white flash. |
| 4–8 s | Key art | The key art resolves from big pixels as the music drops. "A conspiracy to turn a tiny, stubborn computer into a machine that runs itself… without pretending that any intelligence is free." |
| 8–16 s | Player 1: Luna | A pixel handheld flies in, and its stats appear on the beat. Then a mission box: "Make it autonomous… A lot to ask of a 30-euro console. That is the point." |
| 16–20 s | The price list | Three slams: every token costs time and money, every model costs memory, every daemon costs battery. "On Luna, nothing hides those prices." |
| 20–24 s | One word | `> pong` is typed to Claude Code, and a counter rolls to ≈17,700 input tokens, measured on luna-pi. Stamp: "NO FREE LLM." |
| 24–34 s | Select your intelligence | Four cards, cheapest first: Buttons, Mycroft, Mike, Mannie, each with a price meter. The cursor walks across them, and then a banner reads "The least sufficient intelligence wins." |
| 34–40 s | Boss fight: the 1-GiB wall | Claude Code's documented 4 GB minimum against Luna's 983 MiB. Then a segmented memory bar: 547 MiB left, Claude Code's 244 MiB peak fits, and adding Mike's ≈306 MiB puts it right at the limit. |
| 40–48 s | The cell | Six agent tiles (Professor, Wyoh, Mycroft, Mike, Mannie, Luna) and five rules stamped one per second. |
| 48–54 s | Speedrun | Six one-second "stages" of the bring-up, each a problem and its fix, with a little handheld hopping along the floor. |
| 54–57 s | Doctrine | Over the key art: "No free LLMs. No invisible masters. No surrender to the desktop." |
| 57–60 s | End card | The chrome title, the tagline, the GitHub URL, "A personal engineering project by Michael Dussere", and a blinking PRESS START. Fade out. |

## Facts and figures used, and where they come from

All the pages are in `package-20261025/story/`.

| On screen | Source |
|---|---|
| "There ain't no such thing as a free lunch" → free LLM; Heinlein, *The Moon Is a Harsh Mistress* | `00_README.md` (intro), `00_docs-index.md` |
| "A conspiracy to turn a tiny, stubborn computer into a machine that runs itself, without pretending that any intelligence is free." | `00_README.md`, opening quote |
| 4 × Cortex-A35 | `04_architecture.md` §1, `14_luna.md` hardware table |
| 983 MiB of RAM | `04_architecture.md` §1, `14_luna.md` |
| 720 × 720 screen | `00_docs-index.md`, `04_architecture.md` §1, `14_luna.md` |
| 17 buttons, 2 sticks | `04_architecture.md` §1, `14_luna.md` |
| 2.4 GHz Wi-Fi | `04_architecture.md` §1, `14_luna.md` |
| ≈ 30 € ("a 30-euro console") | `00_README.md` (The cause), `00_docs-index.md` |
| Mission: autonomous; listens, acts on its own desktop, maintains its own system; "That is the point." | `00_README.md`, The cause |
| Every token costs time and money / every model costs memory / every daemon costs battery / nothing hides those prices | `00_README.md`, The cause |
| "pong": ≈17,700 input tokens, almost all of it Claude Code's own prompt and tools, measured on luna-pi | `13_mannie.md`, cost table and "No free LLM" |
| Buttons: no model, 17.5 MiB, no CPU at rest, live on Luna | `04_architecture.md` §2; `10_wyoh.md` cost table |
| Mycroft: speech to text offline, corrected before sending; Kroko ≈160 MiB (luna-pi) | `11_mycroft.md`; `04_architecture.md` §3 (Kroko about 160 MiB) and `11_mycroft.md` table (159 MiB on luna-pi) |
| Mike: LFM2.5-350M, one request = one action, you accept or refuse | `12_mike.md`; `01_principles.md` |
| Mannie: Claude Code through the Tunnel; builds, repairs, operates; cost shown first | `00_README.md` (The dual brain); `13_mannie.md` |
| "The least sufficient intelligence wins. A rule beats a model. A small model beats a big one. The frontier is called when it is worth its price." | `00_README.md`, The dual brain |
| Claude Code's documented minimum is 4 GB of RAM; running on Luna is outside what is supported | `13_mannie.md`, under the cost table |
| ≈547 MiB available with the desktop and resident dictation, on Luna under Arch Linux ARM | `04_architecture.md` §3; `14_luna.md` status |
| Claude Code peak 244 MiB (luna-pi): fits | `04_architecture.md` §3; `13_mannie.md` |
| Mike ≈306 MiB lean (desk host): "right at the limit" | `04_architecture.md` §3 |
| "That trade-off, rather than raw speed, is what will shape the next decisions." | `04_architecture.md` §3 |
| The cell: one Claude Code session per part; the six members and their jobs | `00_README.md` (The cell), `15_the-cell.md`, `04_architecture.md` §4 |
| Rules: plans first; nothing built until the human says go; claims measured on the machine; notes, not chatter; everything written down | `00_README.md` (the cell's rules), `15_the-cell.md` |
| Bring-up: the first backup was a 62-byte file, then a verified byte-for-byte copy | `03_r36-ultra-bring-up-story.md`, Step 1 |
| Black screen → the right panel description, and "the screen came alive" | `03_…`, Step 3 |
| Invisible Wi-Fi chip → three hardware (device-tree) patches → `wlan0` | `03_…`, Steps 6–8 |
| The router "had a say": channel Auto → 11, connected | `03_…`, Step 9 |
| `ssh luna` | `03_…`, Step 10 |
| A gaming system that runs everything as root → new root: Arch Linux ARM | `14_luna.md`, appendix |
| "Sept – Oct 2026" | `03_…`, subtitle |
| "No free LLMs. No invisible masters. No surrender to the desktop." | `00_README.md`, last line |
| github.com/mdussere/tanstaafllm, Michael Dussere | `BRIEF.md` |

## Simplifications and choices to review

- **The character faces** are crops of the key art. I matched them as follows: the man with the wrench is Mannie, the novel's technician; the robot is Mike; the woman is Wyoh; the man with glasses and a headset is Professor. The art does not name its characters, so the author should confirm this matching. Mycroft and Luna use drawn icons (a microphone and the handheld) rather than a face.
- **"Price" meters** (0, 1, 2 and 4 pips) on the select screen are an illustration of the "cheapest first" order. They are not measurements.
- **The handheld sprite** is a stylised pixel drawing of a vertical handheld with a square screen, d-pad, ABXY and two sticks. It is not a faithful drawing of the R36 Ultra.
- **The speedrun** squeezes eleven bring-up steps into six beats, and the last stage (the move to Arch Linux ARM, 2026-10-25) comes from the Luna appendix rather than the bring-up story.
- **The memory bar** follows `04_architecture.md` §3 literally: 547 MiB available, + 244 MiB for Claude Code (luna-pi), + ≈306 MiB for Mike (desk host). The sum, 550 MiB, is shown as "right at the limit", which is the page's own phrase. Each figure carries the name of the machine it was measured on.

## Reading time (2026-10-30)

The first cut moved on as soon as the last line had appeared: the "LLM" stamp, the Heinlein credit and the boss-fight line were cut after 0.25–0.6 s. `src/timing.py` now lists, for every screen, the last text before the cut and how long it stays readable, and `src/holds.json` freezes the choreography just before the cut until that text could be read. The stars, the grid and the blinks keep moving during a hold.

Model: the viewer needs **0.4 s** to notice a new text and look at it, then **0.25 s per word** in VT323 mixed case and **0.30 s per word** in Press Start 2P capitals, and a screen never moves on less than **1.0 s** after its last text appeared. With these rules (`--mode last`), the holds add 31.6 s and the cut lasts 91.6 s. Requiring that *all* the text of each screen be readable (`--mode total`) would give 123.5 s.

Where the figures come from:
- **0.25 s per word:** the average adult silent reading rate is 238 words per minute for non-fiction (Brysbaert, *How many words do we read per minute?*, Journal of Memory and Language 109, 2019). Pixel capitals are slower to read than mixed case, so they get 20 % more; that factor is an assumption, not a measurement.
- **0.4 s to notice:** conscious access to a new stimulus ("ignition" in the global neuronal workspace, with the P3b wave) arrives about 0.3 s after it appears (Dehaene and colleagues), plus one eye movement.
- **1.0 s minimum:** subtitles stay at least 5/6 s on screen in Netflix's timed-text rules; a stamp also needs a beat to land.

The music is not yet adapted: the silent cut is for judging the pace first.
