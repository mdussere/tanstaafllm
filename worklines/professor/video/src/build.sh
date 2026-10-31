#!/usr/bin/env bash
# Re-render the whole video: soundtrack, frames, encode. Run from anywhere.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PROJECT="${PROJECT:-$(cd "$HERE/../../../.." && pwd)}"   # the repository root: its uv project has playwright, numpy, pillow
OUT="${OUT:-$PROJECT/results/professor/video/$(date +%Y%m%dT%H%M%S)}"   # renders stay out of Git
mkdir -p "$OUT"
PY=(uv run --project "$PROJECT" python)

# the soundtrack: an emulated NES 2A03 chip (score.py + nes.py), final as rendered
"${PY[@]}" "$HERE/score.py" "$OUT/build_music.wav"
"${PY[@]}" "$HERE/capture.py" video "$OUT/tanstaafllm.mp4" --fps 30 --audio "$OUT/build_music.wav"
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of compact "$OUT/tanstaafllm.mp4"
