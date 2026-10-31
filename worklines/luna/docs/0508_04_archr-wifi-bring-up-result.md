# ArchR Wi-Fi bring-up on Luna — from an empty SDIO bus to a DHCP lease (Steps 5.8c–5.8f)

## Result

On 2026-10-04 Luna (R36 Ultra) running ArchR on the disposable card joined the home WPA2 network over its internal RK915 Wi-Fi and received a DHCP lease:

```
wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP>
    link/ether 02:b2:de:0d:ca:2a
    inet 192.168.50.34/24 … dynamic wlan0
```

Termidor (192.168.50.27) reaches it: 3/3 pings answered. SSH access and reboot persistence followed in Steps 5.8h–5.8i (`0508_05_archr-ssh-and-persistence.md`). Getting there took one device-tree overlay in three revisions plus one router setting. ArchR's driver, firmware, kernel and userspace were not modified.

## Starting point

ArchR boots its own generic `rk3326-gameconsole-eeclone.dtb` ("R36S Clone"). That choice was confirmed live: `uboot.hwid_adc=b,512` falls in the eeclone range 490–540. The Arch R Flasher's **Import DTB** only extracted panel and audio fragments into `mipi-panel.dtbo`; the factory DTB itself is never booted (`0508_03`). On tty1:

- `mmc2` (`ff380000`) existed but had no device; the SDIO bus was empty;
- `rk915.ko` and its firmware were installed but never loaded;
- `ip link` showed only `lo`.

## The quest, stage by stage

Each fix uncovered the next layer down the stack. They're listed in the order they were met.

| # | Symptom | Cause | Fix | Evidence it worked |
|---|---|---|---|---|
| 1 | No SDIO device on `mmc2` | ArchR describes `ff380000` as a second SD slot, and its `cd-gpios` is GPIO0_A2, which on this board is the RK915 **chip enable**. Nothing drives it high, so the chip is never powered. The factory vendor kernel powered it with a Rockchip-only `wlan-platdata` driver that ArchR's 6.12 kernel lacks. | **Overlay v1:** `mmc-pwrseq-simple` driving GPIO0_A2 high, `non-removable` (which also makes the MMC core skip the `cd-gpios` request), 50 MHz, `cap-sdio-irq`, `keep-power-in-suspend` | `allocated mmc-pwrseq`, `mmc2:0001`, SDIO `0296:5348`, `rk915` auto-loaded |
| 2 | `check downloaded fw ok` → `download firmware failed`; works on one boot, fails on another | ArchR's kernel patch `024-mainline-linux-hacks-for-rk915.patch` enables its RK915 MMC quirks only when the host node has the DT property **`supports-rk912`**: no SDIO clock gating, CMD52 waits for DAT busy, short CIS FUNCE accepted. The factory DTB carries it; v1 did not. Without a continuous clock the chip's firmware does not come up reliably. | **Overlay v2:** `supports-rk912`, `no-sd`, `no-mmc`, plus the driver's documented `wifi@1` child with a `host-wake` interrupt (GPIO0_A5, taken from the driver's reference board) | `download firmware success`, `download patch2 success`, `wlan0` and `phy0` present, iwd lists the wiphy |
| 3 | `ip link set wlan0 up` → `No such device`; `No reset complete after 300 ticks`, `umac init failed` | The pinned driver (AveyondFly/rk915) receives every chip event **only** through the `host-wake` GPIO interrupt (rising edge), never through SDIO's built-in interrupt. `/proc/interrupts` showed `rockchip_gpio_irq 5 edge rk915` registered on a pin that never fires. | **Overlay v3:** host wake on **GPIO0_A1**, taken from Luna's factory `wireless-wlan` node (`WIFI,host_wake_irq`) | `rpu_reset_complete: Patch 2_1_2 FW: Dec 29 2021`; 177+ interrupts on `rockchip_gpio_irq 1`; iwd scans and lists the AP (ch 11, -59 dBm) |
| 4 | Every join fails: iwd `connect-failed, status: 1`; kernel `wlan0: AP is in CSA process, reject auth` | Since Linux 6.7, mac80211 refuses to authenticate while it believes the AP is announcing a channel switch (CSA/ECSA). This is reported against ASUS routers on **auto channel** on 2.4 GHz. Neither Termidor's nor Luna's scan showed a CSA element, so the match is circumstantial, but the fix confirmed it in practice. | **Router:** 2.4 GHz Control Channel changed from Auto to a fixed **11** (WPA2-Personal, AES, PMF disabled — all compatible with the RK915) | Join succeeded; DHCP lease 192.168.50.34 |

Two stages were ruled out along the way. The router's security mode was checked from Termidor (WPA2-PSK, CCMP, no WPA3). Typing the passphrase on the AZERTY console was ruled out when the EmulationStation GUI failed in exactly the same way.

## Final overlay (v3)

Source: `worklines/luna/data/wifi-rk915.dts`; compiled: `wifi-rk915.dtbo`, SHA-256 `423feb4eb598b3a9fb706ba0a7cd35f7f168e26313d8103e58896670a9e5ca4a`. Effective result on `mmc@ff380000`:

```dts
sdio-pwrseq {                                   /* new root node */
    compatible = "mmc-pwrseq-simple";
    reset-gpios = <&gpio0 2 GPIO_ACTIVE_LOW>;   /* released = high = chip on */
    post-power-on-delay-ms = <200>;
};

&sdio {                                         /* mmc@ff380000 */
    non-removable; no-sd; no-mmc;
    supports-rk912;                             /* ArchR kernel's RK915 quirks */
    cap-sdio-irq; keep-power-in-suspend;
    mmc-pwrseq = <&sdio_pwrseq>;
    max-frequency = <50000000>;

    wifi@1 {
        compatible = "rockchip,rk915";
        reg = <1>;
        interrupt-parent = <&gpio0>;
        interrupts = <1 IRQ_TYPE_LEVEL_HIGH>;   /* GPIO0_A1; driver requests rising edge */
        interrupt-names = "host-wake";
    };
};
```

It is installed BOOT-only by `worklines/luna/scripts/enable_archr_wifi_overlay.sh`. That script adds `/overlays/wifi-rk915.dtbo` after `mipi-panel.dtbo` on the single `FDTOVERLAYS` line, keeps `extlinux.conf.tanstaafllm-before-wifi-overlay`, refreshes the `.dtbo` in place on later runs, and restores with `--restore`.

## How the network is managed on ArchR

- **iwd 3.10** owns the radio and, with `EnableNetworkConfiguration=true`, also runs DHCP. This join used `iwctl station wlan0 connect "Home network"`.
- **ConnMan 1.43** sits above iwd and is what EmulationStation's network menu uses. Before stage 3 it reported "Wifi is not available" because iwd had no usable device.
- The credentials are stored only on the disposable card, by iwd. They are not in the repository or the logbook.
- iwd's default state directory is on the tmpfs `/var`, so saved networks were initially lost at reboot. Step 5.8i moved it to `/storage/.cache/iwd` with a drop-in (`0508_05`).

## Known limits and open points

- **Stability is untested.** The upstream driver projects report firmware-error recovery under sustained receive traffic and post-association disconnects (ROCKNIX PR #3252 sets `lpw_no_sleep=1` against the latter). Long transfers and idle periods still need testing.
- **Remaining SD-card properties** inherited from ArchR's base DTB (`sd-uhs-*`, LDO7 as `vqmmc`) are harmless so far but unverified. The bus may run in 1.8 V UHS mode where the factory system uses 3.3 V.
- **The router change is a dependency:** if 2.4 GHz is set back to auto channel, joins may fail again with the CSA message.
- Bluetooth (`wireless-bluetooth`, disabled in the factory DTB) is out of scope.
- This is one disposable ArchR card on one Luna unit. No general R36 Ultra compatibility is claimed.

## Sources

- ArchR kernel patch: `projects/ArchR/devices/RK3326/patches/linux/024-mainline-linux-hacks-for-rk915.patch` and package `projects/ArchR/packages/linux-drivers/rk915/package.mk` in [archr-linux/Arch-R](https://github.com/archr-linux/Arch-R)
- Driver source pinned by ArchR: [AveyondFly/rk915](https://github.com/AveyondFly/rk915) at `e2fd616` (`docs/mainline-linux-dts-example.dtsi`, `src/platform.c`, `src/umac_if.c`, `src/firmware.c`)
- [rei512/rk915](https://github.com/rei512/rk915) binding notes (out-of-band host wake, continuous clock)
- [ROCKNIX PR #3252](https://github.com/ROCKNIX/distribution/pull/3252) (RK3326 RK915 integration and known stability issues)
- mac80211 CSA refusal: Linux v6.12 `net/mac80211/mlme.c`; [Fedora discussion](https://discussion.fedoraproject.org/t/wifi-connection-failing-due-to-long-ap-is-in-csa-process-reject-auth/116036); [asuswrt-merlin #1019](https://github.com/gnuton/asuswrt-merlin.ng/issues/1019)
