"""Step 3.7: operate the minimal Wyoh luna-pi session through MCP.

Contract: `minimal_env.feature`. Every session action is an MCP tool call on
the shared Wyoh service; SSH is used only to fetch evidence and to check the
marker file's side effect. Images are saved per step for visual inspection.
"""

from __future__ import annotations

import asyncio
import json
import os
import socket
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

import pytest
from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client
from PIL import Image, ImageChops


HOST = "luna-pi"
REMOTE_VENV = "/home/michael/.local/opt/wyoh-mcp-2.2.0"
REMOTE_DEPLOYED_SERVER = "/home/michael/.local/share/tanstfaafllm/wyoh/wyoh_mcp_server.py"
VNC_TUNNEL_PORT = 5903
# `output * bg #1f2430 solid_color` and the swaybar background in sway-vnc.conf.
BACKGROUND = (31, 36, 48)
BAR = (50, 50, 50)
OUTPUT = (720, 720)
RENDER_TIMEOUT = 15.0

Predicate = Callable[[Image.Image], bool]


def _tool_payload(result: Any) -> Any:
    if result.structured_content is not None:
        content = result.structured_content
        # The SDK wraps tool results declared as `Any` in {"result": ...}.
        if isinstance(content, dict) and set(content) == {"result"}:
            return content["result"]
        return content
    # Without structured content the SDK sends a list as one text block per
    # element, so a one-element list arrives looking like its single element.
    texts = [json.loads(item.text) for item in result.content if hasattr(item, "text")]
    return texts[0] if len(texts) == 1 else texts


def _ssh(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", HOST, command],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30, check=False,
    )


def _app_windows(tree: dict[str, Any]) -> list[dict[str, Any]]:
    """Application containers with the workspace that holds them."""
    found: list[dict[str, Any]] = []

    def walk(node: dict[str, Any], workspace: str | None) -> None:
        if node.get("type") == "workspace":
            workspace = node.get("name")
        if node.get("pid") and node.get("type") in {"con", "floating_con"}:
            found.append({
                "id": node["id"],
                "app_id": node.get("app_id") or (node.get("window_properties") or {}).get("class"),
                "workspace": workspace,
                "rect": node["rect"],
                "visible": node.get("visible"),
                "fullscreen_mode": node.get("fullscreen_mode"),
                "focused": node.get("focused"),
            })
        for child in node.get("nodes", []) + node.get("floating_nodes", []):
            walk(child, workspace)

    walk(tree, None)
    return found


def _fraction(image: Image.Image, rect: dict[str, int], colour: tuple[int, int, int]) -> float:
    box = (rect["x"], rect["y"], rect["x"] + rect["width"], rect["y"] + rect["height"])
    region = image.convert("RGB").crop(box)
    pixels = region.width * region.height
    if pixels == 0:
        return 1.0
    matching = sum(count for count, value in (region.getcolors(pixels) or []) if value == colour)
    return matching / pixels


def _drawn(rect: dict[str, int]) -> Predicate:
    """The window rectangle no longer shows the desktop background."""
    return lambda image: _fraction(image, rect, BACKGROUND) < 0.2


BODY = {"x": 0, "y": 30, "width": OUTPUT[0], "height": OUTPUT[1] - 30}
BAR_ROW = {"x": 0, "y": 0, "width": OUTPUT[0], "height": 20}


def _empty_desktop(image: Image.Image) -> bool:
    return _fraction(image, BODY, BACKGROUND) > 0.99 and _fraction(image, BAR_ROW, BAR) > 0.5


class VncObserver:
    """An independent VNC client over a temporary loopback SSH tunnel."""

    def __init__(self, result_dir: Path) -> None:
        self.result_dir = result_dir
        self.tunnel = subprocess.Popen(
            ["ssh", "-N", "-o", "BatchMode=yes", "-o", "ExitOnForwardFailure=yes",
             "-L", f"{VNC_TUNNEL_PORT}:127.0.0.1:5900", HOST],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        deadline = time.monotonic() + 15.0
        while True:
            if self.tunnel.poll() is not None:
                raise AssertionError(f"VNC tunnel exited: {self.tunnel.stderr.read() if self.tunnel.stderr else ''}")
            try:
                with socket.create_connection(("127.0.0.1", VNC_TUNNEL_PORT), timeout=0.2):
                    break
            except OSError:
                if time.monotonic() > deadline:
                    raise AssertionError("VNC tunnel did not become reachable")
                time.sleep(0.05)
        from vncdotool import api

        self.api = api
        self.client = api.connect(f"127.0.0.1::{VNC_TUNNEL_PORT}", timeout=15)
        # WayVNC answers the first request with a uniform placeholder frame.
        self.client.captureScreen(str(result_dir / "vnc-placeholder.png"))

    def keys(self, *names: str) -> None:
        """Send key presses as a person at the VNC viewer would."""
        for name in names:
            self.client.keyPress(name)

    def capture(self, path: Path) -> Image.Image:
        self.client.captureScreen(str(path))
        with Image.open(path) as image:
            return image.convert("RGB")

    def close(self) -> None:
        try:
            self.client.disconnect()
        finally:
            self.api.shutdown()
            self.tunnel.terminate()
            try:
                self.tunnel.wait(timeout=5.0)
            except subprocess.TimeoutExpired:
                self.tunnel.kill()
            if self.tunnel.stderr:
                (self.result_dir / "ssh-tunnel.stderr.log").write_text(self.tunnel.stderr.read(), encoding="utf-8")


@pytest.mark.live
def test_minimal_environment_is_operated_through_mcp() -> None:
    if os.environ.get("WYOH_SHARED_VNC_LIVE") != "1":
        pytest.skip("set WYOH_SHARED_VNC_LIVE=1 with the Step 3.7 service deployed")
    tools = _ssh("command -v foot wmenu-run wtype")
    if tools.stdout.count("\n") != 3:
        pytest.fail(f"Step 3.7 requires foot, wmenu-run, and wtype on {HOST}; found:\n{tools.stdout}")

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    result_dir = Path("results/wyoh/minimal-env") / timestamp
    result_dir.mkdir(parents=True, exist_ok=False)
    marker = f"WYOH-{timestamp}"
    marker_file = f"/tmp/wyoh-proof-{timestamp}.txt"
    evidence: dict[str, Any] = {"marker": marker, "steps": []}
    vnc = VncObserver(result_dir)

    async def exercise() -> None:
        parameters = StdioServerParameters(
            command="ssh",
            args=["-T", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", HOST,
                  f"{REMOTE_VENV}/bin/python", REMOTE_DEPLOYED_SERVER,
                  "--full-ipc-development", "--shared-vnc-session"],
        )
        with (result_dir / "server.stderr.log").open("w", encoding="utf-8") as stderr_log:
            async with Client(stdio_client(parameters, errlog=stderr_log), read_timeout_seconds=20.0) as client:

                async def call(name: str, arguments: dict[str, Any] | None = None) -> Any:
                    result = await client.call_tool(name, arguments or {})
                    assert not result.is_error, f"{name}: {result.content!r}"
                    return _tool_payload(result)

                async def command(text: str) -> None:
                    replies = await call("sway_command", {"command": text})
                    replies = replies if isinstance(replies, list) else [replies]
                    assert all(reply.get("success") for reply in replies), (text, replies)

                async def windows() -> list[dict[str, Any]]:
                    return _app_windows(await call("sway_get_tree"))

                async def mcp_screenshot(path: Path) -> Image.Image:
                    shot = await call("wyoh_capture_screenshot")
                    fetched = subprocess.run(["scp", "-q", f"{HOST}:{shot['path']}", str(path)],
                                             capture_output=True, text=True, timeout=30, check=False)
                    assert fetched.returncode == 0, fetched.stderr
                    with Image.open(path) as image:
                        return image.convert("RGB")

                async def observe(name: str, predicate: Predicate) -> None:
                    """Poll MCP and VNC images until both satisfy the step's visible end state."""
                    deadline = time.monotonic() + RENDER_TIMEOUT
                    mcp_ok = vnc_ok = False
                    while True:
                        if not mcp_ok:
                            mcp_ok = predicate(await mcp_screenshot(result_dir / f"{name}.mcp.png"))
                        if not vnc_ok:
                            vnc_ok = predicate(vnc.capture(result_dir / f"{name}.vnc.png"))
                        if mcp_ok and vnc_ok:
                            break
                        assert time.monotonic() < deadline, f"{name}: mcp_ok={mcp_ok} vnc_ok={vnc_ok}"
                        await asyncio.sleep(0.2)
                    evidence["steps"].append({"step": name, "windows": await windows()})

                async def new_window(subscription_id: str, app_id: str) -> dict[str, Any]:
                    for _ in range(20):
                        event = await call("sway_next_event", {"subscription_id": subscription_id, "timeout_seconds": 3.0})
                        payload = event.get("payload") or {}
                        container = payload.get("container") or {}
                        if event.get("event") == "window" and payload.get("change") == "new" and app_id in (container.get("app_id") or ""):
                            return container
                    raise AssertionError(f"no new {app_id} window")

                async def window(con_id: int) -> dict[str, Any]:
                    matches = [item for item in await windows() if item["id"] == con_id]
                    assert len(matches) == 1, (con_id, matches)
                    return matches[0]

                assert await windows() == [], "the session must start without application windows"
                await command("workspace number 1")
                await observe("00-empty", _empty_desktop)

                subscription = (await call("sway_subscribe", {"event_names": ["window"]}))["subscription_id"]
                try:
                    # 1 — terminal
                    await command("exec foot")
                    terminal_id = (await new_window(subscription, "foot"))["id"]
                    terminal = await window(terminal_id)
                    await observe("01-terminal", _drawn(terminal["rect"]))

                    # 2 — type a command into the focused terminal and check its side effect
                    before_typing = Image.open(result_dir / "01-terminal.mcp.png").convert("RGB")
                    await command(f"[con_id={terminal_id}] focus")
                    await command(f"exec wtype 'echo {marker} > {marker_file}' -k Return")
                    deadline = time.monotonic() + RENDER_TIMEOUT
                    while _ssh(f"cat {marker_file}").stdout.strip() != marker:
                        assert time.monotonic() < deadline, "marker file was not written by the typed command"
                        await asyncio.sleep(0.2)
                    rect = terminal["rect"]
                    box = (rect["x"], rect["y"], rect["x"] + rect["width"], rect["y"] + rect["height"])
                    await observe("02-typed", lambda image: ImageChops.difference(image.crop(box), before_typing.crop(box)).getbbox() is not None)

                    # 3 — a person at the VNC viewer uses the launcher on workspace 2.
                    # (wmenu 0.1.9 aborts on the keymap change caused by a transient
                    # `wtype` keyboard, so the launcher is driven through WayVNC's
                    # persistent keyboard; MCP observes the result.)
                    await command("workspace number 2")
                    vnc.keys("alt-d")
                    await observe("03a-launcher", lambda image: _fraction(image, BAR_ROW, BAR) < 0.5)
                    vnc.keys(*"mousepad", "enter")
                    editor_id = (await new_window(subscription, "mousepad"))["id"]
                    editor = await window(editor_id)
                    assert editor["workspace"] == "2", editor
                    await observe("03b-editor-ws2", _drawn(editor["rect"]))

                    # 4 — move the editor beside the terminal
                    await command(f"[con_id={editor_id}] move container to workspace number 1")
                    await command("workspace number 1")
                    terminal, editor = await window(terminal_id), await window(editor_id)
                    assert terminal["workspace"] == editor["workspace"] == "1"
                    assert terminal["rect"]["x"] != editor["rect"]["x"], (terminal, editor)
                    await observe("04-split", lambda image: _drawn(terminal["rect"])(image) and _drawn(editor["rect"])(image))

                    # 5 — fullscreen the editor
                    await command(f"[con_id={editor_id}] fullscreen enable")
                    editor = await window(editor_id)
                    assert editor["fullscreen_mode"] == 1 and editor["rect"]["height"] == OUTPUT[1], editor
                    await observe("05-fullscreen", lambda image: _fraction(image, BAR_ROW, BAR) < 0.5)
                    await command(f"[con_id={editor_id}] fullscreen disable")

                    # 6 — a person at the VNC viewer opens and closes a terminal with the bindings
                    vnc.keys("alt-enter")
                    second_id = (await new_window(subscription, "foot"))["id"]
                    second = await window(second_id)
                    await observe("06-vnc-terminal", _drawn(second["rect"]))
                    vnc.keys("alt-shift-Q")  # a real viewer sends the shifted keysym
                    deadline = time.monotonic() + RENDER_TIMEOUT
                    while any(item["id"] == second_id for item in await windows()):
                        assert time.monotonic() < deadline, "Alt+Shift+q over VNC did not close the terminal"
                        await asyncio.sleep(0.2)
                finally:
                    # 7 — close by con_id only; never the focused-window `kill`
                    for item in await windows():
                        await command(f"[con_id={item['id']}] kill")
                    await call("sway_unsubscribe", {"subscription_id": subscription})
                    _ssh(f"rm -f {marker_file}")

                deadline = time.monotonic() + RENDER_TIMEOUT
                while await windows():
                    assert time.monotonic() < deadline, "windows remained after close"
                    await asyncio.sleep(0.2)
                await observe("07-empty", _empty_desktop)

    try:
        asyncio.run(exercise())
    finally:
        vnc.close()
        (result_dir / "evidence.json").write_text(json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8")
    assert _ssh(f"test -e {marker_file}").returncode != 0
