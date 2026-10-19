"""Mike Step 3b.2: run a ready-made micro-harness (ZeroClaw, PicoClaw) on Mike's local model.

The harness talks to `llama-server` (OpenAI-compatible, `--jinja`) through a
recording proxy, so every request it sends (system prompt, tool list, prompt
tokens, timings) is kept. Its only tools are Mike's six contract tools from
`mike_fake_mcp.py`, which record each call and never touch a desktop.

Each harness gets its own throw-away home and configuration; nothing is
written to the user's home. The harness process's own memory is sampled from
`/proc/<pid>/status`, apart from its children (the fake MCP server).
"""

from __future__ import annotations

import http.server
import json
import os
import shutil
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

import mike_server as ms

REPO = Path(__file__).parents[2]
FAKE_MCP = Path(__file__).with_name("mike_fake_mcp.py")
ZEROCLAW = ms.TOOLS_ROOT / "zeroclaw/zeroclaw"
PICOCLAW = ms.TOOLS_ROOT / "picoclaw/picoclaw"

# Short instructions given to every harness, in the file it reads at start-up.
MIKE_INSTRUCTIONS = """You are Mike, the assistant of a small handheld computer. The user speaks French.
Answer every desktop request with exactly one tool call:
- ouvre, lance, démarre X -> launch_app
- passe sur, va sur X -> focus_window
- ferme, quitte X -> close_window
- mets X à gauche / à droite / en plein écran -> move_window
- écris, tape TEXT -> type_text
- quelles fenêtres -> list_windows
"""

# (request, expected tool, expected arguments); the desktop is the fake server's: terminal open and focused.
SCENARIOS = [
    ("ouvre l'éditeur", "launch_app", {"app": "editor"}),
    ("mets le terminal à gauche", "move_window", {"app": "terminal", "place": "left"}),
    ("écris bonjour", "type_text", {"text": "bonjour"}),
    ("quel temps fera-t-il demain", None, {}),
]
MIKE_TOOLS = ["list_windows", "focus_window", "launch_app", "close_window", "move_window", "type_text"]


class RecordingProxy:
    """Forward HTTP to `upstream` and keep each POST body and reply (one JSON line each)."""

    def __init__(self, upstream: str, out: Path):
        self.upstream, self.out = upstream, out
        proxy = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def _forward(self, body: bytes | None) -> bytes:
                request = urllib.request.Request(proxy.upstream + self.path, data=body, method=self.command,
                                                 headers={"Content-Type": "application/json"})
                try:
                    with urllib.request.urlopen(request, timeout=600) as response:
                        data, code = response.read(), response.status
                        ctype = response.headers.get("Content-Type", "application/json")
                except urllib.error.HTTPError as error:
                    data, code, ctype = error.read(), error.code, "application/json"
                self.send_response(code)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return data

            def do_GET(self):
                self._forward(None)

            def do_POST(self):
                body = self.rfile.read(int(self.headers["Content-Length"]))
                started = time.time()
                reply = self._forward(body)
                with proxy.out.open("a") as log:
                    log.write(json.dumps({"t": started, "s": round(time.time() - started, 3), "path": self.path,
                                          "body": json.loads(body), "reply": reply.decode(errors="replace")},
                                         ensure_ascii=False) + "\n")

            def log_message(self, *args):
                pass

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def __enter__(self) -> "RecordingProxy":
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *exc) -> None:
        self.server.shutdown()

    def take(self) -> list[dict[str, Any]]:
        if not self.out.exists():
            return []
        rows = [json.loads(line) for line in self.out.read_text().splitlines()]
        self.out.unlink()
        return rows


def _vm(pid: int) -> dict[str, int]:
    try:
        return ms.proc_status(pid)
    except (FileNotFoundError, ProcessLookupError):
        return {}


def run_sampled(argv: list[str], env: dict[str, str], cwd: Path, timeout: float, log: Path) -> dict[str, Any]:
    """Run one harness command; sample its own VmHWM (not its children's) until it exits."""
    started = time.perf_counter()
    with log.open("w") as out:
        out.write(" ".join(argv) + "\n")
        out.flush()
        process = subprocess.Popen(argv, env=env, cwd=cwd, stdin=subprocess.DEVNULL, stdout=out,
                                   stderr=subprocess.STDOUT)
        peak: dict[str, int] = {}
        while process.poll() is None:
            status = _vm(process.pid)
            if status.get("VmHWM", 0) >= peak.get("VmHWM", 0):
                peak = status
            if time.perf_counter() - started > timeout:
                process.kill()
                process.wait()
                break
            time.sleep(0.05)
    return {"returncode": process.returncode, "wall_s": round(time.perf_counter() - started, 3),
            "timed_out": time.perf_counter() - started > timeout, "status_peak_kib": peak,
            "output": log.read_text()[-4000:]}


# --- harness set-ups ----------------------------------------------------------

def setup_zeroclaw(home: Path, model_url: str, calls: Path) -> tuple[list[str], dict[str, str], Path]:
    cfg = home / "cfg"
    workspace = cfg / "agents/mike/workspace"
    workspace.mkdir(parents=True)
    (workspace / "AGENTS.md").write_text(MIKE_INSTRUCTIONS)
    tools = ", ".join(f'"mike_wyoh__{name}"' for name in MIKE_TOOLS)
    (cfg / "config.toml").write_text(f"""schema_version = 3

[providers.models.llamacpp.mike]
uri = "{model_url}/v1"
model = "lfm2.5-350m"
temperature = 0.0
timeout_secs = 300
vision = false

[risk_profiles.mike]
level = "supervised"
allowed_commands = ["ls"]
allowed_tools = [{tools}]
auto_approve = []
always_ask = [{tools}]

[runtime_profiles.mike]
agentic = false
compact_context = true

[[mcp.servers]]
name = "mike_wyoh"
command = "{sys.executable}"
args = ["{FAKE_MCP}"]

[mcp_bundles.wyoh]
servers = ["mike_wyoh"]

[agents.mike]
model_provider = "llamacpp.mike"
risk_profile = "mike"
runtime_profile = "mike"
mcp_bundles = ["wyoh"]
""")
    env = {"HOME": str(home), "PATH": os.environ["PATH"], "MIKE_FAKE_MCP_LOG": str(calls)}
    return [str(ZEROCLAW), "--config-dir", str(cfg), "agent", "-a", "mike", "-m"], env, home


def setup_picoclaw(home: Path, model_url: str, calls: Path) -> tuple[list[str], dict[str, str], Path]:
    env = {"HOME": str(home), "PATH": os.environ["PATH"], "MIKE_FAKE_MCP_LOG": str(calls)}
    subprocess.run([str(PICOCLAW), "--no-color", "onboard"], env=env, cwd=home, stdin=subprocess.DEVNULL,
                   capture_output=True, check=True, timeout=60)
    root = home / ".picoclaw"
    workspace = root / "workspace"
    # Leave only Mike's instructions: no sample skills, no persona, empty memory.
    shutil.rmtree(workspace / "skills")
    (workspace / "skills").mkdir()
    (workspace / "AGENT.md").write_text(MIKE_INSTRUCTIONS)
    for name in ("SOUL.md", "USER.md", "memory/MEMORY.md"):
        (workspace / name).write_text("")
    config = json.loads((root / "config.json").read_text())
    for key, value in config["tools"].items():
        if isinstance(value, dict) and "enabled" in value:
            value["enabled"] = key == "mcp"
    config["tools"]["mcp"]["servers"] = {"mike_wyoh": {
        "enabled": True, "deferred": False, "type": "stdio", "command": sys.executable,
        "args": [str(FAKE_MCP)], "env": {"MIKE_FAKE_MCP_LOG": str(calls)}}}
    config["model_list"] = [{"model_name": "mike", "provider": "vllm", "model": "lfm2.5-350m",
                             "api_base": f"{model_url}/v1"}]
    defaults = config["agents"]["defaults"]
    defaults.update({"model_name": "mike", "provider": "vllm", "max_tokens": 256, "max_tool_iterations": 1,
                     "temperature": 0.0})
    (root / "config.json").write_text(json.dumps(config, indent=2))
    return [str(PICOCLAW), "--no-color", "agent", "-m"], env, home


HARNESSES = {"zeroclaw": (ZEROCLAW, setup_zeroclaw), "picoclaw": (PICOCLAW, setup_picoclaw)}


def _tool_calls(rows: list[dict[str, Any]]) -> list[tuple[str, dict[str, Any]]]:
    out = []
    for row in rows:
        try:
            message = json.loads(row["reply"])["choices"][0]["message"]
        except (ValueError, KeyError, IndexError):
            continue
        for call in message.get("tool_calls") or []:
            name = call["function"]["name"].split("__")[-1].removeprefix("mcp_mike_wyoh_")
            try:
                args = json.loads(call["function"]["arguments"] or "{}")
            except ValueError:
                args = {"_raw": call["function"]["arguments"]}
            out.append((name, args))
    return out


def run_harness(name: str, model_url: str, work: Path, timeout: float = 300) -> dict[str, Any]:
    """Every scenario through one harness; requests, calls and memory kept per scenario."""
    _, setup = HARNESSES[name]
    home = work / f"{name}-home"
    home.mkdir(parents=True)
    calls = work / f"{name}-calls.jsonl"
    with RecordingProxy(model_url, work / f"{name}-requests.tmp.jsonl") as proxy:
        argv, env, cwd = setup(home, proxy.url, calls)
        report: dict[str, Any] = {"harness": name, "argv": argv, "scenarios": []}
        for request, tool, args in SCENARIOS:
            before = len(calls.read_text().splitlines()) if calls.exists() else 0
            run = run_sampled([*argv, request], env, cwd, timeout, work / f"{name}-{len(report['scenarios'])}.log")
            rows = proxy.take()
            recorded = [json.loads(line) for line in calls.read_text().splitlines()[before:]] if calls.exists() else []
            model_calls = _tool_calls(rows)
            first = model_calls[0] if model_calls else None
            replies = []
            for row in rows:
                try:
                    replies.append(json.loads(row["reply"]))
                except ValueError:
                    replies.append({"error": row["reply"][:500]})
            report["scenarios"].append({
                "request": request, "expected": [tool, args],
                "model_calls": model_calls, "mcp_calls": recorded,
                "right": (first == (tool, args)) if tool else not model_calls,
                "llm_requests": len(rows),
                "system_chars": [len(r["body"]["messages"][0]["content"]) for r in rows if r["body"].get("messages")],
                "tools_sent": [len(r["body"].get("tools") or []) for r in rows],
                "prompt_tokens": [x.get("usage", {}).get("prompt_tokens") for x in replies],
                "cached_tokens": [x.get("timings", {}).get("cache_n") for x in replies],
                "llm_s": [r["s"] for r in rows],
                **run, "requests": rows,
            })
    return report


def summarise(report: dict[str, Any]) -> dict[str, Any]:
    rows = []
    for s in report["scenarios"]:
        peak = s["status_peak_kib"]
        rows.append({"request": s["request"], "right": s["right"], "model_calls": s["model_calls"],
                     "mcp_calls": [(c["tool"], c["args"]) for c in s["mcp_calls"]],
                     "llm_requests": s["llm_requests"], "prompt_tokens": s["prompt_tokens"],
                     "cached_tokens": s["cached_tokens"], "wall_s": s["wall_s"], "llm_s": s["llm_s"],
                     "harness_peak_mib": round(peak.get("VmHWM", 0) / 1024, 1),
                     "harness_anon_mib": round(peak.get("RssAnon", 0) / 1024, 1), "returncode": s["returncode"]})
    return {"harness": report["harness"], "right": sum(r["right"] for r in rows), "n": len(rows), "rows": rows}
