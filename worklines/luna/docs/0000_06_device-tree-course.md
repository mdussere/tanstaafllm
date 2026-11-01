# A short course on the Device Tree (DTS / DTB / DTBO)

> **Freshness:** 🟡 historical · **Written:** 2026-10-04 · **Checked:** 2026-10-31

Learning material, not a work record. Every example is taken from Luna (R36 Ultra, Rockchip RK3326) and the Step 5.8c investigation in `0508_03_factory-vs-archr-dtb-wifi-comparison.md`.

---

## Lesson 1 — The problem the Device Tree solves

On a PC, the kernel can ask the hardware what it has. Buses like PCI and USB can be *enumerated*: each device announces a vendor and product ID, and the kernel loads the matching driver.

Most ARM boards can't do that. On a chip like the RK3326, the display controller, the I²C buses, the SD controllers and hundreds of pins are just registers at fixed addresses. Nothing announces itself. The kernel must be *told*:

- which blocks exist and at which address (`mmc@ff380000`);
- how they are wired on **this** board (which pin does what, which regulator powers what);
- which driver handles each block (`compatible = "rockchip,rk3288-dw-mshc"`).

Before around 2011, ARM Linux hard-coded this in C, one "board file" per device. The **Device Tree** replaced those files with a data file. One kernel can then run on many boards, and each board brings its own description.

> **Key idea:** the kernel holds the *drivers*; the device tree holds the *wiring*. Same SoC with different wiring means the same kernel with a different device tree.

That's why the R36S clones are messy: they look identical and use the same SoC, but each manufacturer wires pins, panels and Wi-Fi a little differently, so each needs its own device tree.

---

## Lesson 2 — The three file types

| Name | What it is | Who uses it |
|---|---|---|
| **DTS** (Device Tree Source) | Human-readable text (`.dts`; included fragments are `.dtsi`) | You, when reading or editing |
| **DTB** (Device Tree Blob) | Compiled binary of a DTS | The bootloader loads it; the kernel reads it |
| **DTBO** (Device Tree Blob Overlay) | Compiled *patch* applied on top of a DTB | The bootloader, before starting the kernel |

The compiler is **`dtc`**. It works in both directions:

```sh
dtc -I dts -O dtb -o board.dtb board.dts      # compile
dtc -I dtb -O dts -o board.dts board.dtb      # decompile (what we did in 5.8c)
```

Decompiling is lossless for the data. You lose comments and symbolic names: `&gpio0` becomes a number like `<0x55>`, and `GPIO_ACTIVE_LOW` becomes `0x01`. That is why the decompiled Luna files are full of hex.

---

## Lesson 3 — Reading the syntax

A device tree is a **tree of nodes**. Each node has **properties**. Here is a real node from the factory Luna DTB, simplified:

```dts
/ {                                         // the root node
    model = "Rockchip rk3326 evb lpddr3 v12 board for linux";

    dwmmc@ff380000 {                        // node name @ unit address
        compatible = "rockchip,px30-dw-mshc", "rockchip,rk3288-dw-mshc";
        reg = <0x00 0xff380000 0x00 0x4000>; // registers: address, size
        bus-width = <4>;
        max-frequency = <50000000>;         // 50 MHz
        status = "okay";                    // enabled ("disabled" = ignored)
        supports-sdio;                      // a boolean: present = true
    };
};
```

The property forms you'll meet:

| Form | Example | Meaning |
|---|---|---|
| String | `status = "okay";` | text |
| Cells | `bus-width = <4>;` | 32-bit numbers in `< >` |
| Boolean | `non-removable;` | present means true, absent means false |
| Reference | `mmc-pwrseq = <&sdio_pwrseq>;` | points to another node |

Some properties carry special meaning:

- **`compatible`** decides which driver binds. The kernel compares this string with the list each driver declares. It is the single most important property.
- **`status`** controls whether a node is used at all. A node with `"disabled"` is ignored entirely, like the factory `seekwcn_boot` node.
- **`reg`** gives the register address and size.

---

## Lesson 4 — References: labels and phandles

Nodes refer to each other. In source you write a **label** and refer to it with `&`:

```dts
gpio0: gpio@ff040000 { ... };               // "gpio0" is a label

wifi {
    enable-gpios = <&gpio0 2 GPIO_ACTIVE_HIGH>;  // bank gpio0, pin 2, active-high
};
```

When compiled, each referenced node gets a numeric **phandle**, and `&gpio0` is replaced by that number. That's why the decompiled files show:

```dts
WIFI,poweren_gpio = <0x5c 0x02 0x00>;   // 0x5c = phandle of gpio0, pin 2, flag 0 = active-high
cd-gpios          = <0x55 0x02 0x01>;   // 0x55 = gpio0 in ArchR's DTB, pin 2, flag 1 = active-low
```

The same bank has different phandles in different DTBs (`0x5c` and `0x55`). Phandles are just numbers handed out at compile time. To know what a phandle is, find the node containing `phandle = <0x5c>;`. That's what the small helper script did in 5.8c.

**How GPIOs are named.** RK3326 pins are grouped in banks of 32 (A0–A7, B0–B7, C0–C7, D0–D7). "GPIO0_A2" means bank 0, pin 2. "GPIO0_B3" would be bank 0, pin 8 + 3 = 11.

**Active-high vs active-low.** This says which electrical level means "asserted". An active-low reset means "the pin low = in reset". This detail is central to the Luna fix (Lesson 8).

---

## Lesson 5 — How the DTB reaches the kernel

The boot chain on Luna under ArchR:

```
power on → boot ROM → U-Boot (bootloader)
            │
            ├─ runs boot.scr: reads the hardware ADC and picks a DTB
            │    490–540 → rk3326-gameconsole-eeclone.dtb  ("R36S Clone")
            │    otherwise → rgb10x / xu-mini-m / odroid-go2 fallback
            ├─ reads extlinux.conf:
            │    LINUX /KERNEL
            │    FDTDIR /dtbs/                          ← where DTBs live
            │    FDTOVERLAYS /overlays/mipi-panel.dtbo  ← patches to apply
            ├─ loads the DTB into memory and applies each overlay to it
            └─ starts the kernel, handing it the final, merged tree
```

The kernel then walks the tree. For every node with `status = "okay"`, it looks for a driver whose `compatible` matches and calls that driver's *probe* function. The driver reads its own node's properties to learn the wiring.

At runtime you can see the tree the kernel actually received:

```sh
cat /proc/device-tree/model                  # e.g. "R36S Clone"
ls /proc/device-tree/                        # one directory per node
dtc -I fs -O dts /proc/device-tree           # the whole live tree as DTS
```

`/proc/device-tree` reflects the **merged** result (base DTB plus overlays), not any file on disk. That's how you check what really happened at boot.

---

## Lesson 6 — Overlays

Keeping one full DTB per clone variant is unmanageable. Overlays let a distribution ship a few base DTBs and patch the differences in.

An overlay is a list of **fragments**. Each fragment names a target node and the content to merge into it:

```dts
/dts-v1/;
/plugin/;                          // marks this file as an overlay

/ {
    fragment@0 {
        target = <&sdio>;          // the base DTB's node labelled "sdio"
        __overlay__ {
            non-removable;         // added
            max-frequency = <50000000>;   // overrides the existing value
        };
    };
};
```

To resolve `&sdio`, the base DTB must have been compiled with `-@`. That keeps a `__symbols__` table mapping labels to paths, and ArchR's DTBs have one (`sdio = "/mmc@ff380000"`). You compile overlays with `dtc -@` as well.

Overlays can:
- **add** new nodes and properties;
- **change** existing property values.

Overlays **cannot delete** a property or node. That is the most important limitation. For example, ArchR's `cd-gpios` could not be removed by our overlay, so it had to be neutralised another way.

Test an overlay offline, without the device:

```sh
fdtoverlay -i base.dtb -o merged.dtb mipi-panel.dtbo wifi-rk915.dtbo
dtc -I dtb -O dts merged.dtb | less
```

---

## Lesson 7 — Bindings: who decides what a property means

The DTS syntax is generic. The *meaning* of `non-removable` or `mmc-pwrseq` is defined by **bindings**, documents in the kernel at `Documentation/devicetree/bindings/`. Each binding says which properties a given `compatible` accepts.

This is where **vendor kernels** and **mainline kernels** part ways:

| | Factory EmuELEC | ArchR |
|---|---|---|
| Kernel | Rockchip BSP 5.10 (vendor) | 6.12 (mainline-based) |
| Wi-Fi power binding | `compatible = "wlan-platdata"` with `WIFI,poweren_gpio` (Rockchip-only) | `compatible = "mmc-pwrseq-simple"` with `reset-gpios` (standard) |

A property that one kernel doesn't know is **silently ignored**, not reported as an error. So a perfectly valid vendor DTB can be useless on a mainline kernel, and the reverse. That's also why "just copy the factory DTB into ArchR" isn't safe: much of its vocabulary would be ignored by ArchR's kernel.

---

## Lesson 8 — Case study: why Luna had no Wi-Fi on ArchR

**Symptom.** On ArchR the SDIO controller `mmc2` (`ff380000`) exists, but no device appears on it (`/sys/bus/mmc/devices` has no `mmc2:0001`). The `rk915` driver is installed but never loads, and only `lo` exists.

**Background.** The RK915 Wi-Fi chip hangs on an SDIO bus. SDIO buses *can* be enumerated, but only if the chip is powered when the controller probes the bus. On Luna, power is switched by **GPIO0_A2**, which must be driven high.

**What the two DTBs say about that pin:**

```dts
// factory (vendor kernel): drive it high to power the Wi-Fi
wireless-wlan {
    compatible = "wlan-platdata";
    WIFI,poweren_gpio = <&gpio0 2 GPIO_ACTIVE_HIGH>;
};

// ArchR eeclone (written for a clone with a second SD slot): read it as card-detect
mmc@ff380000 {
    cd-gpios = <&gpio0 2 GPIO_ACTIVE_LOW>;
    supports-sd;
};
```

**Diagnosis.** ArchR's kernel has no `wlan-platdata` driver, and `rk915.ko` has no power code of its own. Nothing ever drives the pin. Worse, the SD driver claims it as an *input*. The chip stays off, the bus is empty, and there's nothing to bind.

**The fix, expressed in mainline vocabulary** (`worklines/luna/data/wifi-rk915.dts`):

```dts
sdio_pwrseq: sdio-pwrseq {
    compatible = "mmc-pwrseq-simple";
    reset-gpios = <&gpio0 2 GPIO_ACTIVE_LOW>;
    post-power-on-delay-ms = <200>;
};

&sdio {                         // mmc@ff380000
    non-removable;
    cap-sdio-irq;
    keep-power-in-suspend;
    mmc-pwrseq = <&sdio_pwrseq>;
    max-frequency = <50000000>;
};
```

Two subtle points:

1. **The polarity trick.** `mmc-pwrseq-simple` holds a "reset" line during power-up, then *releases* it. Declaring it active-low means "released" = pin **high** = chip enabled, which matches the factory's active-high enable.
2. **The overlay limit.** `cd-gpios` can't be deleted (Lesson 6). Instead, `non-removable` tells the MMC core there is no card to detect. The v6.12 source (`mmc_of_parse()`) then never requests the card-detect GPIO, which frees the pin for the power sequence.

**Expected evidence if it works:** `mmc2:0001` appears, an SDIO device `0296:5348` shows up, `rk915` loads automatically, its firmware downloads, and `wlan0` exists.

---

## Lesson 9 — Toolbox and habits

| Task | Command |
|---|---|
| Decompile a DTB | `dtc -I dtb -O dts -o x.dts x.dtb` |
| Compile an overlay | `dtc -@ -I dts -O dtb -o x.dtbo x.dts` |
| Merge offline | `fdtoverlay -i base.dtb -o out.dtb a.dtbo b.dtbo` |
| Read one property | `fdtget x.dtb /mmc@ff380000 max-frequency` |
| See the live tree | `dtc -I fs -O dts /proc/device-tree` |
| Search a binary quickly | `strings x.dtb \| grep -i wlan` |

On Termidor these live in `/data/michael/tanstaafllm/tools/dtc-env/bin/`.

Good habits, all applied in this workline:

- **Compare, don't copy.** Diff the same node across two DTBs instead of swapping whole files.
- **Read the binding** for the kernel you actually run, not the one the DTB came from.
- **Validate offline** with `fdtoverlay` before touching a card.
- **Confirm the live tree** with `/proc/device-tree/model` before assuming which DTB booted.
- **Keep changes small and reversible:** one extra overlay and a backed-up `extlinux.conf`.

---

## Exercises

1. In `worklines/luna/data/r36-ultra.dtb`, find the microSD controller `dwmmc@ff370000` and its `cd-gpios`. Which GPIO bank and pin detect the card?
2. Decompile `mipi-panel.dtbo`. How many fragments does it have, and which nodes do they target?
3. Using `fdtoverlay`, merge only `wifi-rk915.dtbo` into the eeclone DTB. Then use `fdtget` to confirm `max-frequency` changed from 100 MHz to 50 MHz.
4. Why would setting `status = "disabled"` on `mmc@ff380000` make Wi-Fi *less* likely to work, not more?
5. Explain in one sentence why the factory DTB "works" with Wi-Fi on EmuELEC but its Wi-Fi section would be ignored by ArchR's kernel.
