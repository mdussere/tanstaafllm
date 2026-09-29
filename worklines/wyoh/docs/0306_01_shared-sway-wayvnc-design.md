# Design — one owned Sway session for MCP and WayVNC

**Step:** Wyoh 3.6
**Status:** implementation authorised 2026-09-30
**Question:** How can MCP operate the same virtual display that VNC presents without attaching to an arbitrary desktop?

## Decision

The shared session is a named, user-level `wyoh-sway-vnc.service` on `luna-pi`:

```text
wyoh-sway-vnc.service
    └─ pinned Sway 1.10.1 (headless/Pixman)
         ├─ WayVNC, loopback only, same Wayland display
         ├─ swaybg / visible test client
         └─ private session descriptor: exact Sway IPC socket

development MCP client ── SSH stdio ── Wyoh MCP --shared-vnc-session
                                              └─ reads fixed private descriptor
```

The descriptor is written by an Sway child with owner-only permissions. The MCP does not accept a socket path, does not consult ambient `SWAYSOCK`, and checks that the descriptor is owned by its user and points inside that user’s runtime directory. This is an explicit attachment to one named Wyoh-owned service, not a generic ability to attach to “one Sway or another.”

## Deployment and recovery

`Makefile` deploys `src/wyoh/` with `rsync --checksum` through the existing SSH identity to a user-owned Pi directory. It has separate preview, deploy, activate, status, and rollback targets. Deploy itself changes no running process. Activation stops the existing `luna-vnc.service` only after the new source is present and can be reverted by starting that retained service again.

No package manager is required for this slice: the Pi already has WayVNC, `swaybg`, `lxterminal`, `grim`, `make`, and `rsync`; the pinned Sway prefix remains the Sway binary. No noVNC/websockify, LAN listener, system service, or Luna change is included.

## Screenshot contract

The screenshot MCP tool is development-only. It runs the existing `grim` client inside the owned session, chooses a timestamped file beneath ignored `results/wyoh/`, and returns only the absolute result path, SHA-256, size, and capture time. It never serialises image bytes into the MCP response.

## Validation

1. Preview and deploy source using Make without changing a service.
2. Activate the new loopback-only Sway + WayVNC service and prove its IPC descriptor exists.
3. Through a real MCP client, read Sway state, launch a visible `lxterminal`, observe its window event, capture a file, then close it.
4. Capture the VNC framebuffer through an SSH tunnel into ignored evidence and inspect it for the rendered client.
5. Confirm the old Labwc service is still installed and demonstrate the rollback command.

The first visible Sway workspace may be black before an application appears; that alone is not a Sway/VNC failure.
