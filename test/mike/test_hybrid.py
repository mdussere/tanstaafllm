"""Mike option A (`docs/0302_03`): keyword table first, model second.

The deterministic test checks the routing; the integration test re-scores a
saved model run without loading the model:

    MIKE_EVAL_RUN=results/mike/model-eval/<timestamp>/<model>.<prompt>.json \
        uv run pytest test/mike/test_hybrid.py -m integration -s
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

import mike_eval as ev
from mike_eval import contract

SETS = {"main": ev.EVAL_SET, "holdout": ev.HOLDOUT_SET}


def _case(request: str, open_=("terminal",), focus="terminal") -> ev.EvalCase:
    return ev.EvalCase(request, contract.Desktop(open_, focus), contract.Call("none"), "t")


def test_a_sure_rule_wins_over_the_model():
    model = contract.Call("focus_window", {"app": "terminal"})
    assert ev.hybrid(_case("ferme le terminal"), model, "model-on-any-miss") == \
        contract.Call("close_window", {"app": "terminal"})


def test_the_model_answers_only_where_the_table_is_unsure():
    model = contract.Call("move_window", {"app": "terminal", "place": "left"})
    unsure_verb = _case("colle le terminal sur la gauche")
    no_app = _case("réserve un train pour lyon")
    assert ev.hybrid(unsure_verb, model, "model-on-app-only") == model
    assert ev.hybrid(no_app, model, "model-on-app-only").tool == "none"
    assert ev.hybrid(no_app, model, "model-on-any-miss") == model


@pytest.mark.integration
@pytest.mark.parametrize("variant", ["model-on-any-miss", "model-on-app-only"])
def test_hybrid_on_a_saved_run(variant):
    run = os.environ.get("MIKE_EVAL_RUN")
    if not run or not Path(run).is_file():
        pytest.skip("MIKE_EVAL_RUN not set to a saved test_model_eval.py report")
    report = json.loads(Path(run).read_text())
    scores = ev.hybrid_from_run(report, SETS, variant)
    out = Path(run).parent / f"hybrid.{variant}.json"
    out.write_text(json.dumps({"source": Path(run).name, "variant": variant, "at":
                               datetime.now(timezone.utc).isoformat(), "scores": scores}, indent=1))
    print(variant, {k: (v["model"], v["n"]) for k, v in scores.items()})
    assert all(v["n"] for v in scores.values())
