# ArchR text-mode boot and local-console runbook

**Question:** How can the disposable ArchR card boot directly into its built-in
local shell rather than Sway/EmulationStation, without changing its root
filesystem or panel overlay?

## Decision

Use the kernel argument `systemd.unit=textmode.target` in the sole active
`APPEND` line of `BOOT/extlinux/extlinux.conf`.

Mounted-card evidence establishes that `textmode.target` starts the image’s
built-in `shell.service`, which is bound to tty1. Normal `archr.target` starts
the graphical path instead. This replaces only the boot target for one card;
it does not install a getty or alter F2–F12.

## User-run procedure

From the repository, while the confirmed disposable ArchR BOOT partition is
mounted at `/run/media/michael/ARCHR`:

```bash
./worklines/luna/scripts/enable_archr_textmode_boot.sh /run/media/michael/ARCHR
```

The script requires the expected `extlinux/extlinux.conf`, refuses an existing
`systemd.unit=` override or an ambiguous APPEND layout, and makes this
same-directory backup before writing:

```text
extlinux/extlinux.conf.tanstaafllm-before-textmode
```

It changes exactly one line by appending:

```text
systemd.unit=textmode.target
```

Boot Luna with the USB keyboard connected. The expected result is the built-in
root shell on tty1, instead of Sway/EmulationStation. This is an unrestricted
local shell on a disposable experimental card; do not leave the card in this
mode outside a physically controlled experiment.

## Return to graphical boot

With the card mounted again, run:

```bash
./worklines/luna/scripts/enable_archr_textmode_boot.sh --restore /run/media/michael/ARCHR
```

The command restores the exact saved `extlinux.conf`. It does not touch the
panel overlay or the ArchR root filesystem.

## Console first checks

At the expected shell, establish the route before touching network state:

```sh
id
tty
uname -a
```

The acceptance condition is `uid=0` and `/dev/tty1`, demonstrating that the
textmode service—not a blank VT—has started.

## Applied result — 2026-10-03

The user green-lit this change and the script was run against the mounted
disposable BOOT partition. It created
`extlinux/extlinux.conf.tanstaafllm-before-textmode`; bytewise comparison proves
that backup matches the former active entry. The active entry contains exactly
one additional final argument: `systemd.unit=textmode.target`.

`pytest -q --timeout=30 test/luna/test_enable_archr_textmode_boot_script.py`
passed (`3 passed`). The panel overlay and ArchR root partition were not
changed. The next physical boot must confirm the tty1 shell.
