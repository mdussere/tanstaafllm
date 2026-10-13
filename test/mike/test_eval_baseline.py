"""Mike Step 2: the evaluation set is valid, and the keyword baseline's score is recorded.

The score is evidence, not a threshold: the models of Step 3.2c must beat it.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone

import mike_eval as ev
from mike_eval import contract


import pytest

SETS = {"main": ev.EVAL_SET, "holdout": ev.HOLDOUT_SET}


@pytest.mark.parametrize("name", SETS)
def test_every_case_follows_the_contract(name):
    cases = ev.load_cases(SETS[name])
    assert (60 <= len(cases) <= 100) if name == "main" else (20 <= len(cases) <= 40)
    for case in cases:
        e = case.expected
        assert e.tool in contract.TOOL_NAMES, case
        if "app" in e.args:
            assert e.args["app"] in contract.APP_IDS, case
        if e.tool in contract.NEEDS_OPEN:
            assert e.args["app"] in case.desktop.open, case
        if e.tool == "launch_app":
            assert e.args["app"] not in case.desktop.open, case
        if e.tool == "move_window":
            assert e.args["place"] in contract.PLACES, case
        assert case.request == case.request.lower().rstrip(".?!"), "Mycroft-style text"
    requests = [case.request for case in cases]
    assert len(requests) == len(set(requests))


def test_every_tool_has_cases():
    tools = {case.expected.tool for case in ev.load_cases()}
    assert tools == set(contract.TOOL_NAMES)


def test_scoring_counts_a_text_answer_as_none_and_applies_the_rewrite():
    [launch] = [c for c in ev.load_cases() if c.request == "ouvre la calculatrice"]
    focus = contract.Call("focus_window", {"app": "calculator"})
    assert ev.score(launch, focus) == {"model": False, "adapter": True, "proposal": "refuse", "rewritten": True}
    [refuse] = [c for c in ev.load_cases() if c.request == "appelle maman"]
    assert ev.score(refuse, None)["model"]


def test_held_out_requests_are_new():
    main = {case.request for case in ev.load_cases()}
    assert not main & {case.request for case in ev.load_cases(ev.HOLDOUT_SET)}


@pytest.mark.parametrize("name", SETS)
def test_keyword_baseline_score_is_recorded(name):
    """The baseline was written while reading the main set: its main score is optimistic."""
    report = ev.evaluate(ev.keyword_baseline, ev.load_cases(SETS[name]))
    out = ev.REPO / "results/mike/eval-baseline" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out.mkdir(parents=True, exist_ok=True)
    (out / f"keyword-baseline.{name}.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    summary = report["summary"]
    print(name, json.dumps({k: summary[k] for k in ("n", "model", "adapter")}))
    assert summary["n"] == len(ev.load_cases(SETS[name]))
    assert 0 < summary["model"] <= summary["n"]


def test_prompt_v3_examples_are_in_neither_set():
    pytest.importorskip("jinja2")
    import re
    import mike_eval_model as em
    examples = set(re.findall(r"\] (.+?) -> ", em.SYSTEM_PROMPT_V3))
    assert len(examples) == 6
    for path in SETS.values():
        assert not examples & {case.request for case in ev.load_cases(path)}
