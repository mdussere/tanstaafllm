# Result — development-only full Sway IPC MCP validation over SSH

> **Freshness:** 🟡 historical · **Written:** 2026-09-28 · **Checked:** 2026-10-31 · **Step:** wyoh 3.5 ✅

**Step:** Wyoh 3.5
**Status:** passed on 2026-09-28
**Scope:** an isolated `luna-pi` headless Sway child. This is neither a Luna compatibility result nor a product/consumer API.

## Result

The development host used a real Python MCP client over SSH-carried stdio to discover and exercise the complete documented Sway 1.10 IPC request surface on `luna-pi`. The bridge exposed all fifteen documented request types and accepts all ten documented subscription event names. It never listened on a network port and rejected ambient `SWAYSOCK`/`I3SOCK` before starting a child or opening an IPC connection.

The final live test passed in 5.13 seconds:

```text
test/wyoh/test_mcp_over_ssh.py::test_luna_pi_full_sway_ipc_mcp_over_ssh PASSED
```

The full ignored evidence is `results/wyoh/mcp-over-ssh/20260928T063829Z/`; the invocation log is `logs/wyoh/mcp_over_ssh_final_decoder_20260928_083828.log`.

## Versions and topology

| Item | Validated value |
| --- | --- |
| Development host | Python 3.12.4; `mcp==2.2.0` |
| `luna-pi` bridge environment | Python 3.13.5; isolated user venv `/home/michael/.local/opt/wyoh-mcp-2.2.0`; `mcp==2.2.0` |
| MCP protocol baseline | 2026-07-28 |
| Sway | pinned 1.10.1 proof prefix |
| Sway IPC reference | [Sway 1.10 IPC manual](https://github.com/swaywm/sway/blob/1.10/sway/sway-ipc.7.scd) |
| Transport | `MCP client → stdin/stdout → ssh -T luna-pi → stdin/stdout → MCP server` |

At validation time, the bridge was at `worklines/wyoh/scripts/wyoh_mcp_server.py`; it now lives at `src/wyoh/wyoh_mcp_server.py`. The validated ephemeral mode starts only with `--full-ipc-development`, removes inherited socket variables for its child, refuses `SWAYSOCK` or `I3SOCK`, discovers only its child socket, and stops it in `finally`.

The remote MCP dependency is a deliberately isolated development venv because the Pi’s system Python is externally managed. No system package, SSH configuration, listener, or service was installed.

## IPC request coverage

Each documented request is a named MCP tool and deterministic tests assert its exact numeric IPC mapping: `RUN_COMMAND`, `GET_WORKSPACES`, `SUBSCRIBE`, `GET_OUTPUTS`, `GET_TREE`, `GET_MARKS`, `GET_BAR_CONFIG`, `GET_VERSION`, `GET_BINDING_MODES`, `GET_CONFIG`, `SEND_TICK`, `SYNC`, `GET_BINDING_STATE`, `GET_INPUTS`, and `GET_SEATS`.

The live client called state queries, the harmless owned-child workspace command, tick, `SYNC`, input/seat queries, subscriptions, event reads, unsubscribe, and lifecycle status. MCP SDK result decoding preserves each Sway JSON reply without converting it into a product semantic model. `SYNC` correctly has no input and returns Sway’s documented i3-compatibility failure object.

The three subscription tools are `sway_subscribe`, `sway_next_event`, and `sway_unsubscribe`. A bounded no-event read returns a structured timeout result rather than a tool failure. `wyoh_server_status` is lifecycle evidence, not Sway IPC. `wyoh_stop_owned_child_for_test` is an explicitly development-only lifecycle helper used solely to produce the documented `shutdown` event; it must not be considered a product feature.

## Event coverage matrix

All ten event names are accepted and mapped through the subscription tools. “Untriggerable” below means that the bare owned headless fixture contains no honest producer for that event; it does not mean Sway lacks the event.

| Event | Result in final fixture | Reason / trigger |
| --- | --- | --- |
| `workspace` | Observed | `workspace wyoh-proof` generated the focus event. |
| `tick` | Observed | `sway_send_tick` delivered an event. |
| `shutdown` | Observed | The test-only owned-child lifecycle helper terminated the child cleanly. |
| `output` | Untriggerable | No hotplug, output reconfiguration, or additional output producer in the fixed headless fixture. |
| `mode` | Untriggerable | No input/binding-mode transition is produced by the fixture. |
| `window` | Untriggerable here; observed in Step 3.6 | This fixture deliberately launches no Wayland/Xwayland client. The Step 3.6 shared session observed a `window` `new` event for an MCP-launched `lxterminal` ([0306_03](0306_03_shared-sway-wayvnc-result.md)). |
| `barconfig_update` | Untriggerable | The fixture has no bar or bar-configuration mutation. |
| `binding` | Untriggerable | There is no physical or virtual input sequence/binding execution. |
| `bar_state_update` | Untriggerable | There is no bar state/input-mode producer. |
| `input` | Untriggerable | There is no input hotplug or virtual input device. |

This establishes protocol reachability and complete mapping, not a claim that those seven behaviours have been functionally exercised on Luna. `window` has since been observed on `luna-pi` in Step 3.6; the other six remain unexercised.

## Verification

| Check | Result |
| --- | --- |
| Deterministic mapping, discovery, timeout, subscription, and ambient-socket rejection tests | `7 passed` |
| Default MCP-over-SSH test without external opt-in | skipped as required by `@pytest.mark.live` |
| SSH-carried live MCP client | `1 passed in 5.13s` |
| Owned child lifecycle | Server stderr records start and stop; `shutdown` event observed; final status reports stopped and zero subscriptions. |
| Listener/service | None used or installed; stdio ends with the SSH/MCP client. |

The matching Gherkin contract is `test/wyoh/mcp_over_ssh.feature`. The deterministic implementation tests are `test/wyoh/test_wyoh_mcp_server.py`, and the actual client proof is `test/wyoh/test_mcp_over_ssh.py`.

## Boundaries retained

- Full Sway IPC, raw tree/config/device replies, and arbitrary Sway commands remain development authority only. They are not exposed to Mike, Mycroft, or a future Wyoh consumer contract.
- This result does not attach to the existing VNC/Labwc session. VNC activity cannot make this separate owned Sway child more representative, and no rendered UI/screenshot claim is made.
- This result is evidence about the Pi reference environment and the protocol bridge only. It makes no claim about Luna’s stock compositor, graphics, input, memory budget, controller behaviour, or production suitability.
- Registering this bridge as a tool available to the current chat host is deliberately deferred; it is a host-configuration and authority decision, not evidence of IPC correctness.
