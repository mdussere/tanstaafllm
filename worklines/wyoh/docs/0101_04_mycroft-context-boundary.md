# Wyoh-to-Mycroft context boundary

**Status:** design boundary only, 2026-09-25. It authorises no Sway fixture, live context feed, or Mycroft integration.

Wyoh may later provide Mycroft a small consumer-scoped snapshot for contextual ASR. It is descriptive, revisioned, and optional; it carries neither shell authority nor arbitrary client contents.

Minimum proposed fields: Wyoh revision, focused surface identifier, visible user-facing labels where safely available, advertised finite actions, source/freshness metadata, and an explicit truncation/budget result. Mycroft may turn these into a short vocabulary hint list or ignore them. It must preserve the same baseline behaviour when the snapshot is absent, stale, ambiguous, unauthorised, or over budget.

This division preserves the existing contract: Wyoh observes and mediates; Mycroft composes input; Mike or another authorised component decides whether an accepted proposal causes an action. See [the shared decision record](../../professor/docs/0102_03_shared-chatgpt-options-decision.md).

