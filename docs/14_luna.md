# 14 · Luna, the device

> "The Moon is a harsh mistress", and so is a 30-euro handheld. Every component of this project lives inside its limits.

## In one sentence

Luna is the R36 Ultra itself: what its hardware can do, the card it boots from, and the careful bring-up that turned a retro-gaming console into an ordinary Linux machine, which the agents reach over SSH and Mannie now operates.

![Luna's cards](img/luna-card.svg)

## The hardware

| Part | Fact |
|---|---|
| SoC | Rockchip RK3326: 4 × Cortex-A35, Mali-G31 MP2 GPU |
| Memory | 983 MiB of RAM, shared with the GPU |
| Screen | 720 × 720 DSI panel |
| Controls | 17 buttons (cross, A/B/X/Y, L1/L2/R1/R2, Select/Start/FN, two stick clicks) and two sticks |
| Network | RK915 Wi-Fi, 2.4 GHz |
| Audio | A speaker and a headset jack. The jack's microphone gives no signal, so dictation uses a USB-C headset. |
| GPU APIs | ARM's `libmali`: OpenGL ES and **OpenCL**; **no Vulkan** |

## The system

- **Two systems in one card.**
  - **Boot:** ArchR, an Arch-based handheld distribution. It provides the kernel (6.12), the panel and Wi-Fi descriptions, the start-up code, and the drivers.
  - **Everything else:** **Arch Linux ARM**, a plain, general-purpose Linux, since 2026-10-25. [The appendix](#appendix-from-archr-to-arch-linux-arm) tells why and how.
- **The Seal.** The factory card is archived and never written. The working card was backed up whole, with a verified checksum, before the change of system.
- **The card is reshaped:**
  - `/` is 24 GiB, holding Arch Linux ARM;
  - `/home` is 8 GiB, holding the user's account `michael`;
  - `/storage` is 26 GiB, holding the cell's code, models and apps under `/storage/.local`.
- **The machine boots straight into Wyoh's desktop.** The user's text console stays on the first virtual terminal. Ctrl+Alt+F1 on a USB keyboard reaches it, even when the desktop is stuck.
- **Access:**
  - SSH by key only, with a stable host key;
  - `michael` has a real `sudo`, and root logs in by key only;
  - the agents share Luna one session at a time, through Professor's token (`worklines/luna-access.md`), and reboot it after each test series;
  - since 2026-10-25, Mannie operates Luna's system: packages, services and accounts.

The full story of the first bring-up, card by card, is in [`03_r36-ultra-bring-up-story.md`](03_r36-ultra-bring-up-story.md). It covers the black screen, the hunt for the Wi-Fi driver, the router that had a say, and the full root partition.

## Why it is like this

- **Keep what ArchR does best.** ArchR's boot path, kernel, display and Wi-Fi work on this clone. That was hard-won, so they stay untouched.
- **Use a normal Linux for everything else.** A handheld gaming system runs everything as root, and the cell needs a Linux with users, `sudo` and a full package repository. See the appendix.
- **Checkpoint before every risky change.** Both the reshape and the change of system started from a full image of the card, checked by SHA-256, with a way back.
- **Measure on the device.** Desk and `luna-pi` figures are hints. Luna's slow cores and 1 GiB are the real test.

## Status and limits

- **Live:**
  - boot, panel, Wi-Fi and SSH;
  - the Mali GPU driver;
  - Wyoh's desktop;
  - resident dictation with the USB-C headset;
  - the user account with `sudo`;
  - the keyboard rescue path.
- **Memory:** about **547 MiB** stay available with the desktop and resident dictation running. That is about 80 MiB less than under ArchR, mostly because the newer system services are larger. Trims are proposed.
- **Microphone:** the jack gives no signal, even with the factory codec values. A USB-C headset works.
- **Open after the change of system** (checks to do with the user):
  - the menu and the apps (Wolfenstein's graphics library needs a fix);
  - the Wi-Fi panel;
  - the desktop running as `michael` rather than root;
  - two small permission settings that failed at first boot.

**Sources:** `worklines/luna/plan_luna.md`, Steps 5, 6, 7 and 8; `worklines/mannie/plan_mannie.md`, Steps 6 and 7; study `worklines/mannie/docs/0701_01`; results `0604_01` and `0802_01`; [`03_r36-ultra-bring-up-story.md`](03_r36-ultra-bring-up-story.md).

---

## Appendix: from ArchR to Arch Linux ARM

*October 2026: how Luna got a normal Linux on top of a handheld's boot.*

### Why we had to

ArchR was chosen at bring-up because it boots R36 clones: it has the right kernel, the panel description and the Wi-Fi driver. Above that, it is a gaming distribution:
- everything runs as root;
- the home folder is `/storage`;
- `sudo` is only a stand-in that runs the command as the caller;
- its package repository, about 540 packages, has no `git`, `perl` or `tmux`.

For a while that was enough. The cell installed everything under `/storage/.local` and worked as root over SSH.

Then came the decision to **send Mannie to Luna**. Mannie, Claude Code with its whole harness, was to live on the handheld and operate it. An agent with that much power should not run as root. Mannie was to work as the user, `michael`, and raise its rights through `sudo` when needed, under the normal permission prompts.

On ArchR that was impossible. The `sudo` stand-in gave `michael` no root at all, and the repository had no real `sudo`, not even `git`. Every system change still had to be made as root from the desk computer.

### What we did

We kept ArchR where it is strong and replaced the rest:

| Partition | Before | After |
|---|---|---|
| `BOOT` | ArchR: kernel 6.12, start-up code, panel and Wi-Fi descriptions | **unchanged** |
| root `/` | ArchR's system | **Arch Linux ARM** (glibc 2.43, systemd 262, pacman), with ArchR's kernel modules and firmware carried over |
| `/home` | the user account | **unchanged** |
| `/storage` | the cell's code, models, apps and settings | **unchanged** |

The steps:

1. **Back up the whole card.** A raw image, with its SHA-256 checked again after decompression, plus archives of `/storage` and `/home`.
2. **Build the new root on the desk computer**, without root rights. It starts from the signed Arch Linux ARM archive. The packages are fetched and checked on the desk, then installed by Luna itself at first boot.
3. **Write only the root partition.** The new root keeps the old partition's label, so ArchR's start-up code mounts it without noticing the change.
4. **First boot.** It took about 3 minutes to install 290 packages. Wi-Fi and SSH came back first, with the same host key.
5. **Bring the desktop back.** Arch Linux ARM's open-source GPU driver (Panfrost) had given a black screen on this device earlier. So ArchR's Mali driver was copied across, and Sway now runs on it, as before.
6. **Add a rescue path.** The desktop moved to virtual terminal 7, and the user's console stays on terminal 1. A small service switches between them on Ctrl+Alt+F1…F12, even if the desktop hangs.

### What it changed

- **Gained:**
  - `michael` with a real `sudo`;
  - a full, signed package repository, with `git`, `gh` and `tmux`;
  - a Linux that behaves like any other, ready for Mannie to live on.
- **Paid:**
  - about 80 MiB of memory: newer system services, Sway 1.12 instead of 1.11, Python 3.14 instead of 3.13;
  - a few adjustments, such as Wyoh's tools rebuilt for the new Python, and root's home now in `/root` instead of `/storage`.
- **Kept:**
  - the boot, the kernel, the display, the Wi-Fi driver;
  - the SSH identity;
  - everything in `/storage` and `/home`.
- **Way back:** the full image taken just before the change.
