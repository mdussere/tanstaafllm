# Note from Wyoh — what Wyoh's session needs on a new Luna root

> **Freshness:** 🟢 current · **Written:** 2026-10-25 · **Checked:** 2026-10-31 · **Step:** mannie 7.2 ⏳

**From:** Wyoh workline (session tanstfaafllm-8e)
**To:** Mannie workline
**Date:** 2026-10-25
**Status:** information note, written at Professor's request for the user's decisions of 2026-10-25 (`plan_mannie.md` Steps 6 and 7). It asks no change now. Wyoh plan Step 13 keeps the same list. Reply with a section at the end, or a note back.

## What Wyoh runs on Luna today

Everything Wyoh installed lives on `STORAGE`, under `/storage/.local/` and `/storage/.config/system.d/`, so it survives a root swap. What follows comes from the **root** and must exist on the new one.

## 1. Packages from the root

| Need | Today (ArchR) | Used by |
|---|---|---|
| Sway 1.11, swaybar, swaybg | ArchR's `sway 1.11-1` | the session (`deploy/luna/sway.conf`) |
| seatd | ArchR, `seatd.service` | `wyoh-sway.service` requires it |
| foot 1.19+ | ArchR | Terminal, Text Editor, Mannie entry, the Slate |
| grim | ArchR | screenshots (MCP tests) |
| Python 3 (standard library only) | ArchR 3.13 | gamepad daemon, Slate, layout policy, Wi-Fi panel, app generator |
| `busctl` (systemd) | ArchR | Wi-Fi panel (iwd over D-Bus) |
| iwd, with state in `/storage/.cache/iwd` | ArchR iwd 3.10 + Luna's drop-in `iwd.service.d/10-persistent-state.conf` | Wi-Fi panel; iwd also does DHCP (`EnableNetworkConfiguration=true`) |
| xkeyboard-config | `/usr/share/X11/xkb` | AZERTY layout, uinput typing |
| Fonts: Liberation Sans and Mono, a `monospace` fallback | ArchR | menu, bar, Slate, terminal |
| SDL2 2.32 | ArchR | calculator, Wolfenstein (ECWolf), NetSurf (through the port's sdl12-compat) |
| libjpeg.so.8, libcurl, libpng16, libexpat, zlib | ArchR | NetSurf's `nsfb` (prepared, not yet run) |
| ALSA user-space libraries | ArchR | Mycroft's capture; game sound (`SDL_AUDIODRIVER=alsa`) |
| `commander` | ArchR package (`/usr/bin/commander`) | the "Files" entry; probably absent from Arch Linux ARM |

Wyoh's own binaries are on `STORAGE`, in `/storage/.local/opt/wyoh-tools/bin`: fuzzel 1.12 and wtype 0.4 (Debian 13 arm64) and `wvkbd-luna` (built on `luna-pi`). They need the root's glibc to be at least as new as Debian 13's, which glibc 2.43 is. Their other libraries (cairo, pango, xkbcommon, wayland) must come from the root.

## 2. The GPU path (the main risk)

- Mali-G31 runs on ArchR's **libmali** blob. `wyoh-gpu.sh` loads `mali_kbase`, then runs ArchR's `/usr/lib/archr/gpudriver --start`, which bind-mounts libmali over glvnd's libEGL/libGLESv2. Sway also needs ArchR's libmali hook.
- Every client then needs `MALI_WAYLAND_DMABUF_PROTOCOL=1` (Wyoh 9.1b).
- Panfrost failed on this device. Without libmali, Sway falls back to software rendering, and on 2026-10-11 the DSI panel stayed black that way.
- **So the new root needs:**
  - the `mali_kbase` module for the kept kernel (your study notes the modules under `/usr/lib/kernel-overlays/base/lib/modules/`);
  - ArchR's libmali and its `gpudriver` script, or an equivalent;
  - wlroots able to use it.

## 3. Devices and permissions

- **The gamepad daemon:**
  - grabs `/dev/input/event*` (`r36s_Gamepad`) exclusively;
  - creates uinput devices (keyboard, mouse, "wyoh-game-pad"), so it needs `/dev/uinput` and the `uinput` module;
  - reads `/proc/asound` and picks a capture device in `/dev/snd`.
- **The Wi-Fi panel** writes iwd profiles (mode 600) into iwd's state directory and calls iwd over the system bus.
- **Today all of this runs as root.** As `michael`, each point needs an answer (Luna's note `worklines/professor/docs/0000_04`):
  - `input` group for evdev, plus a udev rule for `/dev/uinput`;
  - `audio` group for `/dev/snd`;
  - iwd's D-Bus policy, which allows the `wheel` group on Arch;
  - write access to iwd's state directory, or an iwd agent instead of profile files;
  - a seat from seatd.

## 4. Services and the session user

- **Units:**
  - `wyoh-sway.service`, with `wyoh-gamepad.service` and `wyoh-layout.service` bound to it (`PartOf`/`Requires`);
  - all three sit in `/storage/.config/system.d/`, ArchR's user unit directory, and `wyoh-sway` is `WantedBy=textmode.target`.
- **Today they run as root, with:**
  - `HOME=/storage`;
  - `XDG_RUNTIME_DIR=/run/wyoh`;
  - `PATH` and `XDG_DATA_DIRS` pointing into `/storage/.local`.
- **On a new root:**
  - their directory and target must still be read (or the units moved to `/etc/systemd/system` or a user session);
  - `textmode.target` must exist (your study: the kernel command line names it).
- **Paths that assume root or `/storage`:**
  - `HOME=/storage`, in the units and the app launchers;
  - Mycroft's assets under `/storage/.local/opt/mycroft`;
  - iwd's state in `/storage/.cache/iwd`;
  - the Slate history in `/storage/.local/state/tanstfaafllm/wyoh/`;
  - the MCP venv `/storage/.local/opt/wyoh-mcp-2.2.0`, built for ArchR's Python 3.13, so a different Python minor version means rebuilding it.

## 5. What Wyoh would check first on a new root

- The panel lights up with Sway on Mali.
- The gamepad is grabbed, and uinput typing works.
- The menu, the Slate and the keyboard appear.
- Kroko dictation runs.
- The Wi-Fi panel lists networks.

These are all existing live tests in `test/wyoh/`, run with `WYOH_LUNA_LIVE=1`.
