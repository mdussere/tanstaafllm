"""Mike Step 3.2c: each shortlisted model on the Step 2 evaluation sets (`model_eval.feature`).

    MIKE_ASSET_ROOT=/data/michael/tanstaafllm/mike-assets \
        uv run --group mike pytest test/mike/test_model_eval.py -m integration
"""

from __future__ import annotations

import json
import multiprocessing
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

import mike_eval as ev

MODELS = [m for m in os.environ.get("MIKE_MODELS", "LFM2.5-350M-Q4_K_M.gguf,LFM2.5-230M-Q4_K_M.gguf").split(",")]
SETS = {"main": ev.EVAL_SET, "holdout": ev.HOLDOUT_SET}
PROMPT = os.environ.get("MIKE_PROMPT", "v3")
LEAN = os.environ.get("MIKE_LEAN", "0") == "1"
RUN_DIR = ev.REPO / "results/mike/model-eval" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _child(model_path: str, queue) -> None:
    try:
        import mike_eval_model as em
        queue.put(em.run_model_eval(model_path, SETS, prompt=PROMPT, lean=LEAN))
    except BaseException as error:  # report, never hang the parent
        queue.put({"error": repr(error)})


@pytest.mark.integration
@pytest.mark.timeout(1800)
@pytest.mark.parametrize("model", MODELS)
def test_model_eval(model):
    pytest.importorskip("llama_cpp")
    root = os.environ.get("MIKE_ASSET_ROOT")
    if not root or not (Path(root) / model).is_file():
        pytest.skip(f"{model} not found under MIKE_ASSET_ROOT")
    context = multiprocessing.get_context("spawn")
    queue = context.Queue()
    process = context.Process(target=_child, args=(str(Path(root) / model), queue))
    process.start()
    report = queue.get(timeout=1750)
    process.join(30)
    assert "error" not in report, report.get("error")

    import mike_eval_model as em
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / f"{model}.{PROMPT}{'.lean' if LEAN else ''}.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    with (RUN_DIR / "summary.md").open("a") as out:
        out.write(f"## {model}, prompt {PROMPT}, lean {LEAN}\n\n```json\n{json.dumps(em.summarise(report), indent=1)}\n```\n\n")
    for name in SETS:
        for mode in ("free", "constrained"):
            assert report["sets"][name][mode]["summary"]["n"] == len(ev.load_cases(SETS[name]))
