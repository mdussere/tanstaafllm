# Step 2.1–2.5 — Luna JSONL anatomy and Claude-managed memory

> **Freshness:** 🟢 current · **Written:** 2026-11-05 · **Checked:** 2026-11-05 · **Step:** bill 2.1–2.5 ✅

**Question answered:** what is the selected Luna Claude Code session file, where can it be cut without falsifying its meaning, and how does Claude's separate managed-memory layer affect preservation and retrieval?

## Safety and method

The selected local raw file was read in place by [`inspect_luna_jsonl.py`](../scripts/inspect_luna_jsonl.py). The inspector emits only safe structural labels, counts, date buckets and a SHA-256 digest; it never writes message text, tool inputs, attachments, credentials or memory-note text to its report. Its private, ignored output is `results/bill/luna-jsonl-anatomy/20261105T195158Z/structural-report.json`.

The deterministic redaction test is [`test/bill/test_luna_jsonl_anatomy.py`](../../../test/bill/test_luna_jsonl_anatomy.py). It proves a sentinel in fake user and tool content cannot appear in the report; it does not prove the completeness or semantic accuracy of the Luna source.

## First correction: JSONL, not JSON-LD

This is **JSONL**: one independent JSON object per physical line. A reader processes the file line by line; there is no enclosing JSON array. It is **not JSON-LD**: no `@context`, `@id` or linked-data vocabulary was observed in the 3,714 objects.

Every observed row has a top-level `type`, but that is the only universal structural rule. A `user` row is not shaped like an `attachment` row, which is not shaped like an API cache blob or a title update. The file is a typed event journal.

## What one object looks like

The examples below are structural templates, with all real values and content omitted.

```json
{"type":"user","uuid":"…","parentUuid":"…","sessionId":"…","timestamp":"…",
 "cwd":"…","gitBranch":"…","message":{"role":"user","content":"…"}}

{"type":"assistant","uuid":"…","parentUuid":"…","sessionId":"…","timestamp":"…",
 "cwd":"…","requestId":"…","message":{"role":"assistant","model":"…",
 "usage":{},"content":[{"type":"text","text":"…"},{"type":"tool_use","id":"…","name":"…","input":{}}]}}
```

The first row represents an incoming human-side turn or a tool-result/permission-related user event. The second represents a model response and can contain text, hidden thinking, tool calls and metadata about model use and stopping. The `uuid` / `parentUuid` pair links these event rows into a causal chain; physical line order alone is not the whole conversation structure.

## Actual object families in the Luna file

| Family | `type` values observed | What it carries |
|---|---|---|
| Conversation | `user` 490; `assistant` 948; `system` 6 | Messages, session and parent IDs, timestamps where present, project/cwd/branch context, permissions and model/request metadata. |
| Assistant content blocks | nested in assistant `message.content` | 298 text, 445 thinking, 435 tool-use, 387 tool-result, 11 image and 1 tool-addition blocks. Tool blocks carry their call ID/name/input or result linkage; they belong to the enclosing assistant/request sequence. |
| Attachments | `attachment` 650 | Attachment payload/reference plus session, UUID-parent linkage, timestamp and optional rendered-role metadata. |
| API/request trace | `api-request` 46; `api-request-blob` 135; `api-request-shape` 1 | Request shape, parameter/cache/digest information, and message blobs. These are operational evidence, not duplicate clean chat turns. |
| Session/lifecycle UI state | `agent-name` 167; `ai-title` 199; `custom-title` 168; `mode` 163; `atis-latch` 200; `last-prompt` 205; `bridge-session` 47 | Names, titles, mode, queue/bridge state and the current leaf/prompt references that let the Claude Code UI resume or render the session. |
| Queue and execution control | `queue-operation` 194 | Queued command/event operation, delivery/reason/timestamp fields where applicable. |
| File history | `file-history-snapshot` 64; `file-history-delta` 25 | Snapshot/delta references tied to message IDs, including tracking and backup information. |
| Accounting | `cost-state` 6 | Aggregate API/model, duration, cost and line-change counters. |

Only the `type` field occurs on all 3,714 rows. `sessionId` occurs on 3,625 rows, `timestamp` on 2,360, and `uuid` plus `parentUuid` on 2,094. A derived parser must therefore tolerate optional fields and dispatch by `type`; it must not assume every row has a timestamp, message, UUID or text.

Nested `message` objects also vary by role:

| `message.role` | Always observed fields in this file | Meaning |
|---|---|---|
| `user` | `role`, `content` | Incoming user-side content; surrounding top-level fields distinguish ordinary prompts, permissions and tool-result events. |
| `assistant` | `role`, `content`, `model`, `usage`, `stop_reason`, `stop_details`, `container`, `context_management`, `diagnostics` | Model response and model/runtime metadata. Its `content` can be a list of typed blocks. |
| `system` | `role`, `content` | System-side messages, with one optional output configuration observed. |

## Consequence for cuts and storage

There are 433 direct user→assistant role transitions, but 506 assistant→assistant transitions and 50 user→user transitions as well. This proves that naïvely pairing alternating rows would invent false questions and answers. A proper request unit starts at a user event and follows its UUID-parent chain through assistant and tool events until the next independent user request. Day boundaries and the two explicit compaction markers are useful outer navigation cuts, not replacements for that causal grouping.

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
