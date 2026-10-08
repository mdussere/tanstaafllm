# Note from Wyoh — the ArchR card's limits, missing software, and a storage layout to fix them

**From:** Wyoh workline
**To:** Luna workline
**Date:** 2026-10-04
**Status:** coordination note and request. It changes nothing on the card and green-lights no Luna step. Luna owns the image; Wyoh only states what it needs.

## Why this note

The user wants Luna to become a workable multi-user Linux machine, not an appliance: at least 20 GB on `/`, a real `/home`, several users, and `/storage` kept only for large data such as models. Wyoh hit the current image's limits while reproducing its `luna-pi` session on the physical panel (Wyoh Step 4.7, [result](../../wyoh/docs/0407_01_luna-real-display-session.md)). The user stopped further installs: there is no room to install, and the image needs reworking first.

## 1. What the current card is

Facts below were observed read-only over `ssh luna` on 2026-10-04 (ArchR 20260709, kernel 6.12.94, glibc 2.40).

| Partition | Size | Filesystem | Mounted | Use |
| --- | --- | --- | --- | --- |
| `mmcblk1p1` | 256 MiB | vfat, label `ARCHR` | `/flash`, **read-only** | kernel, DTBs, `overlays/` (`mipi-panel.dtbo`, `wifi-rk915.dtbo`), `extlinux/` |
| `mmcblk1p2` | 4.5 GiB | ext4, `ARCHR_ROOT` | `/`, read-write | the OS: `/usr` alone is 4.2 GiB; **136 MB free (97% used)** |
| `mmcblk1p3` | 53.5 GiB | ext4, `STORAGE` | `/storage`; also `/var/log` | root's home, all persistent state, ROMs; 290 MB used |
| `zram0` | 512 MiB | — | — | compressed swap |

The card is 58.2 GiB in total. Other mounts: `/var`, `/tmp`, and `/run` are tmpfs.

## 2. Limitations seen so far

ArchR is a LibreELEC-style console appliance. It works as designed, but that design conflicts with what Luna is now asked to be.

| # | Limitation | Consequence |
| --- | --- | --- |
| L1 | `/` is 4.5 GiB and 97% full | No package can be installed system-wide. Wyoh had to put everything under `/storage`. |
| L2 | Only `root` exists, with home `/storage`. There is no `/home`, no `useradd`/`adduser`, and `/etc/shadow` links to `/storage/.cache/shadow` (so `passwd` fails, see `0508_05`) | No multiple users. Wyoh's Sway, the MCP server, and every client run as root. |
| L3 | `/var` is tmpfs, with persistence patched by per-service links and drop-ins | State is lost unless someone wires it up: iwd and sshd needed fixes (`0508_05`), and each new service will need the same. |
| L4 | pacman sees only ArchR's own `[archr]` repository | No `wtype`, `wayvnc`, `wmenu`, `gcc`, `make`, `git`, `lsblk`/`findmnt`, or `fc-list`. Arch Linux ARM packages are not available through pacman. |
| L5 | No GPU driver: no `panfrost`, no `/dev/dri/renderD128`; EGL reports software rendering | Sway composites on the CPU: 0% when idle, but about 80% of a core while a full window redraws. |
| L6 | The boot partition is mounted read-only at `/flash` | Overlay and boot changes need a remount or offline edits (Luna already handles this). |
| L7 | Default boot is the EmulationStation kiosk (`archr.target`); the card currently boots `textmode.target` through `extlinux` | No general desktop session. Wyoh runs its own unit beside ArchR's. |
| L8 | Python 3.13 has no pip; a venv's pip fails while byte-compiling (needs `--no-compile`) | Python tooling is fragile. |
| L9 | No `agetty`, so only tty1 has a shell (`0507_04`) | No logins on other virtual consoles. |
| L10 | Time zone is UTC: `/etc/localtime` points to `/var/run/localtime` on the tmpfs | Clocks show UTC. Cosmetic, but it shows the same `/var` problem. |

## 3. Software Wyoh needs on Luna

| Need | Why | Today |
| --- | --- | --- |
| Sway, swaybar, swaybg, grim, foot | Wyoh v0 session and evidence | present (Sway 1.11, foot 1.19.0, grim 1.4.1) |
| A launcher (`wmenu` or `bemenu`) | person-facing launcher | `bemenu` 0.6.15 present, and it works with `wtype` |
| `wtype` (or a persistent virtual keyboard) | MCP text input | missing; a Debian 13 arm64 binary sits in `/storage/.local/opt/wyoh-tools/bin` |
| *Not* a GTK editor | a GUI toolkit app costs far more than the job needs. On `luna-pi`, `mousepad` (GTK 3) used 48 MB RSS for an empty document, against 15 MB for `foot` running `nano` (11 + 4 MB) | Text editing uses terminal programs in `foot` (`nano` and `vim` are already on ArchR). Do not add GTK applications for Wyoh. |
| WayVNC | optional development view and second observer | missing |
| Python 3 with a working pip, venv, and `mcp==2.2.0` | the Wyoh MCP server | works only with `--no-compile` |
| seatd or logind seat for a normal user | run Sway as a user, not root | seatd present but configured for `-u root` |
| Mesa with Panfrost and the `panfrost` kernel module | GPU composition | missing |
| `gcc`, `make`, `git`, `util-linux`, `fontconfig` tools | development (Mannie) and diagnostics | missing |

## 4. Proposed storage rebalance

Requirement: at least 20 GB on `/`, a real `/home`, and `/storage` only for bulk data. Proposal for the current 58.2 GiB card:

| Partition | Size | Filesystem | Mount | Holds |
| --- | --- | --- | --- | --- |
| p1 | 512 MiB | vfat | `/boot` | kernel, DTBs, `overlays/`, `extlinux/`; ArchR's `/flash` contents |
| p2 | **24 GiB** | ext4 | `/` | OS and packages, including a **persistent `/var`** |
| p3 | 8 GiB | ext4 | `/home` | user homes |
| p4 | rest, about 25.5 GiB | ext4 | `/storage` | models, ROMs, datasets, recordings, evidence |
| — | 512 MiB to 1 GiB | zram | swap | keep zram; no swap partition on SD |

Sizing reasons: `/` gets more than the 20 GB floor so that pacman's cache, compilers, Mesa, and development packages fit with margin. `/home` stays small because large files belong in `/storage`. Sizes can move once Luna confirms the final card size.

## 5. Directory plan — what each directory is for

| Directory | Purpose | Persistence | Owner |
| --- | --- | --- | --- |
| `/boot` | kernel, DTB, DT overlays, bootloader config | persistent, p1 | Luna |
| `/usr`, `/usr/lib`, `/usr/share` | distribution packages only; never hand-installed | p2 | pacman |
| `/etc` | system configuration, including systemd units in `/etc/systemd/system` | p2 | Luna (system), each workline (its own units) |
| `/var` | logs, pacman cache, service state (`/var/lib/iwd`, `/var/lib/sshd`, …) | **persistent on p2**, no tmpfs | system |
| `/opt/tanstaafllm/<component>` | system-wide TANSTAAFLLM components and pinned tools not packaged by the distribution (e.g. `wyoh/` MCP server, a pinned `wtype`) | p2 | the component's workline |
| `/srv/tanstaafllm` | read-mostly service data shared between users, if needed later | p2 | system |
| `/home/<user>` | dotfiles, per-user venvs (`~/.local`), per-user Sway config, user systemd units | p3 | the user |
| `/storage/models` | model weights (Mycroft ASR, Mike), never in Git | p4 | shared, group `tanstaafllm` |
| `/storage/roms` | emulation content, if EmulationStation stays | p4 | shared |
| `/storage/data`, `/storage/results` | datasets, recordings, on-device evidence | p4 | shared |
| `/tmp`, `/run` | scratch and runtime sockets (e.g. a Sway IPC socket in `/run/user/<uid>`) | tmpfs | system |

Proposed users: `michael` as administrator in `wheel` with sudo, a normal home, and SSH key login; `root` for SSH only until sudo works. One unprivileged session user (for example `luna`) runs the graphical session, auto-logged in on tty1, so Sway, Wyoh, and its clients stop running as root. Later service users (`mike`, `mycroft`) can own their services if the worklines need them.

## 6. Options for getting there (Luna's decision)

1. **Rework the ArchR card in place:** grow `/`, add partitions, move `/var` off tmpfs, add `/home`, `shadow`, and user tooling. This fights the image's design (L2, L3, L4) and leaves pacman limited to `[archr]`.
2. **Build a conventional root filesystem on ArchR's proven boot path:** an Arch Linux ARM aarch64 rootfs, or Debian arm64, with ArchR's 6.12 kernel, the R36 Ultra DTB, and Luna's `mipi-panel.dtbo` and `wifi-rk915.dtbo`. This gives normal users, a persistent `/var`, the full package repositories, and Mesa/Panfrost to try. It costs the move of the kernel modules and firmware (including `rk915.ko`) and of the Wi-Fi/panel work.

**Wyoh recommends evaluating option 2.** Luna's boot, panel, and Wi-Fi knowledge transfers, while the appliance constraints do not. It is Luna's call, made under its own green light.

## 7. Wyoh's footprint on the current card

So that a reflash or rework loses nothing unexpected:

| Path | Size | What |
| --- | --- | --- |
| `/storage/.config/system.d/wyoh-sway.service` | — | Wyoh's Sway unit: not enabled, currently stopped |
| `/storage/.local/share/tanstfaafllm/wyoh/` | 88 KB | deployed `src/wyoh/` (reproducible with `make wyoh-luna-deploy`) |
| `/storage/.local/opt/wyoh-mcp-2.2.0/` | 48 MB | MCP SDK venv (reproducible) |
| `/storage/.local/opt/wyoh-tools/bin/wtype` | 68 KB | Debian `wtype 0.4-3+b1` arm64 binary |
| `/storage/.local/state/tanstfaafllm/` | 1.1 MB | descriptor and screenshots (evidence already copied off) |

All of it can be deleted. Nothing in ArchR's own files was changed by Wyoh. A partial `mousepad`/`gtksourceview4` copy that landed after the user stopped the install was removed on 2026-10-04.

## 8. What Wyoh needs back

- A card layout and directory plan that Luna adopts (this note's or a better one), recorded in the Luna plan.
- A normal user able to run Sway on `DSI-1` through seatd or logind, and `sudo` for administration.
- Room on `/` and a package source for the software in section 3.
- Notice when the new image boots with Wi-Fi and SSH, so Wyoh can redeploy and rerun the Step 3.7 scenario. It will use `nano` in `foot` instead of `mousepad`, plus a second observer and the person-at-keyboard steps (through a kernel `uinput` keyboard; `/dev/uinput` exists).

## 9. Addendum — after the Step 6 reshape (2026-10-05)

Wyoh reran its full scenario on the reshaped card (24 GiB `/`, `/home`, 26 GiB `/storage`) and it passed; see `worklines/wyoh/docs/0407_01_luna-real-display-session.md`. The reshape answers section 4. Sections 2 (L2–L5, L8–L10), 3, and 8 still stand: there is still only `root`, a tmpfs `/var`, `[archr]`-only pacman, and no GPU driver. New observations:

| # | Observation | Consequence |
| --- | --- | --- |
| L11 | There is no terminfo database (no `/usr/share/terminfo`), and no `tic` or `infocmp` | Terminal programs run without a description of their terminal; `TERM=foot` is unknown. |
| L12 | ArchR's `nano` 8.5 (`--disable-utf8 --disable-wrapping …`) catches SIGWINCH but keeps drawing 80×24 after a terminal resize, even with a `foot` terminfo supplied | `nano` is unusable in a tiled window. Wyoh uses `vim` 9.1 instead, which resizes correctly. |
| L13 | `/dev/uinput` is usable by root, and Sway treats a uinput keyboard like the USB keyboard (French layout, `--to-code` bindings) | Good: this is how Wyoh tests "a person at the keyboard". A future persistent input path for Mike can use it too. |
| L14 | `/home` now holds a `roms` directory (128 entries) owned by root | Probably moved there by the reshape or by ArchR. Section 5 placed ROMs in `/storage/roms`; Luna may want to confirm which. |

Section 3 additions: a terminfo database (the `ncurses` terminfo entries, at least `foot`, `xterm-256color`, and `linux`). Withdrawn: `mousepad`/GTK, and WayVNC on Luna. The MCP screenshot is the evidence, and WayVNC would need a second FFmpeg 8 stack.

### Correction to L5 (2026-10-05)

L5 ("no GPU driver") is wrong. ArchR selects and loads the GPU driver in its graphical autostart (`/usr/lib/archr/gpudriver --start`: `mali_kbase` and bind mounts of ARM's `libmali`, default `gpu.driver=libmali`). The `textmode.target` boot used on this card skips that autostart. Without it, Sway falls back to software rendering, and **the DSI panel stays black** even though the compositor runs. Wyoh's unit now runs ArchR's step itself. For Luna's base-system decision: whatever replaces or extends ArchR must keep an explicit GPU-driver step, independent of the EmulationStation autostart.

### Update to section 8 (2026-10-07)

User decision: Luna is a single-user device with no keyboard, so the Wyoh session **stays root for now**, with no password login. Wyoh therefore withdraws, for the time being, its request for "a normal user able to run Sway". If a non-root session user comes later, it should log in automatically (no password), with seatd or logind giving it the display and input, and the Mali GPU-driver step should stay a root system step before the session.

## 10. Addendum (2026-10-09): MIME database, SSH penalties, Wi-Fi link

| # | Observation | Consequence |
| --- | --- | --- |
| L15 | ArchR has no shared-mime-info database (`/usr/share/mime/mime.cache`), and its gdk-pixbuf `loaders.cache` lists a loader directory that does not exist (PNG is built in) | Image loading through gdk-pixbuf/GIO fails ("Couldn't recognize the image file format"): `swaybg` could not show any picture. Wyoh deploys its own `mime.cache` in its `XDG_DATA_DIRS`; a system-level `shared-mime-info` would fix it for every program. |
| L16 | OpenSSH 9.8 on Luna applies `PerSourcePenalties` (noauth, grace-exceeded, …) | Bursts of short or interrupted connections from the development host get refused or timed out for minutes. Wyoh now multiplexes one connection. A LAN exemption (`PerSourcePenaltyExemptList`) is Luna's call. |
| L17 | Wi-Fi (RK915): signal −62 dBm, receive 13 Mbit/s (MCS 1), about 1,500 retries, measured throughput about 160 KB/s, with stalls over 60 s | Remote testing and screenshot transfer are slow and intermittent. Worth a look on the Luna side (channel, power save, driver). |
