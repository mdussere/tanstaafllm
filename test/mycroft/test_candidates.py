"""Lighter-model candidates against the current model (plan steps 9.3 and 9.6).

Each candidate is decoded by Sherpa's own prebuilt binary (`bin/sherpa-onnx`),
one fresh process per file, so load time, real-time factor and peak RSS
(kernel `wait4`) are comparable. Word error rate uses the Step 3 harness's
normalisation (`benchmark_asr.py`: NFC, lower case, punctuation ignored).

Corpus:
  * the current model's three public Common Voice clips (references in its
    `trans.txt`; that model was trained on Common Voice, which favours it);
  * optionally the user's consented private reading (MYCROFT_PRIVATE_READING,
    the M4A behind docs/0104_06), referenced by docs/0105_01. It is converted
    in a temporary directory only; its transcripts go to the ignored results/.

Marker: integration (needs MYCROFT_ASSET_ROOT with the x64 runtime, the current
model, and `sherpa-onnx-streaming-zipformer-fr-kroko-2025-08-06`).
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest


REPO = Path(__file__).parents[2]
SPEC = importlib.util.spec_from_file_location("benchmark_asr", REPO / "worklines/mycroft/scripts/benchmark_asr.py")
assert SPEC and SPEC.loader
benchmark = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = benchmark
SPEC.loader.exec_module(benchmark)

RUNTIME = "sherpa-onnx-v1.13.8-linux-x64-shared-no-tts"
CURRENT = "sherpa-onnx-streaming-zipformer-fr-2023-04-14"
KROKO = "sherpa-onnx-streaming-zipformer-fr-kroko-2025-08-06"
INT8 = "epoch-29-avg-9-with-averaged-model.int8.onnx"
THREADS = 2


def _candidates(root: Path) -> dict[str, list[str]]:
    current, kroko = root / CURRENT, root / KROKO
    return {
        "current-int8": [f"--tokens={current}/tokens.txt", f"--encoder={current}/encoder-{INT8}",
                         f"--decoder={current}/decoder-{INT8}", f"--joiner={current}/joiner-{INT8}"],
        "kroko-fp32": [f"--tokens={kroko}/tokens.txt", f"--encoder={kroko}/encoder.onnx",
                       f"--decoder={kroko}/decoder.onnx", f"--joiner={kroko}/joiner.onnx"],
    }


def _corpus(root: Path, scratch: Path) -> list[tuple[str, Path, str]]:
    items = []
    for line in (root / CURRENT / "test_wavs" / "trans.txt").read_text(encoding="utf-8").splitlines():
        name, reference = line.split(maxsplit=1)
        items.append((name, root / CURRENT / "test_wavs" / f"{name}.wav", reference))
    private = os.environ.get("MYCROFT_PRIVATE_READING")
    if private and Path(private).is_file():
        wav = scratch / "private-reading.wav"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", private, "-ac", "1", "-ar", "16000",
                        "-sample_fmt", "s16", str(wav)], check=True)
        script = (REPO / "worklines/mycroft/docs/0105_01_representative-reading-script.md").read_text(encoding="utf-8")
        truth = script.split("## Canonical ground truth", 1)[1]
        reference = " ".join(line[2:] for line in truth.splitlines() if line.startswith("> "))
        items.append(("private-reading", wav, reference))
    return items


def _run(binary: Path, args: list[str], wav: Path) -> dict:
    started = os.times().elapsed
    process = subprocess.Popen([str(binary), *args, f"--num-threads={THREADS}", "--provider=cpu", str(wav)],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = process.stdout.read().decode("utf-8", "replace")
    _, status, usage = os.wait4(process.pid, 0)
    wall = os.times().elapsed - started
    lines = output.splitlines()
    rtf_index = next(i for i, line in enumerate(lines) if "Real time factor" in line)
    created = re.search(r"Recognizer created in ([\d.]+)", output)
    decode = re.search(r"Elapsed seconds: ([\d.e+]+), Audio duration \(s\): ([\d.e+]+)", output)
    return {
        "exit_status": os.waitstatus_to_exitcode(status),
        "text": lines[rtf_index + 1].strip() if rtf_index + 1 < len(lines) else "",
        "load_s": float(created.group(1)) if created else None,
        "decode_s": float(decode.group(1)) if decode else None,
        "audio_s": float(decode.group(2)) if decode else None,
        "wall_s": round(wall, 3),
        "peak_rss_mib": round(usage.ru_maxrss / 1024, 1),
        "cpu_s": round(usage.ru_utime + usage.ru_stime, 3),
    }


@pytest.mark.integration
@pytest.mark.timeout(900)
def test_lighter_candidates_against_the_current_model(tmp_path: Path) -> None:
    root_text = os.environ.get("MYCROFT_ASSET_ROOT")
    if not root_text:
        pytest.skip("MYCROFT_ASSET_ROOT is not set; pinned assets are external to the repository")
    root = Path(root_text)
    if not (root / KROKO / "encoder.onnx").is_file():
        pytest.skip(f"{KROKO} is not installed under MYCROFT_ASSET_ROOT")
    binary = root / RUNTIME / "bin" / "sherpa-onnx"

    report: dict = {"threads": THREADS, "host": os.uname().nodename, "machine": os.uname().machine, "results": {}}
    for name, args in _candidates(root).items():
        rows = []
        for item, wav, reference in _corpus(root, tmp_path):
            run = _run(binary, args, wav)
            run.update(item=item, reference=reference, wer=benchmark.word_error_rate(reference, run["text"]))
            rows.append(run)
        report["results"][name] = rows

    evidence = REPO / "results/mycroft/candidates" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evidence.mkdir(parents=True)
    (evidence / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for rows in report["results"].values():
        assert all(row["exit_status"] == 0 and row["text"] for row in rows)
