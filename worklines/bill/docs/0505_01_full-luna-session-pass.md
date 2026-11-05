# Complete Luna session: first Terra cut

> **Freshness:** 🟡 historical · **Written:** 2026-11-05 · **Checked:** 2026-11-05 · **Step:** 5.5

## Result

The preserved 3,714-line [Luna raw session](0404_01_luna-raw-preservation.md) has a complete first-pass navigation index in [private derived commit `425d015`](https://github.com/mdussere/tanstaafllm-bobiverse/commit/425d015). Its [readable index](https://github.com/mdussere/tanstaafllm-bobiverse/blob/425d015/derived/claude-code/luna/08421a9a-b5dc-435e-a293-8497430d722a/index.md) contains **79 attempted-action sequence candidates** with a beginning and end line, short account, observed state, uncertainty and anchor lines. Four further spans are labelled context-only. The [machine-readable index](https://github.com/mdussere/tanstaafllm-bobiverse/blob/425d015/derived/claude-code/luna/08421a9a-b5dc-435e-a293-8497430d722a/segments.json) has **83 contiguous, non-overlapping spans covering source lines 1–3714 exactly once**. The original JSONL remains the lossless source; these are provisional cuts and summaries, not verbatim-backed atoms.

The current private tree presents those candidates as individual Markdown files in the [Luna reading layout](0506_01_bobiverse-reading-layout.md); this record describes the earlier machine-index pass preserved in Git history.

## Method and context

A deterministic renderer made three contiguous, line-numbered reading views: 1–1572, 1573–2508 and 2509–3714. It omitted thinking blocks, shortened long fields to 1,200-character previews and marked non-text blocks; all originals remain in the private raw JSONL. Three GPT-6.1 Terra agents independently marked sequence candidates in their assigned slice. A fourth Terra pass reviewed the two artificial handoffs and suspicious boundaries. The review separated a replay-heavy context span from fresh actions and described how sequences across the handoffs relate. See the private [manifest](https://github.com/mdussere/tanstaafllm-bobiverse/blob/425d015/derived/claude-code/luna/08421a9a-b5dc-435e-a293-8497430d722a/manifest.json) and [semantic review](https://github.com/mdussere/tanstaafllm-bobiverse/blob/425d015/derived/claude-code/luna/08421a9a-b5dc-435e-a293-8497430d722a/review.md).

The local Terra agent runtime reported a 475,000-token context window. A single-call attempt on the whole 13.45 MB raw JSONL was not run, so its one-shot fit is **unknown**. The largest observed call in the chunked process had 83,783 input tokens. Chunking demonstrably worked for a complete first-pass cut. The views totalled about 800 KB; no exact token count was obtained for a hypothetical one-shot view.

## Usage and cost

The local Codex session usage logs for exactly those four Terra passes reported **35 model calls with usage**, **1,696,060 input tokens** (including **1,508,352 cached** and **187,708 uncached**) and **14,791 output tokens** (including 428 reasoning tokens). Applying the [published standard short-context Terra API prices](https://developers.openai.com/api/docs/models/gpt-6.1-terra) of $1 per million uncached input, $0.05 cached input and $5 output gives **$0.337081 API-price equivalent**. The per-pass counts, formula and sources are in private [cost.json](https://github.com/mdussere/tanstaafllm-bobiverse/blob/425d015/derived/claude-code/luna/08421a9a-b5dc-435e-a293-8497430d722a/cost.json). This is not an account invoice or the total cost of Bill's orchestration; local usage reporting is best-effort. The three segmentation passes account for $0.284103 of that equivalent; the separate review accounts for $0.052978.

## Validation and limits

The deterministic validator checked schema, anchor order and bounds, contiguous coverage, no overlap and no missing line. The integration check against the private checkout passed. The focused deterministic suite passed 10 tests with one integration test deselected; running that integration test separately passed one test. The repeatable checks and behavioural contract are under `test/bill/`.

Line coverage establishes a complete index of this recorded file, not perfect semantic boundaries or proof of every summary claim. Replayed API context, reported device actions and long/truncated blocks require raw-source review before an atom is treated as settled. UUIDs were not uniformly available in the compact views; original IDs remain in the JSONL. The next bounded experiment is [Step 6](../plan_bill.md): one layered atom with its short account and actual verbatim clip, checked against the source.
