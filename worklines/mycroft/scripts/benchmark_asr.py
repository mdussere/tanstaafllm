#!/usr/bin/env python3
"""Run one native ASR command per WAV fixture and write comparable JSON Lines.

The harness deliberately has no model downloader and no ASR dependency.  A candidate
JSON file names an already-installed native command, whose argument list contains one
``{audio}`` placeholder.  Its stdout parser is a regular expression with a named
``text`` group.  Everything else is recorded as raw diagnostics.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import subprocess
import sys
import time
import unicodedata
import wave
from pathlib import Path


POLL_SECONDS = 0.01


def normalise(text: str) -> list[str]:
    text = unicodedata.normalize("NFC", text).lower()
    return re.findall(r"[\wÀ-ÖØ-öø-ÿ]+", text, flags=re.UNICODE)


def word_error_rate(reference: str, hypothesis: str) -> float | None:
    ref, hyp = normalise(reference), normalise(hypothesis)
    if not ref:
        return None
    row = list(range(len(hyp) + 1))
    for i, ref_word in enumerate(ref, start=1):
        next_row = [i]
        for j, hyp_word in enumerate(hyp, start=1):
            next_row.append(min(
                next_row[-1] + 1,
                row[j] + 1,
                row[j - 1] + (ref_word != hyp_word),
            ))
        row = next_row
    return row[-1] / len(ref)


def wav_metadata(path: Path) -> dict[str, float | int]:
    with wave.open(str(path), "rb") as source:
        channels = source.getnchannels()
        width = source.getsampwidth()
        rate = source.getframerate()
        frames = source.getnframes()
        comptype = source.getcomptype()
    if channels != 1 or width != 2 or comptype != "NONE":
        raise ValueError(
            f"expected mono 16-bit PCM WAV; got channels={channels}, "
            f"sample_width={width}, compression={comptype}"
        )
    return {"sample_rate_hz": rate, "duration_seconds": frames / rate}


def rss_kib(pid: int) -> int | None:
    try:
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1])
    except (FileNotFoundError, PermissionError, ValueError):
        return None
    return None


def run_candidate(candidate: dict, audio: Path) -> dict:
    command = [os.path.expandvars(part).replace("{audio}", str(audio)) for part in candidate["command"]]
    if not any(str(audio) in part for part in command):
        raise ValueError("candidate command has no {audio} placeholder")
    environment = os.environ.copy()
    environment.update(candidate.get("environment", {}))
    started = time.perf_counter()
    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=environment
    )
    peak_rss = 0
    while process.poll() is None:
        current_rss = rss_kib(process.pid)
        if current_rss is not None:
            peak_rss = max(peak_rss, current_rss)
        time.sleep(POLL_SECONDS)
    stdout, stderr = process.communicate()
    elapsed = time.perf_counter() - started
    current_rss = rss_kib(process.pid)
    if current_rss is not None:
        peak_rss = max(peak_rss, current_rss)
    transcript_source = stderr if candidate.get("transcript_stream", "stdout") == "stderr" else stdout
    match = re.search(candidate["transcript_regex"], transcript_source, flags=re.MULTILINE)
    transcript = match.group("text").strip() if match else None
    return {
        "command": command,
        "exit_code": process.returncode,
        "elapsed_seconds": round(elapsed, 6),
        "peak_rss_kib": peak_rss or None,
        "stdout": stdout,
        "stderr": stderr,
        "transcript": transcript,
        "parser_matched": bool(match),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--results", type=Path, required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    candidate = json.loads(args.candidate.read_text())
    for required in ("id", "version", "command", "transcript_regex"):
        if required not in candidate:
            raise ValueError(f"candidate is missing {required!r}")
    args.results.parent.mkdir(parents=True, exist_ok=True)

    with args.results.open("w", encoding="utf-8") as output:
        for fixture in manifest["fixtures"]:
            audio = Path(os.path.expandvars(fixture["audio"]))
            record = {
                "schema": "mycroft-asr-benchmark/v1",
                "candidate_id": candidate["id"],
                "candidate_version": candidate["version"],
                "host": {"machine": platform.machine(), "system": platform.system()},
                "fixture_id": fixture["id"],
                "audio": str(audio),
            }
            try:
                record["audio_metadata"] = wav_metadata(audio)
                record.update(run_candidate(candidate, audio))
                reference = fixture.get("reference")
                record["reference"] = reference
                record["wer"] = (
                    round(word_error_rate(reference, record["transcript"] or ""), 6)
                    if reference and record["transcript"] is not None
                    else None
                )
                duration = record["audio_metadata"]["duration_seconds"]
                record["real_time_factor"] = round(record["elapsed_seconds"] / duration, 6)
            except Exception as error:  # A result record is more useful than a harness crash.
                record["harness_error"] = f"{type(error).__name__}: {error}"
            output.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
