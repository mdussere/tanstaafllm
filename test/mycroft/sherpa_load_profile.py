#!/usr/bin/env python3
"""Break down Mycroft's model load and measure unpaced decoding (plan steps 8.2-8.4).

Runs on the measured machine (Luna or the desk host); standard library only.
It imports the provider's own adapter from --scripts, so it measures exactly
the code Mycroft runs. Phases, each timed separately:

  1. read_model_files_s  read the four model files once (cold only if the page
                         cache was dropped beforehand by the caller)
  2. load_libraries_s    ctypes loads the Sherpa C API and ONNX Runtime
  3. create_session_s    SherpaOnnxCreateOnlineRecognizer + first stream
                         (ONNX Runtime graph optimisation and weight prepacking)
  4. decode_s            the WAV fed as fast as possible, then finish()

Prints one JSON object, including real-time factor (decode_s / audio length)
and the kernel's peak RSS and CPU time for this process.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import resource
import sys
import time
import wave
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scripts", required=True, help="directory holding mycroft_console.py")
    parser.add_argument("--assets", required=True)
    parser.add_argument("--wav", required=True)
    parser.add_argument("--threads", type=int, default=1)
    args = parser.parse_args()
    sys.path.insert(0, args.scripts)
    import mycroft_console as console  # noqa: E402  (path set just above)

    assets = Path(args.assets)
    model_dir = assets / console.MODEL_DIRNAME
    report: dict = {"threads": args.threads, "assets": str(assets)}

    started = time.monotonic()
    total = 0
    for path in sorted(model_dir.glob("*.int8.onnx")) + [model_dir / "tokens.txt"]:
        with path.open("rb") as handle:
            while block := handle.read(1 << 20):
                total += len(block)
    report["model_bytes"] = total
    report["read_model_files_s"] = round(time.monotonic() - started, 3)

    started = time.monotonic()
    runtime = assets / console.runtime_dirname() / "lib"
    ctypes.CDLL(str(runtime / "libonnxruntime.so"))
    ctypes.CDLL(str(runtime / "libsherpa-onnx-c-api.so"))
    report["load_libraries_s"] = round(time.monotonic() - started, 3)

    started = time.monotonic()
    recognizer = console.SherpaStreamingRecognizer(assets, num_threads=args.threads)
    report["create_session_s"] = round(time.monotonic() - started, 3)

    with wave.open(args.wav, "rb") as source:
        rate = source.getframerate()
        audio_seconds = source.getnframes() / rate
        started = time.monotonic()
        while pcm := source.readframes(rate // 5):
            recognizer.accept_pcm(pcm, rate)
        text = recognizer.finish()
    report["decode_s"] = round(time.monotonic() - started, 3)
    recognizer.close()

    usage = resource.getrusage(resource.RUSAGE_SELF)
    report.update(
        audio_s=round(audio_seconds, 3),
        rtf=round(report["decode_s"] / audio_seconds, 3),
        text=text,
        peak_rss_mib=round(usage.ru_maxrss / 1024, 1),
        user_cpu_s=round(usage.ru_utime, 3),
        system_cpu_s=round(usage.ru_stime, 3),
    )
    json.dump(report, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
