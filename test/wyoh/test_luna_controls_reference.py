"""Step 5.12: the controls reference must say what the code does.

worklines/wyoh/docs/0512_01_luna-controls-reference.md is checked against
`wyoh_gamepad.Config` as deployed (`deploy/luna/gamepad.toml`). Each check
reads one table row by its evdev code and requires the key, Sway command or
Slate operation the configuration defines.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "src" / "wyoh"))
import wyoh_gamepad as g  # noqa: E402

DOC = ROOT / "worklines/wyoh/docs/0512_01_luna-controls-reference.md"
CONFIG = g.load_config(ROOT / "src/wyoh/deploy/luna/gamepad.toml")


def _section(title: str) -> list[list[str]]:
    """The table rows (cells) of the section headed `## <title>`."""
    text = DOC.read_text(encoding="utf-8")
    match = re.search(rf"^## {re.escape(title)}\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    assert match, f"section missing: {title}"
    rows = []
    for line in match.group(1).splitlines():
        if line.startswith("|") and not set(line) <= set("|- "):
            rows.append([cell.strip() for cell in line.strip("|").split("|")])
    return rows[1:]  # without the header


def _row(title: str, evdev: str) -> str:
    """The text of the row whose evdev cell is exactly `evdev`."""
    for cells in _section(title):
        if len(cells) > 1 and cells[1] == evdev:
            return " | ".join(cells)
    raise AssertionError(f"{title}: no row for {evdev}")


def _code(text: str) -> str:
    return f"`{text}`"


@pytest.mark.parametrize("button", ["BTN_EAST", "BTN_SOUTH", "BTN_NORTH", "BTN_WEST", "BTN_TR", "BTN_TR2"])
def test_desktop_keys(button):
    assert _code(CONFIG.keys[button]) in _row("Desktop (no Slate shown)", _code(button))


def test_desktop_cross_is_arrows():
    row = _row("Desktop (no Slate shown)", "`BTN_DPAD_*`")
    for direction in ("UP", "DOWN", "LEFT", "RIGHT"):
        assert CONFIG.keys[f"BTN_DPAD_{direction}"] in row


def test_desktop_special_buttons():
    assert CONFIG.zone_toggle == "BTN_TL" and "Slate" in _row("Desktop (no Slate shown)", "`BTN_TL`")
    assert CONFIG.menu == "BTN_START" and "menu" in _row("Desktop (no Slate shown)", "`BTN_START`")
    assert CONFIG.next_window == "BTN_SELECT"
    assert "`focus next`" in _row("Desktop (no Slate shown)", "`BTN_SELECT`")
    assert CONFIG.click == "BTN_THUMBR" and "click" in _row("Desktop (no Slate shown)", "`BTN_THUMBR`")
    assert CONFIG.pointer_stick == "right" and "Pointer" in _row("Desktop (no Slate shown)", "`ABS_RX`/`ABS_RY`")
    assert "`dictate`" in _row("Desktop (no Slate shown)", "`BTN_TL2`")


@pytest.mark.parametrize("button", ["BTN_EAST", "BTN_SOUTH", "BTN_TR", "BTN_TR2"])
def test_fn_sway_commands(button):
    assert _code(CONFIG.fn_sway[button]) in _row("With FN held (desktop)", f"`BTN_MODE` + `{button}`")


def test_fn_cross_and_recovery():
    row = _row("With FN held (desktop)", "`BTN_MODE` + `BTN_DPAD_*`")
    for direction in ("UP", "DOWN", "LEFT", "RIGHT"):
        assert CONFIG.fn_sway[f"BTN_DPAD_{direction}"] in row
    assert CONFIG.recovery == ("BTN_MODE", "BTN_START") and CONFIG.recovery_hold_s == 2.0
    assert "held 2 s" in _row("With FN held (desktop)", "`BTN_MODE` + `BTN_START`")


@pytest.mark.parametrize("button", ["BTN_EAST", "BTN_SOUTH", "BTN_NORTH", "BTN_WEST", "BTN_TR", "BTN_TR2"])
def test_slate_keys(button):
    assert _code(CONFIG.zone_keys[button]) in _row("Slate shown", _code(button))


def test_slate_toggle_dictation_and_fn():
    assert "`hide`" in _row("Slate shown", _code(CONFIG.zone_toggle))
    assert "`dictate`" in _row("Slate shown", _code(CONFIG.zone_dictate))
    for button, op in CONFIG.zone_fn.items():
        assert f"`{op}`" in _row("Slate shown", f"`BTN_MODE` + `{button}`")


def test_slate_whole_cross_timings():
    assert CONFIG.cross_window_s == 0.04 and "40 ms" in _row("Slate shown", "`BTN_DPAD_*`")
    assert CONFIG.cross_double_s == 0.4
    assert "0.4 s" in _row("Slate shown", "the same within 0.4 s (`cross_double_s`)")


def test_slate_two_thumb_keyboard():
    for button, cursor in CONFIG.board_press.items():
        assert f"`press {cursor}`" in _row("Slate shown", _code(button))
    assert "`move 0 …`" in _row("Slate shown", "`ABS_X`/`ABS_Y`")
    assert "`move 1 …`" in _row("Slate shown", "`ABS_RX`/`ABS_RY`")
    row = _row("Slate shown", "`ABS_X`/`ABS_Y`")
    assert f"{CONFIG.board_delay_s} s" in row and f"{CONFIG.board_repeat_s} s" in row


def test_gamepad_raw_keeps_fn_b_and_recovery():
    text = DOC.read_text(encoding="utf-8")
    assert CONFIG.raw_close == "BTN_SOUTH" and "`BTN_MODE` + `BTN_SOUTH`, close" in text


def test_every_assigned_button_is_documented():
    text = DOC.read_text(encoding="utf-8")
    assigned = {*CONFIG.keys, *CONFIG.zone_keys, *CONFIG.fn_sway, *CONFIG.zone_fn, *CONFIG.board_press,
                CONFIG.click, CONFIG.zone_toggle, CONFIG.zone_dictate, CONFIG.menu, CONFIG.next_window, CONFIG.modifier}
    for button in assigned:
        assert button in text or button.startswith("BTN_DPAD_"), button


def test_wolfenstein_pad_and_keys_are_documented():
    import tomllib
    manifest = tomllib.loads((ROOT / "src/wyoh/apps/wolf3d/wyoh-app.template.toml").read_text(encoding="utf-8"))
    assert manifest["input"] == "gamepad-virtual"
    for button, number in manifest["pad"].items():
        assert f"Joystick button {number}" in _row("Apps fed a remapped joystick (\"gamepad-virtual\")", _code(button))
    for button, key in manifest["keys"].items():
        if not button.startswith("BTN_DPAD_"):
            assert _code(key) in _row("Apps fed a remapped joystick (\"gamepad-virtual\")", _code(button))
