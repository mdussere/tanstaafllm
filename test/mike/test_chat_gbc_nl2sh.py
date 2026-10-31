"""Mike Step 11: Rudy's Chat-GBC models trained on natural language → shell (`chat_gbc_nl2sh.feature`).

    uv run pytest test/mike/test_chat_gbc_nl2sh.py -m integration -s -k tiny

Chat-GBC (github.com/rudydel/Chat-GBC, commit db83f9b) with one change: its
tokenizer keeps case and every printable ASCII character, so that commands
survive (`chat_gbc_nl2sh.patch`, applied in the clone `mike-tools/chat-gbc/nl2sh`).
Each configuration (tiny, micro) is trained from scratch with Rudy's recipe and
step counts (12,000 pre-training steps, 8,000 fine-tuning steps, batch 32) on the
NL2SH-ALFA training pairs (MIT ALFA, NAACL 2025), without his question
augmentation, which drops punctuation, words and arguments that a command needs.
Then every NL2SH-ALFA test request (300, two accepted commands each) is asked
once, greedy (`chat_gbc_nl2sh_eval.py`).

The checkpoints stay outside the repository (`mike-tools/chat-gbc/runs/`).
"""

from __future__ import annotations

import csv
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

import mike_eval as ev

TOOLS = Path(os.environ.get("MIKE_TOOLS_ROOT", "/data/michael/tanstaafllm/mike-tools")) / "chat-gbc"
CLONE, PYTHON = TOOLS / "nl2sh", TOOLS / "venv/bin/python"
DATA = Path(os.environ.get("MIKE_ASSET_ROOT", "/data/michael/tanstaafllm/mike-assets")) / "datasets/NL2SH-ALFA"
PATCH = Path(__file__).with_name("chat_gbc_nl2sh.patch")
EVAL = Path(__file__).with_name("chat_gbc_nl2sh_eval.py")
STAMP = os.environ.get("MIKE_NL2SH_STAMP") or datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")  # shared by parallel runs
RUN_DIR = ev.REPO / "results/mike/chat-gbc-nl2sh" / STAMP
MAX_CHARS = 250  # request + command; longer training pairs cannot fit a 112–128-token context
STEPS = {"pretrain": int(os.environ.get("MIKE_NL2SH_PRETRAIN", "12000")),
         "sft": int(os.environ.get("MIKE_NL2SH_SFT", "8000"))}


def nl2sh_train_items(rows: list[dict]) -> tuple[list[dict], int]:
    """Chat-GBC chat lines from NL2SH training rows; pairs too long for the context dropped."""
    keep = [{"q": r["nl"].strip(), "a": r["bash"].strip()} for r in rows
            if r["nl"].strip() and r["bash"].strip() and len(r["nl"]) + len(r["bash"]) <= MAX_CHARS]
    return keep, len(rows) - len(keep)


def nl2sh_test_items(rows: list[dict]) -> list[dict]:
    return [{"nl": r["nl"].strip(), "bash": [r["bash"].strip(), r["bash2"].strip()],
             "difficulty": int(r["difficulty"])} for r in rows]


def prepare(out: Path) -> dict:
    with (DATA / "train.csv").open(newline="") as f:
        train, dropped = nl2sh_train_items(list(csv.DictReader(f)))
    with (DATA / "test.csv").open(newline="") as f:
        test = nl2sh_test_items(list(csv.DictReader(f)))
    out.mkdir(parents=True, exist_ok=True)
    (out / "train.jsonl").write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in train))
    # Rudy's trainer reports its own held-out score against the first accepted command.
    (out / "heldout.jsonl").write_text("".join(json.dumps({"q": i["nl"], "a": i["bash"][0]}, ensure_ascii=False) + "\n"
                                               for i in test))
    (out / "test.jsonl").write_text("".join(json.dumps(i, ensure_ascii=False) + "\n" for i in test))
    return {"train": len(train), "train_dropped_too_long": dropped, "test": len(test)}


def run(argv: list[str], log: Path, timeout: int) -> float:
    started = time.perf_counter()
    with log.open("w") as f:
        f.write(" ".join(argv) + "\n")
        f.flush()
        done = subprocess.run(argv, cwd=CLONE, stdout=f, stderr=subprocess.STDOUT, text=True, timeout=timeout)
        seconds = time.perf_counter() - started
        f.write(f"# exit {done.returncode}, {seconds:.1f} s\n")
    assert done.returncode == 0, log
    return seconds


def test_train_items_drop_long_pairs():
    rows = [{"nl": "list files", "bash": "ls"}, {"nl": "x" * 200, "bash": "y" * 60}, {"nl": " ", "bash": "ls"}]
    assert nl2sh_train_items(rows) == ([{"q": "list files", "a": "ls"}], 2)


def test_test_items_keep_both_commands():
    rows = [{"nl": "list files ", "bash": "ls", "bash2": "ls -l", "difficulty": "0"}]
    assert nl2sh_test_items(rows) == [{"nl": "list files", "bash": ["ls", "ls -l"], "difficulty": 0}]


@pytest.fixture(scope="module")
def ready():
    if not PYTHON.is_file() or not (CLONE / "llm/train.py").is_file() or not (DATA / "train.csv").is_file():
        pytest.skip("Chat-GBC shell clone, its venv or NL2SH-ALFA missing")
    tracked = subprocess.run(["git", "ls-files", "configs"], cwd=CLONE, capture_output=True, text=True).stdout
    if "tiny-sh.json" not in tracked:  # once only: parallel runs would race for the index lock
        subprocess.run(["git", "add", "-N", "configs"], cwd=CLONE, check=True)
    diff = subprocess.run(["git", "diff", "db83f9b"], cwd=CLONE, capture_output=True, text=True, check=True).stdout
    assert diff == PATCH.read_text(), "the clone differs from chat_gbc_nl2sh.patch"
    RUN_DIR.mkdir(parents=True, exist_ok=True)


@pytest.mark.integration
@pytest.mark.timeout(6 * 3600)
@pytest.mark.parametrize("model", ["tiny", "micro"])
def test_train_and_measure(ready, model):
    out = RUN_DIR / model
    data = prepare(out / "data")
    ckpt_dir = TOOLS / "runs" / STAMP / f"{model}-sh"
    train_s = run([str(PYTHON), "-m", "llm.train", "--config", f"configs/{model}-sh.json", "--out", str(ckpt_dir),
                   "--chat", str(out / "data/train.jsonl"), "--heldout", "0",
                   "--heldout-chat", str(out / "data/heldout.jsonl"),
                   "--pretrain-steps", str(STEPS["pretrain"]), "--sft-steps", str(STEPS["sft"]),
                   "--augment", "0", "--threads", os.environ.get("MIKE_NL2SH_THREADS", "2"), "--seed", "0"],
                  out / "train.log", timeout=5 * 3600)
    eval_s = run([str(PYTHON), str(EVAL), str(ckpt_dir / "ckpt.pt"), str(out / "data/test.jsonl"), str(out)],
                 out / "eval.log", timeout=3600)
    result = json.loads((out / "eval.json").read_text())
    row = {"model": model, "steps": STEPS, "data": data, "train_s": round(train_s), "eval_s": round(eval_s),
           "ckpt": str(ckpt_dir / "ckpt.pt")} | {k: result[k] for k in (
               "params", "n", "exact", "exact_spaces", "utility", "cer_mean", "fits_ctx", "exact_when_fits")}
    with (RUN_DIR / "summary.jsonl").open("a") as f:
        f.write(json.dumps(row) + "\n")
    print(json.dumps(row))
    assert result["n"] == 300
