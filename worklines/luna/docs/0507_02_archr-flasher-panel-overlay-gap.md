# Arch R Flasher difference — missing R36 Ultra panel overlay

**Question:** Is the current ArchR write different from the earlier use of the Arch R Flasher, and does that explain the apparent non-boot?

## Answer

Yes. The current archive-and-flash script correctly verifies the selected
`ArchR-R36S.aarch64-20260709-clone.img.gz`, decompresses it, and writes those
same base-image bytes to the whole disposable card. That raw write is an
officially supported manual installation method.

However, the Arch R Flasher is not merely an imager. After it writes the base
image, it mounts the BOOT partition and installs the selected panel overlay as
`overlays/mipi-panel.dtbo`. It can generate a custom panel overlay by importing
the stock DTB. The base clone automatically selects a board DTB, but panel
initialisation is a separate layer.

The raw script omitted that overlay stage. On this R36 Ultra, the resulting
black/non-visible boot is therefore expected as a display-configuration
possibility, not proof that the ArchR system failed before booting.

## Confirmed transition state

The user-run script did complete its preservation stage before the card was
put into Luna. The retained checkpoint is:

```text
/data/michael/tanstaafllm/luna-images/darkosre/checkpoints/
luna-r36-ultra-darkosre-720x720_20261002_233847.img.zst
```

Its accompanying manifest and SHA-256 record are present. The preserved
factory DTB needed by the Flasher’s custom-overlay path is available locally
at `worklines/luna/data/r36-ultra.dtb` (108 KiB).

## Correct next action — no reflash

1. Return the ArchR card to Termidor and mount its BOOT partition.
2. Open **Arch R Flasher**, select its **Overlay** mode for the existing card,
   and use **Import DTB** with `worklines/luna/data/r36-ultra.dtb`.
3. Let it generate and install `overlays/mipi-panel.dtbo`; this alters the
   ArchR BOOT partition only.
4. Eject the card, then retry the USB-keyboard first boot.

Do not copy the stock DTB directly into ArchR, and do not select an arbitrary
panel. If the Flasher cannot generate or apply the overlay, stop and preserve
its reported error; the current corrected dArkOS checkpoint remains the
rollback source.

## Sources

- [ArchR README](https://github.com/archr-linux/Arch-R) — manual raw flashing is supported, while board DTB selection and panel overlays are separate.
- [Arch R Flasher](https://github.com/archr-linux/archr-flasher) — documents the post-write BOOT mount and `mipi-panel.dtbo` injection, including custom overlay generation from a stock DTB.
