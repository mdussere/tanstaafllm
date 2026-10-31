# Luna controls reference

**Step:** Wyoh 5.12 (green-lit by Professor on the user's behalf, D4, 2026-10-09)
**Question answered:** what every physical control of the R36 Ultra does in each mode of the Wyoh session, as the code defines it today.
**Source of truth:** `wyoh_gamepad.Config` and `deploy/luna/gamepad.toml`. `test/wyoh/test_luna_controls_reference.py` fails when this document and the code disagree.
**Supersedes:** the mapping table in Step 5 of `plan_wyoh.md` and the mapping in [`0500_01`](0500_01_gamepad-input-intent.md). Both still say "left stick = pointer, L1 opens or discards, L2 validates"; that is no longer true.
**Visual version (French):** [`0609_01_luna-cheat-sheet.svg`](0609_01_luna-cheat-sheet.svg).

**Live on Luna** means deployed and seen working in a live scenario. **Core only** means implemented and tested offline but not yet deployed. Since 2026-10-11, 6.9's keys are live (Slate scenario `20261011T104403Z`).

## Physical controls

Codes come from Luna's device tree (Step 5.1).

| Control | evdev code |
| --- | --- |
| Cross (D-pad) | `BTN_DPAD_UP`, `BTN_DPAD_DOWN`, `BTN_DPAD_LEFT`, `BTN_DPAD_RIGHT` |
| A, B, X, Y | `BTN_EAST`, `BTN_SOUTH`, `BTN_NORTH`, `BTN_WEST` |
| L1, L2, R1, R2 | `BTN_TL`, `BTN_TL2`, `BTN_TR`, `BTN_TR2` |
| Select, Start, FN | `BTN_SELECT`, `BTN_START`, `BTN_MODE` |
| Left stick and its click (L3) | `ABS_X`, `ABS_Y`, `BTN_THUMBL` |
| Right stick and its click (R3) | `ABS_RX`, `ABS_RY`, `BTN_THUMBR` |

## Desktop (no Slate shown)

| Control | evdev | Effect | State |
| --- | --- | --- | --- |
| Cross | `BTN_DPAD_*` | Arrow keys `KEY_UP`/`KEY_DOWN`/`KEY_LEFT`/`KEY_RIGHT`. Held, the key repeats (Wayland's key repeat) | live |
| A | `BTN_EAST` | `KEY_ENTER` | live |
| B | `BTN_SOUTH` | `KEY_ESC` | live |
| X | `BTN_NORTH` | `KEY_DELETE` | live |
| Y | `BTN_WEST` | `KEY_BACKSPACE` | live |
| R1 | `BTN_TR` | `KEY_TAB` (next field) | live |
| R2 | `BTN_TR2` | `KEY_LEFTSHIFT+KEY_TAB` (previous field) | live |
| L1 | `BTN_TL` | Slate: open, or show it again if hidden. Since 2026-10-15 the Slate is opened hidden when the session starts (`zone_preload`), so L1 shows it and Kroko is already loading or loaded | live (open); core only (show, preload) |
| L2 | `BTN_TL2` | Slate straight into dictation: opens it (or shows it again) and starts listening (`open`/`show`, then `dictate`). L1 opens it for the keyboard | core only (2026-10-15) |
| Start | `BTN_START` | Application menu (fuzzel). Pressed again while the menu is open, it closes the menu | live |
| Select | `BTN_SELECT` | Sway `focus next` (next window) | live |
| Right stick | `ABS_RX`/`ABS_RY` | Pointer: speed grows with deflection; dead zone 0.12 | live |
| R3 | `BTN_THUMBR` | Left click | live |
| Left stick, L3 | `ABS_X`/`ABS_Y`, `BTN_THUMBL` | Nothing | live |

## With FN held (desktop)

| Control | evdev | Effect | State |
| --- | --- | --- | --- |
| FN + Cross | `BTN_MODE` + `BTN_DPAD_*` | Sway `focus up`/`focus down`/`focus left`/`focus right` | live |
| FN + A | `BTN_MODE` + `BTN_EAST` | Sway `fullscreen toggle` | live |
| FN + B | `BTN_MODE` + `BTN_SOUTH` | Sway `kill` (close the window) | live |
| FN + R1 | `BTN_MODE` + `BTN_TR` | Sway `workspace next` | live |
| FN + R2 | `BTN_MODE` + `BTN_TR2` | Sway `workspace prev` | live |
| FN + Start, held 2 s | `BTN_MODE` + `BTN_START` | **Recovery**: releases every key held, closes the Slate, takes the gamepad back from a game | live |

## Slate shown

| Control | evdev | Effect | State |
| --- | --- | --- | --- |
| Cross | `BTN_DPAD_*` | Moves the cursor (`KEY_UP`…). Each arrow waits 40 ms (`cross_window_s`) to tell it from a whole-cross press | live |
| Whole cross, once | two `BTN_DPAD_*` within 40 ms | Selects the word under the cursor, or deselects (`select-word`) | live in simulation; the real cross is not calibrated (6.6) |
| Whole cross, twice | the same within 0.4 s (`cross_double_s`) | Selects the line (`select-line`) | as above |
| A | `BTN_EAST` | `KEY_ENTER`: new line | live |
| B | `BTN_SOUTH` | `KEY_BACKSPACE` | live |
| X | `BTN_NORTH` | `KEY_LEFTSHIFT+KEY_DOT`: types "/" for agents' commands (was Delete until 2026-10-15). Dictation right after a word-starting "/" is joined to it, lower case, without end punctuation: "/" then "Usage." gives "/usage" | live (2026-10-15) |
| Y, held | `BTN_WEST` | `KEY_LEFTSHIFT`: selection with the cross | live |
| R1 | `BTN_TR` | `KEY_LEFTCTRL+KEY_RIGHT`: next word | live |
| R2 | `BTN_TR2` | `KEY_LEFTCTRL+KEY_LEFT`: previous word | live |
| L1 | `BTN_TL` | Hides the Slate; the text is kept (`hide`) | live |
| L2 | `BTN_TL2` | Dictation on or off (`dictate`): Mycroft's resident Kroko, loaded once when the Slate first opens (about 24 s; L2 meanwhile shows "loading…" and starts when ready) and kept while the Slate is hidden or closed. Its text appears underlined at the cursor; L2 again (or any key) inserts it about 1.2 s later | live with the fake provider; real voice is the user's test (12.3) |
| FN + A | `BTN_MODE` + `BTN_EAST` | Sends the text into the window that had focus and presses Return (a terminal runs it; since 2026-10-15), then clears and hides the Slate (`validate`). While dictating, the dictated text goes in first | live |
| FN + X | `BTN_MODE` + `BTN_NORTH` | Clears the Slate (`clear`) | live |
| FN + Y | `BTN_MODE` + `BTN_WEST` | Sends the text to Mannie's window (lines joined) and presses Return, then clears and hides the Slate (`mannie`). If Mannie is not open, the text stays and the hint says so | core only (2026-10-15) |
| FN + B | `BTN_MODE` + `BTN_SOUTH` | Send to Mike (`mike`): starts Mike's window if needed, waits for "Mike — ready" (90 s at most), types the text, then Return; while Mannie runs, Mike asks to stop it: the Slate hides with its text, A = yes, B = no in Mike's window; on yes the text follows once Mike is ready (15 min at most) | checked live 2026-10-31 (6.11); the switch offline only (6.12) |
| FN + ↑ | `BTN_MODE` + `BTN_DPAD_UP` | Previous sent text (`history-prev`), newest first; the draft is kept | core only (2026-10-15) |
| FN + ↓ | `BTN_MODE` + `BTN_DPAD_DOWN` | Next sent text (`history-next`); past the newest, the draft comes back | core only (2026-10-15) |
| Left stick | `ABS_X`/`ABS_Y` | Moves the **green** selection on the keyboard (`move 0 …`): one push = one key, held = repeat after 0.3 s every 0.12 s | live |
| L3 | `BTN_THUMBL` | Types the green key (`press 0`) | live |
| Right stick | `ABS_RX`/`ABS_RY` | Moves the **red** selection (`move 1 …`); no pointer while the Slate is shown | live |
| R3 | `BTN_THUMBR` | Types the red key (`press 1`) | live |
| Start, Select | `BTN_START`, `BTN_SELECT` | Nothing | live |

The history keeps the last 50 texts sent with FN + A or FN + Y, on the card (`/storage/.local/state/tanstfaafllm/wyoh/slate-history.jsonl`, mode 600); text sent to the Wi-Fi password window is never kept.

A key pressed while dictation listens ends it and acts once the dictated text is in: A puts the new line after the spoken words (user, 2026-10-15).

The keyboard is AZERTY with é è à ç; its "123" key switches to digits and symbols. The green selection starts on f and the red one on j.

## Menu (Start)

| Control | Effect |
| --- | --- |
| Cross ↑ ↓ | Choose an entry (key repeat when held) |
| A | Launch it |
| B, or Start again | Close the menu |
| Right stick + R3 | Click an entry |

## Apps that read the gamepad themselves ("gamepad-raw")

An app listed as `gamepad-raw` in `app_profiles` gets the gamepad while it has the focus: the daemon releases its grab, and the buttons do what the app defines. Only two controls stay Wyoh's: **FN + B** (`BTN_MODE` + `BTN_SOUTH`, close) and **FN + Start held 2 s** (recovery, which also takes the gamepad back). Core only: no app is listed yet (Step 9).

## Apps fed a remapped joystick ("gamepad-virtual")

An app whose manifest says `input = "gamepad-virtual"` gets the daemon's uinput joystick "wyoh-game-pad" while it has the focus. Both sticks pass through as analog axes, and the manifest's `[pad]` table maps physical buttons to the app's joystick buttons; its `[keys]` table can still send keys. FN + B and FN + Start held 2 s stay Wyoh's, as for "gamepad-raw".

### Wolfenstein 3D (ECWolf)

Source: `src/wyoh/apps/wolf3d/wyoh-app.template.toml`. Live, and accepted by the user on 2026-10-13 (Step 9.8b). Button numbers are wyoh-game-pad indexes; on Arch Linux ARM's SDL3 they reach ECWolf as controller buttons, so Y, X, L2 and R2 moved on 2026-10-30 (Step 13.0b).

| Control | evdev | Effect | State |
| --- | --- | --- | --- |
| A | `BTN_EAST` | Joystick button 0: fire; validate in the menus | live |
| R1 | `BTN_TR` | Joystick button 0: fire | live |
| B | `BTN_SOUTH` | Joystick button 1: open doors; back ("no") in the menus | live |
| L1 | `BTN_TL` | Joystick button 1: open doors | live |
| Y, held | `BTN_WEST` | Joystick button 3 (SDL controller X): run | live |
| X, held | `BTN_NORTH` | Joystick button 4 (SDL controller Y): strafe with the left stick | live |
| L2 | `BTN_TL2` | Joystick button 6 (SDL left shoulder): next weapon | live |
| R2 | `BTN_TR2` | Joystick button 7 (SDL right shoulder): previous weapon | live |
| Left stick | `ABS_X`/`ABS_Y` | Move forward, back (and strafe with X) | live |
| Right stick | `ABS_RX`/`ABS_RY` | Turn | live |
| Cross | `BTN_DPAD_*` | Arrow keys, for the menus | live |
| Start | `BTN_START` | `KEY_ESC`: the game's menu | live |

## Windows

Four tiles at most per workspace: the second window goes on top, the third top right, the fourth bottom right. A fifth is closed and a "Too many tiles" pop-up appears, which B closes. Live.

## Not available, and proposals

- **Brightness and the LED:** while the gamepad daemon runs, it grabs the gamepad exclusively, so ArchR's own shortcuts (FN + cross for brightness, FN + B for the LED) do not work; Wyoh uses FN + cross and FN + B itself. **Brightness cannot be changed from the controls today.** Proposal for the user: **FN + L1 brighter, FN + L2 dimmer** (both free with FN), through the panel's backlight in `/sys/class/backlight`. Not implemented.
- **Volume:** not checked. The side volume keys may be a separate input device that the daemon does not grab; this is to verify on Luna.
