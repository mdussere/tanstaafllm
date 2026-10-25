# Can the cell keep talking when Mannie is on Luna? Remote Control and cross-session messages

**Step:** 6.6 and 6.8 of `plan_mannie.md`. **Date:** 2026-10-25. **Author:** Mannie (session tanstfaafllm-d3).
**Question (user, 2026-10-25):** once Mannie runs on Luna, can it still use `SendMessage` with the desk sessions, and what does Anthropic's Remote Control offer, before choosing between messages and GitHub issues?
**Sources:** Anthropic's documentation only, read on 2026-10-25: [Message your other Claude Code sessions](https://code.claude.com/docs/en/cross-session-messaging) and [Remote Control](https://code.claude.com/docs/en/remote-control). Nothing below has been tested yet.

## Short answer

Yes, it can, under one condition: **both sessions must be connected to Remote Control.** Messages between two machines then travel through Anthropic's servers. Today's desk sessions are not connected, which is why `ListAgents` shows only this machine's sessions.

## Remote Control in brief

- **What it is:** a Claude Code session that keeps running on its own machine, which you can also drive from claude.ai/code, the Claude app on a phone, or another browser. Files, tools and MCP servers stay on that machine.
- **Plans:** Pro, Max, Team and Enterprise. Not with an API key. The user's Pro subscription qualifies.
- **Three ways to start it:**
  - `claude remote-control` (server mode): waits for connections and can open several sessions;
  - `claude --remote-control` (or `--rc`): a normal interactive session that is also reachable from elsewhere;
  - `/remote-control` (or `/rc`) inside a session that is already running, including in the VS Code extension.
  - `remoteControlAtStartup: true` in `~/.claude/settings.json` connects every interactive session automatically.
- **Network:** outbound HTTPS only, and no port is opened on the machine. If the network drops, an interactive session keeps working and reconnects by itself. Server mode gives up after about 10 minutes.
- **What must stay alive:** the `claude` process. If it stops, the session goes offline. On a machine reached over SSH, the docs advise running it inside `tmux` or `screen`.
- **Privacy:** while it is connected, the transcript (messages, answers and tool activity) is stored on Anthropic's servers. Execution stays local.
- **Security:** the existing permission prompts are forwarded to the phone or browser and wait for an answer. "Trusted devices" (beta, Pro included) can require an enrolled device and a sign-in less than 18 hours old.
- **Remote limits:** some commands work only in the local terminal (`/plugin`, `/resume`). Other prompts expire after 5 minutes (`dialogExpiry`).

## Messages between sessions on different machines

| Situation | What happens |
|---|---|
| Both sessions connected to Remote Control | `ListAgents` shows the other machine's session, labelled `Remote Control`. `SendMessage` works both ways, through Anthropic's servers. |
| The target is `offline` (its connection dropped) | The message goes through, but arrives only when that machine reconnects. |
| The sender is not connected | The message goes through without a reply address, so the receiver cannot answer. |
| Cloud session | It can receive, but cannot answer with `SendMessage`. |
| Same machine | A local socket, never through Anthropic's servers (today's case on the desk). |

- **Versions:** v2.1.224 or later for messaging, and v2.1.225 or later to start a conversation with another machine. Luna has 2.1.287, which is enough. The pinned version (`DISABLE_AUTOUPDATER`) does not block Remote Control; only `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` or `DISABLE_GROWTHBOOK` would.
- **Controls:** `crossSessionInbound` (`accept`, `hold` or `refuse`) chooses what happens to incoming messages. `isolatePeerMachines: true` asks the user to approve every message before it leaves the machine.
- **What stays true:** a message never counts as the user's approval, cannot change configuration, and does not run commands. The receiving session's own permission prompts still apply. A delivered message counts toward usage like a typed prompt.

## What this means for the cell

| | Remote Control and `SendMessage` | Git and GitHub issues |
|---|---|---|
| Speed | Immediate, while both sessions are alive | When a session next reads its issues |
| Record | Ephemeral (the transcript at Anthropic, not in the repository) | Durable, visible to the user, in GitHub |
| Needs | A `claude` process kept alive on Luna (about 180 MiB, out of the 629 MiB available with Kroko resident) and on the desk | Nothing resident; `gh` and a token |
| Network outage | Queued until reconnection | Pull or push when the network is back |
| Cost | Each message is a prompt for the receiver | One `gh` call; reading is ordinary work |

**Mannie's view, before any test:** the two are complementary.
- `SendMessage` over Remote Control stays the cell's **live channel**, unchanged from today: Professor coordinates, and the others write only to Professor.
- **Git remains the record**: every request still goes into the receiving plan, as `cell-coordination` requires.
- **Issues** are useful mainly as the **mailbox when no session is running**, and for anything the user should follow in GitHub. They need not be the main channel.

The memory cost of a Claude Code process kept alive on Luna is the real constraint, and it must be measured.

## Proposed tests (Step 6.8, to be green-lit)

1. On the desk, run `/remote-control` in Professor's session and in a test session; `ListAgents` on each side.
2. On Luna, as `michael`, start `claude --remote-control` in `tmux`. Check that it appears on the desk as `Remote Control`, then exchange a message both ways.
3. Cut Luna's Wi-Fi for 2 minutes: queued message, reconnection.
4. Measure Luna's memory with a connected idle session, alongside Kroko.
5. Drive the Luna session from the phone, approve a permission prompt from there, and check that it is not bypassed.
