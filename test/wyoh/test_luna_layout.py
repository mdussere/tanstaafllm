"""Four tiles per workspace, in a fixed order (user requirement 2026-10-08).

Contract: `luna_layout.feature`. The person opens terminals from the menu with
the MCP virtual gamepad; `wyoh-layout.service` places them. MCP checks the
geometry after each step and saves a settled screenshot of DSI-1.
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

from luna_screen import _empty_desktop, _menu_closed, _menu_open, _silver_visible
from test_luna_minimal_env import SSH_MUX, HOST, REMOTE_SERVER, REMOTE_VENV, RUNTIME_DIR, _ssh
from test_minimal_env import RENDER_TIMEOUT, Predicate, _app_windows, _fraction, _tool_payload

FULL = {"x": 0, "y": 0, "width": 720, "height": 720}
TOP, MIDDLE = 22, 371  # the bar takes the first 22 px; halves of the remaining 698 px


def _popup_visible(image: Image.Image) -> bool:
    return _silver_visible(image)


@pytest.mark.live
def test_luna_layout_holds_four_tiles_in_order() -> None:
    if os.environ.get("WYOH_LUNA_LIVE") != "1":
        pytest.skip("set WYOH_LUNA_LIVE=1 with `make wyoh-luna-start` running")
    state = _ssh("systemctl is-active wyoh-sway.service wyoh-gamepad.service wyoh-layout.service")
    assert state.stdout.split() == ["active"] * 3, state.stdout + state.stderr

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    result_dir = Path("results/wyoh/luna-layout") / timestamp
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
                    await asyncio.sleep(0.15)

                async def fn(button: str) -> None:
                    await call("wyoh_dev_gamepad_buttons", {"press": ["BTN_MODE"]})
                    await tap(button)
                    await call("wyoh_dev_gamepad_buttons", {"release": ["BTN_MODE"]})

                async def windows() -> list[dict[str, Any]]:
                    return _app_windows(await call("sway_get_tree"))

                async def screenshot(path: Path, shot: dict[str, Any] | None = None) -> Image.Image:
                    shot = shot or await call("wyoh_capture_screenshot", {"image_format": "jpeg", "quality": 85})
                    fetched = subprocess.run(["scp", *SSH_MUX, "-q", f"{HOST}:{shot['path']}", str(path)],
                                             capture_output=True, text=True, timeout=90, check=False)
                    assert fetched.returncode == 0, fetched.stderr
                    with Image.open(path) as image:
                        return image.convert("RGB")

                async def observe(name: str, predicate: Predicate = lambda image: True) -> Image.Image:
                    """Wait for two identical consecutive frames (compared by SHA-256 on
                    Luna, so nothing is transferred while waiting), then fetch that
                    frame once and check the end state. Luna's Wi-Fi moves about
                    160 KB/s and a wallpaper frame is about 1 MB."""
                    deadline = time.monotonic() + 3 * RENDER_TIMEOUT
                    previous = ""
                    while True:
                        shot = await call("wyoh_capture_screenshot", {"image_format": "jpeg", "quality": 85})
                        if shot["sha256"] == previous:
                            image = await screenshot(result_dir / f"{name}.jpg", shot)
                            if predicate(image):
                                steps.append({"step": name, "windows": await windows()})
                                return image
                        assert time.monotonic() < deadline, f"{name}: end state not reached on a settled frame"
                        previous = shot["sha256"]
                        await asyncio.sleep(0.3)

                async def geometry_after(count: int) -> dict[int, tuple[int, int, int, int]]:
                    deadline = time.monotonic() + RENDER_TIMEOUT
                    while True:
                        current = {w["id"]: (w["rect"]["x"], w["rect"]["y"], w["rect"]["width"], w["rect"]["height"])
                                   for w in await windows()}
                        if len(current) == count:
                            return current
                        assert time.monotonic() < deadline, f"expected {count} windows, have {len(current)}"
                        await asyncio.sleep(0.25)

                async def open_terminal() -> None:
                    await tap("BTN_START")
                    await observe(f"menu-{len(steps):02d}", _menu_open)
                    for _ in range(8):
                        await tap("BTN_DPAD_DOWN")
                    await tap("BTN_EAST")

                await call("wyoh_dev_gamepad_buttons", {})
                deadline = time.monotonic() + RENDER_TIMEOUT
                while len((await call("wyoh_gamepad_status")).get("devices", [])) < 2:
                    assert time.monotonic() < deadline, "daemon did not attach the virtual gamepad"
                    await asyncio.sleep(0.25)
                assert await windows() == [], "the workspace must start empty"
                await observe("00-empty", _empty_desktop)

                await open_terminal()
                g1 = await geometry_after(1)
                (first,) = g1
                assert g1[first] == (0, TOP, 720, 698), g1
                await observe("01-one-tile", _menu_closed)

                await open_terminal()
                g2 = await geometry_after(2)
                (second,) = set(g2) - {first}
                assert g2[second][1] == TOP and g2[first][1] == MIDDLE, g2  # new one on top
                assert g2[second][2] == g2[first][2] == 720, g2
                await observe("02-vertical-split-new-on-top", _menu_closed)

                await open_terminal()
                g3 = await geometry_after(3)
                (third,) = set(g3) - set(g2)
                assert g3[third][:2] == (360, TOP) and g3[second][:2] == (0, TOP), g3  # top-right
                assert g3[first][:3] == (0, MIDDLE, 720), g3
                await observe("03-top-split-new-top-right", _menu_closed)

                await open_terminal()
                g4 = await geometry_after(4)
                (fourth,) = set(g4) - set(g3)
                assert g4[fourth][:2] == (360, MIDDLE) and g4[first][:3] == (0, MIDDLE, 360), g4  # bottom-right
                assert any(w["id"] == fourth and w["focused"] for w in await windows()), "the new tile has the focus"
                await observe("04-bottom-split-new-bottom-right", _menu_closed)

                await open_terminal()
                await observe("05-too-many-tiles", _popup_visible)
                assert set(await geometry_after(4)) == set(g4), "a fifth tile was kept"

                await tap("BTN_SOUTH")  # B = Escape dismisses the pop-up
                await observe("06-popup-dismissed", lambda image: not _popup_visible(image))

                for _ in range(6):
                    remaining = await windows()
                    if not remaining:
                        break
                    await fn("BTN_SOUTH")
                    deadline = time.monotonic() + RENDER_TIMEOUT
                    while len(await windows()) >= len(remaining):
                        assert time.monotonic() < deadline, "FN+B did not close a window"
                        await asyncio.sleep(0.25)
                await observe("07-empty", _empty_desktop)

    try:
        asyncio.run(exercise())
    finally:
        (result_dir / "evidence.json").write_text(json.dumps({"steps": steps}, indent=2, sort_keys=True), encoding="utf-8")
