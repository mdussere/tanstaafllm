#!/usr/bin/env python3
"""Resident Mycroft provider under memory pressure (plan step 8.6).

Runs on the measured machine; standard library only. It loads the model once
and keeps it, as a resident provider would, then:

  1. reports idle memory after load (VmRSS, RssAnon, RssFile) and decodes the
     WAV once (warm latency);
  2. starts a child "hog" that allocates and touches memory in steps until
     the system's MemAvailable reaches --floor-mib (never lower), sampling
     the provider's memory at each step;
  3. decodes the WAV again under that pressure, then frees the hog and
     decodes a third time.

Without swap, anonymous memory (the model weights ONNX Runtime keeps) can't
be reclaimed; only file-backed pages (libraries) can be dropped. The floor
keeps the kernel's OOM killer out of the test.

Prints one JSON report.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import wave
from pathlib import Path


def meminfo(field: str) -> int:
    with open("/proc/meminfo") as handle:
        for line in handle:
            if line.startswith(field + ":"):
                return int(line.split()[1])
    raise KeyError(field)


def own_memory() -> dict:
    values = {}
    with open("/proc/self/status") as handle:
        for line in handle:
            key = line.split(":")[0]
            if key in ("VmRSS", "RssAnon", "RssFile", "VmHWM"):
                values[key + "_mib"] = round(int(line.split()[1]) / 1024, 1)
    values["MemAvailable_mib"] = round(meminfo("MemAvailable") / 1024, 1)
    return values


def decode(recognizer, wav: str) -> dict:
    recognizer.reset()
    with wave.open(wav, "rb") as source:
        rate = source.getframerate()
        started = time.monotonic()
        while pcm := source.readframes(rate // 5):
            recognizer.accept_pcm(pcm, rate)
        text = recognizer.finish()
        seconds = time.monotonic() - started
        return {"decode_s": round(seconds, 3), "rtf": round(seconds * rate / source.getnframes(), 3), "text": text}


def start_hog(floor_kib: int, step_mib: int) -> tuple[int, int]:
    """Fork a child that grows until MemAvailable <= floor; returns (pid, read fd)."""
    read_fd, write_fd = os.pipe()
    pid = os.fork()
    if pid == 0:
        os.close(read_fd)
        blocks = []
        try:
            while meminfo("MemAvailable") - step_mib * 1024 > floor_kib:
                block = bytearray(step_mib << 20)
                for offset in range(0, len(block), 4096):  # touch every page
                    block[offset] = 1
                blocks.append(block)
                os.write(write_fd, f"{len(blocks) * step_mib}\n".encode())
            os.write(write_fd, b"full\n")
            time.sleep(3600)  # hold until killed
        finally:
            os._exit(0)
    os.close(write_fd)
    return pid, read_fd


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scripts", required=True)
    parser.add_argument("--assets", required=True)
    parser.add_argument("--wav", required=True)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--floor-mib", type=int, default=150)
    parser.add_argument("--step-mib", type=int, default=32)
    args = parser.parse_args()
    sys.path.insert(0, args.scripts)
    import mycroft_console as console  # noqa: E402

    report: dict = {"threads": args.threads, "floor_mib": args.floor_mib, "before_load": own_memory()}
    started = time.monotonic()
    recognizer = console.SherpaStreamingRecognizer(Path(args.assets), num_threads=args.threads)
    report["load_s"] = round(time.monotonic() - started, 3)
    report["idle_after_load"] = own_memory()
    report["warm_decode"] = decode(recognizer, args.wav)
    time.sleep(2)
    report["idle_after_first_use"] = own_memory()

    hog, pipe = start_hog(args.floor_mib * 1024, args.step_mib)
    samples = []
    with os.fdopen(pipe) as progress:
        for line in progress:
            sample = own_memory()
            sample["hog_mib"] = line.strip()
            samples.append(sample)
            if line.strip() == "full":
                break
    report["pressure_samples"] = samples
    report["under_pressure"] = own_memory()
    report["decode_under_pressure"] = decode(recognizer, args.wav)
    os.kill(hog, 9)
    os.waitpid(hog, 0)
    time.sleep(2)
    report["after_pressure"] = own_memory()
    report["decode_after_pressure"] = decode(recognizer, args.wav)
    recognizer.close()
    json.dump(report, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
