#!/usr/bin/env python3
"""Step 8.8 probe, run on Luna: memory of the real Slate session with the
resident Kroko provider that Wyoh's daemon started (no second model load).

Waits until the daemon reports the provider idle, then samples MemAvailable,
the provider's RSS and the daemon's dictation state for --window seconds while
the user dictates in the Slate (L2). Prints one JSON object. Standard library
only; reads /proc and /run/wyoh/gamepad.json, changes nothing."""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

STATUS = Path("/run/wyoh/gamepad.json")
TICKS = os.sysconf("SC_CLK_TCK")


def meminfo() -> dict[str, int]:
    values = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key, rest = line.split(":", 1)
        values[key] = int(rest.split()[0])
    return values


def provider_pid() -> int | None:
    for entry in Path("/proc").iterdir():
        if entry.name.isdigit():
            try:
                argv = (entry / "cmdline").read_bytes().split(b"\0")
            except OSError:
                continue
            if any(arg.endswith(b"mycroft_dictate.py") for arg in argv) and b"--resident" in argv:
                return int(entry.name)
    return None


def status_field(pid: int, field: str) -> int | None:
    try:
        for line in Path(f"/proc/{pid}/status").read_text().splitlines():
            if line.startswith(field + ":"):
                return int(line.split()[1])
    except OSError:
        pass
    return None


def dictation_state() -> str | None:
    try:
        return json.loads(STATUS.read_text()).get("dictation")
    except (OSError, ValueError):
        return None


def uptime() -> float:
    return float(Path("/proc/uptime").read_text().split()[0])


def top_rss(count: int = 10) -> list[dict]:
    rows = []
    for entry in Path("/proc").iterdir():
        if entry.name.isdigit():
            rss = status_field(int(entry.name), "VmRSS")
            if rss:
                try:
                    name = (entry / "cmdline").read_bytes().replace(b"\0", b" ").decode("utf-8", "replace").strip()[:120]
                except OSError:
                    continue
                rows.append({"pid": int(entry.name), "rss_mib": round(rss / 1024, 1), "cmd": name})
    return sorted(rows, key=lambda row: -row["rss_mib"])[:count]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--window", type=float, default=180)
    parser.add_argument("--wait", type=float, default=300)
    args = parser.parse_args()
    report: dict = {}
    deadline = time.monotonic() + args.wait
    while time.monotonic() < deadline:
        pid = provider_pid()
        if pid and dictation_state() == "idle":
            break
        time.sleep(0.5)
    else:
        report["error"] = f"provider not idle within {args.wait} s (state {dictation_state()!r}, pid {provider_pid()})"
        print(json.dumps(report))
        return 1
    start_ticks = int(Path(f"/proc/{pid}/stat").read_text().rsplit(")", 1)[1].split()[19])
    report["provider_pid"] = pid
    report["provider_started_s_after_boot"] = round(start_ticks / TICKS, 1)
    report["provider_idle_seen_s_after_boot"] = round(uptime(), 1)
    info = meminfo()
    report["mem_total_mib"] = round(info["MemTotal"] / 1024, 1)
    report["swap_total_mib"] = round(info.get("SwapTotal", 0) / 1024, 1)
    report["top_rss_idle"] = top_rss()
    samples = []
    end = time.monotonic() + args.window
    while time.monotonic() < end:
        samples.append({
            "t": round(uptime(), 1),
            "mem_available_mib": round(meminfo()["MemAvailable"] / 1024, 1),
            "provider_rss_mib": round((status_field(pid, "VmRSS") or 0) / 1024, 1),
            "state": dictation_state(),
        })
        time.sleep(0.5)
    listening = [s for s in samples if s["state"] and s["state"].startswith(("listening", "stopping"))]
    report["idle_mem_available_mib"] = samples[0]["mem_available_mib"]
    report["idle_provider_rss_mib"] = samples[0]["provider_rss_mib"]
    report["min_mem_available_mib"] = min(s["mem_available_mib"] for s in samples)
    report["max_provider_rss_mib"] = max(s["provider_rss_mib"] for s in samples)
    report["provider_hwm_mib"] = round((status_field(pid, "VmHWM") or 0) / 1024, 1)
    report["listening_samples"] = len(listening)
    report["states_seen"] = sorted({s["state"] or "" for s in samples})
    report["provider_alive_at_end"] = provider_pid() == pid
    report["samples"] = samples
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
