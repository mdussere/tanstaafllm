"""Resource probe for Claude Code, run on the target with the system python3.

Standard library only. Prints one JSON object on stdout and never echoes what
Claude Code prints (a logged-in screen can show the account), only its size.

  claude_probe.py time <command…>            wall, CPU, peak RSS of one run
  claude_probe.py pty <seconds> <command…>   start in a pseudo-terminal, sample
                                             the process tree for <seconds>
"""

from __future__ import annotations

import fcntl
import json
import os
import pty
import resource
import select
import signal
import struct
import subprocess
import sys
import termios
import time


def _children() -> dict[int, list[int]]:
    tree: dict[int, list[int]] = {}
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        try:
            with open(f"/proc/{name}/stat", encoding="ascii", errors="replace") as handle:
                parent = int(handle.read().rsplit(")", 1)[1].split()[1])
        except (OSError, IndexError, ValueError):
            continue
        tree.setdefault(parent, []).append(int(name))
    return tree


def _tree(root: int) -> list[int]:
    children, found, todo = _children(), [], [root]
    while todo:
        pid = todo.pop()
        found.append(pid)
        todo.extend(children.get(pid, []))
    return found


def _memory_kib(pid: int) -> tuple[int, int]:
    """(Rss, Pss) in KiB, 0 if the process has gone."""
    rss = pss = 0
    try:
        with open(f"/proc/{pid}/smaps_rollup", encoding="ascii") as handle:
            for line in handle:
                if line.startswith("Rss:"):
                    rss = int(line.split()[1])
                elif line.startswith("Pss:"):
                    pss = int(line.split()[1])
    except OSError:
        pass
    return rss, pss


def _available_kib() -> int:
    with open("/proc/meminfo", encoding="ascii") as handle:
        for line in handle:
            if line.startswith("MemAvailable:"):
                return int(line.split()[1])
    return 0


def run_time(command: list[str]) -> dict:
    start = time.monotonic()
    done = subprocess.run(command, stdin=subprocess.DEVNULL, capture_output=True)
    wall = time.monotonic() - start
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {
        "mode": "time",
        "command": command,
        "exit_status": done.returncode,
        "wall_s": round(wall, 3),
        "user_s": round(usage.ru_utime, 3),
        "sys_s": round(usage.ru_stime, 3),
        "max_rss_kib": usage.ru_maxrss,
        "stdout": done.stdout.decode("utf-8", "replace"),
        "stderr": done.stderr.decode("utf-8", "replace"),
    }


def run_pty(seconds: float, command: list[str]) -> dict:
    available_before = _available_kib()
    start = time.monotonic()
    pid, fd = pty.fork()
    if pid == 0:
        os.environ["TERM"] = "xterm-256color"
        os.execvp(command[0], command)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 30, 100, 0, 0))
    first_output = None
    output_bytes = 0
    samples = []
    deadline = start + seconds
    while time.monotonic() < deadline:
        ready, _, _ = select.select([fd], [], [], 0.2)
        if ready:
            try:
                chunk = os.read(fd, 65536)
            except OSError:
                break
            if not chunk:
                break
            output_bytes += len(chunk)
            if first_output is None:
                first_output = time.monotonic() - start
        pids = _tree(pid)
        memory = [_memory_kib(p) for p in pids]
        samples.append((time.monotonic() - start, len(pids), sum(m[0] for m in memory), sum(m[1] for m in memory)))
        exited, _ = os.waitpid(pid, os.WNOHANG)
        if exited:
            break
    still_running = os.waitpid(pid, os.WNOHANG)[0] == 0
    if still_running:
        os.kill(pid, signal.SIGTERM)
        time.sleep(1)
        if os.waitpid(pid, os.WNOHANG)[0] == 0:
            os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)
    usage = resource.getrusage(resource.RUSAGE_CHILDREN)
    settled = [s for s in samples if s[0] >= seconds - 5] or samples[-1:]
    return {
        "mode": "pty",
        "command": command,
        "seconds": seconds,
        "running_at_end": still_running,
        "first_output_s": None if first_output is None else round(first_output, 3),
        "output_bytes": output_bytes,
        "peak_tree_rss_kib": max((s[2] for s in samples), default=0),
        "peak_tree_pss_kib": max((s[3] for s in samples), default=0),
        "settled_tree_rss_kib": int(sum(s[2] for s in settled) / len(settled)) if settled else 0,
        "settled_tree_pss_kib": int(sum(s[3] for s in settled) / len(settled)) if settled else 0,
        "max_processes": max((s[1] for s in samples), default=0),
        "user_s": round(usage.ru_utime, 3),
        "sys_s": round(usage.ru_stime, 3),
        "mem_available_before_kib": available_before,
        "samples": [[round(s[0], 2), s[1], s[2], s[3]] for s in samples[::5]],
    }


def main(argv: list[str]) -> int:
    if len(argv) >= 2 and argv[0] == "time":
        result = run_time(argv[1:])
    elif len(argv) >= 3 and argv[0] == "pty":
        result = run_pty(float(argv[1]), argv[2:])
    else:
        print(__doc__, file=sys.stderr)
        return 2
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
