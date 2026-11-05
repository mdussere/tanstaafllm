# Bobiverse: Luna reading layout

> **Freshness:** 🟢 current · **Written:** 2026-11-05 · **Checked:** 2026-11-05 · **Step:** 5.6

## What Adam sees

The private [Bobiverse repository](https://github.com/mdussere/tanstaafllm-bobiverse/tree/baa2e51) now opens onto a short [README](https://github.com/mdussere/tanstaafllm-bobiverse/blob/baa2e51/README.md) and one agent directory:

```text
Luna/
  raw/
    luna-claude-code-2026-10-03_2026-11-01.jsonl
  refined/
    2026-10-03_001_review-operating-system-impasse.md
    ... 77 more Markdown files ...
    2026-11-01_079_correct-repository-link-claim.md
```

The [raw directory](https://github.com/mdussere/tanstaafllm-bobiverse/tree/baa2e51/Luna/raw) has exactly one file. It is the original 13,451,993-byte, 3,714-row source, moved with Git's 100% rename detection and independently checked against SHA-256 `9c07746899fd3bba398d103af91f511e67d362a7c2312ea87b3d698093461af9`. The `.jsonl` suffix is intentional: the source is newline-delimited JSON, not one JSON object or JSON-LD. No conversion changed its bytes.

The [refined directory](https://github.com/mdussere/tanstaafllm-bobiverse/tree/baa2e51/Luna/refined) contains only 79 `.md` files, one per Terra sequence candidate. Each filename starts with its source date and a three-digit sequence number, so ordinary alphabetical order is reading order, followed by a meaningful action name. Each file has an essence, observed state, source span and anchors, uncertainty, and an explicit notice that verbatim has **not** yet been selected. These are provisional atom drafts, not finished essence-plus-verbatim bundles.

The four context-only spans (1797–1823, 2509–2510, 2598–2627 and 3010–3102) are listed in the README rather than masquerading as atoms. The former manifests, machine index, boundary review and usage report remain available in [private commit `425d015`](https://github.com/mdussere/tanstaafllm-bobiverse/commit/425d015). The current tree has no technical metadata files under `Luna/`.

## Check and next cut

The `test/bill/test_full_luna_index_live.py` integration check passed against the private checkout. It verified the exact tree, one raw file and hash, 79 alphabetically ordered Markdown files with source links, and complete line coverage when the four context spans are included. This tests layout and references, not the truth of the summaries. [Step 6](../plan_bill.md) remains the review of one actual verbatim-backed atom.
