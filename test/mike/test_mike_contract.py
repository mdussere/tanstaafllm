"""Deterministic checks of Mike's tool contract and adapter against a fake Wyoh (Step 2.2)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src" / "mike"))
import mike_contract as c  # noqa: E402

from fake_wyoh import FakeWyoh  # noqa: E402

DESK = c.Desktop(("terminal", "calculator"), "calculator")


def test_tools_expose_no_raw_sway_or_exec():
    assert c.TOOL_NAMES == ["list_windows", "focus_window", "launch_app", "close_window",
                            "move_window", "type_text", "none"]
    assert not any("sway" in n or "exec" in n for n in c.TOOL_NAMES)


def test_hidden_menu_entries_are_not_on_the_allowlist():
    hidden = {"htop", "nvtop", "cups", "mpv", "gmu", "mupen64plus"}
    assert not hidden & set(c.APP_IDS)


@pytest.mark.parametrize(
    ("call", "kind", "requests"),
    [
        (c.Call("list_windows"), "run", [("sway_get_tree", {})]),
        (c.Call("focus_window", {"app": "terminal"}), "ask",
         [("sway_command", {"command": '[app_id="foot"] focus'})]),
        (c.Call("close_window", {"app": "calculator"}), "ask",
         [("sway_command", {"command": '[app_id="wyoh-calculator"] kill'})]),
        (c.Call("move_window", {"app": "terminal", "place": "full"}), "ask",
         [("sway_command", {"command": '[app_id="foot"] fullscreen toggle'})]),
        (c.Call("move_window", {"app": "terminal", "place": "top"}), "ask",
         [("sway_command", {"command": '[app_id="foot"] focus'}), ("sway_command", {"command": "move up"})]),
        (c.Call("launch_app", {"app": "editor"}), "ask",
         [("sway_command", {"command": "exec foot -a wyoh-editor vim"})]),
        (c.Call("type_text", {"text": "ls -la"}), "ask", [("wyoh_dev_keyboard_type", {"text": "ls -la"})]),
        (c.Call("none", {"reason": "weather"}), "nothing", []),
    ],
)
def test_each_tool_maps_to_fixed_wyoh_requests(call, kind, requests):
    proposal = c.propose(call, DESK)
    assert proposal.kind == kind
    assert list(proposal.requests) == requests


@pytest.mark.parametrize(
    ("call", "why"),
    [
        (c.Call("launch_app", {"app": "spotify"}), "not on the allowlist"),
        (c.Call("launch_app", {"app": "browser"}), "not installed"),
        (c.Call("launch_app", {"app": "calculator"}), "launch command is not known"),
        (c.Call("close_window", {"app": "editor"}), "not open"),
        (c.Call("move_window", {"app": "terminal", "place": "middle"}), "place must be"),
        (c.Call("type_text", {"text": "a\nb"}), "one line"),
        (c.Call("type_text", {"text": "x" * 201}), "one line"),
        (c.Call("sway_command", {"command": "exec rm -rf ~"}), "unknown tool"),
        (c.Call("launch_app", {"app": "terminal", "command": "rm"}), "takes"),
    ],
)
def test_the_adapter_refuses_rather_than_guesses(call, why):
    proposal = c.propose(call, DESK)
    assert proposal.kind == "refuse"
    assert why in proposal.message
    assert proposal.requests == ()


def test_focus_on_a_closed_app_is_proposed_as_a_launch():
    proposal = c.propose(c.Call("focus_window", {"app": "editor"}), DESK)
    assert proposal.call == c.Call("launch_app", {"app": "editor"})
    assert proposal.rewritten_from == c.Call("focus_window", {"app": "editor"})
    assert proposal.kind == "ask" and proposal.message.startswith("editor is not open")


def test_close_asks_twice():
    assert c.propose(c.Call("close_window", {"app": "terminal"}), DESK).confirm_twice


def test_nothing_runs_before_acceptance():
    wyoh = FakeWyoh(DESK)
    proposal = c.propose(c.Call("close_window", {"app": "terminal"}), DESK)
    assert c.run(proposal, wyoh, accepted=False) == []
    assert wyoh.requests == [] and "terminal" in wyoh.open
    c.run(proposal, wyoh, accepted=True)
    assert wyoh.open == ["calculator"]


def test_list_windows_runs_without_asking_and_reads_the_tree():
    wyoh = FakeWyoh(DESK)
    [tree] = c.run(c.propose(c.Call("list_windows"), DESK), wyoh, accepted=False)
    assert c.windows_from_tree(tree) == c.Desktop(("terminal", "calculator"), "calculator")


def test_accepted_actions_change_the_fake_desktop():
    wyoh = FakeWyoh(DESK)
    for call in (c.Call("launch_app", {"app": "editor"}),
                 c.Call("focus_window", {"app": "terminal"}),
                 c.Call("type_text", {"text": "git status"}),
                 c.Call("move_window", {"app": "terminal", "place": "full"})):
        state = c.windows_from_tree(wyoh.tree())
        c.run(c.propose(call, state), wyoh, accepted=True)
    assert wyoh.open == ["terminal", "calculator", "editor"]
    assert wyoh.focus == "terminal" and wyoh.typed == ["git status"] and wyoh.fullscreen == {"terminal"}
    assert all(name in {"sway_command", "wyoh_dev_keyboard_type", "sway_get_tree"} for name, _ in wyoh.requests)


def test_desktop_line():
    assert c.desktop_line(DESK) == "[open: terminal, calculator; focus: calculator]"
    assert c.desktop_line(c.Desktop((), None)) == "[open: none; focus: none]"
