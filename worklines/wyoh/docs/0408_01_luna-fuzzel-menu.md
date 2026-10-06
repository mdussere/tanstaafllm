# Result — fuzzel application menu on Luna's panel

**Step:** Wyoh 4.8 (user direction 2026-10-05: "let's test fuzzel, install and test it with many interactions, take evidence images")
**Date:** 2026-10-05
**Scope:** Luna, ArchR card after Luna Step 6, root session. Development-only.

## What was installed (Wyoh-owned, under `/storage`)

| Item | Source | Notes |
| --- | --- | --- |
| `fuzzel` 1.12.0 | Debian 13 `fuzzel_1.12.0+ds-1_arm64.deb`, SHA-256 `5d4900883a70877ff390cfa6349045690366de8a451be9f2d438d8015b656d9c` | `+svg(nanosvg)`, needs glibc 2.38. Arch Linux ARM's 1.15.0 was rejected: it links `libresvg` 0.48, which needs glibc 2.43 (Luna has 2.40). In `/storage/.local/opt/wyoh-tools/bin/` |
| 12 Papirus icons | Arch Linux ARM `papirus-icon-theme-20260801-1-any` (GPL-3.0) | 60 KB subset, deployed only (not in Git) to `deploy/luna/share/icons/Papirus/` with Wyoh's `index.theme` |
| Menu config | [`deploy/luna/fuzzel.ini`](../../../src/wyoh/deploy/luna/fuzzel.ini) | Windows 3.x palette (silver, navy selection, maroon match), Liberation Sans 12, `cache=/dev/null` |
| App entries | [`deploy/luna/share/applications/`](../../../src/wyoh/deploy/luna/share/applications/) | Terminal, Text Editor (`vim`), Task Manager (`htop`), Calculator (`bc`), Image Viewer (`swayimg`) |

The Sway config binds Alt+d to fuzzel. The unit adds the entries and icons through `XDG_DATA_DIRS`. ArchR's own entries (Htop, mpv, nvtop, Gmu Music Player, Manage Printing) also appear; the last two have no icon.

## Scenario and evidence

Contract: [`test/wyoh/luna_fuzzel.feature`](../../../test/wyoh/luna_fuzzel.feature); execution: [`test/wyoh/test_luna_fuzzel.py`](../../../test/wyoh/test_luna_fuzzel.py). A person is played by kernel uinput devices ([`uinput_keyboard.py`](../../../test/wyoh/uinput_keyboard.py), now a keyboard and a mouse). The MCP server observes, drives a dmenu, and cleans up.

```bash
WYOH_LUNA_LIVE=1 uv run pytest -m live test/wyoh/test_luna_fuzzel.py -vv -rA --timeout=280
```

`1 passed in 62.39s`. Evidence: `results/wyoh/luna-fuzzel/20261005T145737Z/`: 19 settled MCP screenshots, `overview.png`, `evidence.json` (selection band and window rectangles per step), `keyboard.log`. All 19 were inspected:

| Steps | Interaction | Seen |
| --- | --- | --- |
| 00 | — | empty desktop |
| 01–04 | Alt+d; type `ed`; Backspace ×2 and Down ×3; Escape | menu with icons → "Text Editor" and "mpv Media Player" (match in maroon) → selection on row 4 → closed, nothing launched |
| 05a–c | Alt+d; type `term`; Return | single "Terminal" row with preview icon → terminal window |
| 06a–c | Alt+d; type `image`; **mouse click** on the row | "Image Viewer" row → viewer tiled beside the terminal, showing the picture |
| 07a–d | Alt+d; Down ×7 (Task Manager); Up ×7 (Calculator); Return | selection moves down then back → calculator as a third column |
| 08a–c | MCP runs `fuzzel --dmenu` with Cascade/Tile/Close all; person presses Down and Return | Wyoh menu → "Tile windows" selected → choice file contains `Tile windows` |
| 09 | MCP closes all by `con_id` | empty desktop |

Hand-run diagnostic captures are in `results/wyoh/luna-diagnostics/20261005/` (with `INDEX.md`).

## Cost

fuzzel's RSS is about 9 MB while the menu is open, and it exits when the menu closes, so it costs nothing at rest. No GTK and no resident daemon.

## Findings and fixes

1. **The panel was black because the GPU driver wasn't loaded (correction).** ArchR does have a GPU path: its graphical autostart runs `/usr/lib/archr/gpudriver --start`, which loads `mali_kbase` and bind-mounts ARM's `libmali` over `libEGL`/`libGLES`. The text-mode boot skips that step. Wyoh's Sway then fell back to software rendering, and the user saw nothing on the panel, though Sway's own screenshots looked correct. The unit now runs ArchR's step when `/dev/mali0` is missing, and Sway uses Mali-G31 OpenGL ES 3.2. Step 4.7's "no GPU driver" statement and its implicit claim that the panel showed the session were wrong; see `0407_01`.
2. **Focus-follows-mouse closes the menu.** Moving the pointer over a window gave it focus, and fuzzel exits when it loses focus. Wyoh's Luna session now uses `focus_follows_mouse no` (click to focus, as in Windows 3.x).
3. **fuzzel's launch-frequency history reorders the menu.** It is turned off (`cache=/dev/null`), for a stable Program-Manager order and no hidden state.
4. **swayimg floats itself, transparently, over the focused window** through Sway IPC (`position = parent`, `background = none`). The entry starts it without `SWAYSOCK` and with an opaque background, so it tiles like any other window. Started from fuzzel with integration on, it named itself `swayimg_<hash>`.
5. The test now detects new windows by polling the tree with an app-id prefix, against a snapshot taken before the action, rather than relying on the `new` event, which can come before a client sets its app id.

## Limits

- Root session; ArchR still has no users.
- The fuzzel menu is a launcher list, not a Program Manager with icon groups. Desktop icons remain open (see the candidate review in the session; no GTK option found).
- The physical panel's appearance after the GPU fix awaits the user's confirmation.
