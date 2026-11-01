# Result — Luna operated with only its buttons and the input zone

> **Freshness:** 🟡 historical · **Written:** 2026-10-07 · **Checked:** 2026-10-31 · **Step:** wyoh 5.6 ✅

**Step:** Wyoh 5 (sub-steps 5.2–5.6 and 5.8), autonomous work green-lit 2026-10-07
**Intent:** [`0500_01_gamepad-input-intent.md`](0500_01_gamepad-input-intent.md)
**Scope:** Luna, ArchR card after Luna Step 6, root session (user decision). Development-only.

## Outcome

The acceptance the user set is met in simulation. **A person can operate Luna with only the gamepad buttons, the left stick, and the input zone:**
- launch applications from the menu;
- prepare text in the zone and send it, or throw it away;
- run commands;
- move between windows, make them fullscreen and close them;
- point and click;
- navigate with Tab/Shift+Tab;
- recover;
- **Luna boots straight into that session.**

What remains is the user's own check on the physical controls (5.7).

## What was built

| File | Role |
| --- | --- |
| [`src/wyoh/wyoh_gamepad.py`](../../../src/wyoh/wyoh_gamepad.py) | The daemon, standard library only: a pure core (mapping, input zone, recovery, pointer), plus evdev input with an exclusive grab, one persistent uinput keyboard and mouse, a minimal Sway IPC client, the menu and zone processes, and the status file `/run/wyoh/gamepad.json` |
| [`deploy/luna/gamepad.toml`](../../../src/wyoh/deploy/luna/gamepad.toml) | Devices (`r36s_Gamepad`, `wyoh-virtual-gamepad`), menu and zone commands, paced `wtype` delivery, pointer constants |
| [`deploy/luna/wyoh-gamepad.service`](../../../src/wyoh/deploy/luna/wyoh-gamepad.service) | Part of the Sway session (`PartOf=`, wanted by `wyoh-sway.service`) |
| [`deploy/luna/wyoh-gpu.sh`](../../../src/wyoh/deploy/luna/wyoh-gpu.sh) | Loads Mali at boot, before Sway (see finding 1) |
| [`src/wyoh/wyoh_virtual_input.py`](../../../src/wyoh/wyoh_virtual_input.py) | The simulated person: a virtual gamepad (17 buttons, 4 axes) and a virtual AZERTY keyboard |
| `wyoh_mcp_server.py` | Development MCP tools `wyoh_dev_gamepad_tap/buttons/stick`, `wyoh_dev_keyboard_type/key`, plus `wyoh_gamepad_status` |
| `Makefile` | `wyoh-luna-enable` / `wyoh-luna-disable` add or remove the boot links |

The mapping is the intent's table, with the device-tree codes (A = `BTN_EAST`, B = `BTN_SOUTH`, X = `BTN_NORTH`, Y = `BTN_WEST`, FN = `BTN_MODE`):
- D-pad = arrows; left stick = pointer; L3 = click;
- A/B/Y/X = Return/Escape/Backspace/Delete; R1/R2 = Tab/Shift+Tab;
- L1/L2 = open-or-discard / validate the zone (A and B also validate and discard while it is open);
- Start = menu; Select = next window;
- FN + D-pad / A / B / R1 / R2 = focus / fullscreen / close / workspace;
- FN + Start held 2 s = recovery.

The bar now shows the buttons: "Start menu | L1 input | Select next | FN+B close".

## Evidence

| Check | Command | Result |
| --- | --- | --- |
| Core state machine and config (5.2) | `uv run pytest test/wyoh/test_wyoh_gamepad.py` | 49 passed |
| Whole deterministic suite | `uv run pytest -m "not live and not integration"` | 103 passed |
| Button-only scenario (5.6), after a cold boot with Mali | `WYOH_LUNA_LIVE=1 uv run pytest -m live test/wyoh/test_luna_buttons_only.py` | 1 passed in 83 s, `results/wyoh/luna-buttons-only/20261006T234137Z/` |

The scenario ([`luna_buttons_only.feature`](../../../test/wyoh/luna_buttons_only.feature)) drives the person only through MCP development tools and never calls `sway_command`. All 20 settled MCP screenshots were inspected:

| Steps | Seen |
| --- | --- |
| 00–03 | empty desktop → Start opens the menu → D-pad ×8 selects Terminal (the list scrolls) → A opens it |
| 04–07 | L1 opens the zone ("L2 send, L1 cancel") → the keyboard types `touch /tmp/…` → L2 sends it once into the terminal → A runs it, and the marker file exists |
| 08–09 | a second command in the zone → B discards it; nothing reaches the terminal, and the second marker does not exist |
| 10–11 | Start, D-pad ×3, A → the image viewer opens beside the terminal |
| 12–16 | Select gives the terminal focus; FN+A makes it fullscreen and back; the stick goes to the top-left corner and then onto the viewer, and L3 focuses the viewer; Select returns to the terminal |
| 17 | `cat -A` sent through the zone, then R1, R2, A: the terminal prints `^I^[[Z$` (Tab, Shift+Tab, Return) |
| 18 | L1, then FN+Start held 2.6 s: the zone is gone and the daemon records one recovery |
| 19 | FN+B repeated: every window closed, empty desktop |

Device and boot checks:
- **Grab:** with the daemon running, a second grab of `/dev/input/event7` fails with "busy". After `systemctl stop wyoh-gamepad`, it succeeds, so the gamepad returns to ArchR.
- **Boot (5.8):** after `make wyoh-luna-enable` and a reboot, with no SSH action:
  - Mali was ready at 14.7 s, and Sway started with `libmali` mapped;
  - the daemon was attached to the real gamepad;
  - the panel showed the Wyoh desktop.

  The tty1 shell stays underneath. `make wyoh-luna-disable` returns to the text-console boot. The boot partition was not touched.

## Cost

| Measure | Value | Budget |
| --- | --- | --- |
| Daemon RSS | 17.5 MB | ≤ 20 MiB ✓ |
| Daemon CPU at rest | 0 ticks in 30 s | 0 ✓ |
| Daemon CPU with the stick fully deflected | 19 ticks in 5 s (3.8% of a core) | < 5% ✓ |

The first measurement was 20% of a core with the stick deflected, and 2 ticks per 10 s at rest. Three changes brought it into budget:
- the status file was being rewritten on every pointer tick; it is now written only on state changes;
- hotplug detection used to reread `/proc/bus/input/devices` every 2 s; it now checks `/dev/input`'s modification time every 5 s;
- the pointer rate is now 60 Hz, close to the panel's 54.5 Hz refresh.

## Findings

1. **Mali never loaded at boot because `modprobe` was not on the unit's `PATH`** (`/usr/sbin`). ArchR's `gpudriver` failed silently, fell back to panfrost, and removed its `libmali` mounts, leaving software rendering and a black panel. `wyoh-gpu.sh` sets its own `PATH`, retries `mali_kbase`, then runs ArchR's step; both units now include `/usr/sbin`. The error had been hidden by `2>/dev/null`, which now only hides the harmless OpenCL mount messages.
2. **A new uinput device loses its first events** until libinput and Sway have added it: the first zone text arrived as `h /tmp/…`. The MCP tools wait for the device to be listed, plus 1 s. The daemon's own devices are created once, at start.
3. **A 40-column zone overflowed the 720 px panel**; it is now 26 columns, with a short hint.
4. **The menu's state went stale when fuzzel closed by itself**; the loop now notices the process ending.
5. **Calibration came from the device tree**, and corrected the intent's guess (A is `BTN_EAST`, not `BTN_SOUTH`).

## Not yet established

- **5.7:** the user's check with the physical buttons, sticks and panel. Stick polarity and the feel of the pointer curve can only be judged by hand.
- Text in the zone still comes from a keyboard (virtual in tests, USB in person), as planned until voice arrives (Mycroft).
- ArchR's gamepad hotkeys (brightness, LED) are off while the daemon runs (accepted default).

## Addendum (2026-10-09): user feedback, four-tile layout, and link limits

**Changes after the user's first use:**
- **Pointer moved to the right stick.** The click moved to R3 and the left stick is unassigned ("right thumb on the mouse, left thumb on the D-pad"). `pointer_stick` in the config; 51 core tests pass.
- **Wallpaper.** The user's own `TANSTAAF-LLM_background.png` (updated with a blond Wyoh), pre-scaled to `deploy/luna/share/backgrounds/tanstaafllm-720.png`. ArchR's gdk-pixbuf has PNG support built in but no MIME database, so `swaybg` rejected every image. Wyoh deploys `share/mime/mime.cache` (shared-mime-info 2.4 from Debian 13, SHA-256 `24a34007…bc7c89c`) in its `XDG_DATA_DIRS`. A capture of the desktop matches the image file pixel for pixel below the bar; `swaybg` uses 7.3 MB.
- **Four tiles per workspace** (user requirement): `wyoh_layout.py` and `wyoh-layout.service` place the 2nd window on top, the 3rd top-right and the 4th bottom-right. A 5th is closed at once and a red "Too many tiles" pop-up appears, dismissed with B. The policy works from current geometry, so it keeps working after windows close, and a new tile keeps the focus. 11 policy tests pass. The layout scenario (`test_luna_layout.py`) passed on Luna twice; the screenshots of `20261008T215715Z` were inspected. The daemon uses about 17 MB.

**Link limits found:**
- **Luna's OpenSSH 9.8 PerSourcePenalties** temporarily refuse an address after unauthenticated or timed-out connections. All Luna tests now share one multiplexed connection (`SSH_MUX`), and `make` takes `WYOH_LUNA_SSH`.
- **Luna's Wi-Fi moves about 160 KB/s** (receive 13 Mbit/s MCS 1, signal −62 dBm, about 1,500 retries) and sometimes stalls for over a minute. The acceptance tests now settle frames by comparing SHA-256 on Luna and fetch one JPEG per step (about 200 KB instead of 1 MB), with tolerant colour checks (`luna_screen.py`).

**Not established:**
- The full button-only scenario has not passed again since these changes. Its re-runs stopped on link stalls at different steps (once after completing steps 00–18), and the user asked to stop rerunning it after every change.
- The right-stick pointer and the R3 click have not yet been checked live.
