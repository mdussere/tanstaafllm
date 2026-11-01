#!/usr/bin/env bash
# Re-render "Ask the desktop" (TANSTAAFLLM story 2, Wyoh): reading audit, soundtrack, frames, encode, stills.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PROJECT="${PROJECT:-$(cd "$HERE/../../../../.." && pwd)}"   # the repository root: only its uv environment is used
OUT="${OUT:-$PROJECT/results/hazel/story2-ask-the-desktop/$(date +%Y%m%dT%H%M%S)}"   # renders stay out of Git
NAME=tanstaafllm-story2-ask-the-desktop
mkdir -p "$OUT"
PY=(uv run --project "$PROJECT" python)

"${PY[@]}" "$HERE/timing.py" --json "$HERE/holds.json"          # must report +0.0 s of holds
"${PY[@]}" "$HERE/score.py" "$OUT/music.wav"                     # also writes hits.json
"${PY[@]}" "$HERE/capture.py" video "$OUT/$NAME.mp4" --fps 30 --audio "$OUT/music.wav"
mkdir -p "$OUT/stills"
"${PY[@]}" "$HERE/capture.py" stills "$OUT/stills" 3.5 11 15.5 19.5 22.8 27.5 31.2 35.5 38.5 43.5 45.5 51.5 55 57.4 61.5 65.5 71.5 74.5 77 83.5 89
"${PY[@]}" "$HERE/contact.py" "$OUT/contact" "$OUT"/stills/t*.png
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of compact "$OUT/$NAME.mp4"
ffmpeg -hide_banner -i "$OUT/$NAME.mp4" -af ebur128=peak=true -f null - 2>&1 | grep -A14 Summary
