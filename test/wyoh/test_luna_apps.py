"""Step 9.11: graphical apps from Luna's menu, used with the gamepad only.

Contract: `luna_apps.feature`. The person is the MCP virtual gamepad (and the
virtual keyboard only to filter the menu, as a USB keyboard would). MCP
observes Sway and saves a settled screenshot per step; the arithmetic result
is read on the screenshot by the reviewer (21 on the display).
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

from luna_screen import _empty_desktop, _menu_open, _near_fraction
from test_luna_minimal_env import SSH_MUX, HOST, REMOTE_SERVER, REMOTE_VENV, RUNTIME_DIR, _ssh
from test_minimal_env import RENDER_TIMEOUT, Predicate, _app_windows, _tool_payload

SILVER = (192, 192, 192)  # the calculator's Windows 3.1 grey


def _calculator_drawn(rect: dict[str, int]) -> Predicate:
    """The window shows the grey calculator, not the wallpaper through it."""
    inner = {"x": rect["x"] + 4, "y": rect["y"] + 4, "width": rect["width"] - 8, "height": rect["height"] - 8}
    return lambda image: _near_fraction(image, inner, SILVER, tol=20) > 0.35


COMMANDER_ROWS = [(34, 42, 51), (28, 33, 41)]  # its two alternating row colours (sampled 2026-10-11)


def _commander_drawn(image: Image.Image) -> bool:
    """Commander's dark-slate rows fill the left pane (the wallpaper is dark too,
    so a 'changed from the wallpaper' measure is not enough)."""
    pane = {"x": 100, "y": 60, "width": 250, "height": 620}
    return sum(_near_fraction(image, pane, colour, tol=10) for colour in COMMANDER_ROWS) > 0.6


WOLF_HUD = (0, 0, 168)  # Wolfenstein's blue status bar (sampled 2026-10-11)


def _wolf_in_game(image: Image.Image) -> bool:
    return _near_fraction(image, {"x": 0, "y": 560, "width": 720, "height": 150}, WOLF_HUD, tol=30) > 0.25


def _view_changed(before: Image.Image) -> Predicate:
    def changed(image: Image.Image) -> bool:
        a, b = before.convert("L").crop((0, 0, 720, 540)), image.convert("L").crop((0, 0, 720, 540))
        return sum(1 for x, y in zip(a.getdata(), b.getdata()) if abs(x - y) > 30) > 20000
    return changed


def _rows_differ(before: Image.Image, after: Image.Image) -> bool:
    left = (0, 40, 360, 690)
    a, b = before.convert("L").crop(left), after.convert("L").crop(left)
    changed = sum(1 for x, y in zip(a.getdata(), b.getdata()) if abs(x - y) > 30)
    return changed > 2000


@pytest.mark.live
def test_luna_graphical_apps_from_the_menu() -> None:
    if os.environ.get("WYOH_LUNA_LIVE") != "1":
        pytest.skip("set WYOH_LUNA_LIVE=1 with `make wyoh-luna-start` and `make wyoh-luna-apps` done")
    state = _ssh("systemctl is-active wyoh-sway.service wyoh-gamepad.service wyoh-layout.service")
    assert state.stdout.split() == ["active"] * 3, state.stdout + state.stderr

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    result_dir = Path("results/wyoh/luna-apps") / timestamp
    result_dir.mkdir(parents=True, exist_ok=False)
    steps: list[dict[str, Any]] = []

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

                async def tap(*buttons: str) -> None:
                    await call("wyoh_dev_gamepad_tap", {"buttons": list(buttons)})
                    await asyncio.sleep(0.25)

                async def fn(button: str) -> None:
                    await call("wyoh_dev_gamepad_buttons", {"press": ["BTN_MODE"]})
                    await tap(button)
                    await call("wyoh_dev_gamepad_buttons", {"release": ["BTN_MODE"]})

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

                async def observe(name: str, predicate: Predicate = lambda image: True) -> Image.Image:
                    deadline = time.monotonic() + 3 * RENDER_TIMEOUT
                    previous = ""
                    while True:
                        shot = await call("wyoh_capture_screenshot", {"image_format": "jpeg", "quality": 85})
                        if shot["sha256"] == previous:
                            path = result_dir / f"{name}.jpg"
                            fetched = subprocess.run(["scp", *SSH_MUX, "-q", f"{HOST}:{shot['path']}", str(path)],
                                                     capture_output=True, text=True, timeout=90, check=False)
                            assert fetched.returncode == 0, fetched.stderr
                            with Image.open(path) as image:
                                image = image.convert("RGB")
                            if predicate(image):
                                steps.append({"step": name, "windows": await windows()})
                                return image
                        assert time.monotonic() < deadline, f"{name}: end state not reached on a settled frame"
                        previous = shot["sha256"]
                        await asyncio.sleep(0.3)

                async def app(app_id: str) -> dict[str, Any] | None:
                    return next((w for w in await windows() if w["app_id"] == app_id and w["focused"]), None)

                async def launch(query: str, app_id: str, name: str) -> dict[str, Any]:
                    await tap("BTN_START")
                    await observe(f"{name}-menu", _menu_open)
                    await call("wyoh_dev_keyboard_type", {"text": query})
                    await asyncio.sleep(0.5)
                    await observe(f"{name}-menu-filtered", _menu_open)
                    await tap("BTN_EAST")
                    return await until(f"{app_id} focused", lambda: app(app_id), timeout=2 * RENDER_TIMEOUT)

                await call("wyoh_dev_gamepad_buttons", {})
                await until("daemon attached the virtual gamepad",
                            lambda: _devices(call), timeout=2 * RENDER_TIMEOUT)
                assert await windows() == [], "the workspace must start empty"
                await observe("00-empty", _empty_desktop)

                # The calculator: 3 x 7 = 21 with the cross and A (selection starts on "=").
                calc = await launch("calc", "wyoh-calculator", "01-calc")
                await observe("02-calc-open", _calculator_drawn(calc["rect"]))
                await tap("BTN_DPAD_LEFT")            # = -> 3
                await tap("BTN_EAST")                 # 3
                for move in ("BTN_DPAD_UP", "BTN_DPAD_UP", "BTN_DPAD_UP", "BTN_DPAD_RIGHT"):
                    await tap(move)                   # 3 -> 6 -> 9 -> ÷ -> ×
                await tap("BTN_EAST")                 # ×
                for move in ("BTN_DPAD_DOWN", "BTN_DPAD_LEFT", "BTN_DPAD_LEFT", "BTN_DPAD_LEFT"):
                    await tap(move)                   # × -> − -> 9 -> 8 -> 7
                await tap("BTN_EAST")                 # 7
                for move in ("BTN_DPAD_DOWN", "BTN_DPAD_DOWN", "BTN_DPAD_RIGHT", "BTN_DPAD_RIGHT", "BTN_DPAD_RIGHT"):
                    await tap(move)                   # 7 -> 4 -> 1 -> 2 -> 3 -> =
                await tap("BTN_EAST")                 # = : 21
                await observe("03-calc-21", _calculator_drawn(calc["rect"]))
                await fn("BTN_SOUTH")
                await until("calculator closed", lambda: _gone(windows, "wyoh-calculator"))

                # Files (Commander), full screen; the selection moves with the cross.
                await launch("files", "commander", "04-files")
                before = await observe("05-files-open", _commander_drawn)
                await tap("BTN_DPAD_DOWN")
                await tap("BTN_DPAD_DOWN")
                await observe("06-files-moved", lambda image: _rows_differ(before, image))
                await fn("BTN_SOUTH")
                await until("Files closed", lambda: _gone(windows, "commander"))
                await observe("07-empty", _empty_desktop)

                # Wolfenstein 3D (gamepad-virtual, user 2026-10-13): A validates, the left
                # stick moves, R1 fires, L1 opens doors.
                await launch("wolf", "ecwolf", "08-wolf")
                await asyncio.sleep(5)  # about 3 s to initialise with ALSA
                for _ in range(7):      # title screens, main menu (New Game), episode 1, difficulty
                    await tap("BTN_EAST")
                    await asyncio.sleep(1.5)
                game = await observe("09-wolf-floor1", _wolf_in_game)
                await call("wyoh_dev_gamepad_stick", {"x": 0, "y": -1800, "seconds": 1.0, "stick": "left"})
                await tap("BTN_TR")
                await tap("BTN_TL")
                await observe("10-wolf-moved", _view_changed(game))
                await fn("BTN_SOUTH")
                await until("Wolfenstein closed", lambda: _gone(windows, "ecwolf"))
                await observe("11-empty", _empty_desktop)

    try:
        asyncio.run(exercise())
    finally:
        (result_dir / "evidence.json").write_text(json.dumps({"steps": steps}, indent=2, sort_keys=True),
                                                  encoding="utf-8")


async def _devices(call) -> bool:
    return len((await call("wyoh_gamepad_status")).get("devices", [])) >= 2


async def _gone(windows, app_id: str) -> bool:
    return all(w["app_id"] != app_id for w in await windows())
