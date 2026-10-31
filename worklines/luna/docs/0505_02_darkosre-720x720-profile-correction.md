# dArkOSRE 720×720 profile correction

> **Freshness:** 🟢 current · **Written:** 2026-10-04 · **Checked:** 2026-10-31 · **Step:** luna 5.5 ⏳

**Question:** Why did the earlier `r36_config.ini` change not produce a 720×720 screen, and what is the smallest reversible correction on the disposable card?

## Review result

The mounted candidate is `/dev/sde`, with writable `BOOT` at `/run/media/michael/BOOT` and `ROOTFS` at `/run/media/michael/ROOTFS`.

The earlier offline script changed `ROOTFS/etc/r36_config.ini` from `640x480` to `720x720`. That was the wrong control layer: at boot, `r36_config` reads the DTB-provided hardware string, looks it up in `BOOT/dtb/r36_devices.ini`, and regenerates the video profile. Its recorded hardware string was `G80CA-MB V1.2-20250422 Panel 8`; that entry is `640x480`. The log records the resulting reversion from `720x720` to `640x480`.

The active root-BOOT DTBs exactly match the image's bundled G80CA Panel 8 profile:

| File | Active SHA-256 |
|---|---|
| `rg351v-uboot.dtb` | `d7cfe8a0dec06842e08ec3199fb648ead2c88ee735aa7b725eb298a78693a41b` |
| `rk3326-r36s-linux.dtb` | `6f8bfe5d92050ec37795b0b0f7149e64bd25bc8e5ff5720e0c3b1bc2c2093285` |

This proves that dArkOS booted the image default for the wrong family; it does not establish that a 640×480 panel is physically fitted. Independent R36 Ultra hardware references describe the 4-inch square panel as 720×720.

## Available profile and limitation

The flashed 04262026 beta contains `GR36-MB V1.1-20250422`, whose device-map entry is `720x720`, with a paired U-Boot DTB, Linux DTB, and 720×720 logo. It does **not** contain the advertised exact entry `GR36S-MB V1.4-2025-07-30 R36 Ultra`. The official upstream README and beta status still advertise that exact Ultra entry, but the public `main` tree's clone-profile directory does not expose it as of 2026-10-02. An attempted official raw-file retrieval therefore returned HTTP 404.

The bundled GR36 pair is consequently the smallest available fallback, not a verified board identity. It is preferable to the G80CA pair because dArkOS maps G80 profiles to 640×480, while the GR36 profile maps to 720×720. Its different model string also allows the early configuration service to select the bundled 720×720 video profile naturally.

## Reversible experiment

`scripts/select_darkos_ultra_display_fallback.sh` selects only the bundled GR36 fallback. Before copying, it creates `BOOT/tanstaafllm-before-ultra-display/` containing the original two DTBs and `logo.bmp`; it refuses to overwrite that rollback directory. It then replaces only the BOOT-root DTB pair and boot logo, compares each replacement bytewise, and syncs the card. It does not change ROOTFS, Wi-Fi, SSH, or any factory reference artefact.

If the fallback does not boot or behaves incorrectly, return the card to Termidor and restore those three files from that directory before attempting a different profile. Do not substitute the factory EmuELEC DTB.

## Applied result — 2026-10-02

The fallback script completed against the mounted `/dev/sde1` BOOT partition.
The active files byte-match their GR36 sources:

| File | Active SHA-256 |
|---|---|
| `rg351v-uboot.dtb` | `036b61d1ba1ae81d5f7e39a2a110040ae37f8b3c20b2d9eefd08d2898b7531bc` |
| `rk3326-r36s-linux.dtb` | `ff27be335d183b15d6b1894c88872cbefd5478bcbd2b2e0157e413ff8bccbfe5` |
| `logo.bmp` | `914a43dc2975a914a2b18f8e47e0fa69af19491d8306b3e832dc4d5c95166037` |

The rollback directory contains the original G80CA pair with the hashes shown
above and its original logo. This is installation evidence only. The card has
not yet been booted with this profile, so display correctness, UI stability,
controls, audio, Wi-Fi, and SSH remain unproven.

## Post-fallback boot check — 2026-10-02

The user confirmed that Luna now renders at 720×720. The display correction is
therefore successful. The UI failure is unchanged: an approximately one-second
EmulationStation loading sequence (including `favorites`, `kodi`, and
`Starting UI`), followed by the PICO-8 interface, then roughly three seconds
of black screen, repeats indefinitely without a usable input interruption.

Termidor's only newly visible neighbour was `192.168.50.169`
(`c8:a3:e8:49:bc:9f`). A key-only, non-interactive SSH identity query as `ark`
received `Connection refused` on TCP/22. This proves only that the reachable
neighbour is not accepting SSH; it does not identify it as Luna. The old Luna
address is absent from the neighbour table. No Luna state changed during this
probe.

## Sources

- [dArkOSRE firmware-installation guide](https://github.com/southoz/dArkOSRE-R36/wiki/Firmware-Installation) — DTB selection is a BOOT-partition operation; G80CA Panel 8 is a distinct profile.
- [dArkOSRE device map](https://github.com/southoz/dArkOSRE-R36/blob/main/files/BOOT/dtb/r36_devices.ini) — G80CA Panel 8 is 640×480 and GR36 is 720×720.
- [dArkOSRE current support list](https://github.com/southoz/dArkOSRE-R36) — advertises `GR36S-MB V1.4-2025-07-30 R36 Ultra`, absent from the public profile tree inspected above.
- [Handhelds Wiki R36 Ultra entry](https://www.handhelds.wiki/R36_Ultra) — 720×720 hardware specification; treated as corroborating product evidence, not a DTB source.

## Neighbour exclusion update — 2026-10-02

After the SSH probe, the user shut Luna down and verified that
`192.168.50.169` continued to answer ping. It is conclusively not Luna; the
active Luna DHCP address remains unknown.
