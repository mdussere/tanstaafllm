"""Step 4.7: reproduce the luna-pi Step 3.7 run on Luna's real DSI panel.

Contract: `luna_minimal_env.feature`. The nine steps mirror
`results/wyoh/minimal-env/20261003T232433Z` on luna-pi:

* MCP actions are MCP tool calls on `wyoh-sway.service` (ArchR's Sway 1.11).
* "A person at the keyboard" is a kernel uinput keyboard
  (`uinput_keyboard.py`), which Sway handles like the USB keyboard,
  with the French layout and its `--to-code` bindings.
* Evidence is the MCP screenshot of DSI-1 after each step, taken on a
  settled frame. VNC is not used on Luna.
* The editor is `vim` in `foot` (`mousepad`/GTK was rejected as too costly;
  ArchR's stripped `nano` 8.5 ignores terminal resizes and stays 80x24).
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client
from PIL import Image, ImageChops

from test_minimal_env import BAR, BAR_ROW, RENDER_TIMEOUT, Predicate, _app_windows, _drawn, _empty_desktop, _fraction, _tool_payload


HOST = "luna"
REMOTE_VENV = "/storage/.local/opt/wyoh-mcp-2.2.0"
REMOTE_SERVER = "/storage/.local/share/tanstfaafllm/wyoh/wyoh_mcp_server.py"
RUNTIME_DIR = "/run/wyoh"
KEYBOARD = Path(__file__).with_name("uinput_keyboard.py")
REMOTE_KEYBOARD = "/tmp/wyoh-uinput-keyboard.py"
OUTPUT = (720, 720)
EDITOR_COMMAND = "foot -a wyoh-editor vim"


def _ssh(command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", HOST, command],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=30, check=False,
    )


class Person:
    """A person at Luna's keyboard and mouse: uinput devices on the target, fed over SSH."""

    def __init__(self, result_dir: Path) -> None:
        staged = subprocess.run(["scp", "-q", str(KEYBOARD), f"{HOST}:{REMOTE_KEYBOARD}"],
                                capture_output=True, text=True, timeout=30, check=False)
        assert staged.returncode == 0, staged.stderr
        self.log = (result_dir / "keyboard.log").open("w", encoding="utf-8")
        self.process = subprocess.Popen(
            ["ssh", "-T", "-o", "BatchMode=yes", HOST, "python3", "-u", REMOTE_KEYBOARD],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=self.log, text=True,
        )
        ready = self._read()
        assert ready.startswith("ready "), ready
        self.device, self.mouse = ready.split()[1:3]

    def _read(self) -> str:
        assert self.process.stdout
        line = self.process.stdout.readline().strip()
        self.log.write(f"< {line}\n")
        return line

    def _send(self, line: str) -> None:
        assert self.process.stdin
        self.log.write(f"> {line}\n")
        self.process.stdin.write(line + "\n")
        self.process.stdin.flush()
        reply = self._read()
        assert reply == "ok", (line, reply)

    def press(self, combo: str) -> None:
        self._send(f"combo {combo}")

    def type(self, text: str) -> None:
        self._send(f"type {text}")

    def home(self) -> None:
        self._send("home")

    def move(self, dx: int, dy: int) -> None:
        self._send(f"move {dx} {dy}")

    def click(self, button: str = "left") -> None:
        self._send(f"click {button}")

    def close(self) -> None:
        try:
            if self.process.poll() is None:
                self._send("quit")
            self.process.wait(timeout=10)
        finally:
            self.log.close()
            _ssh(f"rm -f {REMOTE_KEYBOARD}")


@pytest.mark.live
def test_luna_panel_reproduces_the_luna_pi_run() -> None:
    if os.environ.get("WYOH_LUNA_LIVE") != "1":
        pytest.skip("set WYOH_LUNA_LIVE=1 with `make wyoh-luna-start` running")
    state = _ssh("systemctl is-active wyoh-sway.service; test -x /storage/.local/opt/wyoh-tools/bin/wtype && echo wtype; command -v vim")
    assert state.stdout.split()[:2] == ["active", "wtype"] and "vim" in state.stdout, state.stdout + state.stderr

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    result_dir = Path("results/wyoh/luna-minimal-env") / timestamp
    result_dir.mkdir(parents=True, exist_ok=False)
    marker = f"WYOH-{timestamp}"
    marker_file = f"/tmp/wyoh-proof-{timestamp}.txt"
    steps: list[dict[str, Any]] = []
    person = Person(result_dir)

    async def exercise() -> None:
        parameters = StdioServerParameters(
            command="ssh",
            args=["-T", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", HOST,
                  "env", f"XDG_RUNTIME_DIR={RUNTIME_DIR}", f"{REMOTE_VENV}/bin/python", REMOTE_SERVER,
                  "--full-ipc-development", "--shared-vnc-session"],
        )
        with (result_dir / "server.stderr.log").open("w", encoding="utf-8") as stderr_log:
            async with Client(stdio_client(parameters, errlog=stderr_log), read_timeout_seconds=30.0) as client:

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

                async def window(con_id: int) -> dict[str, Any]:
                    matches = [item for item in await windows() if item["id"] == con_id]
                    assert len(matches) == 1, (con_id, matches)
                    return matches[0]

                async def screenshot(path: Path) -> Image.Image:
                    shot = await call("wyoh_capture_screenshot")
                    fetched = subprocess.run(["scp", "-q", f"{HOST}:{shot['path']}", str(path)],
                                             capture_output=True, text=True, timeout=30, check=False)
                    assert fetched.returncode == 0, fetched.stderr
                    with Image.open(path) as image:
                        return image.convert("RGB")

                async def observe(name: str, predicate: Predicate) -> Image.Image:
                    """Wait until the end state holds on two identical consecutive MCP
                    screenshots, so evidence never shows a client mid-redraw."""
                    deadline = time.monotonic() + RENDER_TIMEOUT
                    previous: Image.Image | None = None
                    while True:
                        image = await screenshot(result_dir / f"{name}.png")
                        settled = previous is not None and ImageChops.difference(previous, image).getbbox() is None
                        if settled and predicate(image):
                            steps.append({"step": name, "windows": await windows()})
                            return image
                        assert time.monotonic() < deadline, f"{name}: end state not reached on a settled frame"
                        previous = image
                        await asyncio.sleep(0.3)

                async def new_window(subscription_id: str, app_id: str) -> dict[str, Any]:
                    for _ in range(20):
                        event = await call("sway_next_event", {"subscription_id": subscription_id, "timeout_seconds": 3.0})
                        payload = event.get("payload") or {}
                        container = payload.get("container") or {}
                        if event.get("event") == "window" and payload.get("change") == "new" and container.get("app_id") == app_id:
                            return container
                    raise AssertionError(f"no new {app_id} window")

                inputs = await call("sway_get_inputs")
                inputs = inputs if isinstance(inputs, list) else [inputs]
                assert any(person.device in item.get("identifier", "") for item in inputs), "Sway does not see the uinput keyboard"
                assert await windows() == [], "the session must start without application windows"
                await command("workspace number 1")
                await observe("00-empty", _empty_desktop)

                subscription = (await call("sway_subscribe", {"event_names": ["window"]}))["subscription_id"]
                try:
                    # 1 — MCP opens a terminal
                    await command("exec foot")
                    terminal_id = (await new_window(subscription, "foot"))["id"]
                    terminal = await window(terminal_id)
                    before_typing = await observe("01-terminal", _drawn(terminal["rect"]))

                    # 2 — MCP types a command into it and the side effect is checked
                    await command(f"[con_id={terminal_id}] focus")
                    await command(f"exec wtype 'echo {marker} > {marker_file}' -k Return")
                    deadline = time.monotonic() + RENDER_TIMEOUT
                    while _ssh(f"cat {marker_file}").stdout.strip() != marker:
                        assert time.monotonic() < deadline, "marker file was not written by the typed command"
                        await asyncio.sleep(0.3)
                    rect = terminal["rect"]
                    box = (rect["x"], rect["y"], rect["x"] + rect["width"], rect["y"] + rect["height"])
                    await observe("02-typed", lambda image: ImageChops.difference(image.crop(box), before_typing.crop(box)).getbbox() is not None)

                    # 3 — MCP switches to workspace 2; the person opens the launcher
                    #     with Alt+d and starts the editor from it
                    await command("workspace number 2")
                    person.press("alt+d")
                    await observe("03a-launcher", lambda image: _fraction(image, BAR_ROW, BAR) < 0.5)
                    person.type(EDITOR_COMMAND)
                    person.press("enter")
                    editor_id = (await new_window(subscription, "wyoh-editor"))["id"]
                    editor = await window(editor_id)
                    assert editor["workspace"] == "2", editor
                    await observe("03b-editor-ws2", _drawn(editor["rect"]))

                    # 4 — MCP moves the editor beside the terminal
                    await command(f"[con_id={editor_id}] move container to workspace number 1")
                    await command("workspace number 1")
                    terminal, editor = await window(terminal_id), await window(editor_id)
                    assert terminal["workspace"] == editor["workspace"] == "1"
                    assert terminal["rect"]["x"] != editor["rect"]["x"], (terminal, editor)
                    await observe("04-split", lambda image: _drawn(terminal["rect"])(image) and _drawn(editor["rect"])(image))

                    # 5 — MCP makes the editor fullscreen
                    await command(f"[con_id={editor_id}] fullscreen enable")
                    editor = await window(editor_id)
                    assert editor["fullscreen_mode"] == 1 and editor["rect"]["height"] == OUTPUT[1], editor
                    await observe("05-fullscreen", lambda image: _fraction(image, BAR_ROW, BAR) < 0.5)
                    await command(f"[con_id={editor_id}] fullscreen disable")

                    # 6 — the person opens a terminal with Alt+Enter, then closes it with Alt+Shift+q
                    person.press("alt+enter")
                    third_id = (await new_window(subscription, "foot"))["id"]
                    third = await window(third_id)
                    await observe("06-person-terminal", _drawn(third["rect"]))
                    person.press("alt+shift+q")
                    deadline = time.monotonic() + RENDER_TIMEOUT
                    while any(item["id"] == third_id for item in await windows()):
                        assert time.monotonic() < deadline, "Alt+Shift+q did not close the terminal"
                        await asyncio.sleep(0.2)
                finally:
                    # 7 — MCP closes every remaining window by con_id
                    for item in await windows():
                        await command(f"[con_id={item['id']}] kill")
                    await call("sway_unsubscribe", {"subscription_id": subscription})
                    _ssh(f"rm -f {marker_file}")

                deadline = time.monotonic() + RENDER_TIMEOUT
                while await windows():
                    assert time.monotonic() < deadline, "windows remained after close"
                    await asyncio.sleep(0.3)
                await observe("07-empty", _empty_desktop)

    try:
        asyncio.run(exercise())
    finally:
        person.close()
        (result_dir / "evidence.json").write_text(json.dumps({"marker": marker, "steps": steps}, indent=2, sort_keys=True), encoding="utf-8")
    assert _ssh(f"test -e {marker_file}").returncode != 0
