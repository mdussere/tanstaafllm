# Note from Mannie: Wyoh's session runs on Luna's new root

**From:** Mannie (session tanstfaafllm-d3), 2026-10-25 14:40
**To:** Wyoh, Step 13
**Status:** information. Mannie repaired the session at the user's request ("remets-nous une interface graphique"). Wyoh's own files on `STORAGE` were not edited, except the MCP venv (rebuilt; see below).

## State

Luna runs an Arch Linux ARM root on ArchR's boot path (`plan_mannie.md` Step 7, study `worklines/mannie/docs/0701_01`). The session is up and comes back by itself after a reboot. Evidence: `results/mannie/luna-sway/20261025T1335Z/`, including an MCP screenshot.

What Mannie did:
- **GPU:** ArchR's Mali stack (`libmali`, `/usr/lib/mali`, `/usr/lib/glesonly`, `/usr/lib/archr/gpudriver` and `functions`, `/etc/profile.d/001-functions`) was put back from the image's inactive copy with `src/mannie/luna/install-archr-mali.sh`. `wyoh-gpu.sh` works unchanged: `mali_kbase` binds, and `gpudriver --start` bind-mounts libmali's `libEGL`, `libGLESv2`, `libgbm`, `libwayland-egl` and the `/dev/null` `libGL`.
- **Units:** `systemctl link` for `wyoh-sway`, `wyoh-gamepad` and `wyoh-layout` from `/storage/.config/system.d`, then `enable`: the session is `WantedBy=textmode.target` as before. The session still runs as root.
- **Packages from your note `0702_01`:** Arch Linux ARM's Sway **1.12** (wlroots 0.20; ArchR had 1.11), seatd, foot 1.28, grim, xkeyboard-config, Liberation fonts, `sdl2-compat`, libjpeg-turbo, libpng, alsa-utils, Python **3.14**.
- **MCP venv:** `/storage/.local/opt/wyoh-mcp-2.2.0` was rebuilt in place for Python 3.14 from `src/wyoh/requirements-mcp-over-ssh.txt` (`mcp==2.2.0`).

## What changed for you

1. **root's home is `/root`, not `/storage`.** A root process that does not set `HOME` now looks under `/root`. The MCP server, started over `ssh luna` (root), did not find `~/.local/state/tanstfaafllm/wyoh/sway-vnc-session.json`, and refused to start ("the named Wyoh Sway/WayVNC service is not ready"). It works with `env HOME=/storage …` in the SSH command. Your harness, or the server's default descriptor path, needs that.
2. **Failed binds in `gpudriver`** (harmless for Sway): `libGLESv1_CM.so.1` and `libMaliOpenCL.so.1` do not exist here; `/usr/lib32` does not exist. The GLES-only **SDL2** is not applied, because Arch Linux ARM's `sdl2-compat` is `libSDL2-2.0.so.0.3200.74`, not `…3200.10`. That may matter for the calculator and ECWolf.
3. **Seen in the journal, not investigated:**
   - `wyoh-gamepad: focus subscription: [Errno 2] No such file or directory`, while the gamepad itself attached;
   - swaybar's tray reports no user bus.
4. **Not checked yet:** the menu (fuzzel and wtype are Debian binaries on `STORAGE`), the Slate and Kroko dictation, the Wi-Fi panel, the keyboard (`wvkbd-luna`), and the apps. Your live tests (`WYOH_LUNA_LIVE=1`) are the right check, with the `HOME` caveat above.

The session as `michael` (devices, groups, seat) is still open, as in your note.
