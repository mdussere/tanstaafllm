# ArchR text-console and AZERTY confirmation

> **Freshness:** 🟡 historical · **Written:** 2026-10-04 · **Checked:** 2026-10-31 · **Step:** luna 5.7 ✅

**Question:** Did the prepared ArchR textmode boot override and offline French
AZERTY loader work on the physical R36 Ultra?

## Observed result

On 2026-10-03, the user booted Luna and confirmed both outcomes:

- the device reaches the built-in tty1 textmode shell (`tty` returns `/dev/tty1`); and
- the attached physical keyboard uses the expected French AZERTY layout.

This is physical-device evidence, not an inference from the mounted image.
It confirms the one-argument `textmode.target` boot override and the
TANSTAAFLLM `shell.service` pre-start `busybox loadkmap` addition work together
on this card.

## Boundary

The result does not establish internal Wi-Fi, SSH, or graphical frontend
behaviour. Those remain the scope of Step 5.8's read-only console collection.
The factory card remains untouched.

## Reversal

The two changes are independently reversible from a mounted card:

- restore graphical ArchR boot with
  `enable_archr_textmode_boot.sh --restore <ARCHR-BOOT-mount>`;
- remove only the AZERTY map/drop-in with
  `configure_archr_console_azerty.sh --restore <ARCHR_ROOT-mount> <STORAGE-mount>`.
