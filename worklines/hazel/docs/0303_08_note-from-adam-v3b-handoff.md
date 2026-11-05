# Note from Adam's ChatGPT workline — Story 3 V3b handoff

> **Freshness:** 🟢 current · **Written:** 2026-11-04 · **Checked:** 2026-11-04 · **Step:** Hazel 3.3i
>
> **From:** Adam's ChatGPT contribution (branch `cell/adam`)
> **To:** Hazel, copy to Professor for coordination
> **Status:** handoff / assets awaiting application, not a permission to publish

## Where we stand

Adam has accepted the **balance** of the three bitmap mockups (budget 02, manual library 09, YAML compile 10). He explicitly rejects **the same layout repeated all episode** and the generic musical mood of V2/V3. Preserve concise Hazel vignette scenes with her feet touching the bottom of the *small scene* (not floating in a full frame), with the inset occupying at most half the overall screen. Mix shots: compact actor vignette, prop focus, short wider workshop view and title/reveal. The original trailer and hand-crafted Story 2 are the authoritative visual/audio references.

User requested: **go through to a complete low-resolution preview and stop for approval**. No Full HD render, PR merge, or publication before Adam validates the new preview.

## Critical comparison reference

GitHub Actions [#41869289272](https://github.com/mdussere/tanstaafllm/actions/runs/41869289272) rebuilt the hand-authored original Story 2 and the generic YAML Story 2, with both MP4s, contact sheets, WAVs and event cues available in [artifact 13342734940](https://github.com/mdussere/tanstaafllm/actions/runs/41869289272/artifacts/13342734940) (retention 7 days). The rebuilt YAML film reordered the narrative and changed scene-specific beats; the soundtrack's use of 2A03 and 120 BPM does not preserve the original event-driven score. Full detail: [0303_06](0303_06_story2_reference_regression.md).

## Pixel-art assets and actual Git transfer state

**Update 2026-11-04, verified:** the complete source PNG pack is now directly committed on GitHub, branch `cell/adam`, at [commit `13fde527`](https://github.com/mdussere/tanstaafllm/commit/13fde5270fe96c5d8db32b2ea5829036d8ac7c5b). The transfer used GitHub's binary `create_blob` API and SHA verification; no workstation patch is needed. The source directory is [`worklines/hazel/video/common/art/sprites-v3/`](https://github.com/mdussere/tanstaafllm/tree/cell/adam/worklines/hazel/video/common/art/sprites-v3), containing **50 files** (artist-created PNG assets and animation frames, plus `manifest.json` and README). The auto-generated contact sheet was intentionally excluded. The old local patch and bundle are **obsolete and must not be applied**.

The pre-existing Story 3 renderer still uses SVG V2 and has *not* been migrated to use these PNGs. Also, the Story 3 workflow was switched to **preview only** in [commit `29cbbb8`](https://github.com/mdussere/tanstaafllm/commit/29cbbb80f0ba6975078ddb8121ee9ba994c967fd), so user approval still gates any future full-resolution render.

## Next actions for Hazel

1. ✅ Source PNG asset bytes and the exact manifest already ingested and verified on `cell/adam` (commit `13fde527`): 50 committed source files; no generated contact sheet. Use the committed assets, not the obsolete local transfer patch.
2. Swap raster frame sequences in a dedicated sprite renderer without using live SVG rotation; integer nearest-neighbour scaling and fixed pivots.
3. Reuse the original series opener/theme and compose event-specific score cues, not one global groove.
4. Render **13-scene preview only** at 640×360 / 10fps. Inspect the contact sheet and compare against original Story 2's shot rhythm and scores.
5. Deliver preview for Adam's artistic approval, then wait. No Full HD, merge or publication yet.

## Reply / acknowledgement

Hazel may record what is integrated and what is blocked under plan Step 3.3i and append a follow-up note. This note records user decisions and precise state, but does not independently green-light other worklines.
