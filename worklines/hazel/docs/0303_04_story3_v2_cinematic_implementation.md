# Story 3 v2 — cinematic implementation and review checklist

> **Freshness:** 🟡 implementation in progress · **Written:** 2026-11-04 · **Workline:** Hazel 3.3 / Adam · **User direction:** full autonomy to MP4, branch/PR only, no publication

## Reason for this revision

Adam judged the first complete cut too much like a software slide deck; the reused stage, table and two-box templates did not match an introspective movie about filmmaking. The new cut replaces the generic template selections in all 13 scenes with a single **configurable layer-composition engine**. It does **not** duplicate 13 bespoke JS functions.

## Creative arc — 13 scenes, 112 seconds

1. **Insert coin.** An arcade projector lights up, an actual coin enters the picture.
2. **The constraint.** Hazel, one purse, €20/month Claude Pro for the whole cell; the film itself costs intelligence.
3. **The first trailer.** A brief, a projector, a surprising arcade game world.
4. **The first toolchain.** Clockwork reel and film strip synchronize canvas time, NES music and encoding.
5. **The first criticism.** A giant phone and physical inspection show that looking good on the workstation was not enough.
6. **The bill.** A hand-drawn full episode used approximately 290k tokens.
7. **The costly loop.** Paper copies accumulate: copying code reproduces its bugs.
8. **First rationalize.** Extract reusable cartridges from the handmade episodes; every future film must add a novel one.
9. **Then automate.** The YAML recipe activates a factory of deterministic frames/music/tests.
10. **Honest comparison.** The 290k full handmade film and 54k scripted *revision* did not have equivalent scopes.
11. **Return to creativity.** The system takes over the repeated craft; Hazel retains story direction.
12. **Self-reference.** Projection screen loops into itself; the screen displays Story 3 as its own second script-built movie. The ~1.73 uses figure remains an unverified projection.
13. **Quiet closure.** The coin returns; the original TANSTAAFLLM motto ends the film.

## Technical pieces

- `video/common/art/cinema/*.svg`: **20 separate source assets** (4 environmental plates, 4 consistent Hazel poses, 12 props/FX); SVG is used so every asset is separately committed, resolution independent and transparency preserving. These are deliberately **procedurally authored vector/pixel blocks**, not raster exports from the ImageGen reference board. The character/reference sheet generated in conversation is an editorial guide; there is no claim that the shipped assets are its pixel-perfect cutouts.
- `video/common/art/cinema/manifest.yaml`: native sizes and pivots for future asset validation.
- `video/common/cinematic.js`: reuses these images with parametric composition slots, positions, z-order, opacity, movement presets, rotation and timing. Finite mechanical effects add film strips, a rack of cartridges, copies, an assembly line, receipts and a recursive projector.
- `video/common/layout.py` `f_cinema`: resolves a new frame template **T24**, records large key and secondary text slots for the existing reading audit.
- `video/common/templates.js`: T24 delegates to the shared cinematic compositor.
- `video/common/cues.py`: T24 has NES music cues without repetitive `CLEAR!` stamps.
- `video/common/build.py` / `runtime.js`: loads the compositing script and waits for the independent SVG assets before capture, preserving the existing 2A03 / Playwright / ffmpeg engine.
- `video/episodes/story3-insert-coin-how-we-made-videos.yaml`: 13 new layer recipes for one compositional language, 112 seconds.

**Important:** this is a working first implementation, not a verified production result until the associated CI run succeeds. Do not publish or merge before video review.

## Quality gate after GitHub Actions

1. **Rendering:** the video actually renders at 640×360/10 fps and 1920×1080/30 fps; assets are loaded (not invisible).
2. **Reading / layout:** `--strict` reports zero cut holds, text overlap, overflow, unsafe margins and key-message violations. Any text with a measured squeeze below 90% fails.
3. **Visual review:** inspect contact sheet for true on-screen action and continuity; avoid black screens and unreadable micro-UI, verify no baked-in text from SVG assets; ensure scenes 08–09 visibly differ.
4. **Narrative review:** the *two-film joke* is not spoiled before sequence 12; the business arithmetic clearly remains illustrative.
5. **Reuse review:** rebuild the same `cinema` template with at least two different background/prop packs without editing the renderer. Scene 02 vs scene 09 already proves this structurally, but visual review is needed.
6. **Cost:** track the full AI-session/token cost before claiming amortization as a measurement. The image-generation operations have their own usage cost; Actions is deterministic compute, not free energy.
7. **Production:** attach MP4, contact sheet, audit and lint to the open `cell/adam` PR. Keep master off `main` and do not upload to YouTube or Pages without approval.

## Known limits / deliberate compromises

- The vector asset pack is deliberately compact and source-editable. It may need a second, richer art pass to meet the illustrated character sheet's finish; the first priority was to test the layer grammar with real end-to-end rendering.
- The recursive shot is a **designed nested projector illusion**, not an actual live video feedback framebuffer.
- `cinematic.js` currently loads SVG files by filename registry; the manifest is documentation, not yet an executable loader.
- No speech narration was requested; the existing NES score remains the soundtrack.

## Evidence

- [Story 3 PR #5](https://github.com/mdussere/tanstaafllm/pull/5)
- [Original creative alternatives](0303_02_story3-two-concepts-per-sequence.md)
- [Asset and composition plan](0303_03_story3-modular-asset-production-plan.md)
