# ArchR first-boot keyboard and virtual-terminal observation

> **Freshness:** 🟡 historical · **Written:** 2026-10-04 · **Checked:** 2026-10-31 · **Step:** luna 5.7 ✅

**Question:** What does the USB-keyboard behaviour establish after ArchR reaches its graphical frontend, and does the black F2 screen provide a usable console?

## User observation

On the R36 Ultra with ArchR booted to its graphical interface:

- The operating system reaches the graphical frontend, but its network settings
  are not presently usable/configurable.
- `Ctrl`+`Alt`+`F2` changes the display to a black screen.
- `Ctrl`+`Alt`+`F1` returns it to the graphical frontend.
- `Ctrl`+`Alt`+`F3` through `F12` have no visible effect.
- `Ctrl`+`Alt`+`Delete` has no visible effect.

## What this establishes

The simple USB adapter and keyboard are now a demonstrated input path. The
F1/F2 round trip requires the keyboard to be received and a Linux
virtual-terminal switch to be acted on. It does **not** establish a shell.

The black F2 screen initially left two possibilities: no login service
(`getty`) on that terminal, or invisible console text with the current
KMS/panel setup. Mounted-card inspection resolves the first possibility:
ArchR contains neither `getty@.service` nor `autovt@.service`. Its only normal
shell is `shell.service`, bound to `/dev/tty1` and wanted only by the
non-default `textmode.target`. Normal boot selects `archr.target`, which
requires `graphical.target` and starts the Sway/EmulationStation path. Thus no
shell is configured on F2–F12, and the black F2 state is expected.

The mounted card does **not** disable `Ctrl`+`Alt`+`Delete`:
`ctrl-alt-del.target` is the normal alias to `reboot.target`, with no local
override. Its lack of runtime effect therefore means the combination was not
observed by the kernel/system manager as that request, or was intercepted
before reaching it. It is not a safe recovery mechanism for this experiment.

The BOOT partition contains `overlays/mipi-panel.dtbo` (3,440 bytes, mtime
2026-10-03 00:38), so this card now has a panel overlay and reaches the
graphical frontend. The overlay file alone cannot prove which generator or
stock DTB produced it.

ArchR describes an appliance boot flow in which systemd launches autostart
logic and then EmulationStation; it does not promise an enabled visible getty
on every VT. [ArchR README](https://github.com/archr-linux/Arch-R)

## Boundary and next evidence

No network conclusion follows from the unavailable graphical network settings;
the Wi-Fi device, driver binding, connection-manager state, and UI integration
remain unobserved on this ArchR boot.

The keyboard-interruption objective is met, but this card needs a deliberate,
reversible textmode/shell-entry design before it can provide a local console.
That would require a new explicit green light and must not alter networking,
install packages, or replace the panel overlay.
