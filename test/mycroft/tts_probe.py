"""Synthesise sentences with one Sherpa-ONNX TTS model, in its own process (plan step 11.2).

Run by `test_tts_candidates.py` through `uv run --no-project --with sherpa-onnx==1.13.8`,
so the desk project needs no TTS dependency. Prints one JSON object: load time,
per-sentence synthesis time and audio length; writes one WAV per sentence.

    python tts_probe.py KIND MODEL_DIR OUT_DIR THREADS < sentences.txt
"""

from __future__ import annotations

import json
import resource
import sys
import time
import wave
from pathlib import Path

import sherpa_onnx


def model_config(kind: str, d: Path, threads: int) -> sherpa_onnx.OfflineTtsModelConfig:
    common = {"tokens": str(d / "tokens.txt"), "data_dir": str(d / "espeak-ng-data")}
    if kind == "vits":
        onnx = next(p for p in d.glob("*.onnx"))
        model = {"vits": sherpa_onnx.OfflineTtsVitsModelConfig(model=str(onnx), **common)}
    elif kind == "kitten":
        model = {"kitten": sherpa_onnx.OfflineTtsKittenModelConfig(model=str(d / "model.int8.onnx"), voices=str(d / "voices.bin"), **common)}
    elif kind == "kokoro":
        model = {"kokoro": sherpa_onnx.OfflineTtsKokoroModelConfig(model=str(d / "model.int8.onnx"), voices=str(d / "voices.bin"), **common)}
    else:
        raise SystemExit(f"unknown kind {kind}")
    return sherpa_onnx.OfflineTtsModelConfig(num_threads=threads, provider="cpu", **model)


def main(argv: list[str]) -> int:
    kind, model_dir, out_dir, threads = argv[1], Path(argv[2]), Path(argv[3]), int(argv[4])
    sentences = [line.strip() for line in sys.stdin if line.strip()]
    out_dir.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    tts = sherpa_onnx.OfflineTts(sherpa_onnx.OfflineTtsConfig(model=model_config(kind, model_dir, threads)))
    report = {"load_s": round(time.monotonic() - started, 3), "sample_rate": tts.sample_rate, "sentences": []}
    for index, text in enumerate(sentences):
        started = time.monotonic()
        audio = tts.generate(text, sid=0, speed=1.0)
        elapsed = time.monotonic() - started
        seconds = len(audio.samples) / audio.sample_rate
        path = out_dir / f"{index:02d}.wav"
        with wave.open(str(path), "wb") as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(audio.sample_rate)
            out.writeframes(b"".join(int(max(-1.0, min(1.0, s)) * 32767).to_bytes(2, "little", signed=True) for s in audio.samples))
        report["sentences"].append({"text": text, "synth_s": round(elapsed, 3), "audio_s": round(seconds, 3), "wav": str(path)})
    report["peak_rss_mib"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, 1)
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
