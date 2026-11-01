# Result — minimal workable Sway environment on `luna-pi`, operated through MCP

> **Freshness:** 🟡 historical · **Written:** 2026-10-07 · **Checked:** 2026-10-31 · **Step:** wyoh 3.7 ✅

**Step:** Wyoh 3.7
**Status:** completed 2026-10-04
**Scope:** `luna-pi` development session only; not Luna hardware or product-shell evidence.

## Question

Can the shared Wyoh Sway session be made usable by a person over VNC, and can an MCP client be shown, with inspected screenshots, to operate that same environment?

## Environment

| Item | Value |
| --- | --- |
| Compositor | pinned Sway 1.10.1 prefix, headless/Pixman, unchanged |
| Output | `HEADLESS-1`, custom mode 720×720 (Luna's panel size) |
| Config | [`src/wyoh/deploy/luna-pi/sway-vnc.conf`](../../../src/wyoh/deploy/luna-pi/sway-vnc.conf), derived from Sway 1.10's default config |
| Bindings | `$mod` = Alt; Alt+Enter `foot`, Alt+d `wmenu-run`, Alt+Shift+q close, Alt+arrows focus/move, Alt+1–4 workspaces, Alt+f fullscreen, layout toggles, reload; no exit binding |
| Keyboard | Sway `xkb_layout fr`; every binding `--to-code` (physical key, so Alt + AZERTY number row works); WayVNC `--keyboard=fr` |
| Bar | built-in `swaybar` with workspaces and [`status.sh`](../../../src/wyoh/deploy/luna-pi/status.sh) (key hints and clock) |
| Packages | `foot 1.21.0-2`, `wmenu 0.1.9-2+b1`, `wtype 0.4-3+b1`, Debian 13, installed with `apt-get install --no-install-recommends` as root (user-granted 2026-10-04) |
| Access | WayVNC loopback `127.0.0.1:5900` only; SSH tunnel for viewers |

Session memory (Sway + swaybg + swaybar + WayVNC + status script): about 108 MB before Step 3.7 (1280×720 wallpaper session); about 79 MB just after restart and **about 95 MB after the scenario** (WayVNC grows from 40 to 51 MB once a client has connected). These are Pi figures, not Luna figures.

Recovery: `make wyoh-rollback` was exercised; Labwc's WayVNC came back on loopback 5900. `make wyoh-activate` restored the Wyoh session.

## MCP scenario

Contract: [`test/wyoh/minimal_env.feature`](../../../test/wyoh/minimal_env.feature); execution: [`test/wyoh/test_minimal_env.py`](../../../test/wyoh/test_minimal_env.py).

```bash
WYOH_SHARED_VNC_LIVE=1 uv run pytest -m live test/wyoh/test_minimal_env.py -vv -rA --timeout=240
```

`1 passed in 18.19s`. Evidence: `results/wyoh/minimal-env/20261003T232316Z/` (log `logs/wyoh/minimal_env_20261004_012315.log`). The full Wyoh live suite then passed again (`4 passed`), with its own minimal-env run `20261003T232433Z`.

| Step | Actor and action | Observed (MCP screenshot and VNC frame, both inspected) |
| --- | --- | --- |
| 00 | precondition: no application window | bar, workspace 1, empty background |
| 01 | MCP `exec foot`; waits for `window` `new` and the first drawn frame | terminal with prompt |
| 02 | MCP focuses it by `con_id`, `exec wtype 'echo WYOH-… > /tmp/wyoh-proof-….txt' -k Return` | typed command and new prompt; marker file content verified on `luna-pi` |
| 03a | MCP `workspace number 2`; person at VNC presses Alt+d | `wmenu` list over workspace 2 |
| 03b | person types `mousepad`, Return | editor alone on workspace 2 |
| 04 | MCP moves the editor by `con_id` to workspace 1 | terminal and editor side by side |
| 05 | MCP `fullscreen enable` by `con_id` | editor covers the output; bar hidden |
| 06 | MCP leaves fullscreen; person presses Alt+Enter, then Alt+Shift+q | third column terminal appears, then closes |
| 07 | MCP closes remaining windows by `con_id` | empty desktop with bar; marker file removed |

Every image of both runs was opened and looked at by the agent before this record was written. Numerical predicates in the test only decide when to stop waiting; they are not the evidence.

## Findings

1. **The previous session was unusable** because its config replaced Sway's defaults with nothing. It now has bindings, a bar, a terminal, and a launcher.
2. **WayVNC's first frame to a new client is a uniform grey placeholder** (`(96, 96, 96)`); the next frame is correct. Single-capture tests must discard it. This, plus capturing before the client drew, invalidated the Step 3.6 VNC proof.
3. **`wmenu` 0.1.9 cannot be driven by `wtype` under Sway 1.10.1.** A transient virtual keyboard appearing or disappearing makes Sway send a keymap `wmenu` rejects (`Assertion 'format == WL_KEYBOARD_KEYMAP_FORMAT_XKB_V1'`, or a segfault after the keyboard is destroyed). `foot` and `mousepad` are unaffected. A person at VNC is unaffected because WayVNC keeps one keyboard for the connection. Consequence for Mike: focused text injection through short-lived virtual keyboards is client-dependent; a product input path would need one persistent virtual keyboard owned by Wyoh.
4. **A headless seat has no keyboard until one is created**; `wmenu` aborts on start without one. Only relevant to MCP-started keyboard clients on a headless session; Luna has physical input.
5. **MCP result shape is lossy.** Without structured output, the SDK sends a list as one text block per element, so a one-element list such as `[{"success": true}]` is indistinguishable from the object. The test normalises it; a product interface should declare structured output.
6. **The screenshot tool failed on two captures within one second** (directory named by the second, created without `exist_ok`). Fixed with microsecond names.
7. **Real VNC viewers send shifted keysyms** (`Q` with Shift held); a client sending `q` with Shift gets Alt+q from WayVNC, which is unbound.
8. `wmenu-run` lists every executable on `PATH`; it is a command launcher, not an application menu.

## Limits

- Pi-only: no claim about Luna graphics, input, memory, or Sway/ArchR compatibility.
- `sway_command` remains full development authority; this is not the Mike-facing capability boundary.
- No pointer/mouse interaction was tested.
