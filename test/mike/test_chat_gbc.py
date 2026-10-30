"""Mike 10.6: Chat-GBC's shipped models, reproduced on the desk host (`chat_gbc.feature`).

    uv run pytest test/mike/test_chat_gbc.py -m integration -s

Chat-GBC (github.com/rudydel/Chat-GBC, commit db83f9b) is a 2-layer
transformer of 21k–138k parameters that runs on a Game Boy. This test does
not use the ROM or an emulator: it runs the project's own Python entry points
on Termidor, with its shipped checkpoints, and keeps their complete output.

1. Its evaluation (`llm.evaluate`) with the float model and with the bit-exact
   integer simulator (what the Game Boy computes), compared with the numbers
   in each model's `train_log.txt`.
2. A few chat questions (`llm.chat -q`), timed: two from its README, one
   off-topic, and two of Mike's requests.

The project's training is not run: Mike's non-goal excludes training.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

import mike_eval as ev

ROOT = Path(os.environ.get("MIKE_TOOLS_ROOT", "/data/michael/tanstaafllm/mike-tools")) / "chat-gbc"
SRC, PYTHON = ROOT / "src", ROOT / "venv/bin/python"
RUN_DIR = ev.REPO / "results/mike/chat-gbc" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
QUESTIONS = [
    "who designed the game boy",  # README
    "what cpu does the game boy use",  # README
    "what is the capital of france",  # off-topic
    "ouvre la calculatrice",  # Mike's requests
    "open the calculator",
]
LINE = re.compile(r"^(?:\[(\w+)\] )?(train|held-out) questions: exact match (\d+)%, char error rate ([\d.]+) \((\d+) questions\)"
                  r"|^    (\S+)\s+exact\s+(\d+)%\s+cer ([\d.]+)\s+\((\d+)\)")


def parse(text: str) -> dict:
    """`{"train": {"all": exact, "facts.jsonl": exact, …}, "held-out": {…}}` from evaluate's output."""
    out: dict[str, dict] = {}
    current = None
    for line in text.splitlines():
        m = LINE.match(line)
        if not m:
            continue
        if m.group(2):
            current = out.setdefault(m.group(2), {})
            current["all"] = int(m.group(3))
            current["n"] = int(m.group(5))
        elif current is not None:
            current[m.group(6)] = int(m.group(7))
    return out


def claimed(model: str, mode: str) -> dict:
    """The same numbers from the model's own training log (its final `[float]` / `[int]` evaluation)."""
    log = (SRC / "models" / model / "train_log.txt").read_text()
    keep = []
    for block in re.split(r"(?=^\[(?:float|int)\] )", log, flags=re.M):
        if block.startswith(f"[{mode}] "):
            keep.append(block)
    return parse("".join(keep))


def run(argv: list[str], log: Path) -> tuple[str, float]:
    started = time.perf_counter()
    done = subprocess.run(argv, cwd=SRC, capture_output=True, text=True, timeout=3600)
    seconds = time.perf_counter() - started
    log.write_text(" ".join(argv) + f"\n# exit {done.returncode}, {seconds:.1f} s\n" + done.stdout + done.stderr)
    assert done.returncode == 0, log
    return done.stdout, seconds


def test_parse_reads_evaluate_lines():
    text = ("[int] held-out questions: exact match 44%, char error rate 0.60 (144 questions)\n"
            "    facts.jsonl          exact  32%  cer 0.74  (103)\n"
            "    offtopic.jsonl       exact  73%  cer 0.24  (41)\n")
    assert parse(text) == {"held-out": {"all": 44, "n": 144, "facts.jsonl": 32, "offtopic.jsonl": 73}}


@pytest.fixture(scope="module")
def ready():
    if not PYTHON.is_file() or not (SRC / "models/tiny/ckpt.pt").is_file():
        pytest.skip("Chat-GBC clone or its venv missing")
    RUN_DIR.mkdir(parents=True, exist_ok=True)


@pytest.mark.integration
@pytest.mark.timeout(7200)
@pytest.mark.parametrize("model", ["tiny", "micro"])
@pytest.mark.parametrize("mode", ["float", "int"])
def test_evaluate_matches_training_log(ready, model, mode):
    argv = [str(PYTHON), "-m", "llm.evaluate", f"models/{model}/ckpt.pt", "--chat", "data/gameboy",
            "--heldout", "0.2", "--seed", "0", "--show", "200"]
    if mode == "int":
        argv.append("--int")
    stdout, seconds = run(argv, RUN_DIR / f"evaluate.{model}.{mode}.log")
    got, want = parse(stdout), claimed(model, mode)
    row = {"model": model, "mode": mode, "seconds": round(seconds, 1), "got": got, "claimed": want,
           "same": got == want}
    with (RUN_DIR / "summary.jsonl").open("a") as f:
        f.write(json.dumps(row) + "\n")
    print(json.dumps(row))
    assert got == want


@pytest.mark.integration
@pytest.mark.timeout(1800)
@pytest.mark.parametrize("model", ["tiny", "micro"])
@pytest.mark.parametrize("mode", ["float", "int"])
def test_chat_questions(ready, model, mode):
    rows = []
    for question in QUESTIONS:
        argv = [str(PYTHON), "-m", "llm.chat", f"models/{model}/ckpt.pt", "-q", question]
        if mode == "int":
            argv.append("--int")
        slug = re.sub(r"\W+", "-", question).strip("-")
        stdout, seconds = run(argv, RUN_DIR / f"chat.{model}.{mode}.{slug}.log")
        rows.append({"model": model, "mode": mode, "question": question, "answer": stdout.strip(),
                     "seconds_with_load": round(seconds, 2)})
    with (RUN_DIR / "chat.jsonl").open("a") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps(rows, ensure_ascii=False, indent=1))
    assert all(r["answer"] for r in rows)
