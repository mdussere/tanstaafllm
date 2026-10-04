# Factory versus ArchR DTB — RK915 Wi-Fi comparison (Step 5.8c)

> **Superseded outcome:** this records the first overlay proposal (v1). Its physical tests led to v2 and v3 and to a working connection; see `0508_04_archr-wifi-bring-up-result.md`. The v1 hashes below no longer match the current `wifi-rk915.dtbo`.

## Summary

The comparison explains the live finding that `mmc2` (`ff380000.mmc`) enumerates no SDIO device. ArchR's base DTB describes that controller as a **second SD-card slot**, and its card-detect line, GPIO0_A2, is the RK915 **chip-enable** line on the R36 Ultra. Nothing in the running ArchR kernel ever drives that pin high, so the Wi-Fi chip is never powered and there is nothing for `rk915.ko` to bind.

A proposed, offline-validated overlay, `worklines/luna/data/wifi-rk915.dtbo`, powers the chip through the standard `mmc-pwrseq-simple` and makes the host non-removable. **It has not been installed on any card.**

All work was read-only against local copies: the preserved factory DTB, the local panel overlay, and the BOOT/ROOT partitions extracted from the verified ArchR clone image under `/data/michael/tanstaafllm/tmp/archr-5.8c/`. Luna and its cards were not touched.

## Inputs

| Input | Source | SHA-256 |
|---|---|---|
| Factory DTB | `worklines/luna/data/r36-ultra.dtb` (model `Rockchip rk3326 evb lpddr3 v12 board for linux`) | — |
| ArchR base DTB | `BOOT/dtbs/rk3326-gameconsole-eeclone.dtb` from `ArchR-R36S.aarch64-20260709-clone.img.gz` (model `R36S Clone`) | `6fbcaf01…9289974` |
| Panel overlay | `worklines/luna/data/mipi-panel.dtbo` (3,440 bytes, same size as the card's) | — |
| ArchR driver | `/usr/lib/kernel-overlays/base/lib/modules/6.12.94/rk915/rk915.ko` from the image's ROOT | — |
| Tools | DTC 1.7.2 (`dtc`, `fdtoverlay`) in `/data/michael/tanstaafllm/tools/dtc-env` (conda-forge, no root) | — |

## How ArchR chooses its DTB

`extlinux.conf` uses `FDTDIR /dtbs/` plus `FDTOVERLAYS /overlays/mipi-panel.dtbo`. `boot.scr` reads a hardware ADC and picks one of four DTBs: `rgb10x` (140–190), `xu-mini-m` (1000–1050), `gameconsole-eeclone` (490–540), or the `odroid-go2` fallback. Luna's actual ADC value and selected DTB have **not** been observed. This analysis assumes `gameconsole-eeclone`, the only R36S-clone candidate. That must be confirmed on tty1 before any install (see "Open checks").

The Flasher's **Import DTB** only extracted panel and audio fragments into `mipi-panel.dtbo`. The factory DTB is never booted.

## Findings

### 1. The same controller, described for different hardware

| `ff380000` (alias `mmc2` in factory; label `sdio` in ArchR) | Factory | ArchR eeclone |
|---|---|---|
| Role | SDIO (`supports-sdio`, vendor `supports-rk912`) | SD card (`supports-sd`, `sd-uhs-sdr12…104`) |
| Card detect | none | `cd-gpios = <&gpio0 2 GPIO_ACTIVE_LOW>` |
| Power sequence | none on the node; handled by `wireless-wlan` | none |
| Supplies | none | `vqmmc` = LDO_REG7, `vmmc` = LDO_REG8 |
| `max-frequency` | 50 MHz | 100 MHz |
| SDIO pins (`sdio-clk/cmd/bus4`, bank 1 pins 0x14–0x19) | same pins | same pins |

### 2. GPIO0_A2 is the Wi-Fi chip enable

The factory DTB uses GPIO0_A2 as active-high enable in two places:

- `wireless-wlan` (`compatible = "wlan-platdata"`, `wifi_chip_type = "rk915"`): `WIFI,poweren_gpio = <&gpio0 2 GPIO_ACTIVE_HIGH>`, `WIFI,host_wake_irq = <&gpio0 1 …>`.
- disabled alternate-chip node `seekwcn_boot`: `gpio_chip_en = <&gpio0 2 0>`.

Its `sdio-pwrseq` node (`mmc-pwrseq-simple`) is **empty** and unreferenced, so factory power-on is done entirely by the Rockchip vendor `wlan-platdata`/rfkill-wlan driver.

ArchR claims that same pin as an SD card-detect **input**. No other ArchR node references GPIO0_A1 or GPIO0_A2.

### 3. The ArchR kernel and driver cannot use the vendor mechanism

- `BOOT/KERNEL` contains `mmc-pwrseq-simple` and `pwrseq_simple`, but no `wlan-platdata`. The vendor power driver is absent.
- `rk915.ko` (aliases `sdio:c*v0296d5348*`, `…d5347*`) imports no GPIO, regulator, or `rockchip_wifi_power` symbols. It only binds to an SDIO function that something else has already powered and enumerated.

This is consistent with the live evidence: no `mmc2:0001`, an empty SDIO bus, and no RK915 module load.

### 4. Regulator differences (not addressed by the overlay)

| Regulator | Factory | ArchR eeclone |
|---|---|---|
| LDO_REG7 | `vcc2v8_dvp`, 1.8–3.3 V, always-on | `vcc2v8_dvp`, 1.8–3.3 V, always-on; also ArchR's `vqmmc` for `ff380000` |
| LDO_REG8 | `vcc1v8_dvp`, **3.3 V** fixed, always-on | `vcc3v0_dvp`, **3.0 V** fixed, always-on; also ArchR's `vmmc` |

Both rails stay on in both DTBs. Which rail feeds the RK915 is not known from the DTBs alone. If the chip still fails to enumerate once enabled, these rails are the next suspect.

## Proposed overlay (not installed)

Files:

- `worklines/luna/data/wifi-rk915.dts`: source, SHA-256 `4d790cc6…c22f5e1`
- `worklines/luna/data/wifi-rk915.dtbo`: compiled, 1,313 bytes, SHA-256 `80fd1b84a36d1964000979ff07324f98e2d9fc90ec92e8bda67437e5acd6bf07`

What it adds:

- `/sdio-pwrseq`: `mmc-pwrseq-simple`, `reset-gpios = <&gpio0 2 GPIO_ACTIVE_LOW>`, `post-power-on-delay-ms = <200>`, plus a pinctrl entry muxing GPIO0_A2 as GPIO. Releasing an active-low reset drives the pin **high**, which matches the factory's active-high enable.
- `&sdio` (`mmc@ff380000`): `non-removable`, `cap-sdio-irq`, `keep-power-in-suspend`, `mmc-pwrseq = <&sdio_pwrseq>`, and `max-frequency = <50000000>`. This follows the mainline `px30-evb.dts` SDIO Wi-Fi pattern.

Overlays cannot delete properties, so ArchR's `cd-gpios` stays in the tree. That is harmless: mainline v6.12 `mmc_of_parse()` (`drivers/mmc/core/host.c`) skips the card-detect GPIO request entirely when `non-removable` is set, so the pin is free for the pwrseq.

Offline validation:

- `fdtoverlay` applied `mipi-panel.dtbo` and then `wifi-rk915.dtbo` to `rk3326-gameconsole-eeclone.dtb` without error.
- In the decompiled result, `mmc-pwrseq` resolves to `/sdio-pwrseq`, `reset-gpios` resolves to `/pinctrl/gpio@ff040000` pin 2, and `wifi-enable-h` is `<0 2 RK_FUNC_GPIO &pcfg_pull_none>`.
- It also applies structurally to the other three ArchR DTBs, but only eeclone was analysed.

## Residual risks

- The `sd-uhs-*` capabilities and the LDO7 `vqmmc` stay on the SDIO host. If the RK915 advertises 1.8 V signalling, the core could retune LDO7. Expected impact is low (SDIO 2.0-class chip; LDO7 is always-on and 1.8–3.3 V capable), but if it happens, the fallback is a full Luna-specific DTB built from eeclone with those properties deleted, selected by the `FDT` line.
- The host-wake line (GPIO0_A1) is not wired in. The driver should work with in-band SDIO interrupts; the out-of-band wake only matters for suspend.
- The RK915 power rail (finding 4) is unverified.
- If the overlay is wrong, the expected failure is Wi-Fi still absent, not a boot failure: U-Boot ignores missing or failed overlays, and the change touches only the SDIO controller and an otherwise unused GPIO. The panel overlay is applied first and is unchanged.

## Open checks before any install (on tty1, read-only)

```sh
cat /proc/device-tree/model; echo        # expect: R36S Clone
tr ' ' '\n' < /proc/cmdline | grep hwid  # ADC value, expect 490-540
```

## Proposed install (requires a separate green light)

This is a BOOT-only, reversible change on the disposable ArchR card:

1. Back up `extlinux/extlinux.conf`.
2. Copy `wifi-rk915.dtbo` to `BOOT/overlays/`.
3. Change the `FDTOVERLAYS` line to `FDTOVERLAYS /overlays/mipi-panel.dtbo /overlays/wifi-rk915.dtbo`, with no trailing whitespace (ArchR's README warns that its extlinux parser is fragile).

Expected evidence after boot: `mmc2:0001` and an SDIO device `0296:5348`, `rk915` loaded, `wlan0` present, and an RK915 firmware download in `dmesg`. Joining a network is a separate step.

To reverse: restore the backed-up `extlinux.conf`, or remove the second overlay path.
