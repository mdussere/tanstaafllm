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
- [ ] Discuss an individual-versus-shared memory model with Adam.
- [ ] Define ownership, update rules, provenance and conflict resolution before choosing storage or tooling.

## Status

Workline initiated by Adam on 2026-11-05. Discussion and framing only; next technical steps require explicit direction.
