# Stock EmuELEC Wi-Fi driver identification procedure

**Question answered:** Which Wi-Fi hardware path, kernel module, and firmware does the currently running factory EmuELEC image use on this R36 Ultra?

**Status:** Prepared only. The stock image is running and reachable over SSH, but this procedure has not been executed.

## Boundary

All collection is read-only. It must not bring an interface up or down, unblock RF, scan, connect, load/unload a module, change a service, copy a file to Luna, or alter either microSD card.

The output is an evidence record, not a driver-installation plan. A later experimental-image comparison must remain separately authorised.

## Collection sequence

### 1. Establish the running-image identity

Capture the OS, kernel, loaded module list, wireless interface inventory, and radio state:

```sh
uname -a
cat /etc/os-release
cat /proc/cmdline
lsmod
rfkill list
ip link
```

If `rfkill`, `ip`, or `lsmod` is absent, record that fact rather than substituting a state-changing command.

### 2. Discover the wireless network interface and its kernel binding

For every interface reported by `ip link`, collect only candidates that expose `wireless` in sysfs:

```sh
for net in /sys/class/net/*; do
  [ -d "$net/wireless" ] || continue
  echo "=== ${net##*/} ==="
  readlink -f "$net/device" 2>/dev/null || true
  cat "$net/device/uevent" 2>/dev/null || true
  readlink -f "$net/device/driver" 2>/dev/null || true
  readlink -f "$net/device/driver/module" 2>/dev/null || true
  cat "$net/device/modalias" 2>/dev/null || true
done
```

The authoritative driver name is the resolved `driver` and, when available, `driver/module` symlink—not a module name guessed from distribution documentation.

### 3. Identify the transport and hardware descriptor

Record the resolved sysfs parent chain from the wireless interface. It should reveal whether the device is SDIO/MMC, USB, or platform-attached. Then gather non-mutating bus descriptors where present:

```sh
find /sys/bus/usb/devices -maxdepth 2 -name uevent -type f -print -exec cat {} \; 2>/dev/null
find /sys/bus/sdio/devices -maxdepth 2 -name uevent -type f -print -exec cat {} \; 2>/dev/null
find /sys/bus/mmc/devices -maxdepth 2 -name uevent -type f -print -exec cat {} \; 2>/dev/null
```

If a USB descriptor is present, record its vendor and product IDs. If the interface is SDIO/MMC, record `SDIO_ID`, `MODALIAS`, and the parent MMC host. Do not infer that the Wi-Fi chip is USB merely because `lsusb` is available.

### 4. Correlate module, firmware, and boot messages

Collect evidence that ties the bound module to a firmware request or successful initialisation:

```sh
dmesg | grep -Ei 'wlan|wifi|80211|cfg80211|mac80211|firmware|brcm|broadcom|rtl|realtek|rtw|aic|ssv|ap6|sdio|mmc|usb'
find /lib/modules -type f \( -name '*.ko' -o -name '*.ko.*' \) 2>/dev/null | grep -Ei 'wifi|wlan|brcm|broadcom|rtl|realtek|rtw|aic|ssv|ap6|cfg80211|mac80211'
find /lib/firmware /usr/lib/firmware -type f 2>/dev/null | grep -Ei 'brcm|broadcom|rtl|realtek|rtw|aic|ssv|ap6|wifi|wlan'
```

A firmware filename is only a candidate until a kernel message or driver documentation connects it to the bound module. Preserve relevant `dmesg` lines verbatim in the evidence record.

### 5. Device-tree corroboration

The live device tree may identify the wireless node and compatible string. Collect a bounded search without editing it:

```sh
find /proc/device-tree -maxdepth 3 -type f \( -name compatible -o -name status -o -name '*wifi*' -o -name '*wlan*' -o -name '*bluetooth*' \) -print 2>/dev/null
```

For any plausible wireless node, record its path and `compatible` content. The binding still takes priority over a generic device-tree label.

## Evidence record and acceptance

The execution record must state:

- the exact EmuELEC build and kernel;
- each visible wireless interface and RF state;
- the resolved sysfs device path and transport;
- the device identifier available on that transport;
- the actual bound driver/module and its on-disk module path, if exposed;
- firmware request/initialisation evidence, or an explicit absence of it; and
- uncertainty that remains, with no speculative chipset assignment.

Luna Step 4.3 is complete only when this record either identifies the stock driver/firmware binding or demonstrates precisely why the running image does not expose enough evidence. No driver extraction, copying, or configuration is part of this step.
