---
status: foundation-draft
date: 2026-11-05
workline: bill
branch: cell/bill
proposed_private_repository_name: "TANSTAAFLLM Bobiverse"
---

# Bill foundation — TANSTAAFLLM Bobiverse

> **Freshness:** ⚪ draft · **Written:** 2026-11-05 · **Checked:** 2026-11-05 · **Step:** bill pre-plan foundation

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


## Proposed CI-based memory distillation (Adam discussion, 2026-11-05)

**Architecture direction, not implementation approval.** Adam wants to use the **free GitHub Actions CI capacity**, rather than provision local hardware, allocate Luna resources, or consume paid LLM API tokens for background memory processing. The private Bobiverse repository is the proposed processing environment; its actual GitHub Actions entitlement, minutes, storage limits and runner model feasibility remain to be checked.

### Agent-to-memory workflow

1. An agent instance embodies a persistent **role** (several instances and model providers may embody the same role concurrently).
2. Each instance deposits **raw memory** into its role's branch and a uniquely identifiable session directory. A possible convention is `<role>/raw/<start-timestamp>_<provider>_<uuid>/0001.md`, then `0002.md` and so on, with **one immutable file per incremental memory dump**. Preserve the original conversation start time separately from the time of the first dump when known.
3. A GitHub Actions workflow triggers on newly pushed raw records, discovers **only the unprocessed additions**, and preserves the original inputs unchanged.
4. **Atomization** turns conversation excerpts into traceable, independent **Knowledge Atoms** (facts, decisions, corrections, questions, preferences, hypotheses), retaining source references and negations. A small locally executed model such as **Qwen3-0.6B** is a *candidate to benchmark*, not a selected model.
5. **Embedding + SECNA-style clustering** organizes atoms by semantic proximity, highlights novelty and potential duplication, and supports cross-session retrieval.
6. An **explicit relation graph** builds typed edges where justified by evidence (e.g. `supports`, `contradicts`, `supersedes`, `depends_on`), distinguishing exact/source-backed relations from approximate vector similarity.
7. The pipeline writes derived atoms, embeddings, clusters and graph artifacts **back to the private Bobiverse**. Any promotion into shared/common curated knowledge proceeds through **reviewable pull requests**, never by publishing raw transcripts.

### Technical risks / unresolved decisions

- **Branch isolation:** ordinary Git PRs from a role branch may include private raw files. Design a safe staging or cherry-pick mechanism for atom-only PRs, rather than merging role branches wholesale.
- **Workflow triggers:** avoid self-triggering loops when the workflow commits generated artifacts; identify work by immutable input hashes and/or manifest, and make jobs idempotent.
- **Concurrency:** multiple agents may push on the same role branch; prevent lost updates and collisions, and serialize or safely retry generated-state writes.
- **Runner constraints:** confirm *actual* available free CI minutes for a **private** repository, CPU/RAM/disk, execution time, model downloads and cache limits before assuming the proposed pipeline is free or fits.
- **Security:** treat raw memories as untrusted private data; limit runner permissions, action dependencies, artifact/log exposure, and access to any promotion paths.
- **Quality gates:** benchmark small atomization models on real chat corrections, implied decisions, source fidelity, omission/hallucination and multilingual inputs; the target is **minimal incremental LLM cost** rather than a blanket promise of zero compute.
- **Clustering and graph:** distinguish semantic grouping from verified factual edges; clustering alone cannot establish an exact relationship.
- **Persistence design:** decide whether embeddings/indexes are stored in Git, cached/generated, or maintained as derived build artifacts; avoid committing unnecessarily large regenerable binaries.

**No GitHub workflow has been implemented or enabled by this note.**


## Design checkpoint — agent extraction, role structure and science-fiction analogies (2026-11-05)

### Confirmed direction from Adam

- **Roles are persistent; agent instances are ephemeral and concurrent.** Multiple agents, including agents running on different LLM providers, may incarnate the *same role at the same time*. A role has its own namespace and proposed Git branch in the private Bobiverse repository.
- **Raw is per instance, inside each role.** Proposed path: `<role>/raw/<session-start-or-first-dump-UTC>_<provider>_<uuid>/0001.md`, `0002.md`, etc. A timestamp and UUID distinguish concurrent incarnations; preserve start and ingestion timestamps separately. Each successive file contains **only newly exported material** and is immutable once recorded.
- **A memory dump is an extraction, not a summary.** For locally accessible harnesses such as Claude Code, favor a deterministic exporter of accessible session artifacts (e.g. JSONL). Do not require or charge the agent LLM to select what is worth remembering. For cloud-only harnesses such as ChatGPT, a different connector/skill/export method may be necessary; completeness must never be falsely claimed.
- **Atomization is downstream of the raw archive.** It extracts traceable, individual knowledge claims; subsequent SECNA-like embeddings/clustering and exact evidence-backed graph relationships organize them. Importance filtering and cross-role promotion follow later. Preserve raw even when consolidation is revised.
- **GitHub Actions is the preferred compute budget** for this support function: use available CI minutes rather than Luna or additional commercial LLM API tokens, subject to actual free-tier private-repository limits and CPU feasibility.
- **Private Bobiverse remains the planned memory repository**, separate from the public TANSTAAFLLM code/workline repository. Role-scoped branches plus selective PR promotion are the intended model, subject to designing PRs that exclude raw history.

### Distinct tooling categories and possible spin-off

1. **Harness-side raw extractors**: per-provider/harness adapters (deterministic where possible), session/instance registration, incremental export and upload to Git. A ChatGPT-specific skill is a fallback for limited harness access, not the universal design.
2. **CI memory pipeline**: atomization, provenance capture, embeddings, SECNA-like grouping, supported graph-edge extraction, and reviewable distilled-memory promotion.
3. **Possible future independent software project**: if these tools/skills become substantial, spin them off as a reusable **Bobiverse** project. This is a direction under consideration, not a repository that has already been created.

### Science-fiction vocabulary retained intentionally

- **Bobiverse** (Dennis E. Taylor): Bill as knowledge/infrastructure steward; independently evolving copies and selective sharing. The project and proposed private memory repository retain the **Bobiverse** name; the responsible role remains **Bill**.
- **Altered Carbon**: the *cortical stack* and saving/downloading experience as an analogy for persistent memory and a *memory dump*; a model/provider/harness instance loosely resembles an interchangeable *sleeve*. Unlike a fictional consciousness transfer, our accessible raw session archive does not capture a model's complete internal state.
- **Pluribus** (TV series): hive-like shared awareness as an analogy for **collective knowledge**, while TANSTAAFLLM deliberately preserves distinct roles and agent identities instead of merging them.
- These references complement each other rather than dictate engineering constraints. Adam explicitly chose to **keep Bobiverse and Bill as the names**, while retaining the other science-fiction analogies.

### Carry-forward questions

- Define exporter coverage, origin metadata, incremental cursors, missing turns and replay checks per harness.
- Confirm the exact branch and shared-memory directory conventions, promotion workflow and Git safety boundaries.
- Benchmark small English-oriented atomizers (e.g. Qwen3-0.6B) for faithful claims and corrections; no model is approved.
- Test runner feasibility and costs, then decide where to persist structured atoms, embeddings and graph representations.
- Decide when to split a distinct Bobiverse tools project; **do not initiate the spin-off without direction**.

**Checkpoint status:** documented design only. No private memory repository, CI pipeline, harness extractor or cross-role memory-sharing automation has been deployed as part of this workline.
