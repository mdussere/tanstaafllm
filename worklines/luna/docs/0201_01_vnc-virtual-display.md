# Luna Pi VNC virtual display

> **Freshness:** 🟡 historical · **Written:** 2026-09-27 · **Checked:** 2026-10-31 · **Step:** luna 2.1 ✅

**Status:** VNC transport complete; visible desktop blocked
**Question answered:** Is a lightweight, recoverable virtual display available without a physical Pi monitor?

## Installed setup

A user-level service, `luna-vnc.service`, is enabled for user `michael`. It starts a separate headless Labwc session and WayVNC. It does not alter the Pi's existing graphical session.

- WayVNC listens only on `127.0.0.1:5900`; it is not exposed on the LAN.
- VNC authentication is disabled because the endpoint is reachable only through authenticated SSH. Do not change the bind address without adding VNC authentication.
- The headless output is virtual and may resize to the VNC client. It is a Pi approximation, not a verified Luna screen profile.
- The separate Labwc autostart is controlled by this workline; current visible-surface attempts are recorded in `0202_01_vnc-screenshot-diagnostic.md`.

## Access and recovery

From the development machine, open a tunnel and connect a VNC client to `localhost:5900`:

```bash
ssh -N -L 5900:127.0.0.1:5900 luna-pi
```

Useful recovery commands on the Pi:

```bash
systemctl --user status luna-vnc.service
systemctl --user restart luna-vnc.service
systemctl --user disable --now luna-vnc.service
```

The unit and configuration are under `~/.config/systemd/user/luna-vnc.service` and `~/.config/luna-vnc/`.

## Verification

The service runs only Labwc and WayVNC, accepts a loopback TCP connection on port 5900, and returned the `RFB 003.008` protocol greeting both locally and through a temporary SSH tunnel. A graphical viewer was not automated; use the tunnel above to open one.

One harmless Xwayland socket warning remains because the normal Pi session already owns `:0`; it does not affect the Wayland/VNC session.


## Screenshot diagnostic update

The live pytest capture under `test/luna/` reaches this service through fresh SSH tunnels, but its saved frame remains uniform (black or grey depending on the attempted session surface). The VNC protocol is therefore working; the graphical session is not yet a usable rendered desktop. See `0202_01_vnc-screenshot-diagnostic.md`.
