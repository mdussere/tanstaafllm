# Hello, Luna — TANSTAAFLLM story 1

The bring-up story (`docs/03_r36-ultra-bring-up-story.md`) played as an arcade game, in the series' look (`worklines/hazel/docs/0103_01_series-template.md`). The first cut was made by a sub-agent from the story page and the trailer's sources, and Hazel revised it on 2026-10-31. `NOTES.md` has the concept, the structure, the source of every fact, the reading audit and the sound.

`tanstaafllm-story1-hello-luna.mp4`: 1920 × 1080, 30 fps, H.264 + AAC, 94.0 s. The MP4 is not in Git.

## Re-render

```bash
worklines/hazel/video/story1-hello-luna/src/build.sh   # writes results/hazel/story1-hello-luna/<timestamp>/ (or OUT=…)
```

The build runs these steps:

1. the reading audit (`timing.py`, which must report +0.0 s of holds);
2. the NES-chip score (`score.py` + `nes.py` → `music.wav` and `hits.json`);
3. the frame capture and the encode (`capture.py`);
4. the stills and contact sheets;
5. a loudness summary.

It needs `ffmpeg` and this repository's uv project (Playwright with Chromium, numpy, Pillow).

## Licences

- **Fonts:** Press Start 2P and VT323, under the SIL OFL 1.1 (their licence texts are in `src/fonts/`).
- **Music and sound effects:** synthesised from scratch by `src/score.py`.
- **Key art:** the project's own `art/wallpaper.png`.
