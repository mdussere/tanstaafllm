# dArkOSRE first-boot observation — UI loop

**Question:** What did the first dArkOSRE boot establish on the disposable former-ArchR card?

## Observed result

After the verified `dArkOSRE_R36_trixie_04262026.img` was written to the identified 58.2 GiB `/dev/sde` card, reinsertion showed the expected image partitions: `BOOT`, `ROOTFS`, and `EASYROMS`.

The user then reported that Luna renders a PICO-8 front page, but repeatedly returns to the same `Starting UI` loading bar. This is an unstable UI-loop result, not successful operating-system compatibility.

## What it suggests

- The image reaches a visible rendered stage; a purely blank-screen failure is not observed.
- The UI or a prerequisite service appears to fail or restart after that stage.
- This observation alone does not establish that the selected DTB, controls, audio, Wi-Fi, storage expansion, or SSH works.

## DTB limitation

The beta image's BOOT tree does not contain the exact `GR36S-MB V1.4-2025-07-30 R36 Ultra` profile named in the beta notes. It contains a nearer `GR36-MB V1.1-20250422` clone profile, but that is a different board revision. It must remain an explicitly experimental configuration, not an asserted match.

## Next safe diagnostic

Do not change DTBs again or join a network. If the image exposes SSH through an already available network path, collect read-only boot/service logs and process status. Otherwise power Luna off and return the card to Termidor for read-only ROOTFS/BOOT inspection. Record whether the loop happens before or after any visible device-selector action.

## Offline Wi-Fi / SSH preflight — 2026-09-30

The mounted dArkOS ROOTFS uses NetworkManager's `keyfile` plugin. Its normal persistent profile store is `etc/NetworkManager/system-connections/`; no connection profile is preinstalled. The packaged `ssh.service` exists but is not enabled.

Termidor's active `Mick wifi home` profile is WPA-PSK, DHCP, autoconnecting, has no MAC/BSSID/user permission lock, and uses only `connection.interface-name=wlp3s0`. Copying that root-owned profile to dArkOS, removing that one interface lock, enabling `ssh.service` offline, and placing the existing `id_rsa_local.pub` into `ark`'s `authorized_keys` is the planned secret-safe path. The profile copy and boot-time connection have not yet been performed.
