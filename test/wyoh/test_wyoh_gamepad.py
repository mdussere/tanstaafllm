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

def test_slate_sends_with_fn_a(core):
    """User, 2026-10-09: FN+A sends, then clears and hides (the Slate closes)."""
    assert press(core, "BTN_TL") == [g.Zone("open")]
    assert core.zone_state == "open"
    press(core, "BTN_MODE")
    assert press(core, "BTN_EAST") == [g.Zone("validate")]
    assert core.zone_state == "delivering"
    core.zone_finished()
    assert core.zone_state == "closed"


def test_fn_x_clears_the_slate(core):
    press(core, "BTN_TL"); release(core, "BTN_TL")
    press(core, "BTN_MODE")
    assert press(core, "BTN_NORTH") == [g.Zone("clear")]
    assert core.zone_state == "open"


def test_l2_toggles_dictation(core):
    press(core, "BTN_TL"); release(core, "BTN_TL")
    assert press(core, "BTN_TL2") == [g.Zone("dictate")]
    assert core.zone_state == "open"


def test_a_and_b_edit_inside_the_slate_instead_of_closing_it(core):
    press(core, "BTN_TL"); release(core, "BTN_TL")
    assert press(core, "BTN_EAST") == [g.Key(K["KEY_ENTER"], True)]
    assert press(core, "BTN_SOUTH") == [g.Key(K["KEY_BACKSPACE"], True)]
    assert core.zone_state == "open"


def test_optional_alternate_validate_and_discard_buttons(core):
    core = g.GamepadCore(g.Config(zone_validate_alt="BTN_THUMBL", zone_discard_alt="BTN_SELECT"))
    press(core, "BTN_TL"); release(core, "BTN_TL")
    assert press(core, "BTN_THUMBL") == [g.Zone("validate")]
    core.zone_finished()
    press(core, "BTN_TL"); release(core, "BTN_TL")
    assert press(core, "BTN_SELECT") == [g.Zone("discard")]


def test_l1_hides_and_shows_the_slate_keeping_it(core):
    press(core, "BTN_TL"); release(core, "BTN_TL")
    assert press(core, "BTN_TL") == [g.Zone("hide")]
    release(core, "BTN_TL")
    assert core.zone_state == "hidden"
    assert press(core, "BTN_EAST") == [g.Key(K["KEY_ENTER"], True)]  # normal mapping while hidden
    release(core, "BTN_EAST")
    press(core, "BTN_MODE")
    assert press(core, "BTN_EAST") == [g.Sway("fullscreen toggle")]  # FN+A is Sway's again
    release(core, "BTN_EAST"); release(core, "BTN_MODE")
    assert press(core, "BTN_TL") == [g.Zone("show")]
    assert core.zone_state == "open"


def test_l2_does_nothing_while_the_slate_is_closed_or_hidden(core):
    assert press(core, "BTN_TL2") == [g.Note("ignored:BTN_TL2")]
    release(core, "BTN_TL2")
    press(core, "BTN_TL"); release(core, "BTN_TL"); press(core, "BTN_TL"); release(core, "BTN_TL")
    assert press(core, "BTN_TL2") == [g.Note("ignored:BTN_TL2")]


@pytest.mark.parametrize("button, chord", [
    ("BTN_EAST", ["KEY_ENTER"]), ("BTN_SOUTH", ["KEY_BACKSPACE"]), ("BTN_NORTH", ["KEY_DELETE"]),
    ("BTN_WEST", ["KEY_LEFTSHIFT"]),
    ("BTN_TR", ["KEY_LEFTCTRL", "KEY_RIGHT"]), ("BTN_TR2", ["KEY_LEFTCTRL", "KEY_LEFT"]),
])
def test_slate_keys_follow_the_users_mapping(core, button, chord):
    """User, 2026-10-09: A Return, B Backspace, X Delete, Y Shift, R1/R2 word moves."""
    press(core, "BTN_TL"); release(core, "BTN_TL")
    assert press(core, button) == [g.Key(K[k], True) for k in chord]
    assert release(core, button) == [g.Key(K[k], False) for k in reversed(chord)]


def open_slate(core):
    press(core, "BTN_TL"); release(core, "BTN_TL")


def test_an_arrow_in_the_slate_waits_the_cross_window_then_moves(core):
    open_slate(core)
    assert press(core, "BTN_DPAD_RIGHT", 1.0) == []
    assert core.needs_tick()
    assert core.tick(1.02) == []
    assert core.tick(1.05) == [g.Key(K["KEY_RIGHT"], True)]
    assert release(core, "BTN_DPAD_RIGHT", 1.5) == [g.Key(K["KEY_RIGHT"], False)]


def test_a_quick_arrow_tap_is_not_lost(core):
    open_slate(core)
    press(core, "BTN_DPAD_LEFT", 1.0)
    assert release(core, "BTN_DPAD_LEFT", 1.01) == [g.Key(K["KEY_LEFT"], True), g.Key(K["KEY_LEFT"], False)]
    assert not core.needs_tick()


def test_y_held_with_an_arrow_gives_shift_arrow(core):
    open_slate(core)
    assert press(core, "BTN_WEST", 1.0) == [g.Key(K["KEY_LEFTSHIFT"], True)]
    press(core, "BTN_DPAD_LEFT", 1.1)
    assert core.tick(1.2) == [g.Key(K["KEY_LEFT"], True)]


def test_whole_cross_selects_the_word_without_moving(core):
    open_slate(core)
    press(core, "BTN_DPAD_UP", 1.0)
    assert press(core, "BTN_DPAD_DOWN", 1.01) == [g.Zone("select-word")]
    assert press(core, "BTN_DPAD_LEFT", 1.02) == []  # more contacts of the same press
    assert core.tick(1.2) == []
    for button in ("BTN_DPAD_UP", "BTN_DPAD_DOWN", "BTN_DPAD_LEFT"):
        assert release(core, button, 1.3) == []
    assert core.counters["cross"] == 1


def test_whole_cross_twice_selects_the_line(core):
    open_slate(core)
    press(core, "BTN_DPAD_LEFT", 1.0); press(core, "BTN_DPAD_RIGHT", 1.01)
    release(core, "BTN_DPAD_LEFT", 1.1); release(core, "BTN_DPAD_RIGHT", 1.1)
    press(core, "BTN_DPAD_UP", 1.3)
    assert press(core, "BTN_DPAD_DOWN", 1.31) == [g.Zone("select-line")]
    release(core, "BTN_DPAD_UP", 1.4); release(core, "BTN_DPAD_DOWN", 1.4)
    press(core, "BTN_DPAD_UP", 1.5)  # a third press starts over: word again
    assert press(core, "BTN_DPAD_DOWN", 1.51) == [g.Zone("select-word")]


def test_whole_cross_presses_far_apart_are_two_word_toggles(core):
    open_slate(core)
    press(core, "BTN_DPAD_LEFT", 1.0); press(core, "BTN_DPAD_RIGHT", 1.01)
    release(core, "BTN_DPAD_LEFT", 1.1); release(core, "BTN_DPAD_RIGHT", 1.1)
    press(core, "BTN_DPAD_LEFT", 2.0)
    assert press(core, "BTN_DPAD_RIGHT", 2.01) == [g.Zone("select-word")]


def test_a_second_direction_after_the_window_is_two_moves(core):
    open_slate(core)
    press(core, "BTN_DPAD_RIGHT", 1.0)
    core.tick(1.05)
    press(core, "BTN_DPAD_DOWN", 1.2)
    assert core.tick(1.25) == [g.Key(K["KEY_DOWN"], True)]


def test_another_button_flushes_a_waiting_arrow_first(core):
    open_slate(core)
    press(core, "BTN_DPAD_RIGHT", 1.0)
    assert press(core, "BTN_EAST", 1.01) == [g.Key(K["KEY_RIGHT"], True), g.Key(K["KEY_ENTER"], True)]


def test_arrows_outside_the_slate_stay_immediate(core):
    assert press(core, "BTN_DPAD_UP", 1.0) == [g.Key(K["KEY_UP"], True)]
    assert press(core, "BTN_DPAD_DOWN", 1.01) == [g.Key(K["KEY_DOWN"], True)]


def test_hiding_the_slate_flushes_a_waiting_arrow_first(core):
    open_slate(core)
    press(core, "BTN_DPAD_RIGHT", 1.0)
    assert press(core, "BTN_TL", 1.01) == [g.Key(K["KEY_RIGHT"], True), g.Zone("hide")]
    assert not core.needs_tick() or core.tick(1.2) == []


# --- two-thumb typing on the on-screen keyboard (user, 2026-10-09) ----------

@pytest.mark.parametrize("axis, value, cursor, op", [
    (g.ABS_X, -1800, 0, "left"), (g.ABS_X, 1800, 0, "right"),
    (g.ABS_Y, -1800, 0, "up"), (g.ABS_Y, 1800, 0, "down"),
    (g.ABS_RX, -1800, 1, "left"), (g.ABS_RY, 1800, 1, "down"),
])
def test_sticks_step_their_selection_in_the_slate(core, axis, value, cursor, op):
    open_slate(core)
    assert core.axis(axis, value, 1.0) == [g.Board(cursor, op)]


def test_a_held_stick_repeats_after_a_delay(core):
    open_slate(core)
    core.axis(g.ABS_X, 1800, 1.0)
    assert core.needs_tick()
    assert core.tick(1.2) == []
    assert core.tick(1.3) == [g.Board(0, "right")]
    assert core.tick(1.35) == []
    assert core.tick(1.42) == [g.Board(0, "right")]


def test_letting_go_stops_and_a_new_push_steps_again(core):
    open_slate(core)
    core.axis(g.ABS_RY, -1800, 1.0)
    assert core.axis(g.ABS_RY, -500, 1.05) == []  # below the release level: let go
    assert not core.needs_tick()
    assert core.axis(g.ABS_RY, -1800, 1.1) == [g.Board(1, "up")]


def test_a_small_deflection_does_nothing(core):
    open_slate(core)
    assert core.axis(g.ABS_X, 700, 1.0) == []  # 0.39 < threshold 0.5


def test_changing_direction_while_held_steps_at_once(core):
    open_slate(core)
    core.axis(g.ABS_RX, 1800, 1.0)
    core.axis(g.ABS_RX, 0, 1.05)
    assert core.axis(g.ABS_RY, 1800, 1.06) == [g.Board(1, "down")]


def test_both_selections_move_independently(core):
    open_slate(core)
    core.axis(g.ABS_X, -1800, 1.0)
    core.axis(g.ABS_RX, 1800, 1.0)
    assert core.tick(1.31) == [g.Board(0, "left"), g.Board(1, "right")]


@pytest.mark.parametrize("button, cursor", [("BTN_THUMBL", 0), ("BTN_THUMBR", 1)])
def test_stick_clicks_type_the_selected_keys(core, button, cursor):
    open_slate(core)
    assert press(core, button) == [g.Board(cursor, "press")]
    assert release(core, button) == []


def test_no_pointer_while_the_slate_is_open(core):
    open_slate(core)
    core.axis(g.ABS_RX, 1800, 1.0)
    assert all(not isinstance(action, g.Motion) for action in core.tick(1.05) + core.tick(1.4))


def test_sticks_drive_the_pointer_again_when_the_slate_is_hidden(core):
    open_slate(core)
    core.axis(g.ABS_RX, 1800, 1.0)
    press(core, "BTN_TL")  # hide
    assert core.zone_state == "hidden"
    assert core.needs_tick()
    assert any(isinstance(action, g.Motion) for action in core.tick(1.1))


def test_menu_window_and_fn_actions_are_inert_while_the_zone_is_open(core):
    press(core, "BTN_TL"); release(core, "BTN_TL")
    assert press(core, "BTN_START") == [g.Note("ignored:BTN_START")]
    assert press(core, "BTN_SELECT") == [g.Note("ignored:BTN_SELECT")]
    press(core, "BTN_MODE")
    assert press(core, "BTN_SOUTH") == [g.Note("ignored:BTN_SOUTH")]
    assert core.zone_state == "open"


def test_zone_ignores_buttons_while_delivering(core):
    press(core, "BTN_TL"); release(core, "BTN_TL")
    press(core, "BTN_MODE"); press(core, "BTN_EAST")
    release(core, "BTN_EAST"); release(core, "BTN_MODE")
    assert press(core, "BTN_TL") == [g.Note("busy:BTN_TL")]
    assert core.zone_state == "delivering"


# --- per-app gamepad profiles (Step 9.3) ------------------------------------

@pytest.fixture
def raw_core() -> g.GamepadCore:
    return g.GamepadCore(g.Config(app_profiles={"wolf3d": "gamepad-raw", "calc": "keys"}))


def test_a_gamepad_raw_app_gets_the_gamepad(raw_core):
    press(raw_core, "BTN_DPAD_UP")  # held when the focus changes
    actions = raw_core.focus("wolf3d")
    assert g.Key(K["KEY_UP"], False) in actions and g.Grab(False) in actions
    assert raw_core.raw
    assert press(raw_core, "BTN_EAST") == []  # the app reads A itself
    assert raw_core.axis(g.ABS_RX, 1800, 1.0) == [] and not raw_core.needs_tick()


def test_fn_b_still_closes_a_gamepad_raw_app(raw_core):
    raw_core.focus("wolf3d")
    press(raw_core, "BTN_MODE")
    assert press(raw_core, "BTN_SOUTH") == [g.Sway("kill")]


def test_recovery_still_works_and_takes_the_gamepad_back(raw_core):
    raw_core.focus("wolf3d")
    press(raw_core, "BTN_MODE", 0.0)
    press(raw_core, "BTN_START", 0.0)
    actions = raw_core.tick(2.1)
    assert g.Grab(True) in actions and g.Note("recovery") in actions
    assert not raw_core.raw


def test_leaving_the_app_takes_the_gamepad_back(raw_core):
    raw_core.focus("wolf3d")
    press(raw_core, "BTN_EAST")  # held inside the app
    assert raw_core.focus("foot") == [g.Grab(True), g.Note("raw:off")]
    assert press(raw_core, "BTN_EAST") == [g.Key(K["KEY_ENTER"], True)]


@pytest.mark.parametrize("app_id", ["calc", "foot", None])
def test_other_apps_keep_the_mapping(raw_core, app_id):
    assert raw_core.focus(app_id) == []
    assert press(raw_core, "BTN_EAST") == [g.Key(K["KEY_ENTER"], True)]


def test_focus_between_two_raw_apps_changes_nothing():
    core = g.GamepadCore(g.Config(app_profiles={"a": "gamepad-raw", "b": "gamepad-raw"}))
    core.focus("a")
    assert core.focus("b") == []


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
    assert "{socket}" in config.zone_command and "--app-id=wyoh-slate" in config.zone_command
    assert config.keyboard_command[0] == "wvkbd-luna"
    assert "#ffffff" in config.zone_open_sway and "#5294e2" in config.zone_close_sway


@pytest.mark.parametrize("text, message", [
    ('surprise = 1', "unknown setting"),
    ('click = "BTN_NOPE"', "unknown button"),
    ('keys = { BTN_EAST = "KEY_NOPE" }', "unknown key"),
    ('zone_keys = { BTN_EAST = "KEY_NOPE" }', "unknown key"),
    ("cross_window_s = 0.5", "cross_window_s"),
    ("board_release = 0.9", "invalid board"),
    ('app_profiles = { wolf3d = "joystick" }', "app_profiles"),
    ('zone_fn = { BTN_NORTH = "explode" }', "zone_fn"),
    ('board_press = { BTN_THUMBL = 2 }', "invalid board"),
    ('[pointer]\nwobble = 1', "unknown pointer"),
    ('[pointer]\ndead_zone = 1.5', "invalid pointer"),
    ('pointer_stick = "middle"', "pointer_stick"),
])
def test_invalid_config_is_refused(tmp_path, text, message):
    path = tmp_path / "gamepad.toml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(g.ConfigError, match=message):
        g.load_config(path)


# --- typing Slate text through the daemon's keyboard (Step 9.1b fix) --------

P = g.PHYSICAL


def test_plain_letters_and_azerty_swaps():
    assert g.type_events("az") == [(P["q"], 1), (P["q"], 0), (P["w"], 1), (P["w"], 0)]


def test_digits_need_shift_on_azerty():
    assert g.type_events("7") == [(P["shift"], 1), (P["7"], 1), (P["7"], 0), (P["shift"], 0)]


def test_altgr_characters_and_newline():
    assert g.type_events("|") == [(P["altgr"], 1), (P["6"], 1), (P["6"], 0), (P["altgr"], 0)]
    assert g.type_events("\n") == [(P["enter"], 1), (P["enter"], 0)]


@pytest.mark.parametrize("text", ["echo hello > /tmp/x-7 && ls | grep -v ~", "café à l'eau", "A=1; B=$((A+2))"])
def test_typical_shell_text_is_typable(text):
    assert g.type_events(text) is not None


def test_untypable_text_falls_back():
    assert g.type_events("œ") is None and g.type_events("日本") is None


def test_every_mapped_key_is_registered_on_the_daemon_keyboard():
    used = {P[name] for name, _ in g.AZERTY.values()} | {P["shift"], P["altgr"]}
    assert used <= set(P.values())


# --- per-app key maps (Step 9.3: Wolfenstein) ---------------------------------

def test_an_app_key_map_applies_while_it_has_the_focus():
    core = g.GamepadCore(g.Config(app_keys={"ecwolf": {"BTN_TR": "KEY_LEFTCTRL", "BTN_EAST": "KEY_SPACE"}}))
    assert core.focus("ecwolf") == []  # no grab change: the daemon keeps the gamepad
    assert press(core, "BTN_TR") == [g.Key(K["KEY_LEFTCTRL"], True)]
    assert press(core, "BTN_EAST") == [g.Key(K["KEY_SPACE"], True)]
    assert press(core, "BTN_DPAD_UP") == [g.Key(K["KEY_UP"], True)]  # unmapped buttons keep the default
    release(core, "BTN_TR"); release(core, "BTN_EAST")
    core.focus("foot")
    assert press(core, "BTN_TR") == [g.Key(K["KEY_TAB"], True)]


def test_a_key_held_across_a_focus_change_releases_what_it_pressed():
    core = g.GamepadCore(g.Config(app_keys={"ecwolf": {"BTN_TR": "KEY_LEFTCTRL"}}))
    core.focus("ecwolf")
    press(core, "BTN_TR")
    core.focus("foot")
    assert release(core, "BTN_TR") == [g.Key(K["KEY_LEFTCTRL"], False)]


def test_the_slate_keeps_its_own_keys_in_an_app():
    core = g.GamepadCore(g.Config(app_keys={"ecwolf": {"BTN_EAST": "KEY_SPACE"}}))
    core.focus("ecwolf")
    open_slate(core)
    assert press(core, "BTN_EAST") == [g.Key(K["KEY_ENTER"], True)]


def test_invalid_app_keys_are_refused(tmp_path):
    path = tmp_path / "gamepad.toml"
    path.write_text('[app_keys.ecwolf]\nBTN_NOPE = "KEY_SPACE"\n', encoding="utf-8")
    with pytest.raises(g.ConfigError, match="unknown button"):
        g.load_config(path)


# --- dictation (Step 12): Mycroft's protocol -> Slate operations ------------------

def test_lines_are_split_and_the_rest_kept():
    messages, rest = g.split_lines(b'{"op": "ready"}\n{"op": "partial", "text": "ce si')
    assert messages == [{"op": "ready"}] and rest == b'{"op": "partial", "text": "ce si'
    messages, rest = g.split_lines(rest + b'te"}\nnot json\n')
    assert messages == [{"op": "partial", "text": "ce site"}] and rest == b""


@pytest.mark.parametrize("message, operations", [
    ({"op": "ready"}, [{"op": "dictation", "state": "listening"}]),
    ({"op": "partial", "text": "ce site con"}, [{"op": "provisional", "text": "ce site con"}]),
    ({"op": "final", "text": "ce site contient"}, [{"op": "insert", "text": "ce site contient"}]),
    ({"op": "error", "message": "no microphone"},
     [{"op": "provisional", "text": ""}, {"op": "dictation", "state": "error: no microphone"}]),
    ({"op": "unknown"}, []),
])
def test_mycroft_messages_become_slate_operations(message, operations):
    assert g.slate_operations(message) == operations


def test_the_deployed_config_starts_mycroft_on_luna():
    config = g.load_config(ROOT / "src/wyoh/deploy/luna/gamepad.toml")
    command = config.dictate_command
    assert command[1].endswith("mycroft/mycroft_dictate.py")
    assert "--input" in command and "--assets" in command and "--threads" in command


def _sound(tmp_path, cards: dict[int, bool]):
    snd, asound = tmp_path / "snd", tmp_path / "asound"
    snd.mkdir(); asound.mkdir()
    for number, is_usb in cards.items():
        (snd / f"pcmC{number}D0c").touch()
        (snd / f"pcmC{number}D0p").touch()
        (asound / f"card{number}").mkdir()
        if is_usb:
            (asound / f"card{number}" / "usbid").write_text("1234:5678\n", encoding="utf-8")
    return snd, asound


def test_a_usb_microphone_is_preferred(tmp_path):
    snd, asound = _sound(tmp_path, {0: False, 1: True})
    assert g.choose_capture(snd, asound) == str(snd / "pcmC1D0c")


def test_without_usb_the_built_in_capture_device_is_used(tmp_path):
    snd, asound = _sound(tmp_path, {0: False})
    assert g.choose_capture(snd, asound) == str(snd / "pcmC0D0c")


def test_no_capture_device_at_all(tmp_path):
    snd, asound = _sound(tmp_path, {})
    assert g.choose_capture(snd, asound) is None


# --- gamepad-virtual (Step 9.8b: Wolfenstein's remapped joystick) ----------------

@pytest.fixture
def wolf() -> g.GamepadCore:
    core = g.GamepadCore(g.Config(
        app_profiles={"ecwolf": "gamepad-virtual"},
        app_pad={"ecwolf": {"BTN_EAST": 0, "BTN_TR": 0, "BTN_SOUTH": 1, "BTN_TL": 1}},
        app_keys={"ecwolf": {"BTN_START": "KEY_ESC", "BTN_DPAD_UP": "KEY_UP"}}))
    core.focus("ecwolf")
    return core


def test_two_buttons_share_a_virtual_button(wolf):
    assert press(wolf, "BTN_EAST") == [g.PadButton(0, True)]   # A fires / validates
    assert press(wolf, "BTN_TR") == [g.PadButton(0, True)]     # R1 fires too
    assert press(wolf, "BTN_TL") == [g.PadButton(1, True)]     # L1 opens, like B
    assert release(wolf, "BTN_EAST") == [g.PadButton(0, False)]


def test_l1_belongs_to_the_game_not_the_slate(wolf):
    press(wolf, "BTN_TL")
    assert wolf.zone_state == "closed"


def test_sticks_pass_through_and_the_pointer_stays_still(wolf):
    assert wolf.axis(g.ABS_X, -900, 1.0) == [g.PadAxis(g.ABS_X, -900)]
    assert wolf.axis(g.ABS_RX, 1800, 1.0) == [g.PadAxis(g.ABS_RX, 1800)]
    assert not wolf.needs_tick()


def test_app_keys_and_unmapped_buttons(wolf):
    assert press(wolf, "BTN_START") == [g.Key(K["KEY_ESC"], True)]
    assert press(wolf, "BTN_SELECT") == []  # nothing: not mapped for the game


def test_fn_b_closes_the_game_and_recovery_still_works(wolf):
    press(wolf, "BTN_MODE")
    assert press(wolf, "BTN_SOUTH") == [g.Sway("kill")]
    release(wolf, "BTN_SOUTH")
    press(wolf, "BTN_START", 1.0)
    assert g.Note("recovery") in wolf.tick(3.1)


def test_leaving_the_game_releases_virtual_buttons(wolf):
    press(wolf, "BTN_TR")
    assert g.PadButton(0, False) in wolf.focus("foot")
    assert press(wolf, "BTN_TR") == [g.Key(K["KEY_TAB"], True)]


def test_invalid_app_pad_is_refused(tmp_path):
    path = tmp_path / "gamepad.toml"
    path.write_text('[app_pad.ecwolf]\nBTN_EAST = 16\n', encoding="utf-8")
    with pytest.raises(g.ConfigError, match="app_pad"):
        g.load_config(path)
