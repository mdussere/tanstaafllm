"""Deterministic tests for the Wyoh gamepad core (Step 5.2).

The core is pure: gamepad events and clock ticks in, output actions out. These
tests follow the mapping table and state machine in
worklines/wyoh/docs/0500_01_gamepad-input-intent.md. No device is touched.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "src" / "wyoh"))
import wyoh_gamepad as g  # noqa: E402

B = g.BUTTONS
K = g.KEYS


@pytest.fixture
def core() -> g.GamepadCore:
    return g.GamepadCore(g.Config())


def press(core: g.GamepadCore, name: str, now: float = 0.0) -> list:
    return core.button(B[name], True, now)


def release(core: g.GamepadCore, name: str, now: float = 0.0) -> list:
    return core.button(B[name], False, now)


# --- normal mode -------------------------------------------------------------

@pytest.mark.parametrize("button, key", [
    ("BTN_DPAD_UP", "KEY_UP"), ("BTN_DPAD_DOWN", "KEY_DOWN"),
    ("BTN_DPAD_LEFT", "KEY_LEFT"), ("BTN_DPAD_RIGHT", "KEY_RIGHT"),
    ("BTN_EAST", "KEY_ENTER"), ("BTN_SOUTH", "KEY_ESC"),
    ("BTN_WEST", "KEY_BACKSPACE"), ("BTN_NORTH", "KEY_DELETE"),
    ("BTN_TR", "KEY_TAB"),
])
def test_buttons_hold_their_key_until_release(core, button, key):
    assert press(core, button) == [g.Key(K[key], True)]
    assert release(core, button) == [g.Key(K[key], False)]


def test_r2_is_shift_tab_released_in_reverse_order(core):
    assert press(core, "BTN_TR2") == [g.Key(K["KEY_LEFTSHIFT"], True), g.Key(K["KEY_TAB"], True)]
    assert release(core, "BTN_TR2") == [g.Key(K["KEY_TAB"], False), g.Key(K["KEY_LEFTSHIFT"], False)]


def test_r3_is_left_click(core):
    assert press(core, "BTN_THUMBR") == [g.Click(g.BTN_LEFT, True)]
    assert release(core, "BTN_THUMBR") == [g.Click(g.BTN_LEFT, False)]


def test_start_opens_the_menu_and_select_cycles_windows(core):
    assert press(core, "BTN_START") == [g.Menu()]
    assert release(core, "BTN_START") == []
    assert press(core, "BTN_SELECT") == [g.Sway("focus next")]


def test_device_autorepeat_press_is_ignored(core):
    press(core, "BTN_DPAD_DOWN")
    assert press(core, "BTN_DPAD_DOWN") == []


def test_unassigned_buttons_are_ignored_and_counted(core):
    assert press(core, "BTN_THUMBL") == [g.Note("ignored:BTN_THUMBL")]
    assert press(core, "BTN_TL2") == [g.Note("ignored:BTN_TL2")]  # L2 does nothing while the zone is closed
    assert core.counters["ignored"] == 2


def test_left_stick_is_unassigned(core):
    assert core.axis(g.ABS_X, 1800) == []
    assert not core.needs_tick()


def test_pointer_stick_can_be_switched_back_to_the_left():
    core = g.GamepadCore(g.Config(pointer_stick="left"))
    core.axis(g.ABS_X, 1800)
    assert core.needs_tick()


# --- FN combinations ---------------------------------------------------------

@pytest.mark.parametrize("button, command", [
    ("BTN_DPAD_UP", "focus up"), ("BTN_DPAD_DOWN", "focus down"),
    ("BTN_DPAD_LEFT", "focus left"), ("BTN_DPAD_RIGHT", "focus right"),
    ("BTN_EAST", "fullscreen toggle"), ("BTN_SOUTH", "kill"),
    ("BTN_TR", "workspace next"), ("BTN_TR2", "workspace prev"),
])
def test_fn_combinations_are_sway_commands(core, button, command):
    assert press(core, "BTN_MODE") == []
    assert press(core, button) == [g.Sway(command)]
    assert release(core, button) == []  # no key was pressed, nothing to release


def test_fn_with_an_unmapped_button_does_nothing(core):
    press(core, "BTN_MODE")
    assert press(core, "BTN_WEST") == [g.Note("ignored:BTN_WEST")]


def test_key_held_before_fn_is_released_normally(core):
    press(core, "BTN_DPAD_LEFT")
    press(core, "BTN_MODE")
    assert release(core, "BTN_DPAD_LEFT") == [g.Key(K["KEY_LEFT"], False)]


# --- input zone --------------------------------------------------------------

def test_zone_open_validate_with_l2(core):
    assert press(core, "BTN_TL") == [g.Zone("open")]
    assert core.zone_state == "open"
    assert press(core, "BTN_TL2") == [g.Zone("validate")]
    assert core.zone_state == "delivering"
    core.zone_finished()
    assert core.zone_state == "closed"


def test_zone_a_validates_and_b_discards(core):
    press(core, "BTN_TL"); release(core, "BTN_TL")
    assert press(core, "BTN_EAST") == [g.Zone("validate")]
    core.zone_finished(); release(core, "BTN_EAST")
    press(core, "BTN_TL"); release(core, "BTN_TL")
    assert press(core, "BTN_SOUTH") == [g.Zone("discard")]
    assert core.zone_state == "closed"


def test_l1_closes_an_open_zone_by_discarding(core):
    press(core, "BTN_TL"); release(core, "BTN_TL")
    assert press(core, "BTN_TL") == [g.Zone("discard")]
    assert core.zone_state == "closed"


@pytest.mark.parametrize("button, key", [
    ("BTN_DPAD_LEFT", "KEY_LEFT"), ("BTN_DPAD_RIGHT", "KEY_RIGHT"),
    ("BTN_WEST", "KEY_BACKSPACE"), ("BTN_NORTH", "KEY_DELETE"), ("BTN_TR", "KEY_TAB"),
])
def test_editing_keys_work_inside_the_zone(core, button, key):
    press(core, "BTN_TL"); release(core, "BTN_TL")
    assert press(core, button) == [g.Key(K[key], True)]


def test_menu_window_and_fn_actions_are_inert_while_the_zone_is_open(core):
    press(core, "BTN_TL"); release(core, "BTN_TL")
    assert press(core, "BTN_START") == [g.Note("ignored:BTN_START")]
    assert press(core, "BTN_SELECT") == [g.Note("ignored:BTN_SELECT")]
    press(core, "BTN_MODE")
    assert press(core, "BTN_SOUTH") == [g.Note("ignored:BTN_SOUTH")]
    assert core.zone_state == "open"


def test_zone_ignores_buttons_while_delivering(core):
    press(core, "BTN_TL"); release(core, "BTN_TL")
    press(core, "BTN_TL2")
    assert press(core, "BTN_TL") == [g.Note("busy:BTN_TL")]
    assert core.zone_state == "delivering"


# --- recovery ----------------------------------------------------------------

def test_recovery_after_fn_start_held_two_seconds(core):
    press(core, "BTN_DPAD_UP", 0.0)
    press(core, "BTN_TL", 0.0)  # zone opens; arrow key still held
    press(core, "BTN_MODE", 1.0)
    press(core, "BTN_START", 1.0)
    assert core.needs_tick()
    assert core.tick(2.5) == []
    actions = core.tick(3.0)
    assert g.Key(K["KEY_UP"], False) in actions
    assert g.Zone("discard") in actions
    assert g.Note("recovery") in actions
    assert core.zone_state == "closed" and core.counters["recovery"] == 1
    assert core.tick(5.0) == []  # once per hold


def test_recovery_is_cancelled_by_an_early_release(core):
    press(core, "BTN_MODE", 0.0)
    press(core, "BTN_START", 0.0)
    release(core, "BTN_START", 1.0)
    assert core.tick(3.0) == []
    assert core.counters["recovery"] == 0


def test_fn_start_does_not_open_the_menu(core):
    press(core, "BTN_MODE")
    assert press(core, "BTN_START") == []


# --- pointer -----------------------------------------------------------------

def test_dead_zone_produces_no_motion_and_no_ticks(core):
    core.axis(g.ABS_RX, 200)  # 0.11 < 0.12
    assert not core.needs_tick()
    assert core.tick(0.01) == []


def test_full_deflection_reaches_max_speed():
    vx, vy = g.pointer_speed(1800, 0, g.PointerConfig())
    assert math.isclose(vx, 900.0) and vy == 0.0
    vx, vy = g.pointer_speed(-1800, -1800, g.PointerConfig())  # capped at r = 1
    assert math.isclose(math.hypot(vx, vy), 900.0) and vx < 0 and vy < 0


def test_curve_is_gentle_near_the_centre():
    half = g.pointer_speed(0.56 * 1800, 0, g.PointerConfig())[0]
    assert math.isclose(half, 900.0 * 0.5 ** 2, rel_tol=1e-6)


def test_slow_motion_accumulates_fractions(core):
    core.axis(g.ABS_RX, int(0.2 * 1800))  # about 7.4 px/s: under 1 px per tick
    total = 0
    for step in range(1, 101):  # one second at 100 Hz
        for action in core.tick(step / 100):
            total += action.dx
    assert 6 <= total <= 8


def test_stick_return_stops_motion(core):
    core.axis(g.ABS_RY, 1800)
    assert core.needs_tick()
    assert core.tick(0.01) and core.tick(0.02)
    core.axis(g.ABS_RY, 0)
    assert not core.needs_tick()
    assert core.tick(0.03) == []


# --- configuration -----------------------------------------------------------

def test_deployed_config_loads():
    config = g.load_config(ROOT / "src/wyoh/deploy/luna/gamepad.toml")
    assert config.devices == ("r36s_Gamepad", "wyoh-virtual-gamepad")
    assert "--prompt-only" in config.zone_command


@pytest.mark.parametrize("text, message", [
    ('surprise = 1', "unknown setting"),
    ('click = "BTN_NOPE"', "unknown button"),
    ('keys = { BTN_EAST = "KEY_NOPE" }', "unknown key"),
    ('[pointer]\nwobble = 1', "unknown pointer"),
    ('[pointer]\ndead_zone = 1.5', "invalid pointer"),
    ('pointer_stick = "middle"', "pointer_stick"),
])
def test_invalid_config_is_refused(tmp_path, text, message):
    path = tmp_path / "gamepad.toml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(g.ConfigError, match=message):
        g.load_config(path)
