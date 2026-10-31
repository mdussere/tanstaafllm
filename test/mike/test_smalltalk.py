"""Mike Step 12: the small-talk client (`src/mike/smalltalk.py`, `smalltalk.feature`).

    uv run pytest test/mike/test_smalltalk.py                    # deterministic
    uv run pytest test/mike/test_smalltalk.py -m integration -s  # real llama-server, desk

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
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src" / "mike"))
import smalltalk as st  # noqa: E402

import mike_eval as ev  # noqa: E402
import mike_server as ms  # noqa: E402
from test_chat_baseline import CONVERSATIONS  # noqa: E402

RUN_DIR = ev.REPO / "results/mike/smalltalk-desk" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
MODEL = Path(os.environ.get("MIKE_ASSET_ROOT", "/data/michael/tanstaafllm/mike-assets")) / "LFM2.5-350M-Q4_0.gguf"


def fake_tokenize(text: str) -> list[int]:
    return [ord(c) + 100 for c in text]


def test_follow_up_prompt_starts_with_the_exact_history():
    conv = st.Conversation(fake_tokenize, "S")
    assert conv.l0[0] == st.BOS
    p1 = conv.prompt_for("hi")
    conv.finish(p1, [500, 501, st.IM_END])
    p2 = conv.prompt_for("again")
    assert p2[:len(p1) + 3] == p1 + [500, 501, st.IM_END]
    assert p2[len(p1) + 3] == ord("\n") + 100


def test_cut_answer_is_closed():
    conv = st.Conversation(fake_tokenize, "S")
    p1 = conv.prompt_for("hi")
    conv.finish(p1, [500, 501])
    assert conv.ids[len(p1):] == [500, 501, st.IM_END, ord("\n") + 100]


def test_oldest_turns_are_forgotten():
    conv = st.Conversation(fake_tokenize, "S")
    for i in range(40):
        conv.finish(conv.prompt_for(f"q{i}"), [600] * 60 + [st.IM_END])
    assert len(conv.ids) <= st.KEEP_CTX
    assert conv.ids[:len(conv.l0)] == conv.l0
    assert conv.turns[0][0] == len(conv.l0)


def test_brain_lock(tmp_path):
    lock = tmp_path / "brain.lock"
    lock.write_text("mannie 1\n")  # pid 1 is always alive
    with pytest.raises(st.BrainBusy):
        st.take_lock(lock)
    lock.write_text("mannie 999999999\n")  # gone
    st.take_lock(lock)
    assert lock.read_text() == f"mike {os.getpid()}\n"
    st.release_lock(lock)
    assert not lock.exists()


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
                conv = st.Conversation(server.tokenize, st.SYSTEM[lang])
                name = f"l0-{lang}.bin"
                how = server.restore_or_save(conv.l0, name)
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
