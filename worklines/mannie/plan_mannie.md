---
**Status**: 📋 Draft
**Date**: 2026-10-11
**Priority**: Medium
**Maintained**: Yes
---

> **Renamed on 2026-10-11 (user decision, back to the original vocabulary).** From 2026-10-09 to 2026-10-11, the two lines had inverted names: this directory was `worklines/mike/`. The user restored the original split of the initial discussion (`worklines/professor/docs/0001_01_initial_discussion.md`, lines 2926 and 3006–3024): **Mike is the local brain on Luna, and Mannie is the frontier-model capability.** Professor swapped every name in this directory, its tests, and its code, including earlier time-log rows. Session names in old rows are the names at the time: the user kept both sessions and swapped their names (session [5832e9] is now `mike`, session [11ad42] is now `mannie`). User quotes from that period were reworded to fit the new names.

# Mannie — Claude on Luna (workline `mannie`)

## Overview

In the project's vocabulary (initial discussion, restored by the user on 2026-10-11), **Mike** is the local brain on Luna and **Mannie** is the frontier model (Claude, Codex, …) reached through APIs: the capable, costed escalation and the development capability.

The user's first request for this line (2026-10-11): **run Claude directly on Luna, with its whole harness.** In practice that means Claude Code, the agent with its tools and MCP, running on the R36 Ultra itself, not only on the desk host. If it runs, Luna gains a capable assistant that can use Wyoh's MCP server locally. It would then become the "Mannie" escalation behind Mycroft's dictation and Mike's local actions.

Done for the first stage means a measured answer on Luna:
- does Claude Code install and start there;
- what it costs in memory, CPU, storage and start time on a 1 GiB device;
- can it complete a simple task;
- can it reach Wyoh's MCP server;
- and what it costs to use.

## Workline directory layout

- Plan (this file): `worklines/mannie/plan_mannie.md`
- Produced docs: `worklines/mannie/docs/`
- Tests: `test/mannie/`; evidence under `results/mannie/<topic>/<timestamp>/`

## Goals ✅

- Find out whether Claude Code runs on Luna (aarch64, ArchR, glibc 2.40, 983 MiB RAM) and measure its footprint.
- Run a first useful session on Luna: a simple task, then Wyoh's MCP server as a local tool.
- Make Mannie's cost visible: tokens and money per request, latency, and the network dependency. This follows "TANSTAAFLLM": using Mannie is a deliberate escalation.
- Prepare the hand-offs: Mycroft's dictated text to Mannie, Mike's "too hard for me" to Mannie.

## Non-goals ❌

- No local model. That is Mike's line.
- No secret in the repository, the plan, the logs or the results. The API key or login lives only on Luna, outside Git, readable only by its owner.
- No unattended or auto-approve mode. Every action that changes the system stays subject to the user's approval, as Claude Code normally does. Professor's Omarchy analysis (`0601_01`) already rejected copying unattended agent authority.
- No change outside `/storage/.local/` and the user's home on Luna. No boot, card or ArchR change. Creating a Luna user account, if needed, belongs to the Luna workline.
- No Mycroft, Wyoh or Mike code. This line uses their interfaces and leaves notes.

## Key decisions / assumptions

- **Vocabulary** (user, 2026-10-11, D16): Mannie is the frontier model and the development capability, as in `AGENTS.md` and `docs/01_principles.md`; Mike is the local brain.
- **Luna facts** (from Mycroft's `0703_01` and Wyoh's records): ArchR, kernel 6.12.94 aarch64, 4 × Cortex-A35, 983 MiB RAM, glibc 2.40, 25 GB free on `/storage`. Sessions on Luna have run as root until now.
- **Luna is shared.** Access goes through Professor (`worklines/luna-access.md`): one session at a time, and a reboot after each test series.
- **User answers (2026-10-11):**
  - **Login:** the user's Claude **Pro subscription**, not an API key. Usage is flat-rate, so the cost record counts tokens, requests, latency and subscription-limit usage, not money per request.
  - **Spending cap:** none for now. These are small tests on a subscription.
  - **Account:** root on Luna for now. A normal user account on Luna is requested through Professor, who settles it with the Luna workline.
  - **Vocabulary (question 5):** passed to Professor; the user settles it with Professor.
  - **Test machine:** `luna-pi` is reserved for Mannie's tests. Steps 1 and 2 run there. Luna is reserved for Mycroft and Wyoh for now.
- **luna-pi facts** (`worklines/luna/docs/0101_01_luna-pi-quick-check.md`): Raspberry Pi 4, Debian 13 (trixie) arm64, about 8 GiB RAM, 2 GiB zram swap, 13.9 GiB root filesystem. SSH alias `luna-pi`, user `michael` (not root). Its memory proves nothing about a 1 GiB device; the figures there are a reference for Luna, not evidence of fit.
- *To verify, not assumed:* that Claude Code has a Linux arm64 build that runs on Luna's glibc 2.40 and on Debian trixie; its RSS; whether it needs Node.js; how a subscription login works without a browser on the device.

## Risks / constraints

- **Memory.** Sway, the Slate and the gamepad daemon leave about 535–795 MiB available. Mycroft's provider takes about 250 MiB. Claude Code and Mycroft running together may not fit. **Mitigation:** measure Claude Code alone first, then with Mycroft resident.
- **Network.** Luna is on 2.4 GHz Wi-Fi, which has had stalls. **Mitigation:** record latency and failures. A failed request must say so clearly, never fake a result.
- **Cost.** Every request costs tokens, and subscription usage limits. **Mitigation:** log usage per session, and show it to the user.
- **Credentials on a shared, rooted handheld.** **Mitigation:** file mode 600, outside Git and `results/`. The workline documents never record the subscription token.
- **Authority.** An agent with shell tools on the device could break the session. **Mitigation:** normal permission prompts, work inside a dedicated directory, and the first tests read only.

## 🚦 Green light protocol

- Default: planning and documentation only, until the user explicitly says **"🟩 go Step N"**.
- `luna-pi` is Mannie's own test machine (user, 2026-10-11). Luna access through Professor (`worklines/luna-access.md`), and the `cell-coordination` skill for every exchange with other lines.
- If scope changes materially, update this plan before proceeding, and add an entry to `docs/LOGBOOK.md`.

## Plan steps (no execution until green light)

### Step 0 — Workline set-up
**Status**: ✅ Done (2026-10-11, Professor, documentation only)
- [x] 0.1 Plan created from the user's request ("put Claude directly on Luna, with all its harness"). The user starts the Mannie session.

### Step 1 — Desk research (no device)
**Status**: 🧪 In progress (🟩 go Step 1–2, user, 2026-10-11 13:40)
- [x] 1.1 Claude Code on Linux arm64: which install method (native binary or npm), runtime requirements (glibc version, Node.js or not), and disk size. Use official documentation only, with sources.
- [x] 1.2 Subscription (Pro) login without a browser on the device: the supported headless login flow, and where the credential is stored.
- [x] 1.3 Expected memory footprint, from documentation; measured for real on `luna-pi` in Step 2.
- [x] 1.4 Write the intent `docs/0101_01_mannie-on-luna-intent.md`: what will be installed and where (first `luna-pi`, later Luna), what is measured, which tests run (Gherkin + pytest, live marker), the cost record, and the stop conditions.
- **Results** (`docs/0101_01`): native binary, no Node.js, needs glibc ≥ 2.26, ≈232 MiB on disk, GPG-verified (2.1.287). Login: `/login` over SSH, done by the user. Documented minimum is **4 GB RAM**, and the installer needs ~512 MiB free; Luna has 983 MiB.
- **Acceptance:** the user approves the intent. ⏳ open.

### Step 2 — Install and first start on `luna-pi`
**Status**: ✅ Done on `luna-pi` (2.4 on Luna open)
- [x] 2.1 On `luna-pi` (Mannie's machine, user `michael`): install Claude Code in the user's home, and record the version and checksums.
- [x] 2.2 Log in with the Pro subscription, without the credential ever reaching the repository or the logs. The user ran `claude auth login` over SSH; the credential file has mode 600 and was never read.
- [x] 2.3 First start, and `--version` / help. Record start time, peak RSS and CPU time.
- [ ] 2.4 Later, when Luna is free and Professor gives a slot: repeat 2.1–2.3 on Luna under `/storage/.local/` (or the user account, if the Luna workline creates one), then reboot Luna.
- **Figures so far** (`results/mannie/luna-pi-claude/20261011T114535Z/`, version 2.1.287, before login): install 47 s, peak 199 MiB; 232 MiB on disk; `--version` 0.03 s, 38 MiB; `--help` 0.46 s, ~139 MiB; interactive first screen after 0.95 s, peak ~190 MiB RSS (PSS ~188 MiB), settled ~181 MiB, one process. `claude doctor`: native install, ripgrep bundled, auto-updates disabled. Run with `MANNIE_LUNA_PI_LIVE=1 uv run pytest -m live test/mannie`.
- **After login** (`20261011T185853Z/`): logged-in interactive idle ~186–195 MiB RSS; one `-p` "pong" request 5.2 s wall, 4.5 s CPU, peak 244 MiB, ~17,700 input tokens (mostly cache), default model Opus 5.5, $0.077 list-price equivalent (not billed on Pro). Result: [`docs/0203_01`](docs/0203_01_luna-pi-claude-result.md).
- **Acceptance:** Claude Code starts on `luna-pi`, or the blocking reason is measured and recorded. ✅ met on `luna-pi`. 2.4 stays open until Luna is available.

### Step 3 — First session on Luna
**Status**: ⏳ Pending
- [ ] 3.1 A read-only task, for example: describe `/storage/.local/` and the running Wyoh services. Record tokens, cost, latency and peak RSS.
- [ ] 3.2 A small task that changes a file, inside a scratch directory, with the normal permission prompt answered by the user.
- [ ] 3.3 Behaviour on a Wi-Fi stall: the failure must be clear and recoverable.
- **Acceptance:** a result document with the figures, and the user's opinion of the session.

### Step 4 — Wyoh's MCP server as a local tool
**Status**: ⏳ Pending
- [ ] 4.1 Declare Wyoh's MCP server to Claude Code on Luna, configured locally and not committed with any secret.
- [ ] 4.2 Ask for one desktop action (open the calculator, list windows), with the user's approval. Inspect a screenshot.
- [ ] 4.3 Measure Claude Code alongside Wyoh's session, and alongside a resident Mycroft provider if Mycroft has one.
- **Acceptance:** one Wyoh action done through Claude on Luna, with the cost recorded.

### Step 5 — Hand-offs (design only)
**Status**: ⏳ Pending
- [ ] 5.1 Note to Mycroft: how dictated text reaches Mannie (it is the "Mannie/Mike: direct dictation" input mode in Mycroft's plan).
- [ ] 5.2 Note to Mike: the escalation contract (Mike's Step 6.3): what triggers it, and what the user sees and pays.
- **Acceptance:** notes left in the receiving lines' `docs/`.

---

## Progress tracking ✅

- ✅ Step 0 — Workline set-up
- 🧪 Step 1 — Desk research
- ✅ Step 2 — Install and first start on `luna-pi` (Luna later)
- ⏳ Step 3 — First session on Luna
- ⏳ Step 4 — Wyoh's MCP server as a local tool
- ⏳ Step 5 — Hand-offs

---

## Time tracking (use `date`) ⏱️

```bash
date
```

### Time log

| Timestamp (`date`) | Update |
|---|---|
| 2026-10-11 13:20 | Workline created by Professor at the user's request: "put Claude directly on Luna, with all its harness" (then named Mike = large remote model, D1; renamed Mannie by D16). Documentation only; no device access. |
| 2026-10-11 13:29 | Mannie session started (`mike` [11ad42], the name at the time), registered in `worklines/agents.md`. Plan, project principles and coordination rules read; questions put to the user. No work started, waiting for a green light. |
| 2026-10-11 13:40 | User answers recorded: Pro subscription login, no spending cap, root on Luna for now. `luna-pi` is reserved for Mannie; Steps 1–2 run there, and Luna stays with Mycroft and Wyoh. Step 2 retargeted to `luna-pi`, with Luna as 2.4. Two requests sent to Professor: a normal user account on Luna (to settle with the Luna workline), and the Mannie/Mike vocabulary in `AGENTS.md` and `docs/01_principles.md`. Still waiting for 🟩 go Step 1. |
| 2026-10-11 13:40 | 🟩 go Step 1–2 (user). Step 1 started. |
| 2026-10-11 13:42 | Step 1 research done; intent `docs/0101_01` written, awaiting approval. Key finding: the documented minimum is 4 GB RAM, Luna has 983 MiB. Step 2 started on `luna-pi` (tests, install, measurements before login). |
| 2026-10-11 13:48 | 2.1 and 2.3 done on `luna-pi`: 2.1.287 installed (GPG-verified, checksum matched, auto-update off), 4 live tests pass. An earlier run (`20261011T114409Z`) failed on a missing `chmod +x`, fixed in the test. Idle interactive start about 190 MiB. Blocked on 2.2: the user's login. |
| 2026-10-11 20:58 | Professor: pause (usage limit at 99%), then "pause over": resume within the green lights (`luna-pi` only, no Luna slot), and rename nothing while the user reconsiders the Mannie/Mike naming. State unchanged: still waiting for the user's login (2.2). |
| 2026-10-11 20:59 | The user had logged in. 2.2 done: logged-in start and one request measured (2 live tests pass). Step 2 done on `luna-pi`; result `docs/0203_01`. Open: approval of the intent, 2.4 (Luna slot), and the proposed 600 MiB rehearsal (needs a green light). Stopped. |

---

## Workline artifacts

- `worklines/mannie/plan_mannie.md` — this plan.
- `test/mannie/luna_pi_claude.feature`, `test/mannie/test_luna_pi_claude.py`, `test/mannie/claude_probe.py` — Step 2 live harness (`MANNIE_LUNA_PI_LIVE=1`).
- [`docs/0101_01_mannie-on-luna-intent.md`](docs/0101_01_mannie-on-luna-intent.md) — Step 1 research and the intent for Step 2: install, login, measurements, stop conditions.
- [`docs/0203_01_luna-pi-claude-result.md`](docs/0203_01_luna-pi-claude-result.md) — Step 2 result on `luna-pi`: memory, time, tokens, and what they mean for Luna.
- Related: `worklines/professor/docs/0503_01_delegated-coordination-log-2026-10-09.md` (D1, the vocabulary), `worklines/mike/plan_mike.md` (Step 6.3, escalation to Mannie), `worklines/mycroft/plan_mycroft.md` (input modes), `worklines/luna-access.md` (Luna slots).
