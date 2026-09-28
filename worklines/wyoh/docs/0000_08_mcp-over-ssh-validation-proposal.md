# Proposal — development-only full-fidelity Sway IPC MCP bridge over SSH

**Status:** implemented and validated on 2026-09-28 as development-only evidence. See [`0305_01_mcp-over-ssh-validation-result.md`](0305_01_mcp-over-ssh-validation-result.md). The bridge covers every documented Sway IPC request and event only in an isolated child session; it changed neither a user session nor Luna's stock image.

## Question answered

How can a development host exercise every documented Sway 1.10.x IPC feature through a Python Model Context Protocol (MCP) server on `luna-pi`, while keeping that broad authority out of the product and consumer boundary?

## Proposed topology

```text
development-host MCP client
        │ stdin / stdout
        ▼
ssh -T luna-pi -- python3 <versioned Wyoh MCP entry point>
        │ stdin / stdout carried inside the authenticated SSH session
        ▼
development-only Python MCP server on luna-pi
        │ complete direct Unix-domain Sway IPC mapping
        ▼
dedicated headless Sway 1.10.1 child session
```

This is **MCP over stdio carried by SSH**, rather than a TCP port-forward. It creates no listener on `luna-pi`, keeps authentication and host trust in the existing SSH configuration, and terminates the server when the client closes its stream. The [official Python SDK](https://github.com/modelcontextprotocol/python-sdk) supports stdio servers and clients; its [stdio guidance](https://py.sdk.modelcontextprotocol.io/latest/run/) treats stdout as protocol-only and directs logs to stderr.

The Sway session is a disposable headless child, using the same pinned `luna-pi` proof prefix and lifecycle as `test/wyoh/sway_ipc_probe.py`. The bridge must never attach to a user desktop or the real Luna stock image.

## Full IPC coverage manifest

The server exposes each documented request as a named MCP tool rather than hiding the protocol behind an opaque raw-socket escape hatch. The baseline list is the [Sway 1.10 IPC manual](https://github.com/swaywm/sway/blob/1.10/sway/sway-ipc.7.scd); implementation must still verify it against the manual shipped with the tested Sway package. Responses preserve the Sway reply JSON without product-level semantic interpretation.

| Sway IPC request | MCP tool | Input / result |
| --- | --- | --- |
| `RUN_COMMAND` | `sway_command` | An arbitrary Sway command string; the complete command reply array. |
| `GET_WORKSPACES` | `sway_get_workspaces` | No input; raw workspace array. |
| `SUBSCRIBE` | `sway_subscribe` | Event-name set; a subscription handle. |
| `GET_OUTPUTS` | `sway_get_outputs` | No input; raw output array. |
| `GET_TREE` | `sway_get_tree` | No input; raw container tree. |
| `GET_MARKS` | `sway_get_marks` | No input; raw mark array. |
| `GET_BAR_CONFIG` | `sway_get_bar_config` | Optional bar identifier; raw bar identifiers/configuration. |
| `GET_VERSION` | `sway_get_version` | No input; raw version object. |
| `GET_BINDING_MODES` | `sway_get_binding_modes` | No input; raw mode array. |
| `GET_CONFIG` | `sway_get_config` | No input; raw effective configuration. |
| `SEND_TICK` | `sway_send_tick` | Optional payload; raw tick reply. |
| `SYNC` | `sway_sync` | No input; raw compatibility failure object, as Sway documents for i3 compatibility. |
| `GET_BINDING_STATE` | `sway_get_binding_state` | No input; raw binding-state object. |
| `GET_INPUTS` | `sway_get_inputs` | No input; raw input-device array. |
| `GET_SEATS` | `sway_get_seats` | No input; raw seat array. |

`sway_subscribe` keeps a dedicated Sway IPC connection for its handle. `sway_next_event` waits for and returns the next decoded event from that handle, and `sway_unsubscribe` closes it. Together those three MCP tools expose every event documented for `SUBSCRIBE`:

| Event names |
| --- |
| `workspace`, `output`, `mode`, `window`, `barconfig_update`, `binding`, `shutdown`, `tick`, `bar_state_update`, `input` |

`wyoh_server_status` remains bridge lifecycle evidence, rather than an additional Sway feature. It reports the exact Sway/manual/SDK/protocol versions, child-process identity, full-IPC-development-mode flag, and active subscription count. The development-only `wyoh_stop_owned_child_for_test` helper exists solely to make the documented `shutdown` event observable; it is not a Sway feature or consumer capability.

## Development authority and isolation boundary

`sway_command` necessarily forwards broad authority: Sway commands can alter the compositor and can invoke programs through Sway configuration. Raw replies from `GET_TREE`, `GET_CONFIG`, and device queries can also include information that a consumer view would redact. Full coverage is therefore **not** a Mike, Mycroft, or future product capability.

The full mapping is available only when the SSH command explicitly starts `--full-ipc-development` mode. In that mode the bridge must:

- create and own a new disposable, headless Sway child with a test-only configuration;
- refuse a supplied `SWAYSOCK`, an existing socket path, or any attachment to a user session;
- send all IPC only to its child and stop that child when the MCP stream closes; and
- treat the authenticated SSH caller as a development authority. Captured raw replies must remain in ignored test results and never be committed.

This keeps the request faithful to the entire IPC protocol without pretending that full IPC is a safe desktop-control API. A later Wyoh consumer mediator remains a separate, least-authority product decision.

## Validation design

1. Pin the MCP Python SDK, MCP protocol version, Sway package version, and the matching shipped IPC-manual revision before installation. Do not code against an unpinned SDK or assumed IPC surface.
2. Add deterministic pytest tests under `test/wyoh/` using an injectable fake Sway transport. Assert discovery schemas and request-code mappings for every row in the coverage manifest, exact forwarding of `RUN_COMMAND`, raw-reply preservation, subscription-handle cleanup, and rejection of a live/user-session attachment before any Sway call.
3. Add a neighbouring Gherkin feature for the live SSH sequence: start full-development mode, MCP initialise, discover every tool, exercise a harmless command, enumerate representative state, subscribe, observe a triggered event, close the stream, and prove that the headless Sway child exits.
4. Build an event-coverage matrix. For each documented event, record an observed fixture trigger or a concrete explanation why the isolated headless fixture cannot produce it; unsupported-by-fixture is evidence, not a silently missing MCP feature. `shutdown` must be observed during orderly child teardown.
5. Add a `@pytest.mark.live` Python MCP client that launches `ssh -T luna-pi -- …` as its stdio child, captures its stderr separately, and writes complete client/server output plus JSON evidence to `results/wyoh/mcp-over-ssh/<timestamp>/`.
6. Run the client from this development environment after the protocol test passes. That is the honest meaning of “use it ourselves”: the agent invokes every class of MCP tool through a real MCP client, not by calling Sway IPC directly. Dynamic registration of the server as a callable tool in this chat host is a separate host-configuration decision and is not assumed.

No screenshot is required for this headless IPC contract. It must not be presented as visible-desktop, controller, or Luna graphics evidence.

## Acceptance criteria

- A client launched through the existing SSH identity completes MCP discovery and lists every named request, subscription, event-read, event-close, and bridge-status tool in the coverage manifest.
- Every documented Sway IPC request is mapped to the stated Sway message type and preserves its decoded raw reply; `RUN_COMMAND` is demonstrably forwarded only to the owned child.
- A subscription can observe the documented event protocol. The evidence matrix accounts for all ten documented event names, including orderly `shutdown`; no event is silently omitted because it is awkward to trigger headlessly.
- Deterministic tests and the live capture prove that a supplied/live `SWAYSOCK` is rejected and that client disconnect cleans up all subscription sockets and the child session.
- Closing the SSH/MCP stream stops the server and its dedicated headless Sway child; no port, service, or process remains resident.
- The result records exact SDK, protocol, Python, Sway, SSH, and Pi details and expressly makes no Luna compatibility claim.

## Deferred decisions

- Whether a future Mike-facing capability uses MCP at all.
- Any MCP exposure on Luna, any network/HTTP transport, any port-forward, and any persistent service.
- Host-level registration that would turn this server into a tool available to the current chat runtime.
- Any product-safe Wyoh action subset, consumer snapshot, or Mycroft context.
