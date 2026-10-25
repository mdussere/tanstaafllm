#!/usr/bin/python3
"""Ctrl+Alt+F1…F12 switches Luna's virtual terminal, even when Sway is stuck.

plan_mannie.md Step 7.5 (user, 2026-10-25): a hard-wired key combination that
brings back the tty1 console, where michael is logged in, so that a USB keyboard
is enough to recover when SSH or the desktop fail. Sway normally handles these
keys itself; this daemon reads every keyboard directly (libinput does not grab
keyboards) and runs chvt, so it still works when the compositor does not.
Keyboards plugged in later are picked up within a few seconds. The kernel has no
SysRq, so this is the keyboard rescue path. Standard library only; runs as root.
"""

from __future__ import annotations

import glob
import os
import select
import struct
import subprocess
import sys

EVENT = struct.Struct("llHHi")  # struct input_event on 64-bit Linux
EV_KEY = 1
KEY_LEFTCTRL, KEY_RIGHTCTRL, KEY_LEFTALT, KEY_RIGHTALT = 29, 97, 56, 100
F_KEYS = {59: 1, 60: 2, 61: 3, 62: 4, 63: 5, 64: 6, 65: 7, 66: 8, 67: 9, 68: 10, 87: 11, 88: 12}
RESCAN_SECONDS = 5.0


def is_keyboard(event_path: str) -> bool:
    """True when the device reports KEY_F1 (a real keyboard, not the gamepad)."""
    name = os.path.basename(event_path)
    try:
        words = open(f"/sys/class/input/{name}/device/capabilities/key").read().split()
    except OSError:
        return False
    bits = 0
    for word in words:
        bits = (bits << 64) | int(word, 16)
    return bool(bits >> 59 & 1)


def target_vt(held: set[int], code: int, value: int) -> int | None:
    """The VT to switch to for one key event, given the modifiers held."""
    if value != 1 or code not in F_KEYS:
        return None
    ctrl = held & {KEY_LEFTCTRL, KEY_RIGHTCTRL}
    alt = held & {KEY_LEFTALT, KEY_RIGHTALT}
    return F_KEYS[code] if ctrl and alt else None


def main() -> int:
    open_devices: dict[int, tuple[str, set[int]]] = {}
    while True:
        known = {path for path, _ in open_devices.values()}
        for path in glob.glob("/dev/input/event*"):
            if path not in known and is_keyboard(path):
                try:
                    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
                except OSError:
                    continue
                open_devices[fd] = (path, set())
                print(f"luna-vt-rescue: watching {path}", flush=True)
        ready, _, _ = select.select(list(open_devices), [], [], RESCAN_SECONDS)
        for fd in ready:
            path, held = open_devices[fd]
            try:
                data = os.read(fd, EVENT.size * 64)
            except OSError:
                os.close(fd)
                del open_devices[fd]
                print(f"luna-vt-rescue: {path} gone", flush=True)
                continue
            for offset in range(0, len(data) - EVENT.size + 1, EVENT.size):
                _, _, kind, code, value = EVENT.unpack_from(data, offset)
                if kind != EV_KEY:
                    continue
                vt = target_vt(held, code, value)
                if value == 1:
                    held.add(code)
                elif value == 0:
                    held.discard(code)
                if vt is not None:
                    print(f"luna-vt-rescue: chvt {vt}", flush=True)
                    subprocess.run(["/usr/bin/chvt", str(vt)], check=False)


if __name__ == "__main__":
    sys.exit(main())
