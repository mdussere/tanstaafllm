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

The **source PNG sprite pack exists locally only**. It contains 6 character poses, 12 props, 4 backgrounds, the original illustrated frame sequences for reel (8), coin (6) and Hazel reaction/work/walk (4 each), and their exact manifest (`manifest.json`). Local source archive: `/mnt/data/hazel_story3_sprite_pack_v3.zip` (3.5 MB). Detailed inventory and checksum: [0303_07](0303_07_v3b_production_checkpoint.md).

A complete binary Git commit was prepared in the ChatGPT execution container:
- local Git commit: `cbc3d127961eeb27d07d1331cd5a525c5c52a922`;
- local mbox patch: `/mnt/data/hazel-story3-v3-sprite-pack-commit.patch` (~4.5 MB);
- compressed patch: `/mnt/data/hazel-story3-v3-sprite-pack-commit.patch.gz`;
- self-contained Git bundle: `/mnt/data/hazel-story3-v3-sprites.bundle` (~3 MB).

**IMPORTANT:** The GitHub connector cannot access those container filesystem bytes, and the container has no DNS access to github.com. Therefore the local binary commit is **not pushed to GitHub**. The notes and plan are pushed; the PNGs remain the transfer blocker. Never claim that the PNGs are committed to remote `cell/adam` unless the tree includes `worklines/hazel/video/common/art/sprites-v3/*.png`.

### Applying the exact prepared asset commit on an authenticated development workstation

From a clean clone of `mdussere/tanstaafllm` with `cell/adam` checked out, after copying the attached full mbox patch to the machine:

```sh
git switch cell/adam
git status --short          # must be clean
git am --3way /path/to/hazel-story3-v3-sprite-pack-commit.patch
git status --short
git log -1 --oneline
git push origin cell/adam
```

Use **either** the mbox patch **or** the bundle, not both. The mbox applies as a new commit without rewriting prior branch history and preserves binary files and the source manifest; if the branch has new unrelated changes it should still apply, but inspect conflicts. All generated MP4/WAV/frame outputs remain outside Git, in CI artifacts.

## Next actions for Hazel

1. Ingest actual bitmap asset bytes into the remote `cell/adam` branch. Verify all 51 source files and manifest SHA against the local archive. Prevent accidental source-asset omissions.
2. Swap raster frame sequences in a dedicated sprite renderer without using live SVG rotation; integer nearest-neighbour scaling and fixed pivots.
3. Reuse the original series opener/theme and compose event-specific score cues, not one global groove.
4. Render **13-scene preview only** at 640×360 / 10fps. Inspect the contact sheet and compare against original Story 2's shot rhythm and scores.
5. Deliver preview for Adam's artistic approval, then wait. No Full HD, merge or publication yet.

## Reply / acknowledgement

Hazel may record what is integrated and what is blocked under plan Step 3.3i and append a follow-up note. This note records user decisions and precise state, but does not independently green-light other worklines.
