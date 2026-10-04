# R36 Ultra Arch-R Wi-Fi investigation: access to evidence

## Summary

This short discussion follows the Arch-R Wi-Fi failure: the handheld cannot connect and no SSIDs are visible. It reinforces that the immediate objective is to obtain a shell or inspect the removable Arch-R card, then identify the chipset and compare its required driver/firmware with the known-working stock EmuELEC image.

It does not identify the Wi-Fi driver. Its useful outcome is a concrete, read-only evidence checklist and a keyboard/OTG or card-mounting route to obtain it.

## Detailed summary

**Wi-Fi hypothesis**

- The discussion treats a missing SSID list as evidence more consistent with driver, module-index, firmware, or hardware-support failure than with a credentials error.
- It mentions Arch-R release claims about several USB Wi-Fi drivers, but those claims do not establish the R36 Ultra’s chipset or a suitable driver.

**Ways to obtain diagnostics**

- A USB-C OTG adapter plus any USB keyboard was proposed for attempting an EmulationStation exit or Linux TTY.
- If there is no network or terminal, the Arch-R removable card can be mounted on the desktop for read-only examination of systemd, iwd, kernel modules, and firmware.

**Required evidence**

- Identify the wireless device and bus, RF state, service state, loaded modules, firmware-related messages, and actual module tree.
- Compare those facts with the preserved EmuELEC image, where scanning reportedly worked, before making a change.

## Cleaned transcript

> Translated from a French/English ChatGPT discussion. Editorial section headings were added for readability. Speaker labels are retained. Technical assertions by the earlier assistant are preserved as discussion claims, not independently verified facts.

### § 1. Wi-Fi failure and SSH paradox

**User:** I installed Arch-R and cannot connect Wi-Fi. It is probably a driver problem. I am trying to find a terminal to investigate, but I cannot find one. Look through their GitHub for leads.

**Assistant:** The earlier assistant stated that Arch-R documents SSH-based administration but that this is unhelpful until networking works. It said Arch-R uses iwd rather than NetworkManager and reported release claims for USB Wi-Fi driver support. It also reported a historical module-index issue after an update, while making clear that this does not identify the R36 Ultra’s own hardware.

It proposed three routes to a shell: use a USB keyboard to try leaving EmulationStation; attempt Linux TTYs with the keyboard; or mount the Arch-R card on the desktop. The latter was described as a way to inspect the standard writable Arch root, `systemd`, iwd, modules, firmware, and potentially console configuration.

The proposed diagnostic evidence was:

```bash
uname -a
ip link
lsusb
rfkill list
systemctl status iwd
iwctl device list
iwctl station list
lsmod
dmesg | grep -iE 'wifi|wlan|firmware|rtl|realtek|brcm|mediatek|usb'
find /usr/lib/modules/$(uname -r) -type f | grep -iE '8188|8192|8723|8852|wifi'
```

The assistant described `lsusb` as particularly useful for identifying a USB Wi-Fi chipset, while the larger goal remains to determine the actual device and driver rather than guess from a family name.

### § 2. Physical input route

**User:** In any case, I need a USB-C keyboard.

**Assistant:** A USB-C OTG-to-USB-A adapter plus an ordinary USB keyboard was proposed as a more flexible choice than a dedicated USB-C keyboard. The stated uses were keyboard-based diagnostics, storage, Ethernet adapters, and later Luna recovery/development. The conversation reiterated that mounting the card on the desktop remains possible before such hardware arrives.
