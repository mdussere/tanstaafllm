# Local two-day atomization comparison

> **Freshness:** 🟢 current · **Written:** 2026-11-05 · **Checked:** 2026-11-05 · **Step:** 3.4

## Question

Can two current models turn the same bounded Claude Code event slice into short, source-traceable sequence atoms, without exporting or publishing the slice?

## Scope and handling

The private local Luna JSONL supplied the rows timestamped `2026-10-03` and `2026-10-04`: 1,137 event rows. The raw source remained unchanged. Each model wrote its atoms and run notes only under the ignored dated results directory; neither that material nor transcript-derived text is in Git or Tinkstaff LLM Biverse.

Both received the same instructions: select meaningful attempts involving several related events; state a beginning, an end, source references, a short sequence description and uncertainty. This is a comparison of one prompt and one source slice, not a model benchmark.

## Observed result

| Model | Atom count | Recorded model time | Shape validation |
| --- | ---: | ---: | --- |
| GPT-6 Luna | 4 | 54 seconds | Pass |
| GPT-6.1 Terra | 12 | 46 seconds | Pass |

The two lists demonstrate that both can make inspectable sequence descriptions from event-journal material. Their granularity differs materially: Luna chose four long arcs, while Terra subdivided the same two days into twelve shorter arcs. This is useful evidence that an atom definition needs a chosen resolution; raw record boundaries alone do not choose it.

The lightweight validator checked the required observable Markdown fields. During review, one Terra endpoint was corrected so its declared end included its later cited correction. That manual catch is also evidence of the validator's limit: it checks document shape, not source fidelity, causality, chronology, privacy safety or whether every atom is a good human unit.

## What this establishes—and does not

Established:

- Two independent current-model passes can form concise, traceable local drafts from the selected source window in under a minute of recorded model time each.
- The requested Markdown form is sufficient for a human to inspect sequence boundaries and uncertainty.

Not established:

- Which model is better in general, or whether either list is factually faithful to every source event.
- A correct universal atom size: one result can be too coarse, another too finely split.
- That the source's reported actions changed Luna hardware, or that any raw snapshot should now be exported.

## Next smallest decision

Step 4 (private snapshot) remains pending. Before it is green-lit, Adam can either choose a preferred granularity for a short human review of this trial or decide that the observed value already justifies preserving the immutable source. No automatic atomization, embedding store or model selection follows from this trial.
