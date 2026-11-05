# Step 2.1–2.5 — Luna JSONL anatomy and Claude-managed memory

> **Freshness:** 🟢 current · **Written:** 2026-11-05 · **Checked:** 2026-11-05 · **Step:** bill 2.1–2.5 ✅

**Question answered:** what is the selected Luna Claude Code session file, where can it be cut without falsifying its meaning, and how does Claude's separate managed-memory layer affect preservation and retrieval?

## Safety and method

The selected local raw file was read in place by [`inspect_luna_jsonl.py`](../scripts/inspect_luna_jsonl.py). The inspector emits only safe structural labels, counts, date buckets and a SHA-256 digest; it never writes message text, tool inputs, attachments, credentials or memory-note text to its report. Its private, ignored output is `results/bill/luna-jsonl-anatomy/20261105T195158Z/structural-report.json`.

The deterministic redaction test is [`test/bill/test_luna_jsonl_anatomy.py`](../../../test/bill/test_luna_jsonl_anatomy.py). It proves a sentinel in fake user and tool content cannot appear in the report; it does not prove the completeness or semantic accuracy of the Luna source.

## The raw session is an event journal

| Measure | Observed value |
|---|---:|
| Raw file | one Claude Code project-session JSONL |
| Size | 13,451,993 bytes (about 12.8 MiB) |
| SHA-256 | `9c07746899fd3bba398d103af91f511e67d362a7c2312ea87b3d698093461af9` |
| JSON records | 3,714 valid objects; 0 blank or malformed lines |
| Calendar days with root timestamps | 13, from 2026-10-03 through 2026-11-01 |
| Message roles | 497 user, 998 assistant, 78 system |
| Assistant content items | 445 thinking, 435 tool-use, 387 tool-result, 298 text, 11 image |
| Explicit compaction markers | 2 summaries / 2 compaction-metadata records |
| UUID-parent records | 2,094 records each carrying both `uuid` and `parentUuid` |

The remaining lines are not noise to discard blindly. They include 650 attachment events, 948 assistant event records, 490 user event records, API/request metadata, file-history snapshots and deltas, titles, queue/mode state and cost-state summaries. Therefore this file is an **append-only event journal**, not one row per message and not a clean question/answer table.

## Natural cuts: use a hierarchy, not one delimiter

1. **Raw session file:** the immutable preservation unit. Keep its bytes unchanged and identify it with the SHA-256 above.
2. **Compaction boundary:** two explicit summary/compaction markers divide the history into durable context epochs. They are a better high-level split than arbitrary line counts.
3. **Calendar day:** the 13 timestamp days are useful navigation buckets and incremental-export checkpoints, but a single task can cross midnight or resume days later.
4. **Request unit:** a user `message.role` entry followed through `uuid` / `parentUuid` to assistant output and its tool-use/result sequence. This is the first plausible atomization unit.
5. **Tool sub-unit:** retain each tool-use/result pair inside its parent request; splitting it away from the request would erase the evidence for an action and its outcome.

Sequential line order alone is unsafe: 3,714 journal records include assistant→assistant, system, attachment and bookkeeping transitions. The first derived index should preserve original line offsets and UUID/parent links rather than rewrite the source into apparent turns.

## Storage recommendation for the first snapshot

Store one exact raw file in the private repository, for example:

```text
raw/claude-code/luna/08421a9a-b5dc-435e-a293-8497430d722a/
  session.jsonl          # unchanged source bytes
  manifest.json          # source path, session ID, captured time, size, SHA-256, coverage
```

At about 12.8 MiB, this single pilot file is ordinary Git-sized; do **not** split or gzip the only canonical copy. Git already compresses text objects. A later derived, regenerable index may contain line offsets, day buckets, UUID-parent links and request-unit membership. Reconsider Git LFS or external object storage only after measuring several much larger snapshots; no such decision is warranted by one 12.8 MiB file.

## What Claude's managed memory contains

The project `memory/` directory is a compact, curated layer: 13 Markdown notes totalling about 12 KiB, plus an index `MEMORY.md`. Each note uses front matter such as a short name, description, memory type (`feedback`, `project` or `user`), origin session ID and modified time; the body explains a retained rule, why it matters and how to apply it.

Its content is primarily operational preferences and durable project facts: user presentation preferences, commit/coordination procedure, skill layout, language policy, device-safety rules and named project facts. It is not a replayable history, a complete decision ledger, or an index over the raw JSONL.

It is valuable as a **high-priority curated policy layer**, but not automatically authoritative. The inspection found overlapping commit/push notes and a language note that predates the current English-only rule in `AGENTS.md`. A preservation design must retain each note's origin and modified time, check it against current versioned project rules, and mark it current, historical or superseded rather than treating it as eternal memory.

For a later private export, keep this layer separate from raw history, for example `managed-memory/claude-code/project/tanstfaafllm/`. Preserve the individual note files and their metadata; derive a reviewable current-policy index only after freshness resolution.

## Consequence for Step 3 and Step 4

Step 3 can now export a precise immutable source plus manifest once private repository access is available. Step 4 should atomize bounded request units—not JSON lines, full days, or an unreviewed Claude-memory note—and every atom should link to the raw session ID and original line/UUID range.
