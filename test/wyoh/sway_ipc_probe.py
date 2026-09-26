#!/usr/bin/env python3
"""Minimal Sway IPC probe used by the Wyoh pytest suite.

The module uses only the documented Unix-socket protocol so the proof does not
introduce a production dependency.  It can run in a supplied Sway session or
start a short-lived headless session for a live device check.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import select
import socket
import struct
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MAGIC = b"i3-ipc"
RUN_COMMAND = 0
GET_WORKSPACES = 1
SUBSCRIBE = 2
GET_OUTPUTS = 3
GET_TREE = 4
GET_VERSION = 7
GET_INPUTS = 100
GET_SEATS = 101
EVENT_BIT = 1 << 31
WORKSPACE_EVENT = EVENT_BIT | 0
SAFE_WORKSPACE = re.compile(r"[A-Za-z0-9_-]{1,64}\Z")


class IPCError(RuntimeError):
    """The Sway IPC socket sent malformed or unsuccessful data."""


def _recv_exact(connection: socket.socket, size: int) -> bytes:
    data = bytearray()
    while len(data) < size:
        chunk = connection.recv(size - len(data))
        if not chunk:
            raise IPCError("Sway IPC socket closed before a complete reply")
        data.extend(chunk)
    return bytes(data)


class SwayIPC:
    """Small, documented Sway IPC client for the proof fixture only."""

    def __init__(self, socket_path: str, timeout_seconds: float = 5.0) -> None:
        self.connection = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.connection.settimeout(timeout_seconds)
        self.connection.connect(socket_path)

    def close(self) -> None:
        self.connection.close()

    def _send(self, message_type: int, payload: str = "") -> None:
        encoded = payload.encode("utf-8")
        header = MAGIC + struct.pack("=II", len(encoded), message_type)
        self.connection.sendall(header + encoded)

    def _receive(self) -> tuple[int, Any]:
        header = _recv_exact(self.connection, 14)
        if header[:6] != MAGIC:
            raise IPCError("unexpected IPC magic")
        length, message_type = struct.unpack("=II", header[6:])
        payload = _recv_exact(self.connection, length)
        try:
            return message_type, json.loads(payload.decode("utf-8"))
        except json.JSONDecodeError as error:
            raise IPCError("Sway IPC reply was not JSON") from error

    def request(self, message_type: int, payload: str = "") -> Any:
        self._send(message_type, payload)
        reply_type, reply = self._receive()
        if reply_type != message_type:
            raise IPCError(f"reply type {reply_type} did not match {message_type}")
        return reply

    def command(self, command: str) -> list[dict[str, Any]]:
        reply = self.request(RUN_COMMAND, command)
        if not isinstance(reply, list) or not reply or not all(item.get("success") for item in reply):
            raise IPCError(f"Sway rejected command {command!r}: {reply!r}")
        return reply

    def subscribe_workspace(self) -> None:
        reply = self.request(SUBSCRIBE, json.dumps(["workspace"]))
        if reply != {"success": True}:
            raise IPCError(f"workspace subscription rejected: {reply!r}")

    def wait_for_workspace_focus_event(self, workspace: str, timeout_seconds: float) -> dict[str, Any]:
        deadline = time.monotonic() + timeout_seconds
        ignored: list[dict[str, Any]] = []
        while time.monotonic() < deadline:
            self.connection.settimeout(max(0.01, deadline - time.monotonic()))
            message_type, payload = self._receive()
            if (
                message_type == WORKSPACE_EVENT
                and isinstance(payload, dict)
                and payload.get("change") == "focus"
                and payload.get("current", {}).get("name") == workspace
            ):
                return payload
            if message_type == WORKSPACE_EVENT and isinstance(payload, dict):
                ignored.append(payload)
        raise IPCError(f"workspace focus event for {workspace!r} was not observed; ignored={ignored!r}")


@dataclass(frozen=True)
class FocusWorkspaceRequest:
    workspace: str
    expected_revision: int
    allowed: bool


class FocusWorkspaceMediator:
    """Consumer capability boundary: no arbitrary Sway command crosses it."""

    def invoke(self, transport: Any, request: FocusWorkspaceRequest, revision: int) -> None:
        if not request.allowed:
            raise PermissionError("workspace focus capability is not granted")
        if request.expected_revision != revision:
            raise ValueError("stale workspace request")
        if not SAFE_WORKSPACE.fullmatch(request.workspace):
            raise ValueError("workspace selector is unavailable or ambiguous")
        transport.command(f"workspace {request.workspace}")


def _snapshot(ipc: SwayIPC, revision: int) -> dict[str, Any]:
    return {
        "revision": revision,
        "version": ipc.request(GET_VERSION),
        "outputs": ipc.request(GET_OUTPUTS),
        "tree": ipc.request(GET_TREE),
        "workspaces": ipc.request(GET_WORKSPACES),
        "inputs": ipc.request(GET_INPUTS),
        "seats": ipc.request(GET_SEATS),
        "captured_monotonic_ns": time.monotonic_ns(),
    }


def _focused_workspace(snapshot: dict[str, Any]) -> str | None:
    matches = [item["name"] for item in snapshot["workspaces"] if item.get("focused")]
    if len(matches) != 1:
        return None
    return matches[0]


def exercise_sway(socket_path: str, workspace: str = "wyoh-proof") -> dict[str, Any]:
    """Read state, focus an allowlisted workspace, and wait for its event."""
    query = SwayIPC(socket_path)
    events = SwayIPC(socket_path)
    try:
        before = _snapshot(query, revision=1)
        events.subscribe_workspace()
        start_ns = time.monotonic_ns()
        FocusWorkspaceMediator().invoke(
            query,
            FocusWorkspaceRequest(workspace=workspace, expected_revision=1, allowed=True),
            revision=1,
        )
        event = events.wait_for_workspace_focus_event(workspace, timeout_seconds=5.0)
        event_latency_ms = (time.monotonic_ns() - start_ns) / 1_000_000
        after = _snapshot(query, revision=2)
    finally:
        events.close()
        query.close()
    focused = _focused_workspace(after)
    if focused != workspace:
        raise IPCError(f"workspace focus predicate was not observed: {focused!r}")
    return {
        "before": before,
        "after": after,
        "event": event,
        "event_latency_ms": event_latency_ms,
        "focused_workspace": focused,
    }


def _metrics(pid: int) -> dict[str, int]:
    status = Path(f"/proc/{pid}/status").read_text(encoding="utf-8")
    rss_kib = next(
        int(line.split()[1]) for line in status.splitlines() if line.startswith("VmRSS:")
    )
    fields = Path(f"/proc/{pid}/stat").read_text(encoding="utf-8").split()
    return {"rss_kib": rss_kib, "cpu_ticks": int(fields[13]) + int(fields[14])}


def _wait_for_new_socket(runtime_dir: Path, previous: set[str], process: subprocess.Popen[str]) -> str:
    deadline = time.monotonic() + 10.0
    while time.monotonic() < deadline:
        candidates = set(glob.glob(str(runtime_dir / "sway-ipc.*.sock"))) - previous
        if len(candidates) == 1:
            return candidates.pop()
        if process.poll() is not None:
            stderr = process.stderr.read() if process.stderr else ""
            raise IPCError(f"headless Sway exited before its socket appeared: {stderr}")
        select.select([], [], [], 0.02)
    raise IPCError("headless Sway socket did not appear within 10 seconds")


def run_headless(sway_binary: str, library_path: str) -> dict[str, Any]:
    """Run the probe against a dedicated headless Sway child and recover it."""
    runtime_dir = Path(os.environ["XDG_RUNTIME_DIR"])
    with tempfile.TemporaryDirectory(prefix="wyoh-sway-") as temporary:
        config = Path(temporary) / "config"
        config.write_text("xwayland disable\n", encoding="utf-8")
        previous = set(glob.glob(str(runtime_dir / "sway-ipc.*.sock")))
        environment = os.environ | {
            "WLR_BACKENDS": "headless",
            "WLR_HEADLESS_OUTPUTS": "1",
            "WLR_RENDERER": "pixman",
            "LD_LIBRARY_PATH": library_path,
        }
        started_ns = time.monotonic_ns()
        process = subprocess.Popen(
            [sway_binary, "--config", str(config)],
            env=environment,
            text=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        socket_path = _wait_for_new_socket(runtime_dir, previous, process)
        ready_ms = (time.monotonic_ns() - started_ns) / 1_000_000
        idle_before = _metrics(process.pid)
        interval_start_ns = time.monotonic_ns()
        select.select([], [], [], 0.25)
        idle_after = _metrics(process.pid)
        interval_ms = (time.monotonic_ns() - interval_start_ns) / 1_000_000
        try:
            proof = exercise_sway(socket_path)
        finally:
            stopped_ns = time.monotonic_ns()
            process.terminate()
            try:
                process.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5.0)
            recovery_ms = (time.monotonic_ns() - stopped_ns) / 1_000_000
            stderr = process.stderr.read() if process.stderr else ""
    return {
        "sway_version": proof["after"]["version"].get("human_readable"),
        "ready_ms": ready_ms,
        "idle_sample": {
            "interval_ms": interval_ms,
            "rss_kib": idle_after["rss_kib"],
            "cpu_ticks_delta": idle_after["cpu_ticks"] - idle_before["cpu_ticks"],
        },
        "recovery_ms": recovery_ms,
        "sway_stderr": stderr,
        "proof": proof,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--socket")
    parser.add_argument("--start-headless", action="store_true")
    parser.add_argument("--sway-binary")
    parser.add_argument("--library-path")
    arguments = parser.parse_args()
    if arguments.start_headless:
        if not arguments.sway_binary or not arguments.library_path:
            parser.error("--start-headless requires --sway-binary and --library-path")
        result = run_headless(arguments.sway_binary, arguments.library_path)
    elif arguments.socket:
        result = exercise_sway(arguments.socket)
    else:
        parser.error("provide --socket or --start-headless")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
