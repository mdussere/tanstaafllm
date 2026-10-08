#!/usr/bin/env python3
"""Wyoh gamepad daemon: operate the Luna session with the device's own controls.

Intent: worklines/wyoh/docs/0500_01_gamepad-input-intent.md (Wyoh Step 5).

Standard library only. The module has two layers:

* a pure core (`GamepadCore`) that turns gamepad events and clock ticks into
  output actions; it is fully testable without devices;
* thin adapters (evdev input, uinput output, Sway IPC, the input zone) and the
  `select()` loop in `main()`.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import math
import os
import select
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

KEYS = {
    "KEY_ESC": 1, "KEY_BACKSPACE": 14, "KEY_TAB": 15, "KEY_ENTER": 28, "KEY_LEFTSHIFT": 42,
    "KEY_UP": 103, "KEY_LEFT": 105, "KEY_RIGHT": 106, "KEY_DOWN": 108, "KEY_DELETE": 111,
}

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
    zone_toggle: str = "BTN_TL"
    zone_validate: str = "BTN_TL2"
    zone_validate_alt: str = "BTN_EAST"   # A validates while the zone is open
    zone_discard_alt: str = "BTN_SOUTH"   # B discards while the zone is open
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
    zone_command: tuple[str, ...] = ()
    deliver_command: tuple[str, ...] = ("wtype", "-s", "100", "-d", "10", "--")


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
    _validate(config)
    return config


def _validate(config: Config) -> None:
    named = [config.click, config.zone_toggle, config.zone_validate, config.zone_validate_alt,
             config.zone_discard_alt, config.menu, config.next_window, config.modifier,
             *config.recovery, *config.keys, *config.fn_sway]
    for name in named:
        if name not in BUTTONS:
            raise ConfigError(f"unknown button: {name}")
    for chord in config.keys.values():
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
    op: str  # "open" | "validate" | "discard"


@dataclass(frozen=True)
class Menu:
    pass


@dataclass(frozen=True)
class Note:
    """A status-only event (no output), e.g. ignored button or recovery."""
    event: str


Action = Key | Click | Motion | Sway | Zone | Menu | Note


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
        self.zone_state = "closed"  # closed | open | delivering
        self.axes = (ABS_X, ABS_Y) if config.pointer_stick == "left" else (ABS_RX, ABS_RY)
        self.stick = {axis: 0.0 for axis in self.axes}
        self.fraction = [0.0, 0.0]
        self.last_tick: float | None = None
        self.recovery_since: float | None = None
        self.counters = {"ignored": 0, "recovery": 0}
        self.last_action = ""

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

    # events
    def button(self, code: int, pressed: bool, now: float) -> list[Action]:
        if pressed:
            if code in self.held:
                return []  # autorepeat from the device; key repeat is Wayland's job
            self.held.add(code)
            actions = self._press(code)
            first, second = self._recovery_pair()
            if first in self.held and second in self.held and self.recovery_since is None:
                self.recovery_since = now
            return actions
        if code not in self.held:
            return []
        self.held.discard(code)
        if code in self._recovery_pair():
            self.recovery_since = None
        return self._release(code)

    def _press(self, code: int) -> list[Action]:
        cfg, name = self.config, BUTTON_NAMES.get(code, "")
        outputs: list[Action] = []
        result: list[Action] = []
        if code == self._b(cfg.modifier):
            return []
        if self.fn_held:
            if code == self._b(cfg.recovery[1]) or code == self._b(cfg.recovery[0]):
                return []  # recovery is decided by the hold timer
            if name in cfg.fn_sway and self.zone_state == "closed":
                result = [Sway(cfg.fn_sway[name])]
            else:
                result = [Note(f"ignored:{name or code}")]
                self.counters["ignored"] += 1
            self._last(result)
            return result
        if self.zone_state == "open":
            if code in (self._b(cfg.zone_validate), self._b(cfg.zone_validate_alt)):
                self.zone_state = "delivering"
                result = [Zone("validate")]
            elif code in (self._b(cfg.zone_toggle), self._b(cfg.zone_discard_alt)):
                self.zone_state = "closed"
                result = [Zone("discard")]
            elif name in cfg.keys and code not in (self._b(cfg.menu), self._b(cfg.next_window)):
                outputs = [Key(k, True) for k in self._keys(cfg.keys[name])]
            elif code == self._b(cfg.click):
                outputs = [Click(BTN_LEFT, True)]
            else:
                result = [Note(f"ignored:{name or code}")]
                self.counters["ignored"] += 1
        elif self.zone_state == "delivering":
            if name in cfg.keys or code == self._b(cfg.click):
                result = [Note(f"busy:{name or code}")]
            else:
                result = [Note(f"busy:{name or code}")]
        else:  # closed
            if code == self._b(cfg.zone_toggle):
                self.zone_state = "open"
                result = [Zone("open")]
            elif code == self._b(cfg.menu):
                result = [Menu()]
            elif code == self._b(cfg.next_window):
                result = [Sway("focus next")]
            elif name in cfg.keys:
                outputs = [Key(k, True) for k in self._keys(cfg.keys[name])]
            elif code == self._b(cfg.click):
                outputs = [Click(BTN_LEFT, True)]
            else:
                result = [Note(f"ignored:{name or code}")]
                self.counters["ignored"] += 1
        if outputs:
            self.pressed_outputs[code] = outputs
            result = outputs
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
        return released

    def axis(self, code: int, value: int) -> list[Action]:
        if code in self.stick:
            self.stick[code] = float(value)
        return []  # the other stick is unassigned

    def needs_tick(self) -> bool:
        x, y = (self.stick[axis] for axis in self.axes)
        return pointer_speed(x, y, self.config.pointer) != (0.0, 0.0) or self.recovery_since is not None

    def tick(self, now: float) -> list[Action]:
        actions: list[Action] = []
        if self.recovery_since is not None and now - self.recovery_since >= self.config.recovery_hold_s:
            actions += self.recover()
            self.recovery_since = None
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
        self.counters["recovery"] += 1
        actions.append(Note("recovery"))
        self._last(actions)
        return actions

    def zone_finished(self) -> None:
        """The adapter reports the zone closed (delivered, discarded, or failed)."""
        self.zone_state = "closed"

    def release_all(self) -> list[Action]:
        actions: list[Action] = []
        for code in list(self.pressed_outputs):
            actions += self._release(code)
        self.held.clear()
        self.stick = {axis: 0.0 for axis in self.axes}
        self.recovery_since = None
        return actions

    def _last(self, actions: list[Action]) -> None:
        if actions:
            self.last_action = type(actions[0]).__name__.lower() + (
                f":{getattr(actions[0], 'op', '') or getattr(actions[0], 'command', '') or getattr(actions[0], 'event', '')}"
            ).rstrip(":")


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
        self.keyboard = UInputDevice(KEYBOARD_NAME, 0x0010, list(KEYS.values()), rel=False)
        self.mouse = UInputDevice(MOUSE_NAME, 0x0011, [BTN_LEFT, BTN_LEFT + 1], rel=True)
        self.zone: subprocess.Popen[str] | None = None
        self.zone_target: int | None = None
        self.menu: subprocess.Popen[bytes] | None = None
        self.state = {"zone_result": "", "error": "", "deliveries": 0, "discards": 0}

    # devices
    def rescan(self) -> None:
        for path, name in find_devices(self.config.devices).items():
            if path in self.inputs:
                continue
            try:
                fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK)
                if self.config.grab:
                    fcntl.ioctl(fd, EVIOCGRAB, 1)
                self.inputs[path] = fd
                self._log(f"attached {name} at {path}")
                self.write_status()
            except OSError as error:
                self._log(f"cannot attach {path}: {error}")

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
                self.apply(self.core.axis(code, value))

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
        if any(not isinstance(action, Motion) for action in actions):
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
        elif isinstance(action, Zone):
            {"open": self.open_zone, "validate": self.validate_zone, "discard": self.discard_zone}[action.op]()

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

    # zone
    def open_zone(self) -> None:
        if not self.config.zone_command:
            raise subprocess.SubprocessError("no zone command configured")
        try:
            self.zone_target = self.sway.focused_con_id()
        except (OSError, ConnectionError) as error:
            self.core.zone_finished()
            self.state["zone_result"] = "no-sway"
            raise ConnectionError(f"zone needs Sway: {error}") from error
        self.zone = subprocess.Popen(list(self.config.zone_command), env=self._env(), text=True,
                                     stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
        self.state["zone_result"] = "open"

    def validate_zone(self) -> None:
        if self.zone is not None and self.zone.poll() is None:
            self.tap(KEYS["KEY_ENTER"])  # fuzzel prints the text and exits

    def discard_zone(self) -> None:
        if self.zone is not None and self.zone.poll() is None:
            self.tap(KEYS["KEY_ESC"])
        self.state["zone_result"] = "discarded"

    def zone_fd(self) -> int | None:
        return self.zone.stdout.fileno() if self.zone is not None and self.zone.stdout else None

    def zone_exited(self) -> None:
        """fuzzel ended: deliver its text once if it was validated, else discard."""
        assert self.zone is not None and self.zone.stdout
        text = self.zone.stdout.read()
        code = self.zone.wait()
        self.zone.stdout.close()
        self.zone = None
        text = text[:-1] if text.endswith("\n") else text
        validated = code == 0 and self.core.zone_state in ("delivering", "open")
        target, self.zone_target = self.zone_target, None
        self.core.zone_finished()
        if not validated or not text:
            self.state["zone_result"] = "discarded" if not validated else "empty"
            self.state["discards"] += 1
            self.write_status()
            return
        try:
            if target is None or not self.sway.con_exists(target):
                self.state["zone_result"] = "target-gone"
            else:
                self.sway.command(f"[con_id={target}] focus")
                subprocess.run([*self.config.deliver_command, text], env=self._env(), timeout=30, check=True,
                               stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.state["deliveries"] += 1
                self.state["zone_result"] = "delivered"
        except (OSError, ConnectionError, subprocess.SubprocessError) as error:
            self.state["zone_result"] = "failed"
            self.state["error"] = f"deliver: {error}"
        self.write_status()

    # status
    def write_status(self) -> None:
        status = {
            "devices": sorted(self.inputs),
            "grabbed": self.config.grab,
            "zone": self.core.zone_state,
            "zone_target": self.zone_target,
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

    def run(self) -> None:
        next_scan = 0.0
        self.write_status()
        while True:
            now = time.monotonic()
            if now >= next_scan:
                if self._input_dir_changed():
                    self.rescan()
                next_scan = now + 5.0  # hotplug needs no faster reaction
            fds = list(self.inputs.values())
            zone_fd = self.zone_fd()
            if zone_fd is not None:
                fds.append(zone_fd)
            timeout = 1.0 / self.config.pointer.tick_hz if self.core.needs_tick() else max(0.0, next_scan - now)
            if self.menu is not None:
                timeout = min(timeout, 0.25)  # notice the menu closing by itself
            readable, _, _ = select.select(fds, [], [], timeout)
            now = time.monotonic()
            for path, fd in list(self.inputs.items()):
                if fd in readable:
                    self.read(path, now)
            if zone_fd is not None and zone_fd in readable:
                self.zone_exited()
            if self.core.needs_tick() or self.core.recovery_since is not None:
                self.apply(self.core.tick(now))
            if self.menu is not None and self.menu.poll() is not None:
                self.menu = None
                self.write_status()

    def close(self) -> None:
        self.apply(self.core.release_all())
        for path in list(self.inputs):
            os.close(self.inputs.pop(path))
        self.keyboard.close()
        self.mouse.close()


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
