#!/usr/bin/env python3
"""Development-only, full-fidelity Sway IPC server carried over MCP stdio.

The entry point deliberately starts its own headless Sway child.  It neither
accepts nor consults a supplied SWAYSOCK, so it cannot attach to a desktop
session.  The broad `sway_command` tool is therefore development authority
only; it is not a Wyoh product or consumer interface.
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import importlib.metadata
import json
import logging
import os
import select
import socket
import stat
import struct
import subprocess
import tempfile
import time
import uuid
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from mcp.server import MCPServer


LOGGER = logging.getLogger(__name__)
MAGIC = b"i3-ipc"
EVENT_BIT = 1 << 31
DEFAULT_SHARED_DESCRIPTOR = Path.home() / ".local/state/tanstfaafllm/wyoh/sway-vnc-session.json"

REQUEST_TYPES: dict[str, int] = {
    "sway_command": 0,
    "sway_get_workspaces": 1,
    "sway_subscribe": 2,
    "sway_get_outputs": 3,
    "sway_get_tree": 4,
    "sway_get_marks": 5,
    "sway_get_bar_config": 6,
    "sway_get_version": 7,
    "sway_get_binding_modes": 8,
    "sway_get_config": 9,
    "sway_send_tick": 10,
    "sway_sync": 11,
    "sway_get_binding_state": 12,
    "sway_get_inputs": 100,
    "sway_get_seats": 101,
}

EVENT_TYPES: dict[str, int] = {
    "workspace": EVENT_BIT | 0,
    "output": EVENT_BIT | 1,
    "mode": EVENT_BIT | 2,
    "window": EVENT_BIT | 3,
    "barconfig_update": EVENT_BIT | 4,
    "binding": EVENT_BIT | 5,
    "shutdown": EVENT_BIT | 6,
    "tick": EVENT_BIT | 7,
    "bar_state_update": EVENT_BIT | 20,
    "input": EVENT_BIT | 21,
}


class SwayIPCError(RuntimeError):
    """A Sway IPC message could not be completed faithfully."""


def _recv_exact(connection: socket.socket, size: int) -> bytes:
    data = bytearray()
    while len(data) < size:
        chunk = connection.recv(size - len(data))
        if not chunk:
            raise SwayIPCError("Sway IPC socket closed before a complete message")
        data.extend(chunk)
    return bytes(data)


class SwayIPC:
    """Minimal implementation of Sway's documented Unix-socket protocol."""

    def __init__(self, socket_path: str, timeout_seconds: float = 5.0) -> None:
        self.connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.connection.settimeout(timeout_seconds)
        self.connection.connect(socket_path)

    def close(self) -> None:
        self.connection.close()

    def send(self, message_type: int, payload: str = "") -> None:
        encoded = payload.encode("utf-8")
        self.connection.sendall(MAGIC + struct.pack("=II", len(encoded), message_type) + encoded)

    def receive(self, timeout_seconds: float | None = None) -> tuple[int, Any]:
        if timeout_seconds is not None:
            self.connection.settimeout(timeout_seconds)
        header = _recv_exact(self.connection, 14)
        if header[:6] != MAGIC:
            raise SwayIPCError("unexpected Sway IPC magic")
        length, message_type = struct.unpack("=II", header[6:])
        payload = _recv_exact(self.connection, length)
        try:
            return message_type, json.loads(payload.decode("utf-8"))
        except json.JSONDecodeError as error:
            raise SwayIPCError("Sway IPC payload was not JSON") from error

    def request(self, message_type: int, payload: str = "") -> Any:
        self.send(message_type, payload)
        reply_type, reply = self.receive()
        if reply_type != message_type:
            raise SwayIPCError(f"reply type {reply_type} did not match request {message_type}")
        return reply


def _wait_for_new_socket(runtime_dir: Path, previous: set[str], process: subprocess.Popen[str]) -> str:
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        candidates = set(glob.glob(str(runtime_dir / "sway-ipc.*.sock"))) - previous
        if len(candidates) == 1:
            return candidates.pop()
        if process.poll() is not None:
            stderr = process.stderr.read() if process.stderr else ""
            raise SwayIPCError(f"headless Sway exited before its socket appeared: {stderr}")
        select.select([], [], [], 0.02)
    raise SwayIPCError("headless Sway socket did not appear within 10 seconds")


class HeadlessSwaySession:
    """Owns the disposable Sway child used by the full-development bridge."""

    kind = "ephemeral-child"
    is_bridge_owned = True

    def __init__(self, sway_binary: str, library_path: str) -> None:
        self.sway_binary = sway_binary
        self.library_path = library_path
        self._temporary: tempfile.TemporaryDirectory[str] | None = None
        self.process: subprocess.Popen[str] | None = None
        self.socket_path: str | None = None

    def start(self) -> str:
        runtime_dir_value = os.environ.get("XDG_RUNTIME_DIR")
        if not runtime_dir_value:
            raise SwayIPCError("XDG_RUNTIME_DIR is required to create an owned Sway child")
        runtime_dir = Path(runtime_dir_value)
        self._temporary = tempfile.TemporaryDirectory(prefix="wyoh-mcp-sway-")
        config = Path(self._temporary.name) / "config"
        config.write_text(
            'xwayland disable\nmode "wyoh-alt" { bindsym Escape mode "default" }\n',
            encoding="utf-8",
        )
        previous = set(glob.glob(str(runtime_dir / "sway-ipc.*.sock")))
        environment = os.environ.copy()
        environment.update(
            {
                "WLR_BACKENDS": "headless",
                "WLR_HEADLESS_OUTPUTS": "1",
                "WLR_RENDERER": "pixman",
                "LD_LIBRARY_PATH": self.library_path,
            }
        )
        environment.pop("SWAYSOCK", None)
        environment.pop("I3SOCK", None)
        self.process = subprocess.Popen(
            [self.sway_binary, "--config", str(config)],
            env=environment,
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        self.socket_path = _wait_for_new_socket(runtime_dir, previous, self.process)
        LOGGER.info("started owned headless Sway child pid=%s", self.process.pid)
        return self.socket_path

    @property
    def state(self) -> str:
        if self.process is None:
            return "not-started"
        return "running" if self.process.poll() is None else "stopped"

    def stop(self) -> None:
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5.0)
        if self._temporary is not None:
            self._temporary.cleanup()
        LOGGER.info("stopped owned headless Sway child")


class SharedVncSwaySession:
    """Read only the descriptor for the named Wyoh-owned Sway/WayVNC service."""

    kind = "shared-vnc-service"
    is_bridge_owned = False
    process: None = None

    def __init__(self, descriptor: Path = DEFAULT_SHARED_DESCRIPTOR) -> None:
        self.descriptor = descriptor
        self.socket_path: str | None = None
        self.wayland_display: str | None = None
        self.runtime_dir: Path | None = None

    def start(self) -> str:
        runtime_value = os.environ.get("XDG_RUNTIME_DIR")
        if not runtime_value:
            raise SwayIPCError("XDG_RUNTIME_DIR is required for the shared Wyoh session")
        self.runtime_dir = Path(runtime_value).resolve()
        try:
            descriptor_stat = self.descriptor.stat()
        except FileNotFoundError as error:
            raise SwayIPCError("the named Wyoh Sway/WayVNC service is not ready") from error
        if not stat.S_ISREG(descriptor_stat.st_mode):
            raise SwayIPCError("shared-session descriptor is not a regular file")
        if descriptor_stat.st_uid != os.getuid() or descriptor_stat.st_mode & 0o077:
            raise SwayIPCError("shared-session descriptor is not owner-private")
        try:
            contents = json.loads(self.descriptor.read_text(encoding="utf-8"))
            socket_path = Path(contents["sway_socket"]).resolve()
            wayland_display = str(contents["wayland_display"])
        except (KeyError, TypeError, json.JSONDecodeError) as error:
            raise SwayIPCError("shared-session descriptor is malformed") from error
        if socket_path.parent != self.runtime_dir or not stat.S_ISSOCK(socket_path.stat().st_mode):
            raise SwayIPCError("shared-session descriptor does not name a runtime Sway socket")
        if "/" in wayland_display or not wayland_display:
            raise SwayIPCError("shared-session descriptor has an unsafe Wayland display name")
        self.socket_path = str(socket_path)
        self.wayland_display = wayland_display
        return self.socket_path

    @property
    def state(self) -> str:
        if self.socket_path is None:
            return "not-started"
        try:
            return "running" if stat.S_ISSOCK(Path(self.socket_path).stat().st_mode) else "stopped"
        except FileNotFoundError:
            return "stopped"

    def stop(self) -> None:
        """A client disconnect must never stop the shared service."""

    def capture_screenshot(self, image_format: str = "png", quality: int = 90) -> dict[str, Any]:
        if image_format not in ("png", "jpeg") or not 1 <= quality <= 100:
            raise ValueError("image_format must be png or jpeg, quality 1-100")
        if self.state != "running" or self.runtime_dir is None or self.wayland_display is None:
            raise SwayIPCError("the shared Sway/WayVNC session is not running")
        # Microseconds keep consecutive captures within one second distinct.
        stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S.%fZ")
        result_dir = Path.home() / ".local/state/tanstfaafllm/results/wyoh/screenshots" / stamp
        result_dir.mkdir(parents=True, mode=0o700)
        screenshot = result_dir / ("desktop.png" if image_format == "png" else "desktop.jpg")
        environment = os.environ.copy()
        environment.update({"XDG_RUNTIME_DIR": str(self.runtime_dir), "WAYLAND_DISPLAY": self.wayland_display})
        completed = subprocess.run(
            ["/usr/bin/grim", "-t", image_format, *(["-q", str(quality)] if image_format == "jpeg" else []),
             str(screenshot)], env=environment, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, timeout=15.0, check=False,
        )
        (result_dir / "grim.stderr.log").write_text(completed.stderr, encoding="utf-8")
        if completed.returncode != 0 or not screenshot.is_file() or screenshot.stat().st_size == 0:
            raise SwayIPCError(f"grim did not produce a screenshot; see {result_dir / 'grim.stderr.log'}")
        return {
            "path": str(screenshot),
            "bytes": screenshot.stat().st_size,
            "sha256": hashlib.sha256(screenshot.read_bytes()).hexdigest(),
            "captured_at_utc": stamp,
        }


@dataclass
class Subscription:
    event_names: tuple[str, ...]
    ipc: SwayIPC


IPCFactory = Callable[[str], SwayIPC]


class SwayBridge:
    """Maps each documented Sway request/event to a controlled owned socket."""

    def __init__(
        self,
        session: HeadlessSwaySession | SharedVncSwaySession,
        socket_path: str,
        *,
        ipc_factory: IPCFactory = SwayIPC,
    ) -> None:
        self.session = session
        self.socket_path = socket_path
        self.ipc_factory = ipc_factory
        self.subscriptions: dict[str, Subscription] = {}

    def _request(self, message_type: int, payload: str = "") -> Any:
        if self.session.state != "running":
            raise SwayIPCError("owned Sway child is not running")
        ipc = self.ipc_factory(self.socket_path)
        try:
            return ipc.request(message_type, payload)
        finally:
            ipc.close()

    def request(self, tool_name: str, payload: str = "") -> Any:
        try:
            message_type = REQUEST_TYPES[tool_name]
        except KeyError as error:
            raise ValueError(f"unknown Sway IPC tool: {tool_name}") from error
        return self._request(message_type, payload)

    def subscribe(self, event_names: Sequence[str]) -> dict[str, Any]:
        normalized = tuple(event_names)
        if not normalized:
            raise ValueError("at least one Sway event name is required")
        unknown = sorted(set(normalized) - EVENT_TYPES.keys())
        if unknown:
            raise ValueError(f"unsupported Sway event names: {unknown}")
        if len(set(normalized)) != len(normalized):
            raise ValueError("Sway event names must be unique")
        if self.session.state != "running":
            raise SwayIPCError("owned Sway child is not running")
        ipc = self.ipc_factory(self.socket_path)
        try:
            reply = ipc.request(REQUEST_TYPES["sway_subscribe"], json.dumps(normalized))
        except Exception:
            ipc.close()
            raise
        if reply != {"success": True}:
            ipc.close()
            raise SwayIPCError(f"Sway rejected subscription: {reply!r}")
        subscription_id = uuid.uuid4().hex
        self.subscriptions[subscription_id] = Subscription(normalized, ipc)
        return {"subscription_id": subscription_id, "events": list(normalized), "reply": reply}

    def next_event(self, subscription_id: str, timeout_seconds: float = 5.0) -> dict[str, Any]:
        if not 0.01 <= timeout_seconds <= 30.0:
            raise ValueError("timeout_seconds must be between 0.01 and 30")
        try:
            subscription = self.subscriptions[subscription_id]
        except KeyError as error:
            raise ValueError("unknown or closed subscription") from error
        try:
            message_type, payload = subscription.ipc.receive(timeout_seconds)
        except TimeoutError:
            return {
                "timeout": True,
                "timeout_seconds": timeout_seconds,
                "subscription_id": subscription_id,
            }
        if not message_type & EVENT_BIT:
            raise SwayIPCError(f"subscription returned non-event message type {message_type}")
        event_name = next((name for name, value in EVENT_TYPES.items() if value == message_type), None)
        if event_name is None:
            raise SwayIPCError(f"received undocumented Sway event type {message_type}")
        return {"event": event_name, "payload": payload}

    def unsubscribe(self, subscription_id: str) -> dict[str, Any]:
        subscription = self.subscriptions.pop(subscription_id, None)
        if subscription is None:
            raise ValueError("unknown or closed subscription")
        subscription.ipc.close()
        return {"subscription_id": subscription_id, "closed": True}

    def close(self) -> None:
        for subscription in self.subscriptions.values():
            subscription.ipc.close()
        self.subscriptions.clear()

    def status(self) -> dict[str, Any]:
        return {
            "mcp_sdk_version": importlib.metadata.version("mcp"),
            "mcp_protocol_baseline": "2026-07-28",
            "session_kind": self.session.kind,
            "sway_child_pid": self.session.process.pid if self.session.process else None,
            "sway_child_state": self.session.state,
            "full_ipc_development_mode": True,
            "active_subscription_count": len(self.subscriptions),
        }

    def capture_screenshot(self, image_format: str = "png", quality: int = 90) -> dict[str, Any]:
        if not isinstance(self.session, SharedVncSwaySession):
            raise SwayIPCError("screenshots require --shared-vnc-session")
        return self.session.capture_screenshot(image_format, quality)

    def stop_owned_child_for_test(self) -> dict[str, Any]:
        """Terminate only the bridge-owned child for shutdown-event evidence."""
        if not self.session.is_bridge_owned:
            raise SwayIPCError("the shared Sway/WayVNC service cannot be stopped through MCP")
        if self.session.state != "running":
            raise SwayIPCError("owned Sway child is not running")
        self.session.stop()
        return {"stopped": True, "sway_child_state": self.session.state}


_BRIDGE: SwayBridge | None = None


def _bridge() -> SwayBridge:
    if _BRIDGE is None:
        raise RuntimeError("Wyoh full-IPC development bridge is not running")
    return _BRIDGE


mcp = MCPServer(
    "wyoh-full-sway-ipc",
    version="0.1.0",
    instructions=(
        "Development-only full Sway IPC for an owned disposable headless child. "
        "Never use this as a product or consumer desktop-control capability."
    ),
)


@mcp.tool()
def sway_command(command: str) -> Any:
    """Run a Sway command only in the owned disposable headless child."""
    return _bridge().request("sway_command", command)


@mcp.tool()
def sway_get_workspaces() -> Any:
    """Return Sway's raw GET_WORKSPACES reply."""
    return _bridge().request("sway_get_workspaces")


@mcp.tool()
def sway_get_outputs() -> Any:
    """Return Sway's raw GET_OUTPUTS reply."""
    return _bridge().request("sway_get_outputs")


@mcp.tool()
def sway_get_tree() -> Any:
    """Return Sway's raw GET_TREE reply."""
    return _bridge().request("sway_get_tree")


@mcp.tool()
def sway_get_marks() -> Any:
    """Return Sway's raw GET_MARKS reply."""
    return _bridge().request("sway_get_marks")


@mcp.tool()
def sway_get_bar_config(bar_id: str = "") -> Any:
    """Return Sway's raw GET_BAR_CONFIG reply, optionally for one bar ID."""
    return _bridge().request("sway_get_bar_config", bar_id)


@mcp.tool()
def sway_get_version() -> Any:
    """Return Sway's raw GET_VERSION reply."""
    return _bridge().request("sway_get_version")


@mcp.tool()
def sway_get_binding_modes() -> Any:
    """Return Sway's raw GET_BINDING_MODES reply."""
    return _bridge().request("sway_get_binding_modes")


@mcp.tool()
def sway_get_config() -> Any:
    """Return Sway's raw GET_CONFIG reply from the owned child."""
    return _bridge().request("sway_get_config")


@mcp.tool()
def sway_send_tick(payload: str = "") -> Any:
    """Send a Sway tick with an optional payload to the owned child."""
    return _bridge().request("sway_send_tick", payload)


@mcp.tool()
def sway_sync() -> Any:
    """Return Sway's documented SYNC compatibility reply."""
    return _bridge().request("sway_sync")


@mcp.tool()
def sway_get_binding_state() -> Any:
    """Return Sway's raw GET_BINDING_STATE reply."""
    return _bridge().request("sway_get_binding_state")


@mcp.tool()
def sway_get_inputs() -> Any:
    """Return Sway's raw GET_INPUTS reply."""
    return _bridge().request("sway_get_inputs")


@mcp.tool()
def sway_get_seats() -> Any:
    """Return Sway's raw GET_SEATS reply."""
    return _bridge().request("sway_get_seats")


@mcp.tool()
def sway_subscribe(event_names: list[str]) -> dict[str, Any]:
    """Subscribe to one or more documented Sway event names."""
    return _bridge().subscribe(event_names)


@mcp.tool()
def sway_next_event(subscription_id: str, timeout_seconds: float = 5.0) -> dict[str, Any]:
    """Wait for and return the next event on a Sway subscription handle."""
    return _bridge().next_event(subscription_id, timeout_seconds)


@mcp.tool()
def sway_unsubscribe(subscription_id: str) -> dict[str, Any]:
    """Close a Sway subscription handle."""
    return _bridge().unsubscribe(subscription_id)


@mcp.tool()
def wyoh_server_status() -> dict[str, Any]:
    """Return bridge lifecycle and exact MCP runtime information."""
    return _bridge().status()


@mcp.tool()
def wyoh_capture_screenshot(image_format: str = "png", quality: int = 90) -> dict[str, Any]:
    """Capture the shared session to a server-chosen file (PNG, or JPEG for slow
    links: Luna's Wi-Fi moves about 160 KB/s); no image bytes return."""
    return _bridge().capture_screenshot(image_format, quality)


@mcp.tool()
def wyoh_stop_owned_child_for_test() -> dict[str, Any]:
    """Stop the owned headless child; development lifecycle evidence only."""
    return _bridge().stop_owned_child_for_test()


# --- Development-only simulated person (Wyoh Step 5) --------------------------
# Virtual gamepad and keyboard on the target; development authority like
# `sway_command`, never a product capability. Created on first use, destroyed
# when the server exits.

_PERSON: dict[str, Any] = {}


def _person(kind: str) -> Any:
    import wyoh_virtual_input as virtual  # stdlib-only sibling module

    if kind not in _PERSON:
        device = virtual.VirtualGamepad() if kind == "gamepad" else virtual.VirtualKeyboard()
        name = virtual.GAMEPAD_NAME if kind == "gamepad" else virtual.KEYBOARD_NAME
        # A new device is only usable once the kernel lists it and libinput/Sway
        # have added it; events sent earlier are lost (first keys went missing).
        deadline = time.monotonic() + 5.0
        while f'Name="{name}"' not in Path("/proc/bus/input/devices").read_text(encoding="utf-8"):
            if time.monotonic() > deadline:
                device.close()
                raise RuntimeError(f"{name} did not appear")
            time.sleep(0.05)
        time.sleep(1.0)
        _PERSON[kind] = device
    return _PERSON[kind]


def _close_person() -> None:
    for device in _PERSON.values():
        device.close()
    _PERSON.clear()


def _check_buttons(buttons: list[str]) -> None:
    import wyoh_gamepad

    unknown = [name for name in buttons if name not in wyoh_gamepad.BUTTONS]
    if unknown:
        raise ValueError(f"unknown gamepad buttons: {unknown}")


@mcp.tool()
def wyoh_dev_gamepad_tap(buttons: list[str], hold_seconds: float = 0.08) -> dict[str, Any]:
    """Development only: press buttons in order, hold, release in reverse."""
    _check_buttons(buttons)
    if not 0 <= hold_seconds <= 10:
        raise ValueError("hold_seconds must be between 0 and 10")
    _person("gamepad").tap(buttons, hold_seconds)
    return {"tapped": buttons, "hold_seconds": hold_seconds}


@mcp.tool()
def wyoh_dev_gamepad_buttons(press: list[str] | None = None, release: list[str] | None = None) -> dict[str, Any]:
    """Development only: press and/or release buttons without the other half (e.g. hold FN)."""
    press, release = press or [], release or []
    _check_buttons(press + release)
    gamepad = _person("gamepad")
    gamepad.buttons(press, True)
    gamepad.buttons(release, False)
    return {"pressed": press, "released": release}


@mcp.tool()
def wyoh_dev_gamepad_stick(x: int, y: int, seconds: float, stick: str = "left") -> dict[str, Any]:
    """Development only: deflect a stick (raw units, ±1800) for some seconds, then centre it."""
    if stick not in ("left", "right") or not 0 < seconds <= 10:
        raise ValueError("stick must be left/right and seconds within (0, 10]")
    axes = ("ABS_X", "ABS_Y") if stick == "left" else ("ABS_RX", "ABS_RY")
    gamepad = _person("gamepad")
    gamepad.stick(*axes, x, y)
    time.sleep(seconds)
    gamepad.stick(*axes, 0, 0)
    return {"stick": stick, "x": x, "y": y, "seconds": seconds}


@mcp.tool()
def wyoh_dev_keyboard_type(text: str) -> dict[str, Any]:
    """Development only: type text on the virtual AZERTY keyboard (the USB keyboard stand-in)."""
    _person("keyboard").type(text)
    return {"typed_characters": len(text)}


@mcp.tool()
def wyoh_dev_keyboard_key(name: str) -> dict[str, Any]:
    """Development only: press and release one named key (enter, esc, backspace, tab, ...)."""
    _person("keyboard").press(name)
    return {"key": name}


@mcp.tool()
def wyoh_gamepad_status() -> dict[str, Any]:
    """Read the gamepad daemon's status file (no typed text is ever in it)."""
    path = Path("/run/wyoh/gamepad.json")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {"running": False}


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full-ipc-development", action="store_true")
    parser.add_argument("--shared-vnc-session", action="store_true")
    parser.add_argument("--sway-binary")
    parser.add_argument("--library-path")
    return parser.parse_args()


def main() -> int:
    global _BRIDGE
    arguments = _arguments()
    if not arguments.full_ipc_development:
        raise SystemExit("refusing to start without --full-ipc-development")
    if os.environ.get("SWAYSOCK") or os.environ.get("I3SOCK"):
        raise SystemExit("refusing ambient Sway socket variables; the bridge owns its child socket")
    if arguments.shared_vnc_session:
        session: HeadlessSwaySession | SharedVncSwaySession = SharedVncSwaySession()
    else:
        if not arguments.sway_binary or not arguments.library_path:
            raise SystemExit("--sway-binary and --library-path are required for an ephemeral child")
        session = HeadlessSwaySession(arguments.sway_binary, arguments.library_path)
    try:
        socket_path = session.start()
        _BRIDGE = SwayBridge(session, socket_path)
        mcp.run(transport="stdio")
    finally:
        _close_person()
        if _BRIDGE is not None:
            _BRIDGE.close()
        session.stop()
        _BRIDGE = None
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
