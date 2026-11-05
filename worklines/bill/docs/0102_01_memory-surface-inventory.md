# Step 1.2 — Memory-surface inventory

> **Freshness:** 🟡 historical · **Written:** 2026-11-05 · **Checked:** 2026-11-05 · **Step:** bill 1.2 ✅

**Question answered:** what agent-memory sources are actually visible from this Bill session, and which of them can be used for the first Luna pilot without copying a transcript?

## Scope and safety

This is a metadata-only inventory. No JSONL file was opened, no transcript was copied, and no private repository was written. File names, paths, documented command surfaces and access outcomes are not claims about a session's contents or completeness.

## Local Codex surfaces — actionable

The current host contains the following Codex-managed data locations:

| Surface | Observed form | Pilot relevance |
|---|---|---|
| Active sessions | `~/.codex/sessions/YYYY/MM/DD/rollout-<timestamp>-<uuid>.jsonl` | Candidate raw source. The directory contains multiple dated JSONL session records, including records dated 2026-11-05. Contents and role identity were deliberately not inspected in Step 1. |
| Archived sessions | `~/.codex/archived_sessions/rollout-<timestamp>-<uuid>.jsonl` | Separate source for archived conversations; not a substitute for the active-session directory. |
| Session index | `~/.codex/session_index.jsonl` | Local index surface; not yet assessed as a raw record or as the canonical way to identify the Luna session. |
| Prompt history | `~/.codex/history.jsonl` | Local history surface; not yet assessed as a complete session archive. |

Official OpenAI documentation identifies `$CODEX_HOME/sessions` (normally `~/.codex/sessions`) as the local transcript location and separately describes the terminal `/export` command for an interactive session export. Neither mechanism was invoked here. [OpenAI Docs: Developer commands](https://learn.chatgpt.com/docs/developer-commands)

## Codex Cloud — listable, but no records available here

The documented read-only command `codex cloud list --json --limit 20` was available and returned an empty task list for the current authentication. It therefore cannot identify a Cloud-hosted Luna session in this account at present.

The same official documentation describes `codex cloud list` as metadata listing (task ID, URL, title, status, timestamps and environment), not as a raw-conversation export facility. It also marks `codex cloud` experimental. A complete interactive Codex conversation can be exported with `/export`, but that is a session-level action and was not used. [OpenAI Docs: Developer commands](https://learn.chatgpt.com/docs/developer-commands)

## Private destination — not connected yet

The authenticated GitHub connector can list repositories owned by `mdussere`, but it did not list **Tinkstaff LLM Biverse**. This proves only that the current connector cannot see a repository with that name under that account; it does not disprove that Adam created it.

Before Step 2 writes a raw Luna snapshot, one of the following must be supplied or repaired:

- the repository's exact GitHub URL and confirmation that it belongs to the connected account; or
- access/installation permission for the GitHub connector; or
- the intended owner and Git remote URL, if it lives elsewhere.

## Step 2 input

The viable source for the first pilot is a single, deliberately selected JSONL record under `~/.codex/sessions`. Step 2 must identify which record represents Luna before opening it, then export only that record to the verified private destination with a manifest of coverage and omissions. No general ingestion or Cloud workaround follows from this inventory.
