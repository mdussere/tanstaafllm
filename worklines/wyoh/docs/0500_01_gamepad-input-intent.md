# Wyoh gamepad input — intent

> **Freshness:** 🟢 current · **Written:** 2026-10-07 · **Checked:** 2026-10-31 · **Step:** wyoh 5 ⏳

> **Superseded mapping (2026-10-09):** the controls described here are out of date (left-stick pointer, L1 open/discard, L2 validate). The current reference, checked against the code by a test, is [`0512_01_luna-controls-reference.md`](0512_01_luna-controls-reference.md). This intent stays as the record of Step 5's design.

**Question answered:** What exactly is built so that Luna's session is used through the device's own controls, before any code is written?<br>
**Step:** Wyoh 5 — Device interactors<br>
**Status:** green-lit 2026-10-07 (user: "commit the workline before starting, then work in full autonomy; use Gherkin tests and MCP to simulate the human operations"). Revised the same day: device-tree codes, button-only operation, defaults for the open points.<br>
**Acceptance set by the user:** at the end of this step, Luna can be operated with **only the buttons and the input zone**.<br>
**Also required by the user:** Luna boots straight into the Wyoh session, not the text console. Wyoh enables its two units in the current boot target (`textmode.target`) and leaves the boot partition alone.<br>
**Decisions it rests on (user, 2026-10-07):** a small Wyoh daemon rather than `gptokeyb`; the input zone is Wyoh's for now; Y = Backspace; R1/R2 = quick linear navigation, approximated by Tab / Shift+Tab; the session stays root.

## Purpose

On Luna, the person uses the handheld's controls (D-pad, sticks, face buttons, shoulder triggers), not a keyboard and mouse. A small, resident Wyoh daemon owns the gamepad at the lowest level and turns it into ordinary keyboard and pointer input for the Sway session. Two controls do not become keys: **L1** and **L2** open, close and validate an **input zone**, where text is prepared before the system receives it. Today that text is typed on the USB keyboard. Later it will be dictated and corrected by voice (Mycroft), and possibly prepared or supplemented by AI. Owning these events at the lowest level is what makes that later step possible without changing the controls.

## Scope

In scope: the daemon, its mapping, the pointer, the input zone, a recovery combination, a status file, its service unit, and its tests.

Not in scope: major modes on Select/Start/FN; the right stick; voice or AI input; Mike routing; an MCP tool for gamepad state (the status file prepares it); per-application mappings; on-screen keyboards; changes to ArchR's own files or to `input_sense`.

## Device facts (read-only inventory, 2026-10-07)

`r36s_Gamepad` (`/dev/input/event7`, `archr-singleadc-joypad`): 17 buttons (`BTN_DPAD_UP/DOWN/LEFT/RIGHT`, `BTN_SOUTH/EAST/NORTH/WEST`, `BTN_TL/TR/TL2/TR2`, `BTN_SELECT/START/MODE`, `BTN_THUMBL/THUMBR`) and 4 axes (`ABS_X/Y`, `ABS_RX/RY`, range −1800…1800, fuzz and flat 32). The device tree (`/proc/device-tree/joypad/sw*`, read-only, 2026-10-07) labels every button: A = `BTN_EAST`, B = `BTN_SOUTH`, X = `BTN_NORTH`, Y = `BTN_WEST`, L1 = `BTN_TL` (`TOP-LEFT`), R1 = `BTN_TR`, L2 = `BTN_TL2`, R2 = `BTN_TR2`, Select = `BTN_SELECT`, Start = `BTN_START`, FN = `BTN_MODE` (`BTN_FN` label), L3/R3 = `BTN_THUMBL/THUMBR`, D-pad = `BTN_DPAD_*`. Stick polarity (the node has `invert-absx`/`invert-absy`) is confirmed in the user check.

ArchR's `input_sense` reads the same device for hotkeys (L1/Select/Start combinations, FN+D-pad brightness, FN+B LED).

## Behaviour

### Mapping

| Control | Code | Normal mode | Zone open |
| --- | --- | --- | --- |
| D-pad ↑ ↓ ← → | `BTN_DPAD_*` | arrow keys | arrow keys (move in the text) |
| Left stick | `ABS_X/Y` | nothing (unassigned since 2026-10-08) | nothing |
| Right stick | `ABS_RX/RY` | pointer motion (user change 2026-10-08: right thumb on the pointer, left thumb on the D-pad) | pointer motion |
| R3 (right stick click) | `BTN_THUMBR` | left button | left button |
| A | `BTN_EAST` | Return | **validate** (same as L2) |
| B | `BTN_SOUTH` | Escape | **close and discard** (same as L1) |
| Y | `BTN_WEST` | Backspace | Backspace |
| X | `BTN_NORTH` | Delete | Delete |
| L1 | `BTN_TL` | open the zone | close the zone, discarding its text |
| L2 | `BTN_TL2` | (nothing; the zone is closed) | validate |
| R1 | `BTN_TR` | Tab | Tab (no effect in a one-line zone) |
| R2 | `BTN_TR2` | Shift+Tab | Shift+Tab |
| Start | `BTN_START` | open the application menu (Escape if it is already open) | nothing |
| Select | `BTN_SELECT` | focus the next window (cycles) | nothing |
| FN + D-pad | `BTN_MODE` + `BTN_DPAD_*` | move focus to the window in that direction | nothing |
| FN + A | `BTN_MODE` + `BTN_EAST` | toggle fullscreen of the focused window | nothing |
| FN + B | `BTN_MODE` + `BTN_SOUTH` | close the focused window | nothing |
| FN + R1 / FN + R2 | `BTN_MODE` + `BTN_TR` / `BTN_TR2` | next / previous workspace | nothing |
| L3, other FN combinations | — | nothing (ignored, counted in the status) | nothing |
| FN + Start, both held 2 s | `BTN_MODE` + `BTN_START` | **recovery** (below) | recovery |

**Button-only operation (added under the green light):** the user's acceptance is to operate Luna with only the buttons and the input zone. A person therefore also needs to open the application menu, move between windows, and close them without a keyboard. Start (the menu, as on a classic desktop), Select (window cycling), and FN as a held modifier for window management fill that gap. These are Wyoh decisions taken during autonomous work, kept in `gamepad.toml`, and open to change. FN alone does nothing; while FN is held, its combinations replace the plain meaning of the second button. Window-management actions are Sway IPC commands, not synthetic key chords.

Keys are pressed on button-down and released on button-up, so holding the D-pad repeats through the normal Wayland key repeat. While a button is held, its key stays held. A modifier (Shift for R2) is pressed and released around its key.

### Pointer

The right stick (left stick until 2026-10-08) moves the pointer at a speed proportional to how far it is pushed, like the small stick in the middle of some laptop keyboards. With `r` = deflection normalised to 0…1 (the length of the X/Y vector, capped at 1):

- below a **dead zone** of `dz = 0.12` (about 216 of 1800), nothing moves;
- above it, `speed = v_max × ((r − dz) / (1 − dz))^γ`, with `v_max = 900 px/s` (about 0.8 s to cross the 720 px panel) and `γ = 2` (fine control near the centre).

The daemon emits motion at the configured rate (60 Hz on Luna, near the panel's 54.5 Hz refresh; 100 Hz by default) while the stick is out of the dead zone, and keeps fractional pixels between ticks, so slow motion is smooth. It emits nothing at rest. Sway applies a flat 1:1 profile to the daemon's mouse, as it already does for the test mouse. Every number is in the config file.

### Input zone

The zone is a one-line text field in Wyoh's palette, drawn on top of the session: a `fuzzel --dmenu` prompt with no list, so no new software. Its states follow Mycroft's composition rules (`../mycroft/docs/0106_01_input-composition-architecture.md`):

```text
closed --L1--> open --L2 / A--> delivering --> closed
                 |
                 +--L1 / B------------------> closed (discarded)
```

| Event | Result |
| --- | --- |
| L1 while closed | The daemon records the focused window (Sway `con_id`) as the **target**, then opens the zone. Keyboard text goes into the zone. |
| typing (USB keyboard) | Edits the text. D-pad ←/→, Y and X edit too. |
| L2 or A while open | Validate. The zone closes, focus returns to the target, and the exact text is typed into the target **once**, followed by nothing else (no Return). Empty text delivers nothing. |
| L1 or B while open | Discard. The zone closes; nothing is delivered, stored or logged except the event "discarded". |
| target closed meanwhile | Nothing is delivered. The status reports `target-gone`; the text is not sent anywhere else. |
| another L1 while delivering | Ignored until delivery finishes. |

Delivery types the text with `wtype`, paced (`-s 100 -d 10`), because it carries its own keymap and handles accented characters. The text is not interpreted and never run as a command by Wyoh. If the target is a terminal, the person still presses A (Return) themselves to run a typed command.

### Recovery

Holding **FN + Start for 2 seconds**, in any state:
1. releases every key and button the daemon holds;
2. closes the zone without delivering;
3. records the event in the status.

It doesn't restart anything. *Default adopted under the green light; the user can change it.*

### Ownership of the device

The daemon takes the gamepad exclusively (`EVIOCGRAB`). Nobody else sees its events, including ArchR's `input_sense`, so ArchR's gamepad hotkeys (brightness, LED, kill) stop while the daemon runs. *Default adopted under the green light; the user can change it.* The kernel releases the grab when the daemon exits for any reason, so a crash gives the gamepad back to ArchR. Other input devices (power key, ADC keys, USB keyboard and mouse) are untouched.

## Implementation approach

- **One process,** `src/wyoh/wyoh_gamepad.py`, Python 3 standard library only (`os`, `fcntl`, `struct`, `select`, `json`, `tomllib`, `subprocess`), like the test helper. No `python-evdev`, GTK or SDL.
- **Input:** finds the device by name (default `r36s_Gamepad`, configurable, so tests can point it at a virtual gamepad), reads `input_event` records, grabs it.
- **Output:** one persistent uinput keyboard (`wyoh-gamepad-keyboard`) and one mouse (`wyoh-gamepad-mouse`), created once. Never a short-lived keyboard per action, since that broke `wmenu` and forced pacing with `bemenu`.
- **Core:** a pure state machine (`mapping`, `zone`, `recovery`, `pointer`) that turns gamepad events and timer ticks into output actions. Device I/O, Sway IPC, the zone runner and `wtype` are thin adapters around it, replaceable by fakes in tests.
- **Loop:** `select()` blocks with no timeout when the stick is at rest (zero CPU), and wakes every 10 ms while it is deflected or a hold timer is running.
- **Sway:** reads the existing owner-private session descriptor for the IPC socket; uses it only to read the focused `con_id` and to focus the target before delivery.
- **Config:** `src/wyoh/deploy/luna/gamepad.toml` (device name, grab, mapping table, pointer constants, zone command, recovery combination and hold time). An invalid config refuses to start, with a clear error; there is no partial mapping.
- **Status:** `/run/wyoh/gamepad.json`, rewritten atomically on each state change: device, grabbed, zone state, target, last action, recovery count, ignored-button count, last error. No typed text is ever written to it.
- **Service:** `wyoh-gamepad.service` in `/storage/.config/system.d`, `PartOf=` and `After=wyoh-sway.service`, `Restart=on-failure`, started and stopped with the session through `make`. Not enabled at boot, like the Sway unit.

## Failure behaviour

| Failure | Behaviour |
| --- | --- |
| gamepad not found at start | Waits and checks again every 5 s (only rereads the device list when `/dev/input` changes); status `no-device`; keyboard and mouse keep working |
| gamepad disappears | Releases everything it holds, discards an open zone, waits for the device again |
| uinput unavailable | Refuses to start, with an error; nothing is grabbed |
| Sway socket missing | Mapping and pointer keep working; the zone refuses to open (status `no-sway`) |
| `fuzzel` or `wtype` fails | Zone discarded, nothing delivered, error in the status |
| daemon crash | Kernel releases the grab and the virtual devices; systemd restarts the daemon |

## Resource budget

Measured, not assumed: RSS ≤ 20 MiB for the daemon; 0 CPU ticks over 10 s at rest; under 5% of one core while the stick is held at full deflection. The zone's fuzzel exists only while the zone is open.

## Testing policy and harness

1. **State-machine tests** (deterministic, default suite): fake event sequences cover every row of the mapping table in both modes; hold and release; zone open, validate, discard, empty text, target gone, and re-entrance; recovery timing with a fake clock; ignored buttons; invalid configs.
2. **Pointer tests** (deterministic): dead zone, curve values, fractional accumulation, 100 Hz ticks, no output at rest.
3. **Calibration probe** (live, user-assisted): a pytest probe asks the user to press each control in turn and records the evdev codes, confirming or correcting the table before the daemon uses it.
4. **Virtual-gamepad scenario** (live, automated): a uinput device with the same 17 buttons and 4 axes stands in for the real one (the daemon is pointed at it by name). A Gherkin scenario on Luna's panel covers:
   - arrows and Backspace/Delete in a terminal;
   - pointer motion and an L3 click on a fuzzel entry;
   - Tab/Shift+Tab;
   - L1, typing (uinput keyboard), L2, with delivery checked through a marker-file side effect;
   - L1 discard, with no side effect;
   - recovery.

   Every step has an inspected MCP screenshot; the daemon's status file is checked at each step.
5. **User check** on the physical controls, with the panel in view.
6. **Measurements:** RSS and CPU at rest and with the stick deflected, recorded in the result.

## Acceptance

Step 5 is done when:
- every control in the mapping table produces its action on Luna's panel, through the real gamepad after calibration;
- the zone opens, takes keyboard text, discards on L1/B, and delivers exactly once on L2/A to the window that had focus;
- recovery works;
- stopping the daemon returns the gamepad to ArchR;
- the deterministic and virtual-gamepad tests pass, with inspected screenshots;
- the resource budget holds.

## Defaults adopted for the open points (2026-10-07, autonomous work)

The user green-lit autonomous work without answering the four open points; these defaults apply and can be changed in `gamepad.toml`:
1. Recovery: FN + Start held 2 s.
2. Exclusive grab: ArchR's gamepad hotkeys (brightness, LED) pause while the daemon runs.
3. No right click.
4. A validates and B discards while the zone is open, like Enter and Esc in Mycroft's console.

## Simulating the person (testing)

Per the user's instruction, live tests simulate the person through MCP. In `--full-ipc-development` mode only, the MCP server gains development tools that create a **virtual gamepad** with the device's 17 buttons and 4 axes (name `wyoh-virtual-gamepad`), press, hold, and release its buttons, deflect its sticks, and type on a **virtual keyboard** standing in for the USB keyboard. The daemon serves the real gamepad and the virtual one at the same time, so the real device stays usable during tests. These tools are development authority, like `sway_command`, never a product capability.
