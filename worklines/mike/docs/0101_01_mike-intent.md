# Mike v0 intent

**Question answered:** what does Mike v0 do, as the user sees it, before any implementation starts?<br>
**Date:** 2026-10-09<br>
**Status:** reviewed by the user on 2026-10-09: agreed, with Adam removed. No step is green-lit.

## The target (not v0)

```text
user ──voice──► Mycroft ──accepted text──► Mike ──MCP──► Wyoh ──► Luna's desktop
                                             │                │
                                             ◄──── result ────┘
                                             └──► user: what was done, proposed, refused
```

The user speaks to Mycroft, accepts the text, and Mycroft passes it to Mike. Mike is a small local model on Luna. It picks one Wyoh action, shows it, and runs it through the Wyoh MCP server. Requests that are too hard for Mike go to Mannie, the large remote model, as a visible escalation (later, not in this workline's first steps).

**No Adam.** The user does not place Adam in this picture for now (2026-10-09). Mike shows its results to the user directly. Adam appears nowhere in Mike's design until the user brings it back.

## What v0 is

v0 is a **foreground text console on the desk host**, `mike-console`, the counterpart of Mycroft's text console:

1. The user types a short French request, for example `ouvre la calculatrice` or `mets le navigateur à gauche`. (Later, Mycroft's accepted text arrives here instead of typed text.)
2. Mike sends the request and a short tool list to the local model, with constrained decoding so the answer can only be one well-formed call from that list, or `none`.
3. The console shows the **proposed action** in plain words and as the call itself, with the model name and the time taken.
4. The user accepts (`Enter`) or refuses (`Esc`). Nothing runs before acceptance.
5. On acceptance, Mike's adapter turns the call into Wyoh MCP requests and shows Wyoh's answer: done, refused, or failed.

The MCP back end is either a **fake Wyoh** in the tests, or the real Wyoh MCP server on `luna-pi` over SSH. Luna itself is out of scope for v0.

## The curated tool list

The model never sees the raw Wyoh tool list. It sees a few task-level tools, and Mike's adapter maps each to Wyoh MCP calls. The adapter, not the model, writes any Sway command, from a fixed template with checked arguments.

| Tool for the model | Arguments | Adapter does | Risk |
| --- | --- | --- | --- |
| `list_windows` | — | `sway_get_tree`, summarised to app names and focus | read-only |
| `focus_window` | `app` (one of the open apps) | `sway_command` `[app_id=…] focus` | low |
| `launch_app` | `app` (one of an allowlist) | allowlisted launch command only | low; allowlist only |
| `close_window` | `app` | `[app_id=…] kill` | asks again |
| `move_window` | `app`, `place` (`left`, `right`, `top`, `bottom`, `full`) | layout commands from a template | low |
| `type_text` | `text` | `wyoh_dev_keyboard_type` | development-only tool |
| `none` | `reason` | nothing; shows the reason | — |

Rules:

- **No raw `sway_command`, no `exec` of free text.** In Sway, `exec` runs any shell command; giving it to a model would be an arbitrary shell disguised as conversation.
- One call per request in v0. No chained, multi-step agent loop.
- If the model's argument is not one of the allowed values (an app that is not open or not on the allowlist), the adapter refuses and says why. It does not guess.

The exact list is fixed in Step 1. Whether Wyoh should one day expose such task-level tools itself is Wyoh's decision; Mike will ask with a note, not by changing Wyoh.

## What the user sees

| State | Shown |
| --- | --- |
| waiting | prompt, model name, back end (`fake` or `luna-pi`) |
| thinking | elapsed time |
| proposed | the action in words + the call; `Enter` accept, `Esc` refuse |
| none | "Mike cannot do this", with the model's reason; later: "ask Mannie?" |
| done / refused / failed | Wyoh's answer, never a fabricated success |

## Out of scope for v0

- Running on Luna, or any Luna audio or display work.
- Mycroft integration (the hand-off is designed now, connected in a later green-lit step).
- Mannie (remote model) escalation.
- Fine-tuning; a resident background service; speech output.
- Changing the Wyoh MCP server.
