# Transition — shared Sway and WayVNC virtual display

**Step:** Luna 2.6–2.8
**Status:** implementation authorised 2026-09-30
**Question:** Can the Pi’s VNC endpoint display the exact Sway instance operated through Wyoh MCP?

## Before and after

| Before | After |
| --- | --- |
| `luna-vnc.service` starts Labwc and WayVNC | `wyoh-sway-vnc.service` starts pinned Sway and WayVNC |
| MCP starts a separate disposable Sway child | MCP reads the descriptor of this named Wyoh-owned session |
| VNC and MCP describe different desktops | VNC and MCP share one compositor and output |

## Safety and recovery

- The existing `luna-vnc.service` unit and configuration are retained unchanged.
- The new service is separate, user-level, and loopback-only on `127.0.0.1:5900`.
- Initial activation stops but does not disable the old service. Rollback stops the new service and starts the old one.
- The service reuses installed WayVNC, `swaybg`, and `lxterminal`; it uses the pinned Wyoh Sway prefix with its matching library path.
- No noVNC/websocket endpoint or LAN listener is configured in this slice.

## Acceptance evidence

- A fresh SSH-tunnel VNC capture persists a non-uniform rendered Sway image under ignored `results/luna/`.
- A real MCP client queries and actuates the same named Sway session; an `lxterminal` window is observed through Sway IPC.
- A screenshot MCP result is a local file reference and digest, not image bytes.
- The documented rollback command restores the retained Labwc VNC service.
