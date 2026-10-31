# ArchR SSH access and reboot persistence (Steps 5.8h–5.8i)

## Result

As of 2026-10-04, Luna boots the disposable ArchR card, rejoins Wi-Fi by itself, and accepts key-only SSH from Termidor (`ssh luna`, root, `id_rsa_local`) with a stable host identity. Both were verified by a full reboot with no console use:

| Check after reboot | Observed |
|---|---|
| RK915 firmware | `download firmware success` |
| iwd state directory | `STATE_DIRECTORY=/storage/.cache/iwd` |
| Association | `Connected to fc:34:97:d6:0c:c0`, SSID "Home network", 2462 MHz |
| SSH | reachable about 60 s after boot |
| Host key | ED25519 `SHA256:tKesK+3T9te7a1ER0ZP4WY2kbRqrxwcpt/l0TrBIGgE`, accepted with `StrictHostKeyChecking=yes` |

## 5.8h — Installing the SSH key

### Why the password route was dropped

The plan was to set a temporary root password and use `ssh-copy-id`. The user's `passwd` attempt reported a weak password and `password unchanged`. At the time this was wrongly attributed to a read-only `/etc`.

> **Correction (2026-10-04, read-only check):** `/` is mounted read-write and `/etc` is writable by root. `passwd` is BusyBox's applet (`/usr/bin/passwd -> busybox`, v1.36.1); there is no PAM. `/etc/shadow` links to `/storage/.cache/shadow`, which by then held a SHA-512 root hash dated 2026-10-04 (file time 16:48). So one of the attempts did set a root password, and the first failure was BusyBox's weak-password refusal, not a filesystem limit. The password was not needed: key login was installed as below.

### How the key was installed

Root's home is `/storage`, and the image's `sshd_config` reads `.ssh/authorized_keys` with `PermitRootLogin yes` and `StrictModes no`. The public key was sent over the LAN with netcat. Luna listened once and Termidor sent, so no service ran on Termidor:

```sh
# Luna (tty1)
mkdir -p /storage/.ssh
nc -l -p 9999 > /storage/.ssh/authorized_keys
```

```bash
# Termidor
nc -N 192.168.50.34 9999 < ~/.ssh/id_rsa_local.pub
```

A first attempt to serve the key from a temporary HTTP server on Termidor was refused by the session's permission policy and stopped; nothing was served.

### Enabling `sshd`

`sshd.service` is already wanted by `multi-user.target`, but it only starts when `/var/lib/archr/services/sshd.conf` exists (its `ConditionPathExists`) or the kernel command line contains `ssh`. `/var/lib/archr/services` is a link to `/storage/.cache/services`, so the flag persists:

```sh
mkdir -p /var/lib/archr/services && touch /var/lib/archr/services/sshd.conf
systemctl start sshd
```

## 5.8i — Making Wi-Fi and SSH survive a reboot

### The cause: `/var` is a RAM disk

ArchR mounts `/var` as tmpfs. It recreates selected persistent locations as links into `/storage` at boot (`z_02_archr-fhs-bridges.conf`: `services`, `config`, `bluetooth`, `pacman`, `tailscale`, `samba`, …), but two are missing:

| Service | Runtime path | Effect before the fix |
|---|---|---|
| iwd | `STATE_DIRECTORY=/var/lib/iwd` | the saved network (`Home network.psk`) vanished at every boot, and with it Wi-Fi and SSH |
| sshd | `/var/lib/sshd` (the image's link to `/storage/.cache/ssh` is hidden by the tmpfs) | `ssh-keygen -A` generated **new host keys at every boot**; the first reboot produced `REMOTE HOST IDENTIFICATION HAS CHANGED` |

ArchR already creates `/storage/.cache/iwd` and `/storage/.cache/ssh` (`z_03_iwd.conf`, `z_04_openssh.conf`), so the intended persistent locations exist; they just weren't wired up.

### The fix: two systemd drop-ins on `/storage`

`/storage/.config/system.d` appears in systemd's `UnitPath` ahead of `/etc` and `/usr/lib`, so drop-ins placed there override the image's units without modifying them.

`/storage/.config/system.d/iwd.service.d/10-persistent-state.conf`:

```ini
[Service]
Environment=STATE_DIRECTORY=/storage/.cache/iwd
```

The current profile was copied with `cp -a /var/lib/iwd/. /storage/.cache/iwd/` and the directory set to mode 700.

`/storage/.config/system.d/sshd.service.d/10-persistent-hostkeys.conf`:

```ini
[Service]
ExecStartPre=
ExecStartPre=-/bin/sh -c "mkdir -p /storage/.cache/ssh; if [ ! -L /var/lib/sshd ]; then cp -an /var/lib/sshd/. /storage/.cache/ssh/ 2>/dev/null; rm -rf /var/lib/sshd; ln -s /storage/.cache/ssh /var/lib/sshd; fi"
ExecStartPre=/usr/bin/ssh-keygen -A
ExecStartPre=-/bin/sh -c "chmod 600 /var/lib/sshd/ssh_host_*"
ExecStartPre=-/bin/sh -c "chmod 644 /var/lib/sshd/ssh_host_*.pub"
```

The drop-in resets the original `ExecStartPre` list and replays it, with the link restoration first. `ssh-keygen -A` then only creates keys that are missing. The same link was applied live, so the keys of the boot in progress became the permanent ones. `sshd` was not restarted, because the session depended on it.

Both files carry a comment naming the step. Deleting either one returns that service to ArchR's default behaviour.

### Host-key re-trust on Termidor

After the first reboot (before the `sshd` fix), Termidor's `known_hosts` held the earlier key. The ARP entry showed Luna's RK915 MAC `02:b2:de:0d:ca:2a` at 192.168.50.34. The stale entry was removed only after `ssh-keyscan` presented exactly the fingerprint seen after that reboot, and the key file on Luna matched it. The user's `~/.ssh/config` entry `luna` now points to 192.168.50.34.

## Notes and limits

- A second, oddly named profile `Home=20network.psk` (passphrase only) exists alongside `Home network.psk`, probably written by ArchR's settings UI. iwd ignores it and it was left untouched. It contains the passphrase and stays only on the disposable card.
- The card still boots into the tty1 text shell (`systemd.unit=textmode.target`). `systemctl isolate archr.target` switches to the graphical UI until the next reboot.
- Credentials (Wi-Fi passphrase) exist only on the card; nothing secret is in the repository or logbook.
