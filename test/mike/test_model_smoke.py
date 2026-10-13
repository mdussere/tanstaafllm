"""Mike Step 3 smoke test of each shortlisted model (`model_smoke.feature`).

Each model runs alone in a spawned child process so its peak RSS (`VmHWM`) is
its own. The test records evidence; accuracy is reported, not asserted.

    MIKE_ASSET_ROOT=/data/michael/tanstaafllm/mike-assets \
        uv run --group mike pytest test/mike/test_model_smoke.py -m integration
"""

from __future__ import annotations

import json
import multiprocessing
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

import mike_bench as bench


REPO = Path(__file__).parents[2]
MODELS = [
    "LFM2.5-350M-Q4_K_M.gguf",
    "LFM2.5-230M-Q4_K_M.gguf",
    "functiongemma-270m-it-Q4_K_M.gguf",
]
# Compute buffers and llama-cpp-python's logits array grow with n_batch
# (512 tokens × the vocabulary); a small batch trades prompt speed for RAM.
N_BATCH = int(os.environ.get("MIKE_N_BATCH", "512"))
PROMPT = os.environ.get("MIKE_PROMPT", "v1")
PREFIX_CACHE = os.environ.get("MIKE_PREFIX_CACHE", "0") == "1"
RUN_DIR = REPO / "results/mike/model-comparison" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _child(model_path: str, n_batch: int, prompt: str, prefix_cache: bool, queue) -> None:
    try:
        queue.put(bench.run_model(model_path, n_batch=n_batch, prompt=prompt, prefix_cache=prefix_cache))
    except BaseException as error:  # report, never hang the parent
        queue.put({"error": repr(error)})


@pytest.mark.integration
@pytest.mark.timeout(1200)
@pytest.mark.parametrize("model", MODELS)
def test_model_smoke(model):
    pytest.importorskip("llama_cpp")
    root = os.environ.get("MIKE_ASSET_ROOT")
    if not root or not (Path(root) / model).is_file():
        pytest.skip(f"{model} not found under MIKE_ASSET_ROOT")

    context = multiprocessing.get_context("spawn")
    queue = context.Queue()
    process = context.Process(target=_child, args=(str(Path(root) / model), N_BATCH, PROMPT, PREFIX_CACHE, queue))
    process.start()
    report = queue.get(timeout=1150)
    process.join(30)
    assert "error" not in report, report.get("error")

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / f"{model}.b{N_BATCH}.{PROMPT}{'.pc' if PREFIX_CACHE else ''}.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    summary = bench.summarise(report)
    with (RUN_DIR / "summary.md").open("a") as out:
        out.write(f"## {model}, n_batch={N_BATCH}, prompt={PROMPT}, prefix_cache={PREFIX_CACHE}\n\n```json\n{json.dumps(summary, indent=2)}\n```\n\n")

    assert report["vm_hwm_kib_peak"] > 0
    assert len(report["results"]) == 2 * len(bench.CASES)
    constrained = [r for r in report["results"] if r["mode"] == "constrained"]
    assert all(r["got"] is not None for r in constrained), [r["raw"] for r in constrained if r["got"] is None]
