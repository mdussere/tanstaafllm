# RK915 source and Arch-R compatibility assessment

**Questions answered:** Is Luna’s RK915 driver part of upstream EmuELEC? Does Arch-R contain support for it? Can the stock driver be added to the mounted Arch-R image without recompilation?

**Method:** read-only SSH evidence from the factory EmuELEC image; read-only inspection of all three user-mounted Arch-R partitions; and shallow partial clones of the official upstream repositories under `/home/michael/git/`. `ARCHR_ROOT` was already mounted by the user; every action in this assessment was a read. No file on the Arch-R card was changed.

## Short answer

- **Upstream EmuELEC:** no explicit RK915 package, patch, or configuration reference was found in the current official tree for the Rockchip/OdroidGoAdvance target. The stock R36 Ultra image is therefore best treated as a vendor-modified EmuELEC-derived build, not evidence that RK915 is supported by upstream EmuELEC.
- **Arch-R:** yes. Arch-R explicitly builds the out-of-tree RK915 SDIO driver and installs its firmware for RK3326 builds.
- **Directly copy the stock EmuELEC driver into Arch-R:** no. The stock module runs with Linux 5.10.160, while the mounted Arch-R boot kernel is Linux 6.12.94 with module-version CRCs enabled. That module ABI mismatch is fatal.
- **Use a matching prebuilt Arch-R module without recompiling:** unnecessary for this image. Its root overlay already contains a matching `rk915.ko` and both firmware blobs for the exact Arch-R 6.12.94 modversioned kernel.

## Evidence

### Factory EmuELEC image

The running stock image uses `wlan0` on SDIO ID `0296:5348`, on MMC host `mmc2`, bound to `rk915_sdio` from the live `rk915` module. Its kernel is Linux 5.10.160. See `0403_02_stock-emuelec-wifi-driver-result.md` for the direct device evidence.

### Official EmuELEC source

The official repository was cloned from `https://github.com/EmuELEC/EmuELEC` at revision `5acddc6aa00d763e7ac1d808516b18e0dac2bd4c`. Its full tree has no RK915-named source/package path, and a checked-out Rockchip/OdroidGoAdvance build subset has no RK915 reference.

That target currently points at the Hardkernel 4.4 kernel line, whereas the stock R36 Ultra reports Linux 5.10.160. This independently supports the conclusion that the stock RK915 implementation is part of the vendor image delta, not the current upstream EmuELEC OdroidGoAdvance configuration.

### Official Arch-R source

The official repository was cloned from `https://github.com/archr-linux/Arch-R` at revision `dbd45d454f0fea1e61c0b35e429f6be18f3e997e`.

Its RK3326 options select:

```text
ADDITIONAL_DRIVERS="rk915 ..."
```

Its `projects/ArchR/packages/linux-drivers/rk915/package.mk` obtains `AveyondFly/rk915`, builds it with `BUSIF=SDIO`, `ROM=true`, and `CHIP=RK915` against the Arch-R kernel, then installs `*.ko` modules and `firmware/*.bin` files into the image. It also carries `024-mainline-linux-hacks-for-rk915.patch`, which changes MMC/SDIO handling for this hardware family.

The mounted Arch-R `KERNEL` is Linux 6.12.94, with `mod_unload` and `modversions` enabled. It contains the string `supports-rk912`, the property used by Arch-R’s RK915 MMC patch. This proves the installed kernel includes the patch vocabulary, but not that the selected live DTB asserts that property.

### Mounted Arch-R root overlay

Arch-R stores its packaged kernel additions in a base overlay rather than the conventional top-level `/lib/modules` tree. The user-mounted root partition contains:

```text
/usr/lib/kernel-overlays/base/lib/modules/6.12.94/rk915/rk915.ko
/usr/lib/kernel-overlays/base/lib/firmware/rk915_fw.bin
/usr/lib/kernel-overlays/base/lib/firmware/rk915_patch.bin
```

`modinfo` reports the module as `rk915`, describes it as the Rockchip RK915 SDIO Wi-Fi driver, and gives aliases for both `sdio:c*v0296d5348*` and `sdio:c*v0296d5347*`. Its exact vermagic is:

```text
6.12.94 SMP preempt mod_unload modversions aarch64
```

This matches the mounted boot kernel. The installed Arch-R image therefore already has the correct driver binary and firmware for the stock device ID. The many unrelated top-level Ubuntu-style module directories are not the Arch-R driver location and do not alter that conclusion.

## Why the EmuELEC module cannot be copied

A loadable kernel module is linked to its kernel release and exported-symbol CRCs. The two systems differ at least in:

| Stock EmuELEC | Mounted Arch-R |
|---|---|
| Linux 5.10.160 | Linux 6.12.94 |
| Vendor RK915 module | Arch-R kernel has `modversions` enabled |
| Vendor MMC/SDIO stack | Arch-R carries its own RK915 MMC/SDIO patch |

Copying the stock `rk915.ko` would therefore fail module compatibility checks or be unsafe even if forced. Copying firmware alone cannot supply the missing kernel driver.

## Consequence and lowest-risk next action

Do **not** copy the EmuELEC module or add a second RK915 binary to this image: the correct Arch-R driver and firmware are already installed. If Wi-Fi fails after Arch-R boots, collect a read-only runtime record first: `uname -r`, the overlay/module activation state, the selected DTB’s RK915 property, `dmesg`, and the SDIO device/driver binding. The remaining likely classes are overlay activation, DTB/MMC enablement, module autoload, or firmware load—not a missing driver package.

No installation plan is authorised by this assessment.
