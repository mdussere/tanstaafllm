---
**Status**: 📋 Draft
**Date**: 2026-11-05
**Maintained**: Yes
---

# Bill — shared memory and knowledge circulation (workline `bill`)

## Overview

Bill is a proposed TANSTAAFLLM workline inspired by Bill in Dennis E. Taylor's *Bobiverse*: maintaining the shared infrastructure through which autonomous agents exchange knowledge and retain useful history. This is an initial mandate for discussion, not an approved architecture or implementation.

Adam is the human project owner. Professor coordinates programme direction and workline boundaries; Bill focuses specifically on continuity of information between agents, sessions and worklines, without becoming their manager.

## Workline directory

- Plan: `worklines/bill/plan_bill.md`
- Future working documents: `worklines/bill/docs/`

## Objectives (exploratory)

- Investigate durable, reviewable memory that survives chat context limits and session changes.
- Distinguish individual agent history, shared project knowledge, decisions, and transient conversation context.
- Explore how agents discover, share, correct and trace knowledge without erasing their individual perspectives.
- Clarify how existing Git branches, workline plans, issues and other project artifacts might participate in that memory.

## Constraints

- Do not treat every conversation as an authoritative fact or project decision.
- Preserve provenance and distinguish observations, proposals, approvals and superseded information.
- Do not silently rewrite other worklines or merge changes without authorization.
- No implementation, service selection or migration is approved by this document.

## Initial TODO

- [ ] Map current memory and knowledge flows across ChatGPT conversations, GitHub and TANSTAAFLLM agents.
- [ ] Identify what is lost on session turnover and which information must remain recoverable.
- [x] Discuss an individual-versus-shared memory model with Adam (architecture direction recorded; implementation details remain open).
- [ ] Define ownership, update rules, provenance and conflict resolution before choosing storage or tooling.

## Latest checkpoint (2026-11-05)

- Defined distinct persistent **roles** and potentially concurrent provider-specific agent instances; one timestamp/provider/UUID-scoped raw directory per agent instance inside a role namespace.
- Raw memory **dump** should be an incremental, immutable export. Prefer deterministic harness extraction where possible; ChatGPT/cloud exceptions need a separate adapter or skill.
- Proposed private **TANSTAAFLLM Bobiverse** memory repository and role branches; selective promotion into shared knowledge must exclude raw files.
- Proposed **GitHub Actions** incremental atomization, embedding, SECNA-style clustering and evidence-backed graph relations. Free private-CI allowances, quality and concurrency remain unverified.
- Retain the science-fiction framing: **Bobiverse/Bill** as names, **Altered Carbon** for stack/dump/sleeve, and **Pluribus** for hive knowledge without loss of identities.
- Potential separate **Bobiverse tooling spin-off** for harness extractors and CI distillation if justified; not authorized or created yet.
- Detailed decisions and open questions: [foundation document](docs/0100_bill_bobiverse_foundation.md).

### Next design tasks (no implementation green light)

- [ ] Confirm the private repository's verified name, access and creation when Adam creates it.
- [ ] Design raw export contracts, per-instance metadata and deterministic Claude Code extraction, plus ChatGPT limitations.
- [ ] Design safe role-branch-to-common promotion through PRs without including raw material.
- [ ] Benchmark atomization fidelity and Github Actions private CI resources before enabling workflows.
- [ ] Decide whether reusable tooling warrants a Bobiverse spin-off.

## Status

Workline initiated by Adam on 2026-11-05. Discussion and framing only; next technical steps require explicit direction.
