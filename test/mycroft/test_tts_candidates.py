"""English text-to-speech candidates on the desk host (plan step 11.2).

Each model runs in a fresh process (`tts_probe.py`, Sherpa-ONNX 1.13.8's Python
wheel, 2 threads), so load time, real-time factor and peak RSS (the probe's own
`getrusage`) are comparable. The WAVs go to the ignored results/ for the user to listen to;
step 11.4's assessment tools may later score them automatically.

Marker: integration (needs MYCROFT_TTS_ROOT with the extracted model folders).
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import wave
from datetime import datetime, timezone
from pathlib import Path

import pytest


REPO = Path(__file__).parents[2]
PROBE = Path(__file__).with_name("tts_probe.py")
THREADS = 2
CANDIDATES = {
    "piper-lessac-medium-int8": ("vits", "vits-piper-en_US-lessac-medium-int8"),
    "piper-alan-medium-int8": ("vits", "vits-piper-en_GB-alan-medium-int8"),
    "kitten-nano-v0.8-int8": ("kitten", "kitten-nano-en-v0_8-int8"),
    "kokoro-v0.19-int8": ("kokoro", "kokoro-int8-en-v0_19"),
}
# Mike's and the English tutor's kind of sentences, plus the project's names.
SENTENCES = [
    "Good morning. The battery is at eighty percent and charging.",
    "I opened the calculator. Twelve and thirty make forty-two.",
    "Say it after me: there ain't no such thing as a free lunch.",
    "Mycroft is listening, and Wyoh has arranged the windows on Luna.",
    "Close, but the vowel in 'ship' is shorter than in 'sheep'. Try again.",
]


@pytest.mark.integration
@pytest.mark.timeout(900)
def test_english_tts_candidates() -> None:
    root_text = os.environ.get("MYCROFT_TTS_ROOT")
    if not root_text:
        pytest.skip("MYCROFT_TTS_ROOT is not set; TTS models are external to the repository")
    root = Path(root_text)
    evidence = REPO / "results/mycroft/tts" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report: dict = {"threads": THREADS, "host": os.uname().nodename, "machine": os.uname().machine, "results": {}}
    for name, (kind, dirname) in CANDIDATES.items():
        if not (root / dirname).is_dir():
            continue
        process = subprocess.Popen(
            ["uv", "run", "--no-project", "--quiet", "--with", "sherpa-onnx==1.13.8", "python", str(PROBE),
             kind, str(root / dirname), str(evidence / name), str(THREADS)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate("\n".join(SENTENCES).encode("utf-8"))
        run = json.loads(out.decode("utf-8").strip().splitlines()[-1]) if process.returncode == 0 else {"error": err.decode()[-2000:]}
        report["results"][name] = run
    _round_trip(report)
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert report["results"] and all("error" not in run for run in report["results"].values())


def _round_trip(report: dict) -> None:
    """Intelligibility check: Kroko English transcribes each WAV back (needs MYCROFT_ASSET_ROOT)."""
    root_text = os.environ.get("MYCROFT_ASSET_ROOT")
    if not root_text:
        return
    modules = {}
    for name in ("mycroft_console", "benchmark_asr"):
        spec = importlib.util.spec_from_file_location(name, REPO / f"worklines/mycroft/scripts/{name}.py")
        modules[name] = importlib.util.module_from_spec(spec)
        sys.modules[name] = modules[name]
        spec.loader.exec_module(modules[name])
    asr = modules["mycroft_console"].SherpaStreamingRecognizer(Path(root_text), num_threads=2, model="kroko-en-2025")
    try:
        for run in report["results"].values():
            errors = []
            for sentence in run.get("sentences", []):
                wav16 = sentence["wav"].replace(".wav", ".16k.wav")
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", sentence["wav"], "-ar", "16000", wav16], check=True)
                asr.reset()
                with wave.open(wav16, "rb") as source:
                    while pcm := source.readframes(3200):
                        asr.accept_pcm(pcm, 16000)
                sentence["kroko_en"] = asr.finish()
                errors.append(modules["benchmark_asr"].word_error_rate(sentence["text"], sentence["kroko_en"]))
            if errors:
                run["round_trip_wer"] = round(sum(errors) / len(errors), 3)
    finally:
        asr.close()
