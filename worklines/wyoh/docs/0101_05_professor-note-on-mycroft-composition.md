# Note from Professor — Mycroft composition and Wyoh context

> **Freshness:** 🟡 historical · **Written:** 2026-09-26 · **Checked:** 2026-10-31 · **Step:** wyoh 1.1 ✅

**From:** Professor workline  
**To:** Wyoh workline  
**Date:** 2026-09-25  
**Status:** coordination note; planning only

The updated Mycroft direction concerns Wyoh directly. Mycroft is no longer described solely as audio-to-text: its eventual product role is an editable input/composition surface. Voice produces a proposal; the user reviews and explicitly accepts it before any destination receives it.

Wyoh's future responsibility is deliberately narrow. It may offer Mycroft a consumer-scoped context snapshot containing only safe, bounded, observable material: its revision/freshness, focus, finite advertised actions, and safely available visible labels. It must not expose arbitrary desktop contents, become a shell proxy, or make a transcript executable.

Please retain these invariants when ratifying the reopened Step 1 contract:

- absence, staleness, ambiguity, denial, or truncation of context is safe and has no side effect;
- `context = []` remains valid: Mycroft's measured ASR baseline works without Wyoh;
- context carries no authority and cannot bypass Mike's policy or human acceptance;
- context size, source, freshness, and redaction need observable accounting before a live integration is considered;
- Sway IPC remains the proposed substrate. This note neither requires an adapter nor authorises one.

The shared source and cross-workline decision are in [Professor's cleaned record](../../professor/docs/0102_03_shared-chatgpt-options-decision.md); the compact boundary is [0101_04_mycroft-context-boundary.md](0101_04_mycroft-context-boundary.md).
