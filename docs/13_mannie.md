# 13 · Mannie, the frontier model

> In the novel, Mannie is the technician who works with Mike and gets his hands on the machines. Here, Mannie is the big model far away (Claude, Codex) that does the real work when it is worth paying for.

## In one sentence

Mannie is a frontier model reached through the network. It is the development capability (code, build, test), and the costed escalation behind Mike. The current line runs Claude Code, with its whole harness, on the handheld itself.

## Where it lives

| Piece | Where |
|---|---|
| Claude Code 2.1.287, `linux-arm64`, signature and checksum checked, auto-update off | `luna-pi` today (`~/.local/share/claude/`); Luna later, under `/storage/.local/` |
| Install and measurement probes, Gherkin scenario | `test/mannie/` (live only, run explicitly) |
| Login | the user's own; the credential file stays on the device, mode 600, never read by a test or committed |

## How it talks to the others

- **The Tunnel:** an API over the network. Every call has a price in tokens, and in usage on the user's subscription.
- **From Mike (planned):** when Mike answers "too hard", the request can go to Mannie, after the cost is shown.
- **To Wyoh (planned):** Claude Code can use Wyoh's MCP server as a local tool, so the big model can act on Luna's desktop within the same accept-first rule.
- **Never unattended.** It runs with Claude Code's normal permission prompts, and never in an auto-approve mode.

## What it costs (`luna-pi`, Raspberry Pi 4)

| Measurement | Result |
|---|---|
| Install | 47 s; 232 MiB on disk |
| Idle session, logged in | ≈ 186–195 MiB |
| One one-word request ("pong") | 5.2 s wall (1.3 s in the API), 4.5 s of local CPU, **peak 244 MiB** |
| Tokens for that request | ≈ 17,700 input, almost all of it Claude Code's own prompt and tools; caching makes repeats cheaper |

Anthropic documents **4 GB of RAM** as the minimum. Luna has 983 MiB, so running there is outside what is supported, and the results must be read that way. Luna's slower cores will add several seconds of local CPU to every request.

## Why it is like this

- **No free LLM.** Even "pong" costs about 17,700 tokens of harness. That is the project's thesis in one number. Mannie is used when it is worth that price, not by default.
- **Measured on `luna-pi` first.** It has the same arm64 code as Luna but plenty of RAM, so it shows the real footprint without risking the handheld.
- **Pinned version.** With auto-update off, later figures stay comparable.

## Status and limits

- **Done:** install, login and a first request on `luna-pi`.
- **Next, and waiting for the user:**
  - approval of the intent;
  - a rehearsal under a 600 MiB memory limit on the Pi;
  - then a Luna slot.
- **The memory question:** Mannie, Mycroft and Mike together do not fit in Luna's ≈ 795 MiB unless lighter models are used. See [Architecture § 3](04_architecture.md#3-pressure-where-the-memory-goes).

**Sources:** `worklines/mannie/plan_mannie.md`; intent `0101_01`; result `0203_01`.
