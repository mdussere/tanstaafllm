---
**Status**: 📋 Draft
**Date**: 2026-11-05
**Priority**: Medium
**Maintained**: Yes
---

# Bill — shared memory and knowledge circulation (workline `bill`)

## Overview

Bill investigates durable, reviewable memory that lets independently evolving TANSTAAFLLM roles retain and exchange useful knowledge across chat-context limits and session turnover. Its scope is the information-continuity layer: it does not manage the cell or replace the authority of Adam or Professor.

Done means Adam can review a provenance- and privacy-aware design for a private Bobiverse repository, role-local raw archives, and selectively promoted shared knowledge. This plan authorises planning and documentation only; it does not authorise a repository, workflow, storage service, extractor, model, or migration.

## Workline directory layout

- Plan (this file): `worklines/bill/plan_bill.md`
- Produced records: `worklines/bill/docs/`
- Future scripts, only after a green light: `worklines/bill/scripts/`

## Goals ✅

- Map what durable knowledge exists today, who owns it, and what is lost when a session ends.
- Define clear boundaries between raw history, role-local memory, curated shared knowledge, and public project records.
- Make every retained claim traceable to evidence, status, visibility and supersession history.
- Design a reviewable, privacy-preserving exchange path between role-local and shared knowledge.

## Non-goals ❌

- Acting as Professor, changing another workline's plan, or arbitrating cross-workline decisions.
- Treating chat transcripts, agent summaries, embeddings or clusters as automatically authoritative.
- Publishing raw conversations, personal data, credentials or private memory to the public TANSTAAFLLM repository.
- Creating the private Bobiverse repository, enabling GitHub Actions, implementing an exporter or ingestion pipeline, selecting a model, or migrating data without a specific green light.

## Key decisions / assumptions

- Adam owns approvals and disclosure decisions; Professor remains the programme-level coordinator. Bill is the knowledge-continuity steward, not the cell manager.
- The proposed private repository is named **TANSTAAFLLM Bobiverse**. Its slug, access model and existence are unverified until Adam creates it.
- Git is the proposed durable foundation. Raw records are private by default and must remain distinct from derived indexes and curated knowledge.
- Persistent roles may have concurrent, provider-specific agent instances. A proposed raw path is `<role>/raw/<start-or-first-dump-UTC>_<provider>_<uuid>/`; these are design hypotheses, not an adopted contract.
- The initial direction and unresolved questions are evidence, not an implementation mandate: [foundation record](docs/0000_01_bill-bobiverse-foundation.md).

## Risks / constraints

- **Privacy and disclosure:** derived summaries or pull requests can leak raw private material. Classify visibility and require review before promotion.
- **Provenance loss:** an atom, embedding or cluster can be mistaken for a verified fact. Preserve immutable source links and status markers.
- **False completeness:** harnesses expose different degrees of session history. Each exporter must declare coverage, omissions and cursors.
- **CI assumptions:** private GitHub Actions availability, limits, model-download costs and concurrency are unverified. Measure them before adopting CI processing.
- **Scope creep:** memory tooling can become a system of record or a new runtime. Keep it separate from Luna/Mike/Mannie implementation until explicit decisions are made.

## 🚦 Green light protocol

- Planning and documentation are allowed by default. Implementation, private-repository creation, external-account actions, extraction, ingestion, model downloads, CI workflows and data migration require Adam's explicit **`🟩 go Step N`**.
- A step may not claim completion without its listed acceptance criteria and a linked, freshness-labelled record under `docs/`.
- If scope changes materially, update this plan first and add a dated entry to `docs/LOGBOOK.md`.

## Plan steps (no implementation until green light)

### Step 1 — Map current knowledge flows and loss points
**Status**: 🧪 In progress

- [x] 1.1 Record the founding direction, boundaries and open questions in the pre-plan [foundation record](docs/0000_01_bill-bobiverse-foundation.md).
- [ ] 1.2 Inventory ChatGPT conversations, GitHub, Git branches, workline plans, records and issues as possible knowledge sources; state the owner, visibility, provenance and session-turnover loss for each.
- [ ] 1.3 Produce a current, freshness-labelled knowledge-flow map in `docs/0102_01_knowledge-flow-map.md`.
- [ ] 1.4 Acceptance: the map distinguishes observed facts from proposals, names every unverified access limitation, and contains no private raw material.

### Step 2 — Define the memory and provenance contract
**Status**: ⏳ Pending

- [ ] 2.1 Define candidate record fields for source, author/role/instance, event and ingestion time, visibility, status, confidence, revision and supersession.
- [ ] 2.2 Define correction, revocation, retention and deletion semantics for raw and derived material.
- [ ] 2.3 Define the boundary among raw history, individual memory, consolidated memory and shared knowledge, including what cannot be promoted automatically.
- [ ] 2.4 Acceptance: a reviewable design record explains ownership and conflict resolution without selecting a storage product or ingesting data.

### Step 3 — Design safe exchange and processing options
**Status**: ⏳ Pending

- [ ] 3.1 Design role-branch-to-common promotion that prevents raw files from entering reviewable shared pull requests.
- [ ] 3.2 Specify candidate raw-export adapter contracts, including deterministic Claude Code extraction and declared ChatGPT coverage limitations.
- [ ] 3.3 Assess GitHub Actions feasibility: private CI entitlement, runner resources, security, idempotence, concurrency and artifact/index retention.
- [ ] 3.4 Define evidence-based evaluation criteria for atomization, embeddings, SECNA-style clustering and relation graphs; do not select a model yet.
- [ ] 3.5 Acceptance: the options record names the smallest useful next experiment, its privacy controls, measurable success criteria and cost/resource bounds.

### Step 4 — Prepare an implementation decision
**Status**: ⏳ Pending

- [ ] 4.1 Consolidate the completed design records into an implementation proposal with explicit alternatives, residual risks and an ownership matrix.
- [ ] 4.2 Ask Adam to decide whether to create the private repository and, separately, whether to green-light a bounded implementation step.
- [ ] 4.3 Acceptance: no repository or automation is created before Adam's explicit decision; the proposal can be reviewed without access to raw private memory.

---

## Progress tracking ✅

- 🧪 Step 1 — founding direction captured; current-flow mapping remains open.
- ⏳ Step 2 — memory and provenance contract.
- ⏳ Step 3 — safe exchange and processing options.
- ⏳ Step 4 — implementation decision proposal.

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

---

## Workline artifacts

- [Pre-plan foundation](docs/0000_01_bill-bobiverse-foundation.md) — Adam's initial direction, proposed memory layers, safeguards, CI concepts and open questions; ⚪ draft evidence, not an approved architecture.
