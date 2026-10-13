#!/usr/bin/env python3
"""Footprint probe for mycroft_dictate.py, run on the measured machine itself.

Copied to Luna by test_luna_footprint.py, and also exercised locally in fake
mode. Standard library only (Luna has no extra Python packages).

For each run it starts the provider, keeps its stdin open until "final"
(a replayed file ends on its own), and times the protocol lines. The exact
peak RSS and CPU time come from the kernel at exit (``os.wait4``), so nothing
is sampled except system memory (``MemAvailable``, every 50 ms).

Usage: luna_footprint_probe.py [--runs N] [--audio-seconds S] [--stop-after S] -- <provider command…>
Prints one JSON report on stdout.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import select
import subprocess
import sys
import time


def mem_available_kib() -> int:
    with open("/proc/meminfo") as meminfo:
        for line in meminfo:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1])
    raise RuntimeError("no MemAvailable in /proc/meminfo")


def one_run(command: list[str], timeout: float, stop_after: float | None) -> dict:
    started = time.monotonic()
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert process.stdout is not None and process.stdin is not None
    run: dict = {"messages": 0, "partials": 0}
    lowest_available = mem_available_kib()
    buffer = b""
    final_seen = False
    while not final_seen:
        if stop_after is not None and "ready_s" in run and not process.stdin.closed:
            if time.monotonic() - started - run["ready_s"] >= stop_after:
                process.stdin.close()  # the host's stop, as for a live microphone
                run["stopped_at_s"] = round(time.monotonic() - started, 3)
        if time.monotonic() - started > timeout:
            process.kill()
            run["error"] = f"timeout after {timeout} s"
            break
        ready, _, _ = select.select([process.stdout], [], [], 0.05)
        lowest_available = min(lowest_available, mem_available_kib())
        if not ready:
            continue
        chunk = os.read(process.stdout.fileno(), 65536)
        if not chunk:
            run.setdefault("error", "stdout closed before final")
            break
        buffer += chunk
        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            message = json.loads(line)
            now = round(time.monotonic() - started, 3)
            run["messages"] += 1
            op = message.get("op")
            if op == "ready":
                run["ready_s"] = now
            elif op == "partial":
                run["partials"] += 1
                run.setdefault("first_partial_s", now)
            elif op == "final":
                run["final_s"] = now
                run["final_text"] = message.get("text", "")
                final_seen = True
            elif op == "error":
                run["error"] = message.get("message")
                final_seen = True
    if not process.stdin.closed:
        process.stdin.close()
    _, status, usage = os.wait4(process.pid, 0)
    process.returncode = os.waitstatus_to_exitcode(status)
    wall = time.monotonic() - started
    run.update(
        exit_status=process.returncode,
        wall_s=round(wall, 3),
        peak_rss_mib=round(usage.ru_maxrss / 1024, 1),  # Linux reports KiB
        user_cpu_s=round(usage.ru_utime, 3),
        system_cpu_s=round(usage.ru_stime, 3),
        cpu_share_of_one_core=round((usage.ru_utime + usage.ru_stime) / wall, 3) if wall else None,
        lowest_mem_available_mib=round(lowest_available / 1024, 1),
        stderr=process.stderr.read().decode("utf-8", "replace")[-2000:] if process.stderr else "",
    )
    return run


def raw_run(command: list[str], timeout: float) -> dict:
    """Any program run to completion (for example Sherpa's own C++ binary)."""
    started = time.monotonic()
    process = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lowest_available = mem_available_kib()
    output = b""
    assert process.stdout is not None
    while True:
        ready, _, _ = select.select([process.stdout], [], [], 0.05)
        lowest_available = min(lowest_available, mem_available_kib())
        if ready:
            chunk = os.read(process.stdout.fileno(), 65536)
            if not chunk:
                break
            output += chunk
        if time.monotonic() - started > timeout:
            process.kill()
            break
    _, status, usage = os.wait4(process.pid, 0)
    wall = time.monotonic() - started
    return {
        "exit_status": os.waitstatus_to_exitcode(status),
        "wall_s": round(wall, 3),
        "peak_rss_mib": round(usage.ru_maxrss / 1024, 1),
        "user_cpu_s": round(usage.ru_utime, 3),
        "system_cpu_s": round(usage.ru_stime, 3),
        "cpu_share_of_one_core": round((usage.ru_utime + usage.ru_stime) / wall, 3) if wall else None,
        "lowest_mem_available_mib": round(lowest_available / 1024, 1),
        "output": output.decode("utf-8", "replace")[-4000:],
    }


def vm_rss_mib(pid: int) -> float | None:
    try:
        with open(f"/proc/{pid}/status") as status:
            for line in status:
                if line.startswith("VmRSS:"):
                    return round(int(line.split()[1]) / 1024, 1)
    except FileNotFoundError:
        return None
    return None


def resident_run(command: list[str], utterances: int, audio_seconds: float | None, timeout: float,
                 stop_after: float | None = None) -> dict:
    """One resident provider, several start/final cycles, one load (plan step 9.8)."""
    started = time.monotonic()
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    assert process.stdout is not None and process.stdin is not None
    buffer = b""

    def next_message() -> tuple[float, dict]:
        nonlocal buffer
        while b"\n" not in buffer:
            if time.monotonic() - started > timeout:
                raise TimeoutError("no message")
            ready, _, _ = select.select([process.stdout], [], [], 0.05)
            if ready:
                chunk = os.read(process.stdout.fileno(), 65536)
                if not chunk:
                    raise EOFError("stdout closed")
                buffer += chunk
        line, buffer = buffer.split(b"\n", 1)
        return time.monotonic(), json.loads(line)

    report: dict = {"utterances": []}
    try:
        at, message = next_message()
        if message.get("op") != "ready":
            report["error"] = message
            raise RuntimeError("no ready")
        report["ready_s"] = round(at - started, 3)
        time.sleep(2)
        report["idle_rss_mib"] = vm_rss_mib(process.pid)
        for _ in range(utterances):
            sent = time.monotonic()
            process.stdin.write(b'{"op": "start"}\n')
            process.stdin.flush()
            utterance: dict = {"partials": 0}
            while True:
                at, message = next_message()
                op = message.get("op")
                if op == "listening":
                    utterance["start_to_listening_s"] = round(at - sent, 3)
                    listening_at = at
                    if stop_after is not None:  # live or fake input: the host's stop
                        time.sleep(stop_after)
                        process.stdin.write(b'{"op": "stop"}\n')
                        process.stdin.flush()
                elif op == "partial":
                    utterance["partials"] += 1
                    utterance.setdefault("first_partial_s", round(at - sent, 3))
                    utterance["rss_while_listening_mib"] = vm_rss_mib(process.pid)
                elif op == "final":
                    utterance["final_text"] = message.get("text", "")
                    if audio_seconds:
                        utterance["lag_after_audio_s"] = round(at - listening_at - audio_seconds, 3)
                    break
                elif op == "error":
                    utterance["error"] = message.get("message")
                    break
            report["utterances"].append(utterance)
            time.sleep(1)
            report["idle_rss_after_mib"] = vm_rss_mib(process.pid)
    except (TimeoutError, EOFError, RuntimeError) as exc:
        report.setdefault("error", str(exc))
        process.kill()
    if not process.stdin.closed:
        process.stdin.close()
    _, status, usage = os.wait4(process.pid, 0)
    report.update(
        exit_status=os.waitstatus_to_exitcode(status),
        wall_s=round(time.monotonic() - started, 3),
        peak_rss_mib=round(usage.ru_maxrss / 1024, 1),
        cpu_s=round(usage.ru_utime + usage.ru_stime, 3),
        stderr=process.stderr.read().decode("utf-8", "replace")[-2000:] if process.stderr else "",
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--audio-seconds", type=float, help="replayed audio length, to compute the real-time lag")
    parser.add_argument("--timeout", type=float, default=300)
    parser.add_argument("--resident", type=int, metavar="N", help="drive a --resident provider through N start/final cycles")
    parser.add_argument("--raw", action="store_true", help="run any program to completion instead of the dictation protocol")
    parser.add_argument("--stop-after", type=float, metavar="S", help="close stdin S seconds after ready (live or fake input)")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    if not command:
        parser.error("give the provider command after --")

    report = {
        "machine": platform.machine(),
        "node": platform.node(),
        "python": platform.python_version(),
        "cpus": os.cpu_count(),
        "mem_available_before_mib": round(mem_available_kib() / 1024, 1),
        "command": command,
        "runs": [],
    }
    for _ in range(args.runs):
        if args.resident:
            report["runs"].append(resident_run(command, args.resident, args.audio_seconds, args.timeout, args.stop_after))
            continue
        if args.raw:
            report["runs"].append(raw_run(command, args.timeout))
            continue
        run = one_run(command, args.timeout, args.stop_after)
        if args.audio_seconds and "final_s" in run and "ready_s" in run:
            # Replay is paced in real time; time beyond the audio length is backlog.
            run["lag_after_audio_s"] = round(run["final_s"] - run["ready_s"] - args.audio_seconds, 3)
        report["runs"].append(run)
    json.dump(report, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0 if all(run.get("exit_status") == 0 and "error" not in run for run in report["runs"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
