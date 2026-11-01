"""Mike Step 14.1-14.3: the "flashlight embedding" study on Termidor (`flashlight.feature`).

    uv run --group embed pytest test/mike/test_flashlight.py                     # deterministic
    uv run --group embed pytest test/mike/test_flashlight.py -m integration -s   # all candidates

Each candidate is measured in its own process by `flashlight_bench.py`; the results go to
results/mike/flashlight/<timestamp>/ (one JSON line per candidate). Nothing is graded here.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
import flashlight_bench as bench  # noqa: E402
import flashlight_blocks as fb  # noqa: E402

CANDIDATES = ["bm25", "tfidf", "minishlab/potion-base-2M", "minishlab/potion-base-4M", "minishlab/potion-base-8M",
              "minishlab/potion-retrieval-32M"]
RUN_DIR = HERE.parents[1] / "results/mike/flashlight" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def test_guide_blocks_are_short_and_cited():
    blocks = fb.blocks()
    assert len(blocks) > 40 and all(15 <= len(b["text"].split()) <= fb.MAX_WORDS + 60 for b in blocks)
    assert len({b["id"] for b in blocks}) == len(blocks)


def test_every_expected_block_exists():
    ids = {b["id"] for b in fb.blocks()}
    assert all(x in ids for _, want in bench.DATA["retrieval"]["questions"] for x in want)


def test_lexical_scores_and_threshold():
    for kind in ("bm25", "tfidf"):
        lex = bench.Lexical(kind)
        lex.fit(["the cat sat on the mat", "a dog in the fog", "memory of the desktop"])
        assert int(lex.scores("how much desktop memory").argmax()) == 2
    assert bench.auc([3, 4], [1, 2]) == 1.0 and bench.best_threshold([3, 4], [1, 2])["accuracy"] == 1.0


@pytest.mark.integration
@pytest.mark.timeout(1800)
def test_flashlight_candidates_on_the_desk():
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for name in CANDIDATES:
        done = subprocess.run([sys.executable, str(HERE / "flashlight_bench.py"), name], capture_output=True,
                              text=True, timeout=600, env={**__import__("os").environ, "HF_HUB_DISABLE_PROGRESS_BARS": "1"})
        (RUN_DIR / f"{name.replace('/', '_')}.log").write_text(done.stderr)
        assert done.returncode == 0, done.stderr[-2000:]
        rows.append(json.loads(done.stdout.splitlines()[-1]))
    (RUN_DIR / "candidates.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    print(RUN_DIR)
    assert len(rows) == len(CANDIDATES)
