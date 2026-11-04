# Story 3 — bitmap sprites v3: extraction, frame replacement and rhythm

> **Date:** 2026-11-04 · **Workline:** Adam → Hazel · **Status:** local sprite-pack and animated pilot produced; GitHub CI asset ingestion remains pending.

## User feedback driving the change

The first SVG-driven cinematic cut is aesthetically too flat and does **not** look like an authentic late-1980s/early-1990s arcade game. The original video series' stamped title, fixed musical motifs, emphatic beat-by-beat transitions and readable story beats must return. Rather than dynamically rotating SVGs, use **pre-drawn PNG animation frames** in fixed-size atlases or individual transparent PNGs. Rotating the film reel is a series of eight illustrated poses; inserting a coin is a series of six pre-rendered views. Hazel expressions are different supplied frames, not a morph.

## Produced outside GitHub

An **asset pack was actually generated and checked**, using the ChatGPT image-created character and props sheets. It contains:

- 6 distinct Hazel RGBA poses (idle, work, reel, point, excited, walk);
- 12 separate pixel-art props including projector, film reel, coin, purse, terminal, cartridge, YAML document, phone, paper stack, magnifier, workbench and projector light;
- four cropped 320×180 background plates;
- 8 pre-rendered reel orientations;
- 6 coin insertion frames;
- three four-frame Hazel pose cycles;
- a machine-readable `manifest.json` with frame paths, frame rates, sizes and pivot points;
- contact sheet and a 20-second locally rendered 960×540/12fps MP4 pilot using frame replacement rather than browser rotation.

The PNG extraction is **local to the ChatGPT artifact filesystem**, not yet pushed as binary objects to this repository. The original source images are generated conversation attachments, not available to the GitHub runner. **Do not claim the assets are uploaded to GitHub or the new master is rendered in CI.** The first stage is completed; GitHub binary ingestion and integration remain the next task.

## Proposed engine contract (after PNGs arrive in the repository)

```yaml
layers:
  - slot: hazel
    sprite: hazel_reaction
    frame_at: scene_seconds
    frame_rate: 3
    loop: true
    anchor: bottom-center
    x: 120
    y: 840
  - slot: reel
    sprite: reel_spin
    frame_rate: 8
    loop: true
    x: 1070
    y: 340
  - slot: coin
    sprite: coin_insert
    frame_rate: 10
    loop: false
    trigger: drop_coin
```

**Rule:** Draw selected bitmap frame with `imageSmoothingEnabled=false`; no runtime rotation, CSS filter or antialiased scaling. Layout uses 320×180 or 480×270 logical pixels scaled by integer factors, normalizing transparent sprite pivots. Multiple poses can be compiled into regular fixed-frame atlases for fewer network loads; transparency must remain valid.

## Return to the original Hazel identity

1. Restore the original `title_card`/T01 at the opening, including the established title slam, coin intro and musical theme.
2. Introduce sprite-background transitions at **120 BPM**, with distinct 4- or 8-bar phrases and strong transition drums/impact SFX.
3. Preserve the source video series' punchy `CLEAR!`, cut flash, and NES chiptune cues selectively, not on every shot; a cinematic scene is not automatically a T05 stage.
4. The story must make each step visually explicit: **budget** → **unexpected first trailer** → **phone/sound failures** → **expensive handmade repetition** → **manual template library** → **YAML compilation** → **self-referential reveal**. Do not put the measured-revision vs full-film numbers on screen as equivalent facts.
5. The final beat must explicitly say Story 3 is the **second** film built with the pipeline, which is a narrative illustration of an *estimated* payback, not verified economics.
6. Prefer a small number of reusable compositional backdrops and sprite loops; introduce a new pose or action only when it communicates a plot event.

## Acceptance criteria for integrating this pack

- Real pixel sprites rather than vector approximations: no live SVG content in the new cut.
- No double-frames/bleed in the cropped source images or blurred pixel edges.
- Sprite animation looks coherent when cycling, with fixed anchor (feet/reel center).
- Preserve all original cinematic intro and NES audio motifs from Story 1/2 without replacing them with generic ambient music.
- Restore pacing and phone-readable labels (original layout audit).
- Render preview and full MP4 and inspect the contact sheet *before* requesting Adam's review.

The 20-second local pilot is only a **technology and style proof**, not an episode master and not approved for publication.
