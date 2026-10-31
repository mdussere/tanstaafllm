"""Mike Step 11: a pre-trained model, untrained, on the NL2SH-ALFA test set (`nl2sh_baseline.feature`).

    uv run pytest test/mike/test_nl2sh_baseline.py -m integration -s

The baseline against which the trained models of Step 11 are read. Each of
the 300 NL2SH-ALFA test requests (two accepted commands each) is sent once,
greedy, through `llama-server`'s chat endpoint with a short system prompt
asking for one command; the answer's first command line is compared with
both accepted commands, with the same measures as `chat_gbc_nl2sh_eval.py`.
Exact match undercounts: a different but equivalent command counts as wrong.
"""

from __future__ import annotations

import csv
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

import mike_eval as ev
import mike_server as ms

ASSETS = Path(os.environ.get("MIKE_ASSET_ROOT", "/data/michael/tanstaafllm/mike-assets"))
DATA = ASSETS / "datasets/NL2SH-ALFA"
RUN_DIR = ev.REPO / "results/mike/nl2sh-baseline" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
THREADS = os.environ.get("MIKE_NL2SH_THREADS", "4")
SYSTEM = ("You translate a request into one Linux bash command. "
          "Answer with the command only, on one line, without explanation or code fence.")
MODELS = ["LFM2.5-350M-Q4_0.gguf"]


def command_of(content: str) -> str:
    """The first non-empty line that is not a code fence, without a leading `$ `."""
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("```"):
            continue
        return line[2:].strip() if line.startswith("$ ") else line.strip("`").strip()
    return ""


def edit_distance(a: str, b: str) -> int:
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def judge(got: str, golds: list[str]) -> dict:
    squeeze = " ".join
    return {"exact": any(got == g for g in golds),
            "exact_spaces": any(squeeze(got.split()) == squeeze(g.split()) for g in golds),
            "utility": any(got.split()[:1] == g.split()[:1] for g in golds),
            "cer": round(min(edit_distance(got, g) / max(1, len(g)) for g in golds), 3)}


def test_command_of_strips_fences_and_prompt():
    assert command_of("```bash\nls -la\n```") == "ls -la"
    assert command_of("$ df -h\n") == "df -h"
    assert command_of("`pwd`") == "pwd"


def test_judge_accepts_either_command():
    assert judge("ls  -l", ["ls", "ls -l"]) == {"exact": False, "exact_spaces": True, "utility": True, "cer": 0.2}


@pytest.mark.integration
@pytest.mark.timeout(4 * 3600)
@pytest.mark.parametrize("model", MODELS)
def test_nl2sh_baseline(model):
    if not (ASSETS / model).is_file() or not (DATA / "test.csv").is_file():
        pytest.skip("model or NL2SH-ALFA missing")
    with (DATA / "test.csv").open(newline="") as f:
        cases = list(csv.DictReader(f))
    out = RUN_DIR / model
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    started = time.perf_counter()
    with ms.Server(str(ASSETS / model), ["-t", THREADS], out / "llama-server.log") as server, \
            (out / "rows.jsonl").open("w") as f:
        for case in cases:
            golds = [case["bash"].strip(), case["bash2"].strip()]
            reply = server.post("/v1/chat/completions", {
                "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": case["nl"].strip()}],
                "temperature": 0.0, "top_k": 1, "max_tokens": 96, "seed": 0}, timeout=600)
            content = reply["choices"][0]["message"]["content"]
            got = command_of(content)
            row = {"nl": case["nl"].strip(), "golds": golds, "difficulty": int(case["difficulty"]),
                   "raw": content, "got": got, **judge(got, golds),
                   "prompt_tokens": reply["usage"]["prompt_tokens"]}
            rows.append(row)
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    n = len(rows)
    result = {"model": model, "n": n, "seconds": round(time.perf_counter() - started), "threads": THREADS,
              "system": SYSTEM, **{k: sum(r[k] for r in rows) for k in ("exact", "exact_spaces", "utility")},
              "cer_mean": round(sum(r["cer"] for r in rows) / n, 3),
              "by_difficulty": {d: {"n": sum(r["difficulty"] == d for r in rows),
                                    "exact_spaces": sum(r["exact_spaces"] for r in rows if r["difficulty"] == d)}
                                for d in sorted({r["difficulty"] for r in rows})}}
    (out / "result.json").write_text(json.dumps(result, indent=1))
    print(json.dumps(result))
    assert n == 300
