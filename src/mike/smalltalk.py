#!/usr/bin/env python3
"""Mike's small-talk client (Step 12): one question per line, the answer streamed.

Runs on Luna in a terminal window (app_id "mike"), and on the desk host.
Standard library only, so Luna's system Python is enough.

* The model runs in `llama-server` (LFM2.5-350M, untrained). The client
  starts it if nothing answers on the port, and stops it on exit.
* The conversation is kept as **token ids**, not as text. Each turn sends the
  previous ids unchanged plus the new turn, so the server's prompt cache
  matches the whole history and reads only the new question. Re-rendering
  the history as text can tokenise a past answer differently, and then the
  server reads it again (Step 12.1, `docs/1201_01`).
* The fixed system prompt (layer L0) is a PreStaC frame: saved once with the
  server's slot save, restored at start, so a restarted Mike does not read it
  again (`prestac.py`, Step 9).
* The window title becomes "Mike — ready" once input is accepted: Wyoh's
  FN+B (the Slate's "send to Mike") waits for that title, then types the
  text and Return (`worklines/wyoh/plan_wyoh.md` 6.10).
* Luna has one brain at a time: before starting its own server, the client
  takes `/tmp/luna-brain.lock` ("mike <pid>") and refuses to start while
  another live process holds it (Mannie, for instance). The lock goes with
  the server.
* Every turn is logged, with its timings, to `$XDG_STATE_HOME/mike/chat.jsonl`.

Lines starting with "/" are commands: /new starts a new conversation,
/quit leaves.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterator

READY_TITLE = "Mike — ready"
BOS, IM_END = 1, 7  # LFM2: <|startoftext|>, <|im_end|> (also the end of an answer)

SYSTEM = {
    "fr": "Tu es Mike, un petit assistant qui bavarde. Réponds en français, en deux ou trois phrases courtes.",
    "en": "You are Mike, a small assistant for casual chat. Answer in English, in two or three short sentences.",
}
SAMPLING = {"temperature": 0.1, "top_k": 50, "repeat_penalty": 1.05}  # LFM2.5 model card
MAX_TOKENS = 120
KEEP_CTX = 1600  # history kept under this many tokens; the server's context is 2,048


@dataclass
class Conversation:
    """The conversation as the exact token ids the server has read."""

    tokenize: Callable[[str], list[int]]
    system: str
    ids: list[int] = field(default_factory=list)
    l0: list[int] = field(default_factory=list)
    turns: list[tuple[int, int]] = field(default_factory=list)  # (start, end) of each finished turn in ids

    def __post_init__(self) -> None:
        self.l0 = [BOS, *self.tokenize(f"<|im_start|>system\n{self.system}<|im_end|>\n")]
        self.reset()

    def reset(self) -> None:
        self.ids = list(self.l0)
        self.turns = []

    def prompt_for(self, question: str) -> list[int]:
        """The ids to send for this question: the history, unchanged, then the new turn."""
        return self.ids + self.tokenize(f"<|im_start|>user\n{question}<|im_end|>\n<|im_start|>assistant\n")

    def finish(self, prompt: list[int], answer_ids: list[int]) -> None:
        """Record a finished turn: the prompt sent, then the answer ids exactly as generated."""
        start = len(self.ids)
        self.ids = prompt + answer_ids
        if not answer_ids or answer_ids[-1] != IM_END:  # cut by the length limit
            self.ids.append(IM_END)
        self.ids += self.tokenize("\n")
        self.turns.append((start, len(self.ids)))
        while len(self.ids) > KEEP_CTX and len(self.turns) > 1:  # forget the oldest turns
            s, e = self.turns.pop(0)
            self.ids = self.ids[:s] + self.ids[e:]
            self.turns = [(a - (e - s), b - (e - s)) for a, b in self.turns]


def sse_events(lines: Iterator[bytes]) -> Iterator[dict[str, Any]]:
    """The JSON objects of a server-sent-events stream (`data: {...}` lines)."""
    for raw in lines:
        line = raw.decode("utf-8", "replace").strip()
        if line.startswith("data: ") and line != "data: [DONE]":
            yield json.loads(line[6:])


class Server:
    """A `llama-server` on localhost: found running, or started and owned by the client."""

    def __init__(self, port: int, binary: str, model: str, slot_dir: Path, threads: int, log: Path,
                 repack: bool = False):
        self.url = f"http://127.0.0.1:{port}"
        self.argv = [binary, "-m", model, "--host", "127.0.0.1", "--port", str(port), "-c", "2048",
                     "-np", "1", "-t", str(threads), "--no-webui", "--cache-ram", "0",
                     "-b", "16", "-ub", "16", "--slot-save-path", str(slot_dir)]
        if not repack:  # the repacked copy of the weights costs memory; its speed on ARM is to measure
            self.argv.append("--no-repack")
        self.slot_dir, self.log = slot_dir, log
        self.process: subprocess.Popen | None = None
        self.lock: Path | None = None

    def alive(self) -> bool:
        try:
            with urllib.request.urlopen(self.url + "/health", timeout=1) as r:
                return r.status == 200
        except OSError:
            return False

    def start(self, lock: Path, timeout: float = 300) -> None:
        if self.alive():
            return
        take_lock(lock)
        self.lock = lock
        self.slot_dir.mkdir(parents=True, exist_ok=True)
        self.log.parent.mkdir(parents=True, exist_ok=True)
        with self.log.open("w") as log:
            self.process = subprocess.Popen(self.argv, stdout=log, stderr=subprocess.STDOUT)
        started = time.monotonic()
        while not self.alive():
            if self.process.poll() is not None:
                raise RuntimeError(f"llama-server stopped ({self.process.returncode}); see {self.log}")
            if time.monotonic() - started > timeout:
                raise TimeoutError(f"llama-server not ready after {timeout:.0f} s; see {self.log}")
            time.sleep(0.2)

    def stop(self) -> None:
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(10)
            except subprocess.TimeoutExpired:
                self.process.kill()
        if self.lock:
            release_lock(self.lock)
            self.lock = None

    def rss_kib(self) -> dict[str, int]:
        """The owned server's memory (VmRSS, VmHWM), or {} when the server is not ours."""
        if not self.process:
            return {}
        out = {}
        for line in Path(f"/proc/{self.process.pid}/status").read_text().splitlines():
            key, _, value = line.partition(":")
            if key in ("VmRSS", "VmHWM"):
                out[key] = int(value.split()[0])
        return out

    def post(self, path: str, body: dict[str, Any], timeout: float = 600) -> Any:
        req = urllib.request.Request(self.url + path, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)

    def tokenize(self, text: str) -> list[int]:
        return self.post("/tokenize", {"content": text, "parse_special": True})["tokens"]

    def stream(self, prompt: list[int], body: dict[str, Any]) -> Iterator[dict[str, Any]]:
        req = urllib.request.Request(self.url + "/completion", headers={"Content-Type": "application/json"},
                                     data=json.dumps({"prompt": prompt, "stream": True, "return_tokens": True,
                                                      "cache_prompt": True, **body}).encode())
        with urllib.request.urlopen(req, timeout=600) as r:
            yield from sse_events(r)

    def restore_or_save(self, l0: list[int], name: str) -> str:
        """Layer L0 as a PreStaC frame: restore its slot file, or read L0 once and save it."""
        if (self.slot_dir / name).is_file():
            try:
                self.post("/slots/0?action=restore", {"filename": name})
                return "restored"
            except urllib.error.HTTPError:
                pass  # a frame from another build or model: read L0 again below
        self.post("/completion", {"prompt": l0, "n_predict": 0, "cache_prompt": True})
        self.post("/slots/0?action=save", {"filename": name})
        return "read and saved"


class BrainBusy(RuntimeError):
    pass


def take_lock(lock: Path) -> None:
    """Write "mike <pid>" to the brain lock; refuse while another live process holds it."""
    for _ in range(2):
        try:
            fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        except FileExistsError:
            owner = lock.read_text().split()
            pid = int(owner[1]) if len(owner) == 2 and owner[1].isdigit() else None
            if pid and Path(f"/proc/{pid}").exists():
                raise BrainBusy(" ".join(owner))
            lock.unlink(missing_ok=True)  # a stale lock: its process is gone
            continue
        with os.fdopen(fd, "w") as f:
            f.write(f"mike {os.getpid()}\n")
        return
    raise BrainBusy(str(lock))


def release_lock(lock: Path) -> None:
    try:
        if lock.read_text().split() == ["mike", str(os.getpid())]:
            lock.unlink()
    except FileNotFoundError:
        pass


def set_title(title: str) -> None:
    if sys.stdout.isatty():
        print(f"\033]2;{title}\007", end="", flush=True)


def answer(server: Server, conv: Conversation, question: str, out=sys.stdout) -> dict[str, Any]:
    """Stream one answer to `out`; return the turn's record."""
    prompt = conv.prompt_for(question)
    started = time.monotonic()
    first = None
    ids: list[int] = []
    text: list[str] = []
    final: dict[str, Any] = {}
    for event in server.stream(prompt, {"n_predict": MAX_TOKENS, **SAMPLING}):
        if event.get("stop"):
            final = event
            break
        if first is None:
            first = time.monotonic() - started
        ids += event.get("tokens", [])
        text.append(event.get("content", ""))
        print(event.get("content", ""), end="", flush=True, file=out)
    print(file=out, flush=True)
    conv.finish(prompt, ids)
    tm = final.get("timings", {})
    return {"time": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "question": question, "answer": "".join(text).strip(),
            "prompt_tokens": len(prompt), "prompt_n": tm.get("prompt_n"), "predicted_n": tm.get("predicted_n"),
            "first_s": round(first or 0.0, 2), "total_s": round(time.monotonic() - started, 2),
            "prompt_ms": tm.get("prompt_ms"), "predicted_ms": tm.get("predicted_ms"),
            "stop": final.get("stop_type")}


def main(argv: list[str] | None = None) -> int:
    home = Path.home()
    state = Path(os.environ.get("XDG_STATE_HOME", home / ".local/state")) / "mike"
    opt = Path(os.environ.get("MIKE_HOME", home / ".local/opt/mike"))
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--lang", choices=sorted(SYSTEM), default=os.environ.get("MIKE_LANG", "fr"))
    p.add_argument("--port", type=int, default=int(os.environ.get("MIKE_PORT", "8091")))
    p.add_argument("--server", default=os.environ.get("MIKE_SERVER", str(opt / "llama-b11429/llama-server")))
    p.add_argument("--model", default=os.environ.get("MIKE_MODEL", str(opt / "LFM2.5-350M-Q4_0.gguf")))
    p.add_argument("--lock", default=os.environ.get("MIKE_LOCK", "/tmp/luna-brain.lock"))
    p.add_argument("--repack", action="store_true", default=os.environ.get("MIKE_REPACK") == "1")
    p.add_argument("--threads", type=int, default=int(os.environ.get("MIKE_THREADS", "4")))
    args = p.parse_args(argv)

    set_title("Mike — starting")
    print("Mike démarre…" if args.lang == "fr" else "Mike is starting…", flush=True)
    t0 = time.monotonic()
    server = Server(args.port, args.server, args.model, state / "slots", args.threads, state / "llama-server.log",
                    args.repack)
    try:
        try:
            server.start(Path(args.lock))
        except BrainBusy as busy:
            print(f"Luna's brain is busy ({busy}); Mike cannot start now.", flush=True)
            set_title("Mike — busy")
            input()
            return 1
        conv = Conversation(server.tokenize, SYSTEM[args.lang])
        frame = "l0-" + hashlib.sha256(
            json.dumps([Path(args.model).name, conv.l0]).encode()).hexdigest()[:16] + ".bin"
        how = server.restore_or_save(conv.l0, frame)
        start = {"event": "start", "lang": args.lang, "ready_s": round(time.monotonic() - t0, 2), "l0": how,
                 "l0_tokens": len(conv.l0), "own_server": server.process is not None,
                 "repack": args.repack, "threads": args.threads, **server.rss_kib()}
        log = state / "chat.jsonl"
        with log.open("a") as f:
            f.write(json.dumps(start, ensure_ascii=False) + "\n")
        print(f"Prêt ({start['ready_s']} s). Pose ta question." if args.lang == "fr"
              else f"Ready ({start['ready_s']} s). Ask away.", flush=True)
        set_title(READY_TITLE)
        while True:
            try:
                line = input("> ").strip()
            except EOFError:
                break
            if not line:
                continue
            if line in ("/quit", "/exit"):
                break
            if line == "/new":
                conv.reset()
                server.restore_or_save(conv.l0, frame)
                print("(nouvelle conversation)" if args.lang == "fr" else "(new conversation)", flush=True)
                continue
            set_title("Mike — thinking")
            record = answer(server, conv, line) | server.rss_kib()
            set_title(READY_TITLE)
            with log.open("a") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
