"""Step 5.6: Luna operated with only its buttons and the input zone.

Contract: `luna_buttons_only.feature`. The person is simulated entirely through
MCP development tools (virtual gamepad + virtual keyboard for the zone); MCP
also observes Sway and the gamepad daemon's status, and saves a settled
screenshot of DSI-1 per step. No Sway command operates the session on the
person's behalf: `sway_command` is never called here.
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

from test_luna_fuzzel import SILVER, _menu_closed, _menu_open
from test_luna_minimal_env import HOST, REMOTE_SERVER, REMOTE_VENV, RUNTIME_DIR, _ssh
from test_minimal_env import RENDER_TIMEOUT, Predicate, _app_windows, _drawn, _empty_desktop, _fraction, _tool_payload

FULL = {"x": 0, "y": 0, "width": 720, "height": 720}


def _zone_visible(image: Image.Image) -> bool:
    return _fraction(image, FULL, SILVER) > 0.02


@pytest.mark.live
def test_luna_is_operated_with_only_buttons_and_the_input_zone() -> None:
    if os.environ.get("WYOH_LUNA_LIVE") != "1":
        pytest.skip("set WYOH_LUNA_LIVE=1 with `make wyoh-luna-start` running")
    state = _ssh("systemctl is-active wyoh-sway.service wyoh-gamepad.service")
    assert state.stdout.split() == ["active", "active"], state.stdout + state.stderr

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    result_dir = Path("results/wyoh/luna-buttons-only") / timestamp
    result_dir.mkdir(parents=True, exist_ok=False)
    marker = f"/tmp/wyoh-buttons-{timestamp}"
    discarded = f"/tmp/wyoh-discarded-{timestamp}"
    steps: list[dict[str, Any]] = []

    async def exercise() -> None:
        parameters = StdioServerParameters(
            command="ssh",
            args=["-T", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", HOST,
                  "env", f"XDG_RUNTIME_DIR={RUNTIME_DIR}", f"{REMOTE_VENV}/bin/python", REMOTE_SERVER,
                  "--full-ipc-development", "--shared-vnc-session"],
        )
        with (result_dir / "server.stderr.log").open("w", encoding="utf-8") as stderr_log:
            async with Client(stdio_client(parameters, errlog=stderr_log), read_timeout_seconds=60.0) as client:

                async def call(name: str, arguments: dict[str, Any] | None = None) -> Any:
                    result = await client.call_tool(name, arguments or {})
                    assert not result.is_error, f"{name}: {result.content!r}"
                    return _tool_payload(result)

                # the person
                async def tap(*buttons: str, hold: float = 0.08) -> None:
                    await call("wyoh_dev_gamepad_tap", {"buttons": list(buttons), "hold_seconds": hold})
                    await asyncio.sleep(0.15)

                async def fn(button: str) -> None:
                    await call("wyoh_dev_gamepad_buttons", {"press": ["BTN_MODE"]})
                    await tap(button)
                    await call("wyoh_dev_gamepad_buttons", {"release": ["BTN_MODE"]})

                async def type_text(text: str) -> None:
                    await call("wyoh_dev_keyboard_type", {"text": text})

                async def stick(x: int, y: int, seconds: float) -> None:
                    await call("wyoh_dev_gamepad_stick", {"x": x, "y": y, "seconds": seconds})

                # observation
                async def status() -> dict[str, Any]:
                    return await call("wyoh_gamepad_status")

                async def windows() -> list[dict[str, Any]]:
                    return _app_windows(await call("sway_get_tree"))

                async def focused() -> dict[str, Any] | None:
                    return next((item for item in await windows() if item["focused"]), None)

                async def screenshot(path: Path) -> Image.Image:
                    shot = await call("wyoh_capture_screenshot")
                    fetched = subprocess.run(["scp", "-q", f"{HOST}:{shot['path']}", str(path)],
                                             capture_output=True, text=True, timeout=30, check=False)
                    assert fetched.returncode == 0, fetched.stderr
                    with Image.open(path) as image:
                        return image.convert("RGB")

                async def observe(name: str, predicate: Predicate = lambda image: True) -> Image.Image:
                    deadline = time.monotonic() + RENDER_TIMEOUT
                    previous: Image.Image | None = None
                    while True:
                        image = await screenshot(result_dir / f"{name}.png")
                        settled = previous is not None and ImageChops.difference(previous, image).getbbox() is None
                        if settled and predicate(image):
                            steps.append({"step": name, "status": await status(), "windows": await windows()})
                            return image
                        assert time.monotonic() < deadline, f"{name}: end state not reached on a settled frame"
                        previous = image
                        await asyncio.sleep(0.3)

                async def until(description: str, check) -> Any:
                    deadline = time.monotonic() + RENDER_TIMEOUT
                    while True:
                        value = await check()
                        if value:
                            return value
                        assert time.monotonic() < deadline, f"timed out: {description}"
                        await asyncio.sleep(0.25)

                async def new_window(before: set[int], prefix: str) -> dict[str, Any]:
                    async def fresh():
                        return next((item for item in await windows()
                                     if (item["app_id"] or "").startswith(prefix) and item["id"] not in before), None)
                    return await until(f"new {prefix} window", fresh)

                # --- background: both gamepads attached, empty session
                await call("wyoh_dev_gamepad_buttons", {})  # creates the virtual gamepad
                await until("daemon attached the virtual gamepad",
                            lambda: _devices_at_least(status, 2))
                assert await windows() == [], "the session must start without application windows"
                await observe("00-empty", _empty_desktop)

                # --- launch the terminal from the menu with the D-pad
                await tap("BTN_START")
                await observe("01-menu", _menu_open)
                for _ in range(8):
                    await tap("BTN_DPAD_DOWN")
                await observe("02-menu-terminal-selected", _menu_open)
                before = {item["id"] for item in await windows()}
                await tap("BTN_EAST")
                terminal = await new_window(before, "foot")
                await observe("03-terminal", lambda image: _menu_closed(image) and _drawn(terminal["rect"])(image))

                # --- input zone: prepare, send, run
                await tap("BTN_TL")
                await until("zone open", lambda: _status_is(status, zone="open"))
                await observe("04-zone-open", _zone_visible)
                await type_text(f"touch {marker}")
                await observe("05-zone-typed", _zone_visible)
                await tap("BTN_TL2")
                await until("zone delivered", lambda: _status_is(status, zone="closed", zone_result="delivered"))
                await observe("06-delivered", lambda image: not _zone_visible(image))
                await tap("BTN_EAST")
                await until("marker file exists", lambda: _async_true(_ssh(f"test -e {marker}").returncode == 0))
                await observe("07-command-ran")

                # --- input zone: discard with B
                await tap("BTN_TL")
                await until("zone open again", lambda: _status_is(status, zone="open"))
                await type_text(f"touch {discarded}")
                await observe("08-zone-before-discard", _zone_visible)
                await tap("BTN_SOUTH")
                await until("zone discarded", lambda: _status_is(status, zone="closed", zone_result="discarded"))
                await observe("09-discarded", lambda image: not _zone_visible(image))
                await tap("BTN_EAST")  # an Enter on an empty prompt: proves nothing was typed
                await asyncio.sleep(1.0)
                assert _ssh(f"test -e {discarded}").returncode != 0, "discarded text was delivered"

                # --- second window, focus, fullscreen, pointer
                await tap("BTN_START")
                await observe("10-menu-again", _menu_open)
                for _ in range(3):
                    await tap("BTN_DPAD_DOWN")
                before = {item["id"] for item in await windows()}
                await tap("BTN_EAST")
                viewer = await new_window(before, "swayimg")
                await until("viewer focused", lambda: _focused_is(focused, viewer["id"]))
                await observe("11-viewer-beside-terminal", lambda image: _menu_closed(image))
                await tap("BTN_SELECT")
                await until("terminal focused", lambda: _focused_is(focused, terminal["id"]))
                await observe("12-select-focus-terminal")
                await fn("BTN_EAST")
                await until("terminal fullscreen", lambda: _fullscreen_is(windows, terminal["id"], 1))
                await observe("13-fn-a-fullscreen")
                await fn("BTN_EAST")
                await until("terminal tiled again", lambda: _fullscreen_is(windows, terminal["id"], 0))
                await observe("14-fn-a-back")
                await stick(-1800, -1800, 1.5)   # into the top-left corner
                await stick(1800, 0, 0.65)       # right, onto the viewer (x > 360)
                await stick(0, 1800, 0.45)       # down, into the window body
                await tap("BTN_THUMBL")
                await until("viewer focused by click", lambda: _focused_is(focused, viewer["id"]))
                await observe("15-pointer-click-viewer")
                await tap("BTN_SELECT")
                await until("terminal focused again", lambda: _focused_is(focused, terminal["id"]))
                await observe("16-select-back-to-terminal")

                # --- Tab and Shift+Tab reach the application
                await tap("BTN_TL")
                await until("zone open for cat", lambda: _status_is(status, zone="open"))
                await type_text("cat -A")
                await tap("BTN_TL2")
                await until("cat delivered", lambda: _status_is(status, zone="closed", zone_result="delivered"))
                await tap("BTN_EAST")
                await asyncio.sleep(0.5)
                await tap("BTN_TR")
                await tap("BTN_TR2")
                await tap("BTN_EAST")
                await observe("17-tab-shift-tab-in-cat")

                # --- recovery: FN + Start held more than two seconds
                recoveries = (await status())["recovery"]
                await tap("BTN_TL")
                await until("zone open before recovery", lambda: _status_is(status, zone="open"))
                await tap("BTN_MODE", "BTN_START", hold=2.6)
                await until("recovery recorded", lambda: _status_recovered(status, recoveries + 1))
                await observe("18-recovered", lambda image: not _zone_visible(image))

                # --- close everything with FN + B
                for _ in range(6):
                    remaining = await windows()
                    if not remaining:
                        break
                    await fn("BTN_SOUTH")
                    await until("one window closed", lambda: _fewer(windows, len(remaining)))
                assert await windows() == []
                await observe("19-empty", _empty_desktop)

    try:
        asyncio.run(exercise())
    finally:
        (result_dir / "evidence.json").write_text(json.dumps({"steps": steps}, indent=2, sort_keys=True), encoding="utf-8")
        _ssh(f"rm -f {marker} {discarded}")


# small async predicates used with `until`

async def _async_true(value: bool) -> bool:
    return value


async def _devices_at_least(status, count: int) -> bool:
    return len((await status()).get("devices", [])) >= count


async def _status_is(status, **expected: Any) -> bool:
    current = await status()
    return all(current.get(key) == value for key, value in expected.items())


async def _status_recovered(status, count: int) -> bool:
    current = await status()
    return current.get("recovery") == count and current.get("zone") == "closed"


async def _focused_is(focused, con_id: int) -> bool:
    item = await focused()
    return item is not None and item["id"] == con_id


async def _fullscreen_is(windows, con_id: int, mode: int) -> bool:
    return any(item["id"] == con_id and item["fullscreen_mode"] == mode for item in await windows())


async def _fewer(windows, count: int) -> bool:
    return len(await windows()) < count
