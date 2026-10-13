# Claude Code on luna-pi — Step 2 result

**Status:** done for `luna-pi`; Luna (2.4) waits for a slot<br>
**Date:** 2026-10-11<br>
**Question answered:** Does Claude Code install, log in and start on an arm64 board, and what does it cost in memory, time and tokens?

**Short answer:** yes. On `luna-pi`, Claude Code 2.1.287 installs in 47 s and idles at about 190 MiB. A one-word request peaks at about 244 MiB and costs about 17,700 input tokens, almost all of them Claude Code's own system prompt and tools. These are arm64 reference figures from an 8 GiB board, not evidence that Claude Code fits on Luna.

## Set-up

- `luna-pi`: Raspberry Pi 4, Debian 13 trixie (glibc 2.41), aarch64, 7.6 GiB RAM, user `michael`.
- Claude Code **2.1.287** (stable), `linux-arm64`. The manifest's GPG signature was checked, and the binary matched the manifest's SHA-256 both on the desk and on the Pi (`e4daf793…3b03`). It is installed in `~/.local/share/claude/versions/`, and auto-update is off (`DISABLE_AUTOUPDATER=1`, confirmed by `claude doctor`).
- Login: the user ran `claude auth login` (Pro subscription) in their own SSH terminal. The credential file is `~/.claude/.credentials.json`, mode `0600`. No test read it.
- Harness: `test/mannie/luna_pi_claude.feature`, `test/mannie/test_luna_pi_claude.py`, `test/mannie/claude_probe.py`. Run with `MANNIE_LUNA_PI_LIVE=1 uv run pytest -m live test/mannie`.

## Figures

| Measurement | Result | Evidence |
|---|---|---|
| Install (`claude install 2.1.287`) | 47.1 s wall, peak 199 MiB RSS | `20261011T114535Z/install.json` |
| Disk | 232 MiB binary; `~/.claude` 20 KiB before login | `…/installed.txt` |
| `claude --version` (×3) | 0.03 s, 38 MiB | `…/start-summary.json` |
| `claude --help` (×3) | 0.46 s, 137–140 MiB | `…/start-summary.json` |
| Interactive start, not logged in (20 s idle) | first output 0.95 s; peak 190 MiB RSS / 188 MiB PSS; settled 181 MiB RSS; one process | `…/interactive-summary.json` |
| Interactive start, logged in (20 s idle) | first output 1.32 s; peak 195 MiB RSS / 141 MiB PSS; settled 186 MiB RSS / 132 MiB PSS; one process | `20261011T185853Z/interactive-summary.json` |
| One request: `claude -p "Reply with the single word: pong"` | 5.2 s wall (API 1.3 s), 4.5 s CPU, **peak 244 MiB RSS** | `20261011T185853Z/request-summary.json` |
| Tokens for that request | 2 input + 9,345 cache-write + 8,368 cache-read input, 4 output. Model: **Opus 5.5** (the default). | same |
| List-price equivalent | $0.077. On the Pro subscription this is not billed; it counts towards the usage limit. | same |

## What this means for Luna

- **Memory.** An idle session uses about 186–195 MiB RSS, and a single request peaks at about 244 MiB. Luna leaves about 535–795 MiB available under Sway, and Mycroft's provider takes about 250 MiB. Claude Code alone would probably fit. Alongside Mycroft, the margin is thin. Real tool use (file reads, shell, MCP) was not measured and will push the peak higher. Anthropic's documented minimum is 4 GB, so Luna is outside what Anthropic supports.
- **CPU.** One trivial request needed 4.5 s of CPU on the Pi 4's Cortex-A72 cores. Luna's Cortex-A35 cores are slower, so expect several seconds of local CPU per request on Luna, on top of the network time.
- **Tokens.** Even a one-word reply carries about 17,700 input tokens of harness context. Prompt caching makes repeats cheaper, but it is still the price of the full harness on every request. This is the TANSTAAFLLM cost of "Claude with all its harness". Options to weigh later: a smaller default model (Sonnet or Haiku), fewer tools, or calling the API directly from Mike for escalations.
- **The fixed version is pinned.** Auto-update is off, so later figures are comparable.

## Open

- 2.4: repeat on Luna under `/storage/.local/` when Luna is free and Professor gives a slot.
- Proposal (needs a green light): rehearse under a ~600 MiB memory limit on the Pi before taking a Luna slot.
- The user's verdict on the intent (`0101_01`) is still open.
