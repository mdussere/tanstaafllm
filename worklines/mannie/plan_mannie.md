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
- No unattended or auto-approve mode. Every action that changes the system stays subject to the user's approval, as Claude Code normally does. Professor's Omarchy analysis (`0601_01`) already rejected copying unattended agent authority. *Changed for Mannie from Luna (user, 2026-10-25): it runs in Claude Code's auto mode, where a classifier lets lower-risk actions through and blocks the rest; anything destructive or hard to undo is still asked first.*
- No change outside `/storage/.local/` and the user's home on Luna. No boot, card or ArchR change. Creating a Luna user account, if needed, belongs to the Luna workline. *Superseded for Step 6 (user, 2026-10-25): Mannie now operates Luna, starting with `pacman -S git`; boot partition and card layout changes still need the user's explicit go.*
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
- **Finding (2026-10-25): `michael` has no root access on Luna.** ArchR's `/usr/bin/sudo` is a shim that strips sudo's options and runs the command as the caller ("everything already runs as root"); there is no `sudoers`. The "passwordless sudo" recorded for Luna 7.0 does not exist. System work is done as root over SSH from the desk (`ssh luna`). A real `sudo` (or `doas`) for `michael` is needed before Mannie, running on Luna as `michael`, can do system work itself: user to decide.
- **Account (user, 2026-10-15):** from now on Mannie works on Luna as the user `michael` (Luna 7.0: key login, passwordless sudo, home on the `LUNA_HOME` partition), not as root. On 2026-10-25 the graphical session still ran as root; moving it is Wyoh's and the Luna line's work.
- **The move (user, 2026-10-25), Step 6:** "on envoie Mannie sur Luna". Until now the cell prepared and operated Luna from the desk host (Termidor). When Luna is ready, Mannie goes there: Claude Code and a clone of the repository in `michael`'s home, committing its own work and talking to the cell through Git and **GitHub issues** (thread and mailbox). Anthropic's Remote Control is a later test. At the end, a travel journal: how Mannie left Termidor and settled on Luna alone, the reverse of the novel, where Mannie travels from Luna to Earth.
- **User decisions (2026-10-25):**
  - **Mannie operates Luna from now on** and makes it grow: system work on Luna (packages, services, accounts) is part of Mannie's assignment, within the normal permission prompts. Until now it belonged to the Luna line; Professor is told.
  - **`git` is installed with `pacman`** (an accepted change to ArchR's system).
  - **One branch for Mannie, `cell/mannie`**, no sub-branches; work reaches `main` through pull requests. Other cell members may get their own `cell/<name>` branch later.
  - **Messages or issues:** not decided. The user first wanted a short study of Remote Control and cross-machine `SendMessage`: [`docs/0606_01`](docs/0606_01_remote-sessions-study.md).
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
- [ ] 2.4 On Luna (user's direct grant, 2026-10-13 22:53; "fais les tests … vérifier les empreintes mémoire … tester un peu les performances … juste en SSH, pas directement sur l'interface"): repeat 2.1–2.3 on Luna under `/storage/.local/`, then the performance requests, then reboot Luna.
  - **Done (`results/mannie/luna-claude/20261013T210230Z/`):** 2.1.287 installed (signed manifest, checksum matched on Luna, auto-update off), 232 MiB in `/storage/.local/share/claude`. Install 345 s wall but 65 s CPU (writing to the card), peak 181 MiB, lowest MemAvailable 681 MiB, no swap. `--version` 0.08 s, 38 MiB; `--help` 1.64 s, 140 MiB (Pi 0.46 s); interactive first screen 3.5 s (Pi 0.95 s), settled 176 MiB RSS, one process. Memory as on the Pi; CPU about 3.5 × slower. `claude doctor`: only `~/.local/bin` not on PATH (the full path is used; no shell profile changed).
  - Harness changes: target switch `MANNIE_LUNA_LIVE=1`, all remote files under `~/.local/share/tanstfaafllm/mannie/`, installer `TMPDIR` on the card (Luna's `/tmp` is RAM), copy timeout raised (Luna's Wi-Fi moved 0.2–0.5 MB/s), probe records the lowest MemAvailable and swap use, ArchR's `ldd` banner accepted. The preflight assertion failed on that banner in this run; fixed, its output was saved.
  - **Open:** the user's login on Luna (`/storage/.local/bin/claude auth login` in their own SSH terminal), then `test_interactive_start` (logged in), `test_one_request`, `test_repeated_requests`, `test_read_tool_request`, then reboot Luna. Luna was not rebooted after the first series; Wyoh has rebooted it since (2026-10-15). From 2026-10-15, as the `michael` user (user decision): reinstall or move Claude Code into `/home/michael`, and the user logs in there.
- [ ] 2.5 **Mannie's persona and project snapshot on the device** (user, 2026-10-15: Claude on Luna should know it is Mannie and have "a semblance of personality"; the project's Markdown placed on Luna, not loaded by default, with Mannie told where it is if needed).
  - **Prepared (desk):** persona `src/mannie/context/MANNIE.md` (3.3 KB, about 800 tokens per session: who Mannie is, Luna's limits, the other components, the rules, French to the user); `src/mannie/build_context.py` builds the bundle (persona, `VERSION`, `repo/` snapshot of 148 Markdown files, 1.9 MB, with `INDEX.md`). Deployed to `~/.local/share/tanstfaafllm/mannie/context/`; `~/.claude/CLAUDE.md` gets one import line, other lines kept. Relative to `$HOME`, so it moves with the planned `michael` account (Luna 7.0). Tests `test/mannie/test_mannie_context.py` + `mannie_context.feature`: 3 bundle checks pass.
  - **Open:** deploy and the "who are you" request. `luna-pi` did not resolve on 2026-10-15 02:20 (off?); Luna is held by the Luna session for 7.0. Then: does the persona change the cost of a "pong"?
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

### Step 6 — Mannie moves to Luna (user, 2026-10-25)
**Status**: 🧪 6.1–6.5 in progress (🟩 user, 2026-10-25 00:28: "tu as mon feu vert")
- [ ] 6.1 **Claude Code for `michael`**: install 2.1.287 from the binary already verified on Luna (no new download) into `/home/michael/.local`, auto-update off; the user logs in as `michael`; then the 2.4 request measurements and 2.5 (persona and snapshot) under that account.
  - **Installed (`results/mannie/luna-michael-claude/20261024T222859Z/`, 4 tests pass):** from root's verified copy (checksum matched, no Wi-Fi copy), in 92 s (35 s user CPU); `--version` 0.08 s, `--help` 1.6 s, interactive first screen 3.3 s, settled 177 MiB RSS, with Kroko resident: lowest MemAvailable 522 MiB, 2 MiB of swap. `~/.local/bin` added to `michael`'s PATH (`~/.bashrc`, `~/.bash_profile`). The harness now targets `michael@luna` (`MANNIE_LUNA_LIVE=1`).
  - **Open:** the user's login as `michael` (`ssh michael@luna`, then `claude auth login`).
- [ ] 6.2 **Git on Luna**: Luna has no `git` (2026-10-25). **Decided:** `sudo pacman -S git`, done by Mannie (user, 2026-10-25).
  - **Done (2026-10-25, user's choice "b minimal"; evidence `results/mannie/luna-git/20261025T021806Z/`):** `git` 2.56.0-1 and `zlib-ng` 2.3.3-1 from Arch Linux ARM, checked on the desk (SHA-256 equal to the index, good signatures from the Arch Linux ARM Build System key `68B3537F39A313B3E574D06777193F152BDBE6A6`, cross-checked on archlinuxarm.org), installed as root with `pacman -U --assume-installed perl,perl-error,perl-mailtools,shadow`. The original `git` package conflicts with ArchR's `/usr/share/locale` symbolic link (`--overwrite` would break it; `NoExtract` does not help), so it was **repacked** without its translations, `sysusers.d/git.conf` and `git-daemon` units; every other file is the signed original. Explanation on Luna in `/usr/bin/git.readme` (copy: `src/mannie/luna/git.readme`). Checked: `git --version`, HTTPS `ls-remote`, a local commit. **Noise:** every command prints `libpcre2-8.so.0: no version information available` (git built against pcre2 10.47 with symbol versions; ArchR's 10.45 has none); ArchR's pcre2 also serves Sway and glib, so it was not replaced (user to decide).
  - **Earlier blocker:** ArchR's only repository (`[archr]`, 543 packages, index unchanged upstream on 2026-10-25) has no `git`, `perl` or `tmux`. Options put to the user: (a) **micromamba** (one static aarch64 binary) with conda-forge's `git` 2.56 and `tmux` 3.8 in a prefix under `~/.local`, no system change (recommended); (b) Arch Linux ARM packages with `pacman -U`, mixing a second distribution's libraries into ArchR (risky); (c) building from source (no compiler on Luna). The repository is small (16 MB of `.git`; `results/` is not tracked).
- [ ] 6.3 **GitHub credentials on Luna** (proposal, user to decide):
  - **Done:** key `~/.ssh/id_ed25519_github` generated on Luna (`SHA256:nZr/aYaKzZcmPieEkNCwzQYFfFVWUO0cc+PpBM2ZbnE`, comment `mannie@luna (tanstfaafllm deploy key)`), `~/.ssh/config` uses it for `github.com`; GitHub's host key taken from `api.github.com/meta` and checked against the published fingerprint (`SHA256:+DiY3wvvV6TuJJhbpZisF/zLDA0zPMSvHdkr4UvCOqU`), as Luna has no `ssh-keyscan`. **Open:** the user adds the public key as a deploy key with write access.
  - *Git:* a **new SSH key generated on Luna** (`ed25519`, private key never leaves Luna), added to `mdussere/tanstfaafllm` as a **deploy key with write access**. It opens only this repository. The desk host's private keys are **not** copied: Luna runs an agent with shell tools and passwordless sudo, and a copied key would open every repository and server those keys reach.
  - *Issues:* a deploy key cannot use the API. `gh` (official `linux_arm64` release, unpacked under `~/.local/bin`, no system change) with a **fine-grained token** limited to this repository, Issues read/write only, created by the user and pasted by the user into `gh auth login` on Luna. Never in the repository or the logs.
- [ ] 6.4 **Clone and identity**: clone into `/home/michael/git/tanstfaafllm`; commit identity distinct from the desk sessions (e.g. `Mannie on Luna`, with the user's address or a no-reply one); `.claude` settings and the persona point at the clone instead of a snapshot (2.5's snapshot then becomes unnecessary or a fallback).
- [ ] 6.5 **How Mannie's work reaches `main`**. **Decided (user, 2026-10-25):** one branch, `cell/mannie`, and pull requests; no sub-branches.
- [ ] 6.6 **GitHub issues as the cell's mailbox** (open; study [`docs/0606_01`](docs/0606_01_remote-sessions-study.md): cross-machine `SendMessage` works when both sessions are connected to Remote Control, so issues may be only the offline mailbox): labels per workline (`to:professor`, `from:mannie`, …), one issue per request, replies as comments. This changes the `cell-coordination` rules, which are Professor's: proposal sent to Professor (recorded as `plan_professor.md` 5.5, 2026-10-25), decision with the user.
- [ ] 6.7a **First contact, "Mannie from Luna" (user, 2026-10-25 14:56).** There will be two Mannies: **Mannie from Luna**, a Claude Code session running on Luna as `michael`, and this session, which stays on Termidor (the user may stop it later). First goal: start Mannie from Luna and check that it and the desk sessions (this one, then Professor) can talk through Claude Code's Remote Control (`docs/0606_01`). Then its memory: it resumes the same session, and keeps enough memory to go on working even after a full reset. In the end Mannie from Luna takes over this workline.
  - **Checked 2026-10-25 14:56:**
    - on Luna: Claude Code 2.1.287 in `michael`'s `~/.local/bin`, kept on `LUNA_HOME`, auto-update off; `tmux`, `git` and `gh` installed;
    - Luna's GitHub key is unchanged (`SHA256:nZr/aYaK…`).
  - **Waiting for the user:**
    - (1) add the deploy key on GitHub (with write access); GitHub still answers "Permission denied";
    - (2) log in to Claude as `michael` on Luna (`ssh michael@luna`, then `claude auth login`); no credential file yet;
    - (3) ~~connect this desk session to Remote Control~~: already connected; the user was talking to it from a phone (2026-10-25). `ListAgents` shows only Termidor's sessions until one runs on Luna.
  - **Started 2026-10-25 ~16:05:**
    - Setup:
      - the user added the deploy key and logged in as `michael`;
      - the repository is cloned to `~/git/tanstfaafllm` (`main` at `ec4d26a`), on branch `cell/mannie`, with git identity "Mannie from Luna";
      - the persona was rewritten for Mannie from Luna and deployed: it covers its clone, plan, Luna operation, auto mode and the cell channel; 2.7 KB; `test_mannie_context.py` passes;
      - Claude Code runs in `tmux` session `mannie`: `claude --remote-control "Mannie from Luna"`;
      - the first-run login screen was skipped by setting `hasCompletedOnboarding` in `~/.claude.json` (the existing login was reused); the clone was trusted.
    - **Auto mode:** Claude Code now starts in auto mode by default; **the user chose to keep it** (non-goal updated).
    - **Messaging:**
      - `ListAgents` here shows `Mannie from Luna [c004a3] · Remote Control`;
      - Termidor → Luna works: the message arrived;
      - Mannie from Luna declined to answer a peer and showed the user its would-be reply instead, as `cell-coordination` requires. That shows the persona, the clone and the rules are loaded;
      - **Luna → desk works** (Professor, 2026-10-25): Professor pinged it, and its three-line reply reached Professor over Remote Control. It is Claude Code on Luna as `michael`, in `~/git/tanstfaafllm` on `cell/mannie`, with its persona loaded through `~/.claude/CLAUDE.md`. It also reported the declined peer message. Professor registered it in `worklines/agents.md` as "mannie (on Luna) | Mannie from Luna | c004a3". **Both directions work.**
  - **Memory (user, 2026-10-25 16:40):** Mannie and Mike are both expensive and mutually exclusive, so Mannie from Luna will often be stopped and restarted. It must find its session again and keep a memory across sessions and full resets. All exchanges with Mannie from Luna go through Professor (user).
    - **Restart checked:** `claude --continue` resumes the conversation. `--remote-control` is ignored on resume; `/remote-control "Mannie from Luna"` inside the resumed session reconnects to the same claude.ai session and the same `ListAgents` reference.
    - **Design:** [`docs/0607_01`](docs/0607_01_mannie-from-luna-memory.md). Three layers: the conversation, Claude Code's auto memory on `LUNA_HOME`, and the plan in Git. The habits are in the persona's new "Memory" section (3.3 KB).
    - **Launcher:** `~/.local/bin/mannie` (`src/mannie/luna/mannie`): `start [--fresh]`, `stop`, `status`, `attach`; brain lock `/tmp/luna-brain.lock`, to be shared with Mike.
    - **Mannie from Luna's review (through Professor), all taken into the launcher:**
      - the name is quoted;
      - the history check is limited to this project;
      - the lock holds "name pid" (a dead pid counts as free) and is taken with `noclobber`;
      - a failed start cleans up;
      - Escape comes before `/exit`;
      - an optional `stop --save`;
      - the screen texts are pinned for 2.1.287.
    - **Decisions:** on demand, not at boot. `start` resumes only a conversation under 60 min old, otherwise it starts fresh. Mannie from Luna saved `start-stop.md` in its auto memory. It has one local commit on `cell/mannie` (`a5e5a9c`, not pushed) to merge once the desk's work is pushed.
    - Relayed through Professor for Mannie from Luna's review. **Open:** the user tests `mannie stop` and `mannie start`; whether to start at boot or on demand; a note to Mike about the lock.
  - **Then Mannie (desk):**
    - clone the repository to `/home/michael/git/tanstfaafllm` on Luna, branch `cell/mannie`;
    - point the persona (2.5) at the clone;
    - start `claude --remote-control "Mannie from Luna"` in a `tmux` session in the clone;
    - exchange a message both ways.
- [ ] 6.7b **Handing Luna over to Mike (proposed, user 2026-10-25; needs 🟩 go).** Today only the user, or Professor at the user's request, can stop Mannie (`mannie stop --save`), and Mike has no launcher that honours `/tmp/luna-brain.lock`. Proposal: `mannie handoff mike`, run by Mannie from Luna itself.
  - Mannie logs its state in this plan, saves its memory, commits and pushes, and says so in its reply.
  - It then schedules its own stop outside its process, about a minute later (`systemd-run --user --on-active=60 …`), so its turn ends cleanly first. The stop runs `mannie stop` (Escape, `/exit`), releases the lock, and starts Mike with Mike's launcher.
  - Mike gives Luna back the same way when it escalates or finishes (`mike handoff mannie`), so the two are never in memory together.
  - **Depends on:** Mike's launcher on Luna adopting the same lock (note to `mike`, to write when this is green-lit); the user's agreement that Mannie may stop itself. Until then, Mannie never stops or restarts itself.
  - **Acceptance:** a handoff with `free -m` before and after, the lock held by `mike` with a live pid, and no Claude process left; then the way back to Mannie.
- [ ] 6.7 **The departure**: the desk session hands over (plan, open items), the first session on Luna starts from the clone, reads its plan, and opens a first issue ("arrived"). Memory with Kroko resident and Claude Code together is measured (MemAvailable 629 MiB on 2026-10-25 before Claude).
- [ ] 6.8 **The user's goal for Remote Control (2026-10-25):** talk to Mannie live from Claude Desktop, because Luna's screen is too small. The user leaves Luna and Mannie switched on at home, gives Mannie work for the day, and watches it from the office: "la machine qui s'opère toute seule". Mannie works slowly, so it should burn few tokens; how to control usage is part of the step.
  Anthropic's Remote Control: drive the Luna session from the desk or a phone, and `SendMessage` between Luna and the desk. Five tests proposed in [`docs/0606_01`](docs/0606_01_remote-sessions-study.md), to be green-lit; the memory of a resident session on Luna is the key figure.
- [ ] 6.9 **Travel journal**: `docs/` page told by Mannie: leaving Termidor, settling on Luna, working with the cell from afar.
- **Acceptance:** a Claude Code session on Luna, as `michael`, commits and pushes from its own clone, opens and answers a GitHub issue, and the desk cell receives it.

### Step 7 — An Arch Linux ARM root on ArchR's boot path (proposed, user 2026-10-25)
**Status**: 🧪 7.1 done; 🟩 7.2–7.3 (user, 2026-10-25 12:45: "je suis d'accord avec les propositions … modèle ton environnement selon tes besoins. Go"; the card work stays in this line, since Mannie now operates Luna). Backup not run yet (needs the user's `sudo`); nothing is written before it is verified. Earlier: 7.1 in progress (user, 2026-10-25 ~08:55: card in Termidor, "déjà fait le backup … télécharge Arch Linux ARM … commence à préparer l'image … travaille un peu en autonomie … demande à Professor"). Preparation only: nothing is written to the card without the user's explicit go.

The user asked why Luna runs ArchR rather than Arch Linux ARM, since the cell has had to adapt nearly everything. ArchR was chosen at bring-up because it boots R36 clones: its kernel, the panel DTB from Arch R Flasher, and the `rk915` Wi-Fi driver (`docs/03`). Its userland is a gaming distribution: everything as root, home in `/storage`, a `sudo` shim, and a 543-package repository without `git`, `perl` or `tmux`. This is the Luna line's open 7.1, option 2 (recommended by Wyoh), now Mannie's to carry (user, 2026-10-25: Mannie operates Luna).

- **Shape (user, 2026-10-25):** image the current card first; keep p1 `BOOT` (kernel 6.12.94, DTB, overlays, `extlinux.conf`, initramfs), `LUNA_HOME` and `STORAGE`; replace `ARCHR_ROOT`'s contents with the official `ArchLinuxARM-aarch64-latest` root, prepared offline on Termidor (chroot with aarch64 emulation, fast network); carry over ArchR's 6.12.94 modules and firmware; reconfigure Wi-Fi, SSH host keys, `michael` with a real `sudo`, and Wyoh's session. Proposed on a second disposable card, the current card kept as fallback.
- **First compatibility check (2026-10-25, from Luna and ALARM's index):** no blocker found. glibc 2.43 needs a far older kernel; systemd 262 needs ≥ 5.10 (≥ 5.14 recommended), and Luna runs 6.12.94 with cgroup2, fanotify, namespaces, bpf and seccomp present. ArchR runs systemd 255 in hybrid cgroup mode; 262 is cgroup2 only, which the kernel has.
- **To settle in the study:**
  - keep ArchR's kernel: drop or ignore ALARM's `linux-aarch64` (7.3) and `mkinitcpio`;
  - the GPU route: ArchR runs Sway on the proprietary Mali stack (`mali_kbase` + `libmali`), and `/usr/lib/modprobe.d/mali-gpu-noauto.conf` blacklists both drivers until one is chosen; the kernel has `panfrost.ko`, so ALARM's Mesa/Panfrost is the standard route, to measure with Sway and the Slate, with `libmali` as a fallback;
  - the kernel configuration against systemd's list (Luna has no `/proc/config.gz`; read ArchR's kernel sources);
  - the initramfs (`root=LABEL=ARCHR_ROOT`, `boot=`, `disk=` arguments) and ArchR's hardware userland (RK817 audio, `hwid_adc`, `textmode.target`, GPU selection);
  - the work of Step 6 survives in `/home`; `git` then comes from `pacman -S`.
- [ ] 7.1 Study (desk, read-only on Luna): what to carry over, how to build the root, the test list. Acceptance: the user approves the study.
  - **Backup:** the user says it is done; Mannie found no image newer than `luna-archr-before-reshape_20261005_124112.img.zst` in `/data/michael/tanstaafllm/luna-images/` or the user's home. To confirm with the user before any write.
  - **Card read (2026-10-25, read-only):**
    - `BOOT` has `KERNEL` (uncompressed arm64 Image, md5 matches `KERNEL.md5`) with a built-in LZO initramfs, `boot.scr` (picks the DTB by ADC, then `extlinux.conf`), four DTBs, and our overlays.
    - **ArchR's `/init`** (source `projects/ArchR/packages/sysutils/busybox/scripts/init`): resolves `LABEL=`; mounts `ARCHR_ROOT` read-write on `/sysroot`, `BOOT` read-only on `/flash` and `STORAGE` on `/storage`; moves both into the root; then `switch_root … /usr/lib/systemd/systemd`. It warns and waits 60 s when `/usr/lib/kernel-overlays/base/lib/modules/$(uname -r)/` is missing. An Arch Linux ARM root fits if it has `/flash`, `/storage`, that path (a relative link to `/usr/lib/modules`), and a `textmode.target` (on the kernel command line).
    - **Kernel config** (ArchR commit `2d04170214`, 2026-07-08, matching the 2026-07-09 image): every option systemd requires is set (only `DMIID`, absent on ARM, and the optional `CFS_BANDWIDTH` are missing); `DRM_PANFROST=m`; modules uncompressed.
    - **Modules and firmware** live in `/usr/lib/kernel-overlays/base/lib/{modules/6.12.94,firmware}` (LibreELEC style, linked from `/run` at boot): 317 modules including `rk915`, `mali-bifrost`, `archr-joypad`; 40 MB of firmware.
    - **The cell's own units live in `STORAGE/.config/system.d`**, which ArchR reads: `home.mount`, iwd and sshd persistence drop-ins (`/storage/.cache/iwd`, `/storage/.cache/ssh`), and Wyoh's `wyoh-sway`, `wyoh-gamepad`, `wyoh-layout`. Arch Linux ARM will not read that directory: the first new root boots in text mode with Wi-Fi and SSH, reusing iwd's known networks and the SSH host keys in place (the private keys are root-only and are not copied); Wyoh's session is a second phase with Wyoh, after the GPU choice.
  - **Image built (2026-10-25 09:30; study [`docs/0701_01`](docs/0701_01_alarm-root-study.md); evidence `results/mannie/alarm-root/`):** `luna-alarm-root.ext4` in `/data/michael/tanstaafllm/tmp/mannie-alarm/` (24 GiB apparent, 2.2 GB used, label `ARCHR_ROOT`, `e2fsck` clean), from the signed Arch Linux ARM tarball (2026-08-05) and ArchR's modules and firmware. `michael` uid 1000 with sudo; root locked, SSH by key with Luna's host keys on `STORAGE`; iwd with the known networks on `STORAGE`; zram as ArchR; tty1 autologin as the rescue path; `luna-firstboot` installs 21 signed packages offline with Luna's own pacman. Tests `test/mannie/test_alarm_root.py` pass (default and image). Write script `src/mannie/alarm/write-luna-root.sh` (user-run, backs up `ARCHR_ROOT` with `e2image` first) **not run**. Wyoh's session, Mycroft and audio are a second phase.
  - **Build method (desk, no root):** `fakeroot` for ownership, `mke2fs -d` for an ext4 image labelled `ARCHR_ROOT`. No `qemu`, so packages are installed natively on Luna at first boot by `pacman`, from a cache filled on the desk (`src/mannie/alarm/fetch_packages.py`: dependency closure, SHA-256 against the database, signature from the Arch Linux ARM key).
- [ ] 7.2 **Back up the whole card** (user, 2026-10-25: there is no backup system yet and only one card; back it up, recover what is on it to feed the next image, then rewrite the card). Script `src/mannie/luna/backup-luna-card.sh`, user-run with `sudo`, adapted from the Luna line's factory-card archive script:
  - pins the card on its exact size (62,534,975,488 bytes) and its four filesystem UUIDs;
  - unmounts it and sets it kernel read-only;
  - makes the raw image (`.img.zst`), with its SHA-256 computed while reading and checked again on the decompressed image;
  - adds `STORAGE` and `LUNA_HOME` as tar files (read-only mounts, numeric owners, ACLs and xattrs; mode 400, because they hold Luna's SSH host keys and Wi-Fi passphrases);
  - writes everything to `/data/michael/tanstaafllm/luna-images/archr/luna-archr-before-alarm_<stamp>.*`.
  Static safety tests: `test/mannie/test_luna_card_scripts.py` (pass). **Not run yet:** it needs the user's `sudo`.
  - **Done 2026-10-25 13:36–13:58 (user's `sudo`):** `luna-archr-before-alarm_20261025_133603.*` in `/data/michael/tanstaafllm/luna-images/archr/`: raw image 4.85 GB compressed, which decompresses to the card's exact 62,534,975,488 bytes with the raw-card SHA-256 `b7bb0c4b…bd73`; `STORAGE` tar 652 MB and `LUNA_HOME` tar 113 MB (mode 400). Mannie re-checked every SHA-256 and `zstd -t`.
  - 2026-10-25 12:50: the user thought the backup was done; no `luna-archr-before-alarm_*` file exists and the card was never set read-only. Still to run.
- [ ] 7.2b **Notes from the other lines (Professor's relay, 2026-10-25), read before 7.3:**
  - **Wyoh** [`docs/0702_01`](docs/0702_01_note-from-wyoh-session-needs-on-a-new-root.md):
    - root packages: Sway, seatd, foot, grim, Python 3, xkeyboard-config, Liberation fonts, SDL2, ALSA libraries, NetSurf's libraries;
    - devices for `michael`: `input`, `/dev/uinput`, `audio`, iwd's D-Bus policy and state, a seatd seat;
    - its units in `/storage/.config/system.d` and `textmode.target`;
    - root-and-`/storage` assumptions (`HOME=/storage`, the MCP venv built for Python 3.13).
    - **Main risk: the GPU.** Panfrost failed on this device (black panel, 2026-10-11), so Sway needs ArchR's libmali, `/usr/lib/archr/gpudriver` and its libmali hook, with `mali_kbase`.
  - **Mycroft** [`docs/0700_02`](docs/0700_02_note-from-mycroft-dictation-on-the-new-root.md): `/usr/bin/python3` (standard library only), `arecord` with alsa-lib's `plug` plugin, glibc and libstdc++, `audio` for `michael` if the provider stops running as root; its harness needs root SSH and reboots (kept: root logs in by key).
  - **User decisions (2026-10-25 13:50):** complete the image first, then boot to text mode; Mannie relocates to Luna, operates it over SSH, then repairs Sway from there. **Done:** Wyoh's and Mycroft's packages are added (`packages.txt`, 125 packages, 161 MB), and ArchR's Mali stack is copied, inactive, to `/usr/local/lib/archr-mali/`. No graphical unit is enabled. First boot installs `iwd` and `sudo` first, so SSH answers within minutes. The done flag is set only if the full install succeeds. The write script makes only the disk and `ARCHR_ROOT` writable again, after the backup's kernel read-only.
  - **Consequence:** the current image boots to text mode only, so Luna's screen session stops until a second phase. Adding Wyoh's and Mycroft's packages comes to 125 packages and 161 MB with Arch Linux ARM's Sway (wlroots 0.20, newer than ArchR's 1.11) and Mesa. ArchR's Mali stack must be carried over from the card, which is unmounted until the backup ends. Put to the user: write the text-mode root now, or extend the image first.
- [ ] 7.3 (User, 2026-10-25: the same card, after the backup; only `ARCHR_ROOT` is replaced, and `BOOT`, `LUNA_HOME` and `STORAGE` are kept, as proposed.) Image rebuilt at 12:55 with Mannie's working set (`src/mannie/alarm/packages.txt`: 40 packages, 69 MB, including `github-cli`, `jq`, `ripgrep`, `man-db`); the signing key is now in the repository (`archlinuxarm-builder.asc`). Tests pass. Then: write it (`write-luna-root.sh`, user-run); boot; test Wi-Fi, SSH, Sway, gamepad, audio and the USB-C microphone, Kroko, Claude.

  - **Written and booted (2026-10-25 14:27; user ran `write-luna-root.sh`):** Arch Linux ARM on ArchR's kernel 6.12.94. Luna kept its SSH host key; Wi-Fi was up in under 90 s. `luna-firstboot` finished in about 3 minutes (290 packages; `iwd`, `sudo`, zram 491 MiB; the two `setcap` calls failed, rc=1, not yet looked at). `michael` has a real `sudo`. No failed unit.
- [x] 7.4 **Sway back on the new root** (user: "remets-nous une interface graphique", 2026-10-25). Done 14:35:
  - ArchR's Mali stack was put back from the image's inactive copy (`src/mannie/luna/install-archr-mali.sh`); `mali_kbase` binds (`/dev/mali0`).
  - Wyoh's units were linked from `/storage/.config/system.d` and enabled; the session runs as root, as on ArchR. Sway 1.12 renders on Mali, the gamepad is attached, the bar shows "Mick wifi home".
  - After a reboot the session came back by itself in about 1 minute.
  - Wyoh's MCP venv was rebuilt for Python 3.14. An MCP screenshot needs `HOME=/storage`, because root's home is now `/root`.
  - Evidence: `results/mannie/luna-sway/20261025T1335Z/` (grim, after the reboot, and the MCP capture). Note to Wyoh: `worklines/wyoh/docs/1300_01`.
  - **Memory (2026-10-25 14:43, 8 min after boot, session idle, Kroko resident, Slate and keyboard started):** 983 MiB total, 435 MiB used, **547 MiB available**, zram 491 MiB unused, memory pressure 0. PSS: Mycroft/Kroko 153 MiB, Wyoh's session 167 MiB (Sway 63, swaybg 21, gamepad 19, layout 19, Slate foot 15 + 12, swaybar 9, keyboard 8), system 97 MiB (with Mannie's SSH probe). ArchR with the same set (2026-10-25 00:05): 629 MiB available, so about **80 MiB less** on the new root, roughly from Sway 1.12/wlroots 0.20 (+13 MiB RSS), the four Python 3.14 processes (about +5 MiB each), Kroko (+9 MiB), and larger journald and resolved. Room left for Claude Code (about 180 MiB idle, 244 MiB peak per request on `luna-pi`): about 300 MiB before zram is touched.
  - **Open:** the GLES-only SDL2 bind (Arch Linux ARM's file name differs); `wyoh-gamepad`'s focus subscription error; menu, Slate, Kroko, Wi-Fi panel and apps not yet checked; the session as `michael`; `setcap`.
- [x] 7.5 **Keyboard rescue: Ctrl+Alt+F1 brings back the console** (user, 2026-10-25: keep michael's autologin console on tty1 and reach it with the classic keys from a USB keyboard if SSH or the desktop fail). The kernel has no SysRq (`CONFIG_MAGIC_SYSRQ` unset).
  - Sway now runs on **tty7**, through a drop-in `/etc/systemd/system/wyoh-sway.service.d/10-luna-vt7.conf` (`chvt 7`; Wyoh's unit is unchanged); tty1 keeps michael's autologin console.
  - `luna-vt-rescue.service` (`src/mannie/luna/luna-vt-rescue.py`, standard-library Python, about 15 MiB RSS) reads every keyboard directly, picks up new ones within 5 s, and runs `chvt N` on Ctrl+Alt+F1…F12, so it works even if Sway is stuck.
  - Checked with a uinput virtual keyboard (`test/mannie/test_luna_vt_rescue.py` + `luna_vt_rescue.feature`): tty1, then tty7, the service's journal shows both `chvt`, and the desktop renders afterwards. After a reboot: Sway on tty7, bash on tty1, every unit active, 530 MiB available.
- [ ] 7.6 **To test interactively with the user** (user, 2026-10-25: no long test sessions now; collect them):
  - a real USB keyboard: Ctrl+Alt+F1 shows the console, Ctrl+Alt+F7 the desktop;
  - the menu (Start), the apps, and the Mannie entry (it still starts root's Claude in `/storage`);
  - the Slate (L1) and Kroko dictation, with the USB-C headset;
  - the on-screen keyboard and the gamepad controls;
  - the Wi-Fi panel (and the boot network: the Freebox profile is still in iwd's state);
  - the calculator and Wolfenstein (the GLES-only SDL2 bind fails: Arch Linux ARM's file name differs);
  - `wyoh-gamepad`'s "focus subscription" error in the journal;
  - Wyoh's MCP harness with `HOME=/storage`;
  - the two `setcap` calls that failed at first boot;
  - memory trims, if wanted: `systemd-networkd` (unused), `systemd-userdbd`.

---

## Progress tracking ✅

- ✅ Step 0 — Workline set-up
- 🧪 Step 1 — Desk research
- ✅ Step 2 — Install and first start on `luna-pi` (Luna later)
- ⏳ Step 3 — First session on Luna
- ⏳ Step 4 — Wyoh's MCP server as a local tool
- ⏳ Step 5 — Hand-offs
- 🧪 Step 6 — Mannie moves to Luna (6.1–6.2 done)
- 📋 Step 7 — Arch Linux ARM root (proposed)

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
| 2026-10-13 22:53 | User: "Luna est à ta disposition … fais les tests … juste en SSH". Professor confirmed the holder at 22:55 and stood Wyoh down. 2.4 started. |
| 2026-10-13 23:20 | 2.4 first series done on Luna (install, CLI and interactive start, not logged in); figures in 2.4. Two false starts first: a stalled desk download (the renamed cache; the old cached binary reused, checksum matched) and the 10-minute copy timeout. Waiting for the user's login. |
| 2026-10-15 02:20 | User request recorded as 2.5 (persona and project snapshot on the device). Prepared and tested on the desk; deployment waits for `luna-pi` (unreachable) or a Luna slot (Luna session holds it for 7.0). |
| 2026-10-15 02:40 | User: deploy 2.5 on Luna under the `michael` account; from now on Mannie works as the user, not root (Luna 7.0; Luna rebooted). Luna did not come back on "Mick wifi home": it seems to join the Freebox at boot (user). Note to Wyoh `worklines/wyoh/docs/0700_02`. Waiting for Luna on the home network. |
| 2026-10-25 00:10 | Status check as `michael` (SSH `michael@luna`, key login, passwordless sudo): Luna is back on "Mick wifi home". The graphical session still runs as **root** (Sway, Wyoh's services, Mycroft's resident Kroko, about 156 MiB); `/home` is a new 7.8 GB partition and `/home/michael` holds no Claude Code yet. Root's Claude Code in `/storage` was logged in on 2026-10-14 and used (Wyoh's Mannie menu entry). MemAvailable 629 MiB with Kroko resident. Nothing changed on Luna. |
| 2026-10-25 00:20 | User's direction recorded as Step 6, "Mannie moves to Luna": Claude Code and the repository in `michael`'s home, commits from Luna, GitHub issues as the cell's mailbox, Remote Control later, then a travel journal. Checked: no `git` or `gh` on Luna, `.git` is 16 MB. Proposals for the key, the token and the branch put to the user; the mailbox proposal goes to Professor. |
| 2026-10-25 00:27 | User decisions: Mannie operates Luna from now on; `git` with `pacman`; one branch `cell/mannie` with pull requests. Study of Remote Control and cross-machine messages written (`docs/0606_01`, documentation only): `SendMessage` works between machines when both sessions are connected to Remote Control (Pro qualifies; Luna's 2.1.287 is recent enough). Messages or issues: the user decides after the study. |
| 2026-10-25 00:28 | 🟩 go 6.1–6.5 (user). The user's Remote Control goal recorded in 6.8 (live talk from Claude Desktop, Mannie working alone during the day, token control). Luna taken in `luna-access.md`. |
| 2026-10-25 00:32 | 6.1 installed for `michael` (4 live tests pass). 6.3 key generated on Luna, GitHub host key verified. 6.2 blocked: ArchR's repository has no `git`; options put to the user. Waiting for: the deploy key, the git route, the user's login. Luna still held. |
| 2026-10-25 03:22 | 6.2 done: `git` 2.56.0 from Arch Linux ARM (signatures checked, repacked around ArchR's locale link), `zlib-ng`, `/usr/bin/git.readme`. Found: ArchR's `sudo` is a shim, `michael` has no root; install done as root over SSH. Open: deploy key (user), login as `michael` (user), pcre2 noise and a real `sudo` (user decisions). Luna still held. |
| 2026-10-25 03:35 | Step 7 proposed after the user's question (why ArchR, not Arch Linux ARM): keep ArchR's boot path, kernel and modules, and replace its root with Arch Linux ARM's. First compatibility check found no blocker (systemd 262 ≥ 5.10, glibc fine, kernel 6.12.94); the GPU route (Mali blob versus Panfrost) is the main point to measure. |
| 2026-10-25 09:10 | 7.1 started (user: card in Termidor, prepare the Arch Linux ARM image, work autonomously, ask Professor if needed). Card remounted read-only; boot path, initramfs, kernel config, modules and the cell's units read (findings in 7.1). Arch Linux ARM tarball downloading. |
| 2026-10-25 09:31 | 7.1 study written (`docs/0701_01`): no compatibility blocker between Arch Linux ARM (glibc 2.43, systemd 262) and ArchR's 6.12.94 kernel and initramfs. First root image built and checked on the desk (tests pass); write script ready, not run. Waiting for the user: the backup's location, same or second card, and the go to write. |
| 2026-10-25 12:20 | User: no backup exists yet, one card only. 7.2 backup script written and tested statically (whole-card image with verified SHA-256, plus `STORAGE` and `LUNA_HOME` tar files); waiting for the user to run it with `sudo`. |
| 2026-10-25 12:56 | 🟩 7.2–7.3 (user). Backup not found on disk (the user thought it done): waiting for `sudo src/mannie/luna/backup-luna-card.sh /dev/sde`. Meanwhile the image was rebuilt with Mannie's working set (40 packages, `github-cli` included); tests pass. |
| 2026-10-25 13:45 | Backup running (user's `sudo`, started 13:36). Wyoh's note `0702_01` and Mycroft's `0700_02` read (7.2b): the GPU needs ArchR's libmali stack, since Panfrost failed on Luna; the current image would leave Luna in text mode until a second phase. |
| 2026-10-25 14:10 | Backup done and verified (7.2). Final image built (`7f079765…`, 2.3 GB used): Wyoh's and Mycroft's packages, ArchR's Mali stack kept inactive, network first at first boot. Tests pass. Waiting for the user to run `write-luna-root.sh` (7.3). |
| 2026-10-25 14:40 | 7.3 done: the user wrote the new root; Luna boots Arch Linux ARM, first boot done in about 3 minutes, SSH as before. 7.4 done: Sway is back on ArchR's Mali stack with Wyoh's units, and survives a reboot; MCP screenshot taken after rebuilding Wyoh's venv for Python 3.14. Note to Wyoh `1300_01`. |
| 2026-10-25 14:45 | Memory measured: 547 MiB available with Kroko and the session; about 80 MiB less than ArchR, mostly systemd 262's larger services and units ArchR lacked (`networkd`, `userdbd`, michael's user session); trims proposed. |
| 2026-10-25 14:53 | 7.5 done: Sway on tty7, michael's console on tty1, `luna-vt-rescue` makes Ctrl+Alt+F1 work even if Sway is stuck; checked with a virtual keyboard and after a reboot. The user asked to stop long tests: the remaining checks are collected in 7.6 for an interactive session. |
| 2026-10-25 14:56 | User: prepare the move. Mannie from Luna on Luna, this session stays on Termidor; first check Remote Control messaging, then memory across sessions and resets; then Mannie from Luna takes over the workline. Recorded as 6.7a. Waiting for the deploy key, the login as `michael`, and `/remote-control` in this session. |
| 2026-10-25 16:08 | Mannie from Luna started (clone, `cell/mannie`, persona, `tmux`, Remote Control; auto mode kept by the user). Termidor → Luna message delivered; it declined a peer's request per `cell-coordination`. Professor asked to test Luna → desk. |
| 2026-10-25 16:09 | Luna → desk confirmed through Professor: Remote Control messaging works both ways. Next: memory (resume the session, durable notes across resets, restart at boot), and committing the desk's work so the Luna clone has the current plan. |
| 2026-10-25 16:54 | Memory: restart behaviour checked; design `docs/0607_01`; launcher `mannie` installed on Luna; persona gains a "Memory" section; relayed to Mannie from Luna through Professor (user's rule). |
| 2026-10-25 16:54 | Mannie from Luna, on Professor's relay of desk Mannie (6.7a, memory across restarts): reviewed `docs/0607_01` and `~/.local/bin/mannie`, answered the two open questions, saved the first auto-memory entry (`start-stop`). Review sent to Professor. |
| 2026-10-25 16:56 | Mannie from Luna's review of the memory design taken into `mannie` (stale-lock handling, cleanup, `stop --save`, pinned screen texts); on demand; resume only under 60 min. Waiting for the user's go to commit and push the desk's work to `cell/mannie`. |
| 2026-10-25 17:20 | Request from Mycroft (tanstfaafllm-e6) through Professor, at the user's request: (1) check dictation on the new Arch Linux ARM root; (2) prepare Luna for Mycroft 8.8 (MemAvailable with Wyoh and resident Kroko, one WAV-replay dictation, reboot before and after, ~15 min). Its needs note `docs/0700_02` is not on this branch. Check 1: python3 3.14.8 and arecord present; `michael` is in `audio`; resident Kroko (`mycroft_dictate.py --resident`, root, up 2 h 26, RSS 130 MiB) maps `libsherpa-onnx-c-api.so` and `libonnxruntime.so` from `/storage/.local/opt/mycroft/sherpa-onnx-v1.13.8…`, capturing from card 0 (`pcmC0D0c`, rk817). **No card 1**: only rk817 in `/proc/asound/cards`, only the root hub in `lsusb`, so the USB-C headset is not seen. 8.8 waits for the user: headset, my stop during the slot, the reboots. |
| 2026-10-25 20:05 | User: a second Claude Code (root, `/storage/.local/bin/claude`, ~250 MiB) came from Wyoh's "Mannie" menu entry; the user closed it and asked that the entry open this session. Added `mannie open` (start if needed, then attach) to the launcher; the deployed `wyoh-mannie.desktop` now runs it as `michael` (original kept). Note to Wyoh for its repository copy: `worklines/wyoh/docs/0000_09`. The user's two new Luna rules (SSH needs Mannie's go, no reboot while Mannie runs) saved in auto memory until the desk commits them. |
| 2026-10-25 21:08 | User asked how Mannie can step aside for Mike; proposal recorded as 6.7b (`mannie handoff mike`: save, then a stop scheduled outside the session, lock released, Mike started). Waiting for 🟩 go and for Mike's launcher. |
| 2026-10-25 21:20 | User via Professor: stop now for Mike's first run on Luna. State saved: auto memory `open-items` (Mycroft 8.8 waits for the user's three answers: headset, reboot slot, Mannie stopped; 6.7b waits for a go; Wyoh note 0000_09). Professor stops Mannie over SSH with `mannie stop`; nothing restarts it until Mike's run is over and the user says so. |
| 2026-10-26 07:10 | Started fresh by Professor at the user's request (lock `mannie 13735`). Mike's 4.5–4.6 done: LFM2.5-350M too slow on Luna (105–165 s per request), Mike back to desk studies, Luna left to Mannie. The 22:11 reboot was not clean: boot −1 ends at 22:08:12 with no shutdown sequence, no OOM or panic logged, so a hard reset or power loss (button, battery or freeze); reported to the user. USB-C headset now seen as card 1 (LUDOS Earphones), answering one of Mycroft 8.8's three questions; the reboot slot and Mannie's stop still wait for the user. 6.7b still waits for a go. MemAvailable 361 MiB. |

---

## Workline artifacts

- `worklines/mannie/plan_mannie.md` — this plan.
- `test/mannie/luna_pi_claude.feature`, `test/mannie/test_luna_pi_claude.py`, `test/mannie/claude_probe.py` — Step 2 live harness (`MANNIE_LUNA_PI_LIVE=1` for `luna-pi`, `MANNIE_LUNA_LIVE=1` for Luna).
- [`docs/0606_01_remote-sessions-study.md`](docs/0606_01_remote-sessions-study.md) — Remote Control and cross-machine messages, for 6.6 and 6.8.
- [`docs/0701_01_alarm-root-study.md`](docs/0701_01_alarm-root-study.md) — Step 7: how Luna boots, kernel compatibility, the Arch Linux ARM root image, risks, how to write it.
- `src/mannie/alarm/` (`build-luna-root.sh`, `fetch_packages.py`, `accounts.py`, `write-luna-root.sh`, `files/`, `README-luna.md`), `test/mannie/test_alarm_root.py`, `test/mannie/alarm_root.feature` — Step 7 build, write script and tests.
- `src/mannie/context/MANNIE.md`, `src/mannie/build_context.py`, `test/mannie/test_mannie_context.py`, `test/mannie/mannie_context.feature` — 2.5 persona and project snapshot for Claude Code on the device.
- [`docs/0101_01_mannie-on-luna-intent.md`](docs/0101_01_mannie-on-luna-intent.md) — Step 1 research and the intent for Step 2: install, login, measurements, stop conditions.
- [`docs/0203_01_luna-pi-claude-result.md`](docs/0203_01_luna-pi-claude-result.md) — Step 2 result on `luna-pi`: memory, time, tokens, and what they mean for Luna.
- Related: `worklines/professor/docs/0503_01_delegated-coordination-log-2026-10-09.md` (D1, the vocabulary), `worklines/mike/plan_mike.md` (Step 6.3, escalation to Mannie), `worklines/mycroft/plan_mycroft.md` (input modes), `worklines/luna-access.md` (Luna slots).
