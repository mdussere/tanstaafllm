# Story 3 V3b preview — bitmap render and CI verification

> **Freshness:** 🟢 current · **Written:** 2026-11-05 · **Checked:** 2026-11-05 · **Step:** Hazel 3.3i

## Result

The V3b preview is ready for Adam's artistic review. It is intentionally a preview-only deliverable: **640×360 at 10 fps**, 112.0 seconds, with the 13-scene Story 3 edit.

GitHub Actions [run #42042702087](https://github.com/mdussere/tanstaafllm/actions/runs/42042702087) completed the actual MP4 render, strict checks, duration/audio verification and artifact upload from branch `cell/adam` at [`756a938`](https://github.com/mdussere/tanstaafllm/commit/756a9385c5013b27129c10520979ec4bc9ea9a58). The [preview artifact](https://github.com/mdussere/tanstaafllm/actions/runs/42042702087/artifacts/13421868368) contains the MP4, `contact.png`, `audit.md` and `lint.txt`.

CI evidence:

- 1120 preview frames; 112.0 s; no reading holds added.
- Layout lint: zero overflow, margin, overlap, clear-zone and squeeze failures; all 13 scenes retain a ≥50 px key message.
- Audio: integrated −15.0 LUFS; peak −0.6 dBFS.
- The local contact sheet was visually inspected after the same strict build. The end card was corrected so its title does not collide with the `TANSTAAFLLM` label.

## Asset provenance

`/home/michael/Downloads/TANSTAAFLLM_Hazel_Sprites_V3_2026-11-05.zip` was integrity-checked. Its 50 source assets match the committed `art/sprites-v3/` files byte-for-byte; its additional `contact.png` is generated review evidence, not a second source asset. No duplicate asset bytes were committed.

## What changed

- [`df8f888`](https://github.com/mdussere/tanstaafllm/commit/df8f888) installs the bitmap compositor, scene framing, score cues and deterministic V3b coverage.
- [`0542b12`](https://github.com/mdussere/tanstaafllm/commit/0542b12) lets the preview-only workflow validate matching pushes to `cell/adam` as well as pull requests.
- [`756a938`](https://github.com/mdussere/tanstaafllm/commit/756a9385c5013b27129c10520979ec4bc9ea9a58) adds a per-scene heading-size field and makes the end-card heading fit without squeeze or overlap.

## Boundary

This does not approve a 1080p master, a merge, publication, or a claim that the illustrative token/payback figures are measured. Those remain gated by Adam's review and Step 3.3j.
