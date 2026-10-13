"""Deterministic tests for the Wyoh calculator core (Step 9.5)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "src" / "wyoh" / "apps" / "calculator"))
import calc_core as c  # noqa: E402


def run(keys: str) -> str:
    calc = c.Calculator()
    display = calc.display
    for key in keys.split():
        display = calc.press(key)
    return display


@pytest.mark.parametrize("keys, shown", [
    ("1 2 + 3 =", "15"),
    ("7 − 1 0 =", "-3"),
    ("6 × 7 =", "42"),
    ("1 ÷ 3 =", "0.333333333333"),
    ("2 ÷ 3 =", "0.666666666667"),
    ("0 . 1 + 0 . 2 =", "0.3"),
    ("2 + 3 × 4 =", "20"),          # left to right, as the original (no precedence)
    ("5 + =", "10"),                # "=" with no second operand reuses the display
    ("2 + 3 = =", "8"),             # "=" again repeats the last operation
    ("2 × 3 = = =", "54"),
    ("9 + 1 C", "0"),
    ("1 2 3 ⌫", "12"),
    ("1 ⌫ ⌫", "0"),
    (". 5 + . 5 =", "1"),
    ("1 . 2 . 3", "1.23"),           # a second point is ignored
    ("3 + − 1 =", "2"),             # the last operator wins
])
def test_keys(keys, shown):
    assert run(keys) == shown


def test_division_by_zero_shows_error_and_any_key_starts_over():
    calc = c.Calculator()
    for key in "8 ÷ 0 =".split():
        calc.press(key)
    assert calc.display == "Error"
    assert calc.press("⌫") == "Error"  # backspace does not clear an error
    assert calc.press("7") == "7"


def test_input_is_limited_to_twelve_digits():
    assert run(" ".join("1234567890123")) == "123456789012"


def test_overflow_shows_error():
    assert run("9 9 9 9 9 9 9 9 9 9 9 9 × 9 9 =") == "Error"


def test_backspace_does_not_touch_a_result():
    assert run("2 + 2 = ⌫") == "4"


def test_unknown_key_is_refused():
    with pytest.raises(ValueError):
        c.Calculator().press("%")


# --- keypad selection ----------------------------------------------------------

def test_keypad_has_the_eighteen_keys():
    keys = {key for row in c.KEYPAD for key in row}
    assert keys == set("0123456789") | {".", "+", "−", "×", "÷", "=", "C", "⌫"}
    assert len(keys) == 18


@pytest.mark.parametrize("start, direction, end", [
    ((1, 0), "up", (0, 0)),          # 7 -> C
    ((0, 0), "up", (0, 0)),          # stops at the edge
    ((3, 2), "right", (3, 3)),       # 3 -> =
    ((3, 3), "down", (3, 3)),        # = is tall: down stays on it (edge)
    ((4, 2), "right", (3, 3)),       # . -> = (anchored at its top)
    ((4, 0), "right", (4, 2)),       # 0 is wide: right goes to .
    ((4, 2), "left", (4, 0)),        # . -> 0
    ((3, 1), "down", (4, 0)),        # 2 -> 0 (anchored at its left)
    ((2, 3), "down", (3, 3)),        # + -> =
])
def test_selection_moves(start, direction, end):
    assert c.move(start, direction) == end


def test_key_at():
    assert c.key_at((4, 1)) == "0" and c.key_at((0, 1)) == "⌫"
