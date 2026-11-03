# Camp Currie — design and stack for the first shell (Step 1)

> **Freshness:** 🟢 current · **Written:** 2026-11-02 · **Checked:** 2026-11-02 · **Step:** Camp Currie 1

This record designs the first playable shell without speech (Steps 2–3) and chooses its stack. It replaces Codex's Step 1 study, which is archived out of Git in `tmp/camp-currie-codex-20261101/`.

## 1. Learner journey and screens (1.1)

Every screen is 720×720. The game reads only three kinds of key, which Wyoh's gamepad daemon will produce from Luna's buttons:

| Key | Luna button (Wyoh `keys` profile, later) | Meaning |
|---|---|---|
| ↑ ↓ | D-pad | move in a menu |
| Return | A | confirm, continue, transmit |
| Escape | B | back |

| Screen | What it shows | Keys |
|---|---|---|
| **Title** | Starfield and the Moon's limb; "CAMP CURRIE", "L-CAT · Lunar Communication Assessment Training"; a blinking "PRESS A". | A → Missions |
| **Missions** | "STAGE SELECT". Three mission panels: *Meet the Crew* (open), *Talk to the Crew* and *Command Center* (locked, "needs speech, later"). | ↑↓ choose · A open (a locked one shows why) · B → Title |
| **Briefing** | Professor's portrait and a dialogue box: the task, five contacts, simulated results. | A → first contact · B → Missions |
| **Contact** | "STAGE 1 · CONTACT n/5", five signal lights, the crew member's portrait and name card, and a dialogue box: their line, the target word in large type, and a pronunciation hint. | A → Your turn · B → Missions |
| **Your turn** | A crossed-out microphone with "NO MICROPHONE · SIMULATED", the target again, and the options TRANSMIT / LISTEN AGAIN. | ↑↓ choose · A: transmit, or back to the prompt · B → Contact |
| **Result** | **success:** a green "CLEAR!", the crew member's reply, one more light lit. **retry:** "TRY AGAIN" with the simulated reason. **uncertain:** "NOT SURE", with "this is not a mark against you". | A → next contact, Debrief, or Your turn again |
| **Debrief** | "STAGE 1 CLEAR!", contacts 5/5, attempts, retries and uncertain results, and "Simulated results — not a pronunciation score". | A → Missions |

**Timing:** no screen times out, and the learner always moves on with A. The only animations are the blinking prompt, the stars and the "CLEAR!" stamp, and none of them blocks input.

**Error states:** a locked mission explains itself. Escape always goes back one level and never loses progress inside the mission, except when leaving it to Missions, which restarts it.

## 2. Simulated evaluator contract (1.2)

```python
class Evaluator(Protocol):
    def evaluate(self, target: str, attempt: int) -> Outcome: ...

@dataclass(frozen=True)
class Outcome:
    kind: Literal["success", "retry", "uncertain"]
    reason: str          # one sentence shown to the learner
```

- **Steps 2–3** use `ScriptedEvaluator(script)`. It returns the script's outcomes in order and starts again at the end. The default script, `success, retry, success, uncertain, success, success, success`, shows all three outcomes in one run. Tests pass their own scripts.
- **Every result says it is simulated.** The reasons are honest: "Simulated check: matched", "Simulated check: heard another word", "Simulated check: could not decide".
- **Replacement boundary:** a Step 4 speech evaluator implements the same `evaluate`. It receives the target and returns the same three kinds; capture and models stay behind it. Scenes, progress and tests do not change.
- **Uncertain is never a failure.** It does not count as a retry in the debrief, which follows Adam's rule against judging an accent from an ASR mistake.

## 3. Visual direction (1.3)

**Adam, 2026-11-02:**
- "look at the videos' rendering: that is the kind of rendering we want";
- then: "don't stick to the videos' examples; it must fit the game's dynamics; take examples from reference games".

So the series gives the palette, the type and the cast (stills in `worklines/hazel/video/library/T06-two-boxes`, `T11-boss-fight`, `T15-roster`), and the screens borrow their mechanics from games whose loop matches ours: a call comes in, you answer it, you get feedback, you move on.

| Our screen | Borrowed mechanic | From |
|---|---|---|
| Contact (a crew member calls) | an incoming radio call: portrait in a comm frame, the speaker's name, signal bars, text typed out letter by letter | Star Fox 64 comm calls; Metal Gear Solid's Codec |
| Your turn | a "transmit" moment with a big, unmistakable state (microphone, level meter), then a beat before the verdict | Codec "send"; Rhythm Heaven's call and response |
| Result | a stamp that slams in and tilts ("CLEAR!", "TRY AGAIN", "NOT SURE"), with a short shake; the crew member answers in character | Ace Attorney's "OBJECTION!" stamps; Duolingo's immediate correct/incorrect banner |
| Missions | a small map of nodes on the Moon, one lit and the others locked, with a cursor that moves between them | Super Mario World's overworld; FTL's sector map |
| Progress | five signal lights in the header, one lit per cleared contact, and a streak | Duolingo's progress bar |
| Debrief | a results screen: rank letter (S/A/B), hits, retries, "uncertain" counted apart | Star Fox 64 and F-Zero mission results |

- **Background:** a vertical gradient from navy `#0b1026` to violet `#2a1650`, with small white and amber stars. It is drawn once, then reused.
- **Type:**
  - Press Start 2P for titles (24–40 px) and labels (16 px);
  - VT323 for body text, at least 30 px, so it reads at arm's length on a 720 px panel (body sizes as in the Story 2 video).
- **Colours:** amber `#f2a93b` for stage labels and the selection; white `#e8eef6` for headlines; cyan `#4fd8e8` for hints and system lines; green `#5be37d` for "CLEAR!"; coral `#e8605a` for "TRY AGAIN".
- **Panels:** 3 px borders, violet `#6b5fa8`, or amber when selected, on a slightly lighter navy fill.
- **Portraits:** (provenance)
  - cropped once from the series' key art (`worklines/hazel/video/story2-ask-the-desktop/src/art/wallpaper.png`) into `src/camp-currie/assets/portraits/` by `src/camp-currie/tools/make_portraits.py`: Mannie, Wyoh, Mike, Professor, and the Moon for Luna;
  - Mycroft has no face in the key art, so the game draws its microphone, as the video roster does.
- **Provenance:** the key art is the project's own image (`docs/`, Hazel's videos). The fonts are SIL OFL 1.1, copied with their licence files from Hazel's video sources. Hazel's sources are not modified.

## 4. Stack (1.4)

**Python 3 + pygame-ce 2.5.6 (SDL 2.32), software rendering into one 720×720 surface.**

| Measure (a 720×720 window, 60 frames with text) | Peak RSS (VmHWM) |
|---|---|
| Termidor, x86_64, Python 3.12, SDL dummy driver | 30.4 MiB |
| `luna-pi`, aarch64, Python 3.13, pip wheel, SDL dummy driver | 28.3 MiB |
| Luna | not measured (needs Mannie's agreement and a slot) |

**Why:**
- The repository's tools are already Python, and so is Wyoh's own code.
- SDL2 is what Luna's games already use.
- pygame-ce ships aarch64 wheels, so it installs in a user venv without a system package.
- The core is plain Python, so it is tested without a display.

**Memory (Adam, 2026-11-02):** "it must stay small, but 50 MiB is not a problem". Every run reports its peak RSS; optimisation comes once the look is right.

**Rejected:**
- C with a hand-made Wayland client: far more code, for a gain Adam does not need.
- A browser: too heavy.
- raylib: there is no Python binding as light as pygame-ce, and it brings nothing over SDL2 here.

## 5. Tests and evidence (1.5)

- **Core:** pure tests of every scene transition, of the evaluator script and of a full mission; no display.
- **Rendering:** the SDL dummy video driver renders each screen to PNG under `results/camp-currie/shell/<timestamp>/`, and every PNG is inspected before any claim. A `.feature` file next to the test holds the readable scenarios.
- **Agent protocol:** with `python -m camp_currie --agent`, each stdin line names an action (`up`, `down`, `confirm`, `back`, or `shot <path>`), and each stdout line is the JSON state: scene, contact, target, options, cursor, progress, last outcome, available actions and `rss_kib`. Tests drive the real program through it, the same way an agent would.
- **Memory:** the peak RSS after a full mission, on Termidor and on `luna-pi`, goes in the Steps 2–3 record.
