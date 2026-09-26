# Shared ChatGPT discussion — cleaned decision record

**Source:** [0102_02_shared-chatgpt-options-source.md](0102_02_shared-chatgpt-options-source.md)<br>
**Captured:** 2026-09-25 with `scripts/scrape_shared_chat.py` (14 messages)<br>
**Status:** decision record; external technical claims remain unverified unless separately evidenced.

## Summary

The user keeps Sherpa-ONNX French Zipformer as the current context-free ASR reference. Mycroft is broadened from an ASR component into Luna's interactive input-and-composition capability: transcription becomes an editable proposal, never an immediate action. The next candidate panel must include very small, FOSS-capable ASR candidates with bounded contextual-vocabulary support, while a separate later experiment measures the value and cost of context.

## Detailed summary

- The existing Sherpa-versus-Whisper result remains valid evidence for the context-free baseline; it is not a complete product choice.
- Mycroft's eventual path is capture → ASR hypotheses → editable composition buffer → human acceptance → destination. A rejected or unaccepted proposal has no external effect.
- Input modes (free prose, coding, shell, and UI navigation) constrain the available vocabulary and destination. Their exact controls, colour mapping, and stick mapping are design work, not yet an implementation decision.
- Wyoh may later provide a small, revisioned and policy-scoped context snapshot (for example focused surface, visible labels, and advertised actions). It must not hand Mycroft arbitrary desktop contents or authority.
- The candidate panel is reopened to assess compact, open candidates that may accept dynamically injected vocabulary. Candidate size, ARM support, licensing, and actual biasing behaviour all require fresh evidence.
- Context must be tested separately from generic ASR: identical utterances under no context, mode context, environment context, and structured-command context, with both improvement and resource cost measured.
- A local, Jev-like closed-set classifier/ranker is an idea-box item only. It must be local, bounded, separately budgeted, reject/abstain safely, and never replace human acceptance by implication.

## Cleaned / translated verbatim

### §1 — Baseline result and the actual gap

**User concern:** the accurate ASR alternative remains larger than desired and has no usable contextual vocabulary path.

**Decision:** retain Sherpa as the reference backend for bring-up. Its measured context-free quality is useful, but it does not settle the smaller, context-aware path.

### §2 — Candidate and evaluation direction

**User decision:** add very small, context-capable ASR candidates to the panel, then run a dedicated contextualisation step.

**Interpretation:** generic WER and contextual performance are different questions. No unverified claim about a specific Vosk model, hotword API, size, or licence is adopted as a project fact.

### §3 — Composition instead of direct voice commands

**User direction:** voice capture should open a composition interaction. The user can inspect, alter, select alternatives, and validate the text using constrained handheld controls.

**Boundary:** ASR output is inert until explicit acceptance. The exact controller mapping, colour code, N-best display, and accessibility behaviour are open design questions.

### §4 — Modes and context

**User direction:** modes can distinguish prose, coding, shell, and UI navigation. Each mode may supply a narrow vocabulary from an appropriate context provider: project state for coding, cwd/files for shell, and Wyoh-visible objects/actions for navigation.

**Boundary:** the current ASR baseline remains context-free. Future context must be optional, bounded, attributable to a revision/source, and measured for memory, decoding cost, errors, and privacy.

### §5 — Closed-set local decision models

**User idea:** after transcription, small local classifiers/rankers may turn a bounded input into two or three reviewable proposals.

**Decision status:** idea box only. No Jev API, BERT-family model, command router, or execution path is selected or authorised.

## Consequences by owner

| Owner | Consequence |
| --- | --- |
| Professor | Maintains the cross-workline boundary: Mycroft owns composition; Wyoh owns scoped observable state; neither gains command authority by context alone. |
| Mycroft | Reopen candidate/harness/selection work for compact contextual-ASR evidence. Preserve Sherpa as the context-free reference and add a later contextualisation experiment. |
| Wyoh | Define, but do not implement, a bounded revisioned context snapshot for a later Mycroft consumer. |
| Luna | On real hardware inventory, include actual buttons/sticks and feedback affordances; `luna-pi` remains only a graphical approximation. |
