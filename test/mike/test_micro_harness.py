"""Mike Step 3b.2: ready-made micro-harnesses on LFM2.5-350M (`micro_harness.feature`).

    MIKE_ASSET_ROOT=/data/michael/tanstaafllm/mike-assets \
        uv run pytest test/mike/test_micro_harness.py -m integration -s

The harness binaries and llama.cpp live under MIKE_TOOLS_ROOT
(default /data/michael/tanstaafllm/mike-tools); `MIKE_HARNESSES` narrows the run.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

import mike_eval as ev
import mike_harness as mh
import mike_server as ms

MODEL = "LFM2.5-350M-Q4_K_M.gguf"
NAMES = os.environ.get("MIKE_HARNESSES", ",".join(mh.HARNESSES)).split(",")
RUN_DIR = ev.REPO / "results/mike/micro-harness" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


@pytest.fixture(scope="module")
def model_server():
    root = os.environ.get("MIKE_ASSET_ROOT")
    if not root or not (Path(root) / MODEL).is_file():
        pytest.skip(f"{MODEL} not found under MIKE_ASSET_ROOT")
    if not ms.SERVER.is_file():
        pytest.skip(f"llama-server not found at {ms.SERVER}")
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    with ms.Server(str(Path(root) / MODEL), ["--jinja", "-c", "8192", "--alias", "lfm2.5-350m"],
                   RUN_DIR / "llama-server.log") as server:
        yield server


@pytest.mark.integration
@pytest.mark.timeout(3600)
@pytest.mark.parametrize("name", NAMES)
def test_micro_harness(model_server, name):
    binary, _ = mh.HARNESSES[name]
    if not binary.is_file():
        pytest.skip(f"{name} not found at {binary}")
    report = mh.run_harness(name, model_server.url, RUN_DIR / name)
    (RUN_DIR / f"{name}.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    summary = mh.summarise(report)
    with (RUN_DIR / "summary.jsonl").open("a") as out:
        out.write(json.dumps(summary, ensure_ascii=False) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    assert len(report["scenarios"]) == len(mh.SCENARIOS)
    assert all(s["llm_requests"] >= 1 for s in report["scenarios"]), "a harness never reached the model"
