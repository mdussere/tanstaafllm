# Result — the Slate and its on-screen keyboard on Luna

**Step:** Wyoh 6 (sub-steps 6.1–6.5), green-lit by the user on 2026-10-09 ("go")
**Proposal and decisions:** [`0600_01_slate-and-keyboard-proposal.md`](0600_01_slate-and-keyboard-proposal.md)
**Scope:** Luna, ArchR card, root session. Development-only.

## Outcome

The Slate replaces the one-line fuzzel zone:
- L1 opens a black multi-line editor at the top of the panel, with a white 2 px border, white text at half the old font size, and the AZERTY on-screen keyboard below it.
- L2 sends the text once into the window that had focus; L1 throws it away.
- Inside the Slate: A Return, B Backspace, X Delete, Y Shift (selection with the arrows), R1/R2 next/previous word. The whole cross pressed once selects or deselects the word under the cursor; pressed twice, the line.

The live scenario passed on Luna's panel and its screenshots were inspected (below).

**Still open:**
- **6.6 — the user's check on the physical controls.** In particular, it must show whether pressing the real cross as a whole is detected (see "Whole-cross press").
- ~~The full scenario against the final AZERTY build~~: done, see the addendum below.

## What was built

| File | Role |
| --- | --- |
| [`src/wyoh/wyoh_slate.py`](../../../src/wyoh/wyoh_slate.py) | The Slate, standard library only. A pure editor core (`Slate`), a decoder for foot's xterm input (`Decoder`), and a renderer (`render`, ANSI, no curses: ArchR has no terminfo). A raw-tty loop also reads commands (select word or line, send, discard) from the daemon's socket. The text is never written to disk or logged. |
| [`src/wyoh/wyoh_gamepad.py`](../../../src/wyoh/wyoh_gamepad.py) | Slate mode in the core: `zone_keys` (the user's mapping) and whole-cross detection (arrows wait 40 ms inside the Slate; two directions within that window are one whole-cross press; a second press within 0.4 s selects the line). The daemon now also: opens a private socket (`/run/wyoh/slate.sock`, mode 600); starts the Slate and the keyboard together; switches the focused border to white and back; places the Slate; delivers through `wtype` as before. The status file records `slate_ready`, `cross` and `delivered_length`, never the text. |
| [`deploy/luna/gamepad.toml`](../../../src/wyoh/deploy/luna/gamepad.toml), [`sway.conf`](../../../src/wyoh/deploy/luna/sway.conf), `status.sh` | The Slate command (foot, Liberation Mono 12 px, 716 × 214, `resize-by-cells=no`), the keyboard command, border colours, a floating rule, and the bar hint "L1 Slate" |
| [`src/wyoh/wvkbd/`](../../../src/wyoh/wvkbd/) | `keys_simple.luna.h` (AZERTY letters with é è à ç) and `build_wvkbd_luna.sh` (Debian's wvkbd 0.15 source, checked against `wvkbd_0.15-1.dsc`, built on `luna-pi`) |
| `wyoh_virtual_input.py`, `wyoh_mcp_server.py` | `<` and `>` on the virtual AZERTY keyboard; a `repeat` option on the development tap tool, so a double press fits in one call |

### Deployed, not committed

| Item | Provenance | SHA-256 |
| --- | --- | --- |
| `wvkbd-luna` in `/storage/.local/opt/wyoh-tools/bin/` | `build_wvkbd_luna.sh` on `luna-pi` (Debian 13 arm64, glibc 2.41), AZERTY layer and `luna-cursors.patch`. It needs only GLIBC ≤ 2.34; Luna has 2.40. | `6bd6c67e…022cd0` (the earlier AZERTY-only build was `1104cbbe…90065b`) |
| `wvkbd-mobintl` (stock, used for the first passing run, no longer configured) | Debian `wvkbd_0.15-1+b1_arm64.deb` (`3600d626…347ad8`) | `8c5c2e0f…e9db6` |

## Evidence

| Check | Command | Result |
| --- | --- | --- |
| Slate core and gamepad core | `uv run pytest test/wyoh/test_wyoh_slate.py test/wyoh/test_wyoh_gamepad.py` | 107 passed |
| Live scenario, stock wvkbd (QWERTY) | `WYOH_LUNA_LIVE=1 uv run pytest -m live test/wyoh/test_luna_slate.py` | 1 passed in 141 s, `results/wyoh/luna-slate/20261008T232237Z/` |

The contract is [`luna_slate.feature`](../../../test/wyoh/luna_slate.feature). The scenario drives the person through MCP development tools only. Every effect on text is proven by a marker file that the receiving terminal writes. All 20 settled screenshots were inspected, along with `overview.png`:

| Steps | Seen |
| --- | --- |
| 01 | Black Slate under the bar, white border, hint "L2 send · L1 discard · 1 line"; keyboard on the bottom 240 px, black keys outlined in white |
| 02–03 | Two lines typed, hint "2 lines" → L2: Slate and keyboard gone, blue border back; the terminal ran both lines once (`M` = `first\nsecond\n`) |
| 04–06 | Two lines → L1: nothing reached the terminal, and `D` does not exist |
| 07–10 | Cursor moved into "brave"; the whole cross selected it (reverse video); B deleted it; `W` = `hello world` |
| 11–13 | Y + ← ×4 selected "drop"; B deleted it; `S` = `keep` |
| 14–16 | R2, "b", R1, "d" gave `echo bcd`; `R` = `bcd` |
| 17–20 | Whole cross twice selected "junk line"; X deleted it; the stick and R3 clicked `a`, `a`, `⌫` on the keyboard; `K` = `a` |

The test also asserts that no typed word ever appears in the status file.

An earlier run of the same scenario, `20261008T231819Z`, also passed. Its screenshots showed the Slate shifted by a few pixels with a strip of the terminal behind it, which led to the size fixes under Findings.

## Cost

Measured on Luna while open, with the AZERTY build.

| Process | RSS | Budget (proposal) |
| --- | --- | --- |
| Slate window (`foot`) | 7.4 MB | |
| Slate editor (Python) | 14.9 MB | |
| Slate total | 22.3 MB | ≤ 20 MiB, **over by about 1.3 MiB** |
| Keyboard (`wvkbd-luna`) | 13.0 MB | ≤ 10 MiB, **over by about 2.4 MiB** |
| Gamepad daemon | 18.1 MB | ≤ 20 MiB ✓ |

- When closed, the Slate and keyboard processes are gone and cost nothing.
- While idle and open, foot and wvkbd used 0 CPU ticks in 10 s.
- The two overruns are recorded, not hidden. Ways to cut them, if wanted:
  - Python's footprint, for example by not importing `unicodedata`;
  - keeping wvkbd resident and hidden instead of starting it each time (that trades memory at rest for start-up time).

## Findings

1. **wvkbd picks its landscape mode on Luna's square panel** and then uses its landscape layer at the landscape height (120 px). Both landscape options are now set to the same layers and height.
2. **Sway resizing the Slate raced with foot's own size.** The result was sometimes a smaller surface centred in a larger frame, with the terminal showing behind. foot now sizes the window itself (`--window-size-pixels`, `resize-by-cells=no`, otherwise it rounds to whole cells), and Sway only positions it. Sway's `move position` counts from the workspace area, below the bar.
3. **The daemon must write its status when the Slate connects.** Otherwise `slate_ready` stays stale until the next event.
4. **The stock Debian wvkbd is QWERTY.** Its layouts are compiled in, and Luna has no compiler, so Wyoh builds `wvkbd-luna` on `luna-pi`.
5. **The test's virtual gamepad can take up to about 17 s to attach** after a daemon restart: the daemon rescans every 5 s and the MCP server starts slowly on Luna. The scenario now allows 30 s for that step only.

## Whole-cross press (not yet calibrated)

The device tree has no centre button on the cross. Detection assumes that pressing the whole cross reports two directions within 40 ms; in simulation, the virtual gamepad presses them 20 ms apart. Whether the physical cross does this is unknown.

To check it: open the Slate, type a word, press the cross as a whole, and see whether the word is highlighted. The daemon's `cross` counter in `/run/wyoh/gamepad.json` also counts each detected press. If presses are missed, the window (`cross_window_s`) can be widened in `gamepad.toml`. If the hardware never reports a whole-cross press, the step stops there, as the proposal says.

## Addendum (2026-10-09): two-thumb typing (6.8, user request)

**Request:** "Left joystick moves the green selection on the keyboard like arrows; clicking the joystick adds the letter to the Slate. The right joystick acts the same way with the red selection, so we can tap with two fingers. Use pastel colours."

**Built:**
- **[`src/wyoh/wvkbd/luna-cursors.patch`](../../../src/wyoh/wvkbd/luna-cursors.patch)** (wvkbd 0.15, applied by the build script):
  - `--cursors` draws two key selections, pastel green `#b8e6b8` and pastel red `#f5b5b5`, with dark text `#1e1e1e`. When both are on one key, it is split green and red.
  - Commands on standard input, one per line: `move <0|1> <up|down|left|right>` and `press <0|1>`.
  - Up and down go to the nearest row, then the key closest horizontally.
  - A selection survives layer and Shift switches.
  - Start positions are set with `--home0`/`--home1`: green on f, red on j.
- **Gamepad core**, while the Slate is open:
  - the left stick steps green and the right stick steps red;
  - a push past half deflection is one step; held, it repeats after 0.3 s every 0.12 s; below 0.35 it is let go;
  - L3 and R3 type the green and red keys;
  - the pointer is off.

  Outside the Slate, the right stick is the pointer again. The daemon writes the commands to the keyboard's standard input.
- 17 new core tests: 124 Slate and gamepad tests pass.

**Live evidence:** `WYOH_LUNA_LIVE=1 uv run pytest -m live test/wyoh/test_luna_slate.py` passed in 109 s with the final build: `results/wyoh/luna-slate/20261009T155843Z/`. All 22 frames and `overview.png` were inspected.
- Steps 01–18 match the table above.
- **19:** green on f, red on j, at every Slate opening.
- **20:** green steered f → q → a and typed it twice ("echo aa"); red steered j → n → ⌫.
- **21:** R3 on ⌫, then red back to é and R3: "echo aé".
- **22:** the terminal ran `echo aé > …-K`; `K` = `aé`, so the code-point key works through the selection too.

**A failed run, recorded:** the first run with this build (`20261008T234120Z`) stopped at step 10. Its frames show letters inserted into typed text and both selections moved away from f and j, although the scenario had not touched the sticks or L3/R3 yet.
- 20 s of observation with nothing running showed no spontaneous activity.
- The next run passed, and the daemon's counters showed that someone had used the Slate in between.
- The most likely cause is a person on the real gamepad during the run. A fault cannot be excluded until the user's physical check (6.6): the real sticks have not been seen at rest by the daemon.
