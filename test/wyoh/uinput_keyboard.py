"""A kernel-level keyboard and mouse for the "person" steps on Luna.

Runs on the target as root (stdin-fed over SSH, like `sway_ipc_probe.py`). It
creates one /dev/uinput keyboard that libinput and Sway treat exactly like a
USB keyboard, so Sway's own `xkb_layout fr` and `--to-code` bindings apply.
The device lives for the whole session, which avoids the keymap churn that
short-lived `wtype` keyboards cause.

Protocol (one command per line on stdin; each answered by `ok` or `error ...`):
    combo alt+shift+q    press the keys together, release in reverse order
    type <text>          type characters as on a French AZERTY keyboard
    home                 move the mouse to the top-left corner of the output
    move <dx> <dy>       move the mouse by a relative amount (Sway sets it to
                         a flat 1:1 profile for this device)
    click [left|right]   press and release a mouse button
    quit                 destroy the devices and exit
After creation it prints `ready <keyboard name> <mouse name>`.
"""

from __future__ import annotations

import fcntl
import os
import struct
import sys
import time

DEVICE_NAME = "wyoh-uinput-keyboard"
MOUSE_NAME = "wyoh-uinput-mouse"

UI_SET_EVBIT = 0x40045564
UI_SET_KEYBIT = 0x40045565
UI_DEV_SETUP = 0x405C5503
UI_DEV_CREATE = 0x5501
UI_DEV_DESTROY = 0x5502
EV_SYN, EV_KEY, EV_REL, SYN_REPORT = 0, 1, 2, 0
UI_SET_RELBIT = 0x40045566
REL_X, REL_Y = 0, 1
BUTTONS = {"left": 0x110, "right": 0x111}
BUS_VIRTUAL = 0x06

# Linux input key codes (physical key positions, US-labelled).
KEYS = {
    "esc": 1, "1": 2, "2": 3, "3": 4, "4": 5, "5": 6, "6": 7, "7": 8, "8": 9, "9": 10, "0": 11,
    "q": 16, "w": 17, "e": 18, "r": 19, "t": 20, "y": 21, "u": 22, "i": 23, "o": 24, "p": 25,
    "enter": 28, "a": 30, "s": 31, "d": 32, "f": 33, "g": 34, "h": 35, "j": 36, "k": 37, "l": 38,
    "semicolon": 39, "shift": 42, "z": 44, "x": 45, "c": 46, "v": 47, "b": 48, "n": 49, "m": 50,
    "alt": 56, "space": 57, "backspace": 14, "up": 103, "down": 108,
}

# Character -> (physical key, shifted) on a French AZERTY keyboard. Only the
# characters the scenario needs; anything else is refused rather than guessed.
AZERTY = {**{c: (c, False) for c in "bcdefghijklnoprstuvxy"},
          "a": ("q", False), "q": ("a", False), "z": ("w", False), "w": ("z", False),
          "m": ("semicolon", False), " ": ("space", False), "-": ("6", False)}

# Named keys for `combo`, given by their AZERTY label where it differs.
COMBO = {**KEYS, "q": KEYS["a"], "a": KEYS["q"], "z": KEYS["w"], "w": KEYS["z"]}


def _emit(fd: int, kind: int, code: int, value: int) -> None:
    os.write(fd, struct.pack("llHHi", 0, 0, kind, code, value))


def _key(fd: int, code: int, value: int) -> None:
    _emit(fd, EV_KEY, code, value)
    _emit(fd, EV_SYN, SYN_REPORT, 0)
    time.sleep(0.02)


def _combo(fd: int, names: list[str]) -> None:
    codes = [COMBO[name] for name in names]
    for code in codes:
        _key(fd, code, 1)
    for code in reversed(codes):
        _key(fd, code, 0)


def _type(fd: int, text: str) -> None:
    for char in text:
        if char not in AZERTY:
            raise ValueError(f"character {char!r} has no AZERTY mapping here")
        name, shifted = AZERTY[char]  # `name` is already a physical key
        codes = [KEYS["shift"], KEYS[name]] if shifted else [KEYS[name]]
        for code in codes:
            _key(fd, code, 1)
        for code in reversed(codes):
            _key(fd, code, 0)


def _move(fd: int, dx: int, dy: int) -> None:
    # libinput may drop very large single events; send moderate steps.
    while dx or dy:
        step_x, step_y = max(-50, min(50, dx)), max(-50, min(50, dy))
        _emit(fd, EV_REL, REL_X, step_x)
        _emit(fd, EV_REL, REL_Y, step_y)
        _emit(fd, EV_SYN, SYN_REPORT, 0)
        time.sleep(0.005)
        dx, dy = dx - step_x, dy - step_y
    time.sleep(0.05)


def _create(name: str, product: int, setup_bits) -> int:
    fd = os.open("/dev/uinput", os.O_WRONLY | os.O_NONBLOCK)
    setup_bits(fd)
    setup = struct.pack("HHHH80sI", BUS_VIRTUAL, 0x1209, product, 1, name.encode(), 0)
    fcntl.ioctl(fd, UI_DEV_SETUP, setup)
    fcntl.ioctl(fd, UI_DEV_CREATE)
    return fd


def _keyboard_bits(fd: int) -> None:
    fcntl.ioctl(fd, UI_SET_EVBIT, EV_KEY)
    for code in range(1, 120):
        fcntl.ioctl(fd, UI_SET_KEYBIT, code)


def _mouse_bits(fd: int) -> None:
    fcntl.ioctl(fd, UI_SET_EVBIT, EV_KEY)
    for code in BUTTONS.values():
        fcntl.ioctl(fd, UI_SET_KEYBIT, code)
    fcntl.ioctl(fd, UI_SET_EVBIT, EV_REL)
    fcntl.ioctl(fd, UI_SET_RELBIT, REL_X)
    fcntl.ioctl(fd, UI_SET_RELBIT, REL_Y)


def main() -> int:
    fd = _create(DEVICE_NAME, 0x0001, _keyboard_bits)
    mouse = _create(MOUSE_NAME, 0x0002, _mouse_bits)
    print(f"ready {DEVICE_NAME} {MOUSE_NAME}", flush=True)
    try:
        for line in sys.stdin:
            command, _, argument = line.rstrip("\n").partition(" ")
            try:
                if command == "combo":
                    _combo(fd, argument.split("+"))
                elif command == "type":
                    _type(fd, argument)
                elif command == "home":
                    _move(mouse, -2000, -2000)
                elif command == "move":
                    dx, dy = (int(value) for value in argument.split())
                    _move(mouse, dx, dy)
                elif command == "click":
                    button = BUTTONS[argument or "left"]
                    _key(mouse, button, 1)
                    _key(mouse, button, 0)
                elif command == "quit":
                    print("ok", flush=True)
                    break
                else:
                    raise ValueError(f"unknown command {command!r}")
                print("ok", flush=True)
            except (KeyError, ValueError) as error:
                print(f"error {error}", flush=True)
    finally:
        for device in (fd, mouse):
            fcntl.ioctl(device, UI_DEV_DESTROY)
            os.close(device)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
