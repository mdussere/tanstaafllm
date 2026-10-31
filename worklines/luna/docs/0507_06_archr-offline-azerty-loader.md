# Offline French AZERTY loader for ArchR textmode

> **Freshness:** 🟡 historical · **Written:** 2026-10-04 · **Checked:** 2026-10-31 · **Step:** luna 5.7 ✅

**Question:** How can the ArchR textmode shell use a French AZERTY keyboard
when the image has neither `loadkeys`, `localectl`, `/etc/vconsole.conf`, nor
installed `kbd` keymaps?

## Evidence

Read-only inspection of the mounted ArchR root found no console-keymap stack:

- `/etc/vconsole.conf` and `/usr/share/kbd/keymaps/` are absent.
- `loadkeys` and `localectl` are absent from the target root.
- The target’s ARM64 BusyBox binary contains the `loadkmap` applet.

Surcouf has `loadkeys` 2.7.1 but not its map-data package. Its first attempt
against a newer upstream map failed during parsing (`syntax error, unexpected
ERROR`), before any Luna file was installed. To match the local parser and
avoid a package installation or any Luna network use, the complete official
`kbd` **v2.7.1** keymap data tree was cached outside Git at:

```text
/data/michael/tanstaafllm/luna-assets/kbd-keymaps-v2.7.1/keymaps/i386
```

It comes from `https://github.com/legionus/kbd.git` tag `v2.7.1`, commit
`f2c0d3185b300780f4f69abe3ff7493ec7634f39`. The selected `azerty/fr.map`
SHA-256 is `da1c27ccde8ceb034c53c6a2c279ddf3b2c510a4fbe9370248299978c713bf7b`.
The source tree retains its required AZERTY and Linux include files. The
newer cache remains untouched but is deliberately not used by this installer.

## Selected approach

The root-run host script uses the real Surcouf VT `/dev/tty1` only to compile
that source map with `loadkeys --bkeymap`; this output operation does not load
or alter Surcouf’s own keymap. It stores the resulting binary map on Luna’s
STORAGE partition and adds an `ExecStartPre` drop-in to ArchR’s existing
`shell.service`:

```text
/usr/bin/busybox loadkmap < /storage/.config/tanstaafllm/fr.bkeymap
```

Thus target BusyBox loads AZERTY before its tty1 root shell starts. No vendor
unit is edited, no package is installed, no Luna network is used, and no
password is involved.

## User-run root procedure

With the disposable card mounted as shown, run:

```bash
sudo ./worklines/luna/scripts/configure_archr_console_azerty.sh \
  /run/media/michael/ARCHR_ROOT \
  /run/media/michael/STORAGE
```

Then safely eject and boot the existing textmode configuration. Test the layout
without needing accented characters:

```sh
printf 'physical A should produce: q\n'
printf 'physical Q should produce: a\n'
```

## Restore

With the card mounted again:

```bash
sudo ./worklines/luna/scripts/configure_archr_console_azerty.sh --restore \
  /run/media/michael/ARCHR_ROOT \
  /run/media/michael/STORAGE
```

Restore removes only the TANSTAAFLLM-created drop-in and binary keymap. It does
not change the textmode boot override, panel overlay, network state, or vendor
files.
