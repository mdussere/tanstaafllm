# Luna storage and Bluetooth observation

> **Freshness:** 🟡 historical · **Written:** 2026-09-27 · **Checked:** 2026-10-31 · **Step:** wyoh 4.1 ✅

**Question answered:** What does the preserved EmuELEC image currently expose for its claimed 8 GB eMMC and Bluetooth?

**Method:** read-only SSH inspection of `luna` on 2026-09-27. No device configuration, package, firmware, partition, or file was changed.

## Storage

The operating system exposes one physical block device: `mmcblk1`, a 48.8 GiB SDXC card. Its partitions supply the mounted `/flash`, `/storage`, and ROMs filesystems. There is no `/dev/mmcblk0`.

The device tree declares three MMC controllers. The controller at `dwmmc@ff390000` has eMMC support and eMMC pin configuration, and the kernel identifies its `mmc0` host as non-removable. It then repeatedly times out while issuing commands, and no block device is registered for it.

Consequently, the “8 GB eMMC” shown in console details is **not usable or verifiable from this stock image**. It may describe fitted hardware that this image cannot initialise, an unpopulated or faulty device, or a board/firmware variation. Do not initialise, partition, or write it while preserving the retrogaming card. A future experimental image can retry enumeration before any destructive storage action.

## Bluetooth

The kernel Bluetooth protocol stack is present, and the device tree contains a `wireless-bluetooth` node. However, the stock system exposes no Bluetooth HCI adapter, no `/sys/class/bluetooth` device, and no Bluetooth rfkill entry. The kernel log records unsuccessful Bluetooth rfkill-driver initialisation.

Therefore Bluetooth is **not currently usable by this EmuELEC installation**. This does not prove the physical hardware lacks Bluetooth: the missing adapter may require the correct board driver, firmware, power sequence, or device-tree configuration. Wi-Fi is separate and is active through the SDIO-attached `mmc2` device.

## Follow-up boundary

These are stock-image observations, not a hardware modification. On the future experimental card, first record eMMC and Bluetooth enumeration before installing a desktop/session stack or making any persistent change.
