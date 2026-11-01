"""Mike Step 4.5: run `llama-server` on Luna as `michael`, drive it from the desk through an SSH tunnel.

Nothing is installed in the system: the release and the model go under
`~/.local/opt/mike/` on Luna. The server starts only if the shared brain lock
`/tmp/luna-brain.lock` can be created (noclobber), and its pid is written in it
(`mike <pid>`). A sampler reads the server's `/proc/<pid>/status` and Luna's
`MemAvailable` over the same multiplexed SSH connection, and stops the server if
`MemAvailable` falls below the floor. The client (prompt rendering, grammar,
scoring) runs on the desk, as in `mike_server`; Luna only runs the model.
"""

from __future__ import annotations

import json
import subprocess
import threading
import time
import urllib.request
from pathlib import Path
from typing import Any

import mike_server as ms

HOST = "luna"
USER = "michael"
SSH_MUX = ["-o", "ControlMaster=auto", "-o", f"ControlPath={Path.home()}/.ssh/cm/%r@%h:%p",
           "-o", "ControlPersist=15m", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10"]
(Path.home() / ".ssh/cm").mkdir(mode=0o700, exist_ok=True)
REMOTE_DIR = "/home/michael/.local/opt/mike"
RELEASE = "llama-b11429-bin-ubuntu-arm64.tar.gz"
RELEASE_SHA256 = "ed44c0f79c3d02424f62bdc87e106318b0b89f49050e2e80c5f352723d14e00b"
MODEL = "LFM2.5-350M-Q4_0.gguf"
MODEL_SHA256 = "85e32858daafad55b7bcd6b97a1343ee0661188e8036f9862d14d6b563142f50"
LOCK = "/tmp/luna-brain.lock"
FLOOR_MIB = 150


def ssh(command: str, timeout: float = 60, check: bool = True) -> str:
    done = subprocess.run(["ssh", *SSH_MUX, "-l", USER, HOST, command], capture_output=True, text=True,
                          timeout=timeout)
    if check and done.returncode != 0:
        raise RuntimeError(f"ssh {command!r}: {done.returncode} {done.stderr.strip()}")
    return done.stdout


def mem_available_kib() -> int:
    for line in ssh("cat /proc/meminfo").splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1])
    raise RuntimeError("no MemAvailable")


def install(local_release: Path, local_model: Path, log) -> dict[str, Any]:
    """Copy the release and the model if their checksums differ; unpack the release."""
    ssh(f"mkdir -p {REMOTE_DIR}/slots")
    sums = ssh(f"cd {REMOTE_DIR} && sha256sum {RELEASE} {MODEL} 2>/dev/null", check=False)
    copied = []
    for path, digest in ((local_release, RELEASE_SHA256), (local_model, MODEL_SHA256)):
        if f"{digest}  {path.name}" not in sums:
            t0 = time.perf_counter()
            subprocess.run(["scp", *SSH_MUX, "-q", str(path), f"{USER}@{HOST}:{REMOTE_DIR}/"], check=True,
                           timeout=1800)
            copied.append({"file": path.name, "s": round(time.perf_counter() - t0, 1)})
    check = ssh(f"cd {REMOTE_DIR} && sha256sum {RELEASE} {MODEL}")
    assert f"{RELEASE_SHA256}  {RELEASE}" in check and f"{MODEL_SHA256}  {MODEL}" in check, check
    ssh(f"cd {REMOTE_DIR} && [ -x llama-b11429/llama-server ] || tar -xzf {RELEASE}")
    log.write(f"install: copied={copied}\n{check}\n")
    return {"copied": copied, "sha256": check.strip().splitlines()}


class LunaServer:
    """`llama-server` on Luna under the brain lock, reached through a local SSH tunnel."""

    def __init__(self, extra: list[str], log_path: Path, threads: int = 4):
        self.port = ms._free_port()
        self.remote_port = 18090
        self.argv = [f"{REMOTE_DIR}/llama-b11429/llama-server", "-m", f"{REMOTE_DIR}/{MODEL}",
                     "--host", "127.0.0.1", "--port", str(self.remote_port),
                     *[a for a in ms.COMMON if a not in ("-t", "4")], *extra, "-t", str(threads)]
        self.log_path = log_path
        self.url = f"http://127.0.0.1:{self.port}"
        self.samples: list[dict[str, Any]] = []
        self.stopped_for_memory = False
        self.pid: int | None = None

    def __enter__(self) -> "LunaServer":
        try:
            return self._enter()
        except BaseException:
            self.__exit__()  # a failed start still stops the server and frees the lock
            raise

    def _enter(self) -> "LunaServer":
        self.samples.append({"t": time.time(), "event": "before-start", "mem_available_kib": mem_available_kib()})
        held = ssh(f"cat {LOCK} 2>/dev/null", check=False).strip()
        if held:
            raise RuntimeError(f"brain lock held: {held!r}")
        remote_log = f"{REMOTE_DIR}/server.log"
        # `exec` keeps the shell's pid, so the lock names the server itself.
        start = (f"cd {REMOTE_DIR}/llama-b11429 && "
                 f"setsid -f sh -c 'set -C; echo \"mike $$\" > {LOCK} || exit 3; exec {' '.join(self.argv)}' "
                 f"> {remote_log} 2>&1 < /dev/null; sleep 1; cat {LOCK}")
        self.started = time.perf_counter()
        lock = ssh(start, timeout=30).strip()
        assert lock.startswith("mike "), lock
        self.pid = int(lock.split()[1])
        self.tunnel = subprocess.Popen(["ssh", *SSH_MUX, "-l", USER, "-N", "-L",
                                        f"{self.port}:127.0.0.1:{self.remote_port}", HOST])
        while True:
            try:
                with urllib.request.urlopen(self.url + "/health", timeout=2) as response:
                    if response.status == 200:
                        break
            except OSError:
                pass
            if not ssh(f"kill -0 {self.pid} 2>/dev/null && echo up", check=False).strip():
                raise RuntimeError("llama-server exited on Luna: " + ssh(f"tail -20 {remote_log}", check=False))
            if time.perf_counter() - self.started > 600:
                raise TimeoutError("llama-server on Luna not healthy in 600 s")
            time.sleep(1)
        self.ready_s = time.perf_counter() - self.started
        self.sample("after-load")
        self._stop = threading.Event()
        self._sampler = threading.Thread(target=self._watch, daemon=True)
        self._sampler.start()
        return self

    def sample(self, event: str) -> dict[str, Any]:
        row = {"t": time.time(), "event": event, "mem_available_kib": mem_available_kib(),
               "server": self.status() if self.pid else {}}
        self.samples.append(row)
        return row

    def _watch(self) -> None:
        while not self._stop.wait(1.0):
            try:
                row = self.sample("tick")
            except Exception as error:  # keep watching; record the miss
                self.samples.append({"t": time.time(), "event": "sample-error", "error": repr(error)})
                continue
            if row["mem_available_kib"] < FLOOR_MIB * 1024:
                self.stopped_for_memory = True
                ssh(f"kill {self.pid}", check=False)
                return

    def status(self) -> dict[str, int]:
        out = {}
        for line in ssh(f"cat /proc/{self.pid}/status", check=False).splitlines():
            key, _, value = line.partition(":")
            if key in ("VmHWM", "VmRSS", "RssAnon", "RssFile"):
                out[key] = int(value.split()[0])
        return out

    get = ms.Server.get
    post = ms.Server.post

    def __exit__(self, *exc) -> None:
        if hasattr(self, "_stop"):
            self._stop.set()
            self._sampler.join(5)
        if self.pid is None:
            # A start that failed half-way may still have taken the lock and started the server.
            held = ssh(f"cat {LOCK} 2>/dev/null", check=False).strip()
            if held.startswith("mike ") and held.split()[1].isdigit():
                self.pid = int(held.split()[1])
        if self.pid:
            self.samples.append({"t": time.time(), "event": "before-stop", "server": self.status()})
            ssh(f"kill {self.pid}; for i in 1 2 3 4 5 6 7 8 9 10; do kill -0 {self.pid} 2>/dev/null || break; sleep 1; done; "
                f"kill -9 {self.pid} 2>/dev/null; true", check=False)
            # Remove the lock only if it is still ours.
            ssh(f"[ \"$(cat {LOCK} 2>/dev/null)\" = \"mike {self.pid}\" ] && rm -f {LOCK}; true", check=False)
        if hasattr(self, "tunnel"):
            self.tunnel.terminate()
            self.tunnel.wait(10)
        self.log_path.write_text(ssh(f"cat {REMOTE_DIR}/server.log", check=False))
        time.sleep(2)
        self.samples.append({"t": time.time(), "event": "after-stop", "mem_available_kib": mem_available_kib(),
                             "lock": ssh(f"cat {LOCK} 2>/dev/null", check=False).strip()})


def peak_between(samples: list[dict[str, Any]], start: float, end: float) -> dict[str, Any]:
    window = [s for s in samples if start <= s["t"] <= end + 1.5 and "mem_available_kib" in s]
    if not window:
        return {}
    low = min(window, key=lambda s: s["mem_available_kib"])
    return {"min_mem_available_kib": low["mem_available_kib"], "vm_rss_kib": low.get("server", {}).get("VmRSS")}


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=1, ensure_ascii=False))
