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
import importlib.metadata
import json
import logging
import os
import select
import socket
import struct
import subprocess
import tempfile
import time
import uuid
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from mcp.server import MCPServer


LOGGER = logging.getLogger(__name__)
MAGIC = b"i3-ipc"
EVENT_BIT = 1 << 31

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


@dataclass
class Subscription:
    event_names: tuple[str, ...]
    ipc: SwayIPC


IPCFactory = Callable[[str], SwayIPC]


class SwayBridge:
    """Maps each documented Sway request/event to a controlled owned socket."""

    def __init__(
        self,
        session: HeadlessSwaySession,
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
            "sway_child_pid": self.session.process.pid if self.session.process else None,
            "sway_child_state": self.session.state,
            "full_ipc_development_mode": True,
            "active_subscription_count": len(self.subscriptions),
        }

    def stop_owned_child_for_test(self) -> dict[str, Any]:
        """Terminate only the bridge-owned child for shutdown-event evidence."""
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
def wyoh_stop_owned_child_for_test() -> dict[str, Any]:
    """Stop the owned headless child; development lifecycle evidence only."""
    return _bridge().stop_owned_child_for_test()


def _arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full-ipc-development", action="store_true")
    parser.add_argument("--sway-binary", required=True)
    parser.add_argument("--library-path", required=True)
    return parser.parse_args()


def main() -> int:
    global _BRIDGE
    arguments = _arguments()
    if not arguments.full_ipc_development:
        raise SystemExit("refusing to start without --full-ipc-development")
    if os.environ.get("SWAYSOCK") or os.environ.get("I3SOCK"):
        raise SystemExit("refusing ambient Sway socket variables; the bridge owns its child socket")
    session = HeadlessSwaySession(arguments.sway_binary, arguments.library_path)
    try:
        socket_path = session.start()
        _BRIDGE = SwayBridge(session, socket_path)
        mcp.run(transport="stdio")
    finally:
        if _BRIDGE is not None:
            _BRIDGE.close()
        session.stop()
        _BRIDGE = None
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
