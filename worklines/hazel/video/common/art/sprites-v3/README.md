# TANSTAAFLLM Hazel — bitmap sprite pack v3

Real PNG files extracted from the art generated in ChatGPT. Individual source artworks are trimmed and normalized; animation frames are separate RGBA images, not CSS/SVG transformations.

- sprites/: 6 Hazel poses + 12 reusable props
- animations/: 8 reel orientations, 6 coin-insert states, three Hazel pose-switch loops
- backgrounds/: four 320x180 pseudo-pixel-art backgrounds from the art board
- manifest.json: frame lists, timing, fixed dimensions, pivots

All texts critical to the story must still be rendered by Hazel using its existing fonts, not baked into assets. Keep original opening title/music and the 120 BPM stage cadence.

**Caveat**: Some original samples were cut from presentation sheets. They may require final art touch-ups to remove edge artifacts. Do not claim clean production sprites without checking the transparent borders and frames in a running scene.
