# Result — shared Sway, WayVNC, and MCP validation

**Step:** Wyoh 3.6

**Status:** completed on 2026-09-30

**Scope:** `luna-pi` development evidence only; not Luna hardware or product-shell evidence.

## Question

Can an explicitly named, Wyoh-owned headless Sway session be presented through loopback-only WayVNC and operated through a descriptor-bound MCP without attaching to an arbitrary desktop?

## Result

Yes, for the development slice. `wyoh-sway-vnc.service` owns the pinned headless Sway 1.10.1 process and its WayVNC child. It remains active after VNC clients disconnect. The MCP reads only the service-written owner-private descriptor, launches `lxterminal` through Sway IPC, observes the resulting Sway `window` event, writes a server-side screenshot path/digest without image bytes, and does not stop the service when the MCP stream ends.

An independent VNC client, connected through a temporary loopback SSH tunnel, captured a frame before the terminal launch and another while Sway reported the terminal visible. The two frames differed. The test closed the terminal and the tunnel. The screenshots were retained only under ignored `results/`; they were not inserted into agent context at the user's request.

## Deployment and ownership evidence

- `make wyoh-deploy-preview` executed two `rsync --dry-run` transfers only. It did not invoke `systemctl`.
- `make wyoh-deploy` synchronised `src/wyoh/` and the user unit to `/home/michael/.local/share/tanstfaafllm/wyoh` and reloaded user-unit metadata. It did not start, stop, enable, or disable a service.
- The active `wyoh-sway-vnc.service` includes only a loopback `127.0.0.1:5900` WayVNC listener. Its descriptor names `/run/user/1000/sway-ipc.1000.25831.sock` and `wayland-2`.
- The retained `luna-vnc.service` unit is still installed and disabled. `make wyoh-rollback` remains the explicit recovery operation; it was not exercised during the final evidence run, so the currently active session was not disrupted.

## Automated evidence

| Check | Command | Outcome |
| --- | --- | --- |
| Deterministic bridge/deploy checks | `pytest -m 'not live and not integration' test/wyoh -q` | `11 passed, 5 deselected` after the VNC test was added. |
| Descriptor-bound MCP control | `WYOH_SHARED_VNC_LIVE=1 pytest -m live test/wyoh/test_mcp_over_ssh.py::test_luna_pi_shared_sway_vnc_session_is_operated_over_mcp -q` | `1 passed in 4.69s`; a visible `lxterminal` window event and MCP screenshot metadata were saved. |
| Independent VNC framebuffer proof | `WYOH_SHARED_VNC_LIVE=1 pytest -m live test/wyoh/test_shared_sway_vnc.py -vv -s` | `1 passed in 6.97s`; frame-difference assertion passed. |

Successful independent-VNC evidence is retained at `results/wyoh/shared-sway-vnc-vnc/20260929T230828Z/`:

- `before-terminal.png` and `terminal-visible.png` — ignored local VNC captures.
- `evidence.json` — Sway reports `lxterminal` (`app_id: lxterminal`) as `visible: true` for the terminal-visible capture.
- `server.stderr.log`, capture logs, and `ssh-tunnel.stderr.log` — complete text diagnostics.

The MCP-only proof immediately before it is retained at `results/wyoh/shared-sway-vnc/20260929T230437Z/`; it records the server-chosen remote screenshot path, 10,392 bytes, and SHA-256 `16faec2ad49ea363884cd88f1aae55db74aae067f8c7bab97cc8d85445f15b47`.

## What this does and does not establish

This establishes one Pi-owned virtual session, its loopback VNC presentation, its fixed-descriptor MCP attachment, remote screenshot-to-file behaviour, and a rendered-frame change caused by an MCP operation. It does not establish controller input, a usable handheld shell, noVNC, authentication, multi-user access, physical Luna graphics, power/thermal cost, or authority suitable for Mike/Mycroft. The broad `sway_command` tool remains explicit full-development authority, not a product capability.
