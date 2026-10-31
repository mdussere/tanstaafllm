---
**Status**: 📋 Draft
**Date**: 2026-09-25
**Priority**: High
**Maintained**: Yes
---

# Luna — Pi hardware and virtual-display setup (workline `luna`)

## Overview

`luna-pi` is the practical first test machine. We will make a quick inventory, including Bluetooth, then configure a VNC-accessible virtual display because the Pi has no physical display.

The goal is a useful Luna-like development environment, not a deep hardware study or a claim that the Pi is Luna. We will match known Luna-facing choices where they are known—such as display shape, a lightweight graphical session, controller-style input, and the eventual Wyoh direction—and mark everything else as a Pi approximation.

Done means: basic Pi facts are recorded, Bluetooth is checked, a lightweight virtual display is reachable by VNC, and its setup/removal path is documented.

## Workline directory layout

- Plan (this file): `worklines/luna/plan_luna.md`
- Produced docs: `worklines/luna/docs/`
- Scripts: `worklines/luna/scripts/` only when useful

## Goals ✅

- Quickly identify the Pi's board, OS, CPU, RAM, storage, graphics/display support, and Bluetooth state.
- Provide a lightweight VNC virtual display for graphical experiments without a physical monitor.
- Make the Pi environment resemble the intended Luna experience where the evidence supports that choice.

## Non-goals ❌

- A comprehensive benchmark, thermal study, or hardware certification.
- Treating Pi behaviour as proof of Luna compatibility or performance.
- Changing the factory Luna card, flashing an experimental image, or implementing Mycroft, Wyoh, Mike, Adam, or Mannie outside a separately green-lit Luna step.

## Key decisions / assumptions

- `luna-pi` is dedicated to TANSTAAFLLM experiments and the user has authorised its administration.
- The Pi has no display; the graphical environment must use a virtual display accessed over VNC.
- Bluetooth presence is an explicit first-pass check.
- Use a small graphical stack and a display profile based on verified Luna facts. Until those facts exist, label the profile as a Pi approximation.
- The factory EmuELEC card is the hardware-reference artefact. Archive images live under `/data/michael/tanstaafllm/luna-images/` (371 GiB free verified on 2026-09-28); the factory card must be archived and physically set aside before any alternative-image write. Its extracted DTB is comparison evidence, not an automatically reusable boot file.

- **Mannie operates the device (user, 2026-10-25, relayed by Professor).** System work on Luna (packages, services, accounts, the root image) belongs to Mannie's line. The Luna line keeps hardware characterisation (audio, boot facts). No SSH to Luna without first telling Mannie on Luna and getting its "go", and no reboot while Mannie runs there.
- **Cell messaging (user, 2026-10-30, relayed by Professor):** the ban on sessions messaging each other is lifted; message any session directly (roster: `worklines/agents.md`). A request that changes this line's work still lands in this plan first, and no session is asked to do what this session's own permissions blocked.

## Risks / constraints

- VNC and a virtual display cannot reproduce Luna's physical screen, controls, battery, or graphics drivers. Record the difference rather than hiding it.
- Remote graphical configuration can make recovery awkward. Keep SSH usable and document how to stop or remove the graphical service.
- Package installation and service configuration are allowed only in the explicitly green-lit setup step.

## 🚦 Green light protocol

- Default: planning and documentation only until you explicitly say **🟩 go Step N**.
- The user has authorised administration of `luna-pi`; that authority applies within a green-lit plan step.
- SSH and read-only inspection start at **🟩 go Step 1**. Installation and VNC configuration start at **🟩 go Step 2**.
- Record material setup choices and results in this workline and the project logbook.
- Real-Luna imaging, first boot, network configuration, or experimental-card modification each require an explicit green light for their relevant step; never write an unverified block device.

## Plan steps (no execution until green light)

### Step 1 — Quick Pi check
**Status**: ✅ Done

- [x] 1.1 Connected through the existing `luna-pi` SSH entry and recorded basic board, OS, kernel, CPU, RAM, and storage facts.
- [x] 1.2 Checked Bluetooth hardware and service state: the adapter is present but off-blocked and could not power on.
- [x] 1.3 Checked available graphics/display support and the current graphical-session state.
- [x] 1.4 Wrote a short fact sheet with Pi-only findings and the few Luna-facing choices they can inform.
- [x] 1.5 Acceptance: the fact sheet answers whether Bluetooth exists and whether the Pi can host a virtual graphical session.

### Step 2 — Create the VNC virtual display
**Status**: 🧪 In progress — VNC transport works, but fresh screenshot evidence is still a uniform blank frame

- [x] 2.1 Selected the existing Labwc and WayVNC stack; no desktop environment or package installation was added.
- [x] 2.2 Configured a resizable headless virtual output and labelled it a provisional Pi profile.
- [x] 2.3 Configured a user service bound only to loopback; SSH remains the recovery and access path, with start/stop/disable commands documented.
- [x] 2.4 Verified the VNC endpoint from this development machine through a temporary SSH tunnel; it returned `RFB 003.008`.
- [ ] 2.6 Replace the separate Labwc service only after deploying a separately named, reversible Wyoh-owned Sway + WayVNC service. Retain `luna-vnc.service` unchanged as the rollback path.
- [ ] 2.7 Use only the existing loopback `127.0.0.1:5900` endpoint and SSH for initial validation. Do not install or expose noVNC/websockify, a LAN listener, or a product service in this step.
- [ ] 2.8 Acceptance: a fresh pytest-owned VNC capture contains a non-uniform Sway surface generated by a visible client; the MCP is proven to address that exact owned session; screenshot files remain ignored evidence; and `luna-vnc.service` can be restored.
- [ ] 2.5 Acceptance: run the live pytest VNC capture in `test/luna/`, inspect its saved screenshot, and confirm visual/input behaviour.

### Step 3 — Simple Luna-like smoke check
**Status**: 🧪 In progress — fresh screenshot evidence is blank; visual/input use remains blocked

- [ ] 3.1 Capture and inspect the VNC session's screen shape and input path with the live `test/luna/` diagnostic; the service is intentionally bare and headless.
- [x] 3.2 Recorded host-side Bluetooth: the adapter exists, but its radio is off-blocked and no external device was paired.
- [x] 3.3 Recorded the remaining differences between the Pi environment and real Luna for Mycroft and Wyoh.
- [x] 3.4 The workline states what can now be tried on the Pi and what must wait for Luna.

### Step 4 — Recheck on real Luna when available
**Status**: 🧪 In progress — stock EmuELEC Wi-Fi path identified; broader direct Luna baseline remains pending.

- [ ] 4.1 Inspect Luna read-only before making any change.
- [ ] 4.2 Replace Pi assumptions with direct Luna facts where they differ.
- [x] 4.3 Completed the read-only SSH collection in `docs/0403_02_stock-emuelec-wifi-driver-result.md`: `wlan0` is SDIO `0296:5348` on `mmc2`, bound to `rk915_sdio` from the live `rk915` module; firmware download succeeds. No Luna state changed.
- [x] 4.4 Acceptance: direct Luna evidence records the stock Wi-Fi hardware path and driver/firmware binding, or each unavailable fact, before any experimental-image comparison or driver-change proposal.
- [x] 4.5 Completed the source/boot-partition assessment in `docs/0405_01_rk915-source-and-archr-compatibility.md`: upstream EmuELEC has no explicit RK915 target support; Arch-R selects/builds it; the stock 5.10.160 module cannot load into Arch-R 6.12.94 with module versioning. No Arch-R file changed.
- [x] 4.6 Completed a read-only inspection of the user-mounted `ARCHR_ROOT`: its `kernel-overlays/base` contains `rk915.ko` and both firmware blobs. The module aliases SDIO ID `0296:5348` and has exact `6.12.94 SMP preempt mod_unload modversions aarch64` vermagic. No driver insertion is needed; any Wi-Fi failure is now an activation/DTB/runtime diagnosis, not a missing-driver diagnosis.

### Step 5 — Preserve the factory reference and stage an alternative-image proof
**Status**: 🧪 In progress — factory card archived and verified (2026-10-03). The disposable card now runs ArchR with a working text console, Wi-Fi and SSH (Step 5.8). dArkOSRE was set aside after an unstable UI loop. Remaining: 5.6 acceptance and 5.7b's panel-overlay provenance note.

- [x] 5.1 Identified the factory EmuELEC card as removable `/dev/sde` (48.8 GiB, labels `EMUELEC`, `STORAGE`, and `EEROMS`) and created the separate `/data/michael/tanstaafllm/luna-images/` archive hierarchy.
- [x] 5.2 Archived the factory card on 2026-10-03 with user-run `scripts/archive_factory_emuelec_card.sh` (identity pinned on exact size and filesystem UUIDs, since the reader serial is shared; kernel read-only during imaging). Golden image `golden/r36-ultra-factory-emuelec_20261003_222430.img.zst` (42,226,178,053 bytes): raw-card and decompressed-image SHA-256 both `a11a4d7318460d5ee9f2090a29e4a4d483d8772d0e81a62ff5d20dbb816e9127`. The earlier 62-byte `…_20260927_220227.img.zst` is a failed attempt (a `sudo` error piped into `zstd`), not an archive. The card itself is now to be set aside unchanged.
- [x] 5.3 Recorded the official dArkOSRE 04262026 beta URL and official ArchR v2.1.1 clone-image URL/checksum in the runbook. The ArchR clone archive passed its published clone-specific SHA-256. The dArkOSRE beta archive was retrieved unchanged, passed a read-only `7z t` integrity test, and was recorded with local SHA-256 `cbeff6e022a958060379894621ff4f84a656ec10a98715b1b2584a270e8cef4d`; the official beta page supplies no checksum, so this is local-corruption evidence only.
- [x] 5.4 Positively identified the former ArchR card as removable `/dev/sde` (58.2 GiB), flashed the 8,301,576,192-byte dArkOSRE image, and confirmed its `BOOT`, `ROOTFS`, and `EASYROMS` partitions after reinsertion. The root defaults were a different clone profile; the exact R36 Ultra DTB folder expected from beta notes is absent, so no board-profile compatibility is claimed.
- [ ] 5.5 First-boot compatibility proof: user reports a rendered PICO-8 front page followed by a recurring `Starting UI` bar. Treat this as an unstable UI-loop failure until read-only logs or SSH evidence identifies the failing component; do not claim controls, internal Wi-Fi, or SSH availability. Treat a network join or configuration write as a separately announced action.
- [x] 5.5a User authorised an offline Wi-Fi profile solely to establish SSH for this disposable dArkOS card. The user ran `scripts/configure_darkos_ssh.sh` successfully against the re-enumerated writable `/dev/sdf2` root partition: it copied the active Termidor WPA-PSK/DHCP profile after removing only its `wlp3s0` binding, enabled `ssh.service`, and authorized the supplied key for `ark`. It neither embeds nor prints a secret. An initial script revision also edited `r36_config.ini`; review proves that file is a boot-regenerated video profile, not physical panel timing, so the reusable script no longer changes it.
- [x] 5.5b Applied the dedicated backup-and-select script on 2026-10-02 to the verified writable `/dev/sde1` BOOT partition. It replaced only the two root DTBs and `logo.bmp` with the bundled `GR36-MB V1.1-20250422` 720×720 fallback; bytewise checks passed and the original G80CA files are retained in `BOOT/tanstaafllm-before-ultra-display/`. This remains an experimental fallback, not an asserted exact board match.
- [x] 5.5c User booted Luna with the fallback and confirmed 720×720 output. The UI remains unstable: a roughly one-second EmulationStation progress sequence (`favorites`, `kodi`, `Starting UI`), PICO-8 interface, then about three seconds of black screen, repeating without an input escape. The user subsequently shut Luna down while `192.168.50.169` continued to answer ping, conclusively excluding that neighbour as Luna. Retain the fallback because it corrected the display; UI-loop diagnosis remains open.
- [ ] 5.6 Acceptance: the factory card is verifiably archived and untouched; the candidate’s provenance and intended DTB are recorded; and the disposable-card result is evidenced as pass, fail, or unavailable without claiming compatibility from an untested release.
- [x] 5.7a The user-run script preserved the corrected dArkOS card as `/data/michael/tanstaafllm/luna-images/darkosre/checkpoints/luna-r36-ultra-darkosre-720x720_20261002_233847.img.zst`, then wrote the locally verified ArchR clone to the identified disposable card. The apparent non-boot is not yet an ArchR failure: this base write omitted the panel-overlay injection performed by Arch R Flasher.
- [ ] 5.7b Return the ArchR card to Termidor and use Arch R Flasher’s **Overlay → Import DTB** path with the preserved factory `r36-ultra.dtb`, producing only `BOOT/overlays/mipi-panel.dtbo`. Then retry the USB-keyboard first boot; no network setup, package installation, arbitrary panel selection, or vendor-DTB replacement is authorised.
- [x] 5.7c The USB-keyboard first-boot observation establishes a working input/VT-switch path: `Ctrl`+`Alt`+`F2` yields a black screen and `Ctrl`+`Alt`+`F1` returns to the graphical frontend. F3–F12 and `Ctrl`+`Alt`+`Delete` have no visible effect. This is not a shell or network result; the black F2 state is an unproven console/getty condition, and graphical network configuration remains unavailable.
- [x] 5.7d Read-only mounted-card inspection explains the blank VTs: default boot is `archr.target` (graphical Sway/EmulationStation) and the image has no `getty@.service` or `autovt@.service`; its sole ordinary shell is `shell.service` on tty1 and only starts under non-default `textmode.target`. `BOOT/overlays/mipi-panel.dtbo` is present (3,440 bytes), though its generator/source-DTB provenance is not proven by that file alone. No card file changed.
- [x] 5.7e Green-lit and applied: `enable_archr_textmode_boot.sh` added the one `systemd.unit=textmode.target` argument to the mounted disposable card’s active BOOT `APPEND` line, after creating `extlinux.conf.tanstaafllm-before-textmode`. The backup byte-matches the prior entry; `pytest -q --timeout=30 test/luna/test_enable_archr_textmode_boot_script.py` passed (3 passed). Console boot confirmation remains physical; no root filesystem, panel-overlay, network, package, or factory-card file changed.
- [x] 5.7f Completed on physical Luna: the root-run, fully removable BusyBox `loadkmap` service drop-in plus offline host-compiled `fr.bkeymap` on STORAGE produces the expected French AZERTY layout in the built-in tty1 textmode shell. The target lacks `kbd`, `loadkeys`, `localectl`, and `vconsole.conf`; source data was pinned to official `kbd` v2.7.1 to match Surcouf’s parser after newer source produced a syntax error. No package installation or Luna networking was used. See `docs/0507_07_archr-text-console-success.md`.

### Step 5.8 — Diagnose ArchR network from the text console
**Status**: ✅ Done (2026-10-04) — Luna on ArchR joins Wi-Fi by itself at boot and accepts key-only SSH (`ssh luna`, 192.168.50.34) with a stable host key. Fixes: the `wifi-rk915.dtbo` overlay (v3), a fixed 2.4 GHz router channel, and two persistence drop-ins on `/storage`. See `0508_03`–`0508_05`.

- [x] 5.8a Completed read-only physical collection: only `lo`; `iw dev` empty; no RK915/WLAN stack module; no RK915/SDIO Wi-Fi bind or firmware event; iwd and ConnMan active but ConnMan sees only `lo`; rfkill empty; `mmc2` (`ff380000.mmc`) exists but has no `mmc2:0001` device; SDIO bus empty; and the live DT has no `wlan-platdata`/`wlan*` node. See `docs/0508_02_archr-live-interface-observation.md`.
- [x] 5.8b Classified the fault from live evidence as SDIO device-enumeration failure, not a service, rfkill, association, credential, firmware-file, or absent-driver-package failure. A missing/non-applied/differently represented DT Wi-Fi configuration and its power/reset/MMC dependencies remain hypotheses, not a proven cause. The next action must be a separately green-lit read-only factory-versus-active DTB comparison before any overlay proposal.
- [x] 5.8c Completed the green-lit read-only comparison in `docs/0508_03_factory-vs-archr-dtb-wifi-comparison.md`. ArchR's `rk3326-gameconsole-eeclone` base DTB describes `mmc@ff380000` as a second SD slot with `cd-gpios` on GPIO0_A2. The factory DTB uses that same pin as the RK915 active-high chip enable, through the vendor `wlan-platdata` driver that ArchR's 6.12 kernel lacks, and `rk915.ko` has no power control. The chip is therefore never powered. Prepared `data/wifi-rk915.dts`/`.dtbo` (`mmc-pwrseq-simple` on GPIO0_A2, `non-removable`, `cap-sdio-irq`, 50 MHz) and validated it offline with `fdtoverlay` on top of `mipi-panel.dtbo`. It is not installed and no Wi-Fi claim is made.
- [x] 5.8d Confirmed on tty1: model `R36S Clone`, `uboot.hwid_adc=b,512`, so the eeclone DTB is the one booted. The user installed overlay v1 with `scripts/enable_archr_wifi_overlay.sh`. Result: `mmc-pwrseq` was allocated, the card was reported non-removable, `mmc2:0001` appeared with SDIO `0296:5348`, `rk915` auto-loaded and probed, and all 48,056 bytes of firmware uploaded and read back correctly. The firmware then never reached `WAIT_PATCH` (`download firmware failed` → `fw_bring_up failed`).
- [ ] 5.8e Overlay v2 adds `supports-rk912`, the DT property that ArchR's `024-mainline-linux-hacks-for-rk915.patch` keys its RK915 MMC quirks on (continuous SDIO clock, CMD52 DAT-busy wait, short CIS). The factory DTB carries it on `ff380000`. v2 also adds `no-sd`/`no-mmc` and the driver's `wifi@1` host-wake child on GPIO0_A5 (the factory `wlan-platdata` says A1; unverified). Validated offline; the script now refreshes the `.dtbo` in place. Result on Luna (2026-10-04): v2 installed by the user. `wlan0` and `phy0` appear and iwd lists phy0 (2.4 GHz, station mode). Every interface-up fails with `ENODEV`: the firmware starts but sends no "reset complete", and `rpu_core_init` fails (`umac init failed`). The driver receives chip events only through the host-wake GPIO interrupt, so GPIO0_A5 is the wrong pin.
- [ ] 5.8f Overlay v3 moves host wake to GPIO0_A1, the pin in Luna's factory `wireless-wlan` node (`423feb4e…e5ca4a`). Validated offline; the script refreshes the `.dtbo` in place. Result (2026-10-04): v3 works. The firmware loads and resets with `Patch 2_1_2 FW Dec 29 2021`, host wake on GPIO0_A1 fires (177+ interrupts), and iwd scans and lists the target WPA2-PSK/CCMP 2.4 GHz AP on channel 11 at -59 dBm. Authentication is refused locally by mac80211 (`AP is in CSA process, reject auth`) on every attempt, while neither Termidor's nor Luna's scan shows a channel-switch element. This matches a known Linux 6.7+ interaction with ASUS routers on auto channel, which leave a stuck CSA in their frames; the reported fix is a fixed 2.4 GHz channel on the router. The Luna Wi-Fi bring-up itself is no longer blocking.
- [x] 5.8g With the router's 2.4 GHz channel fixed at 11, Luna joined "Mick wifi home" with `iwctl` and received DHCP lease 192.168.50.34. Termidor pings it 3/3. Full narrative: `docs/0508_04_archr-wifi-bring-up-result.md`.
- [x] 5.8h SSH works: `ssh luna` (root, `id_rsa_local`) reaches ArchR 20260709, kernel 6.12.94, at 192.168.50.34. The temporary-password route was dropped after BusyBox `passwd` refused a weak password (an initial "read-only `/etc`" explanation was wrong and has been corrected in `0508_05`); the public key was sent to `/storage/.ssh/authorized_keys` with netcat (Luna listening, Termidor sending). `sshd` persists: its flag `/var/lib/archr/services` links to `/storage/.cache/services`, and `sshd.service` is wanted by multi-user. Live check: associated to `fc:34:97:d6:0c:c0` at 2462 MHz, -60 dBm; 3,796 host-wake interrupts.
- [x] 5.8i Green-lit and done over SSH (2026-10-04). ArchR mounts `/var` as tmpfs, which hides the image's persistent links, and its tmpfiles bridges recreate several but not `iwd` or `sshd`. As a result, saved Wi-Fi networks were lost and SSH host keys were regenerated at every boot (seen as a host-key-change warning). Two reversible drop-ins in `/storage/.config/system.d` (part of systemd's UnitPath) fix this:
  - `iwd.service.d/10-persistent-state.conf` sets `STATE_DIRECTORY=/storage/.cache/iwd`; the profile was copied there.
  - `sshd.service.d/10-persistent-hostkeys.conf` restores `/var/lib/sshd -> /storage/.cache/ssh` before `ssh-keygen -A`.
  After a full reboot with no console use, Luna rejoined Wi-Fi, the RK915 firmware loaded, and strict-checking SSH accepted the same ED25519 key `SHA256:tKesK+3T9te7a1ER0ZP4WY2kbRqrxwcpt/l0TrBIGgE`. Revert by deleting either file. A harmless duplicate profile `Mick=20wifi=20home.psk`, probably written by the ArchR UI, was left in place.


### Step 6 — Reshape the ArchR card's storage
**Status**: ✅ Done (2026-10-05) — `/` is 24 GiB (20 GiB free), `/home` 8 GiB, `/storage` 26 GiB; boot, panel, Wi-Fi and SSH (same host key) intact. Result: `docs/0604_01_card-storage-reshape-result.md`.

Answers Wyoh's request (`docs/0000_07_note-from-wyoh-image-limits-and-storage-layout.md`): at least 20 GB on `/`, a real `/home`, and `/storage` kept for bulk data. Target layout:
- p1 `ARCHR` 256 MiB, untouched;
- p2 `ARCHR_ROOT` grown in place to 24 GiB;
- new p3 `LUNA_HOME` 8 GiB at `/home`;
- p4 `STORAGE` ~26 GiB, recreated with its old UUID and its contents restored.

ArchR mounts by label, so the boot path is unaffected.

- [x] 6.1 Wrote `scripts/reshape_archr_card_storage.sh` (user-run root, offline on Termidor). It checks exact size, labels, UUIDs, current geometry and absence of a p4, refuses the system disk, and requires typing `RESHAPE-LUNA-CARD`. A temporary `/run` udev rule keeps the automounter away. Repartitioning uses `sfdisk --wipe never --wipe-partitions never` and keeps the disk label-id. The new ext4 filesystems use ArchR's feature set (`-O ^orphan_file`). `test/luna/test_reshape_archr_card_storage_script.py`: 9 passed, including the script's exact table applied with `sfdisk` to a sparse card-sized file (p1/p2 starts, label-id, bootable flag and types preserved). Awaiting user review and run.
- [x] 6.2 The user ran the script on 2026-10-05. Checkpoint `luna-archr-before-reshape_20261005_124112.img.zst`: raw card = decompressed image SHA-256 `b6a5f410…0e2f1d`. STORAGE tar 282,501,120 bytes, verified against the card before repartitioning.
- [x] 6.3 Repartitioned to the target table; p1 byte-identical; `ARCHR_ROOT` grown to 24 GiB; `LUNA_HOME` created; `STORAGE` recreated with its old UUID, restored and compared; `/home` and `home.mount` added; offline `e2fsck -n` clean.
- [x] 6.4 Boot check over SSH passed, with one fix. The first boot stalled 90 s and `/home` failed to mount: on ArchR, `systemd-udevd` is ordered after `local-fs.target` (via `tz-data.service` → `systemd-tmpfiles-setup`), so a device mount inside `local-fs.target` deadlocks. `home.mount` was moved to `multi-user.target` with `DefaultDependencies=no` and `After=local-fs.target systemd-udevd.service`. After a reboot `/home` mounts by itself and boot takes 13.3 s. The script and its tests were updated to match (28 passed).
- [x] 6.5 Acceptance met; recorded in `docs/0604_01_card-storage-reshape-result.md`. Out of scope and still open: persistent `/var`, users and packages (Step 7).

### Step 7 — Choose Luna's base system on the reshaped card
**Status**: ➡️ Decided and carried out in Mannie's line (user, 2026-10-25): ARCHR_ROOT is replaced by an Arch Linux ARM root, keeping BOOT, LUNA_HOME and STORAGE, and Mannie now operates Luna (packages, services, accounts). See `worklines/mannie/plan_mannie.md` Steps 6 and 7. Relayed by Professor on 2026-10-25; the Luna line does not act on the card. 7.0 (the `michael` account inside ArchR) is done.

- [x] 7.0 Requested by Professor on 2026-10-11 (note `docs/0700_01_note-from-professor-user-accounts.md`), not yet answered; recorded 2026-10-15 when the user asked about it. Propose normal user accounts on Luna in a reply section of that note: `michael` as administrator, unprivileged accounts for agent uses (at least `mannie` and `mike`), a real home for `root` too, group membership, route (a) minimal inside ArchR now versus (b) within Step 7, impact on Wyoh, Mycroft and Mannie, and rollback with root SSH by key kept. Proposal only; no card change before the user's green light. **User decisions (2026-10-15):** one user account, not one per agent (agents are user processes, like `startx`), and passwordless sudo for now. Reply written in the note; recommends route (a). Green-lit by the user ("go", 2026-10-15). Prepared offline: `scripts/luna_user_account.sh` (`--check` read-only, `--apply`, `--undo`; backs up `passwd`, `group` and the real shadow file under `/storage/.local/share/luna-accounts/` first; shadow entry `*` so key login works; sudoers drop-in only if `sudo` exists) and `test/luna/test_luna_user_account_script.py` (8 passed, fake root with the shadow link). **Blocked:** Wyoh holds Luna (`worklines/luna-access.md`), and the access rules forbid changing ArchR's own files such as `/etc/passwd`, so applying needs the user's explicit exception and a Luna slot. Root's real home is left for a later sub-step, after checking what in ArchR relies on `/storage`. **Applied 2026-10-15** (user: "take Luna over, interrupt Wyoh"; exception to the ArchR-files rule). `--check` found ArchR's `/usr/bin/sudo` is a non-setuid shim (it runs the command as the same user), with no `sudo` package in `[archr]`, so no sudoers drop-in was written; `/bin/bash` is setuid root. `michael` (uid 1000; `wheel`, `video`, `audio`, `input`, `render`) was added and logs in by key; backup `/storage/.local/share/luna-accounts/20261014T211515-before-apply` (Luna's clock). After the reboot Luna was slow to come back on Wi-Fi (more than 10 min with no route to 192.168.50.34; cause not found). Once it was back, `michael` was intact, but its shadow line was gone: ArchR's `usercache-setup` rebuilds `/storage/.cache/shadow` from `/usr/cache/shadow` (no package owns it) at every boot, keeping only root. The script now also writes that template, and it was patched on Luna. A second reboot confirmed it: `michael` in both shadow files, key login works, `wyoh-sway` and `sshd` active. Luna released. The user saw the session terminal still open as root, which is expected: `wyoh-sway` runs as root until Wyoh moves it. Left open: a real sudo and root's home, both now part of the Arch Linux ARM root (7.1, Mannie's line). The user asked that every workline be told through Professor: note `worklines/professor/docs/0000_04_note-from-luna-user-account-on-luna.md` (no Professor session identifiable).
- [x] 7.1 **Decided 2026-10-25 by the user: option 2, an Arch Linux ARM root on ArchR's boot path, carried out by Mannie** (`worklines/mannie/plan_mannie.md` Step 7; Professor's relay, 2026-10-25). The new root is to give `michael` a real sudo. Original scope: decide between reworking ArchR in place (option 1) and a conventional Arch Linux ARM or Debian root on ArchR's boot path (option 2, recommended by Wyoh). Record the decision with evidence: kernel modules, firmware and `rk915.ko` transfer, the initramfs's `LABEL=` mounts, persistent `/var`, users and `sudo`, package source, Mesa/Panfrost.

### Step 8 — Find where Luna's microphone is wired
**Status**: 🔄 Resumed and nearly done (2026-10-13): **a USB-C headset gives Luna a working microphone** (8.2e, card 1, `hw:1,0`). Only 8.3, the written conclusion, remains. Paused 2026-10-11 while the headset was ordered. The jack microphone is ruled out under ArchR (8.2c), and the USB-C/jack adapter gave no USB audio (8.2d). Started 2026-10-09 at the user's request ("let's test the record").

The factory device tree describes headphone detection and a headset play/pause button read by an ADC, which suggests a 4-pole headset jack. ArchR exposes one capture device (`hw:0,0`, RK817) but reports only headphone insertion. Mycroft's speech input depends on the answer.

- [x] 8.1 Wrote `test/luna/test_audio_jack_record.py` and its Gherkin contract `test/luna/audio_jack_record.feature`: one live recording per condition (nothing / 4-pole headset / 3-pole headphones, silent or speaking), saved with the jack and mixer state and per-channel RMS/peak under `results/luna/audio-jack/`. The harness check passed: 5.0 s, idle noise floor about −61 dBFS RMS. Note that `Headphones Jack` read "on" during it.
- [x] 8.1b Done 2026-10-09; draft in `docs/0802_01_audio-jack-result.md`. Factory: single-ended mic input, headset button on SARADC ch1 (so the jack's mic line is very probably wired), and the BSP driver puts the headset mic on the right channel and writes `AMIC_CFG1 = 0x30` when recording starts. ArchR: `rockchip,mic-in-differential`, no mic route, and mainline never writes `AMIC_CFG1` (possibly the mic bias, unconfirmed). Detection uses the same pin and polarity (GPIO2_C6, active-high). Live register reading blocked: Luna was offline. Original scope: read-only comparison of the factory DTB and ArchR's DTB/driver for the audio path (hp-det GPIO polarity, mic input selection, mic bias, rk817 codec properties), explaining the flat headset recordings (−61 dBFS, identical to idle) and the always-"inserted" detection; draft `docs/0802_01_audio-jack-result.md` marked "pending user checks". Decided by Professor on the user's behalf (D2, 2026-10-09, `worklines/professor/docs/0503_01_delegated-coordination-log-2026-10-09.md`): no card, overlay or boot change; no commit.
- [x] 8.1c User test reported by Wyoh (note `docs/0800_01_note-from-wyoh-jack-microphone-user-test.md`, 2026-10-11): dictation through Wyoh's Slate (capture from `pcmC0D0c`, card 0, RK817) gave **no signal** with a 4-pole jack headset nor with a microphone-only jack plug. The user's reading is that the jack is output only. This is consistent with 8.1b's two remaining explanations: no microphone line, or a line ArchR does not enable. It does not choose between them. Replied in the note.
- [ ] 8.2 The user runs the five conditions; optionally the headset button with `evtest` (`adc-keys`), and a multimeter check for mic bias on the jack.
- [x] 8.2b Done 2026-10-11 22:47 (Luna granted by Professor, read-only, Luna rebooted afterwards). `test_codec_and_mic_line_snapshot` in `test/luna/test_audio_jack_record.py`; evidence in `results/luna/audio-jack/20261011T224723_snapshot/`. During capture: **`AMIC_CFG0` (0x27) = 0x8c**, so differential mode is on (bit 7), where the factory BSP uses single-ended 0x0a. **`AMIC_CFG1` (0x28) = 0x00**, where the BSP writes 0x30. `DMIC_PGA_GAIN` 0x29 = 0x66 (BSP 0xaa). `AADC_CFG0` 0x18 = 0x08, the same as the BSP. Jack empty: `Headphones Jack` off and GPIO 86 low, so **detection works**; it read high only while a plug was in. SARADC ch1 (the factory headset-button line) reads about 508/1023 ≈ 0.89 V with the jack empty, at rest and during capture. Both 8.1b suspicions are confirmed as register facts; whether they silence the microphone is for 8.2c.
- [x] 8.2c **Green-lit by the user 2026-10-11** ("go pour 8.2c", with access to Luna; exclusive use requested from Professor). Runtime test, reversible at reboot: during a recording, write `AMIC_CFG1 = 0x30` and/or clear the differential bit in `AMIC_CFG0`, and record the right channel with a headset. No boot-partition or card change. If it brings a signal, a device-tree overlay (single-ended input plus a microphone route) would be proposed as a separate step. **Done 2026-10-11, result negative.** Two trials, each a single 10 s recording while the user tapped the headset microphone, with Luna held exclusively (Professor), registers restored and Luna rebooted (0x27/0x28/0x29 back to 0xf0/0x00/0x66).
  - Trial 1 (`results/luna/audio-jack/20261011T225901_trial-8.2c/`): phases as-is, `AMIC_CFG1` = 0x30, plus single-ended, then single-ended alone.
  - Trial 2 (`20261011T230033_trial-8.2c-factory/`): the factory driver's **exact** capture values (`0x27` = 0x0a, `0x28` = 0x30, `0x29` = 0xaa, +12 dB), then two variants of the `0x27` low bits.
  - Every phase stayed at −72 to −79 dBFS RMS: no tapping signal. The writes did reach the codec (read back by `i2cget`; the noise floor shifts by a few dB between phases).
  - SARADC ch1 reads the same ≈ 508/1023 with the headset plugged and with the jack empty.
  - Tests: `test_register_trial` and `test_register_trial_factory_values` (guarded by `LUNA_AUDIO_WRITE=1`).
- [ ] 8.2d If the user plugs a USB-C microphone: record ArchR's card and capture-device names (`arecord -l`, `/dev/snd/pcmC*D*c`) for Wyoh and Mycroft. 2026-10-11: the user offers a **USB-C-to-jack adapter** (not sure it works) with the headset. Test: does it enumerate as USB audio (an active adapter with its own converter) or not (a passive adapter, which Luna can't use)? If it does, record its device names and a tapping recording. Luna requested from Professor. **Tried 2026-10-11 (Luna granted by Professor): no USB audio device.** Plugged in, the adapter showed nothing, and Luna logged no new USB event when it was replugged. Luna enumerated only a GenesysLogic hub (05e3:0610 with 05e3:0608 behind it) with nothing behind it, even after the user reported the adapter and the microphone plugged in. ALSA still lists only card 0 (RK817). Evidence: `results/luna/audio-jack/20261011T230655_usb-audio/` (`test_usb_audio_snapshot`). The adapter is very probably passive, or a hub whose jack is not a USB sound card; it can't give Luna a microphone. Next: a USB sound card or a USB microphone through the USB-C-to-A adapter that worked for the keyboard (`snd-usb-audio.ko` is present in ArchR's kernel).
- [x] 8.2e **Started 2026-10-13: the user plugged a USB-C headset and asked to rerun the tests** (Luna given directly by the user; no Professor session running). When the USB-C headset arrives (it must contain its own converter, "digital" or "DAC" USB-C; a passive one works only with phones): plug it straight into Luna, which recognised a USB-C hub directly in 8.2d, so host mode works. Record its names with `test_usb_audio_snapshot` and a recording through its microphone. Needs Luna from Professor. **Done 2026-10-13: the USB-C headset's microphone works.**
  - **Device:** TTGK "LUDOS Earphones" (USB 3302:3b77), ALSA **card 1 `Earphones`**, capture **`hw:1,0`** = `/dev/snd/pcmC1D0c`. Stable name `hw:CARD=Earphones,DEV=0`; `/dev/snd/by-id/usb-TTGK_Technology_Co._Ltd_LUDOS_Earphones_20250423.1-00`.
  - **Capture format:** S16_LE, 2 channels (identical, a mono microphone), 48 kHz only. Mixer `Headset` capture is 120/120 (0 dB), on.
  - **Levels:** silent −65.6 dBFS RMS; speaking −43.5 dBFS RMS, peak −10.0 dBFS, so **+22 dB**.
  - **After a reboot:** still card 1, enumerated at boot.
  - **Evidence:** `results/luna/audio-jack/20261013T221719_usb-audio/`, `20261013T221752_usb-silent/`, `20261013T221801_usb-speak/` (`test_usb_audio_snapshot`; `test_record_condition[usb-silent]` and `[usb-speak]`, the latter two added for this sub-step).
  - Luna was given directly by the user (no Professor session running), rebooted afterwards, and released in `worklines/luna-access.md`.
- [ ] 8.3 Record the conclusion (headset jack, internal mic, or mic path not enabled in ArchR) in `docs/0802_01_audio-jack-result.md`.

---

## Progress tracking ✅

- ✅ Step 1 — Quick Pi check.
- 🧪 Step 2 — VNC transport verified; fresh framebuffer remains blank.
- 🧪 Step 2.6–2.8 — transition the Pi virtual display to a shared owned Sway + WayVNC session; explicitly authorised 2026-09-30.
- 🧪 Step 3 — Host-side smoke check complete; visible desktop remains blocked.
- 🧪 Step 4 — Stock EmuELEC Wi-Fi driver path identified; broader direct baseline remains pending.
- 🧪 Step 5 — Factory card archived and verified (5.2); dArkOSRE set aside (unstable UI loop); ArchR text console works.
- ✅ Step 5.8 — ArchR Wi-Fi and SSH work on Luna and survive reboots (2026-10-04).
- ✅ Step 6 — Card reshaped: 24 GiB `/`, 8 GiB `/home`, 26 GiB `/storage` (2026-10-05).
- ⏳ Step 7 — Choose the base system on the reshaped card; decision pending.

---

## Time tracking (use `date`) ⏱️

```bash
date
```

### Time log

| Timestamp (`date`) | Update |
|---|---|
| 2026-09-25 | Workline created; no target access or hardware action performed. |
| 2026-09-25 | Plan simplified by user direction: add Bluetooth to the quick check and make a VNC virtual display the next setup task. No target action performed. |
| 2026-09-25T22:54:51+02:00 | Steps 1–3 green-lit. Step 1 completed: Pi 4B / Debian 13 / 8 GiB baseline recorded; Bluetooth is present but off-blocked. Created a separate user-level, local-only Labwc + WayVNC headless session. Its VNC protocol was verified locally and through a temporary SSH tunnel; graphical viewer/input validation remains open. |
| 2026-09-25 | Added a live pytest VNC screenshot diagnostic under `test/luna/` to resolve the reported black screen with persisted visual evidence. |
| 2026-09-25 | Live pytest VNC screenshot diagnostic ran through fresh SSH tunnels. It correctly fails on the uniform blank framebuffer; visible-session configuration remains open. |
| 2026-09-27 | Moved the pending stock-EmuELEC Wi-Fi-driver inventory from Wyoh to Luna. The factory image is reachable over SSH; collection remains read-only and awaits explicit green light. |
| 2026-09-27 | Step 4.3 green-lit and completed read-only: `wlan0` is SDIO `0296:5348` on `mmc2`, bound to `rk915_sdio` from `rk915`; the observed firmware download succeeds. No radio, network, module, or card state was changed. |
| 2026-09-27 | Began the user-authorised, read-only Step 4.5 comparison of the official EmuELEC sources and mounted Arch-R image for RK915 availability and ABI compatibility. No Arch-R file is to be changed. |
| 2026-09-27 | Step 4.5 completed: Arch-R explicitly builds/selects RK915, but the stock 5.10.160 module is ABI-incompatible with Arch-R’s 6.12.94 modversioned kernel. `ARCHR_ROOT` needs a later read-only inspection before any configuration or package conclusion. |
| 2026-09-27 | Step 4.6 completed read-only on the user-mounted root partition: Arch-R’s base kernel overlay contains the matching 6.12.94 RK915 module and its firmware. No card file changed; the next question is live activation/DTB/runtime behaviour, not module installation. |
| 2026-09-27 | Cleaned the shared discussion on keyboard access, factory-image preservation, and a possible dArkOSRE trial. Added pending Step 5: archive the factory reference first, verify a candidate release and DTB procedure, then use only a separately confirmed disposable card after a green light. No Luna card was written or booted. |
| 2026-09-27 | Added a human-executable Step 5 runbook with current official dArkOSRE beta/stable URLs, immutable factory-image archival, checksum handling, disposable-card `dd` gates, and image-supplied GR36S DTB selection. No command was run against a card. |
| 2026-09-27 | Confirmed `/data/tanstaafllm/luna-images/` as the image archive root from user-supplied storage evidence: `/data` has 374 GiB free. |
| 2026-09-28 | Corrected the final archive root to `/data/michael/tanstaafllm/luna-images/`, where the repository `data` symlink points. The official dArkOSRE 04262026 beta archive was retrieved from Mega unchanged (3,939,259,438 bytes) and its local SHA-256 was recorded; this does not replace a maintainer checksum. No SD card was accessed. |
| 2026-09-30 | User separately authorised offline Wi-Fi preconfiguration on the disposable dArkOS card solely to make read-only SSH diagnostics possible. Read-only inspection identified NetworkManager keyfiles and disabled packaged SSH; Termidor’s active profile is portable after removing its `wlp3s0` lock. The profile write and SSH result remain pending; credentials remain outside Git and the logbook. |
| 2026-09-30 | Added `worklines/luna/scripts/configure_darkos_ssh.sh`: a user-run root script that copies the active host NetworkManager profile at runtime, removes its host interface lock, enables dArkOS SSH, and authorizes a supplied public key for `ark`. It neither embeds nor prints a Wi-Fi secret; a static pytest check covers syntax and that policy. |
| 2026-09-30 | User flashed the verified dArkOSRE beta to the identified, disposable former-ArchR `/dev/sde` card. After reinsertion, dArkOS partitions mounted as `BOOT`, `ROOTFS`, and `EASYROMS`. First boot renders a PICO-8 front page but loops on `Starting UI`; no stable compatibility, control, Wi-Fi, or SSH result is claimed. |
| 2026-09-30 | An initial revision of the user-run dArkOS setup script changed `r36_config.ini` to 720×720 alongside Wi-Fi/SSH, preserving a one-time rollback copy. A USB-reader disconnect had left the old Btrfs mount stale and force-read-only, so the user remounted the re-enumerated card before running it. |
| 2026-09-30 | User ran the Luna offline setup script successfully against the re-enumerated, writable dArkOS `/dev/sdf2` root partition (`ROOTFS1`), applying the initial `r36_config.ini` setting, Wi-Fi profile, SSH enablement, and `ark` public key. No credential was logged. Later BOOT/log review shows dArkOS regenerated that setting from the DTB hardware profile, so it is not physical display evidence. |
| 2026-10-02 | Reviewed the mounted disposable card after the reported 640×480-like output. Its active BOOT DTBs exactly matched the G80CA Panel 8 640×480 profile and the boot log proved `r36_config.ini` was regenerated accordingly. The image’s only bundled 720×720 fallback is GR36; the advertised exact Ultra profile is absent. After static pytest checks passed, installed that BOOT-only fallback on verified writable `/dev/sde1`; its three active files byte-match the bundled sources and the original files are snapshotted. Physical boot result pending. |
| 2026-10-02T23:01:35+02:00 | User confirmed the installed fallback produces 720×720 output, but the EmulationStation/PICO-8/black-screen loop is unchanged. Passive neighbour inspection found only `.169`; a non-interactive `ark` SSH attempt with the installed key received `Connection refused` on port 22. The user then shut Luna down and `.169` continued to answer ping, conclusively excluding it as Luna. |
| 2026-10-03T22:56+02:00 | Step 5.2 completed: the user ran the new read-only factory archive script; the golden image's raw-card and decompressed SHA-256 match (`a11a4d73…6e9127`). Static review of the local `mipi-panel.dtbo` shows Arch R Flasher's DTB import produced only panel/audio fragments: no `wlan-platdata`, `sdio-pwrseq`, or `ff380000` content, while the factory DTB has all three. ArchR therefore boots its own base DTB without the factory Wi-Fi wiring. |
| 2026-10-03T23:15+02:00 | Step 5.8c completed read-only: the factory-versus-ArchR DTB comparison shows `ff380000` described as an SD slot whose card detect is the RK915 chip enable (GPIO0_A2). Proposed `wifi-rk915.dtbo` compiled and validated offline; not installed. |
| 2026-10-04 | 5.8d: overlay v1 on Luna powers and enumerates the RK915 and `rk915` loads, but the firmware never reports ready. Root cause traced to the missing `supports-rk912` quirk property in ArchR's kernel patch; overlay v2 prepared (5.8e). |
| 2026-10-04 | 5.8f/g: overlay v3 (host wake on GPIO0_A1) brought the RK915 fully up; the stuck-CSA refusal was cleared by fixing the router's 2.4 GHz channel to 11. Luna obtained 192.168.50.34. |
| 2026-10-04 | 5.8h/i: SSH key installed with netcat (the password route was dropped). iwd networks and SSH host keys made persistent with two `/storage/.config/system.d` drop-ins; verified by an unattended reboot. |
| 2026-10-04 | Received Wyoh's note on the ArchR image's limits (`0000_07`). Added Step 6, the storage reshape (design `0601_01`), and a Step 7 placeholder for the base-system decision. Corrected the 5.8h claim that `/etc` is read-only. No card change. |
| 2026-10-05 | Step 6 done: the user ran the reshape script; root 24 GiB, `/home` 8 GiB, `/storage` 26 GiB. A `/home` boot deadlock (udevd ordered after `local-fs.target` on ArchR) was fixed by moving `home.mount` to `multi-user.target`; boot 13.3 s. |
| 2026-10-09 | Step 8 started (user: "let's test the record"): recording test written; headset recordings flat (−61 dBFS, as idle). 8.1b desk comparison (Professor D2) points to ArchR's differential mic mode and an unwritten `AMIC_CFG1`. |
| 2026-10-11 22:45 | Wyoh's note `0800_01`: the user's dictation test got no signal from the jack (headset and mic-only plug). Recorded as 8.1c; proposed 8.2b (read-only, needs Luna from Professor), 8.2c (runtime register test, needs green light) and 8.2d (USB-C mic names). |
| 2026-10-11 22:47 | 8.2b done on Luna (Professor's slot, read-only, rebooted): during capture `AMIC_CFG0` = 0x8c (differential), `AMIC_CFG1` = 0x00 (BSP 0x30); jack detection works (off/low when empty). |
| 2026-10-11 | 8.2c done (user go, exclusive Luna): codec set to the factory driver's exact capture values at runtime; still no signal from the headset microphone. Registers restored, Luna rebooted. |
| 2026-10-11 | 8.2d: the user's USB-C/jack adapter gives no USB audio device (only a GenesysLogic hub enumerated). Luna rebooted and released. |
| 2026-10-11 | Step 8 paused: the user is ordering a USB-C headset with a microphone; resume with 8.2e in a few days. |
| 2026-10-13 | 8.2e done: the USB-C headset (LUDOS Earphones) enumerates as ALSA card 1; its microphone records speech at +22 dB over silence; still present after a reboot. |

---
| 2026-09-30 | User explicitly authorised the reversible transition from the separate Labwc VNC session to a shared, Wyoh-owned Sway + WayVNC session. Existing WayVNC, `swaybg`, and `lxterminal` will be reused; no noVNC, LAN listener, or Luna claim is in scope. |

## Workline artifacts

- `worklines/luna/docs/0000_01_luna-hardware-discovery-brief.md` — original scope record.
- `worklines/luna/docs/0000_02_vnc-and-bluetooth-revision.md` — current simplified scope and environment decision.
- `worklines/luna/docs/0101_01_luna-pi-quick-check.md` — completed Pi fact sheet and Bluetooth result.
- `worklines/luna/docs/0201_01_vnc-virtual-display.md` — VNC transport, recovery, and visible-desktop status.
- `test/luna/` — live VNC diagnostic, readable scenario, and captured screenshot evidence.
- `worklines/luna/docs/0202_01_vnc-screenshot-diagnostic.md` — persisted visual evidence and current blank-frame block.

- `worklines/luna/docs/0000_03_r36-ultra-wifi-driver-discussion-a.md` — cleaned source discussion: stock-image preservation, Arch-R bring-up, DTB, and Wi-Fi-driver evidence plan.
- `worklines/luna/docs/0000_04_r36-ultra-wifi-driver-discussion-b.md` — cleaned source discussion: obtaining Wi-Fi diagnostics when Arch-R has no network or exposed terminal.
- `worklines/luna/docs/0403_01_stock-emuelec-wifi-driver-procedure.md` — pending, read-only SSH collection sequence and acceptance criteria for the factory image’s Wi-Fi driver/firmware binding.
- `worklines/luna/docs/0403_02_stock-emuelec-wifi-driver-result.md` — completed Step 4.3 evidence: RK915 SDIO path, driver binding, firmware behaviour, and limits.
- `worklines/luna/docs/0405_01_rk915-source-and-archr-compatibility.md` — completed source, boot, and root-overlay comparison; rules out copying the stock module and confirms Arch-R already contains its matching module and firmware.
- `worklines/luna/docs/0206_01_shared-sway-wayvnc-transition.md` — shared-session transition, recovery, and validation design.
- `worklines/luna/docs/0000_05_archr-rk915-runtime-diagnosis-discussion.md` — cleaned discussion record: console-access limits, factory BSP preservation, candidate-image comparison, and the staged dArkOSRE proof proposal.
- `worklines/luna/docs/0501_01_factory-archive-and-darkosre-runbook.md` — detailed human procedure and verified official dArkOSRE URLs for the pending Step 5 archive and candidate-card proof.
- `worklines/luna/scripts/configure_darkos_ssh.sh` — user-run offline NetworkManager/SSH/key configuration for the disposable dArkOS card; requires its mounted ROOTFS and a public key path.
- `worklines/luna/docs/0505_01_darkosre-first-boot-observation.md` — user-observed first-boot UI-loop result and read-only diagnostic boundary.
- `worklines/luna/docs/0505_02_darkosre-720x720-profile-correction.md` — mounted-card evidence, exact control-layer correction, and the constrained GR36 fallback decision.
- `worklines/luna/docs/0507_01_archr-return-and-usb-keyboard-trial.md` — user-run archive-then-ArchR-write procedure and restricted USB-keyboard first-boot observation.
- `worklines/luna/docs/0507_02_archr-flasher-panel-overlay-gap.md` — explains why the base raw write differs from Arch R Flasher and defines the missing, constrained panel-overlay stage.
- `worklines/luna/docs/0507_03_archr-keyboard-vt-observation.md` — observed keyboard and virtual-terminal behaviour; separates the demonstrated input path from an unproven console and network state.
- `worklines/luna/docs/0507_04_archr-mounted-console-diagnosis.md` — read-only systemd/boot configuration evidence explaining blank F2–F12 and confirming a panel overlay exists.
- `worklines/luna/docs/0507_05_archr-textmode-console-runbook.md` — backup-first BOOT-only path to the image’s built-in tty1 textmode shell and exact graphical-boot restore.
- `worklines/luna/docs/0507_06_archr-offline-azerty-loader.md` — mounted-card evidence and reversible offline French AZERTY loader procedure for the tty1 shell.
- `worklines/luna/scripts/configure_archr_console_azerty.sh` — root-run target-only drop-in/keymap installer and restore path.
- `test/luna/test_configure_archr_console_azerty.py` — static safety and explicit host-keymap-generation checks.
- `worklines/luna/docs/0508_02_archr-live-interface-observation.md` — first physical tty1 network fact: `ip link` reported only loopback; it is insufficient to identify the activation failure.
- `worklines/luna/docs/0507_07_archr-text-console-success.md` — physical Luna confirmation that the built-in tty1 text console and offline AZERTY loader work; it records scope and independent reversals.
- `worklines/luna/scripts/enable_archr_textmode_boot.sh` — reversible, backup-first one-argument BOOT configuration switch between graphical ArchR and its built-in tty1 textmode shell.
- `test/luna/test_enable_archr_textmode_boot_script.py` — deterministic enable/restore and safety-gate checks for that boot-entry transformer.
- `worklines/luna/docs/0508_01_archr-console-network-investigation-plan.md` — staged console collection and evidence-first network diagnosis plan; no connection action yet.
- `worklines/luna/scripts/archive_darkos_and_flash_archr.sh` — serial-locked, confirmation-gated root script that archives the corrected disposable dArkOS card before writing the verified ArchR clone.
- `worklines/luna/docs/0000_06_device-tree-course.md` — short learning course on DTS/DTB/DTBO, overlays and bindings, using the Luna Wi-Fi case as the worked example.
- `worklines/luna/docs/0508_03_factory-vs-archr-dtb-wifi-comparison.md` — factory-versus-ArchR DTB evidence for the unpowered RK915, the proposed overlay, its offline validation, residual risks, and the gated install.
- `worklines/luna/data/wifi-rk915.dts` / `.dtbo` — proposed RK915 power-sequence overlay; not installed.
- `worklines/luna/docs/0508_04_archr-wifi-bring-up-result.md` — the four-stage Wi-Fi bring-up (power, quirks, host wake, router CSA), the final overlay, and its limits.
- `worklines/luna/docs/0508_05_archr-ssh-and-persistence.md` — SSH key installation by netcat, and the `/storage` drop-ins that keep Wi-Fi networks and SSH host keys across reboots.
- `worklines/luna/docs/0000_07_note-from-wyoh-image-limits-and-storage-layout.md` — Wyoh's coordination note: ArchR card limits, software Wyoh needs, proposed layout and directory plan.
- `worklines/luna/docs/0601_01_card-storage-reshape-design.md` — Step 6 design: current geometry, label-based boot facts, target layout, offline procedure, boot check and rollback.
- `worklines/luna/docs/0604_01_card-storage-reshape-result.md` — Step 6 result: checkpoint hashes, verified layout, the `/home` udev deadlock and its fix.
- `worklines/luna/scripts/reshape_archr_card_storage.sh` — user-run, checkpoint-first offline reshape of the ArchR card.
- `test/luna/test_reshape_archr_card_storage_script.py` — safety, geometry (sfdisk on a sparse card-sized file) and `home.mount` ordering checks.
- `docs/03_r36-ultra-bring-up-story.md` — plain-language narrative of preparing the R36 Ultra card and getting it online, for readers outside the workline.
- `worklines/luna/scripts/enable_archr_wifi_overlay.sh` — backup-first install, in-place update, and restore of `wifi-rk915.dtbo` on the ArchR BOOT partition.
- `test/luna/test_enable_archr_wifi_overlay_script.py` — deterministic install/update/restore and refusal checks.
- `worklines/luna/scripts/archive_factory_emuelec_card.sh` — user-run, read-only, identity-pinned golden archive of the factory card with raw-versus-decompressed SHA-256 verification.
- `test/luna/test_archive_factory_emuelec_card_script.py` — static safety checks that the archive script never writes the card.
- `worklines/luna/scripts/select_darkos_ultra_display_fallback.sh` — backup-first selection of the image-bundled GR36 720×720 fallback on the disposable card.
## Input affordance amendment — 2026-09-25

| 2026-09-27 | Step 5 green-lit: created the ignored `/data/michael/tanstaafllm` image hierarchy and `data` symlink; identified the factory card as `/dev/sde` and unmounted it cleanly. Full-card archival could not start because non-interactive `sudo` is unavailable. Downloaded and verified the official ArchR v2.1.1 clone archive (1.51 GiB) against its published clone SHA-256. The official dArkOSRE beta URL is recorded; its automated Mega download failed due client/runtime incompatibility. |
The later real-Luna inventory must include physical buttons/sticks and available visible feedback affordances for Mycroft composition input. `luna-pi` remains only a graphical approximation; this creates no Pi or Luna action.
