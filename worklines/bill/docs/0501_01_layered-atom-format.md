# A layered atom: essence and verbatim

> **Freshness:** ⚪ draft · **Written:** 2026-11-05 · **Checked:** 2026-11-05 · **Step:** 5.1

## Why this draft exists

Adam compared atoms to verbatim clips: a short, concentrated account should be readable immediately, while the passage from which it came remains available in full. The first Luna/Terra trial produced short accounts with line ranges but did not preserve readable clips or enumerate which events actually belonged to each atom. This is a small format to try on **one** episode, not a storage architecture for every agent.

## The reading bundle

For the pilot, one atom has two readable parts:

1. **`atom.md` — the essence.** A title; one or two sentences stating what was attempted and what happened; an ordered list of meaningful events (the “electrons”); a state such as completed, blocked or still open; uncertainty; and exact source references. Start and end identify the actual trigger and observed stopping point, not just the first and last convenient line. The electron count is the number of listed meaningful events, not the number of JSONL rows in the surrounding span.
2. **`verbatim.md` — the clip.** The exact selected user/assistant words and relevant tool input/output in original order, with role, original line number and UUID where present. Framing labels may be added, but the quoted content is not paraphrased. If an interval is skipped, the clip marks the gap and its line range. Non-text content such as an image is identified by its original source reference; it is not silently turned into an asserted textual observation.

Both parts cite the same source session, source checksum and selected lines/UUIDs. The **full original JSONL remains immutable and available once** as the lossless source; the verbatim clip is a readable selection from it. A later correction can be a linked second clip or atom rather than stretching the first atom across unrelated work. The format will be adjusted after one human review; a whole directory tree or automated exporter is premature.

## A content-free sketch

```text
atom.md
  Essence: what was attempted, and its observed result
  Events: trigger → attempted actions → observations → result
  State: completed | blocked | open
  Evidence: source session, checksum, included line/UUID list, clip link
  Uncertainty: what the evidence does not establish

verbatim.md
  Source line/UUID + speaker or tool + exact content
  [explicit omitted interval, if any]
  Source line/UUID + speaker or tool + exact content
```

## Review questions for the first specimen

- Does each sentence in the essence survive a check against the verbatim?
- Does the event list include the failure, correction or reversal that changes the story?
- Do the first and last included events actually bound the attempt and its outcome?
- Can a reader distinguish the selected clip from the complete source, including any gaps or non-text material?
- Is the clip sufficiently useful to inspect without making the concise account as long as the source?

Raw or derived Luna content used to try this draft stays in the private destination or ignored local results; this public record contains only the format proposal.
