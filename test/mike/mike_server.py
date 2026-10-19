"""Mike Step 3b.1: the same evaluation through llama.cpp's C++ `llama-server` (no Python in the model process).

The server runs as a separate process; this harness only renders the prompt
(the model's own chat template, prompt v4, as in `mike_eval_model`), sends
token ids and the contract grammar to `/completion`, and reads the server's
memory from `/proc/<pid>/status`. Prompt caching is the server's own
(`cache_prompt`); nothing is saved or restored by the client.

The executable boundary is what is under test, so the server is a
subprocess and its complete log is kept.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Any

import mike_bench as bench
import mike_eval as ev
import mike_eval_model as em
from mike_eval import contract

TOOLS_ROOT = Path(os.environ.get("MIKE_TOOLS_ROOT", "/data/michael/tanstaafllm/mike-tools"))
SERVER = TOOLS_ROOT / "llama/llama-b11429/llama-server"

# Every configuration: one slot, context 2,048, 4 threads, no web UI, no host-RAM prompt cache.
COMMON = ["-c", "2048", "-np", "1", "-t", "4", "--no-webui", "--cache-ram", "0"]
CONFIGS = {
    # llama.cpp's defaults (repacked weights, batch 2048 / ubatch 512)
    "default": [],
    # as Python's lean setting (`docs/0302_05`): no repacked copy, batch 16
    "lean": ["--no-repack", "-b", "16", "-ub", "16"],
    # lean, and a context checkpoint at any distance, so the hybrid model's prefix can be reused
    "lean-ckpt": ["--no-repack", "-b", "16", "-ub", "16", "--checkpoint-min-step", "0"],
    # lean, and the shared prefix saved once in a slot file and restored before each request,
    # as Python's save_state/load_state (`docs/0302_02`)
    "lean-slot": ["--no-repack", "-b", "16", "-ub", "16"],
}
SLOT_STATE = {"lean-slot"}


def proc_status(pid: int) -> dict[str, int]:
    out = {}
    for line in Path(f"/proc/{pid}/status").read_text().splitlines():
        key, _, value = line.partition(":")
        if key in ("VmHWM", "VmRSS", "RssAnon", "RssFile"):
            out[key] = int(value.split()[0])
    return out


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class Server:
    """A `llama-server` subprocess on a free local port, with its log kept."""

    def __init__(self, model_path: str, extra: list[str], log_path: Path, binary: Path = SERVER):
        self.port = _free_port()
        self.argv = [str(binary), "-m", model_path, "--host", "127.0.0.1", "--port", str(self.port),
                     *COMMON, *extra]
        self.log_path = log_path
        self.url = f"http://127.0.0.1:{self.port}"

    def __enter__(self) -> "Server":
        self.log = self.log_path.open("w")
        self.log.write(" ".join(self.argv) + "\n")
        self.log.flush()
        started = time.perf_counter()
        self.process = subprocess.Popen(self.argv, stdout=self.log, stderr=subprocess.STDOUT,
                                        cwd=self.argv[0].rsplit("/", 1)[0])
        while True:
            if self.process.poll() is not None:
                raise RuntimeError(f"llama-server exited with {self.process.returncode}; see {self.log_path}")
            try:
                with urllib.request.urlopen(self.url + "/health", timeout=1) as response:
                    if response.status == 200:
                        break
            except OSError:
                pass
            if time.perf_counter() - started > 120:
                raise TimeoutError("llama-server did not become healthy in 120 s")
            time.sleep(0.1)
        self.ready_s = time.perf_counter() - started
        return self

    def __exit__(self, *exc) -> None:
        self.process.terminate()
        try:
            self.process.wait(10)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait()
        self.log.close()

    def status(self) -> dict[str, int]:
        return proc_status(self.process.pid)

    def get(self, path: str) -> Any:
        with urllib.request.urlopen(self.url + path, timeout=30) as response:
            return json.load(response)

    def post(self, path: str, body: dict[str, Any], timeout: float = 120) -> Any:
        request = urllib.request.Request(self.url + path, data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.load(response)


def run_server_eval(model_path: str, config: str, sets: dict[str, Path], run_dir: Path,
                    max_tokens: int = 64) -> dict[str, Any]:
    """Prompt v4, constrained, every set, one server process; memory read from the server."""
    name = Path(model_path).name
    run_dir.mkdir(parents=True, exist_ok=True)
    fmt = bench.format_for(name)
    grammar = bench.grammar_for(fmt, contract.APP_IDS, contract.PLACES)
    extra = list(CONFIGS[config])
    if config in SLOT_STATE:
        slots = run_dir / "slots"
        slots.mkdir(exist_ok=True)
        extra += ["--slot-save-path", str(slots)]
    with Server(model_path, extra, run_dir / f"{name}.{config}.server.log") as server:
        props = server.get("/props")
        template = props["chat_template"]
        bos, eos = props.get("bos_token", ""), props.get("eos_token", "")
        loaded = server.status()

        def tokens_for(case: ev.EvalCase) -> list[int]:
            bench.PROMPTS["v4"] = (em.system_v4(case.desktop), contract.TOOLS)
            text = bench.render_prompt(template, bos, eos, em.user_turn(case, "v4"), "v4") + fmt.opener
            return server.post("/tokenize", {"content": text, "add_special": False, "parse_special": True})["tokens"]

        prefix_report = None
        if config in SLOT_STATE:
            # The prefix shared by every case, evaluated once and saved to a slot file.
            everything = [c for path in sets.values() for c in ev.load_cases(path)]
            first = tokens_for(everything[0])
            prefix = first[:min(bench.common_prefix(first, tokens_for(c)) for c in everything[1:])]
            t0 = time.perf_counter()
            server.post("/completion", {"prompt": prefix, "n_predict": 0, "cache_prompt": True})
            server.post("/slots/0?action=save", {"filename": "prefix.bin"})
            prefix_report = {"tokens": len(prefix), "eval_and_save_s": round(time.perf_counter() - t0, 3),
                             "file_bytes": (run_dir / "slots/prefix.bin").stat().st_size}
        report: dict[str, Any] = {"model": name, "config": config, "argv": server.argv, "prompt": "v4",
                                  "mode": "constrained", "ready_s": round(server.ready_s, 3),
                                  "status_loaded_kib": loaded, "prefix": prefix_report, "sets": {}}
        for set_name, path in sets.items():
            group = ev.load_cases(path)
            timings: list[float] = []
            extra: dict[str, dict[str, Any]] = {}

            def predict(case: ev.EvalCase) -> contract.Call | None:
                tokens = tokens_for(case)
                t = time.perf_counter()
                if config in SLOT_STATE:
                    server.post("/slots/0?action=restore", {"filename": "prefix.bin"})
                answer = server.post("/completion", {
                    "prompt": tokens, "grammar": grammar, "n_predict": max_tokens, "temperature": 0.0,
                    "top_k": 1, "repeat_penalty": 1.0, "cache_prompt": True,
                    "stop": list(bench.STOP_PIECES)})
                timings.append(time.perf_counter() - t)
                raw = answer["content"]
                timing = answer.get("timings", {})
                extra[case.request] = {"raw": raw, "prompt_tokens": len(tokens),
                                       "prompt_n": timing.get("prompt_n"), "prompt_ms": timing.get("prompt_ms"),
                                       "predicted_n": timing.get("predicted_n"),
                                       "predicted_ms": timing.get("predicted_ms")}
                parsed = bench.parse_call(fmt, fmt.opener + raw + fmt.closer[1:])
                return contract.Call(parsed.tool, parsed.args) if parsed else None

            result = ev.evaluate(predict, group)
            for row in result["rows"]:
                row.update(extra[row["request"]])
            ordered = sorted(timings)
            evaluated = sorted(r["prompt_n"] or 0 for r in result["rows"])
            result["summary"].update({
                "median_s": round(ordered[len(ordered) // 2], 3), "max_s": round(ordered[-1], 3),
                "median_prompt_tokens_evaluated": evaluated[len(evaluated) // 2]})
            report["sets"][set_name] = result
        report["status_end_kib"] = server.status()
    return report


def summarise(report: dict[str, Any]) -> dict[str, Any]:
    mib = lambda kib: round(kib / 1024, 1)  # noqa: E731
    end = report["status_end_kib"]
    out = {"model": report["model"], "config": report["config"], "ready_s": report["ready_s"],
           "peak_rss_mib": mib(end["VmHWM"]), "rss_anon_mib": mib(end["RssAnon"]),
           "rss_file_mib": mib(end["RssFile"]), "loaded_rss_mib": mib(report["status_loaded_kib"]["VmRSS"])}
    for name, result in report["sets"].items():
        s = result["summary"]
        out[name] = {k: s[k] for k in ("n", "model", "adapter", "median_s", "max_s",
                                       "median_prompt_tokens_evaluated")}
    return out
