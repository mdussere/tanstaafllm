---
**Status**: 📋 Draft
**Date**: 2026-11-05
**Priority**: Medium
**Maintained**: Yes
---

# Bill — shared memory and knowledge circulation (workline `bill`)

## Overview

This is a field notebook, not a blueprint. Bill will learn from one small, inspectable pilot at a time: first discover what agent memory is actually accessible locally and in the Cloud, then understand the shape of one Luna raw session and its Claude-managed memory, then make a local-only atomization comparison against two bounded days, then decide whether to save it. Every step ends in a record of what was observed, what could not be observed, and the next smallest action.

The destination is Adam's new private repository, **Tinkstaff LLM Biverse** (name as supplied). Raw material never enters this public repository. Bill does not manage the cell or replace Adam's approval authority or Professor's coordination role.

## Workline directory layout

- Plan (this file): `worklines/bill/plan_bill.md`
- Produced records: `worklines/bill/docs/`
- Future scripts, only after a green light: `worklines/bill/scripts/`

## Goals ✅

- See the real local and Cloud-agent memory surfaces before designing around assumptions.
- Understand the raw Luna JSONL's size, record shape, natural cut points and relationship to Claude Code's curated memory before deciding how to store it.
- Compare two small, human-readable atomizations against the same local Luna source without exporting it.
- Preserve one authentic Luna-agent memory snapshot only if the comparison makes that next step useful.
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
**Status**: ✅ Done (2026-11-05)

- [x] 2.1 Read the identified Luna JSONL in place and measure bytes, record count, record/event types, field shape, timestamps, roles and tool/subagent/compaction markers. The source was not modified or copied.
- [x] 2.2 Identify natural boundaries: session start/end, calendar day, user request → assistant response/tool-result cycle, explicit summary/compaction and UUID-parent causal links.
- [x] 2.3 Read Claude Code's project `memory/` files for the same project; distinguish the maintained memory layer from raw history, and classify what it retains without publishing raw text.
- [x] 2.4 Write [the Luna JSONL anatomy](docs/0201_01_luna-jsonl-anatomy.md): a non-sensitive structural analysis, candidate segmentation rule, and storage/exploitation recommendation.
- [x] 2.5 Acceptance: the observed structure supports retaining one immutable JSONL, a separate derived turn index, and a first atomization unit bounded by a user request and its causally linked assistant/tool sequence.
- [x] 2.6 Map the actual JSONL object families and their top-level/nested field shapes by `type`, and explain what is and is not shared between rows. Update the anatomy record with no message content.
- [x] 2.7 Acceptance: Adam can distinguish JSONL from JSON-LD and understand the data carried by conversation, tool, attachment, title, request, queue, file-history and summary rows.

### Step 3 — Compare a local two-day atomization
**Status**: ✅ Done (2026-11-05)

- [x] 3.1 Bound the trial to the first two source timestamp days, `2026-10-03` and `2026-10-04` (1,137 event rows), while leaving the source unchanged and keeping every derived result under ignored `results/`.
- [x] 3.2 Give the same task to GPT-6 Luna and GPT-6.1 Terra: turn several causally related events into concise Markdown sequence atoms with a beginning, an end, source references and explicit uncertainty.
- [x] 3.3 Preserve each model's Markdown and run notes locally; capture start/finish time, model name, scope and validation result. Do not commit raw or derived content to this repository or write to Tinkstaff LLM Biverse.
- [x] 3.4 Compare only observable trial properties (elapsed time, atom count, traceability and readability); state what the trial cannot establish about general memory quality in [the comparison record](docs/0304_01_local-atomization-comparison.md).
- [x] 3.5 Acceptance: two independently produced, locally retained atom lists cover the same two-day scope and can be checked for a clear sequence boundary and source trace, without public disclosure or private-repository writes.

### Step 4 — Save one Luna snapshot
**Status**: ⏳ Pending

- [ ] 4.1 State exactly what “complete” means for the selected Luna source, using Step 2's observed boundaries and the Step 3 trial outcome.
- [ ] 4.2 Export its accessible raw artifact immutably, with a small manifest stating method, timestamps, coverage, omissions and a content checksum.
- [ ] 4.3 Inspect the export for destination and privacy safety, then commit it to **Tinkstaff LLM Biverse**. The public workline record contains only non-sensitive metadata and the private commit identifier.
- [ ] 4.4 Acceptance: the private commit can be checked out and its manifest reproduces the claimed scope without exposing raw content publicly.

### Step 5 — Review a first atom set
**Status**: ⏳ Pending

- [ ] 5.1 Select a bounded, representative list from the private snapshot or a follow-up trial; keep the raw source unchanged.
- [ ] 5.2 Review it with Adam: what is useful, misleading, missing or too costly to retain?
- [ ] 5.3 Acceptance: the review can trace every retained atom to the raw snapshot and decides the next smallest experiment. No embedding, model or CI workflow is assumed.

### Step 6 — Continue only from evidence
**Status**: ⏳ Pending

- [ ] 6.1 Update this plan with the pilot outcome and one approved next action.
- [ ] 6.2 Acceptance: the next action is bounded by observed access, privacy and usefulness rather than a general-purpose memory-system design.

---

## Progress tracking ✅

- ✅ Step 1 — Claude Code local-memory inventory; the Luna raw-session candidate is identified, with private-destination access still required before export.
- ✅ Step 2 — inspect the Luna JSONL and Claude memory layers in place; structure, schema families, storage and segmentation recommendation recorded.
- ✅ Step 3 — two local atomizations of the first two Luna days validated; no export.
- ⏳ Step 4 — export and preserve one Luna snapshot privately, only if useful after the trial.
- ⏳ Step 5 — review a bounded first atom set with Adam.
- ⏳ Step 6 — choose one evidence-led continuation.

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
| 2026-11-05 | Step 2 completed: the Luna source is a 13,451,993-byte, 3,714-record event journal over 13 days, not a simple alternating chat log. Preserve one immutable JSONL; derive request/response/tool units from UUID-parent links and use day/compaction boundaries for navigation. Claude's small managed-memory layer is useful but needs provenance and freshness checks. |
| 2026-11-05 | Adam asked for the concrete JSONL schema explanation rather than aggregate counts. Step 2 reopened to map record families and field shapes without emitting message content. |
| 2026-11-05 | Step 2 schema clarification completed: every row has `type`, but there is no uniform row schema or JSON-LD vocabulary. Added the actual conversation, tool, attachment, API, lifecycle, queue, file-history and cost object families plus nested message/content shapes to the anatomy record. |
| 2026-11-05 | Adam green-lit a bounded local comparison before any private export: GPT-6 Luna and GPT-6.1 Terra receive the same first two Luna timestamp days (`2026-10-03`–`2026-10-04`) and produce compact, traceable Markdown sequence atoms. Step 3 is in progress; results stay under ignored `results/` and neither raw nor derived content will be committed. |
| 2026-11-05 | Step 3 completed: both models produced locally retained atom lists for the same 1,137-row scope. GPT-6 Luna made 4 broader atoms in 54 seconds; GPT-6.1 Terra made 12 finer-grained atoms in 46 seconds. The shape validator accepted both; the comparison record notes that this does not validate source fidelity or establish a general model-quality ranking. No private-repository write or public memory-content commit occurred. |

---

## Workline artifacts

- [Pre-plan foundation](docs/0000_01_bill-bobiverse-foundation.md) — earlier direction and safeguards; ⚪ draft background evidence, not the pilot plan.
- [Codex surface inventory](docs/0102_01_memory-surface-inventory.md) — historical background observation, retained for a later Codex-memory export.
- [Claude Code memory-surface record](docs/0102_02_claude-code-memory-surface.md) — Step 1's current source map and selected Luna raw-session candidate; 🟢 current.
- [Luna JSONL anatomy](docs/0201_01_luna-jsonl-anatomy.md) — completed Step 2 structure, cut-point, storage and Claude-memory analysis; 🟢 current.
- [Atomization-trial contract](../../../test/bill/luna_atomization_trial.feature) — the local-only, two-model Step 3 observable contract; raw and derived trial material remains ignored.
- [Local atomization comparison](docs/0304_01_local-atomization-comparison.md) — Step 3's non-sensitive comparison and limits; 🟢 current.
