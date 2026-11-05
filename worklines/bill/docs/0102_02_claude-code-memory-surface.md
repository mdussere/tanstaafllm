# Step 1.3–1.5 — What Claude Code leaves on disk

> **Freshness:** 🟢 current · **Written:** 2026-11-05 · **Checked:** 2026-11-05 · **Step:** bill 1.3–1.5 ✅

**Question answered:** which Claude Code artifacts on this host are candidate memory sources, and which exact raw record belongs to the Luna workline?

## Scope and safety

This is an on-disk metadata inspection only. It read file names, types, modification times, byte sizes and the identity fields of Claude Code's small session metadata files. It did **not** open any raw JSONL transcript, project-memory note, global history file or credential file. Nothing was copied or written outside this public planning repository.

## What Claude Code retains

| Surface | Observed location | Meaning for the pilot |
|---|---|---|
| Raw project session | `~/.claude/projects/-home-michael-git-tanstfaafllm/<session-uuid>.jsonl` | The primary raw source. Claude Code keeps large project-scoped JSONL records here; the directory name encodes the project path. |
| Session identity metadata | `~/.claude/sessions/<number>.json` | Small metadata records identify `sessionId`, `cwd`, display `name`, timestamps, status and CLI version. They can select a raw record without reading it. |
| Curated project memory | `~/.claude/projects/-home-michael-git-tanstfaafllm/memory/MEMORY.md` and sibling Markdown files | Claude Code's separate, editable memory layer. It is not the raw transcript and should be archived separately if ever selected. |
| Global prompt history | `~/.claude/history.jsonl` | A separate global history surface. Its coverage and relation to raw sessions are unverified. |
| Archived/other project sessions | `~/.claude/projects/<other-encoded-project>/` | Other projects' data exists and is out of scope for the Luna pilot. |

Claude Code also has settings, cache, plugin and credential surfaces under `~/.claude/` and a user-level `~/.claude.json`. They are configuration or secret-bearing material, not candidate memory exports; the credential file must never be copied to the memory repository.

## Luna candidate — identified, not opened

`worklines/agents.md` names the Luna workline's Claude session **`tanstfaafllm-e0`**. Claude Code's identity metadata maps that name to:

- **Session ID:** `08421a9a-b5dc-435e-a293-8497430d722a`
- **Project:** `/home/michael/git/tanstfaafllm`
- **Raw candidate:** `~/.claude/projects/-home-michael-git-tanstfaafllm/08421a9a-b5dc-435e-a293-8497430d722a.jsonl`
- **Observed metadata:** 13,451,993 bytes; last modified 2026-11-01.

The candidate was not opened. Its byte size and the existence of an associated `custom-title.json` do not establish completeness, finality or semantic content.

## Step 2 boundary

The first export should copy this one raw JSONL file unchanged, plus a newly written manifest containing this selection evidence, extraction time, source path, byte count and checksum. It must not include the credential file, unrelated project sessions, Codex records, caches, settings, plugins or project-memory Markdown unless Adam explicitly expands the pilot.

Step 2 remains blocked until the exact Git URL/access for **Tinkstaff LLM Biverse** is available to this session. The export itself needs a separate `🟩 go Step 2`.
