# Proposal — development-only Wyoh MCP bridge over SSH

**Status:** prepared only; no dependency, server, SSH configuration, or `luna-pi` state has been changed.

## Question answered

How can a development host exercise a small, safe subset of Wyoh's existing Sway IPC proof through a Python Model Context Protocol (MCP) server on `luna-pi`?

## Proposed topology

```text
development-host MCP client
        │ stdin / stdout
        ▼
ssh -T luna-pi -- python3 <versioned Wyoh MCP entry point>
        │ stdin / stdout carried inside the authenticated SSH session
        ▼
development-only Python MCP server on luna-pi
        │ direct Unix-domain Sway IPC, limited by server-side policy
        ▼
dedicated headless Sway 1.10.1 child session
```

This is **MCP over stdio carried by SSH**, rather than a TCP port-forward. It creates no listener on `luna-pi`, keeps authentication and host trust in the existing SSH configuration, and terminates the server when the client closes its stream. The [official Python SDK](https://github.com/modelcontextprotocol/python-sdk) supports stdio servers and clients; its [stdio guidance](https://py.sdk.modelcontextprotocol.io/latest/run/) treats stdout as protocol-only and directs logs to stderr.

The Sway session is a disposable headless child, using the same pinned `luna-pi` proof prefix and lifecycle as `test/wyoh/sway_ipc_probe.py`. The bridge must never attach to a user desktop or the real Luna stock image.

## Proposed v0 tool surface

| MCP tool | Input | Result | Authority |
| --- | --- | --- | --- |
| `wyoh_snapshot` | none | schema version, monotonic revision, output/workspace summary, focused workspace, seat/input counts, freshness | read-only |
| `wyoh_focus_proof_workspace` | exact expected revision and the fixed name `wyoh-proof` | operation result, matching workspace-focus event, post-operation revision | only the fixed `workspace wyoh-proof` Sway command |
| `wyoh_server_status` | none | pinned Sway/SDK version, session state, policy version, process lifecycle state | read-only |

The snapshot must exclude raw Sway tree data, application/window titles, `app_id`, environment variables, filesystem paths, and arbitrary visible text. There is no generic `command`, shell, selector, raw-socket, subscription, resource, or prompt capability. A stale revision, missing session, unauthorised method, malformed input, or client disconnect must have no Sway side effect.

## Validation design

1. Pin the MCP Python SDK and MCP protocol version in the implementation record before installation. Do not code against an unpinned SDK surface.
2. Add deterministic pytest tests under `test/wyoh/` using an injectable fake Sway transport. Prove the advertised tool schemas and that every rejection makes zero Sway calls.
3. Add a neighbouring Gherkin feature for the live SSH sequence: start server, MCP initialise, list tools, take snapshot, focus `wyoh-proof`, observe the matching event/post-state, close stream, and prove that the headless Sway child exits.
4. Add a `@pytest.mark.live` Python MCP client that launches `ssh -T luna-pi -- …` as its stdio child, captures its stderr separately, and writes complete client/server output plus JSON evidence to `results/wyoh/mcp-over-ssh/<timestamp>/`.
5. Run the client from this development environment after the protocol test passes. That is the honest meaning of “use it ourselves”: the agent invokes the MCP tools through a real MCP client, not by calling Sway IPC directly. Dynamic registration of the server as a callable tool in this chat host is a separate host-configuration decision and is not assumed.

No screenshot is required for this headless IPC contract. It must not be presented as visible-desktop, controller, or Luna graphics evidence.

## Acceptance criteria

- A client launched through the existing SSH identity completes MCP discovery and lists exactly the three advertised tools.
- `wyoh_snapshot` returns only the redacted schema and an explicit revision/freshness value.
- The fixed focus tool proves its result through an observed Sway workspace-focus event and a post-operation snapshot; no fixed completion sleep is used.
- Deterministic rejection tests and the live client capture show that no unsupported request can issue a Sway command.
- Closing the SSH/MCP stream stops the server and its dedicated headless Sway child; no port, service, or process remains resident.
- The result records exact SDK, protocol, Python, Sway, SSH, and Pi details and expressly makes no Luna compatibility claim.

## Deferred decisions

- Whether a future Mike-facing capability uses MCP at all.
- Any MCP exposure on Luna, any network/HTTP transport, any port-forward, and any persistent service.
- Host-level registration that would turn this server into a tool available to the current chat runtime.
- Broader Wyoh actions, live subscriptions, client semantics, or Mycroft context.
