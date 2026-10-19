"""Mike Step 3b.1: LFM2.5-350M through llama.cpp's C++ server (`server_runtime.feature`).

    MIKE_ASSET_ROOT=/data/michael/tanstaafllm/mike-assets \
        uv run pytest test/mike/test_server_runtime.py -m integration -s

`MIKE_TOOLS_ROOT` holds the unpacked llama.cpp release (default
/data/michael/tanstaafllm/mike-tools); `MIKE_MODELS` and `MIKE_CONFIGS`
narrow the run.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

import mike_eval as ev
import mike_server as ms

MODELS = os.environ.get("MIKE_MODELS", "LFM2.5-350M-Q4_K_M.gguf").split(",")
CONFIG_NAMES = os.environ.get("MIKE_CONFIGS", ",".join(ms.CONFIGS)).split(",")
SETS = {"main": ev.EVAL_SET, "holdout": ev.HOLDOUT_SET}
RUN_DIR = ev.REPO / "results/mike/server-runtime" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


@pytest.mark.integration
@pytest.mark.timeout(1800)
@pytest.mark.parametrize("config", CONFIG_NAMES)
@pytest.mark.parametrize("model", MODELS)
def test_server_runtime(model, config):
    root = os.environ.get("MIKE_ASSET_ROOT")
    if not root or not (Path(root) / model).is_file():
        pytest.skip(f"{model} not found under MIKE_ASSET_ROOT")
    if not ms.SERVER.is_file():
        pytest.skip(f"llama-server not found at {ms.SERVER}")
    report = ms.run_server_eval(str(Path(root) / model), config, SETS, RUN_DIR)
    (RUN_DIR / f"{model}.{config}.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    summary = ms.summarise(report)
    with (RUN_DIR / "summary.jsonl").open("a") as out:
        out.write(json.dumps(summary, ensure_ascii=False) + "\n")
    print(json.dumps(summary, ensure_ascii=False))
    for name, path in SETS.items():
        assert report["sets"][name]["summary"]["n"] == len(ev.load_cases(path))
