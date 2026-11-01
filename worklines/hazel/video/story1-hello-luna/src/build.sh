#!/usr/bin/env bash
# Re-render "Hello, Luna" (TANSTAAFLLM story 1): reading audit, soundtrack, frames, encode, stills.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PROJECT="${PROJECT:-$(cd "$HERE/../../../../.." && pwd)}"   # the repository root: only its uv environment is used
OUT="${OUT:-$PROJECT/results/hazel/story1-hello-luna/$(date +%Y%m%dT%H%M%S)}"   # renders stay out of Git
mkdir -p "$OUT"
PY=(uv run --project "$PROJECT" python)

"${PY[@]}" "$HERE/timing.py" --json "$HERE/holds.json"          # must report +0.0 s of holds
"${PY[@]}" "$HERE/score.py" "$OUT/music.wav"                     # also writes hits.json
"${PY[@]}" "$HERE/capture.py" video "$OUT/tanstaafllm-story1-hello-luna.mp4" --fps 30 --audio "$OUT/music.wav"
mkdir -p "$OUT/stills"
"${PY[@]}" "$HERE/capture.py" stills "$OUT/stills" 3.5 10.5 14.5 16.8 18.9 21.0 22.7 25.6 30 32.8 38.8 42 46.8 52.5 58 65 68.5 72.8 77.7 80 86 91
"${PY[@]}" "$HERE/contact.py" "$OUT/contact" "$OUT"/stills/t*.png
ffprobe -v error -show_entries format=duration:stream=codec_name,width,height,r_frame_rate -of compact "$OUT/tanstaafllm-story1-hello-luna.mp4"
ffmpeg -hide_banner -i "$OUT/tanstaafllm-story1-hello-luna.mp4" -af ebur128=peak=true -f null - 2>&1 | grep -A14 Summary
