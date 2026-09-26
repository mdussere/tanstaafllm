---
name: shared-chat-discussion
description: Capture a public ChatGPT shared discussion as TANSTAAFLLM source evidence, clean it, and coordinate the resulting workline-plan changes.
---

# Shared Chat Discussion

Use this skill when a user supplies a `chatgpt.com/share/...` discussion as project input.

1. Capture it with `scripts/scrape_shared_chat.py`; this is the canonical source mechanism. Do not substitute HTTP extraction, search snippets, or a manually reconstructed conversation.
2. Run the script against the supplied URL, retain its raw Markdown export in the owning workline's `docs/`, and keep debug JSON/run logs in `/tmp` unless a review artifact requires them.
3. The scraper needs the Python `playwright` package and its configured Chrome binary. If either is absent, state the exact failure and obtain permission before installation or environment change. Verify the terminal's `Exported <N> messages` result.
4. Check the raw export for collapsed-message controls. `Show more` indicates incomplete text. The repository scraper must expand those controls before collecting `innerText`; fix and rerun that script rather than using a different source path.
5. When cleaning is requested, use `clean-verbatim` on a separate decision record linked to the raw export. Preserve user decisions, distinguish them from assistant proposals, and flag unverified technical claims.
6. For cross-workline effects, use `workplan`, read every affected plan, preserve earlier evidence, and reopen only criteria invalidated or made incomplete by the new direction. Update `docs/LOGBOOK.md`; plan/docs changes do not authorise implementation.
