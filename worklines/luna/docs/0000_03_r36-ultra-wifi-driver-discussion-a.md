# R36 Ultra: stock firmware, Arch-R bring-up, and Wi-Fi-driver investigation

## Summary

This discussion records recovery of access to the stock R36 Ultra EmuELEC image, the decision to preserve that image, and a proposed Arch-R-based experimental path. Its central technical lead is that stock EmuELEC could scan Wi-Fi networks while an Arch-R installation could not see any SSIDs, suggesting a driver, firmware, module-binding, or clone-hardware mismatch.

The discussion does not establish the Wi-Fi chipset or its driver. It identifies the stock image’s device tree, loaded modules, firmware, and kernel logs as the evidence needed before attempting any driver transfer or configuration change.

## Detailed summary

**Stock-image access and preservation**

- The R36 Ultra was reachable over the network but its factory EmuELEC root password differed from the usual `root` / `emuelec` default.
- The discussion proposed resetting the password or adding SSH access through the persistent storage overlay, and preserving the factory image and its live device tree before replacing the card.

**Experimental base proposal**

- The discussion proposed Arch-R Clone as a bring-up distribution because it provides a conventional Arch Linux ARM userland, systemd, pacman, and R36-family hardware support.
- This was a proposal, not a verified selection. It also noted ROCKNIX as a hardware reference and a custom Debian/Buildroot system as a later possibility.

**Why the device tree matters**

- The live DTB (`/sys/firmware/fdt`) was identified as the authoritative hardware description for the actual unit, especially its panel, GPIOs, audio, MMC, regulators, and Wi-Fi wiring.
- The discussion recommends preserving it before flashing the experimental card and using it for any panel-overlay generation workflow.

**Wi-Fi investigation hypothesis**

- The reported symptom on Arch-R was that Wi-Fi showed no SSIDs, despite the factory EmuELEC image having scanned successfully.
- Possible causes proposed in the discussion are a missing or wrong driver, absent firmware, interface/rfkill state, incorrect USB/SDIO mapping, or an unsupported clone-specific chipset.
- The next evidence set is the Wi-Fi device/bus identity, bound kernel driver, loaded modules, firmware files, kernel messages, and RF state from the preserved EmuELEC image.

## Cleaned transcript

> Translated from a French/English ChatGPT discussion. Editorial section headings were added for readability. Speaker labels are retained. Technical assertions by the earlier assistant are preserved as discussion claims, not independently verified facts.

### § 1. Stock EmuELEC access

**User:** I received my R36. I connected it to the network; it responds to ping and SSH answers, but I cannot find the login/password.

**Assistant:** The usual EmuELEC SSH account is `root` with password `emuelec`. The discussion warned that some R36 Ultra factory images use a changed, unknown root password. It suggested trying the standard credentials once, then identifying the exact factory build rather than guessing many passwords.

**User:** It does not work. I can still mount the flash and change the `etc/password` file.

**Assistant:** The password hash belongs in `shadow`, not `passwd`. The discussion noted that an EmuELEC/LibreELEC-style image can use an immutable system root and a separate persistent `/storage`, so a direct edit of a conventional root filesystem may not be possible. It recommended identifying the partitions before modifying anything and preserving the stock storage layout as a useful Luna reference.

### § 2. A more conventional experimental Linux base

**User:** I want to burn a distribution image for the R36 as a base for the project: minimal and adapted to the hardware, but more like a normal distribution than EmuELEC.

**Assistant:** The proposed candidates were ROCKNIX as a strong hardware reference, ArkOS, Arch-R, NixOS R36S, Buildroot R36S, and a hand-built Debian or Ubuntu root filesystem. The assistant’s preference was Arch-R as an early experiment because it was said to combine RK3326 handheld support with an Arch Linux ARM userland, `pacman`, `systemd`, SSH, networking, audio, input, and graphics infrastructure.

The proposed longer path was: first use a distribution with working hardware; then preserve or reuse the known-good kernel, DTB, and firmware combination; finally build a minimal Debian, Arch, or Buildroot Luna image. The discussion explicitly warned that the R36 Ultra clone family may differ from canonical R36S hardware and that the factory DTB must be preserved.

**User:** Why do you say Arch-R is less minimal than a hand-crafted Debian?

**Assistant:** The distinction was clarified as “less minimal as delivered,” not an inherent property of Arch. Arch-R includes selected handheld integration, firmware, graphics, input, services, and convenience packages. A custom Debian `minbase` system could include only the selected kernel/device-tree components, `systemd`, SSH, networking, ALSA, Wayland, Python, and Luna services. Arch-R could nonetheless be a useful initial base whose footprint is measured and later stripped.

**User:** Let’s go with Arch-R and see its footprint.

**Assistant:** The discussion proposed using the Clone image for the R36 Ultra family, retaining the original image and stock DTB before flashing. It suggested recording memory, services, top processes, package count, storage use, and zram before removing EmulationStation or gaming components. It cautioned that panel/DTB configuration may determine whether the screen works after flashing.

### § 3. Flashing and clone/panel selection

**User:** I tried the flasher but got a dependency problem. [The AppImage reported GTK/GVFS warnings and `Could not create default EGL display: EGL_BAD_PARAMETER`.]

**Assistant:** The discussion treated the EGL error as the likely fatal issue and the other messages as likely host/AppImage compatibility warnings. It proposed software rendering, forcing X11, using the native `.deb` flasher build, or reproducing the image-writing workflow manually only after understanding any device-specific work that the flasher performs.

**User:** I installed the flasher with apt and it works, but I do not see Ultra among the choices. Which is closest?

**Assistant:** It recommended choosing `R36S Clone`, while warning that board-family selection does not necessarily choose the exact display panel. The proposed safe route was to import the factory DTB rather than guess a panel overlay.

### § 4. What a DTB is and how to preserve it

**User:** The Arch-R overlay generator needs the DTB file from the console. Where can I find it? Can I get it with SSH? What is a DTB anyway?

**Assistant:** The discussion identified the live device tree at `/sys/firmware/fdt` as the best source because it is the binary device description actually passed to the running kernel. It proposed copying it to writable storage and retrieving it over SSH. It explained that a Device Tree Blob describes ARM hardware that is not automatically enumerated like a PC: SoC, RAM layout, GPIOs, display panel/timings, audio, MMC controllers, power, Wi-Fi, regulators, and clocks. It noted that an incorrect DTB can yield a booting kernel with a black or corrupt screen, missing buttons, audio, or battery reporting.

### § 5. The Arch-R Wi-Fi symptom

**User:** I think the Wi-Fi driver has a problem. It cannot connect although EmuELEC could, and it shows no SSID.

**Assistant:** The earlier assistant treated this as more suggestive of driver/module/firmware or clone-hardware mismatch than of a network password. It listed possible causes: wrong driver, missing firmware, interface blocked or down, incorrect USB/SDIO mapping, or an unsupported chipset. It mentioned Arch-R Wi-Fi support claims for several Realtek/AIC families but did not identify the R36 Ultra’s actual device.

It proposed collecting, from a shell:

```bash
ip link
iw dev
rfkill list
lsusb
dmesg | grep -Ei 'wifi|wlan|rtl|realtek|aic|firmware|80211|usb'
lsmod | grep -Ei 'rtl|rtw|8188|aic|wifi|80211'
```

If a wireless interface existed, it proposed bringing it up and using the distribution’s Wi-Fi tooling to scan. The stated goal was to distinguish an unknown chipset, wrong module, absent firmware, or an uninitialised interface. The discussion specifically treated `lsusb` or an equivalent bus/device identification as decisive evidence rather than assuming a Realtek variant.

### § 6. Lack of an interactive terminal

**User:** Before that, what is Local Play Mode? Then: where is the console? I only have the buttons.

**Assistant:** The earlier assistant described Local Play Mode as local, on-device play rather than network play or streaming, while noting that the exact meaning depends on the menu context. It first proposed a USB keyboard and TTY shortcuts, then corrected itself: with only handheld buttons, a normal interactive terminal may not be exposed through the EmulationStation UI. It suggested checking the UI tools/system-information screens, or using a USB-C OTG adapter and conventional USB keyboard for F4/TTY attempts.

The discussion also noted that mounting the Arch-R card on the desktop can expose the normal writable root filesystem for inspection of systemd, iwd, modules, and firmware. That was presented as a diagnostic path, not permission to alter the stock EmuELEC card.

### § 7. Why the stock EmuELEC image is the comparison point

**User:** Can you search the EmuELEC GitHub repository for commits related to R36 Ultra?

**Assistant:** The earlier assistant reported finding no public upstream commit explicitly naming R36 Ultra and hypothesised a vendor-specific or private delta over the EmuELEC Rockchip/OdroidGoAdvance target. It proposed that the relevant comparison is not a commit name but the stock image’s kernel modules, firmware blobs, DTB, kernel configuration, and actual Wi-Fi binding.

The final proposed evidence commands on the working stock image were:

```bash
lsusb
lsmod
dmesg | grep -Ei 'wifi|wlan|rtl|realtek|aic|firmware|80211'
find /lib/modules -type f | grep -Ei 'wifi|rtl|rtw|8188|aic'
find /lib/firmware -type f | grep -Ei 'rtl|realtek|aic'
```

The conversation’s conclusion was that a documented stock-image Wi-Fi driver/firmware inventory should precede any attempt to diagnose or repair the Arch-R Wi-Fi failure.
