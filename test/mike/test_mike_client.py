"""Mike Step 12: the small-talk client (`src/mike/mike.py`, `mike_client.feature`).

    uv run pytest test/mike/test_mike_client.py                    # deterministic
    uv run pytest test/mike/test_mike_client.py -m integration -s  # real llama-server, desk

The deterministic tests check that the conversation is kept as the exact
token ids sent and generated. The integration test plays Step 12.1's
conversations through the client against a real `llama-server`, twice: the
first start reads layer L0 and saves it, the second restores it. It checks
that a follow-up turn reads only its own new tokens.
"""

from __future__ import annotations

import io
import json
import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src" / "mike"))
import mike as st  # noqa: E402

import mike_eval as ev  # noqa: E402
import mike_server as ms  # noqa: E402
from test_chat_baseline import CONVERSATIONS  # noqa: E402

RUN_DIR = ev.REPO / "results/mike/client-desk" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
MODEL = Path(os.environ.get("MIKE_ASSET_ROOT", "/data/michael/tanstaafllm/mike-assets")) / "LFM2.5-350M-Q4_0.gguf"


def fake_tokenize(text: str) -> list[int]:
    return [ord(c) + 100 for c in text]


T = st.Template(bos=1, end=7, newline=fake_tokenize("\n"))


def test_follow_up_prompt_starts_with_the_exact_history():
    conv = st.Conversation(fake_tokenize, "S", T)
    assert conv.l0[0] == T.bos
    p1 = conv.prompt_for("hi")
    conv.finish(p1, [500, 501, T.end])
    p2 = conv.prompt_for("again")
    assert p2[:len(p1) + 3] == p1 + [500, 501, T.end]
    assert p2[len(p1) + 3] == ord("\n") + 100


def test_cut_answer_is_closed():
    conv = st.Conversation(fake_tokenize, "S", T)
    p1 = conv.prompt_for("hi")
    conv.finish(p1, [500, 501])
    assert conv.ids[len(p1):] == [500, 501, T.end, ord("\n") + 100]


def test_long_conversation_rolls_over_to_the_last_exchange():
    conv = st.Conversation(fake_tokenize, "S", T)
    rolled = []
    for i in range(40):
        p = conv.prompt_for(f"q{i}")
        rolled.append(conv.finish(p, [600 + i] * 60 + [T.end]))
        if rolled[-1]:
            kept = p[len(p) - len(fake_tokenize(f"<|im_start|>user\nq{i}<|im_end|>\n<|im_start|>assistant\n")):]
            break
    assert rolled[-1] and not any(rolled[:-1])
    assert conv.ids[:len(conv.l0)] == conv.l0
    assert conv.ids[len(conv.l0):] == kept + [600 + i] * 60 + [T.end] + T.newline
    assert conv.turns == [(len(conv.l0), len(conv.ids))]


def test_question_is_capped():
    conv = st.Conversation(fake_tokenize, "S", T)
    assert len(conv.prompt_for("x" * 5000)) < len(conv.l0) + st.MAX_QUESTION_CHARS + 60


def test_brain_lock(tmp_path):
    lock = tmp_path / "brain.lock"
    lock.write_text("mannie 1\n")  # pid 1 is always alive
    with pytest.raises(st.BrainBusy):
        st.take_lock(lock)
    lock.write_text("mannie 999999999\n")  # gone
    st.take_lock(lock)
    assert lock.read_text() == f"mike {os.getpid()}\n"
    st.name_server_in_lock(lock, 4242)
    assert lock.read_text() == f"mike {os.getpid()} 4242\n"
    st.release_lock(lock)
    assert not lock.exists()


def test_stale_mike_lock_stops_its_orphan_server(tmp_path):
    fake = tmp_path / "llama-server"  # a process whose name is llama-server
    fake.symlink_to("/bin/sleep")
    orphan = subprocess.Popen([str(fake), "60"])
    try:
        lock = tmp_path / "brain.lock"
        lock.write_text(f"mike 999999999 {orphan.pid}\n")  # the client died, its server did not
        st.take_lock(lock)
        assert orphan.wait(5) is not None
        assert lock.read_text() == f"mike {os.getpid()}\n"
    finally:
        orphan.kill()


def test_plain_drops_markdown_emphasis():
    assert st.plain("un total de **deux** prix") == "un total de deux prix"


class FakeStream:
    def __init__(self, events, interrupt_after=None):
        self.events, self.interrupt_after, self.closed = events, interrupt_after, False

    def __iter__(self):
        for i, e in enumerate(self.events):
            if i == self.interrupt_after:
                raise KeyboardInterrupt
            yield e

    def close(self):
        self.closed = True


class FakeServer:
    def __init__(self, stream):
        self._stream = stream

    def stream(self, prompt, body):
        it = iter(self._stream)

        class Gen:
            def __iter__(s):
                return it

            def __next__(s):
                return next(it)

            def close(s):
                self._stream.close()
        return Gen()


def test_ctrl_c_stops_the_answer_and_keeps_the_conversation():
    conv = st.Conversation(fake_tokenize, "S", T)
    events = [{"content": "Bon", "tokens": [500]}, {"content": "jour", "tokens": [501]},
              {"content": " !", "tokens": [502]}, {"stop": True, "timings": {}}]
    stream = FakeStream(events, interrupt_after=2)
    out = io.StringIO()
    r = st.answer(FakeServer(stream), conv, "hi", out, lang="en")
    assert r["stop"] == "user" and r["answer"] == "Bonjour" and stream.closed
    assert out.getvalue() == "Bonjour [stopped]\n"
    assert conv.ids[-3:] == [501, T.end, *T.newline]


def test_sse_events():
    lines = [b'data: {"content": "a"}\n', b"\n", b'data: {"stop": true}\n']
    assert list(st.sse_events(iter(lines))) == [{"content": "a"}, {"stop": True}]


def _port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.mark.integration
@pytest.mark.timeout(1800)
def test_smalltalk_desk():
    if not MODEL.is_file():
        pytest.skip("model missing")
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    slots = RUN_DIR / "slots"
    rows = []
    for start in ("cold", "warm"):
        server = st.Server(_port(), str(ms.SERVER), str(MODEL), slots, 4, RUN_DIR / f"llama-server-{start}.log")
        server.start(RUN_DIR / "brain.lock")
        try:
            for c, (lang, questions) in enumerate(CONVERSATIONS):
                conv = st.Conversation(server.tokenize, st.SYSTEM[lang], server.template())
                how = st.L0Frame(server, conv.l0).put_back()
                for t, q in enumerate(questions):
                    out = io.StringIO()
                    r = st.answer(server, conv, q, out)
                    r |= {"start": start, "conversation": c, "turn": t, "l0": how, "l0_tokens": len(conv.l0),
                          "streamed": out.getvalue().strip()}
                    rows.append(r)
        finally:
            server.stop()
    (RUN_DIR / "turns.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    follow = [r for r in rows if r["turn"] > 0]
    first_warm = [r for r in rows if r["turn"] == 0 and r["start"] == "warm"]
    summary = {"turns": len(rows),
               "follow_up_prompt_n_max": max(r["prompt_n"] for r in follow),
               "follow_up_new_tokens_max": max(r["prompt_tokens"] - (r["prompt_tokens"] - r["prompt_n"]) for r in follow),
               "first_turn_warm_prompt_n": [r["prompt_n"] for r in first_warm],
               "first_s_median": sorted(r["first_s"] for r in rows)[len(rows) // 2]}
    (RUN_DIR / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary))
    assert all(r["streamed"] == r["answer"] for r in rows)
    # a follow-up reads its own turn only: the previous answer's closing tokens and the new question
    assert summary["follow_up_prompt_n_max"] <= 40
    # after a restart, L0 comes from its frame: the first turn reads only the question
    assert all(r["l0"] == "restored" for r in first_warm)
    assert max(summary["first_turn_warm_prompt_n"]) <= 40


def _client(tmp_path, lock):
    """The client as a process, as in Mike's window, with its stdin open."""
    env = {**os.environ, "XDG_STATE_HOME": str(tmp_path / "state"), "MIKE_LOCK": str(lock),
           "MIKE_PORT": str(_port()), "MIKE_SERVER": str(ms.SERVER), "MIKE_MODEL": str(MODEL)}
    proc = subprocess.Popen([sys.executable, str(Path(st.__file__)), "--lang", "en"], env=env, text=True,
                            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    line = ""
    while "Ready" not in line:
        line = proc.stdout.readline()
        assert line, "the client stopped before it was ready"
    return proc


@pytest.mark.integration
@pytest.mark.timeout(300)
@pytest.mark.parametrize("sig", ["SIGHUP", "SIGTERM", "SIGKILL"])
def test_client_signal_leaves_no_server_and_no_lock(tmp_path, sig):
    """F2: the window closing (SIGHUP), a kill, even SIGKILL: the server goes with the client."""
    if not MODEL.is_file():
        pytest.skip("model missing")
    lock = tmp_path / "brain.lock"
    proc = _client(tmp_path, lock)
    owner = lock.read_text().split()
    assert owner[0] == "mike" and int(owner[1]) == proc.pid and len(owner) == 3
    server_pid = int(owner[2])
    assert st.is_llama_server(server_pid)
    proc.send_signal(getattr(__import__("signal"), sig))
    proc.wait(30)
    deadline = __import__("time").monotonic() + 15
    while st.alive(server_pid) and __import__("time").monotonic() < deadline:
        __import__("time").sleep(0.1)
    assert not st.alive(server_pid), f"llama-server survived {sig}"
    if sig != "SIGKILL":  # after SIGKILL the lock stays, stale, and the next start removes it
        assert not lock.exists()


@pytest.mark.integration
@pytest.mark.timeout(600)
def test_rollover_reads_only_the_kept_exchange(tmp_path, monkeypatch):
    """F1: past KEEP_CTX the next question reads the kept exchange and itself, not the whole history."""
    if not MODEL.is_file():
        pytest.skip("model missing")
    monkeypatch.setattr(st, "KEEP_CTX", 260)
    server = st.Server(_port(), str(ms.SERVER), str(MODEL), tmp_path / "slots", 4, tmp_path / "server.log")
    server.start(tmp_path / "brain.lock")
    rows = []
    try:
        conv = st.Conversation(server.tokenize, st.SYSTEM["en"], server.template())
        frame = st.L0Frame(server, conv.l0)
        frame.put_back()
        for q in ["What is the capital of France?", "And of Italy?", "And of Spain?", "And of Germany?",
                  "And of Japan?", "And of Peru?", "And of Chile?"]:
            r = st.answer(server, conv, q, io.StringIO(), lang="en")
            kept = len(conv.ids) - len(conv.l0)
            if r["rolled_over"]:
                frame.put_back()
            rows.append(r | {"kept_after": kept})
    finally:
        server.stop()
    (tmp_path / "rows.json").write_text(json.dumps(rows, indent=1))
    i = next(i for i, r in enumerate(rows) if r["rolled_over"])
    after = rows[i + 1]
    print(json.dumps([{k: r[k] for k in ("prompt_tokens", "prompt_n", "rolled_over")} for r in rows]))
    assert after["prompt_n"] <= rows[i]["kept_after"] + 30
