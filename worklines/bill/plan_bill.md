---
**Status**: 📋 Draft
**Date**: 2026-11-05
**Priority**: Medium
**Maintained**: Yes
---

# Bill — shared memory and knowledge circulation (workline `bill`)

## Overview

This is a field notebook, not a blueprint. Bill will learn from one small, inspectable pilot at a time: first discover what agent memory is actually accessible locally and in the Cloud, then understand the shape of one Luna raw session and its Claude-managed memory, then save it, then see what useful atoms can be made from it. Every step ends in a record of what was observed, what could not be observed, and the next smallest action.

The destination is Adam's new private repository, **Tinkstaff LLM Biverse** (name as supplied). Raw material never enters this public repository. Bill does not manage the cell or replace Adam's approval authority or Professor's coordination role.

## Workline directory layout

- Plan (this file): `worklines/bill/plan_bill.md`
- Produced records: `worklines/bill/docs/`
- Future scripts, only after a green light: `worklines/bill/scripts/`

## Goals ✅

- See the real local and Cloud-agent memory surfaces before designing around assumptions.
- Understand the raw Luna JSONL's size, record shape, natural cut points and relationship to Claude Code's curated memory before deciding how to store it.
- Preserve one authentic Luna-agent memory snapshot, with method and coverage stated honestly.
- Try a small, human-readable first atomization against that source.
- Let the next step follow evidence from the pilot rather than a premature architecture.

## Non-goals ❌

- Acting as Professor, changing another workline's plan, or arbitrating cross-workline decisions.
- Treating chat transcripts, agent summaries, embeddings or clusters as automatically authoritative.
- Publishing raw conversations, personal data, credentials or private memory to the public TANSTAAFLLM repository.
- Turning this first pilot into a background service, CI pipeline, vector store, model selection, or migration programme.

## Working rules

- Adam owns approvals and disclosure decisions. Bill records and preserves; it does not silently collect, interpret, or publish another agent's history.
- The private repository exists according to Adam. Its exact URL, connected access and default branch must be observed before the first write.
- “Raw” means the original accessible session artifact, not an LLM-made summary. Every export states source, target agent, time, extraction method, coverage and known omissions.
- The first target is the **Luna** agent/workline. We choose no general directory layout or automation until the pilot shows what the source actually provides.
- The previous [foundation record](docs/0000_01_bill-bobiverse-foundation.md) remains background evidence; this pilot plan is the current operational source of truth.

## Risks / constraints

- A Cloud harness may expose only a partial history. A partial export is useful only when labelled partial.
- Raw memory can contain private data or credentials. Inspect the destination and the exact files before copying; never use the public TANSTAAFLLM repository as a staging area.
- An atom is a claim about a source, not a fact merely because it was extracted. The first pass is manual and traceable.
- We stop after each step to update the plan from the result rather than filling in imagined future work.

## 🚦 Green light protocol

- Planning and documentation are allowed by default. External-account actions, writing to the private repository, extraction, ingestion, model downloads and automation require Adam's explicit **`🟩 go Step N`**.
- A step may not claim completion without its listed acceptance criteria and a linked, freshness-labelled record under `docs/`.
- If scope changes materially, update this plan first and add a dated entry to `docs/LOGBOOK.md`.

## Plan steps (no implementation until green light)

### Step 1 — See what Claude Code leaves locally
**Status**: ✅ Done (2026-11-05)

- [x] 1.1 Probe connected access to **Tinkstaff LLM Biverse** without writing to it. Result: it is not visible through the currently connected GitHub account; its exact URL, owner or connector permission is still needed before a private write.
- [x] 1.2 Record the non-target Codex surface and access result in [the first inventory](docs/0102_01_memory-surface-inventory.md). This did not inspect Claude Code.
- [x] 1.3 Locate Claude Code's on-disk session, project and archive artifacts; record paths, file types, timestamps, sizes and identity metadata only. Do not read transcript bodies or copy raw material.
- [x] 1.4 Write [the Claude Code memory-surface record](docs/0102_02_claude-code-memory-surface.md) with the observed surface, coverage limits and the exact Luna candidate.
- [x] 1.5 Acceptance: Adam can see precisely what Claude Code retains on this disk, what is safe to export, and which identified record is the Luna candidate; the private-destination blocker remains explicit.

### Step 2 — Read the shape of one Luna memory
**Status**: ⏳ Pending

 - [ ] 2.1 Read the identified Luna JSONL in place and measure bytes, record count, record/event types, field shape, timestamps, roles and tool/subagent/compaction markers. Do not modify or copy it.
 - [ ] 2.2 Identify natural boundaries: session start/end, calendar day, user request → assistant response/tool-result cycle, explicit summary/compaction and any other actual stable identifier.
 - [ ] 2.3 Read Claude Code's project `memory/` files for the same project; distinguish the maintained memory layer from raw history, and classify what it retains without publishing private text.
 - [ ] 2.4 Write `docs/0201_01_luna-jsonl-anatomy.md`: a non-sensitive structural analysis, candidate segmentation rule, and storage/exploitation recommendation. It must not quote raw content or include credentials.
 - [ ] 2.5 Acceptance: Adam can decide whether to retain one immutable JSONL, split it, compress it, derive an index, and what first atomization unit to use—based on observed structure, not guesswork.

### Step 3 — Save one Luna snapshot
**Status**: ⏳ Pending

- [ ] 3.1 State exactly what “complete” means for the selected Luna source, using Step 2's observed boundaries.
- [ ] 3.2 Export its accessible raw artifact immutably, with a small manifest stating method, timestamps, coverage, omissions and a content checksum.
- [ ] 3.3 Inspect the export for destination and privacy safety, then commit it to **Tinkstaff LLM Biverse**. The public workline record contains only non-sensitive metadata and the private commit identifier.
- [ ] 3.4 Acceptance: the private commit can be checked out and its manifest reproduces the claimed scope without exposing raw content publicly.

### Step 4 — Make the first atoms
**Status**: ⏳ Pending

- [ ] 4.1 Take a bounded, representative portion of the private Luna snapshot; keep the raw source unchanged.
- [ ] 4.2 Produce a small manual atom list. Each atom says what it claims, its source reference, type (observation, decision, request, proposal or correction) and uncertainty.
- [ ] 4.3 Review the list with Adam: what is useful, misleading, missing or too costly to retain?
- [ ] 4.4 Acceptance: the review can trace every atom to the raw snapshot and decides the next smallest experiment. No embedding, model or CI workflow is assumed.

### Step 5 — Continue only from evidence
**Status**: ⏳ Pending

- [ ] 5.1 Update this plan with the pilot outcome and one approved next action.
- [ ] 5.2 Acceptance: the next action is bounded by observed access, privacy and usefulness rather than a general-purpose memory-system design.

---

## Progress tracking ✅

- ✅ Step 1 — Claude Code local-memory inventory; the Luna raw-session candidate is identified, with private-destination access still required before export.
- ⏳ Step 2 — inspect the Luna JSONL and Claude memory layers in place.
- ⏳ Step 3 — export and preserve one Luna snapshot privately.
- ⏳ Step 4 — manually atomize a bounded Luna excerpt.
- ⏳ Step 5 — choose one evidence-led continuation.

---

## Time tracking (use `date`) ⏱️

```bash
date
```

### Time log

| Timestamp (`date`) | Update |
|---|---|
| 2026-11-05 | Adam initiated Bill for durable shared memory and knowledge circulation; the initial foundation was recorded as planning-only direction. |
| 2026-11-05 | Reworked this plan to the repository workline template: scope, non-goals, risks, step-level acceptance criteria, green-light boundary, progress tracking and linked pre-plan evidence. No implementation or tests were run. |
| 2026-11-05 | Adam created **Tinkstaff LLM Biverse** and redirected Bill from a broad architecture plan to an incremental pilot: inventory accessible local/Cloud memory, save one Luna snapshot privately, then inspect a first atomization. |
| 2026-11-05 | Step 1 completed: recorded local Codex JSONL session surfaces, empty Codex Cloud task listing for the current account, and the absence of the new private repository from the connected GitHub account. No transcript was read, copied or exported. |
| 2026-11-05 | Adam corrected the target: inspect what **Claude Code** leaves on disk, not Codex. Step 1 reopened for a Claude Code metadata-only inventory; no transcript export is authorised. |
| 2026-11-05 | Step 1 completed after the correction: identified Claude Code's raw project JSONL sessions, curated project memory, global history and small session metadata. The `luna` workline maps to the `tanstfaafllm-e0` raw JSONL candidate. No source body was opened or copied. |
| 2026-11-05 | Adam asked for source anatomy before preservation: a read-only analysis of the Luna JSONL's size, record structure and natural cut points, plus Claude Code's curated memory layer. Added as the new Step 2; private export and atomization move to Steps 3–4. |

---

## Workline artifacts

- [Pre-plan foundation](docs/0000_01_bill-bobiverse-foundation.md) — earlier direction and safeguards; ⚪ draft background evidence, not the pilot plan.
- [Codex surface inventory](docs/0102_01_memory-surface-inventory.md) — historical background observation, retained for a later Codex-memory export.
- [Claude Code memory-surface record](docs/0102_02_claude-code-memory-surface.md) — Step 1's current source map and selected Luna raw-session candidate; 🟢 current.
- `docs/0201_01_luna-jsonl-anatomy.md` — planned Step 2 structural and memory-layer analysis; no raw text in the public record.
