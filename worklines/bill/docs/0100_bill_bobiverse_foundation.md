---
status: foundation-draft
date: 2026-11-05
workline: bill
branch: cell/bill
proposed_private_repository_name: "TANSTAAFLLM Bobiverse"
---

# Bill foundation — TANSTAAFLLM Bobiverse

## Purpose

This document carries forward Adam's discussions about durable memory for TANSTAAFLLM. **Bill** takes inspiration from Bill in Dennis E. Taylor's *Bobiverse*: the steward of shared infrastructure, communication and accumulated knowledge between independently evolving agents. Bill is **not** the boss of the other agents. Professor remains responsible for programme-level coordination and decisions; Adam is the human owner.

This is a foundation for discussion and review, **not** an implementation mandate. It intentionally contains no private transcripts or sensitive memories: this file lives in the public TANSTAAFLLM repository.

## Decisions and explicit preferences already expressed by Adam

1. A **separate, private GitHub repository** is needed for agent memory; raw personal conversations and Mike's memories **must not be placed in the public** `mdussere/tanstaafllm` repository.
2. The name has been changed from the earlier **“TANSTAAFLLM Memories”** to **“TANSTAAFLLM Bobiverse”** (5 November 2026). This is the intended repository *name*; its eventual GitHub slug and URL have not yet been created or verified.
3. **Git remains the preferred foundation** for persistence, history, traceability and exchange.
4. Each agent should be able to maintain its **own memory** and **selectively publish or share** relevant knowledge with others. The publication mechanism and its authorization rules are not yet selected.
5. Conversation in French is fine; project deliverables should be written in **English**.
6. First develop the memory design and prepare the repository structure; do not assume a working memory system exists.

## Context recovered from prior discussions

- **31 October 2026 — Mike / clone discussion:** Mike on Luna and a possible Pike clone on luna-pi motivate separate notions of model, agent identity/persona and memory. Clones could share an initial baseline then diverge, selectively exchanging lessons rather than automatically merging every experience.
- **31 October 2026 — persistence and knowledge:** conversation memory with dates, a RAG corpus for project documentation, and possible semantic or graph retrieval were discussed. Raw conversations were considered a source of evidence rather than an already curated knowledge base.
- **31 October–4 November 2026 — private/public boundary:** an independent private repository with per-agent history and a deliberately selective path to public project knowledge was proposed. The architecture of consolidation and sharing remained exploratory.
- **5 November 2026 — Bill workline:** Adam requested `cell/bill`, a Bill workline, and this foundation note. The name **TANSTAAFLLM Bobiverse** supersedes “TANSTAAFLLM Memories.”

These are recovered discussion notes, not verbatim archival transcripts. Original conversations and any subsequent decisions must be linked with verifiable provenance before treating a detail as authoritative.

## Conceptual memory layers (proposed, not finalized)

1. **Raw history:** original conversation/event records, timestamps, agent origin and source references; private by default.
2. **Individual memory:** agent-specific summaries, learned preferences, ongoing work and experiential context, with links to raw evidence. Different agent copies may diverge.
3. **Consolidated memory:** reviewed, deduplicated and time-aware statements with confidence, provenance, conflict/supersession markers and revision history.
4. **Shared knowledge:** a curated subset useful to other agents or to the project, explicitly approved for its destination. Publication to a public repository is a distinct disclosure decision.

The division among these layers, their formats and retention policies are open questions. A plausible implementation might use Markdown/JSON/JSONL, lexical search, then lightweight embeddings if justified by measured value. None of those choices is approved yet.

## Key safeguards and boundaries

- **Private is the default.** Never mirror a private transcript, personal datum, credential, or sensitive context into public TANSTAAFLLM merely because it is useful to an agent.
- **Keep provenance.** Distinguish user-approved decisions from agent interpretations, hypotheses and generated summaries. Prefer recoverable source links over unsupported assertions.
- **Keep agent autonomy.** Bill may coordinate knowledge exchange, not silently overwrite another agent's memory or alter a workline's plan.
- **Support correction.** The design should account for contradictory memories, changing facts, revocation, retention and deletion across replicas and derived summaries.
- **Separate stores from indexes.** Retrieval mechanisms and derived indexes must not be mistaken for the durable source of truth.
- **No premature automation.** No background ingestion, cross-repository synchronization, embedding pipeline or new services are authorized by this foundation.

## Open design questions for Bill and Adam

- What exactly constitutes an **agent identity** and its independent memory namespace?
- Which events are recorded verbatim, which are summarized, and how are consent and retention handled?
- What is the canonical memory record schema (time, source, author, type, status, confidence, visibility, supersedes)?
- How do raw logs become curated memories? Who reviews or approves shared claims?
- What can be shared within the private Bobiverse, and what — if anything — may be exported to public TANSTAAFLLM?
- How will agents retrieve memories efficiently on resource-constrained Luna versus remote environments?
- How does a Bob-like clone inherit a baseline and then diverge, reconcile or cherry-pick memories?
- How do access controls, compromised agents, accidental disclosure, corrections and deletion requests propagate?

## Next steps — planning only

- [ ] Adam creates the independent **private** GitHub repository named **TANSTAAFLLM Bobiverse**; record its verified slug and access policy afterward.
- [ ] Review primary transcripts and existing workline documents to compile a sourced decision ledger, marking unknowns explicitly.
- [ ] Draft a private-repository layout with separate agent histories, consolidated memory and exchange mechanisms.
- [ ] Define record provenance, privacy classification, promotion/review and deletion semantics before ingesting data.
- [ ] Evaluate retrieval and consolidation approaches against memory, latency, cost and maintainability constraints.
- [ ] Request Adam's explicit decision before implementation or publication.

## Relationship to other project artifacts

- Public project: `mdussere/tanstaafllm`
- Bill planning document: `worklines/bill/plan_bill.md` on `cell/bill`
- Professor: programme coordination and architectural arbitration
- Adam: human owner and strategic workline
- Future private memory repository: **TANSTAAFLLM Bobiverse** (not yet created at the time of this note)

**Principle:** preserve the full record privately, develop trustworthy memory from it, and share only what is appropriate and explicitly authorized.
