from __future__ import annotations

import asyncio
import json
import os
import select
import socket
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client
from PIL import Image, ImageChops


REMOTE_VENV = "/home/michael/.local/opt/wyoh-mcp-2.2.0"
REMOTE_DEPLOYED_SERVER = "/home/michael/.local/share/tanstfaafllm/wyoh/wyoh_mcp_server.py"
VNC_CAPTURE = Path("test/luna/capture_vnc.py")
VNC_TUNNEL_PORT = 5901


def _tool_payload(result: Any) -> Any:
    if result.structured_content is not None:
        return result.structured_content
    if len(result.content) == 1 and hasattr(result.content[0], "text"):
        return json.loads(result.content[0].text)
    return result.content


def _wait_for_tunnel(tunnel: subprocess.Popen[str]) -> None:
    deadline = time.monotonic() + 15.0
    while time.monotonic() < deadline:
        if tunnel.poll() is not None:
            stderr = tunnel.stderr.read() if tunnel.stderr else ""
            raise AssertionError(f"SSH VNC tunnel exited early: {stderr}")
        try:
            with socket.create_connection(("127.0.0.1", VNC_TUNNEL_PORT), timeout=0.2):
                return
        except OSError:
            select.select([], [], [], 0.05)
    raise AssertionError("SSH VNC tunnel did not become reachable within 15 seconds")


def _capture_vnc(result_dir: Path, name: str) -> Path:
    image = result_dir / f"{name}.png"
    completed = subprocess.run(
        [
            sys.executable,
            str(VNC_CAPTURE),
            "--host",
            "127.0.0.1",
            "--port",
            str(VNC_TUNNEL_PORT),
            "--output",
            str(image),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
        timeout=20,
    )
    (result_dir / f"{name}.capture.stdout.log").write_text(completed.stdout, encoding="utf-8")
    assert completed.returncode == 0, completed.stdout
    return image


@pytest.mark.live
def test_luna_pi_vnc_frame_changes_for_the_mcp_launched_terminal() -> None:
    """A VNC client must see the one Sway session operated through MCP."""
    if os.environ.get("WYOH_SHARED_VNC_LIVE") != "1":
        pytest.skip("set WYOH_SHARED_VNC_LIVE=1 after `make wyoh-activate`")
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    result_dir = Path("results/wyoh/shared-sway-vnc-vnc") / timestamp
    result_dir.mkdir(parents=True, exist_ok=False)
    tunnel = subprocess.Popen(
        [
            "ssh",
            "-N",
            "-o",
            "BatchMode=yes",
            "-o",
            "ExitOnForwardFailure=yes",
            "-L",
            f"{VNC_TUNNEL_PORT}:127.0.0.1:5900",
            "luna-pi",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        _wait_for_tunnel(tunnel)
        before = _capture_vnc(result_dir, "before-terminal")

        async def exercise() -> dict[str, Any]:
            parameters = StdioServerParameters(
                command="ssh",
                args=[
                    "-T",
                    "-o",
                    "BatchMode=yes",
                    "-o",
                    "ConnectTimeout=10",
                    "luna-pi",
                    f"{REMOTE_VENV}/bin/python",
                    REMOTE_DEPLOYED_SERVER,
                    "--full-ipc-development",
                    "--shared-vnc-session",
                ],
            )
            with (result_dir / "server.stderr.log").open("w", encoding="utf-8") as stderr_log:
                async with Client(stdio_client(parameters, errlog=stderr_log), read_timeout_seconds=15.0) as client:
                    subscription_result = await client.call_tool("sway_subscribe", {"event_names": ["window"]})
                    assert not subscription_result.is_error, subscription_result.content
                    subscription = _tool_payload(subscription_result)
                    command_result = await client.call_tool("sway_command", {"command": "exec /usr/bin/lxterminal"})
                    assert not command_result.is_error, command_result.content
                    try:
                        for _ in range(8):
                            event_result = await client.call_tool(
                                "sway_next_event",
                                {"subscription_id": subscription["subscription_id"], "timeout_seconds": 3.0},
                            )
                            assert not event_result.is_error, event_result.content
                            event = _tool_payload(event_result)
                            if event.get("event") == "window" and event["payload"].get("change") in {"new", "focus"}:
                                after = _capture_vnc(result_dir, "terminal-visible")
                                return {"event": event, "after": str(after)}
                        raise AssertionError("did not observe an lxterminal window event")
                    finally:
                        close_result = await client.call_tool("sway_command", {"command": "kill"})
                        assert not close_result.is_error, close_result.content
                        unsubscribe_result = await client.call_tool(
                            "sway_unsubscribe", {"subscription_id": subscription["subscription_id"]}
                        )
                        assert not unsubscribe_result.is_error, unsubscribe_result.content

        evidence = asyncio.run(exercise())
        with Image.open(before) as before_raw, Image.open(evidence["after"]) as after_raw:
            before_image = before_raw.convert("RGB")
            after_image = after_raw.convert("RGB")
            assert before_image.size == after_image.size
            assert ImageChops.difference(before_image, after_image).getbbox() is not None, (
                "VNC frame did not change after MCP launched lxterminal"
            )
        (result_dir / "evidence.json").write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
    finally:
        tunnel.terminate()
        try:
            tunnel.wait(timeout=5.0)
        except subprocess.TimeoutExpired:
            tunnel.kill()
            tunnel.wait(timeout=5.0)
        if tunnel.stderr:
            (result_dir / "ssh-tunnel.stderr.log").write_text(tunnel.stderr.read(), encoding="utf-8")
