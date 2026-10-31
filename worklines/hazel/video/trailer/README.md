# TANSTAAFLLM — the video

Made by a sub-agent from the README and the `docs/` pages only, plus the key art (2026-10-25). The rendered MP4 is not in Git: rebuild it with `src/build.sh`.

`tanstaafllm.mp4`: 1920 × 1080, 30 fps, H.264 (high profile, yuv420p) + AAC 48 kHz stereo, 60 s of choreography plus the reading holds of `src/holds.json` (86.5 s on 2026-10-31).

## Re-render

```bash
worklines/professor/video/src/build.sh            # writes results/professor/video/<timestamp>/ (or OUT=…)
```

It needs `ffmpeg`, `uv` and a Python project that provides Playwright (with Chromium), numpy and Pillow. By default it uses
this repository's uv project; set `PROJECT=/path/to/project` to use another one. A full render takes about 6–7 minutes.

What it does:
1. `src/music.py` synthesises the soundtrack and every sound effect with numpy → `build_music_raw.wav`.
2. ffmpeg softens the top end and limits the peaks → `build_music.wav` (about −15 LUFS integrated, peaks at about −1 dBFS).
3. `src/capture.py video` serves `src/` over a local HTTP server, opens `src/index.html` in headless Chromium, calls `renderFrame(t)` for each of the 1800 frames, and pipes the screenshots straight into ffmpeg with the music.

## Look at one moment

```bash
cd worklines/professor/video/src
uv run --project ../../../.. python capture.py stills /tmp/tanstaafllm-check/stills 12.5 30 58.6
uv run --project ../../../.. python contact.py /tmp/tanstaafllm-check/sheet /tmp/tanstaafllm-check/stills/*.png
```

You can also serve `src/` (for example `python -m http.server` in `src/`) and open `index.html?t=12.5` for a single frame, or `index.html?play` to watch it loop without sound.

## Files

| Path | What |
|---|---|
| `src/index.html` | The whole picture: a 1920 × 1080 canvas, and every frame is a pure function of time. |
| `src/capture.py` | Frame capture with Playwright, and ffmpeg encoding. |
| `src/score.py`, `src/nes.py` | The soundtrack: an emulated NES 2A03 sound chip (two pulses, a triangle, noise; mono; 60 Hz frames), composed by a sub-agent from the cue sheet (version A, kept by the user on 2026-10-30) and fitted to the cut. |
| `src/build.sh` | One-command rebuild. |
| `src/contact.py` | Contact sheets for frame inspection. |
| `src/timing.py`, `src/holds.json` | Reading-time audit, and the holds that keep each screen's last text readable (see NOTES.md). |
| `src/art/wallpaper.png` | The project's key art, copied unchanged from the package. |
| `src/fonts/` | Press Start 2P and VT323, both SIL Open Font License 1.1 (licence texts beside them). |
| `NOTES.md` | Concept, structure, and every fact and figure with its source page. |

## Licences

- **Fonts:** Press Start 2P (© 2012 The Press Start 2P Project Authors, cody@zone38.net) and VT323 (© 2011 The VT323 Project Authors). Both under the SIL OFL 1.1, downloaded from github.com/google/fonts.
- **Music and sound effects:** synthesised from scratch by `src/music.py`. No samples, no third-party music.
- **Key art:** the project's own `art/wallpaper.png`.
