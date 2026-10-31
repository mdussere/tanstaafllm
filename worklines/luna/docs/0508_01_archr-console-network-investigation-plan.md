# ArchR network investigation from the local text console

> **Freshness:** 🟡 historical · **Written:** 2026-10-04 · **Checked:** 2026-10-31 · **Step:** luna 5.8 ✅

> **Outcome (2026-10-04):** this plan was carried through to a working connection. The live collection is in `0508_02`, the DTB comparison in `0508_03`, the Wi-Fi bring-up in `0508_04`, and SSH and reboot persistence in `0508_05`.

**Question:** Once the local ArchR console works, how should we investigate
unavailable graphical network configuration without guessing drivers,
credentials, or connection settings?

## Boundary

This is a staged **read-only** diagnosis. Do not scan, connect, enter a Wi-Fi
passphrase, edit connection files, enable SSH, install packages, or copy a
factory driver until the collected evidence identifies the failing layer.

The mounted ArchR root already contains the matching RK915 kernel module and
firmware for the factory chip’s SDIO ID. The remaining uncertainty is live
activation: device-tree/MMC exposure, module binding, firmware runtime,
rfkill, ConnMan/iwd services, or frontend integration.

## Phase 1 — prove the console and collect the live state

At the textmode tty1 root shell, run the following commands and transcribe or
photograph their complete output:

```sh
id
tty
ip -br link
iw dev
rfkill list
lsmod | grep -Ei 'rk915|wlan|cfg80211|mac80211'
dmesg | grep -Ei 'rk915|wlan|wifi|sdio|mmc|firmware|rfkill'
systemctl --no-pager --full status iwd.service connman.service
connmanctl technologies
connmanctl services
journalctl -b -u iwd.service -u connman.service --no-pager
```

`connmanctl technologies` and `connmanctl services` are observation commands
in this phase; do **not** run `scan`, `connect`, `agent on`, or `config`.

## Phase 2 — classify before changing anything

| Evidence | Likely layer | Next action, still pending a green light |
| --- | --- | --- |
| No Wi-Fi interface and no RK915 bind/firmware log | DTB/MMC/module activation | Compare live SDIO/MMC and module-load evidence against the factory record. |
| Wi-Fi interface exists but is rfkill-blocked | RF policy | Identify the responsible rfkill path before any unblock. |
| Interface exists but iwd/ConnMan failed | Service/runtime | Read service journal and configuration; do not restart yet. |
| iwd and ConnMan healthy but no UI option | Frontend integration | Inspect ArchR/EmulationStation network-menu integration. |
| A visible service is available but unconnected | Credentials/association | Prepare a separately authorised connection method that never commits the passphrase. |

## Phase 3 — later configuration only

Only after Phase 2 identifies a viable interface and service path should we
prepare a one-purpose, reversible Wi-Fi and key-based SSH configuration step.
That step must keep the passphrase outside Git and demonstrate recovery to the
known textmode shell.
