"""Mannie 7.5: Ctrl+Alt+F1 brings back Luna's tty1 console (`luna_vt_rescue.feature`).

The key logic runs by default. The live test (MANNIE_LUNA_LIVE=1) creates a
virtual USB-like keyboard with uinput on Luna, presses Ctrl+Alt+F1 then
Ctrl+Alt+F7, and checks the active VT and luna-vt-rescue's journal.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).parents[2]
SPEC = importlib.util.spec_from_file_location("luna_vt_rescue", REPO / "src/mannie/luna/luna-vt-rescue.py")
rescue = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rescue)

LIVE = os.environ.get("MANNIE_LUNA_LIVE") == "1"


def test_only_ctrl_alt_function_keys_switch() -> None:
    ctrl, alt, f1, f7 = rescue.KEY_LEFTCTRL, rescue.KEY_LEFTALT, 59, 65
    assert rescue.target_vt({ctrl, alt}, f1, 1) == 1
    assert rescue.target_vt({rescue.KEY_RIGHTCTRL, rescue.KEY_RIGHTALT}, f7, 1) == 7
    assert rescue.target_vt({ctrl}, f1, 1) is None
    assert rescue.target_vt({alt}, f1, 1) is None
    assert rescue.target_vt({ctrl, alt}, f1, 0) is None  # release
    assert rescue.target_vt({ctrl, alt}, 30, 1) is None  # "a"


# Runs on Luna as root: a uinput keyboard that taps Ctrl+Alt+F<n>.
INJECT = r'''
import fcntl, os, struct, sys, time
UI_SET_EVBIT, UI_SET_KEYBIT, UI_DEV_CREATE, UI_DEV_DESTROY = 0x40045564, 0x40045565, 0x5501, 0x5502
fd = os.open("/dev/uinput", os.O_WRONLY | os.O_NONBLOCK)
fcntl.ioctl(fd, UI_SET_EVBIT, 1)
for key in range(1, 128):
    fcntl.ioctl(fd, UI_SET_KEYBIT, key)
os.write(fd, struct.pack("80sHHHHi64i64i64i64i", b"mannie-test-keyboard", 3, 1, 1, 1, 0, *([0] * 256)))
fcntl.ioctl(fd, UI_DEV_CREATE)
time.sleep(7)  # luna-vt-rescue rescans every 5 s
def emit(kind, code, value):
    os.write(fd, struct.pack("llHHi", 0, 0, kind, code, value))
def tap(fkey):
    for code in (29, 56):
        emit(1, code, 1); emit(0, 0, 0)
    emit(1, fkey, 1); emit(0, 0, 0); emit(1, fkey, 0); emit(0, 0, 0)
    for code in (56, 29):
        emit(1, code, 0); emit(0, 0, 0)
for fkey in sys.argv[1:]:
    tap(int(fkey)); time.sleep(3)
    print(open("/sys/class/tty/tty0/active").read().strip(), flush=True)
fcntl.ioctl(fd, UI_DEV_DESTROY)
'''


@pytest.mark.live
@pytest.mark.skipif(not LIVE, reason="set MANNIE_LUNA_LIVE=1 to run on Luna")
@pytest.mark.timeout(120)
def test_ctrl_alt_f1_and_f7_on_luna() -> None:
    since = subprocess.run(["ssh", "luna", "date +%s"], capture_output=True, text=True, check=True).stdout.strip()
    run = subprocess.run(["ssh", "luna", "python3 - 59 65"], input=INJECT, capture_output=True, text=True, timeout=60)
    assert run.returncode == 0, run.stderr
    assert run.stdout.split() == ["tty1", "tty7"]
    journal = subprocess.run(
        ["ssh", "luna", f"journalctl -u luna-vt-rescue --since @{since} --no-pager -o cat"], capture_output=True, text=True
    ).stdout
    assert "watching" in journal and "chvt 1" in journal and "chvt 7" in journal
    active = subprocess.run(["ssh", "luna", "systemctl is-active wyoh-sway"], capture_output=True, text=True).stdout.strip()
    assert active == "active"
