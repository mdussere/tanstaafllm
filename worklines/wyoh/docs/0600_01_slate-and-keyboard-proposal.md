# Proposal — Slate (multi-line input) and the backup on-screen keyboard

> **User decisions recorded 2026-10-09** (section 10): name Slate; Slate controls (A Return, B Backspace, X Delete, Y Shift for selection, cross pressed as a whole selects the word, twice selects the line); keyboard shown whenever the Slate is open; black-and-white look with a half-size font; no discard confirmation. Sections 3, 5 and 6 follow these decisions; points still open are marked ❓.

**Step:** Wyoh 6 (proposal; nothing is green-lit)
**Date:** 2026-10-09
**Question answered:** what replaces the one-line input zone, how the backup keyboard fits below it, and what must be decided before any code.
**Sources:**
- user requests (2026-10-09): "the text input widget (find a name for it, make proposals) must be multilines. I must also have a virtual keyboard usable below it that can be used for backup (ex: for password)";
- the user's ChatGPT discussion ([raw export](0500_02_input-widget-discussion-raw.md));
- the Step 5 result ([0506_01](0506_01_buttons-only-result.md)).

## 1. What the ChatGPT discussion establishes, and what it doesn't

| Point | Status |
| --- | --- |
| **wvkbd** as the keyboard: a minimal C Wayland keyboard for wlroots, no GTK | Checked against the upstream README (2026-10-09). Dependencies are Cairo, Pango, wayland-client and xkbcommon. SIGUSR1 hides it, SIGUSR2 shows it, SIGRTMIN toggles it. Layouts are compiled in (`make LAYOUT=…`), and `-l` picks the layers. `-o` echoes the keys to standard output. |
| Squeekboard rejected (GTK3/Rust) | Consistent with the user's no-GTK decision. |
| Driving wvkbd with the D-pad, through a fork | ChatGPT's idea, untested. The stock wvkbd has no focused-key highlight. |
| wvkbd size (≈1,300-line `main.c`, ≈793 kB installed) | Not checked. Measure it on Luna. |
| An ArchR package for wvkbd | Unknown. ArchR has no usable package source for Wyoh; fuzzel came from a Debian arm64 build. |
| **A multi-line widget** | **Not addressed.** fuzzel's prompt is one line, so the zone has to be replaced in any case. |
| A name for the widget | Not addressed. |

ChatGPT's view of the repository was out of date (the recent commits were not pushed), so it says nothing about the current code.

## 2. Name

**Slate** (recommended): a small board you write on, wipe and rewrite, then hand over. It's the place where Wyoh prepares text before the system receives it; Mycroft will later fill it by voice. The name is descriptive, following the rule that the novel's vocabulary stays secondary to clear technical behaviour.

Alternative in the novel's vocabulary: **Hazel**, after Hazel Meade, who runs the children carrying messages between cells, like this widget carrying text to its target. Rejected: **Draft** (bland, close to Mycroft's "composition"), **Pad** (clashes with "gamepad").

**Decision (user, 2026-10-09): Slate.**

## 3. Screen layout (720 × 720)

```
┌──────────────────────────────── bar (22 px) ┐
│ Slate — L2 send · L1 discard                │
│ ┌─────────────────────────────────────────┐ │
│ │ first line of text                      │ │  Slate: floating, top,
│ │ second line_                            │ │  about 6–8 lines
│ └─────────────────────────────────────────┘ │
│        (target window, still visible)       │
├─────────────────────────────────────────────┤
│ a z e r t y u i o p                         │  wvkbd: bottom edge,
│  q s d f g h j k l m                        │  about 240 px, AZERTY,
│ ⇧ w x c v b n , ⌫                           │  layers: letters /
│ 123   space     ⏎                           │  digits+symbols
└─────────────────────────────────────────────┘
```

- The Slate is a floating window, so the four-tile policy ignores it (`wyoh_layout.py` counts tiled windows only).
- The keyboard is a layer-shell surface at the bottom edge. It doesn't take keyboard focus: it types into whatever has the focus, which is the Slate while it's open.
- **Decision (user, 2026-10-09): the keyboard is shown whenever the Slate is open**, at least for now. L1 opens both, and L2 or L1 closes both. There is no separate toggle.

### Look (user decision, 2026-10-09)

| Part | Look | How |
| --- | --- | --- |
| Slate | Black background, white text, **white 2 px border** | foot colours: background `000000`, foreground `ffffff`. Sway colours the focused window's border with one global colour (`client.focused`, currently blue `#5294e2`); the Slate always has the focus while open, so the daemon switches that colour to white when it opens the Slate and back when it closes it. |
| Slate font | **Half the size of the current zone font** (fuzzel, Liberation Sans 12) | The zone's rendered glyph height is measured on a panel screenshot, and the Slate uses half of it as a pixel size (foot `pixelsize=`). The user checks it is still readable on the panel. |
| Keyboard | Same look: black keys, white labels, white 2 px outlines | wvkbd's colours and font are options (to check in 6.1). If it can't draw a 2 px outline, set a white background with black keys so the gaps between keys look like borders; otherwise a small patch. |
| Keyboard font | **Fits the screen width**: the longest row fills 720 px | Size derived from the number of keys on the widest row; checked on a screenshot. |

## 4. Building Slate

| Option | Cost | Verdict |
| --- | --- | --- |
| **A. Python editor (standard library, `curses`) in a floating `foot` window** | foot is already deployed (about 15 MB with a terminal app). Python is already on Luna for the daemon. The editor core is pure, so it can be tested offline. | **Recommended.** |
| B. SDL2 window | A new dependency and a graphics stack, plus more code for text and fonts. | Kept for later only if A looks or feels wrong on the panel. |
| C. Keep fuzzel and add line breaks | fuzzel has no multi-line prompt. | Rejected. |

The daemon keeps everything it owns in Step 5:
- capturing the target window (`con_id`) when the Slate opens;
- refocusing that target and delivering the text with `wtype`;
- the status file;
- the guarantees: text is delivered once, and discarding sends nothing.

Only the editing surface changes. The Slate and the daemon talk over a private pipe or socket, not over Sway.

## 5. Controls (user decisions, 2026-10-09)

When the Slate is closed, nothing changes from Step 5.

When the Slate is open:

| Control | Action |
| --- | --- |
| L1 | Discard and close, **with no confirmation** (user decision) |
| L2 | Send to the target, then close |
| D-pad | Move the cursor (←↑→↓) |
| **A** | **Return** (new line) |
| **B** | **Backspace** (B no longer discards inside the Slate; only L1 does) |
| **X** | **Delete** |
| **Y (held)** | **Shift:** Y plus the arrows extends the selection |
| **Cross pressed as a whole, once** | Select the word under the cursor, or deselect it if it's already selected |
| **Cross pressed as a whole, twice (quickly)** | Select the line |
| **R1 / R2** | **Next / previous word** (user, 2026-10-09) |
| Right stick + R3 | Pointer and click, unchanged; keyboard keys are clicked this way |

With a selection, typing replaces it, B or X deletes it, and moving without Y clears it, as in a desktop editor.

### Pressing the cross as a whole

The device tree lists no separate centre button: the cross reports four directions only (`BTN_DPAD_UP/DOWN/LEFT/RIGHT`).

**Hypothesis:** pressing the whole cross reports two or more directions at once, including opposite ones (up with down, or left with right), which never happens when the cross is used normally.

**Calibration (6.1):** record the events with `evtest` while the user presses the whole cross with the panel in view, then set the rule. For example: opposite directions within about 40 ms count as one press, and a second press within about 400 ms selects the line.

**Consequence:** inside the Slate, the core holds back a direction for that short window before sending the arrow, so a whole-cross press doesn't also move the cursor. Outside the Slate, arrows stay immediate.

If the hardware doesn't report a whole-cross press distinctly, the step stops, the evidence is recorded, and another control is proposed to the user.

### Using wvkbd without a touchscreen

| Stage | How a key is pressed | Cost |
| --- | --- | --- |
| **V0 (stock wvkbd)** | Right-stick pointer, then R3 | Nothing to build. Slow, but acceptable as a backup. |
| V1 (only if V0 proves too slow during the user check) | A "keyboard mode" in the daemon: the D-pad moves a highlighted key, A presses it, B leaves the mode | A small wvkbd patch (highlight plus a command to press the focused key) to maintain as a fork. Decided after V0, not before. |

## 6. Passwords and privacy

- **Since the keyboard only shows with the Slate, a password is typed in the Slate and sent like any other text:**
  - It passes through the daemon's memory only, on its way to `wtype`.
  - The Slate's text is never written to disk: no history. The status file records only the state and length, never the text. Logs record lengths only.
- **The Slate shows the password in plain text on the panel.** ❓ A masked mode (`••••`) is left for Step 7 (Wi-Fi passwords) or for when the user asks for it.
- Test evidence must never contain a real secret. Tests use dummy values only.

## 7. Risks

- **Several lines sent to a terminal:** `wtype` types a newline as Return, so a shell runs each line as it arrives. Proposal: the Slate sends Return between lines (the plain behaviour), shows the line count before sending, and warns in its hint when the target is a terminal. Bracketed paste would need the clipboard (`wl-copy`), which is not deployed; that stays a later option.
- **Whole-cross detection** depends on what the hardware reports (section 5); it's calibrated first and can stop the step.
- **Selection in the target:** the Slate edits its own text, so selection is Slate-only; it doesn't select text in the target application.
- **Two keymaps:** wvkbd uploads its own keymap through the virtual-keyboard protocol, while Sway uses `xkb fr`. Accented letters and AZERTY symbols must be checked on Luna in 6.1.
- **Screen space:** with the Slate open, 720 px leaves about 450 px for the Slate and the target together. A short keyboard (4 rows, about 240 px) is part of the Luna layout.
- **Small font:** half of the zone's size may be hard to read on the panel; the user's check decides.
- **wvkbd provenance:** it must be built for aarch64, or a Debian arm64 build taken with recorded versions and checksums, as with fuzzel. No ArchR package is assumed.

## 8. Budget

| Part | Target |
| --- | --- |
| Slate (foot + Python editor) | ≤ 20 MiB RSS while open, 0 when closed |
| wvkbd | ≤ 10 MiB RSS, resident and hidden, 0 CPU while hidden (to measure) |
| Daemon | Unchanged (about 17.5 MB) |

## 9. Tests

- **Deterministic:**
  - the Slate editor core: insert, Return, Backspace, Delete, cursor, line wrap, Shift selection, word toggle, line select, typing over a selection, empty send;
  - whole-cross detection with timing (once, twice, a normal direction, two adjacent directions), in the gamepad core;
  - the new daemon states and the config.
- **Live, Gherkin + pytest, MCP person, inspected screenshots:**
  - open the Slate on a terminal, write two lines, send, and check a marker file proves each line ran once;
  - discard a multi-line text, nothing arrives;
  - the keyboard appears with the Slate and disappears with it;
  - click `a`, `1` and Backspace on the keyboard with the stick, and check the Slate received exactly that;
  - select a word and a line with the cross, delete the selection;
  - a dummy password sent through the Slate leaves nothing in the status file, logs or results;
  - the look: black Slate with a white 2 px border, white half-size text, keyboard fitting 720 px; focused tiles get back their blue border after the Slate closes.
- **The user's check** on the panel: readability of the half-size font, the whole-cross press, and V0 (pointer clicks) against V1 (D-pad on the keyboard).

## 10. Decisions (user, 2026-10-09)

1. Name: **Slate**.
2. Inside the Slate:
   - A = Return, B = Backspace, X = Delete, Y = Shift (selection with the arrows);
   - pressing the cross as a whole selects or deselects the word under the cursor; pressing it twice selects the line.
3. **The keyboard is shown whenever the Slate is open** (at least for now; no separate toggle).
   - The Slate is black with a white 2 px border and white text, in a font half the current size.
   - The keyboard has the same look, with its font adapted to the screen width.
4. No confirmation before discarding: L1 discards at once.

5. R1/R2 in the Slate: next/previous word (yes).

Still open: a masked mode for passwords (Step 7).

Step 6 was green-lit the same day; the result is in [`0605_01_slate-result.md`](0605_01_slate-result.md).
