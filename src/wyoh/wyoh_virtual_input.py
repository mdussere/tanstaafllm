"""Development-only virtual input devices: the simulated person (Wyoh Step 5).

`VirtualGamepad` mirrors Luna's `r36s_Gamepad` (17 buttons, 4 axes, ±1800) under
the name `wyoh-virtual-gamepad`, which the gamepad daemon serves alongside the
real device. `VirtualKeyboard` stands in for the USB keyboard and types as a
French AZERTY keyboard (physical key codes; Sway applies `xkb_layout fr`).

Used only by the MCP server's `--full-ipc-development` tools and by tests.
Standard library only.
"""

from __future__ import annotations

import fcntl
import os
import struct
import time

from wyoh_gamepad import (
    ABS_RX, ABS_RY, ABS_X, ABS_Y, BUS_VIRTUAL, BUTTONS, EV_ABS, EV_KEY, EV_SYN, EVENT_FORMAT,
    SYN_REPORT, UI_DEV_CREATE, UI_DEV_DESTROY, UI_DEV_SETUP, UI_SET_EVBIT, UI_SET_KEYBIT, VENDOR,
)

GAMEPAD_NAME = "wyoh-virtual-gamepad"
KEYBOARD_NAME = "wyoh-virtual-keyboard"
UI_SET_ABSBIT = 0x40045567
UI_ABS_SETUP = 0x401C5504
AXES = {"ABS_X": ABS_X, "ABS_Y": ABS_Y, "ABS_RX": ABS_RX, "ABS_RY": ABS_RY}
AXIS_RANGE = 1800

# Linux key codes at physical (US-labelled) positions.
_KEY = {
    "1": 2, "2": 3, "3": 4, "4": 5, "5": 6, "6": 7, "7": 8, "8": 9, "9": 10, "0": 11,
    "q": 16, "w": 17, "e": 18, "r": 19, "t": 20, "y": 21, "u": 22, "i": 23, "o": 24, "p": 25,
    "a": 30, "s": 31, "d": 32, "f": 33, "g": 34, "h": 35, "j": 36, "k": 37, "l": 38,
    "semicolon": 39, "z": 44, "x": 45, "c": 46, "v": 47, "b": 48, "n": 49, "m": 50,
    "comma": 51, "dot": 52, "slash": 53, "space": 57, "enter": 28, "esc": 1,
    "backspace": 14, "tab": 15, "shift": 42,
}

# Character -> (physical key, shift) on a French AZERTY keyboard.
AZERTY: dict[str, tuple[str, bool]] = {
    **{c: (c, False) for c in "bcdefghijklnoprstuvxy"},
    **{c.upper(): (c, True) for c in "bcdefghijklnoprstuvxy"},
    "a": ("q", False), "A": ("q", True), "q": ("a", False), "Q": ("a", True),
    "z": ("w", False), "Z": ("w", True), "w": ("z", False), "W": ("z", True),
    "m": ("semicolon", False), "M": ("semicolon", True),
    **{d: (d, True) for d in "1234567890"},  # digits are shifted on AZERTY
    " ": ("space", False), "-": ("6", False), "_": ("8", False),
    ",": ("m", False), ".": ("comma", True), "/": ("dot", True),
    ";": ("comma", False), ":": ("dot", False), "!": ("slash", False),
}


def _setup(fd: int, name: str, product: int) -> None:
    fcntl.ioctl(fd, UI_DEV_SETUP, struct.pack("HHHH80sI", BUS_VIRTUAL, VENDOR, product, 1, name.encode(), 0))
    fcntl.ioctl(fd, UI_DEV_CREATE)


def _emit(fd: int, kind: int, code: int, value: int) -> None:
    os.write(fd, struct.pack(EVENT_FORMAT, 0, 0, kind, code, value))


def _sync(fd: int) -> None:
    _emit(fd, EV_SYN, SYN_REPORT, 0)


class VirtualGamepad:
    def __init__(self) -> None:
        self.fd = os.open("/dev/uinput", os.O_WRONLY | os.O_NONBLOCK)
        fcntl.ioctl(self.fd, UI_SET_EVBIT, EV_KEY)
        for code in BUTTONS.values():
            fcntl.ioctl(self.fd, UI_SET_KEYBIT, code)
        fcntl.ioctl(self.fd, UI_SET_EVBIT, EV_ABS)
        for code in AXES.values():
            fcntl.ioctl(self.fd, UI_SET_ABSBIT, code)
            fcntl.ioctl(self.fd, UI_ABS_SETUP, struct.pack("HHiiiiii", code, 0, 0, -AXIS_RANGE, AXIS_RANGE, 32, 32, 0))
        _setup(self.fd, GAMEPAD_NAME, 0x0020)

    def buttons(self, names: list[str], pressed: bool) -> None:
        for name in names:
            _emit(self.fd, EV_KEY, BUTTONS[name], 1 if pressed else 0)
            _sync(self.fd)
            time.sleep(0.02)

    def tap(self, names: list[str], hold_seconds: float = 0.08) -> None:
        """Press the buttons in order, hold, release in reverse (a chord or one button)."""
        self.buttons(names, True)
        time.sleep(hold_seconds)
        self.buttons(list(reversed(names)), False)

    def stick(self, axis_x: str, axis_y: str, x: int, y: int) -> None:
        _emit(self.fd, EV_ABS, AXES[axis_x], max(-AXIS_RANGE, min(AXIS_RANGE, x)))
        _emit(self.fd, EV_ABS, AXES[axis_y], max(-AXIS_RANGE, min(AXIS_RANGE, y)))
        _sync(self.fd)

    def close(self) -> None:
        try:
            fcntl.ioctl(self.fd, UI_DEV_DESTROY)
        finally:
            os.close(self.fd)


class VirtualKeyboard:
    def __init__(self) -> None:
        self.fd = os.open("/dev/uinput", os.O_WRONLY | os.O_NONBLOCK)
        fcntl.ioctl(self.fd, UI_SET_EVBIT, EV_KEY)
        for code in range(1, 120):
            fcntl.ioctl(self.fd, UI_SET_KEYBIT, code)
        _setup(self.fd, KEYBOARD_NAME, 0x0021)

    def _key(self, code: int, value: int) -> None:
        _emit(self.fd, EV_KEY, code, value)
        _sync(self.fd)
        time.sleep(0.015)

    def type(self, text: str) -> None:
        missing = sorted({char for char in text if char not in AZERTY})
        if missing:
            raise ValueError(f"characters without an AZERTY mapping here: {missing}")
        for char in text:
            name, shifted = AZERTY[char]
            codes = [_KEY["shift"], _KEY[name]] if shifted else [_KEY[name]]
            for code in codes:
                self._key(code, 1)
            for code in reversed(codes):
                self._key(code, 0)

    def press(self, name: str) -> None:
        self._key(_KEY[name], 1)
        self._key(_KEY[name], 0)

    def close(self) -> None:
        try:
            fcntl.ioctl(self.fd, UI_DEV_DESTROY)
        finally:
            os.close(self.fd)
