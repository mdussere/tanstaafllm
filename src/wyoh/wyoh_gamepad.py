#!/usr/bin/env python3
"""Wyoh gamepad daemon: operate the Luna session with the device's own controls.

Intent: worklines/wyoh/docs/0500_01_gamepad-input-intent.md (Wyoh Step 5);
the Slate and its controls: worklines/wyoh/docs/0600_01_slate-and-keyboard-proposal.md
(Wyoh Step 6).

Standard library only. The module has two layers:

* a pure core (`GamepadCore`) that turns gamepad events and clock ticks into
  output actions; it is fully testable without devices;
* thin adapters (evdev input, uinput output, Sway IPC, the Slate and its
  on-screen keyboard) and the `select()` loop in `main()`.

The "zone" of Step 5 is now the Slate (`wyoh_slate.py`): a floating terminal
window that receives editing keys from this daemon's virtual keyboard and
commands (select, send, discard) on a private Unix socket.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import math
import os
import select
import signal
import socket
import struct
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# --- Linux input codes -------------------------------------------------------

EV_SYN, EV_KEY, EV_REL, EV_ABS = 0, 1, 2, 3
SYN_REPORT = 0
REL_X, REL_Y = 0, 1
ABS_X, ABS_Y, ABS_RX, ABS_RY = 0, 1, 3, 4
BTN_LEFT = 0x110

BUTTONS = {
    "BTN_SOUTH": 0x130, "BTN_EAST": 0x131, "BTN_NORTH": 0x133, "BTN_WEST": 0x134,
    "BTN_TL": 0x136, "BTN_TR": 0x137, "BTN_TL2": 0x138, "BTN_TR2": 0x139,
    "BTN_SELECT": 0x13A, "BTN_START": 0x13B, "BTN_MODE": 0x13C,
    "BTN_THUMBL": 0x13D, "BTN_THUMBR": 0x13E,
    "BTN_DPAD_UP": 0x220, "BTN_DPAD_DOWN": 0x221, "BTN_DPAD_LEFT": 0x222, "BTN_DPAD_RIGHT": 0x223,
}
BUTTON_NAMES = {code: name for name, code in BUTTONS.items()}
PAD_BUTTONS = 16  # the virtual joystick's buttons, codes 0x130.. in order (SDL numbers them 0..15)
DPAD = {BUTTONS[f"BTN_DPAD_{d}"] for d in ("UP", "DOWN", "LEFT", "RIGHT")}

KEYS = {
    "KEY_ESC": 1, "KEY_BACKSPACE": 14, "KEY_TAB": 15, "KEY_ENTER": 28, "KEY_LEFTCTRL": 29, "KEY_LEFTSHIFT": 42,
    "KEY_LEFTALT": 56, "KEY_SPACE": 57,
    "KEY_UP": 103, "KEY_LEFT": 105, "KEY_RIGHT": 106, "KEY_DOWN": 108, "KEY_DELETE": 111,
    "KEY_DOT": 52,  # with Shift on Sway's AZERTY: "/"
}

# Physical key codes (US-labelled positions); Sway applies `xkb_layout fr`.
PHYSICAL = {
    "1": 2, "2": 3, "3": 4, "4": 5, "5": 6, "6": 7, "7": 8, "8": 9, "9": 10, "0": 11,
    "minus": 12, "equal": 13,
    "q": 16, "w": 17, "e": 18, "r": 19, "t": 20, "y": 21, "u": 22, "i": 23, "o": 24, "p": 25,
    "rightbrace": 27,
    "a": 30, "s": 31, "d": 32, "f": 33, "g": 34, "h": 35, "j": 36, "k": 37, "l": 38,
    "semicolon": 39, "apostrophe": 40, "backslash": 43,
    "z": 44, "x": 45, "c": 46, "v": 47, "b": 48, "n": 49, "m": 50,
    "comma": 51, "dot": 52, "slash": 53, "space": 57, "enter": 28, "tab": 15, "esc": 1,
    "backspace": 14, "shift": 42, "altgr": 100, "less": 86,
}

# Character -> (physical key, modifier) on a French AZERTY keyboard; modifier is
# "" (none), "shift" or "altgr". Used to type Slate text through the daemon's
# own uinput keyboard (SDL2 apps crash on wtype's per-key keymaps, Wyoh 9.1b).
AZERTY: dict[str, tuple[str, str]] = {
    **{c: (c, "") for c in "bcdefghijklnoprstuvxy"},
    **{c.upper(): (c, "shift") for c in "bcdefghijklnoprstuvxy"},
    "a": ("q", ""), "A": ("q", "shift"), "q": ("a", ""), "Q": ("a", "shift"),
    "z": ("w", ""), "Z": ("w", "shift"), "w": ("z", ""), "W": ("z", "shift"),
    "m": ("semicolon", ""), "M": ("semicolon", "shift"),
    **{d: (d, "shift") for d in "1234567890"},  # digits are shifted on AZERTY
    "&": ("1", ""), "é": ("2", ""), '"': ("3", ""), "'": ("4", ""), "(": ("5", ""), "-": ("6", ""),
    "è": ("7", ""), "_": ("8", ""), "ç": ("9", ""), "à": ("0", ""), ")": ("minus", ""), "=": ("equal", ""),
    "°": ("minus", "shift"), "+": ("equal", "shift"),
    "~": ("2", "altgr"), "#": ("3", "altgr"), "{": ("4", "altgr"), "[": ("5", "altgr"), "|": ("6", "altgr"),
    "`": ("7", "altgr"), "\\": ("8", "altgr"), "^": ("9", "altgr"), "@": ("0", "altgr"),
    "]": ("minus", "altgr"), "}": ("equal", "altgr"),
    "$": ("rightbrace", ""), "£": ("rightbrace", "shift"), "ù": ("apostrophe", ""), "%": ("apostrophe", "shift"),
    "*": ("backslash", ""), "µ": ("backslash", "shift"),
    " ": ("space", ""), "\n": ("enter", ""), "\t": ("tab", ""),
    ",": ("m", ""), "?": ("m", "shift"), ";": ("comma", ""), ".": ("comma", "shift"),
    ":": ("dot", ""), "/": ("dot", "shift"), "!": ("slash", ""), "§": ("slash", "shift"),
    "<": ("less", ""), ">": ("less", "shift"),
}


def type_events(text: str) -> list[tuple[int, int]] | None:
    """(key code, 1 or 0) presses that type `text` on AZERTY, or None if a
    character has no key (the caller then falls back to wtype)."""
    events: list[tuple[int, int]] = []
    for char in text:
        if char not in AZERTY:
            return None
        name, modifier = AZERTY[char]
        codes = ([PHYSICAL[modifier]] if modifier else []) + [PHYSICAL[name]]
        events += [(code, 1) for code in codes] + [(code, 0) for code in reversed(codes)]
    return events


# --- Configuration -----------------------------------------------------------


@dataclass(frozen=True)
class PointerConfig:
    dead_zone: float = 0.12
    max_speed: float = 900.0  # px/s at full deflection
    gamma: float = 2.0
    tick_hz: float = 100.0
    axis_max: float = 1800.0


@dataclass(frozen=True)
class Config:
    devices: tuple[str, ...] = ("r36s_Gamepad", "wyoh-virtual-gamepad")
    grab: bool = True
    # button -> key (one key, or "KEY_LEFTSHIFT+KEY_TAB" for a chord)
    keys: dict[str, str] = field(default_factory=lambda: {
        "BTN_DPAD_UP": "KEY_UP", "BTN_DPAD_DOWN": "KEY_DOWN",
        "BTN_DPAD_LEFT": "KEY_LEFT", "BTN_DPAD_RIGHT": "KEY_RIGHT",
        "BTN_EAST": "KEY_ENTER", "BTN_SOUTH": "KEY_ESC",
        "BTN_WEST": "KEY_BACKSPACE", "BTN_NORTH": "KEY_DELETE",
        "BTN_TR": "KEY_TAB", "BTN_TR2": "KEY_LEFTSHIFT+KEY_TAB",
    })
    # Right thumb on the pointer, left thumb on the D-pad (user, 2026-10-08).
    pointer_stick: str = "right"  # "left" | "right"
    click: str = "BTN_THUMBR"
    # The Slate (user, 2026-10-09): L1 shows or hides it (its text is kept),
    # L2 starts or stops dictation (Step 12), and inside it FN+X clears and
    # FN+A sends, then clears and hides.
    zone_toggle: str = "BTN_TL"
    zone_dictate: str = "BTN_TL2"
    # FN in the Slate (user, 2026-10-15): B sends to Mike (reserved until Mike
    # runs on Luna), Y sends to Mannie's window, up/down walk the history.
    zone_fn: dict[str, str] = field(default_factory=lambda: {
        "BTN_NORTH": "clear", "BTN_EAST": "validate", "BTN_SOUTH": "mike", "BTN_WEST": "mannie",
        "BTN_DPAD_UP": "history-prev", "BTN_DPAD_DOWN": "history-next"})
    zone_validate: str = ""  # optional plain-button send ("" = none)
    zone_validate_alt: str = ""  # optional second validate button ("" = none)
    zone_discard_alt: str = ""   # optional second discard button ("" = none)
    # While the Slate is open (user, 2026-10-09): A Return, B Backspace,
    # X Delete, Y Shift (selection with the arrows), R1/R2 next/previous word.
    zone_keys: dict[str, str] = field(default_factory=lambda: {
        "BTN_DPAD_UP": "KEY_UP", "BTN_DPAD_DOWN": "KEY_DOWN",
        "BTN_DPAD_LEFT": "KEY_LEFT", "BTN_DPAD_RIGHT": "KEY_RIGHT",
        "BTN_EAST": "KEY_ENTER", "BTN_SOUTH": "KEY_BACKSPACE",
        # X types "/" for agents' commands (user, 2026-10-15; was Delete).
        "BTN_NORTH": "KEY_LEFTSHIFT+KEY_DOT", "BTN_WEST": "KEY_LEFTSHIFT",
        "BTN_TR": "KEY_LEFTCTRL+KEY_RIGHT", "BTN_TR2": "KEY_LEFTCTRL+KEY_LEFT",
    })
    # The whole cross pressed at once (two directions within cross_window_s)
    # selects the word; a second one within cross_double_s selects the line.
    # Only inside the Slate, where arrows wait cross_window_s before moving.
    cross_window_s: float = 0.04
    cross_double_s: float = 0.4
    # Two-thumb typing on the on-screen keyboard (user, 2026-10-09): while the
    # Slate is open, the left stick steps the green selection and L3 types its
    # key; the right stick steps the red one and R3 types its key. A deflection
    # past board_threshold is one step; held, it repeats after board_delay_s
    # every board_repeat_s; below board_release it is let go.
    board_press: dict[str, int] = field(default_factory=lambda: {"BTN_THUMBL": 0, "BTN_THUMBR": 1})
    board_threshold: float = 0.5
    board_release: float = 0.35
    board_delay_s: float = 0.3
    board_repeat_s: float = 0.12
    # Per-app gamepad profiles (Step 9.3), keyed by the Wayland app_id Sway
    # reports: "keys" (default: this mapping), "pointer" (the same), or
    # "gamepad-raw": while that app has the focus the daemon releases its grab
    # and the app reads the gamepad itself; FN+B (close) and FN+Start held
    # (recovery, which also takes the gamepad back) still work.
    app_profiles: dict[str, str] = field(default_factory=dict)
    # Per-app key maps (Step 9.3): while that app has the focus, these buttons
    # send these keys instead of `keys` (e.g. Wolfenstein: R1 = Ctrl to fire).
    app_keys: dict[str, dict[str, str]] = field(default_factory=dict)
    # "gamepad-virtual" apps (Step 9.8b): the daemon keeps the real gamepad and
    # feeds the app a remapped joystick ("wyoh-game-pad"): these buttons press
    # these virtual button numbers (several buttons may share one), the sticks
    # pass through as analog axes, and app_keys still send keys.
    app_pad: dict[str, dict[str, int]] = field(default_factory=dict)
    # Generated by wyoh_apps.py from the apps' manifests; merged at start.
    app_profiles_file: str = ""
    raw_close: str = "BTN_SOUTH"  # with FN, in a gamepad-raw app
    menu: str = "BTN_START"
    next_window: str = "BTN_SELECT"
    modifier: str = "BTN_MODE"
    # FN + button -> Sway command
    fn_sway: dict[str, str] = field(default_factory=lambda: {
        "BTN_DPAD_UP": "focus up", "BTN_DPAD_DOWN": "focus down",
        "BTN_DPAD_LEFT": "focus left", "BTN_DPAD_RIGHT": "focus right",
        "BTN_EAST": "fullscreen toggle", "BTN_SOUTH": "kill",
        "BTN_TR": "workspace next", "BTN_TR2": "workspace prev",
    })
    recovery: tuple[str, str] = ("BTN_MODE", "BTN_START")
    recovery_hold_s: float = 2.0
    pointer: PointerConfig = PointerConfig()
    menu_command: str = ""
    # The Slate window; "{socket}" is replaced by the daemon's Slate socket.
    zone_command: tuple[str, ...] = ()
    # The on-screen keyboard, shown whenever the Slate is open (user, 2026-10-09).
    keyboard_command: tuple[str, ...] = ()
    # Sway commands run when the Slate opens and closes (the white border).
    zone_open_sway: str = ""
    zone_close_sway: str = ""
    # Run once the Slate has connected (its window exists): place it.
    zone_ready_sway: str = ""
    deliver_command: tuple[str, ...] = ("wtype", "-s", "100", "-d", "10", "--")
    deliver_key_delay_s: float = 0.004  # between key events when typing through uinput
    # Mycroft's dictation provider (Step 12), started by L2 in the Slate; it
    # writes ready/partial/final/error JSON lines and stops when stdin closes.
    dictate_command: tuple[str, ...] = ()
    # Open the Slate hidden as soon as the session starts (with a resident
    # provider, its model loads then), so the first L1 or L2 needs no wait.
    zone_preload: bool = False


ZONE_FN_OPS = {"clear", "validate", "mike", "mannie", "history-prev", "history-next"}


class ConfigError(ValueError):
    pass


def load_config(path: Path | None) -> Config:
    """Read `gamepad.toml`; refuse anything unknown rather than map partially."""
    if path is None:
        return Config()
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    base = Config()
    values: dict[str, Any] = {}
    allowed = set(Config.__dataclass_fields__) - {"pointer"}
    for key, value in data.items():
        if key == "pointer":
            unknown = set(value) - set(PointerConfig.__dataclass_fields__)
            if unknown:
                raise ConfigError(f"unknown pointer settings: {sorted(unknown)}")
            values["pointer"] = PointerConfig(**value)
        elif key in allowed:
            values[key] = tuple(value) if isinstance(getattr(base, key), tuple) else value
        else:
            raise ConfigError(f"unknown setting: {key}")
    config = Config(**{**base.__dict__, **values})
    if config.app_profiles_file and Path(config.app_profiles_file).is_file():
        generated = tomllib.loads(Path(config.app_profiles_file).read_text(encoding="utf-8"))
        unknown = set(generated) - {"app_profiles", "app_keys", "app_pad"}
        if unknown:
            raise ConfigError(f"{config.app_profiles_file}: unknown settings {sorted(unknown)}")
        merged = {**generated.get("app_profiles", {}), **config.app_profiles}  # the main file wins
        keys = {**generated.get("app_keys", {}), **config.app_keys}
        pad = {**generated.get("app_pad", {}), **config.app_pad}
        config = Config(**{**config.__dict__, "app_profiles": merged, "app_keys": keys, "app_pad": pad})
    _validate(config)
    return config


def _validate(config: Config) -> None:
    named = [config.click, config.zone_toggle, config.zone_dictate, *config.zone_fn, config.menu, config.next_window,
             config.modifier, *config.recovery, *config.keys, *config.zone_keys, *config.fn_sway]
    optional = [config.zone_validate, config.zone_validate_alt, config.zone_discard_alt]
    if set(config.zone_fn.values()) - ZONE_FN_OPS:
        raise ConfigError(f"zone_fn values must be among {sorted(ZONE_FN_OPS)}")
    for name in named + [name for name in optional if name] + list(config.board_press):
        if name not in BUTTONS:
            raise ConfigError(f"unknown button: {name}")
    if not (0 < config.cross_window_s < config.cross_double_s):
        raise ConfigError("need 0 < cross_window_s < cross_double_s")
    if set(config.app_profiles.values()) - {"keys", "pointer", "gamepad-raw", "gamepad-virtual"}:
        raise ConfigError("app_profiles values must be keys, pointer, gamepad-raw or gamepad-virtual")
    for app_id, mapping in config.app_pad.items():
        for name, index in mapping.items():
            if name not in BUTTONS or not (isinstance(index, int) and 0 <= index < PAD_BUTTONS):
                raise ConfigError(f"app_pad {app_id}: {name} = {index} (buttons 0-{PAD_BUTTONS - 1})")
    if config.raw_close not in BUTTONS:
        raise ConfigError(f"unknown button: {config.raw_close}")
    if not (0 < config.board_release < config.board_threshold <= 1 and config.board_delay_s > 0
            and config.board_repeat_s > 0) or set(config.board_press.values()) - {0, 1}:
        raise ConfigError("invalid board settings")
    for app_id, mapping in config.app_keys.items():
        for name in mapping:
            if name not in BUTTONS:
                raise ConfigError(f"app_keys {app_id}: unknown button: {name}")
    for chord in [*config.keys.values(), *config.zone_keys.values(),
                  *(chord for mapping in config.app_keys.values() for chord in mapping.values())]:
        for key in chord.split("+"):
            if key not in KEYS:
                raise ConfigError(f"unknown key: {key}")
    if config.pointer_stick not in ("left", "right"):
        raise ConfigError("pointer_stick must be left or right")
    if len(config.recovery) != 2:
        raise ConfigError("recovery needs exactly two buttons")
    p = config.pointer
    if not (0 <= p.dead_zone < 1 and p.max_speed > 0 and p.gamma > 0 and p.tick_hz > 0 and p.axis_max > 0):
        raise ConfigError("invalid pointer settings")


# --- Output actions (what the core asks the adapters to do) ------------------


@dataclass(frozen=True)
class Key:
    code: int
    down: bool


@dataclass(frozen=True)
class Click:
    button: int
    down: bool


@dataclass(frozen=True)
class Motion:
    dx: int
    dy: int


@dataclass(frozen=True)
class Sway:
    command: str


@dataclass(frozen=True)
class Zone:
    op: str  # open | hide | show | clear | validate | discard | dictate | select-word | select-line


@dataclass(frozen=True)
class Menu:
    pass


@dataclass(frozen=True)
class Grab:
    """Take (True) or release (False) the exclusive grab of the gamepads."""
    on: bool


@dataclass(frozen=True)
class PadButton:
    """A button of the virtual joystick fed to a gamepad-virtual app."""
    index: int
    down: bool


@dataclass(frozen=True)
class PadAxis:
    """A stick axis passed through to the virtual joystick (raw axis units)."""
    code: int
    value: int


@dataclass(frozen=True)
class Board:
    """A command for the on-screen keyboard's selection 0 (green) or 1 (red)."""
    cursor: int
    op: str  # "up" | "down" | "left" | "right" | "press"


@dataclass(frozen=True)
class Note:
    """A status-only event (no output), e.g. ignored button or recovery."""
    event: str


Action = Key | Click | Motion | Sway | Zone | Menu | Board | Grab | PadButton | PadAxis | Note


# --- Pointer curve -----------------------------------------------------------


def pointer_speed(x: float, y: float, cfg: PointerConfig) -> tuple[float, float]:
    """Velocity in px/s for a stick at (x, y) in raw axis units."""
    nx, ny = x / cfg.axis_max, y / cfg.axis_max
    r = math.hypot(nx, ny)
    if r <= cfg.dead_zone:
        return 0.0, 0.0
    r_capped = min(r, 1.0)
    speed = cfg.max_speed * ((r_capped - cfg.dead_zone) / (1.0 - cfg.dead_zone)) ** cfg.gamma
    return speed * nx / r, speed * ny / r


# --- Core state machine ------------------------------------------------------


class GamepadCore:
    """Pure mapping, input-zone, recovery, and pointer logic."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.code = {name: BUTTONS[name] for name in BUTTONS}
        self.held: set[int] = set()
        # gamepad button -> outputs it pressed and must release on button-up
        self.pressed_outputs: dict[int, list[Action]] = {}
        self.zone_state = "closed"  # closed | open | hidden | delivering
        self.axes = (ABS_X, ABS_Y) if config.pointer_stick == "left" else (ABS_RX, ABS_RY)
        self.stick = {axis: 0.0 for axis in (ABS_X, ABS_Y, ABS_RX, ABS_RY)}
        # on-screen keyboard selections: per stick, the held direction and next repeat
        self.board_sticks = {0: (ABS_X, ABS_Y), 1: (ABS_RX, ABS_RY)}
        self.board_dir: dict[int, str | None] = {0: None, 1: None}
        self.board_next: dict[int, float] = {0: 0.0, 1: 0.0}
        self.fraction = [0.0, 0.0]
        self.last_tick: float | None = None
        self.recovery_since: float | None = None
        self.counters = {"ignored": 0, "recovery": 0, "cross": 0}
        self.raw = False  # a gamepad-raw app has the focus; the grab is released
        self.active_keys = dict(config.keys)  # the focused app's key map (Step 9.3)
        self.app_keys_now: dict[str, str] = {}  # the focused app's own keys only
        self.pad: dict[str, int] | None = None  # gamepad-virtual mapping of the focused app
        self.last_action = ""
        # whole-cross detection (Slate only)
        self.dpad_pending: tuple[int, float] | None = None
        self.cross_held: set[int] = set()
        self.last_cross: float | None = None

    # helpers
    def _b(self, name: str) -> int:
        return self.code[name]

    def _keys(self, chord: str) -> list[int]:
        return [KEYS[k] for k in chord.split("+")]

    @property
    def fn_held(self) -> bool:
        return self._b(self.config.modifier) in self.held

    def _recovery_pair(self) -> tuple[int, int]:
        a, b = self.config.recovery
        return self._b(a), self._b(b)

    # focus (Step 9.3)
    def focus(self, app_id: str | None) -> list[Action]:
        """The focused window changed: apply its app's gamepad profile."""
        self.app_keys_now = dict(self.config.app_keys.get(app_id or "", {}))
        self.active_keys = {**self.config.keys, **self.app_keys_now}
        profile = self.config.app_profiles.get(app_id or "", "keys")
        pad = self.config.app_pad.get(app_id or "", {}) if profile == "gamepad-virtual" else None
        if pad != self.pad:
            released = self.release_all()  # nothing stays pressed across the switch
            self.pad = pad
            if pad is not None:
                return released + [Note(f"virtual:{app_id}")]
            return released
        raw = profile == "gamepad-raw"
        if raw == self.raw:
            return []
        if raw:
            actions = self.release_all()  # nothing stays pressed for the app behind
            self.raw = True
            return actions + [Grab(False), Note(f"raw:{app_id}")]
        self.raw = False
        self.held.clear()  # what was held belonged to the app
        return [Grab(True), Note("raw:off")]

    # events
    def button(self, code: int, pressed: bool, now: float) -> list[Action]:
        if self.raw:
            return self._button_raw(code, pressed, now)
        # The Slate is hidden, not closed, from session start (zone_preload): the
        # game keeps its joystick unless the Slate is actually on screen.
        if self.pad is not None and self.zone_state in ("closed", "hidden"):
            return self._button_virtual(code, pressed, now)
        if pressed:
            if code in self.held:
                return []  # autorepeat from the device; key repeat is Wayland's job
            self.held.add(code)
            actions = self._press(code, now)
            first, second = self._recovery_pair()
            if first in self.held and second in self.held and self.recovery_since is None:
                self.recovery_since = now
            return actions
        if code not in self.held:
            return []
        self.held.discard(code)
        if code in self._recovery_pair():
            self.recovery_since = None
        if code in self.cross_held:
            self.cross_held.discard(code)
            return []
        if self.dpad_pending is not None and self.dpad_pending[0] == code:
            # a short tap released inside the window: it was a plain arrow
            return self._flush_pending() + self._release(code)
        return self._release(code)

    def _button_raw(self, code: int, pressed: bool, now: float) -> list[Action]:
        """A gamepad-raw app reads the buttons itself; only FN+B and recovery are ours."""
        first, second = self._recovery_pair()
        if pressed:
            self.held.add(code)
            if first in self.held and second in self.held and self.recovery_since is None:
                self.recovery_since = now
            if self.fn_held and code == self._b(self.config.raw_close):
                result: list[Action] = [Sway("kill")]
                self._last(result)
                return result
            return []
        self.held.discard(code)
        if code in (first, second):
            self.recovery_since = None
        return []

    def _button_virtual(self, code: int, pressed: bool, now: float) -> list[Action]:
        """A gamepad-virtual app: mapped buttons press the virtual joystick, its own
        keys send keys; FN+B (close) and FN+Start held (recovery) stay Wyoh's."""
        assert self.pad is not None
        name = BUTTON_NAMES.get(code, "")
        first, second = self._recovery_pair()
        if not pressed:
            if code not in self.held:
                return []
            self.held.discard(code)
            if code in (first, second):
                self.recovery_since = None
            return self._release(code)
        if code in self.held:
            return []
        self.held.add(code)
        if first in self.held and second in self.held and self.recovery_since is None:
            self.recovery_since = now
        if code == self._b(self.config.modifier):
            return []
        if self.fn_held:
            if code == self._b(self.config.raw_close):
                result: list[Action] = [Sway("kill")]
                self._last(result)
                return result
            return []
        if name in self.pad:
            outputs: list[Action] = [PadButton(self.pad[name], True)]
        elif name in self.app_keys_now:
            outputs = [Key(k, True) for k in self._keys(self.app_keys_now[name])]
        else:
            return []
        self.pressed_outputs[code] = outputs
        self._last(outputs)
        return list(outputs)

    def _zone_outputs(self, code: int) -> list[Action]:
        return [Key(k, True) for k in self._keys(self.config.zone_keys[BUTTON_NAMES[code]])]

    def _flush_pending(self) -> list[Action]:
        """Send the arrow that was waiting to see whether the whole cross was pressed."""
        if self.dpad_pending is None:
            return []
        code, _ = self.dpad_pending
        self.dpad_pending = None
        outputs = self._zone_outputs(code)
        self.pressed_outputs[code] = outputs
        return list(outputs)

    def _clear_cross(self) -> None:
        self.dpad_pending = None
        self.cross_held.clear()
        self.last_cross = None
        self._board_reset()

    def _dpad_in_zone(self, code: int, now: float) -> list[Action]:
        if self.cross_held:  # more contacts of the same whole-cross press
            self.cross_held.add(code)
            return []
        if self.dpad_pending is not None:
            first, _ = self.dpad_pending
            self.dpad_pending = None
            self.cross_held = {first, code}
            double = self.last_cross is not None and now - self.last_cross <= self.config.cross_double_s
            self.last_cross = None if double else now
            self.counters["cross"] += 1
            return [Zone("select-line" if double else "select-word")]
        self.dpad_pending = (code, now)
        return []

    def _press(self, code: int, now: float = 0.0) -> list[Action]:
        cfg, name = self.config, BUTTON_NAMES.get(code, "")
        outputs: list[Action] = []
        result: list[Action] = []
        if code == self._b(cfg.modifier):
            return []
        if self.fn_held:
            if code == self._b(cfg.recovery[1]) or code == self._b(cfg.recovery[0]):
                return []  # recovery is decided by the hold timer
            if self.zone_state == "open" and name in cfg.zone_fn:
                flushed = self._flush_pending()
                if cfg.zone_fn[name] == "validate":
                    self.zone_state = "delivering"
                    self._clear_cross()
                    result = flushed + [Zone("validate")]
                else:  # mannie: the daemon decides, since only it knows whether Mannie is open
                    result = flushed + [Zone(cfg.zone_fn[name])]
            elif name in cfg.fn_sway and self.zone_state in ("closed", "hidden"):
                result = [Sway(cfg.fn_sway[name])]
            else:
                result = [Note(f"ignored:{name or code}")]
                self.counters["ignored"] += 1
            self._last(result)
            return result
        if self.zone_state == "open":
            validate = {self._b(n) for n in (cfg.zone_validate, cfg.zone_validate_alt) if n}
            discard = {self._b(cfg.zone_discard_alt)} if cfg.zone_discard_alt else set()
            if code in DPAD and name in cfg.zone_keys:
                result = self._dpad_in_zone(code, now)
                self._last(result)
                return result
            flushed = self._flush_pending()
            if code in validate:
                self.zone_state = "delivering"
                self._clear_cross()
                result = flushed + [Zone("validate")]
            elif code == self._b(cfg.zone_toggle):
                self.zone_state = "hidden"
                self._clear_cross()
                result = flushed + [Zone("hide")]
            elif code == self._b(cfg.zone_dictate):
                result = flushed + [Zone("dictate")]
            elif code in discard:
                self.zone_state = "closed"
                self._clear_cross()
                result = flushed + [Zone("discard")]
            elif name in cfg.zone_keys:
                outputs = self._zone_outputs(code)
                self.pressed_outputs[code] = outputs
                result = flushed + outputs
                self._last(result)
                return result
            elif name in cfg.board_press:
                result = flushed + [Board(cfg.board_press[name], "press")]
            elif code == self._b(cfg.click):
                outputs = [Click(BTN_LEFT, True)]
                result = flushed
            else:
                result = flushed + [Note(f"ignored:{name or code}")]
                self.counters["ignored"] += 1
        elif self.zone_state == "delivering":
            if name in cfg.keys or code == self._b(cfg.click):
                result = [Note(f"busy:{name or code}")]
            else:
                result = [Note(f"busy:{name or code}")]
        else:  # closed, or hidden (the Slate keeps its text out of sight)
            if code == self._b(cfg.zone_toggle):
                result = [Zone("show" if self.zone_state == "hidden" else "open")]
                self.zone_state = "open"
            elif code == self._b(cfg.menu):
                result = [Menu()]
            elif code == self._b(cfg.next_window):
                result = [Sway("focus next")]
            elif name in self.active_keys:
                outputs = [Key(k, True) for k in self._keys(self.active_keys[name])]
            elif code == self._b(cfg.zone_dictate):  # L2: the Slate, straight into dictation (2026-10-15)
                result = [Zone("show" if self.zone_state == "hidden" else "open"), Zone("dictate")]
                self.zone_state = "open"
            elif code == self._b(cfg.click):
                outputs = [Click(BTN_LEFT, True)]
            else:
                result = [Note(f"ignored:{name or code}")]
                self.counters["ignored"] += 1
        if outputs:
            self.pressed_outputs[code] = outputs
            result = result + outputs if self.zone_state == "open" else outputs
        self._last(result)
        return result

    def _release(self, code: int) -> list[Action]:
        outputs = self.pressed_outputs.pop(code, [])
        released: list[Action] = []
        for action in reversed(outputs):
            if isinstance(action, Key):
                released.append(Key(action.code, False))
            elif isinstance(action, Click):
                released.append(Click(action.button, False))
            elif isinstance(action, PadButton):
                released.append(PadButton(action.index, False))
        return released

    def axis(self, code: int, value: int, now: float = 0.0) -> list[Action]:
        if code not in self.stick or self.raw:
            return []
        if self.pad is not None and self.zone_state in ("closed", "hidden"):
            return [PadAxis(code, value)]  # both sticks go to the game as they are
        self.stick[code] = float(value)
        if self.zone_state != "open":
            return []  # sticks drive the pointer (one of them) outside the Slate
        for cursor, (ax, ay) in self.board_sticks.items():
            if code in (ax, ay):
                return self._board_stick(cursor, now)
        return []

    def _board_direction(self, cursor: int) -> str | None:
        ax, ay = self.board_sticks[cursor]
        nx, ny = self.stick[ax] / self.config.pointer.axis_max, self.stick[ay] / self.config.pointer.axis_max
        r = math.hypot(nx, ny)
        held = self.board_dir[cursor]
        if r < (self.config.board_release if held else self.config.board_threshold):
            return None
        if r < self.config.board_threshold:
            return held  # between release and threshold: keep the held direction
        if abs(nx) >= abs(ny):
            return "right" if nx > 0 else "left"
        return "down" if ny > 0 else "up"

    def _board_stick(self, cursor: int, now: float) -> list[Action]:
        direction = self._board_direction(cursor)
        if direction == self.board_dir[cursor]:
            return []
        self.board_dir[cursor] = direction
        if direction is None:
            return []
        self.board_next[cursor] = now + self.config.board_delay_s
        result = [Board(cursor, direction)]
        self._last(result)
        return result

    def _board_reset(self) -> None:
        self.board_dir = {0: None, 1: None}

    def needs_tick(self) -> bool:
        x, y = (self.stick[axis] for axis in self.axes)
        pointer = (self.zone_state != "open" and self.pad is None
                   and pointer_speed(x, y, self.config.pointer) != (0.0, 0.0))
        board = self.zone_state == "open" and any(self.board_dir.values())
        return pointer or board or self.recovery_since is not None or self.dpad_pending is not None

    def tick(self, now: float) -> list[Action]:
        actions: list[Action] = []
        if self.dpad_pending is not None and now - self.dpad_pending[1] >= self.config.cross_window_s:
            actions += self._flush_pending()
        if self.recovery_since is not None and now - self.recovery_since >= self.config.recovery_hold_s:
            actions += self.recover()
            self.recovery_since = None
        if self.zone_state == "open":
            for cursor, direction in self.board_dir.items():
                if direction and now >= self.board_next[cursor]:
                    actions.append(Board(cursor, direction))
                    self.board_next[cursor] = max(self.board_next[cursor] + self.config.board_repeat_s, now)
            self.last_tick = None
            return actions  # no pointer while the Slate is open
        if self.pad is not None:
            return actions  # the sticks belong to the game
        vx, vy = pointer_speed(*(self.stick[axis] for axis in self.axes), self.config.pointer)
        if (vx, vy) == (0.0, 0.0):
            self.last_tick = None
            self.fraction = [0.0, 0.0]
            return actions
        dt = 1.0 / self.config.pointer.tick_hz if self.last_tick is None else min(now - self.last_tick, 0.1)
        self.last_tick = now
        self.fraction[0] += vx * dt
        self.fraction[1] += vy * dt
        dx, dy = int(self.fraction[0]), int(self.fraction[1])
        self.fraction[0] -= dx
        self.fraction[1] -= dy
        if dx or dy:
            actions.append(Motion(dx, dy))
        return actions

    def recover(self) -> list[Action]:
        """Release every output held, discard the zone, record the event."""
        actions: list[Action] = []
        for code in list(self.pressed_outputs):
            actions += self._release(code)
        if self.zone_state != "closed":
            actions.append(Zone("discard"))
            self.zone_state = "closed"
        self._clear_cross()
        if self.raw:  # recovery always takes the gamepad back
            self.raw = False
            actions.append(Grab(True))
        self.counters["recovery"] += 1
        actions.append(Note("recovery"))
        self._last(actions)
        return actions

    def zone_finished(self) -> None:
        """The adapter reports the zone closed (delivered, discarded, or failed)."""
        self.zone_state = "closed"
        self._clear_cross()

    def release_all(self) -> list[Action]:
        actions: list[Action] = []
        for code in list(self.pressed_outputs):
            actions += self._release(code)
        self.held.clear()
        self.stick = {axis: 0.0 for axis in self.stick}
        self.recovery_since = None
        self._clear_cross()
        return actions

    def _last(self, actions: list[Action]) -> None:
        if actions:
            self.last_action = type(actions[0]).__name__.lower() + (
                f":{getattr(actions[0], 'op', '') or getattr(actions[0], 'command', '') or getattr(actions[0], 'event', '')}"
            ).rstrip(":")


# --- Dictation (Step 12): Mycroft's lines -> Slate operations -------------------


def choose_capture(snd: Path = Path("/dev/snd"), asound: Path = Path("/proc/asound")) -> str | None:
    """The capture device for dictation: a USB microphone when one is plugged in
    (its card has a `usbid` file), otherwise the first capture device; None if
    there is none. Luna's jack gave no microphone signal (user test 2026-10-11)."""
    devices = sorted(snd.glob("pcmC*D*c"), key=lambda d: d.name)
    def card(device: Path) -> str:
        return device.name[4:].split("D", 1)[0]
    usb = [d for d in devices if (asound / f"card{card(d)}" / "usbid").exists()]
    chosen = (usb or devices or [None])[0]
    return str(chosen) if chosen is not None else None


def split_lines(buffer: bytes) -> tuple[list[dict[str, Any]], bytes]:
    """Complete JSON lines from `buffer`, and the incomplete rest. Bad lines are skipped."""
    messages: list[dict[str, Any]] = []
    while b"\n" in buffer:
        line, buffer = buffer.split(b"\n", 1)
        try:
            message = json.loads(line)
        except ValueError:
            continue
        if isinstance(message, dict):
            messages.append(message)
    return messages, buffer


def slate_operations(message: dict[str, Any]) -> list[dict[str, Any]]:
    """What the Slate must do for one message of Mycroft's dictation protocol
    (worklines/mycroft/docs/0704_01): ready -> listening; partial -> provisional
    text; final -> insert it; error -> show it."""
    op = message.get("op")
    if op == "ready":
        return [{"op": "dictation", "state": "listening"}]
    if op == "partial":
        return [{"op": "provisional", "text": str(message.get("text", ""))}]
    if op == "final":
        return [{"op": "insert", "text": str(message.get("text", ""))}]
    if op == "error":
        return [{"op": "provisional", "text": ""},
                {"op": "dictation", "state": f"error: {message.get('message', 'unknown')}"[:120]}]
    return []


# --- Slate destinations and history (user, 2026-10-15) -------------------------

HISTORY_PATH = Path("/storage/.local/state/tanstfaafllm/wyoh/slate-history.jsonl")
HISTORY_LIMIT = 50
HISTORY_SKIP_APPS = {"wyoh-wifi"}  # Wi-Fi passwords are never kept


def find_app_con(tree: dict[str, Any], app_id: str) -> int | None:
    """The first window with this Wayland app_id in a Sway tree."""
    if tree.get("app_id") == app_id and tree.get("type") in ("con", "floating_con"):
        return tree["id"]
    for child in tree.get("nodes", []) + tree.get("floating_nodes", []):
        found = find_app_con(child, app_id)
        if found is not None:
            return found
    return None


def con_app_id(tree: dict[str, Any], con_id: int) -> str | None:
    if tree.get("id") == con_id:
        return tree.get("app_id")
    for child in tree.get("nodes", []) + tree.get("floating_nodes", []):
        found = con_app_id(child, con_id)
        if found is not None:
            return found
    return None


def load_history(path: Path) -> list[str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    items = []
    for line in lines:
        try:
            item = json.loads(line)
        except ValueError:
            continue
        if isinstance(item, str) and item:
            items.append(item)
    return items[-HISTORY_LIMIT:]


def remember(path: Path, items: list[str], text: str, app_id: str | None) -> list[str]:
    """Add a sent text (not a repeat of the last one, nor one sent to a skipped
    app) and rewrite the file, mode 600, keeping the last HISTORY_LIMIT."""
    if not text or app_id in HISTORY_SKIP_APPS or (items and items[-1] == text):
        return items
    items = (items + [text])[-HISTORY_LIMIT:]
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w", encoding="utf-8") as handle:
        handle.writelines(json.dumps(item, ensure_ascii=False) + "\n" for item in items)
    os.replace(temporary, path)
    return items


class ResidentDictation:
    """Wyoh's side of Mycroft's resident provider (Step 12.4, Mycroft's reply in
    worklines/mycroft/docs/0903_03): the model loads once, when the Slate first
    opens, and stays loaded while the Slate is hidden or closed; L2 sends
    `start` and `stop`. Pure: each call returns what to send to the provider
    ("launch" means start its process; anything else is a stdin `op`) and the
    operations for the Slate."""

    def __init__(self) -> None:
        self.state = "off"  # off | loading | idle | listening | stopping
        self.pending = False  # L2 pressed while loading: start once ready

    @staticmethod
    def _show(state: str) -> dict[str, Any]:
        return {"op": "dictation", "state": state}

    def preload(self) -> tuple[list[str], list[dict[str, Any]]]:
        """The Slate opens: load the model in the background, silently."""
        if self.state != "off":
            return [], []
        self.state, self.pending = "loading", False
        return ["launch"], []

    def toggle(self) -> tuple[list[str], list[dict[str, Any]]]:
        """L2 in the Slate."""
        if self.state == "off":
            self.state, self.pending = "loading", True
            return ["launch"], [self._show("loading")]
        if self.state == "loading":
            self.pending = not self.pending
            return [], [self._show("loading" if self.pending else "")]
        if self.state == "idle":
            self.state = "listening"
            return ["start"], [self._show("listening")]
        if self.state == "listening":
            self.state = "stopping"
            return ["stop"], [self._show("stopping")]
        return [], []

    def interrupt(self) -> tuple[list[str], list[dict[str, Any]]]:
        """A key edits the Slate, or it is hidden or closed: end the utterance
        (its text is still inserted), and forget a start waiting for the model."""
        if self.state == "loading" and self.pending:
            self.pending = False
            return [], [self._show("")]
        if self.state == "listening":
            self.state = "stopping"
            return ["stop"], [self._show("stopping")]
        return [], []

    def message(self, message: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]]]:
        """One JSON line from the provider."""
        op = message.get("op")
        if op == "ready":
            self.state = "idle"
            if self.pending:
                self.state, self.pending = "listening", False
                return ["start"], [self._show("listening")]
            return [], []
        if op == "listening":
            return [], [self._show("listening")] if self.state == "listening" else []
        if op == "partial" and self.state in ("listening", "stopping"):
            return [], [{"op": "provisional", "text": str(message.get("text", ""))}]
        if op == "final":
            if self.state != "off":
                self.state = "idle"
            return [], [{"op": "insert", "text": str(message.get("text", ""))}, self._show("")]
        if op == "error":
            if self.state == "loading":  # before ready: the provider exits
                self.state, self.pending = "off", False
            elif self.state != "off":
                self.state = "idle"  # during an utterance: the model is kept
            return [], [{"op": "provisional", "text": ""},
                        self._show(f"error: {message.get('message', 'unknown')}"[:120])]
        return [], []

    def exited(self) -> tuple[list[str], list[dict[str, Any]]]:
        """The provider's process ended (crash, or an error before ready)."""
        was, self.state, self.pending = self.state, "off", False
        return [], [] if was == "off" else [self._show("")]


# --- Adapters ----------------------------------------------------------------

EVENT_FORMAT = "llHHi"
EVENT_SIZE = struct.calcsize(EVENT_FORMAT)
EVIOCGRAB = 0x40044590
UI_SET_EVBIT, UI_SET_KEYBIT, UI_SET_RELBIT = 0x40045564, 0x40045565, 0x40045566
UI_DEV_SETUP, UI_DEV_CREATE, UI_DEV_DESTROY = 0x405C5503, 0x5501, 0x5502
BUS_VIRTUAL, VENDOR = 0x06, 0x1209
KEYBOARD_NAME, MOUSE_NAME = "wyoh-gamepad-keyboard", "wyoh-gamepad-mouse"
RUNTIME_DIR = Path("/run/wyoh")
STATUS_PATH = RUNTIME_DIR / "gamepad.json"
SLATE_SOCKET = RUNTIME_DIR / "slate.sock"
DESCRIPTOR = Path.home() / ".local/state/tanstfaafllm/wyoh/sway-vnc-session.json"


def find_devices(names: tuple[str, ...]) -> dict[str, str]:
    """Map event-device path -> name for input devices whose name is in `names`."""
    found: dict[str, str] = {}
    name = ""
    for line in Path("/proc/bus/input/devices").read_text(encoding="utf-8").splitlines():
        if line.startswith("N: Name="):
            name = line.split("=", 1)[1].strip().strip('"')
        elif line.startswith("H: Handlers=") and name in names:
            for handler in line.split("=", 1)[1].split():
                if handler.startswith("event"):
                    found[f"/dev/input/{handler}"] = name
    return found


class UInputDevice:
    def __init__(self, name: str, product: int, keys: list[int], rel: bool) -> None:
        self.fd = os.open("/dev/uinput", os.O_WRONLY | os.O_NONBLOCK)
        fcntl.ioctl(self.fd, UI_SET_EVBIT, EV_KEY)
        for code in keys:
            fcntl.ioctl(self.fd, UI_SET_KEYBIT, code)
        if rel:
            fcntl.ioctl(self.fd, UI_SET_EVBIT, EV_REL)
            fcntl.ioctl(self.fd, UI_SET_RELBIT, REL_X)
            fcntl.ioctl(self.fd, UI_SET_RELBIT, REL_Y)
        fcntl.ioctl(self.fd, UI_DEV_SETUP, struct.pack("HHHH80sI", BUS_VIRTUAL, VENDOR, product, 1, name.encode(), 0))
        fcntl.ioctl(self.fd, UI_DEV_CREATE)

    def emit(self, events: list[tuple[int, int, int]]) -> None:
        for kind, code, value in events:
            os.write(self.fd, struct.pack(EVENT_FORMAT, 0, 0, kind, code, value))
        os.write(self.fd, struct.pack(EVENT_FORMAT, 0, 0, EV_SYN, SYN_REPORT, 0))

    def close(self) -> None:
        try:
            fcntl.ioctl(self.fd, UI_DEV_DESTROY)
        finally:
            os.close(self.fd)


UI_SET_ABSBIT, UI_ABS_SETUP = 0x40045567, 0x401C5504
PAD_NAME = "wyoh-game-pad"


class UInputPad:
    """The virtual joystick for gamepad-virtual apps: buttons 0x130..0x13F
    (SDL numbers them 0..15) and the two sticks as analog axes."""

    def __init__(self, axis_max: int) -> None:
        self.fd = os.open("/dev/uinput", os.O_WRONLY | os.O_NONBLOCK)
        fcntl.ioctl(self.fd, UI_SET_EVBIT, EV_KEY)
        for index in range(PAD_BUTTONS):
            fcntl.ioctl(self.fd, UI_SET_KEYBIT, 0x130 + index)
        fcntl.ioctl(self.fd, UI_SET_EVBIT, EV_ABS)
        for code in (ABS_X, ABS_Y, ABS_RX, ABS_RY):
            fcntl.ioctl(self.fd, UI_SET_ABSBIT, code)
            fcntl.ioctl(self.fd, UI_ABS_SETUP, struct.pack("Hxx6i", code, 0, -axis_max, axis_max, 0, 0, 0))
        fcntl.ioctl(self.fd, UI_DEV_SETUP, struct.pack("HHHH80sI", BUS_VIRTUAL, VENDOR, 0x0012, 1, PAD_NAME.encode(), 0))
        fcntl.ioctl(self.fd, UI_DEV_CREATE)

    def emit(self, kind: int, code: int, value: int) -> None:
        os.write(self.fd, struct.pack(EVENT_FORMAT, 0, 0, kind, code, value))
        os.write(self.fd, struct.pack(EVENT_FORMAT, 0, 0, EV_SYN, SYN_REPORT, 0))

    def close(self) -> None:
        try:
            fcntl.ioctl(self.fd, UI_DEV_DESTROY)
        finally:
            os.close(self.fd)


class SwayClient:
    """Minimal Sway IPC client (RUN_COMMAND, GET_TREE) on the session's socket."""

    MAGIC = b"i3-ipc"

    def __init__(self, descriptor: Path = DESCRIPTOR) -> None:
        self.descriptor = descriptor

    def _socket_path(self) -> str | None:
        try:
            return json.loads(self.descriptor.read_text(encoding="utf-8"))["sway_socket"]
        except (OSError, KeyError, ValueError):
            return None

    def wayland_display(self) -> str | None:
        try:
            return json.loads(self.descriptor.read_text(encoding="utf-8"))["wayland_display"]
        except (OSError, KeyError, ValueError):
            return None

    def request(self, message_type: int, payload: str = "") -> Any:
        path = self._socket_path()
        if not path:
            raise ConnectionError("no Sway session descriptor")
        body = payload.encode()
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
            sock.settimeout(2.0)
            sock.connect(path)
            sock.sendall(self.MAGIC + struct.pack("=II", len(body), message_type) + body)
            header = self._recv(sock, len(self.MAGIC) + 8)
            length, _ = struct.unpack("=II", header[len(self.MAGIC):])
            return json.loads(self._recv(sock, length))

    @staticmethod
    def _recv(sock: socket.socket, size: int) -> bytes:
        data = b""
        while len(data) < size:
            chunk = sock.recv(size - len(data))
            if not chunk:
                raise ConnectionError("Sway closed the IPC socket")
            data += chunk
        return data

    def command(self, text: str) -> bool:
        replies = self.request(0, text)
        return all(reply.get("success") for reply in replies)

    def focused_con_id(self) -> int | None:
        def walk(node: dict[str, Any]) -> int | None:
            if node.get("focused") and node.get("type") in ("con", "floating_con"):
                return node["id"]
            for child in node.get("nodes", []) + node.get("floating_nodes", []):
                found = walk(child)
                if found is not None:
                    return found
            return None
        return walk(self.request(4))

    def con_exists(self, con_id: int) -> bool:
        def walk(node: dict[str, Any]) -> bool:
            return node.get("id") == con_id or any(
                walk(child) for child in node.get("nodes", []) + node.get("floating_nodes", []))
        return walk(self.request(4))


class Daemon:
    """Runs the core against real devices; owns the zone and menu processes."""

    def __init__(self, config: Config, sway: SwayClient | None = None) -> None:
        self.config = config
        self.core = GamepadCore(config)
        self.sway = sway or SwayClient()
        self.inputs: dict[str, int] = {}  # path -> fd
        self.keyboard = UInputDevice(KEYBOARD_NAME, 0x0010, sorted({*KEYS.values(), *PHYSICAL.values()}), rel=False)
        self.mouse = UInputDevice(MOUSE_NAME, 0x0011, [BTN_LEFT, BTN_LEFT + 1], rel=True)
        # created at start, before any game opens its joysticks (they enumerate at launch)
        self.pad = UInputPad(int(config.pointer.axis_max)) if config.app_pad else None
        self.zone: subprocess.Popen[bytes] | None = None  # the Slate's terminal
        self.zone_keyboard: subprocess.Popen[bytes] | None = None
        self.zone_link: socket.socket | None = None
        self.zone_inbox = b""
        self.zone_target: int | None = None
        self.menu: subprocess.Popen[bytes] | None = None
        RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
        SLATE_SOCKET.unlink(missing_ok=True)
        self.zone_listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.zone_listener.bind(str(SLATE_SOCKET))
        os.chmod(SLATE_SOCKET, 0o600)
        self.zone_listener.listen(1)
        self.state = {"zone_result": "", "error": "", "deliveries": 0, "discards": 0, "delivered_length": 0}
        self.grabbed = config.grab
        self.focus_events: socket.socket | None = None
        self.dictation: subprocess.Popen[bytes] | None = None
        self.dictation_buffer = b""
        self.history = load_history(HISTORY_PATH)
        self.zone_submit = False  # Mannie: one prompt, lines joined
        self.preload_pending = config.zone_preload or "--resident" in config.dictate_command
        self.zone_start_hidden = False
        # Mycroft's resident mode (Step 12.4) when the command asks for it.
        self.resident = ResidentDictation() if "--resident" in config.dictate_command else None
        if config.zone_close_sway:  # a previous run may have died with the Slate open
            try:
                self.sway.command(config.zone_close_sway)
            except (OSError, ConnectionError):
                pass

    # devices
    def rescan(self) -> None:
        for path, name in find_devices(self.config.devices).items():
            if path in self.inputs:
                continue
            try:
                fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
                if self.config.grab and self.grabbed:
                    fcntl.ioctl(fd, EVIOCGRAB, 1)
                self.inputs[path] = fd
                self._log(f"attached {name} at {path}")
                self.write_status()
            except OSError as error:
                self._log(f"cannot attach {path}: {error}")

    def set_grab(self, on: bool) -> None:
        """Take or release the exclusive grab; the daemon keeps reading either way."""
        if not self.config.grab:
            return
        self.grabbed = on
        for path, fd in self.inputs.items():
            try:
                fcntl.ioctl(fd, EVIOCGRAB, 1 if on else 0)
            except OSError as error:
                self._log(f"grab {on} on {path}: {error}")

    # focus events (Step 9.3)
    def subscribe_focus(self) -> None:
        """Follow window focus to apply per-app profiles (only if any are configured)."""
        if not (self.config.app_profiles or self.config.app_keys or self.config.app_pad) or self.focus_events is not None:
            return
        try:
            path = self.sway._socket_path()
            if not path:
                return
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(path)
            body = json.dumps(["window"]).encode()
            sock.sendall(SwayClient.MAGIC + struct.pack("=II", len(body), 2) + body)
            header = SwayClient._recv(sock, len(SwayClient.MAGIC) + 8)
            length, _ = struct.unpack("=II", header[len(SwayClient.MAGIC):])
            SwayClient._recv(sock, length)
            self.focus_events = sock
            self.apply(self.core.focus(self.focused_app_id()))
        except (OSError, ConnectionError) as error:
            self._log(f"focus subscription: {error}")

    def focused_app_id(self) -> str | None:
        def walk(node: dict[str, Any]) -> str | None:
            if node.get("focused") and node.get("type") in ("con", "floating_con"):
                return node.get("app_id") or (node.get("window_properties") or {}).get("class")
            for child in node.get("nodes", []) + node.get("floating_nodes", []):
                found = walk(child)
                if found is not None:
                    return found
            return None
        return walk(self.sway.request(4))

    def focus_event(self) -> None:
        assert self.focus_events is not None
        try:
            header = SwayClient._recv(self.focus_events, len(SwayClient.MAGIC) + 8)
            length, _ = struct.unpack("=II", header[len(SwayClient.MAGIC):])
            event = json.loads(SwayClient._recv(self.focus_events, length))
        except (OSError, ConnectionError, ValueError):
            self.focus_events.close()
            self.focus_events = None  # resubscribed at the next device scan
            self.apply(self.core.focus(None))
            return
        if event.get("change") in ("focus", "close"):
            try:
                app_id = self.focused_app_id()
            except (OSError, ConnectionError):
                app_id = None
            self.apply(self.core.focus(app_id))

    def detach(self, path: str) -> None:
        fd = self.inputs.pop(path)
        os.close(fd)  # closing releases the grab
        self.apply(self.core.release_all())
        self._log(f"detached {path}")
        self.write_status()

    def read(self, path: str, now: float) -> None:
        fd = self.inputs[path]
        try:
            data = os.read(fd, EVENT_SIZE * 64)
        except BlockingIOError:
            return
        except OSError:
            self.detach(path)
            return
        for offset in range(0, len(data) - EVENT_SIZE + 1, EVENT_SIZE):
            _, _, kind, code, value = struct.unpack_from(EVENT_FORMAT, data, offset)
            if kind == EV_KEY and value in (0, 1):
                self.apply(self.core.button(code, value == 1, now))
            elif kind == EV_ABS:
                self.apply(self.core.axis(code, value, now))

    # actions
    def apply(self, actions: list[Action]) -> None:
        for action in actions:
            try:
                self._apply(action)
            except (OSError, ConnectionError, subprocess.SubprocessError) as error:
                self.state["error"] = f"{type(action).__name__}: {error}"
                self._log(self.state["error"])
        # Pointer motion alone is not a state change worth a status write
        # (it ran at the tick rate and cost most of the daemon's CPU).
        if any(not isinstance(action, (Motion, PadAxis)) for action in actions):
            self.write_status()

    def _apply(self, action: Action) -> None:
        if isinstance(action, Key):
            self.keyboard.emit([(EV_KEY, action.code, 1 if action.down else 0)])
        elif isinstance(action, Click):
            self.mouse.emit([(EV_KEY, action.button, 1 if action.down else 0)])
        elif isinstance(action, Motion):
            self.mouse.emit([(EV_REL, REL_X, action.dx), (EV_REL, REL_Y, action.dy)])
        elif isinstance(action, Sway):
            self.sway.command(action.command)
        elif isinstance(action, Menu):
            self.toggle_menu()
        elif isinstance(action, Board):
            self.tell_board(action)
        elif isinstance(action, Grab):
            self.set_grab(action.on)
        elif isinstance(action, PadButton):
            if self.pad is not None:
                self.pad.emit(EV_KEY, 0x130 + action.index, 1 if action.down else 0)
        elif isinstance(action, PadAxis):
            if self.pad is not None:
                self.pad.emit(EV_ABS, action.code, action.value)
        elif isinstance(action, Zone):
            {"open": self.open_zone, "validate": self.validate_zone, "discard": self.discard_zone,
             "hide": self.hide_zone, "show": self.show_zone, "clear": lambda: self.tell_zone("clear"),
             "dictate": self.dictate_zone,
             "mike": lambda: self.tell_slate({"op": "notice", "text": "Mike is not on Luna yet; text kept"}),
             "mannie": self.mannie_zone,
             "history-prev": lambda: self.tell_zone("history-prev"),
             "history-next": lambda: self.tell_zone("history-next"),
             "select-word": lambda: self.tell_zone("select-word"),
             "select-line": lambda: self.tell_zone("select-line")}[action.op]()

    def tap(self, code: int) -> None:
        self.keyboard.emit([(EV_KEY, code, 1)])
        self.keyboard.emit([(EV_KEY, code, 0)])

    def _env(self) -> dict[str, str]:
        env = dict(os.environ)
        display = self.sway.wayland_display()
        if display:
            env["WAYLAND_DISPLAY"] = display
        return env

    # menu
    def toggle_menu(self) -> None:
        if self.menu is not None and self.menu.poll() is None:
            self.tap(KEYS["KEY_ESC"])
            return
        if self.config.menu_command:
            self.menu = subprocess.Popen(self.config.menu_command, shell=True, env=self._env(),
                                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # zone (the Slate)
    def open_zone(self) -> None:
        if not self.config.zone_command:
            raise subprocess.SubprocessError("no Slate command configured")
        try:
            self.zone_target = self.sway.focused_con_id()
        except (OSError, ConnectionError) as error:
            self.core.zone_finished()
            self.state["zone_result"] = "no-sway"
            raise ConnectionError(f"the Slate needs Sway: {error}") from error
        command = [part.replace("{socket}", str(SLATE_SOCKET)) for part in self.config.zone_command]
        quiet = {"stdin": subprocess.DEVNULL, "stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
        try:
            if self.config.zone_open_sway:
                self.sway.command(self.config.zone_open_sway)
            self.zone = subprocess.Popen(command, env=self._env(), **quiet)
            if self.config.keyboard_command:
                self.zone_keyboard = subprocess.Popen(list(self.config.keyboard_command), env=self._env(),
                                                      **{**quiet, "stdin": subprocess.PIPE})
        except (OSError, ConnectionError):
            self.finish_zone("failed")
            raise
        self.state["zone_result"] = "open"
        if self.resident is not None:  # first opening: load the model now, not at the first L2
            self.resident_do(self.resident.preload())

    def hide_zone(self) -> None:
        """L1 while open: the Slate keeps its text in Sway's scratchpad; the keyboard hides."""
        if self.zone is None or self.zone.poll() is not None:
            self.finish_zone("discarded")
            return
        self.stop_dictation()
        self.sway.command('[app_id="wyoh-slate"] move scratchpad')
        if self.zone_keyboard is not None and self.zone_keyboard.poll() is None:
            self.zone_keyboard.send_signal(signal.SIGUSR1)  # wvkbd: hide
        if self.config.zone_close_sway:
            self.sway.command(self.config.zone_close_sway)
        self.state["zone_result"] = "hidden"

    def show_zone(self) -> None:
        """L1 while hidden: show the same Slate again, for the window focused now."""
        if self.zone is None or self.zone.poll() is not None:
            self.finish_zone("discarded")
            self.core.zone_state = "open"
            self.open_zone()
            return
        try:
            self.zone_target = self.sway.focused_con_id()
        except (OSError, ConnectionError):
            self.zone_target = None
        if self.config.zone_open_sway:
            self.sway.command(self.config.zone_open_sway)
        self.sway.command('[app_id="wyoh-slate"] scratchpad show')
        if self.config.zone_ready_sway:
            self.sway.command(self.config.zone_ready_sway)
        if self.zone_keyboard is not None and self.zone_keyboard.poll() is None:
            self.zone_keyboard.send_signal(signal.SIGUSR2)  # wvkbd: show
        self.state["zone_result"] = "open"

    def tell_slate(self, message: dict[str, Any]) -> None:
        if self.zone_link is not None:
            try:
                self.zone_link.sendall(json.dumps(message, ensure_ascii=False).encode() + b"\n")
            except OSError:
                pass

    def dictate_zone(self) -> None:
        """L2 in the Slate: start Mycroft's dictation, or stop it (Step 12)."""
        if self.resident is not None:
            self.resident_do(self.resident.toggle())
            return
        if self.dictation is not None:
            self.stop_dictation()
            return
        if self.launch_provider():
            self.state["dictation"] = "loading"
            self.tell_slate({"op": "dictation", "state": "loading"})

    def launch_provider(self) -> bool:
        """Start Mycroft's provider process; tell the Slate why if it cannot."""
        if not self.config.dictate_command:
            self.state["dictation"] = "not configured"
            self.tell_slate({"op": "dictation", "state": "error: dictation not configured"})
            return False
        command = list(self.config.dictate_command)
        if any("{capture}" in part for part in command):
            capture = choose_capture()
            if capture is None:
                self.state["dictation"] = "no microphone"
                self.tell_slate({"op": "dictation", "state": "error: no capture device (plug in a USB microphone)"})
                return False
            command = [part.replace("{capture}", capture) for part in command]
            self.state["dictation_input"] = capture
        log = (RUNTIME_DIR / "dictation.log").open("w", encoding="utf-8")
        try:
            self.dictation = subprocess.Popen(command, env=self._env(),
                                              stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=log)
        finally:
            log.close()
        assert self.dictation.stdout is not None
        os.set_blocking(self.dictation.stdout.fileno(), False)
        self.dictation_buffer = b""
        self.state["dictation_pid"] = self.dictation.pid
        return True

    def resident_do(self, result: tuple[list[str], list[dict[str, Any]]]) -> None:
        """Carry out what ResidentDictation decided: provider commands, then Slate operations."""
        provider, operations = result
        for op in provider:
            if op == "launch":
                if not self.launch_provider():
                    assert self.resident is not None
                    self.resident.exited()
                    operations = []  # launch_provider already told the Slate
                    break
            elif self.dictation is not None and self.dictation.stdin is not None:
                try:
                    self.dictation.stdin.write(json.dumps({"op": op}).encode() + b"\n")
                    self.dictation.stdin.flush()
                except OSError:
                    pass  # it has exited: dictation_readable will see the end
        for operation in operations:
            self.tell_slate(operation)
        if self.resident is not None:
            self.state["dictation"] = self.resident.state + (" (start pending)" if self.resident.pending else "")
        self.write_status()

    def stop_dictation(self) -> None:
        """End the utterance; its text is kept. Resident: send `stop`, the model
        stays loaded. Otherwise close the provider's stdin: it sends `final` and exits."""
        if self.resident is not None:
            self.resident_do(self.resident.interrupt())
            return
        if self.dictation is not None and self.dictation.stdin is not None and not self.dictation.stdin.closed:
            try:
                self.dictation.stdin.close()
            except OSError:
                pass
            self.state["dictation"] = "stopping"

    def kill_dictation(self) -> None:
        """The Slate (or the daemon) is going away: end the provider without inserting anything."""
        if self.resident is not None:
            self.resident.exited()
        if self.dictation is None:
            return
        if self.dictation.poll() is None:
            self.dictation.terminate()
            try:
                self.dictation.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.dictation.kill()
        self.dictation = None
        self.state["dictation"] = "off"

    def dictation_readable(self) -> None:
        assert self.dictation is not None and self.dictation.stdout is not None
        try:
            data = os.read(self.dictation.stdout.fileno(), 65536)
        except BlockingIOError:
            return
        except OSError:
            data = b""
        if data:
            messages, self.dictation_buffer = split_lines(self.dictation_buffer + data)
            if self.resident is not None:
                for message in messages:
                    self.resident_do(self.resident.message(message))
                return
            for message in messages:
                if message.get("op") in ("ready", "error"):
                    self.state["dictation"] = "listening" if message["op"] == "ready" else "error"
                for operation in slate_operations(message):
                    self.tell_slate(operation)
            self.write_status()
            return
        code = self.dictation.wait()  # end of output: the provider has exited
        self.state["dictation_exit"] = code
        self.dictation = None
        if self.resident is not None:
            self.resident_do(self.resident.exited())
            return
        if self.state.get("dictation") != "error":
            self.state["dictation"] = "off"
            self.tell_slate({"op": "dictation", "state": ""})
        self.write_status()

    def tell_board(self, action: Board) -> None:
        """Move or press a selection on the on-screen keyboard (wvkbd-luna --cursors)."""
        keyboard = self.zone_keyboard
        if keyboard is None or keyboard.stdin is None or keyboard.poll() is not None:
            return
        line = f"press {action.cursor}\n" if action.op == "press" else f"move {action.cursor} {action.op}\n"
        try:
            keyboard.stdin.write(line.encode())
            keyboard.stdin.flush()
        except (BrokenPipeError, OSError) as error:
            self.state["error"] = f"keyboard: {type(error).__name__}"

    def tell_zone(self, op: str) -> bool:
        if self.zone_link is None:
            return False
        self.zone_link.sendall(json.dumps({"op": op}).encode() + b"\n")
        return True

    def validate_zone(self) -> None:
        if not self.tell_zone("send"):  # the Slate never connected: nothing to send
            self.finish_zone("empty")

    def mannie_zone(self) -> None:
        """FN+Y: send the Slate's text to Mannie's window and press Return; if
        Mannie is not open, the text stays in the Slate."""
        try:
            target = find_app_con(self.sway.request(4), "mannie")
        except (OSError, ConnectionError):
            target = None
        if target is None:
            self.tell_slate({"op": "notice", "text": "Mannie is not open; text kept"})
            return
        self.zone_target, self.zone_submit = target, True
        self.core.zone_state = "delivering"
        self.core._clear_cross()
        self.validate_zone()

    def discard_zone(self) -> None:
        self.tell_zone("discard")
        self.finish_zone("discarded")

    def zone_accept(self) -> None:
        link, _ = self.zone_listener.accept()
        if self.zone is None:  # not ours
            link.close()
            return
        if self.zone_link is not None:
            self.zone_link.close()
        self.zone_link, self.zone_inbox = link, b""
        self.tell_slate({"op": "history", "items": self.history})
        if self.zone_start_hidden:  # preloaded at session start: out of sight until L1 or L2
            self.zone_start_hidden = False
            if self.core.zone_state == "hidden":
                self.hide_zone()
                self.write_status()
                return
        if self.resident is not None and (self.resident.pending or self.resident.state == "listening"):
            self.tell_slate({"op": "dictation", "state": "listening" if self.resident.state == "listening" else "loading"})
        if self.config.zone_ready_sway:
            try:
                self.sway.command(self.config.zone_ready_sway)
            except (OSError, ConnectionError) as error:
                self.state["error"] = f"place the Slate: {error}"
        self.write_status()

    def zone_readable(self) -> None:
        """A message from the Slate, or its end."""
        assert self.zone_link is not None
        try:
            data = self.zone_link.recv(65536)
        except OSError:
            data = b""
        if not data:  # the Slate ended without sending (FN+B, crash): discard
            self.finish_zone("discarded" if self.core.zone_state != "closed" else self.state["zone_result"])
            return
        self.zone_inbox += data
        while b"\n" in self.zone_inbox:
            line, self.zone_inbox = self.zone_inbox.split(b"\n", 1)
            try:
                message = json.loads(line)
            except ValueError:
                continue
            if message.get("op") == "stop-dictation":
                self.stop_dictation()
                continue
            if message.get("op") == "text" and self.core.zone_state == "delivering":
                self.deliver(str(message.get("text", "")))
                return

    def finish_zone(self, result: str) -> None:
        """Close the Slate and its keyboard; restore the border. Idempotent.
        A resident provider only ends its utterance: the model stays loaded."""
        if self.resident is not None:
            self.stop_dictation()
        else:
            self.kill_dictation()
        if self.zone_link is not None:
            self.zone_link.close()
            self.zone_link = None
        if self.zone_keyboard is not None and self.zone_keyboard.stdin is not None:
            try:
                self.zone_keyboard.stdin.close()
            except OSError:
                pass
        for process in (self.zone_keyboard, self.zone):
            if process is not None and process.poll() is None:
                process.terminate()
        for process in (self.zone_keyboard, self.zone):
            if process is not None:
                try:
                    process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    process.kill()
        was_open = self.zone is not None
        self.zone = self.zone_keyboard = None
        if self.config.zone_close_sway and (was_open or result == "failed"):
            try:
                self.sway.command(self.config.zone_close_sway)
            except (OSError, ConnectionError) as error:
                self.state["error"] = f"restore border: {error}"
        if was_open and result in ("discarded", "empty"):
            self.state["discards"] += 1
        self.state["zone_result"] = result
        self.core.zone_finished()
        self.write_status()

    def deliver(self, text: str) -> None:
        """Send the Slate's text once into the window that had focus."""
        target, self.zone_target = self.zone_target, None
        submit, self.zone_submit = self.zone_submit, False
        self.finish_zone("delivering")
        if not text:
            self.state["zone_result"] = "empty"
            self.state["discards"] += 1
            self.write_status()
            return
        try:
            if target is None or not self.sway.con_exists(target):
                self.state["zone_result"] = "target-gone"
            else:
                app_id = con_app_id(self.sway.request(4), target)
                self.history = remember(HISTORY_PATH, self.history, text, app_id)
                self.sway.command(f"[con_id={target}] focus")
                if submit:  # one prompt for Mannie: lines joined
                    text = " ".join(line.strip() for line in text.splitlines() if line.strip())
                events = type_events(text)
                if events is not None:  # the daemon's own keyboard: safe for SDL2 apps
                    for code, value in events:
                        self.keyboard.emit([(EV_KEY, code, value)])
                        time.sleep(self.config.deliver_key_delay_s)
                    self.state["deliver_path"] = "uinput"
                else:  # a character AZERTY cannot type: wtype (unsafe for SDL2 apps)
                    subprocess.run([*self.config.deliver_command, text], env=self._env(), timeout=60, check=True,
                                   stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    self.state["deliver_path"] = "wtype"
                # Every send ends with Return (user, 2026-10-15): a terminal runs
                # the command, Mannie answers, a password window accepts it.
                time.sleep(0.1)
                self.tap(KEYS["KEY_ENTER"])
                self.state["deliveries"] += 1
                self.state["delivered_length"] = len(text)  # never the text itself
                self.state["zone_result"] = "delivered"
        except (OSError, ConnectionError, subprocess.SubprocessError) as error:
            self.state["zone_result"] = "failed"
            self.state["error"] = f"deliver: {type(error).__name__}"
        self.write_status()

    # status
    def write_status(self) -> None:
        status = {
            "devices": sorted(self.inputs),
            "grabbed": self.config.grab and self.grabbed,
            "raw_app": self.core.raw,
            "zone": self.core.zone_state,
            "zone_target": self.zone_target,
            "slate_ready": self.zone_link is not None,
            "menu_open": self.menu is not None and self.menu.poll() is None,
            "last_action": self.core.last_action,
            **self.core.counters,
            **self.state,
        }
        try:
            RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
            temporary = STATUS_PATH.with_suffix(".tmp")
            temporary.write_text(json.dumps(status, sort_keys=True), encoding="utf-8")
            temporary.replace(STATUS_PATH)
        except OSError as error:
            self._log(f"status not written: {error}")

    @staticmethod
    def _log(message: str) -> None:
        print(f"wyoh-gamepad: {message}", file=sys.stderr, flush=True)

    # loop
    def _input_dir_changed(self) -> bool:
        """Cheap hotplug check: /dev/input's mtime changes when a node appears or goes."""
        try:
            mtime = os.stat("/dev/input").st_mtime_ns
        except OSError:
            return True
        changed, self._input_mtime = mtime != getattr(self, "_input_mtime", None), mtime
        return changed

    def preload(self) -> None:
        """Session start: load the resident model, and open the Slate hidden.
        Retried every scan until Sway answers."""
        if self.resident is not None and self.resident.state == "off":
            self.resident_do(self.resident.preload())
        if not self.config.zone_preload or self.zone is not None or self.core.zone_state != "closed":
            self.preload_pending = False
            return
        self.zone_start_hidden = True
        try:
            self.open_zone()
        except (OSError, ConnectionError, subprocess.SubprocessError):
            self.zone_start_hidden = False
            return  # Sway not up yet: next scan
        self.core.zone_state = "hidden"
        self.preload_pending = False

    def run(self) -> None:
        next_scan = 0.0
        self.write_status()
        while True:
            now = time.monotonic()
            if now >= next_scan:
                if self._input_dir_changed():
                    self.rescan()
                self.subscribe_focus()
                if self.preload_pending:
                    self.preload()
                next_scan = now + 5.0  # hotplug needs no faster reaction
            fds: list[Any] = [*self.inputs.values(), self.zone_listener]
            if self.zone_link is not None:
                fds.append(self.zone_link)
            if self.focus_events is not None:
                fds.append(self.focus_events)
            dictation_fd = self.dictation.stdout.fileno() if self.dictation is not None and self.dictation.stdout else None
            if dictation_fd is not None:
                fds.append(dictation_fd)
            timeout = 1.0 / self.config.pointer.tick_hz if self.core.needs_tick() else max(0.0, next_scan - now)
            if self.core.dpad_pending is not None:
                timeout = min(timeout, self.config.cross_window_s / 2)
            if self.menu is not None or self.zone is not None:
                timeout = min(timeout, 0.25)  # notice the menu or the Slate closing by itself
            readable, _, _ = select.select(fds, [], [], timeout)
            now = time.monotonic()
            for path, fd in list(self.inputs.items()):
                if fd in readable:
                    self.read(path, now)
            if self.focus_events is not None and self.focus_events in readable:
                self.focus_event()
            if dictation_fd is not None and dictation_fd in readable and self.dictation is not None:
                self.dictation_readable()
            if self.zone_listener in readable:
                self.zone_accept()
            if self.zone_link is not None and self.zone_link in readable:
                self.zone_readable()
            if self.zone is not None and self.zone.poll() is not None and self.zone_link is None:
                self.finish_zone("discarded" if self.core.zone_state != "closed" else "failed")
            if self.core.needs_tick() or self.core.recovery_since is not None:
                self.apply(self.core.tick(now))
            if self.menu is not None and self.menu.poll() is not None:
                self.menu = None
                self.write_status()

    def close(self) -> None:
        self.apply(self.core.release_all())
        if self.zone is not None:
            self.finish_zone("discarded")
        self.kill_dictation()
        self.zone_listener.close()
        SLATE_SOCKET.unlink(missing_ok=True)
        for path in list(self.inputs):
            os.close(self.inputs.pop(path))
        self.keyboard.close()
        self.mouse.close()
        if self.pad is not None:
            self.pad.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path)
    args = parser.parse_args()
    try:
        config = load_config(args.config)
    except (ConfigError, OSError, tomllib.TOMLDecodeError, TypeError) as error:
        print(f"wyoh-gamepad: invalid config: {error}", file=sys.stderr)
        return 2
    daemon = Daemon(config)
    try:
        daemon.run()
    except KeyboardInterrupt:
        pass
    finally:
        daemon.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
