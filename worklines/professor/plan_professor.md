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
**Status**: ⏳ Pending

- [ ] 1.1 Read the complete initial transcript and produce a decision ledger: confirmed decisions, strong preferences, hypotheses, and discarded ideas.
- [ ] 1.2 Correct or supersede the current translated analysis where the incomplete extract omitted material decisions.
- [ ] 1.3 Identify conflicts needing your arbitration, including project naming, primary v0 purpose, device roles, and component names.
- [ ] 1.4 Acceptance: you approve a concise decision ledger and an explicit open-questions list.

### Step 2 — Define the v0 charter and system boundaries
**Status**: ⏳ Pending

- [ ] 2.1 Choose one primary v0 outcome: local intelligence experiment, portable development companion, frugal system assistant, voice interaction, or another explicitly defined use case.
- [ ] 2.2 Define what runs on the desktop, `luna-pi`, Luna, and remote services; identify mandatory offline and latency expectations.
- [ ] 2.3 State success measures: usability, memory ceiling, responsiveness, battery/thermal constraints, reproducibility, and learning goals.
- [ ] 2.4 Acceptance: a one-page charter excludes more scope than it admits and makes v0 testable.

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

---

## Progress tracking ✅

- ✅ Professor workline established as the project’s coordination and isolation boundary; English translation of the existing partial analysis retained as planning documentation.
- Mycroft — explicitly authorised pre-hardware ASR v0 workline; see worklines/mycroft/plan_mycroft.md.
- ⏳ Step 1 — Reconcile the complete decision baseline.
- ⏳ Step 2 — Define the v0 charter and system boundaries.
- ⏳ Step 3 — Design the workline map.
- ⏳ Step 4 — Open approved foundation workline(s).
- ⏳ Step 5 — Maintain programme integration.

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

---

## Workline artifacts

- `worklines/professor/docs/0001_01_initial_discussion.md` — complete initial discussion transcript (155 messages; source evidence).
- `worklines/professor/docs/0000_01_initial_discussion_analysis_fr.md` — archived French version of the earlier partial synthesis.
- `worklines/professor/docs/0001_01_initial_discussion_analysis.md` — English translation of that synthesis, with its scope limitation stated.
- `worklines/mycroft/plan_mycroft.md` — explicitly authorised Mycroft pre-hardware ASR v0 plan.
