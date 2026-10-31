# Stock EmuELEC Wi-Fi driver evidence

> **Freshness:** 🟡 historical · **Written:** 2026-10-04 · **Checked:** 2026-10-31 · **Step:** luna 4.3 ✅

**Question answered:** Which Wi-Fi hardware path, driver, and firmware behaviour does the running factory EmuELEC image use on Luna?

**Method:** Step 4.3 read-only SSH collection on 2026-09-27. Commands inspected kernel, sysfs, module, firmware, device-tree, and radio state only. They did not scan, connect, alter RF state, load/unload modules, or modify either card.

## Result

The factory image uses the Rockchip **RK915** Wi-Fi stack over **SDIO**:

| Evidence | Observed value |
|---|---|
| Network interface | `wlan0` |
| RF state | `phy0` is neither soft- nor hard-blocked |
| Sysfs hardware path | `/sys/devices/platform/ff380000.dwmmc/mmc_host/mmc2/mmc2:0001/mmc2:0001:1` |
| Transport | SDIO on MMC host `mmc2` |
| SDIO identifier | `SDIO_ID=0296:5348`; `MODALIAS=sdio:c00v0296d5348` |
| Bound SDIO driver | `rk915_sdio` (`/sys/bus/sdio/drivers/rk915_sdio`) |
| Loaded kernel module | `rk915`, 192,512 bytes, live in `/sys/module/rk915` |
| Device-tree Wi-Fi type | `wifi_chip_type = rk915`; node is `wlan-platdata`, status `okay` |

The kernel identifies the driver as `RK915 WiFi Ver: 2022-11-08-17:51:56.2094f659.Wei`. It powers the radio through the board GPIO configuration, discovers an SDIO function on `mmc2`, binds `rk915_sdio`, and reports a successful firmware download of 48,056 bytes. The radio has successfully associated during this boot; this was observed in existing kernel messages, not triggered by this step.

## Firmware and provenance limits

The driver reports that it opens a firmware/patch source and downloads firmware successfully. It also reports failure to open two optional calibration inputs:

```text
rk915_read_firmware_file: failed to open rk915_cal.bin
rk915_read_firmware_file: failed to open rk915_rf_para.txt
rk915_download: download firmware success
```

No matching `rk915` module file or firmware candidate was visible under the standard `/lib/modules`, `/usr/lib/modules`, `/lib/firmware`, `/usr/lib/firmware`, or `/storage` paths. `modinfo rk915` therefore reports that the module is not found, even though `/sys/module/rk915` and the SDIO-driver binding prove it is live. The image may package the module and firmware outside those standard trees or embed some assets; this collection does not establish which.

## Exact stock build

- EmuELEC `4.7-Nexus_devel_20260811180851`, build `8ce736adf89ea558ffb41f00f8d84688255c3c5a`
- Linux `5.10.160`, aarch64

## Consequence for the experimental image

The relevant comparison target is now concrete: it must expose the same `0296:5348` SDIO function and either bind a compatible RK915 driver/firmware path or explain why it cannot. No driver was extracted, copied, or proposed for installation in this step.
