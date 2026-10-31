#!/usr/bin/env python3
"""Mike's client (Step 12 onwards; small talk first): one question per line, the answer streamed.

Runs on Luna in a terminal window (app_id "mike"), and on the desk host.
Standard library only, so Luna's system Python is enough; `prestac.py` must
sit next to this file.

* The model runs in `llama-server` (LFM2.5-350M, untrained). The client
  always starts its own server and stops it on exit. A server it finds on its
  port without a live Mike client is an orphan and is stopped first.
* The conversation is kept as **token ids**, not as text. Each turn sends the
  previous ids unchanged plus the new turn, so the server's prompt cache
  matches the whole history and reads only the new question. Re-rendering
  the history as text can tokenise a past answer differently, and then the
  server reads it again (Step 12.1, `docs/1201_01`).
* The fixed system prompt (layer L0) is a PreStaC frame in PreStaC's `Store`:
  saved once with the server's slot save, restored at start, so a restarted
  Mike does not read it again (`prestac.py`, Step 9).
* When the history passes `KEEP_CTX`, the conversation rolls over: L0 is
  restored and only the last exchange is kept and read again, with a notice
  (Step 13.2). Cutting turns out of the middle would make the server read
  the whole history again (`docs/16` F1).
* The window title becomes "Mike — ready" once input is accepted: Wyoh's
  FN+B (the Slate's "send to Mike") waits for that title, then types the
  text and Return (`worklines/wyoh/plan_wyoh.md` 6.10, 6.11).
* Luna has one brain at a time: before starting its server, the client takes
  `/tmp/luna-brain.lock`, written "mike <client pid> <server pid>", and
  refuses to start while another live client holds it (Mannie, for
  instance). The server dies with the client (its own process group, and a
  parent-death signal), and `SIGHUP`/`SIGTERM` run the client's clean-up.
* Every turn is logged, with its timings, to `$XDG_STATE_HOME/mike/chat.jsonl`.

Lines starting with "/" are commands: /new starts a new conversation,
/quit leaves. Ctrl+C stops the answer being written; at the prompt it quits.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterator

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prestac  # noqa: E402

READY_TITLE = "Mike — ready"

SYSTEM = {
    "fr": "Tu es Mike, un petit assistant qui bavarde. Réponds en français, en deux ou trois phrases courtes.",
    "en": "You are Mike, a small assistant for casual chat. Answer in English, in two or three short sentences.",
}
NOTICE = {"fr": {"new": "(nouvelle conversation)", "roll": "(conversation longue : je ne garde que le dernier échange)",
                 "stopped": " [arrêté]"},
          "en": {"new": "(new conversation)", "roll": "(long conversation: only the last exchange is kept)",
                 "stopped": " [stopped]"}}
SAMPLING = {"temperature": 0.1, "top_k": 50, "repeat_penalty": 1.05}  # LFM2.5 model card
CTX = 2048
MAX_TOKENS = 120
KEEP_CTX = 1600  # past this, the conversation rolls over
MAX_QUESTION_CHARS = 600  # about 150–200 tokens, so that KEEP_CTX + question + answer fits CTX
FRAME_BUDGET = 20 * 1024 * 1024


@dataclass
class Template:
    """The chat template's special ids, read from the server (LFM2: <|startoftext|> 1, <|im_end|> 7)."""

    bos: int
    end: int
    newline: list[int]


@dataclass
class Conversation:
    """The conversation as the exact token ids the server has read."""

    tokenize: Callable[[str], list[int]]
    system: str
    template: Template
    ids: list[int] = field(default_factory=list)
    l0: list[int] = field(default_factory=list)
    turns: list[tuple[int, int]] = field(default_factory=list)  # (start, end) of each finished turn in ids

    def __post_init__(self) -> None:
        self.l0 = [self.template.bos, *self.tokenize(f"<|im_start|>system\n{self.system}<|im_end|>\n")]
        self.reset()

    def reset(self) -> None:
        self.ids = list(self.l0)
        self.turns = []

    def prompt_for(self, question: str) -> list[int]:
        """The ids to send for this question: the history, unchanged, then the new turn."""
        question = question[:MAX_QUESTION_CHARS]
        return self.ids + self.tokenize(f"<|im_start|>user\n{question}<|im_end|>\n<|im_start|>assistant\n")

    def finish(self, prompt: list[int], answer_ids: list[int]) -> bool:
        """Record a finished turn: the prompt sent, then the answer ids exactly as generated.

        Returns True when the conversation rolled over: only L0 and this last
        exchange are kept, and the caller must put the slot back to L0.
        """
        start = len(self.ids)
        self.ids = prompt + answer_ids
        if not answer_ids or answer_ids[-1] != self.template.end:  # cut by the length limit or by Ctrl+C
            self.ids.append(self.template.end)
        self.ids += self.template.newline
        self.turns.append((start, len(self.ids)))
        if len(self.ids) <= KEEP_CTX or len(self.turns) < 2:
            return False
        s, e = self.turns[-1]
        self.ids = self.l0 + self.ids[s:e]
        self.turns = [(len(self.l0), len(self.ids))]
        return True


def sse_events(lines: Iterator[bytes]) -> Iterator[dict[str, Any]]:
    """The JSON objects of a server-sent-events stream (`data: {...}` lines)."""
    for raw in lines:
        line = raw.decode("utf-8", "replace").strip()
        if line.startswith("data: ") and line != "data: [DONE]":
            yield json.loads(line[6:])


# --- one brain on Luna ---------------------------------------------------------

class BrainBusy(RuntimeError):
    pass


def alive(pid: int) -> bool:
    return pid > 0 and Path(f"/proc/{pid}").exists()


def is_llama_server(pid: int) -> bool:
    try:
        argv0 = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")[0]
    except OSError:
        return False
    return Path(argv0.decode(errors="replace")).name == "llama-server"


def stop_pid(pid: int, wait_s: float = 10) -> None:
    """Stop a process (and its group when it leads one)."""
    try:
        os.killpg(pid, signal.SIGTERM) if os.getpgid(pid) == pid else os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    deadline = time.monotonic() + wait_s
    while alive(pid) and time.monotonic() < deadline:
        time.sleep(0.1)
    if alive(pid):
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass


def take_lock(lock: Path) -> None:
    """Write "mike <pid>" to the brain lock; refuse while another live client holds it.

    A Mike lock whose client is dead is stale; if its server outlived it,
    that orphan server is stopped first (`docs/16` F2).
    """
    for _ in range(2):
        try:
            fd = os.open(lock, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        except FileExistsError:
            owner = lock.read_text().split()
            pids = [int(p) for p in owner[1:] if p.isdigit()]
            if pids and alive(pids[0]):
                raise BrainBusy(" ".join(owner))
            if owner[:1] == ["mike"]:
                for pid in pids[1:]:
                    if alive(pid) and is_llama_server(pid):
                        stop_pid(pid)
            lock.unlink(missing_ok=True)
            continue
        with os.fdopen(fd, "w") as f:
            f.write(f"mike {os.getpid()}\n")
        return
    raise BrainBusy(str(lock))


def name_server_in_lock(lock: Path, server_pid: int) -> None:
    tmp = lock.with_name(lock.name + f".{os.getpid()}")
    tmp.write_text(f"mike {os.getpid()} {server_pid}\n")
    os.replace(tmp, lock)


def release_lock(lock: Path) -> None:
    try:
        if lock.read_text().split()[:2] == ["mike", str(os.getpid())]:
            lock.unlink()
    except (FileNotFoundError, IndexError):
        pass


def orphan_servers(port: int) -> list[int]:
    """`llama-server` processes listening on our port by their command line."""
    found = []
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            argv = proc.joinpath("cmdline").read_bytes().split(b"\0")
        except OSError:
            continue
        if argv and Path(argv[0].decode(errors="replace")).name == "llama-server" \
                and b"--port" in argv and str(port).encode() in argv:
            found.append(int(proc.name))
    return found


def _die_with_parent() -> None:
    """In the child: receive SIGTERM when the client dies, even by SIGKILL (Linux)."""
    try:
        ctypes.CDLL(None, use_errno=True).prctl(1, signal.SIGTERM)  # PR_SET_PDEATHSIG
    except (OSError, AttributeError):
        pass


# --- the server -----------------------------------------------------------------

class Server:
    """A `llama-server` on localhost, started and owned by the client."""

    def __init__(self, port: int, binary: str, model: str, slot_dir: Path, threads: int, log: Path,
                 repack: bool = False):
        self.port = port
        self.url = f"http://127.0.0.1:{port}"
        self.argv = [binary, "-m", model, "--host", "127.0.0.1", "--port", str(port), "-c", str(CTX),
                     "-np", "1", "-t", str(threads), "--no-webui", "--cache-ram", "0",
                     "-b", "16", "-ub", "16", "--slot-save-path", str(slot_dir)]
        if not repack:  # the repacked copy costs memory and was no faster on Luna (docs/1205_01)
            self.argv.append("--no-repack")
        self.model = Path(model)
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
        take_lock(lock)
        self.lock = lock
        for pid in orphan_servers(self.port):  # a server on our port with no live client (F3)
            stop_pid(pid)
        self.slot_dir.mkdir(parents=True, exist_ok=True)
        self.log.parent.mkdir(parents=True, exist_ok=True)
        with self.log.open("w") as log:
            self.process = subprocess.Popen(self.argv, stdout=log, stderr=subprocess.STDOUT,
                                            start_new_session=True, preexec_fn=_die_with_parent)
        name_server_in_lock(lock, self.process.pid)
        started = time.monotonic()
        while not self.alive():
            if self.process.poll() is not None:
                raise RuntimeError(f"llama-server stopped ({self.process.returncode}); see {self.log}")
            if time.monotonic() - started > timeout:
                raise TimeoutError(f"llama-server not ready after {timeout:.0f} s; see {self.log}")
            time.sleep(0.2)

    def stop(self) -> None:
        if self.process and self.process.poll() is None:
            stop_pid(self.process.pid)
            try:
                self.process.wait(1)
            except subprocess.TimeoutExpired:
                pass
        if self.lock:
            release_lock(self.lock)
            self.lock = None

    def rss_kib(self) -> dict[str, int]:
        """The server's memory (VmRSS, VmHWM)."""
        if not self.process:
            return {}
        out = {}
        try:
            for line in Path(f"/proc/{self.process.pid}/status").read_text().splitlines():
                key, _, value = line.partition(":")
                if key in ("VmRSS", "VmHWM"):
                    out[key] = int(value.split()[0])
        except OSError:
            pass
        return out

    def post(self, path: str, body: dict[str, Any], timeout: float = 600) -> Any:
        req = urllib.request.Request(self.url + path, data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)

    def get(self, path: str) -> Any:
        with urllib.request.urlopen(self.url + path, timeout=30) as r:
            return json.load(r)

    def tokenize(self, text: str) -> list[int]:
        return self.post("/tokenize", {"content": text, "parse_special": True})["tokens"]

    def template(self) -> Template:
        props = self.get("/props")
        bos, end = self.tokenize(props["bos_token"]), self.tokenize(props["eos_token"])
        if len(bos) != 1 or len(end) != 1:
            raise RuntimeError(f"unexpected special tokens: {props['bos_token']}={bos}, {props['eos_token']}={end}")
        return Template(bos[0], end[0], self.tokenize("\n"))

    def namespace(self) -> str:
        """What a frame depends on besides its tokens: the model file and the runtime build (F5)."""
        st = self.model.stat()
        build = self.get("/props").get("build_info", "unknown")
        return f"{self.model.name}|{st.st_size}|{int(st.st_mtime)}|{build}"

    def stream(self, prompt: list[int], body: dict[str, Any]) -> Iterator[dict[str, Any]]:
        req = urllib.request.Request(self.url + "/completion", headers={"Content-Type": "application/json"},
                                     data=json.dumps({"prompt": prompt, "stream": True, "return_tokens": True,
                                                      "cache_prompt": True, **body}).encode())
        with urllib.request.urlopen(req, timeout=600) as r:
            yield from sse_events(r)


class L0Frame:
    """Layer L0 as a PreStaC frame in PreStaC's Store (atomic commit, metadata, eviction; F4–F6)."""

    def __init__(self, server: Server, l0: list[int]):
        self.store = prestac.Store(server.slot_dir, FRAME_BUDGET)
        self.engine = prestac.HttpEngine(server.url)
        self.l0 = l0
        self.ns = server.namespace()
        self.key = prestac.frame_keys(self.ns, [prestac.Layer("L0", tuple(l0))])[0]
        for legacy in server.slot_dir.glob("l0-*.bin"):  # frames of the first client (Step 12.2)
            legacy.unlink(missing_ok=True)

    def put_back(self) -> str:
        """Make the slot hold exactly L0: restore its frame, or read L0 and save it."""
        if self.store.lookup(self.key):
            try:
                self.engine.restore(self.store.bin(self.key).name)
                self.store.touch(self.key)
                return "restored"
            except urllib.error.HTTPError:
                self.store.drop(self.key)  # unreadable for this server: read L0 again
        timings = self.engine.extend(self.l0)
        self.engine.save(self.store.tmp_name(self.key))
        self.store.commit(self.key, {"layers": ["L0"], "tokens": len(self.l0), "namespace": self.ns,
                                     "prompt_n": timings.get("prompt_n")})
        self.store.evict(pinned={self.key})
        return "read and saved"


def set_title(title: str) -> None:
    if sys.stdout.isatty():
        print(f"\033]2;{title}\007", end="", flush=True)


def plain(text: str) -> str:
    """The model's Markdown emphasis is not shown in a terminal (F11)."""
    return text.replace("**", "").replace("__", "")


def answer(server: Server, conv: Conversation, question: str, out=sys.stdout, lang: str = "fr") -> dict[str, Any]:
    """Stream one answer to `out`; Ctrl+C stops it and keeps what was written. Returns the turn's record."""
    prompt = conv.prompt_for(question)
    started = time.monotonic()
    first = None
    ids: list[int] = []
    text: list[str] = []
    final: dict[str, Any] = {}
    stopped = False
    events = server.stream(prompt, {"n_predict": MAX_TOKENS, **SAMPLING})
    try:
        for event in events:
            if event.get("stop"):
                final = event
                break
            if first is None:
                first = time.monotonic() - started
            ids += event.get("tokens", [])
            text.append(event.get("content", ""))
            print(plain(event.get("content", "")), end="", flush=True, file=out)
    except KeyboardInterrupt:  # F7: the answer stops, the conversation goes on
        stopped = True
        print(NOTICE[lang]["stopped"], end="", file=out)
    finally:
        events.close()  # closes the connection: the server stops writing
    print(file=out, flush=True)
    rolled = conv.finish(prompt, ids)
    tm = final.get("timings", {})
    return {"time": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "question": question, "answer": "".join(text).strip(),
            "prompt_tokens": len(prompt), "prompt_n": tm.get("prompt_n"), "predicted_n": tm.get("predicted_n"),
            "first_s": round(first or 0.0, 2), "total_s": round(time.monotonic() - started, 2),
            "prompt_ms": tm.get("prompt_ms"), "predicted_ms": tm.get("predicted_ms"),
            "stop": "user" if stopped else final.get("stop_type"), "rolled_over": rolled}


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

    def leave(signum, _frame):  # F2: the window closing (SIGHUP) or a kill (SIGTERM) runs `finally`
        raise SystemExit(128 + signum)
    for sig in (signal.SIGHUP, signal.SIGTERM):
        signal.signal(sig, leave)

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
        conv = Conversation(server.tokenize, SYSTEM[args.lang], server.template())
        frame = L0Frame(server, conv.l0)
        how = frame.put_back()
        start = {"event": "start", "lang": args.lang, "ready_s": round(time.monotonic() - t0, 2), "l0": how,
                 "l0_tokens": len(conv.l0), "repack": args.repack, "threads": args.threads, **server.rss_kib()}
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
                frame.put_back()
                print(NOTICE[args.lang]["new"], flush=True)
                continue
            set_title("Mike — thinking")
            record = answer(server, conv, line, lang=args.lang) | server.rss_kib()
            if record["rolled_over"]:  # the slot must hold L0 alone before the kept exchange is read
                frame.put_back()
                print(NOTICE[args.lang]["roll"], flush=True)
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
