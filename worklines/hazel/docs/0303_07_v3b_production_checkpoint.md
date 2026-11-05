# Story 3 — V3/V3b production checkpoint (bitmap sprites and music regression)

> **Recorded:** 2026-11-04 · **Workline:** Adam/ChatGPT → Hazel · **Status:** source PNGs committed to GitHub; bitmap renderer integration **not finished** · **Review boundary:** PREVIEW ONLY, no full render or public release without Adam's approval.

## Human review: preserve this feedback verbatim in intent

- The tiny **Hazel character vignettes are a good beginning**, but need polish.
- Hazel's feet must visibly rest on the bottom/ground line **of her vignette**, not float in the middle of a full-frame environment.
- The animated Hazel scene should occupy **at most half the surface**, with room for large key text, secondary messages, stage badges and stamps.
- A good balance was reached in the three local mockups: **budget** (sequence 02), **manual template library** (09) and **YAML compilation** (10).
- **Do not reuse that layout across the whole film.** Vary camera composition: short side-vignette explanation, prop close-up, wide workshop action and arcade title/reveal.
- The old Story 2 and trailer **beat-driven score and deliberate stage transitions** are the artistic reference. A continuously looping chiptune over a slide deck is not enough.
- The narrative must visibly explain: constraint (€20/month single Claude Pro subscription) → unexpectedly inventive first trailer → failure on a phone → costly repeated manual work → **first** extract template patterns → **then** compile them from YAML → this very film as an estimated self-payback joke.
- Stop at the **complete low-resolution preview** until the user approves it; do **not** trigger the full 1080p master.

## What exists outside GitHub, in this conversation's container

| Local file | Contents | Git commit? |
|---|---|---|
| `/mnt/data/hazel_story3_sprite_pack_v3.zip` | 51-entry 3.5 MB package: 6 Hazel poses, 12 props, 4 320×180 backgrounds, 5 frame-series loops, `manifest.json`, `README.md`, contact sheet | **YES** (50 source entries committed, excluding generated contact) |
| `/mnt/data/hazel_story3_pixel_sprite_pilot.mp4` | ~20 s experimental sprite animation | **NO** |
| `/mnt/data/hazel_story3_layout_previews/02_budget.png` | Approved layout mockup, compact Hazel scene + message board | **NO** |
| `/mnt/data/hazel_story3_layout_previews/09_library.png` | Approved library mockup | **NO** |
| `/mnt/data/hazel_story3_layout_previews/10_compiler.png` | Approved YAML compilation mockup | **NO** |
| `/mnt/data/hazel_story3_layout_previews/story3_v3_layout_pilot.mp4` | 12 s demonstration of layout, sprite frames and transitions | **NO** |
| `/mnt/data/TANSTAAFLLM_Story3_V3_PREVIEW.mp4` | Earlier 102-second V3 preview exported locally; **not** the post–Story-2-regression revision | **NO** |
| `/mnt/data/TANSTAAFLLM_Story3_V3_CONTACT.png` | Contact sheet for earlier V3 preview | **NO** |
| `/mnt/data/story3_v3b_work/contact.png` | Work-in-progress V3b contact sheet, **not** an approved new full preview | **NO** |
| `/mnt/data/story3_v3b_work/README.md` | Duplicate pack README (sprite constraints; no new renderer) | captured by this checkpoint |

These filesystem paths identify **conversation-local artifacts**, not GitHub links or durable storage. If they are needed by a future agent, transfer their actual bytes to the repository or a durable artifact store; a Markdown path alone does not preserve them.

**Pack checksum:** `sha256:470c8a048ed4a698c89a76b54a8454cedf6b2d80728d3623cec37a6cf5ef4da9`. The archive is 51 entries, including source artwork and frame PNGs.

## Asset manifest summary (from the local ZIP)

- Individual PNG sprites: `hazel_idle`, `hazel_work`, `hazel_reel`, `hazel_point`, `hazel_excited`, `hazel_walk`, `projector`, `reel`, `coin`, `purse`, `terminal`, `cartridge`, `yaml`, `phone`, `paper_stack`, `magnifier`, `workbench`, `beam`.
- Background plates: `workshop`, `screening`, `factory`, `arcade`, all 320×180.
- Animation groups: `reel_spin` (8 frames, 8 fps), `coin_insert` (6 frames, 10 fps), `hazel_reaction` (4 frames, 3 fps), `hazel_working` (4 frames, 4 fps), `hazel_walking` (4 frames, 5 fps).
- Assets must be read as RGBA with transparent pixels; frame rotation is **image substitution**, not a canvas transform. Keep fixed per-frame pivots and draw with `imageSmoothingEnabled=false`.

## GitHub baseline, verified 2026-11-04

- PR [#5](https://github.com/mdussere/tanstaafllm/pull/5) on `cell/adam` remains unmerged.
- `common/cinematic.js` and `common/art/cinema/*.svg` still implement the **rejected SVG V2 cut**, not the desired bitmap sprite system.
- `episodes/story3-insert-coin-how-we-made-videos.yaml` still describes the SVG cut.
- Story 2 regression was rebuilt successfully, [run #41869289272](https://github.com/mdussere/tanstaafllm/actions/runs/41869289272); original and generic reconstructions differ in narrative order, pictures and score. Detailed findings: [0303_06](0303_06_story2_reference_regression.md).
- No **new V3b MP4** is in the repo or an Actions artifact yet. Do not label the previous V3 video as the new reference-based preview.

## Remaining actions (not done by this checkpoint)

1. ✅ Commit the *actual PNG byte assets* and `manifest.json`: done on `cell/adam` in commit `13fde527`. Verify their proper alpha and anchors in the next rendering stage.
2. Implement the frame-switching asset loader and 4 scene framing families in the Hazel engine. Reuse original T01 title and NES score cues where artistically correct, but keep shot-specific cue timing.
3. Render an entire preview at 640×360/10fps, with the correct 13-scene narrative and named beat/stamp events.
4. Inspect contact sheet and listen to the score versus the hand-authored Story 2, then deliver preview for **Adam's approval**.
5. Only after approval render the 1080p final; no merge or public upload yet.

**Checkpoint scope:** documentation + recoverable inventory, not a completed asset ingestion or final film.

## Repository follow-up (2026-11-04)

The 50 source files are stored at `worklines/hazel/video/common/art/sprites-v3/` in commit `13fde527` and the preview-only CI constraint was enforced in `.github/workflows/hazel-story3-render.yml` commit `29cbbb8`. Earlier local transfer instructions are superseded. This does **not** mean the SVG-based renderer has been migrated or that a valid V3b preview has been created.
