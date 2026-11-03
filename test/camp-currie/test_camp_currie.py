"""Camp Currie Steps 2-3: the shell and the simulated first mission.

Contract: camp_currie_shell.feature. The core tests run in the default suite.
The rendered run (pygame, SDL dummy video driver) plays the whole game through
the agent protocol, as an agent would, and saves every screen:
    uv run --group camp-currie pytest -m integration test/camp-currie
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

GAME = Path(__file__).resolve().parents[2] / "src" / "camp-currie"
sys.path.insert(0, str(GAME))
from camp_currie.core import REASONS, ScriptedEvaluator, State, semantic, step  # noqa: E402


def play(actions: str, script=("success",)) -> State:
    evaluator, state = ScriptedEvaluator(script), State()
    for action in actions.split():
        state = step(state, action, evaluator)
    return state


def test_from_the_title_to_mannies_call():
    view = semantic(play("confirm confirm confirm"))
    assert view["scene"] == "contact" and view["speaker"] == "Mannie" and view["target"] == "Mannie"


def test_locked_missions_explain_themselves():
    state = play("confirm down confirm")
    assert state.scene == "missions" and "speech" in state.notice


def test_back_always_goes_up_one_level():
    assert play("confirm confirm back").scene == "missions"
    assert play("confirm back").scene == "title"
    assert play("confirm confirm confirm confirm back").scene == "contact"  # your turn -> the prompt


def test_listen_again_shows_the_prompt_without_transmitting():
    state = play("confirm confirm confirm confirm down confirm")
    assert state.scene == "contact" and state.attempts == 0


@pytest.mark.parametrize("kind, scene_after", [("success", "contact"), ("retry", "turn"), ("uncertain", "turn")])
def test_each_simulated_outcome(kind, scene_after):
    state = play("confirm confirm confirm confirm confirm", script=(kind,))
    assert state.scene == "result" and state.last.kind == kind and state.last.reason == REASONS[kind]
    assert "Simulated" in state.last.reason
    assert state.cleared[0] == (kind == "success")
    assert play("confirm confirm confirm confirm confirm confirm", script=(kind,)).scene == scene_after


def test_the_whole_mission_with_the_default_script():
    state, evaluator = State(), ScriptedEvaluator()
    for action in ["confirm"] * 3:
        state = step(state, action, evaluator)
    while state.scene != "debrief":
        state = step(state, "confirm", evaluator)
    assert all(state.cleared) and (state.attempts, state.retries, state.uncertain) == (7, 1, 1)
    assert state.rank() == "A"
    assert step(state, "confirm", evaluator).scene == "missions"


def test_uncertain_never_counts_as_a_retry():
    state = play("confirm confirm confirm confirm confirm", script=("uncertain",))
    assert state.retries == 0 and state.uncertain == 1


@pytest.mark.integration
def test_the_rendered_game_played_through_the_agent_protocol():
    out = Path("results/camp-currie/shell") / datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out.mkdir(parents=True, exist_ok=False)
    script, shots = [], []

    def shot(name):
        shots.append(name)
        script.append(f"shot {out.resolve() / (name + '.png')}")

    shot("01-title")
    script.append("confirm"); shot("02-missions")
    script += ["down", "confirm"]; shot("03-missions-locked")
    script += ["up", "confirm"]; shot("04-briefing")
    script.append("confirm"); shot("05-contact-mannie")
    script.append("confirm"); shot("06-your-turn")
    script.append("confirm"); shot("07-result-success")
    script.append("confirm")                       # Wyoh
    script += ["confirm", "confirm"]; shot("08-result-retry")
    script += ["confirm", "confirm"]               # try again: success
    script += ["confirm", "confirm", "confirm"]; shot("09-result-uncertain")   # Mycroft
    script += ["confirm", "confirm"]               # success
    for _ in range(2):                             # Mike, Luna
        script += ["confirm", "confirm", "confirm"]
    script.append("confirm"); shot("11-debrief")
    script.append("quit")
    env = {**os.environ, "SDL_VIDEODRIVER": "dummy", "SDL_AUDIODRIVER": "dummy"}
    run = subprocess.run([sys.executable, "-m", "camp_currie", "--agent"], cwd=GAME, env=env, input="\n".join(script) + "\n",
                         capture_output=True, text=True, timeout=120, check=False)
    (out / "run.log").write_text(run.stdout + run.stderr, encoding="utf-8")
    assert run.returncode == 0, run.stderr
    states = [json.loads(line) for line in run.stdout.splitlines() if line.startswith("{") and '"scene"' in line]
    assert states[-1]["scene"] == "debrief" and states[-1]["rank"] == "A" and states[-1]["progress"] == [1] * 5
    assert {s["last"]["kind"] for s in states if s["last"]} == {"success", "retry", "uncertain"}
    for name in shots:
        assert (out / f"{name}.png").stat().st_size > 10_000, name
    peak = max(s["rss_kib"] for s in states)
    (out / "memory.json").write_text(json.dumps({"platform": os.uname().machine, "peak_rss_kib": peak}), encoding="utf-8")
    assert peak < 50 * 1024  # Adam: "50 MiB is not a problem"
