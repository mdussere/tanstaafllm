# Proposal — icons on Luna's desktop

**Step:** Wyoh 10 (proposal; nothing is green-lit)
**Date:** 2026-10-09
**Question answered:** how to put movable application icons on the desktop above the wallpaper, pin them from the menu, and use them with the gamepad.
**Source (user, 2026-10-09, translated from French):** "I really meant putting a few icons on the desktop, positioned above the desktop image. Movable icons, etc. We may not have left and right click, but that would be the idea. And maybe we could take icons out of the menu and pin them." Professor's records do not cover desktop icons; they only list "the icons visible on the desktop" as possible context for a future voice navigation mode.

## 1. What exists

- Sway draws no desktop and no icons; the wallpaper comes from `swaybg`.
- Desktop-icon programs (the desktops of GNOME, Xfce and similar) are tied to their GTK desktops, which Wyoh does not use.
- **Not checked:** whether a small wlroots desktop-icon program without GTK exists. That survey is 10.1.

## 2. Proposed design

### What it is

A small program, `wyoh-desk`, that draws icons on a Wayland *layer-shell* surface on the **bottom layer**: above the wallpaper, below the windows.
- It is built like `wvkbd-luna`: C, Cairo, Pango, PNG icons, cross-built on `luna-pi`. Its drawing and selection code can start from wvkbd's.
- At rest it costs nothing; the target is ≤ 10 MiB RSS and 0 CPU.

### Where the icons live

```
┌──────────────────────────── bar ┐
│ [▣]   [♜]   [🗀]                 │   icons snap to a grid of cells
│ Term  Chess Files               │   (7 × 7 at about 100 px)
│                                 │
│ [W]                             │   wallpaper behind
│ Wolf3D                          │
└─────────────────────────────────┘
```

- The icons are visible when the workspace shows the desktop, as in Windows 3.x.
- With the four-tile layout, open windows cover them; the desktop shows again when the windows close.
- **Positions persist** in `/storage/.config/wyoh/desktop.toml` (desktop-file ID, column, row).

### With the gamepad (no left or right click needed)

| Control | Action |
| --- | --- |
| ❓ **FN+Select** (proposed) | Enter or leave the desktop: a selection appears on an icon, in the same pastel style as the keyboard selections |
| D-pad or left stick | Move the selection between icons |
| A | Launch the selected icon |
| **X held + D-pad** | **Move** the selected icon on the grid (release X to drop it) |
| Y | Unpin the selected icon (asks: Y again to confirm) |
| B | Leave the desktop |
| Right stick + R3 | The pointer still works: click launches; hold R3 and move to drag an icon |

### Pinning from the menu

fuzzel has no right-click or context actions. Two proposals:
1. ❓ A **"Pin to desktop…"** entry in the Start menu. It opens a second fuzzel list of the applications; choosing one pins it in the first free cell. No new button, and it works with Start, the D-pad and A as today.
2. A button chord while the Start menu is open (for example FN+A on a highlighted entry) pins that entry. This is closer to "taking the icon out of the menu", but it needs to know which entry fuzzel has highlighted, which fuzzel does not expose. So it is a later option only.

### Observable state

`wyoh-desk` reports its icons (ID, label, cell, selected) to Wyoh's status, and the development MCP gets a read tool. Tests can check it, and a later Mycroft navigation mode can use "the icons visible on the desktop" as context, under the existing Mycroft boundary.

## 3. Risks

- **Bottom layer and input.** A bottom-layer surface must receive pointer input only where it draws icons, so that clicks on empty desktop do nothing. This is to check with Sway 1.11.
- **The keyboard's selection code is wvkbd's,** which is GPL-3.0. Reusing it makes `wyoh-desk` GPL-3.0 too; Wyoh's own code licence must allow that, so the user decides.
- **Icons need PNGs.** The Papirus subset Wyoh deploys must include PNG sizes, or the icons are rasterised at build time.
- **Covered by tiles.** With windows open, icons are hidden. A "show desktop" control (for example a workspace switch to an empty workspace) may be wanted later.

## 4. Tests

- **Deterministic:** grid placement, collision and the next free cell; reading and writing `desktop.toml`; selection moves; pin and unpin.
- **Live** (Gherkin + pytest through MCP, inspected screenshots):
  - pin Terminal from the menu, and it appears;
  - move it with X + D-pad, and its position survives a session restart;
  - launch it with A;
  - unpin it;
  - drag an icon with the pointer.
- **Cost:** RSS and CPU at rest.

## 5. Decisions for the user

1. The button to enter the desktop: **FN+Select** (proposed)?
2. Pinning through a **"Pin to desktop…"** menu entry (proposed)?
3. GPL-3.0 for `wyoh-desk` if it reuses wvkbd's code, or write the drawing part from scratch?
4. Which icons to pin by default: Terminal plus the Step 9 apps once they exist?
