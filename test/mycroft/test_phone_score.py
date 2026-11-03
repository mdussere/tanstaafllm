"""Deterministic checks of the phone normaliser and aligner (plan step 11.5)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO = Path(__file__).parents[2]
SPEC = importlib.util.spec_from_file_location("phone_score", REPO / "worklines/mycroft/scripts/phone_score.py")
assert SPEC and SPEC.loader
score = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = score
SPEC.loader.exec_module(score)


def test_notation_differences_are_not_errors() -> None:
    assert score.phones("ʃˈɪp ˈæftɚ") == ["ʃ", "ɪ", "p", "æ", "f", "t", "ə˞"]
    assert score.phones("æftə˞") == score.phones("ˈæftɚ")
    assert score.phones("kwˈɔːɹɾɚ") == score.phones("kwɔɹtə˞")


def test_ship_heard_as_sheep_is_one_substitution() -> None:
    rate, confusions = score.align(score.phones("ʃɪp"), score.phones("ʃiːp"))
    assert rate == 1 / 3
    assert confusions == {"ɪ→i": 1}


def test_deletion_and_insertion_are_named() -> None:
    rate, confusions = score.align(["h", "ɪ", "l"], ["ɪ", "l", "ə"])
    assert rate == 2 / 3
    assert confusions == {"h→∅": 1, "∅→ə": 1}
