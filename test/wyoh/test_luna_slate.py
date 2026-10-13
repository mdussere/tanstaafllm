"""Step 6.5: the Slate and its on-screen keyboard on Luna's panel.

Contract: `luna_slate.feature`. The person is simulated through MCP
development tools only: the virtual gamepad, the virtual AZERTY keyboard (the
USB keyboard stand-in), and both sticks with L3/R3 on the on-screen keyboard
(green and red selections).
MCP also observes Sway and the daemon's status and saves a settled screenshot
of DSI-1 per step. Text effects are proven with marker files written by the
terminal that receives the Slate's text. `sway_command` is never called.
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
from PIL import Image

from luna_screen import _near_fraction
from test_luna_minimal_env import SSH_MUX, HOST, REMOTE_SERVER, REMOTE_VENV, RUNTIME_DIR, _ssh
from test_minimal_env import RENDER_TIMEOUT, Predicate, _app_windows, _tool_payload

SLATE = {"x": 6, "y": 30, "width": 708, "height": 200}       # inside the Slate's border
SLATE_LEFT_BORDER = {"x": 0, "y": 40, "width": 2, "height": 180}
KEYBOARD = {"x": 0, "y": 482, "width": 720, "height": 236}
BLACK, WHITE, BLUE = (0, 0, 0), (255, 255, 255), (0x52, 0x94, 0xE2)

# Luna's AZERTY layer (src/wyoh/wvkbd/keys_simple.luna.h): the green
# selection starts on "f" (row 2), the red one on "j" (row 2).
AXIS = 1800
STICK_STEP = {"up": (0, -AXIS), "down": (0, AXIS), "left": (-AXIS, 0), "right": (AXIS, 0)}


def _slate_open(image: Image.Image) -> bool:
    return (_near_fraction(image, SLATE, BLACK, tol=12) > 0.8
            and _near_fraction(image, SLATE_LEFT_BORDER, WHITE, tol=40) > 0.8
            and _near_fraction(image, KEYBOARD, BLACK, tol=12) > 0.4
            and _near_fraction(image, KEYBOARD, WHITE, tol=40) > 0.03)


def _slate_closed(image: Image.Image) -> bool:
    """No keyboard at the bottom, and the focused terminal's border is blue again."""
    return (_near_fraction(image, KEYBOARD, BLACK, tol=12) < 0.2
            and _near_fraction(image, SLATE_LEFT_BORDER, BLUE, tol=40) > 0.8)


@pytest.mark.live
def test_luna_slate_and_keyboard() -> None:
    if os.environ.get("WYOH_LUNA_LIVE") != "1":
        pytest.skip("set WYOH_LUNA_LIVE=1 with `make wyoh-luna-start` running")
    state = _ssh("systemctl is-active wyoh-sway.service wyoh-gamepad.service wyoh-layout.service")
    assert state.stdout.split() == ["active"] * 3, state.stdout + state.stderr

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    result_dir = Path("results/wyoh/luna-slate") / timestamp
    result_dir.mkdir(parents=True, exist_ok=False)
    base = f"/tmp/wyoh-slate-{timestamp}"
    files = {name: f"{base}-{name}" for name in ("M", "D", "W", "S", "R", "K")}
    steps: list[dict[str, Any]] = []
    statuses: list[dict[str, Any]] = []

    async def exercise() -> None:
        parameters = StdioServerParameters(
            command="ssh",
            args=[*SSH_MUX, "-T", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", HOST,
                  "env", f"XDG_RUNTIME_DIR={RUNTIME_DIR}", f"{REMOTE_VENV}/bin/python", REMOTE_SERVER,
                  "--full-ipc-development", "--shared-vnc-session"],
        )
        with (result_dir / "server.stderr.log").open("w", encoding="utf-8") as stderr_log:
            async with Client(stdio_client(parameters, errlog=stderr_log), read_timeout_seconds=60.0) as client:

                async def call(name: str, arguments: dict[str, Any] | None = None) -> Any:
                    result = await client.call_tool(name, arguments or {})
                    assert not result.is_error, f"{name}: {result.content!r}"
                    return _tool_payload(result)

                async def tap(*buttons: str, repeat: int = 1) -> None:
                    await call("wyoh_dev_gamepad_tap", {"buttons": list(buttons), "repeat": repeat})
                    await asyncio.sleep(0.15)

                async def hold(*buttons: str) -> None:
                    await call("wyoh_dev_gamepad_buttons", {"press": list(buttons)})

                async def let_go(*buttons: str) -> None:
                    await call("wyoh_dev_gamepad_buttons", {"release": list(buttons)})

                async def type_text(text: str) -> None:
                    await call("wyoh_dev_keyboard_type", {"text": text})
                    await asyncio.sleep(0.3)

                async def status() -> dict[str, Any]:
                    current = await call("wyoh_gamepad_status")
                    statuses.append(current)
                    return current

                async def windows() -> list[dict[str, Any]]:
                    return _app_windows(await call("sway_get_tree"))

                async def until(description: str, check, timeout: float = RENDER_TIMEOUT) -> Any:
                    deadline = time.monotonic() + timeout
                    while True:
                        value = await check()
                        if value:
                            return value
                        assert time.monotonic() < deadline, f"timed out: {description}"
                        await asyncio.sleep(0.25)

                async def screenshot(path: Path, shot: dict[str, Any]) -> Image.Image:
                    fetched = subprocess.run(["scp", *SSH_MUX, "-q", f"{HOST}:{shot['path']}", str(path)],
                                             capture_output=True, text=True, timeout=90, check=False)
                    assert fetched.returncode == 0, fetched.stderr
                    with Image.open(path) as image:
                        return image.convert("RGB")

                async def observe(name: str, predicate: Predicate = lambda image: True) -> Image.Image:
                    """Two identical consecutive frames (SHA-256 on Luna), then fetch and check."""
                    deadline = time.monotonic() + 3 * RENDER_TIMEOUT
                    previous = ""
                    while True:
                        shot = await call("wyoh_capture_screenshot", {"image_format": "jpeg", "quality": 85})
                        if shot["sha256"] == previous:
                            image = await screenshot(result_dir / f"{name}.jpg", shot)
                            if predicate(image):
                                steps.append({"step": name, "windows": await windows(), "status": await status()})
                                return image
                        assert time.monotonic() < deadline, f"{name}: end state not reached on a settled frame"
                        previous = shot["sha256"]
                        await asyncio.sleep(0.3)

                async def slate_window() -> dict[str, Any] | None:
                    return next((w for w in await windows() if w["app_id"] == "wyoh-slate"), None)

                async def open_slate(name: str) -> None:
                    await tap("BTN_TL")

                    seen: dict[str, Any] = {}

                    async def ready():
                        seen["windows"], seen["status"] = await windows(), await status()
                        window = next((w for w in seen["windows"] if w["app_id"] == "wyoh-slate"), None)
                        return bool(window and window["focused"] and seen["status"].get("slate_ready"))
                    try:
                        await until("the Slate is open, focused and connected", ready)
                    except AssertionError as error:
                        raise AssertionError(f"{error}; last seen: {seen}") from None
                    await observe(name, _slate_open)

                async def send_slate(name: str) -> None:
                    before = (await status())["deliveries"]
                    await hold("BTN_MODE")
                    await tap("BTN_EAST")  # FN+A: send, then clear and hide (user, 2026-10-09)
                    await let_go("BTN_MODE")

                    async def delivered():
                        current = await status()
                        return current["deliveries"] == before + 1 and current["zone"] == "closed"
                    await until("the Slate delivered once", delivered)
                    await until("the Slate window is gone", lambda: _none(slate_window))
                    await tap("BTN_EAST")  # A outside the Slate: Return runs the last line
                    await observe(name, _slate_closed)

                async def file_holds(name: str, expected: str) -> None:
                    async def check():
                        result = _ssh(f"cat {files[name]}")
                        return result.returncode == 0 and result.stdout == expected
                    await until(f"{name} holds {expected!r}", check)

                async def steer(stick: str, *moves: str) -> None:
                    """Step a selection: one short push per move (shorter than the repeat delay)."""
                    for move in moves:
                        x, y = STICK_STEP[move]
                        await call("wyoh_dev_gamepad_stick", {"x": x, "y": y, "seconds": 0.1, "stick": stick})
                        await asyncio.sleep(0.15)

                # Background: the person, a terminal opened with the buttons.
                await call("wyoh_dev_gamepad_buttons", {})
                # The daemon looks for new devices every 5 s; allow two looks after a slow start.
                await until("daemon attached the virtual gamepad",
                            lambda: _at_least((status()), "devices", 2), timeout=2 * RENDER_TIMEOUT)
                assert await windows() == [], "the workspace must start empty"
                await tap("BTN_START")
                await asyncio.sleep(0.8)
                await type_text("term")  # filter the menu (its entries change with Step 9)
                await tap("BTN_EAST")
                await until("a terminal is open and focused",
                            lambda: _any_focused(windows, "foot"))
                await type_text("clear")
                await tap("BTN_EAST")

                # Open the Slate: look.
                await open_slate("01-slate-open")

                # Two lines are sent once.
                await type_text(f"echo first >> {files['M']}")
                await tap("BTN_EAST")
                await type_text(f"echo second >> {files['M']}")
                await observe("02-two-lines", _slate_open)
                await send_slate("03-sent")
                await file_holds("M", "first\nsecond\n")

                # L1 hides the Slate and keeps its text; L1 shows it again.
                await open_slate("04-slate-again")
                await type_text(f"echo bad >> {files['D']}")
                await tap("BTN_EAST")
                await type_text(f"echo worse >> {files['D']}")
                await observe("05-before-hide", _slate_open)
                await tap("BTN_TL")
                await until("the Slate is hidden", lambda: _zone_is(status, "hidden"))
                await observe("06-hidden", _slate_closed)
                await tap("BTN_TL")
                await until("the Slate is shown", lambda: _zone_is(status, "open"))
                await observe("07-shown-with-its-text", _slate_open)

                # FN+X clears it; nothing reaches the terminal.
                await hold("BTN_MODE")
                await tap("BTN_NORTH")
                await let_go("BTN_MODE")
                await observe("08-cleared", _slate_open)
                await tap("BTN_TL")
                await until("the Slate is hidden", lambda: _zone_is(status, "hidden"))
                await observe("09-hidden-empty", _slate_closed)
                assert _ssh(f"test -e {files['D']}").returncode != 0, "cleared text reached the terminal"

                # The whole cross selects a word; B deletes it.
                await open_slate("10-slate-word")
                text = f"echo hello brave world > {files['W']}"
                await type_text(text)
                for _ in range(len(text) - text.index("brave") - 3):  # into "brave"
                    await tap("BTN_DPAD_LEFT")
                crosses = (await status())["cross"]
                await tap("BTN_DPAD_UP", "BTN_DPAD_DOWN")
                await until("one whole-cross press", lambda: _count(status, "cross", crosses + 1))
                await observe("11-word-selected", _slate_open)
                await tap("BTN_SOUTH")  # B: Backspace deletes the selection
                await observe("12-word-deleted", _slate_open)
                await send_slate("13-word-sent")
                await file_holds("W", "hello world\n")

                # Y with the arrows selects; R1/R2 move by words.
                await open_slate("14-slate-shift")
                await type_text("echo keep drop")
                await hold("BTN_WEST")
                for _ in range(4):
                    await tap("BTN_DPAD_LEFT")
                await let_go("BTN_WEST")
                await observe("15-shift-selected", _slate_open)
                await tap("BTN_SOUTH")
                await type_text(f"> {files['S']}")
                await send_slate("16-shift-sent")
                await file_holds("S", "keep\n")

                await open_slate("17-slate-words")
                await type_text("echo c")
                await tap("BTN_TR2")  # R2: back to the start of "c"
                await type_text("b")
                await tap("BTN_TR")  # R1: to the end of "bc"
                await type_text("d")
                await type_text(f" > {files['R']}")
                await observe("18-words-edited", _slate_open)
                await send_slate("19-words-sent")
                await file_holds("R", "bcd\n")

                # The whole cross twice selects the line; the on-screen keyboard types.
                await open_slate("20-slate-line")
                await type_text("junk line")
                crosses = (await status())["cross"]
                await call("wyoh_dev_gamepad_tap", {"buttons": ["BTN_DPAD_UP", "BTN_DPAD_DOWN"],
                                                    "repeat": 2, "gap_seconds": 0.1})
                await until("two whole-cross presses", lambda: _count(status, "cross", crosses + 2))
                await observe("21-line-selected", _slate_open)
                await tap("BTN_NORTH")  # X: Delete removes the selected line
                await type_text("echo ")
                await observe("22-keyboard-home", _slate_open)  # green on "f", red on "j"
                await steer("left", "left", "left", "left", "up")  # green: f d s q, up to a
                await tap("BTN_THUMBL")
                await tap("BTN_THUMBL")
                await steer("right", "down", "right", "right", "right")  # red: j, down to n, é è ⌫
                await observe("23-keyboard-steered", _slate_open)
                await tap("BTN_THUMBR")
                await steer("right", "left", "left")  # red: back to é
                await tap("BTN_THUMBR")
                await observe("24-keyboard-typed", _slate_open)
                await type_text(f" > {files['K']}")
                await send_slate("25-keyboard-sent")
                await file_holds("K", "aé\n")

                # Close the terminal with FN+B.
                await hold("BTN_MODE")
                await tap("BTN_SOUTH")
                await let_go("BTN_MODE")
                await until("the terminal closed", lambda: _empty(windows))

    try:
        asyncio.run(exercise())
    finally:
        (result_dir / "evidence.json").write_text(
            json.dumps({"steps": steps, "files": files}, indent=2, sort_keys=True), encoding="utf-8")
        _ssh(f"rm -f {base}-*")
    typed = ["first", "second", "brave", "keep", "junk", "echo"]
    for current in statuses:
        assert not any(word in json.dumps(current) for word in typed), "typed text leaked into the status"


async def _at_least(status, key: str, count: int) -> bool:
    return len((await status).get(key, [])) >= count


async def _none(getter) -> bool:
    return await getter() is None


async def _empty(windows) -> bool:
    return await windows() == []


async def _any_focused(windows, app_id: str) -> bool:
    return any(w["app_id"] == app_id and w["focused"] for w in await windows())


async def _discarded(status, before: int) -> bool:
    current = await status()
    return current["discards"] == before + 1 and current["zone"] == "closed"


async def _count(status, key: str, expected: int) -> bool:
    return (await status()).get(key) == expected


async def _zone_is(status, state: str) -> bool:
    return (await status()).get("zone") == state
