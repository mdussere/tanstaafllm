# Result — the Step 3.7 session on Luna's real display

> **Freshness:** 🟡 historical · **Written:** 2026-10-07 · **Checked:** 2026-10-31 · **Step:** wyoh 4.7 ✅

**Step:** Wyoh 4.7
**Date:** 2026-10-04
**Scope:** physical Luna (R36 Ultra) on the disposable ArchR card. Development session only; not a product shell, and not the production-base decision.

## Question

Can the minimal Sway session proven on `luna-pi` (Step 3.7) run on Luna's own panel, with ArchR's unmodified Sway, and be operated through the same MCP server?

## Target facts (read-only inventory)

| Item | Observed |
| --- | --- |
| OS | ArchR 20260709, Linux 6.12.94 aarch64, glibc 2.40, 983 MiB RAM |
| Display | `card0-DSI-1`, connected, 720×720; EDID unparsable (normal for a DSI panel) |
| GPU | **no GPU driver loaded** (no `panfrost`, no `renderD128`); EGL reports software rendering, so wlroots falls back to its software renderer |
| Sway | ArchR's `sway 1.11-1` (newer than the 1.10.1 pinned on `luna-pi`); swaybar, swaybg, grim 1.4.1, foot 1.19.0, bemenu 0.6.15 |
| Missing | `wtype`, WayVNC, `wmenu`, pip; pacman sees only ArchR's own repository |
| ArchR's session | `sway.service` (root, seatd, DRM + libinput) with EmulationStation started inside it by `essway.service`; kiosk config in `/storage/.config/sway/config`; a `config.desktop` is also shipped |
| Input | Logitech USB receiver (keyboard, mouse, consumer/system control), `rk805 pwrkey`, `adc-keys` on the seat; `r36s_Gamepad` is a joystick, not a seat device |
| Storage | root ext4 97% full (136 MB free); `/storage` 54 GB |

## What was installed (all under `/storage`, all removable)

| Path | Content |
| --- | --- |
| `/storage/.config/system.d/wyoh-sway.service` | systemd unit, **not enabled**: ArchR's `/usr/bin/sway` on DRM with our config; `Conflicts=sway.service essway.service`; `XDG_RUNTIME_DIR=/run/wyoh` |
| `/storage/.local/share/tanstfaafllm/wyoh/` | deployed `src/wyoh/` (MCP server and `deploy/luna/`: `sway.conf`, `status.sh`, descriptor writer) |
| `/storage/.local/opt/wyoh-mcp-2.2.0/` | Python 3.13 venv with `mcp==2.2.0` (48 MB). pip had to run with `--no-compile`: byte-compilation fails on this image |
| `/storage/.local/opt/wyoh-tools/bin/wtype` | Debian 13 `wtype 0.4-3+b1` arm64 binary copied from `luna-pi`, SHA-256 `d1133faec235832c04b8fefe239ef19606be3ce9dcca54a4263475eb40c0cb6d` |

ArchR's own files and units are untouched. Operation: `make wyoh-luna-deploy | wyoh-luna-start | wyoh-luna-stop | wyoh-luna-status`. Stopping the unit returns the panel to the tty1 text shell; the card still boots into text mode, so a reboot also returns there.

The config ([`deploy/luna/sway.conf`](../../../src/wyoh/deploy/luna/sway.conf)) is the Step 3.7 one adapted to the device: output `DSI-1`, no WayVNC, `bemenu-run` (ArchR's launcher) instead of `wmenu`, Liberation Sans, Xwayland disabled. Same Alt bindings, `--to-code` with `xkb_layout fr`, swaybar with key hints.

## MCP scenario

Contract: [`test/wyoh/luna_minimal_env.feature`](../../../test/wyoh/luna_minimal_env.feature); execution: [`test/wyoh/test_luna_minimal_env.py`](../../../test/wyoh/test_luna_minimal_env.py).

```bash
WYOH_LUNA_LIVE=1 uv run pytest -m live test/wyoh/test_luna_minimal_env.py -vv -rA --timeout=240
```

`1 passed in 35.37s`. Evidence: `results/wyoh/luna-minimal-env/20261004T204916Z/` (log `logs/wyoh/luna_minimal_env_20261004_224915.log`). Each screenshot is Sway's own capture of `DSI-1`, taken once two consecutive frames were identical. All eight were inspected:

| Step | MCP action | Inspected screenshot |
| --- | --- | --- |
| 00 | precondition: no window | bar, workspace 1, empty background |
| 01 | `exec foot` | root shell prompt `sh-5.3#` |
| 02 | focus by `con_id`; `exec wtype 'echo WYOH-… > /tmp/…' -k Return` | typed command and new prompt; marker file verified on Luna |
| 03a | `workspace number 2`; `exec bemenu-run …` | launcher listing commands over workspace 2 |
| 03b | `exec wtype -s 200 -d 20 'foot --app-id=wyoh-viewer less /etc/os-release' -k Return` | `/etc/os-release` viewer alone on workspace 2 |
| 04 | move it by `con_id` to workspace 1 | shell and viewer side by side, text re-wrapped |
| 05 | `fullscreen enable` on the shell by `con_id` | shell alone, no bar |
| 06 | close all by `con_id` | empty desktop with bar; marker removed |

Unlike on `luna-pi`, **the MCP drove the launcher itself**: `bemenu` accepts `wtype`'s short-lived keyboard, where `wmenu` 0.1.9 aborted.

## Cost on Luna

| Measure | Value |
| --- | --- |
| Session RSS (sway 28.0 + swaybar 10.9 + swaybg 5.2 + status 3.4 MB) | **≈ 46 MiB** after the scenario, within the 150/200 MiB Wyoh budget; no WayVNC |
| `MemAvailable` with the session running | 803 MiB of 983 |
| Sway idle CPU | 0 ticks over 10 s |
| Sway CPU while `htop` redrew a full window | ≈ 80% of one core, sampled by `htop` itself (software compositing, no GPU) |

## Findings

1. **ArchR's unmodified Sway 1.11 drives the real panel and its IPC works with the Wyoh MCP server unchanged** (descriptor-bound attachment, screenshots, events, commands).
2. **There is no GPU acceleration.** The Mali-G31 has no loaded driver on this image; composition is software. Idle cost is nil, but full-window redraws are CPU-heavy. This matters for Step 5 and belongs to Luna characterisation.
3. **`wtype` typing needs pacing for some clients.** `bemenu` lost the first keys (sent before it loaded `wtype`'s keymap) and repeated letters; `-s 200 -d 20` made it reliable (3/3 by hand, then the test). `foot` needed no pacing. A product input path should own one persistent virtual keyboard rather than spawn one per action.
4. **Evidence must wait for a settled frame.** A terminal app captured right after a resize can show foot's reflow mixed with the app's redraw; the test now waits for two identical frames. Live apps such as `htop` never settle, so the scenario uses a static viewer.
5. Luna's clock is UTC (bar shows 17:49 at 19:49 local); cosmetic.

## Not yet established

- **The physical panel and keyboard were not observed by a person during this run.** Sway's screenshots are what the compositor drew for `DSI-1`; that the panel shows it, and that the USB AZERTY keyboard drives the bindings, awaits the user's check.
- Gamepad/button bindings, suspend/blank, touch, audio, and ArchR's EmulationStation coexistence (the unit simply displaces it).
- Whether ArchR's Sway 1.11 or the pinned 1.10.1 is "the" Wyoh v0 Sway (Step 6.1 question).

## Reproduction of the luna-pi run on the reshaped card (2026-10-05)

After Luna's Step 6 reshape (24 GiB `/`, `/home`, 26 GiB `/storage`; still ArchR, root-only), the user asked for a step-for-step reproduction of `luna-pi` run `results/wyoh/minimal-env/20261003T232433Z` on the physical display.

| luna-pi run | Luna reproduction |
| --- | --- |
| MCP actions on the shared Sway | same MCP server and tools on `wyoh-sway.service` (ArchR's Sway 1.11 on `DSI-1`) |
| a person typing through VNC | a kernel uinput keyboard ([`test/wyoh/uinput_keyboard.py`](../../../test/wyoh/uinput_keyboard.py)) that Sway treats like the USB keyboard, with the French layout and `--to-code` bindings |
| MCP screenshot + VNC frame per step | MCP screenshot of `DSI-1` per step, on a settled frame. VNC is not used on Luna (user direction); WayVNC would also need FFmpeg 8 |
| `mousepad` (GTK) | `vim` in `foot`: GTK rejected for cost; ArchR's stripped `nano` 8.5 stays 80×24 after resizes |

```bash
WYOH_LUNA_LIVE=1 uv run pytest -m live test/wyoh/test_luna_minimal_env.py -vv -rA --timeout=240
```

`1 passed in 39.88s`. Evidence: `results/wyoh/luna-minimal-env/20261005T141451Z/` (nine step screenshots, `overview.png`, `keyboard.log`; log `logs/wyoh/luna_minimal_env_20261005_161449.log`). All nine screenshots were inspected:

| Step | Actor | Inspected screenshot |
| --- | --- | --- |
| 00-empty | — | bar and empty workspace 1 |
| 01-terminal | MCP `exec foot` | shell prompt |
| 02-typed | MCP `wtype` into the terminal | typed `echo WYOH-…` and new prompt; marker file verified |
| 03a-launcher | MCP `workspace number 2`; person Alt+d | bemenu over workspace 2 |
| 03b-editor-ws2 | person types `foot -a wyoh-editor vim`, Return | `vim` filling workspace 2 |
| 04-split | MCP moves it by `con_id` to workspace 1 | shell and `vim` side by side, `vim` re-laid out |
| 05-fullscreen | MCP fullscreens `vim` | `vim` alone, no bar |
| 06-person-terminal | person Alt+Enter, then Alt+Shift+q | a third, focused terminal; then closed |
| 07-empty | MCP closes by `con_id` | empty desktop; marker removed |

Two failures were found and fixed on the way. **The uinput helper** remapped AZERTY keys twice, so the launcher received `foot -q zyoh-editor nqno`; typing now uses physical key codes directly, checked by screenshot. **`nano`** never filled its window; `foot` reported the new size (24×80 → 53×119) and `nano` caught SIGWINCH but did not redraw. A `foot` terminfo entry did not help, and `vim` did. Both and the missing terminfo database are reported to Luna (note `0000_07`, section 9).

Remaining differences from the luna-pi run, all deliberate: no VNC column, `vim` instead of `mousepad`, and root instead of a normal user (Luna has no users yet). The session is left running on the panel for the user to look at; `make wyoh-luna-stop` returns to the text console.

## Correction (2026-10-05): GPU and the physical panel

Two statements above are wrong:

- **"No GPU driver" is wrong.** ArchR loads ARM's Mali driver (`mali_kbase` plus `libmali` bind mounts) through `/usr/lib/archr/gpudriver --start` in its graphical autostart. The text-mode boot skips that step, which is why Wyoh's Sway reported software rendering. With the step run, Sway uses Mali-G31 OpenGL ES 3.2. The unit now runs it when `/dev/mali0` is missing.
- **The runs above prove what Sway drew, not what the panel showed.** The user later saw a black panel while Sway's screenshots were correct. The software-rendered sessions above were never confirmed on the physical display. See `0408_01_luna-fuzzel-menu.md`.
