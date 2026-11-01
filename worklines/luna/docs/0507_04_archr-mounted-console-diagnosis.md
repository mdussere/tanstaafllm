# ArchR mounted-card console configuration result

> **Freshness:** 🟡 historical · **Written:** 2026-10-04 · **Checked:** 2026-10-31 · **Step:** luna 5.7 ✅

**Question:** Why does `Ctrl`+`Alt`+`F2` show a black screen while F1 returns
to the ArchR frontend, and can the mounted card explain it?

## Read-only result

The mounted disposable ArchR card has:

- BOOT at `/run/media/michael/ARCHR` and root at
  `/run/media/michael/ARCHR_ROOT`.
- `default.target` aliased to `archr.target`; that target requires both
  `multi-user.target` and `graphical.target`.
- A Sway service installed as the graphical display manager and the ArchR
  frontend/autostart service path.
- No installed `getty@.service` or `autovt@.service`, and no local
  `/etc/systemd/system` unit override that would add one.
- A single built-in ordinary shell service, `shell.service`, bound to
  `/dev/tty1`. It is wanted only by `textmode.target`, which is not the
  default target.
- No active logind configuration override: the persistent
  `/storage/.config/logind.conf.d/` directory contains only its README.

The kernel command line retains `console=tty0`, so a framebuffer console has
not been globally removed. Nevertheless, nothing is configured to start a
shell on F2 through F12.

## Explanation

The observed F1/F2 switch proves that the keyboard and VT switching work. F1
returns to the graphical Sway/EmulationStation session; F2 switches to an
otherwise unused terminal, which appears black because no getty or shell is
attached. F3–F12 behave the same way or are not visibly switched, but none
have a configured login service.

`Ctrl`+`Alt`+`Delete` is *not* disabled in the static system image:
`ctrl-alt-del.target` aliases `reboot.target`. Since it showed no action at
runtime, the remaining possibilities are input/compositor interception or the
combination not being delivered as the kernel’s Ctrl-Alt-Del event. Static
inspection cannot distinguish those cases.

The needed panel overlay now exists at `BOOT/overlays/mipi-panel.dtbo` (3,440
bytes; SHA-256
`62449b4b6f87ec5a7041d282a1f883d24c8f1c425a83d47dcb640fde69e149a9`). Its
presence supports the successful graphical boot, but does not by itself prove
which generator or source DTB created it.

## Consequence

This card needs a deliberate, reversible textmode-entry design before it can
be used as a local console. Do not guess at enabling a getty, changing default
targets, configuring Wi-Fi, or replacing the panel overlay without a new
explicit green light.
