> **Freshness:** 🟡 historical · **Written:** 2026-10-04 · **Checked:** 2026-10-31 · **Step:** luna 5.8 ✅



> **Outcome (2026-10-04):** the SDIO enumeration failure recorded here was traced to ArchR's device tree treating the Wi-Fi chip-enable pin as an SD card-detect input. It was fixed by the `wifi-rk915.dtbo` overlay (see `0508_03` and `0508_04`).
## Additional Phase 1 evidence from user-supplied console photographs

The user then supplied photographs of the same physical tty1 session:

- `ip link` lists only `lo`; `iw dev` produces no wireless-device output.
- `lsmod | grep -Ei 'rk915|wlan|cfg80211|mac80211'` returns no matching
  modules. In particular, the image's installed `rk915` module is not loaded.
- The filtered `dmesg` output contains generic Rockchip MMC-controller setup,
  the removable SD card (`mmc1`) discovery, and the kernel-overlay firmware
  staging message, but no RK915 bind, SDIO Wi-Fi device, Wi-Fi firmware load,
  WLAN, or rfkill event.
- `iwd.service` (wireless daemon 3.10) and `connman.service` (1.43) are both
  active. ConnMan's recorded network setup names only the loopback interface.

## Current classification

This rules out a failed iwd/ConnMan start as the immediate cause. The failure is
currently below those services: the RK915 SDIO device is not becoming a network
interface, so the next read-only evidence must check rfkill and the live
SDIO/MMC/device-tree and module-autoload paths. No conclusion about a missing
or incompatible driver is justified: the mounted-image inspection previously
proved that the matching module and firmware are present.

The initial interface-only observation left rfkill and the detailed iwd/ConnMan
views uncollected. The subsequent evidence below resolves the activation-layer
question; ConnMan technology/service listings and journal detail remain
optional and cannot make a missing SDIO device appear.

## Decisive SDIO and device-tree evidence

A further user-supplied tty1 photograph establishes the hardware-discovery
state without changing it:

- `rfkill list` has no output.
- `/sys/class/mmc_host` contains both `mmc1` (`ff370000.mmc`) and `mmc2`
  (`ff380000.mmc`), so the controller used by stock Luna's Wi-Fi path exists
  in the running kernel.
- `/sys/bus/mmc/devices` contains only `mmc1:0001`, the removable SD-card
  function. It contains no factory-equivalent `mmc2:0001` function.
- `/sys/bus/sdio/devices` is empty.
- Searches of the live device tree find neither `wlan-platdata` nor a node
  matching `*wlan*`.

## Refined classification

The driver package is present but has nothing to bind: no SDIO function is
being enumerated on the Wi-Fi host. That is a runtime device-enumeration
failure below iwd and ConnMan. The absent `wlan-platdata` name is a useful
clue because stock Luna uses it, but it is not proof that the ArchR DTB lacks
every equivalent Wi-Fi property: the property may be represented differently,
not applied, or its power/reset/MMC dependencies may be failing. Loading
`rk915.ko` manually would not repair an absent SDIO device.

The safe next phase is a **read-only DTB comparison** of the preserved factory
R36 Ultra DTB and the running/selected ArchR DTB, specifically around
`ff380000.mmc` and `wlan-platdata`. A new overlay must not be guessed or
installed until that difference is evidenced.
