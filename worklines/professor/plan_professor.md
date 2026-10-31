---
**Status**: 📋 Draft
**Date**: 2026-09-25
**Priority**: High
**Maintained**: Yes
---

# Professor de la Paz — programme framing and workline coordination (workline `professor`)

## Overview

Professor de la Paz owns the project’s shared direction: a single, reviewable decision baseline, top-level architecture boundaries, and the coordination and isolation of specialised worklines. It does not implement the handheld, Raspberry Pi, local models, voice stack, or window manager.

The source discussion is now available as a 155-message transcript. The prior synthesis was prepared from an incomplete extract, so the immediate planning problem is not to execute ideas prematurely: it is to reconcile the full evidence into a small set of decisions that you can arbitrate.

Done means that the project has an agreed charter, a bounded v0 objective, named worklines with clear inputs/outputs, and an approved order for opening them.

## Workline directory layout

- Plan (this file): `worklines/professor/plan_professor.md`
- Produced docs: `worklines/professor/docs/`
- Workline scripts: `worklines/professor/scripts/` if later needed

## Goals ✅

- Establish one authoritative decision ledger from the completed initial discussion.
- Turn the project concept into an arbitrable v0 scope and a small set of architectural boundaries.
- Define the contracts and sequence for follow-on worklines before initiating any of them.
- Preserve the distinction between the final handheld (`Luna`) and its Raspberry Pi reference target (`luna-pi`).

## Non-goals ❌

- Implementing operating-system images, services, models, voice features, or a window manager.
- Buying hardware, domains, or paid services.
- Treating ChatGPT discussion claims as verified technical facts.
- Creating specialised worklines before their mandate and acceptance criteria are approved.

## Key decisions / assumptions

- The programme name is provisionally **TANSTAAFLLM**; the current repository spelling and any rename remain an open administrative decision.
- `Luna` is the intended handheld target. The discussion associates it with an RK3326/Mali-G31-class, approximately 1 GB device, but the exact variant must be measured on arrival.
- `luna-pi` is a Raspberry Pi 4B reference/prototyping target; its RAM and configuration remain to be verified.
- Early development happens on the desktop machine. Devices are reached through SSH rather than being treated as primary coding workstations.
- The names Luna, Mycroft, Mannie, and Wyoh are candidate components of a shared project vocabulary; their precise component ownership must be ratified.
- The full transcript, not the earlier partial synthesis, is the source of truth for initial discovery.

## Risks / constraints

- The transcript contains proposals, guesses, and web claims that may be obsolete or unsupported. **Mitigation:** label each item as decided, hypothesis, or research question before implementation.
- Hardware variants and the 1 GB target make resource assumptions risky. **Mitigation:** hardware characterisation precedes runtime commitments.
- The discussion contains several attractive directions (local LLM, frugal assistant, voice, portable Codex interface, WM). **Mitigation:** select one v0 outcome and make the rest explicit follow-on tracks.
- The project has a strong thematic identity. **Mitigation:** retain it in naming and interaction design without letting it substitute for measurable requirements.

## 🚦 Green light protocol

- Default: planning and documentation only until you explicitly say **“🟩 go Step N”**.
- You arbitrate the decision points in each step before the next one is opened.
- If scope changes materially, update this plan before proceeding.
- No specialised workline starts until Step 3 is approved, except a line you explicitly authorise. The Mycroft line is authorised as a pre-hardware ASR v0 track.

## Plan steps (no execution until green light)

### Step 1 — Reconcile the decision baseline
**Status**: 🧪 Ready for review

- [x] 1.1 Read the complete initial transcript and produce a decision ledger: confirmed decisions, strong preferences, hypotheses, and discarded ideas.
- [x] 1.2 Correct or supersede the current translated analysis where the incomplete extract omitted material decisions.
- [x] 1.3 Identify conflicts needing your arbitration, including project naming, primary v0 purpose, device roles, and component names.
- [ ] 1.4 Acceptance: you approve a concise decision ledger and an explicit open-questions list.

### Step 2 — Define the v0 charter and system boundaries
**Status**: 🧪 Ready for review

- [x] 2.1 Propose one primary v0 outcome: Mycroft v0, offline French recorded-audio transcription to text.
- [x] 2.2 Define what runs on the desktop, `luna-pi`, Luna, and remote services; identify mandatory offline and latency expectations.
- [x] 2.3 State success measures: usability, memory ceiling, responsiveness, battery/thermal constraints, reproducibility, and learning goals.
- [ ] 2.4 Acceptance: you approve a one-page charter that excludes more scope than it admits and makes v0 testable.

### Step 3 — Design the workline map
**Status**: ⏳ Pending

- [ ] 3.1 Define the minimum specialist worklines, their dependencies, owners, deliverables, and stop conditions.
- [ ] 3.2 Proposed candidates for arbitration: platform characterisation; local intelligence runtime; frugal system assistant; interaction/WM; developer workflow and deployment. Mycroft is already its own explicitly authorised line.
- [ ] 3.3 Decide which candidates are actual independent worklines versus sub-steps of another line.
- [ ] 3.4 Acceptance: every approved workline has one clear question to answer, concrete inputs, and an exit artifact.

### Step 4 — Open the approved foundation workline(s)
**Status**: ⏳ Pending

- [ ] 4.1 Create only the workline(s) approved in Step 3, each with its own plan and green-light protocol.
- [ ] 4.2 Start with hardware/platform characterisation if it remains a dependency for every selected v0 path.
- [ ] 4.3 Acceptance: no implementation begins without a workline plan and its explicit green light.

### Step 5 — Maintain programme integration
**Status**: ⏳ Pending

- [ ] 5.1 Review completed workline artifacts against the v0 charter and update cross-workline decisions.
- [ ] 5.2 Record decisions that change public naming, hardware assumptions, interfaces, or delivery scope.
- [ ] 5.3 Acceptance: the Professor workline always exposes the current project direction, workline boundaries, and next approved action.

- [ ] 5.4 **Delegated coordination, 2026-10-09 22:30 → midnight (user mandate).** The user is away and asked Professor to manage the cell, relaunch sessions that have finished, and decide in their place, within the limits written in the log. Every instruction and decision is recorded in [`docs/0503_01_delegated-coordination-log-2026-10-09.md`](docs/0503_01_delegated-coordination-log-2026-10-09.md) for the user's review.
- [ ] 5.5 **Mannie on Luna: the cell's channel through GitHub issues (request from Mannie, tanstfaafllm-d3, 2026-10-25; `worklines/mannie/plan_mannie.md` Step 6, point 6.6).** Claude Code and a repository clone are to run under `michael` on Luna, and Mannie would commit from there. A session on Luna cannot use SendMessage, so Mannie proposes GitHub issues as its channel to Professor: one issue per request, labels `to:<workline>` / `from:<workline>`, replies as comments; Remote Control later. This would change `skills/cell-coordination`. Professor gives its view only when the user asks. Open for the user, not Professor: git on ArchR through pacman (system files, possibly Luna's job), and branch with PRs or direct commits to `main`.
- [x] 5.6 **Boundary change (confirmed by the user, 2026-10-25; applied) reported by Mannie (user decisions of 2026-10-25, recorded in `plan_mannie.md`).** (1) Mannie operates Luna and makes it grow: system work on Luna (packages, services, accounts) moves from the Luna line to Mannie, within normal permission prompts, starting with `sudo pacman -S git`; boot and card layout still need the user's go. (2) Mannie works on one branch, `cell/mannie`, and reaches `main` through PRs; other members may get `cell/<name>` later. (3) Messages or issues still open (study `worklines/mannie/docs/0606_01`: cross-machine SendMessage works if both sessions use Remote Control, which would mean `/remote-control` in Professor's session too). To reflect (1) and (2) in `AGENTS.md`, `plan_luna.md` and the cell-coordination skill, Professor waits for the user's own confirmation, because the user asked Professor to stand by.

### Step 6 — Analyse Omarchy as an external reference
**Status**: 🧪 Ready for review — analysis done 2026-10-05 ([note](docs/0601_01_omarchy-analysis.md))

- [x] 6.1 Read Omarchy's public site and manual and record what it is: base, compositor, packaging, update/recovery model, keybinding and menu model, theming, hardware assumptions.
- [x] 6.2 Compare it with TANSTAAFLLM's principles and the active Wyoh/Luna/Mycroft direction, judged against the low-end R36 Ultra target (RK3326, ~1 GiB, 720×720, no GPU driver on ArchR, controller plus optional USB keyboard).
- [x] 6.3 Classify each idea as adoptable, adaptable, or rejected for Luna, with the reason; name the owning workline for each without opening any work there.
- [ ] 6.4 Acceptance: a reviewable note in `docs/` that makes no hardware or performance claim beyond published sources and recorded Luna evidence, and starts no implementation in another workline.

### Step 7 — Document the software produced and the architecture
**Status**: 🧪 In progress: green-lit 2026-10-11; stage 1 written (architecture and the six component pages), stopped for the user's review.

**Why:** the project now produces real software spread across six worklines, but it is described only in plans, intents, results and the LOGBOOK. Nobody can see how the pieces fit, how to run them, or what they cost, without reading the history. The user wants a documentation of the **software elements and the architecture**, not of the worklines themselves.

**What exists to document** (inventory of 2026-10-11, to be completed in 7.1):

| Area | Software | Where |
|---|---|---|
| Wyoh (desktop) | Sway configuration and units; gamepad daemon (`wyoh_gamepad.py`), with per-app profiles and key maps; Slate (`wyoh_slate.py`); patched AZERTY on-screen keyboard (`wvkbd`); four-tile layout (`wyoh_layout.py`); app manifests and menu (`wyoh_apps.py`, `apps/`: calculator, Commander, Wolfenstein 3D, Dino); development MCP server (`wyoh_mcp_server.py`) and virtual input; deploy and Make targets | `src/wyoh/`, `Makefile` |
| Mycroft (input) | text console (`mycroft_console.py`); dictation provider for the Slate (`mycroft_dictate.py`, JSON-lines protocol); ASR benchmark and model pre-optimisation | `worklines/mycroft/scripts/` |
| Mike (local brain) | tool contract (`mike_contract.py`), evaluation harness and fake Wyoh, manual chat (`mike_chat.py`) | `src/mike/`, `test/mike/`, `worklines/mike/scripts/` |
| Mannie (frontier model) | Claude Code install and measurement probes | `test/mannie/` |
| Luna (device) | card archive, flash, reshape, Wi-Fi overlay, console and boot scripts | `worklines/luna/scripts/` |
| Cross-cutting | test conventions, live tests over SSH, `luna-access.md`, `agents.md`, skills | `docs/02_testing.md`, `test/`, `skills/` |

- [ ] 7.1 **Inventory (read-only):** list every program, service, configuration, interface between components (MCP tools, sockets, JSON-lines protocols, status files, Make targets), deployment location on Luna or `luna-pi`, and measured cost. Mark what is live on Luna and what is offline only. Output: an appendix to the intent.
- [x] 7.2 **Options chosen by the user, 2026-10-11:**
  - **Audience:** the user, then very capable friends and colleagues, interested in the architecture, choices and models.
  - **Layers:** all five, with decision records at a high level; everything readable without two hours or an AI.
  - **Form:** Markdown in `docs/`, diagrams in SVG (not Mermaid), each one rendered to PNG and inspected.
  - **Tone:** *Moon Is a Harsh Mistress*, the agent cell, and retro gaming, like the wallpaper.
  - **Checking:** no formal tests; each workline reviews its own page after each stage.
  - **Writer:** Professor writes the first version.
  - **Order:** in stages, architecture and components first; the 7.1 inventory is done along the way.
  - The options as offered:
  - **(a) Audience:**
    - a newcomer, human or agent, who must run and change the system;
    - the user, as a map of their own project;
    - an outside reader.
    - One primary audience, possibly a second.
  - **(b) Layers** (one or several):
    1. **Architecture overview:** the components on Luna, the processes and who starts them, the data flows (voice → Mycroft → Slate or Mike → Wyoh → apps; Mannie as escalation), the interfaces between them, the 1 GiB memory budget, and what runs where (desk host, `luna-pi`, Luna).
    2. **Component reference, one page per software element:** purpose, how to run it, configuration, interfaces, deployment, tests, measured cost, status, and known limits.
    3. **Operations:** set up or restore Luna, deploy, Make targets, reboot rule, sharing Luna between sessions, troubleshooting (SSH stalls, GPU display).
    4. **User guide:** controls (from Wyoh's controls reference and cheat sheet), apps, Slate, dictation.
    5. **Decision records:** the decisions that shape the architecture, with their reasons (Sway v0, the gamepad grab, the Mike/Mannie split, CPU before OpenCL, and so on).
  - **(c) Form and place:**
    - Markdown in `docs/` (for example `docs/architecture/`, `docs/components/`), or a `README.md` next to each piece of code (`src/wyoh/README.md` already exists), or both, with an index.
    - Diagrams as Mermaid in the Markdown.
    - Optionally, a published page that gathers it all.
  - **(d) Staying true:** which parts are generated or checked against the code, the way Wyoh's 5.12 checks its controls reference against `Config`. Candidates: MCP tool list, configuration keys, Make targets, protocol messages. A test fails when the doc and the code disagree.
  - **(e) Who writes:**
    - Professor writes everything from the repository;
    - or Professor writes the architecture and the index, and each workline writes its own component pages through a note and a sub-step in its plan (cell rules).
- [ ] 7.3 **Intent** written: [`docs/0703_01_documentation-intent.md`](docs/0703_01_documentation-intent.md), awaiting the user's approval. From the user's choices: structure, page list, templates, generation and checks, sources, order of writing, what is out of scope, acceptance. The user approves it.
- [ ] 7.4 **Write** after `🟩 go Step 7`, in the chosen order; inspect rendered diagrams.
  - *2026-10-11, 🟩 go from the user: "start with the architecture and Wyoh, then stop".* Written: `docs/README.md`, `docs/04_architecture.md`, `docs/10_wyoh.md` (first written under `docs/guide/`, merged into `docs/` at the user's request); five SVG diagrams in `docs/img/` (`luna-machine`, `request-path`, `memory-budget`, `the-cell`, `wyoh-inside`), each rendered to PNG with `scripts/render_svg.py` (Chromium) and inspected, with fixes for overflow and wording. Image prompts for ChatGPT: [`docs/0704_01_image-prompts.md`](docs/0704_01_image-prompts.md). Stopped for review; the user then asked to merge the guide into `docs/` and to continue.
  - *2026-10-11, continued:*
    - the guide was merged into `docs/` (one numbering, `docs/README.md` as the way in);
    - `01_principles.md` was revised: Adam on hold, current roles, the request path as SVG, current boundaries, and a new "Documentation conventions" section; `AGENTS.md` vocabulary was aligned;
    - written: `11_mycroft.md`, `12_mike.md`, `13_mannie.md`, `14_luna.md` and `15_the-cell.md`, with four more SVG diagrams (`mycroft-dictation`, `mike-one-action`, `luna-card`, `step-lifecycle`), rendered and inspected.

    **Stopped for the user's review.** Not yet: operations, user guide, decisions; the workline reviews.
- [ ] 7.5 Acceptance: following the docs alone, a newcomer can explain the architecture, find each component, run it, and know its cost and status. Generated or checked parts pass their tests. Each page names its sources.

### Step 8 — Adam is the user
**Status**: 🧪 In progress (user, 2026-10-31: "c'est mon rôle, ça, Adam").

**Why:** the vocabulary said Adam was "on hold", a human-facing identity not yet assigned. The user states that Adam is their own role in the cell: the human, the one who gives the go. In the novel, Adam Selene is the public face of the committee; in Hebrew, *adam* is "man", from *adamah*, the earth, the dust.

- [ ] 8.1 Align the vocabulary: `AGENTS.md`, `docs/01_principles.md`, `docs/00_the-moon-is-a-harsh-mistress.md`, `docs/15_the-cell.md`, the README; record in `docs/LOGBOOK.md`.
- [ ] 8.2 Tell every session.

### Step 9 — The trailer ends on an opening

*Since 2026-10-31 the videos belong to Hazel's workline: the trailer's sources are in `worklines/hazel/video/trailer/` (renders in `results/hazel/trailer/`), and Steps 9 and 11 continue in `worklines/hazel/plan_hazel.md`.*
**Status**: 🧪 In progress (user, 2026-10-31).

**Why:** the user drops the planned colonisation segment (story-a and story-b are not used). The trailer presents the cell in a fun, lively way, then opens: the adventure starts, follow it. The stories come later, one video per story.

- [ ] 9.1 Replace the speedrun (scene 8) with a short opening ("the adventure begins / follow our adventures"); make the cell's presentation fun, with the ticker on how the cell runs. A sub-agent may do it from a brief.
- [ ] 9.2 Fit the chosen soundtrack (version A, NES-style, `/data/michael/tanstaafllm/video/music-a/`) to the new cut, and bring it into `video/src/` in place of the stop-gap `music.py`.
- [ ] 9.3 Render, inspect frames, commit, push, links.

### Step 10 — Story: the cell at work (case: Mike's Step 12)
**Status**: 🧪 In progress (user, 2026-10-31).

**Why:** the user finds the cell's exchanges interesting and wants them told as a story: who talks to whom, how work is split, what the user (Adam) gives and where they step in, how decisions are taken; an agora rather than a hierarchy. The case is the work the user gave Mike in Step 12 (small talk on Luna), including the Luna slot, Mannie stopping, and the rule changes it triggered.

- [ ] 10.1 **Scribe:** collect the exchanges of the case from Professor's transcript, the plans, `luna-access.md`, the commits and the other sessions (ask them for their side): a dated log of who said what to whom, Adam's interventions, decisions. Output: `docs/1001_01_cell-at-work-log.md`.
- [ ] 10.2 **Story** in `docs/` (next free number), in the house style of the other stories.
- [ ] 10.3 **Animation:** a short, fun, shareable video of the cell at work: the agents, message bubbles, decisions, Adam's go. Same pipeline as the trailer (HTML canvas, Playwright, ffmpeg), NES-style sound.

### Step 11 — Stories as videos, for LinkedIn
**Status**: 📝 Proposed (user, 2026-10-31).

**Why:** the user wants to share the project on LinkedIn: the trailer as the introduction, then one short video per story (the bring-up, text-to-shell, the cell at work, …).

- [ ] 11.1 Agree on a common format (length, opening and closing cards, captions readable on a phone, sound) once the trailer and the first story video exist.
- [ ] 11.2 One video per story, each committed with its sources.
  - *2026-10-31, the user via Mike:* first story video: the bring-up, from the box to the first `ssh luna` (`docs/03`). Handed to a sub-agent with a short brief (`/data/michael/tanstaafllm/video/bringup-pkg/BRIEF.md`, output `bringup-v1/`), 60–90 s, same pipeline and NES-chip sound as the trailer.
- [ ] 11.3 A private screening page on claude.ai for the user's phone: https://claude.ai/artifact/Wqpg9wD9Ew5MunsYFhxqLn (trailer online 2026-10-31; add each story video as it is done). A public page later, by Hazel.

### Step 13 — Say how fresh every record is
**Status**: 📝 Proposal for the user (user, 2026-10-31); nothing applied yet.

**Why:** the worklines accumulate Markdown records, and that is the intended way of working. Records of finished steps are not kept up to date, and they should not be: they say what was true on their date. The risk is that a new agent, or one of us, reads an old record as current. Each record should say, at the top, whether it still holds and how old it is.

**What exists (survey, 2026-10-31):** 150 records in `worklines/*/docs/` (Wyoh 41, Luna 34, Mycroft 26, Mike 25, Professor 14, Mannie 7, Hazel 3). 93 have a `**Status:**` line, but it describes the result ("passed on the reference board"), not whether the record is still current; 66 carry a date; only 3 say they are superseded.

**Proposal:**

1. **One banner line under the title of every record** in `worklines/*/docs/`, kept apart from the existing `**Status:**` line:

   ```markdown
   > **Freshness:** 🟡 historical · **Written:** 2026-10-03 · **Checked:** 2026-10-31 · **Step:** luna 5.2 ✅
   ```

   Four values only:
   - 🟢 **current**: the reference for an open step, or a standing contract, runbook or protocol still in use. Kept up to date.
   - 🟡 **historical**: the record of a finished step. True on its date, not updated. The default once the step is ticked in the plan.
   - 🔴 **superseded by** [the newer record](…): a later record or decision replaces it; the link is mandatory.
   - ⚪ **draft**: a proposal or note not yet acted on.

   **Written** is the record's first commit date; **Checked** is the date someone last confirmed the banner; **Step** names the plan step and its state.
2. **Where it does not apply:** plans (`plan_<name>.md`) are the source of truth and stay as they are; the `docs/` guide pages are living documents and get only a "Checked" date; the stories (`docs/03`, `05`, `06`) are dated narratives and say so in their subtitle already.
3. **The rule for readers**, one line in `AGENTS.md`: a 🟡 or 🔴 record is evidence of what was true then; before acting on it, read the plan and the newest record of that step.
4. **Tooling, so it stays true:** `scripts/doc_freshness.py` proposes each banner from Git (dates), the file's step prefix and the step's checkbox in the plan; Professor reviews the 🟢 and 🔴 cases by hand. A deterministic test in `test/professor/` fails when a record has no banner or a 🔴 without a link. Each workline adds the banner when it writes a record, and switches it to 🟡 when it closes the step.
5. **One commit for the whole pass**, containing only the banners, the `AGENTS.md` line, the script, the test and the LOGBOOK entry, so it is easy to review and to revert.

- [x] 13.1 Proposal written (above).
- [ ] 13.2 The user approves or adjusts it.
- [ ] 13.3 Apply: run the script, review by hand, one commit, push, links; tell every session the rule.

### Step 12 — Move the cell out of Termidor, into an isolated place
**Status**: 📝 Proposed, to discuss and decide with the user (user, 2026-10-31).

**Why:** the cell now has wide freedom (standing commit-and-push routine, Professor's delegated gos), and Termidor is the user's own desk machine with other projects on it. The user wants the agents isolated, so that they can keep that freedom without risk to the rest: either in a virtual machine ("OpenShell", to clarify with the user) or directly on `luna-pi`. No model training in the cell.

**First assessment (2026-10-31, measured):**

| Need | Today on Termidor | `luna-pi` (Pi 4B, 4 × Cortex-A72, 7.6 GiB, 14 GB card) |
|---|---|---|
| Claude Code sessions (6 to 7 at once) | about 1.1 GiB for all sessions and their tools | fits in RAM; Claude Code peaked at 244 MiB there in Mannie's measures |
| Repository, `.venv`, Playwright's Chromium | 440 MB + 474 MB + 1.4 GB | **disk is the limit:** 5.3 GB free on the card; a larger card or a USB SSD would be needed |
| Video renders (Chromium frame capture, ffmpeg) | about 10 min for 86 s | runs, but several times slower |
| Mike's desk studies (models up to 4B, llama.cpp) | yes | slow (a few tokens per second for 4B); the large evaluations would stay elsewhere |
| SSH to Luna, Remote Control | yes | yes, same network |
| PyTorch training (Chat-GBC) | done once | out of scope (the user: no retraining) |

Options to weigh:
- **`luna-pi` as the cell's home:** physical isolation, same arm64 code as Luna; needs storage; heavy jobs (renders, large model evaluations) stay on Termidor or are dropped.
- **A VM on Termidor:** strong isolation without new hardware; Termidor (i5-4590, 8 GB DDR3) would have to give it 4–5 GB, which squeezes the desktop.
- **A container on Termidor** (rootless Podman or similar, only the repository mounted): the lightest, weaker isolation than a VM.
- In every case: credentials scoped to the cell (a GitHub deploy key for this repository only, Claude login), no access to the user's other projects or home.

- [ ] 12.1 Clarify "OpenShell" with the user; list what the agents must reach (GitHub, Luna, `luna-pi`, the network, the desk's `/data` results).
- [ ] 12.2 Decide the target and its storage; plan the move (repository, venv, Playwright, skills, memories, `agents.md`).
- [ ] 12.3 After the go: set up, move one session first (Professor), then the others; keep Termidor for heavy jobs only.

---

## Progress tracking ✅

- ✅ Professor workline established as the project’s coordination and isolation boundary; English translation of the existing partial analysis retained as planning documentation.
- Mycroft — explicitly authorised pre-hardware ASR v0 workline; see worklines/mycroft/plan_mycroft.md.
- 🧪 Step 1 — Decision ledger ready for review.
- 🧪 Step 2 — V0 charter ready for review.
- ⏳ Step 3 — Design the workline map.
- ⏳ Step 4 — Open approved foundation workline(s).
- ⏳ Step 5 — Maintain programme integration.
- 🧪 Step 6 — Omarchy analysis ready for review.
- 📝 Step 7 — Documentation of the software and the architecture: proposed, options for the user.

---

## Time tracking (use `date`) ⏱️

```bash
date
```

### Time log

| Timestamp (`date`) | Update |
|---|---|
| 2026-09-25 | Created draft coordinating-workline plan; no implementation or specialised workline was initiated. |
| 2026-09-25T01:24:13+02:00 | Renamed the coordinating workline from `general` to `professor` (Professor de la Paz); updated its role to maintain cross-workline coordination and isolation. No implementation started. |
| 2026-09-25T02:22:12+02:00 | Green-lit Sections 1 and 2 produced a complete-source decision ledger and a review-ready v0 charter. No subsystem implementation, hardware operation, model download, or benchmark was run. |
| 2026-10-05 | Added Step 6 (Omarchy as an external reference) and ran it on the user's direct instruction. Documentation only; ideas are proposed to Wyoh, Luna, Mycroft and Mannie without opening work there. |
| 2026-10-30 | User: the cell may message directly (rule lifted; skill, `AGENTS.md`, docs 04 and 15, README, all sessions told). User via Wyoh: commit everything, coordinated; sequence set (Mike, Mycroft, Luna, Mannie desk, then Professor with LOGBOOK, `agents.md`, `pyproject.toml`/`uv.lock`; one push at the end). |
| 2026-10-30 | Video: reading-time audit (`video/src/timing.py`, `holds.json`: last text before each cut stays readable; 0.4 s + 0.25–0.30 s per word, min 1 s; Brysbaert 2019, Dehaene, Netflix). Cut now 94 s. Music map `video/music-map.svg`. Two composer sub-agents, then the user's NES 2A03 constraint; the user keeps version A (`/data/michael/tanstaafllm/video/music-a/`), not yet in the repo. Speedrun to be replaced by the story of the cell colonising Luna: two concurrent sub-agents delivered `story-a` (99.5 s) and `story-b` (96.5 s); both send Mike up where the user wants Mannie, so a correction is pending. Repo `music.py` is the stop-gap gap-filling version the user rejected. Added a `video` dependency group (numpy, scipy, soundfile, cairosvg). |
| 2026-10-29 | User: find the Playwright options that let Google accept a manual login (answer: launch the system Chrome with `--remote-debugging-port` and a dedicated profile, attach with `connect_over_cdp`; `michael` repo, `worklines/amazon/scripts/browser.py`). On Luna: Mannie restarted; sudo blocked by Claude Code's auto-mode classifier, not by the system; the user added `Bash(sudo:*)` to Mannie's settings. `vi` → Vim through links in `/usr/local/bin` (Mannie's go). |
| 2026-10-28 | User: the video into the sources. Professor's screenshot-based cut is dropped (user: "c'est horrible"). The sub-agent's video, made from the README and `docs/` only, now lives in `worklines/professor/video/`: `src/` (index.html, capture.py, music.py, build.sh, fonts under OFL, the key art), README and NOTES. `build.sh` now writes to `results/professor/video/<stamp>/`. Rendering checked from the repo copy. The MP4 itself stays out of Git. |
| 2026-10-25 22:25 | Supervised Mike's first run on Luna (4.5): Mannie saved and stopped with its go, Mike ran under the brain lock, and Luna was checked clean afterwards. Result `mike/docs/0405_01`: 3.5 s load, about 300 MiB, at least 562 MiB available, but about 105 s per request. With 4.6, the user decided that LFM2.5-350M is not usable on Luna as it is; Mike returns to desk studies (its Step 8), and Luna is left to Mannie. |
| 2026-10-25 17:30 | User: Mannie on Luna is the operator, and may be messaged directly about Luna operations; no SSH to Luna without its go, and no reboot while it runs. 5.6 confirmed and applied to `AGENTS.md`, `skills/cell-coordination` and `luna-access.md`; all sessions told. Relayed between Mannie (desk), Mannie from Luna and Mycroft: messaging test passed both ways, launcher review, check 1 (no USB-C headset seen on the new root), 8.8 conditions put to the user. |
| 2026-10-25 16:50 | User: a 60-second epic retro trailer for YouTube. Professor's first cut used device screenshots; the user rejected it, and a sub-agent made the kept version from a package of the README, the `docs/` pages and the key art, with no storyboard (`/data/michael/tanstaafllm/video/package-20261025/BRIEF.md`). |
| 2026-10-25 15:20 | User: reduce the gaps between the CV (`michael` repository) and the public presentation, make the README slightly more serious, add banners from the wallpaper. Gaps in `docs/0505_01`; README rewritten; two banners cropped and inspected. Not committed or pushed. |
| 2026-10-25 | Mannie read both notes (plan_mannie 7.2b): the current image boots to text mode only, since Sway needs ArchR's libmali stack (Panfrost failed). User choice put by Mannie: write the text-mode root now, or first add Wyoh's and Mycroft's packages (125, 161 MB) and ArchR's Mali stack. Root SSH by key stays. |
| 2026-10-25 | Replies: Wyoh closed 12.3 and 12.4, kept the rest open as 12.5, added Step 13 and note `mannie/docs/0702_01` (main risk: the Mali/libmali path). Mycroft closed 7.5, recorded the 8.7 profile (code defaults wait for a go), 8.8 half met, 9.3 adopted with the licence unconfirmed; note `mannie/docs/0700_02`. Both notes pointed out to Mannie before 7.3. |
| 2026-10-25 | User: check progress, notably Mycroft ↔ Wyoh. New sessions identified (mycroft e6, luna e0, wyoh 8e, mike 02). Kroko in the Slate was delivered on 2026-10-15; asked Mycroft (7.5, 8.7, 8.8, 9.3) and Wyoh (12.3, 12.4) to close what the evidence supports in their plans. Relayed Luna's note `0000_04` to Wyoh, Mycroft and Mike, with the user's 2026-10-25 decision to replace ArchR's root (Mannie Step 7; card backup running, Luna off, held by Mannie). Asked Wyoh and Mycroft to note for Mannie what they need on the new root; told Luna that its 7.1 is carried out in Mannie's line. |
| 2026-10-25 | Mannie: ArchR's `/usr/bin/sudo` is a shim (runs as the caller, no sudoers), so `michael` has no root access and 7.0's "passwordless sudo" does not exist (the 2026-10-15 logbook already said it was not in place); real sudo or doas put to the user. git 2.56.0 installed on Luna from Arch Linux ARM (signatures checked, repacked around ArchR's locale link), plan_mannie 6.2. Luna's note `0700_01` still to be corrected, by whoever owns Luna's records after 5.6. |
| 2026-10-25 | Mannie reported the user's decisions (Mannie operates Luna; branch `cell/mannie` with PRs); recorded as 5.6, boundary edits waiting for the user's confirmation. |
| 2026-10-25 | Mannie's request recorded as 5.5 (GitHub issues as the channel from Luna; cell-coordination change pending the user). No action taken. |
| 2026-10-11 23:26 | Guide merged into `docs/`, principles revised, component pages 11–15 written with four more diagrams. Stopped for review. |
| 2026-10-11 23:30 | Step 7 green-lit (architecture and Wyoh first): three guide pages, five SVG diagrams rendered and inspected, and image prompts. Stopped for review. |
| 2026-10-11 22:30 | Added Step 7 (documentation of the software produced and of the architecture) at the user's request. Options listed for the user; the intent follows their choices. Documentation only. |
| 2026-10-09 22:30 | User away until midnight: Professor manages the cell and decides in the user's place (Step 5.4). Log: `docs/0503_01_delegated-coordination-log-2026-10-09.md`. |
| 2026-10-09 | Step 5 integration work: the graphical-apps shortlist was selected by the user and sent to Wyoh as a coordination note. Who assembles the apps is not decided; Professor implements nothing. |

---

## Workline artifacts

- `worklines/professor/docs/0001_01_initial_discussion.md` — complete initial discussion transcript (155 messages; source evidence).
- `worklines/professor/docs/0000_01_initial_discussion_analysis_fr.md` — archived French version of the earlier partial synthesis.
- `worklines/professor/docs/0001_01_initial_discussion_analysis.md` — English translation of the earlier partial synthesis, with its scope limitation stated.
- `worklines/professor/docs/0101_01_decision-ledger.md` — authoritative reconciliation of the complete discussion with active repository decisions.
- `worklines/professor/docs/0201_01_v0-charter.md` — review-ready boundary, success measures, and exclusions for the immediate v0.
- `worklines/mycroft/plan_mycroft.md` — explicitly authorised Mycroft pre-hardware ASR v0 plan.

## Shared-discussion integration — 2026-09-25

The shared discussion expands Mycroft to an input-and-composition capability while retaining its measured ASR slice as a context-free baseline. Professor records the cross-workline split: Mycroft owns composition, Wyoh owns scoped observable context, and neither receives execution authority through context alone. Mycroft candidate, harness, and selection criteria are reopened; no implementation is implied.

See [the cleaned decision record](docs/0102_03_shared-chatgpt-options-decision.md).

### Amendment log

| Timestamp (`date`) | Update |
|---|---|
| 2026-09-25T23:10:00+02:00 | Captured and cleaned the shared discussion with the repository scraper; recorded its cross-workline consequences. |

## Additional workline artifacts

- `worklines/professor/docs/0102_02_shared-chatgpt-options-source.md` — canonical raw export.
- `worklines/professor/docs/0102_03_shared-chatgpt-options-decision.md` — cleaned decisions and owner consequences.
- `worklines/professor/docs/0601_01_omarchy-analysis.md` — Step 6: Omarchy compared with TANSTAAFLLM for the R36 Ultra; ideas classified adopt/adapt/reject with proposed owners.
- `worklines/wyoh/docs/0900_01_note-from-professor-graphical-apps.md` — note to Wyoh: the user's selection of graphical apps, the menu clean-up, the search-engine caveat, and questions about who assembles the apps.
- `worklines/professor/docs/0503_01_delegated-coordination-log-2026-10-09.md` — log of the instructions Professor sent and the decisions it took while the user was away (2026-10-09, 22:30 to midnight).
- `worklines/professor/docs/0703_01_documentation-intent.md` — Step 7 intent: the structure, reading budget, SVG style, tone and stages of the project guide.
- `docs/` — the project documentation (Step 7): `README.md` (navigation), `04_architecture.md`, `10_wyoh.md`…, diagrams in `docs/img/`.
- `worklines/professor/docs/0704_01_image-prompts.md` — ChatGPT prompts for the guide's illustrations.
- `scripts/render_svg.py` — renders SVG diagrams to PNG with Chromium, for visual review.
