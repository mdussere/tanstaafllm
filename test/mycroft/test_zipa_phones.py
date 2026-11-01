"""ZIPA-T small (INT8) phone recognition against eSpeak's expected phones (plan step 11.5).

Offline scoring, not live: each file is decoded once by Sherpa's own
`sherpa-onnx-offline` binary (one fresh process, 2 threads), so load time,
seconds of compute per second of audio and peak RSS (kernel `wait4`) are
comparable with Mycroft's other measures. Phones are compared with
`phone_score.py`.

Corpus: the two LibriSpeech clips shipped with the English Zipformer 20M (a
native-speaker floor for the notation mismatch), and optionally the user's
consented English reading (MYCROFT_PRIVATE_READING_EN, script docs/1003_01; the
user also read the sentence numbers, so they are part of the expected text).

Marker: integration (needs MYCROFT_ASSET_ROOT with the x64 runtime, the
English Zipformer 20M clips and `zipa-small-noncausal-500k`; and espeak-ng).
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import pytest


REPO = Path(__file__).parents[2]
SPEC = importlib.util.spec_from_file_location("phone_score", REPO / "worklines/mycroft/scripts/phone_score.py")
assert SPEC and SPEC.loader
score = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = score
SPEC.loader.exec_module(score)

RUNTIME = "sherpa-onnx-v1.13.8-linux-x64-shared-no-tts"
ZIPA = "zipa-small-noncausal-500k"
INT8 = "epoch-999-avg-1.int8.onnx"
CLIPS = "sherpa-onnx-streaming-zipformer-en-20M-2023-02-17"
THREADS = 2
NUMBERS = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen".split()


def _corpus(root: Path, scratch: Path) -> list[tuple[str, Path, str]]:
    items = []
    for line in (root / CLIPS / "test_wavs" / "trans.txt").read_text(encoding="utf-8").splitlines():
        name, text = line.split(maxsplit=1)
        if name != "8k.wav":
            items.append((name, root / CLIPS / "test_wavs" / name, text.lower()))
    reading = os.environ.get("MYCROFT_PRIVATE_READING_EN")
    if reading and Path(reading).is_file():
        wav = scratch / "reading.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", reading, "-ac", "1", "-ar", "16000",
                        "-sample_fmt", "s16", str(wav)], check=True)
        script = (REPO / "worklines/mycroft/docs/1003_01_english-reading-script.md").read_text(encoding="utf-8")
        truth = script.split("## Canonical ground truth", 1)[1]
        sentences = [line[2:] for line in truth.splitlines() if line.startswith("> ")]
        text = " ".join(f"{number}. {sentence}" for number, sentence in zip(NUMBERS, sentences))
        items.append(("private-reading", wav, text))
    return items


def _decode(root: Path, wav: Path) -> dict:
    zipa = root / ZIPA
    process = subprocess.Popen(
        [str(root / RUNTIME / "bin" / "sherpa-onnx-offline"), f"--tokens={zipa}/tokens.txt",
         f"--encoder={zipa}/encoder-{INT8}", f"--decoder={zipa}/decoder-{INT8}", f"--joiner={zipa}/joiner-{INT8}",
         f"--num-threads={THREADS}", "--provider=cpu", str(wav)],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = process.stdout.read().decode("utf-8", "replace")
    _, status, usage = os.wait4(process.pid, 0)
    # Sherpa's JSON line is not always valid JSON (token lists can break it); take the text field.
    text = re.search(r'"text": "(.*?)", "timestamps"', output)
    decode = re.search(r"Elapsed seconds: ([\d.]+) s\s+Real time factor \(RTF\): [\d.]+ / ([\d.]+)", output)
    return {
        "exit_status": os.waitstatus_to_exitcode(status),
        "ipa": text.group(1) if text else "",
        "decode_s": float(decode.group(1)),
        "audio_s": float(decode.group(2)),
        "peak_rss_mib": round(usage.ru_maxrss / 1024, 1),
        "cpu_s": round(usage.ru_utime + usage.ru_stime, 3),
    }


@pytest.mark.integration
@pytest.mark.timeout(600)
def test_zipa_phones_against_espeak(tmp_path: Path) -> None:
    root_text = os.environ.get("MYCROFT_ASSET_ROOT")
    if not root_text or not shutil.which("espeak-ng"):
        pytest.skip("MYCROFT_ASSET_ROOT and espeak-ng are needed")
    root = Path(root_text)
    if not (root / ZIPA / f"encoder-{INT8}").is_file():
        pytest.skip(f"{ZIPA} is not installed under MYCROFT_ASSET_ROOT")

    report: dict = {"threads": THREADS, "host": os.uname().nodename, "machine": os.uname().machine, "items": []}
    for name, wav, text in _corpus(root, tmp_path):
        run = _decode(root, wav)
        expected = score.espeak_phones(text)
        rate, confusions = score.align(expected, score.phones(run["ipa"]))
        run.update(item=name, text=text, expected="".join(expected), per=round(rate, 3),
                   top_confusions=Counter(confusions).most_common(15))
        report["items"].append(run)

    evidence = REPO / "results/mycroft/zipa" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evidence.mkdir(parents=True)
    (evidence / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert all(item["exit_status"] == 0 and item["ipa"] for item in report["items"])
