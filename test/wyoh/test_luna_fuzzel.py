"""Step 4.8: the fuzzel application menu on Luna's real panel, many interactions.

Contract: `luna_fuzzel.feature`. A person (uinput keyboard + mouse, see
`uinput_keyboard.py`) drives fuzzel the way a user would; MCP observes Sway,
drives fuzzel's `--dmenu` mode for a Wyoh-defined menu, and cleans up. Every
step saves the MCP screenshot of DSI-1 on a settled frame for inspection.
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

from test_luna_minimal_env import SSH_MUX, HOST, REMOTE_SERVER, REMOTE_VENV, RUNTIME_DIR, Person, _ssh
from test_minimal_env import RENDER_TIMEOUT, Predicate, _app_windows, _fraction, _tool_payload
from luna_screen import _drawn, _empty_desktop


FUZZEL_CONFIG = "/storage/.local/share/tanstfaafllm/wyoh/deploy/luna/fuzzel.ini"
SILVER = (192, 192, 192)  # fuzzel background in fuzzel.ini
NAVY = (0, 0, 128)        # fuzzel selection
MENU_AREA = {"x": 120, "y": 200, "width": 480, "height": 320}


def _menu_open(image: Image.Image) -> bool:
    return _fraction(image, MENU_AREA, SILVER) > 0.2


def _menu_closed(image: Image.Image) -> bool:
    return _fraction(image, MENU_AREA, SILVER) < 0.01


def _selection(image: Image.Image) -> tuple[int, int, int, int] | None:
    """Bounding box of the navy selection band, if any."""
    navy = Image.new("RGB", image.size, NAVY)
    difference = ImageChops.difference(image.convert("RGB"), navy).convert("L")
    return difference.point(lambda value: 255 if value == 0 else 0).getbbox()


@pytest.mark.live
def test_luna_fuzzel_menu_interactions() -> None:
    if os.environ.get("WYOH_LUNA_LIVE") != "1":
        pytest.skip("set WYOH_LUNA_LIVE=1 with `make wyoh-luna-start` running")
    state = _ssh("systemctl is-active wyoh-sway.service; test -x /storage/.local/opt/wyoh-tools/bin/fuzzel && echo fuzzel; test -e /dev/mali0 && echo mali")
    assert state.stdout.split() == ["active", "fuzzel", "mali"], state.stdout + state.stderr

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    result_dir = Path("results/wyoh/luna-fuzzel") / timestamp
    result_dir.mkdir(parents=True, exist_ok=False)
    choice_file = f"/tmp/wyoh-menu-choice-{timestamp}.txt"
    steps: list[dict[str, Any]] = []
    person = Person(result_dir)

    async def exercise() -> None:
        parameters = StdioServerParameters(
            command="ssh",
            args=[*SSH_MUX, "-T", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", HOST,
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
                    fetched = subprocess.run(["scp", *SSH_MUX, "-q", f"{HOST}:{shot['path']}", str(path)],
                                             capture_output=True, text=True, timeout=30, check=False)
                    assert fetched.returncode == 0, fetched.stderr
                    with Image.open(path) as image:
                        return image.convert("RGB")

                async def observe(name: str, predicate: Predicate) -> Image.Image:
                    """Wait for the end state on two identical consecutive screenshots."""
                    deadline = time.monotonic() + RENDER_TIMEOUT
                    previous: Image.Image | None = None
                    while True:
                        image = await screenshot(result_dir / f"{name}.png")
                        settled = previous is not None and ImageChops.difference(previous, image).getbbox() is None
                        if settled and predicate(image):
                            steps.append({"step": name, "selection": _selection(image), "windows": await windows()})
                            return image
                        assert time.monotonic() < deadline, f"{name}: end state not reached on a settled frame"
                        previous = image
                        await asyncio.sleep(0.3)

                async def window_ids() -> set[int]:
                    return {item["id"] for item in await windows()}

                async def new_window(before: set[int], app_id: str) -> dict[str, Any]:
                    """Wait for a window whose app_id starts with `app_id` and was not in `before`
                    (swayimg launched by fuzzel names itself `swayimg_<hash>`).
                    Polls the tree: some clients (swayimg) set their app_id only
                    after the `new` event, so the event alone is not enough."""
                    deadline = time.monotonic() + RENDER_TIMEOUT
                    while True:
                        fresh = [item for item in await windows() if (item["app_id"] or "").startswith(app_id) and item["id"] not in before]
                        if fresh:
                            return fresh[0]
                        assert time.monotonic() < deadline, f"no new {app_id} window"
                        await asyncio.sleep(0.2)

                assert await windows() == [], "the session must start without application windows"
                await command("workspace number 1")
                await observe("00-empty", _empty_desktop)

                subscription = (await call("sway_subscribe", {"event_names": ["window"]}))["subscription_id"]
                try:
                    # 1 — Alt+d opens the menu with icons
                    person.press("alt+d")
                    opened = await observe("01-menu-open", _menu_open)
                    first = _selection(opened)
                    assert first is not None, "no selection band in the open menu"

                    # 2 — typing filters the list
                    person.type("ed")
                    await observe("02-filter-ed", lambda image: _menu_open(image) and ImageChops.difference(image, opened).getbbox() is not None)

                    # 3 — clear the filter, move the selection down three rows
                    person.press("backspace")
                    person.press("backspace")
                    for _ in range(3):
                        person.press("down")
                    moved = await observe("03-arrow-down-3", lambda image: _menu_open(image) and (_selection(image) or (0, 0, 0, 0))[1] > first[1])
                    assert _selection(moved)[1] - first[1] > 100, (_selection(moved), first)

                    # 4 — Escape closes the menu without launching anything
                    person.press("esc")
                    await observe("04-escape", lambda image: _menu_closed(image) and _empty_desktop(image))
                    assert await windows() == []

                    # 5 — keyboard launch: filter "term", Return
                    person.press("alt+d")
                    await observe("05a-menu-open", _menu_open)
                    person.type("term")
                    await observe("05b-filter-term", lambda image: _menu_open(image) and _selection(image) is not None)
                    before = await window_ids()
                    person.press("enter")
                    terminal_id = (await new_window(before, "foot"))["id"]
                    await observe("05c-terminal-launched", lambda image: _menu_closed(image))
                    del terminal_id

                    # 6 — mouse launch: filter "image", click the selected row
                    person.press("alt+d")
                    await observe("06a-menu-open", _menu_open)
                    person.type("image")
                    filtered = await observe("06b-filter-image", lambda image: _menu_open(image) and _selection(image) is not None)
                    left, top, right, bottom = _selection(filtered)
                    person.home()
                    person.move((left + right) // 2, (top + bottom) // 2)
                    before = await window_ids()
                    person.click("left")
                    viewer = await new_window(before, "swayimg")
                    viewer = await window(viewer["id"])
                    await observe("06c-image-viewer-launched", lambda image: _menu_closed(image) and _drawn(viewer["rect"])(image))

                    # 7 — arrow navigation down then back up, then Return launches the first entry
                    person.press("alt+d")
                    top_of_list = await observe("07a-menu-open", _menu_open)
                    top_row = _selection(top_of_list)
                    for _ in range(7):
                        person.press("down")
                    await observe("07b-down-7", lambda image: _menu_open(image) and (_selection(image) or (0, 0, 0, 0))[1] > top_row[1] + 300)
                    for _ in range(7):
                        person.press("up")
                    await observe("07c-up-7", lambda image: _menu_open(image) and _selection(image) == top_row)
                    before = await window_ids()
                    person.press("enter")
                    calculator = await new_window(before, "wyoh-calc")
                    calculator = await window(calculator["id"])
                    await observe("07d-calculator-launched", lambda image: _menu_closed(image) and _drawn(calculator["rect"])(image))

                    # 8 — a Wyoh-defined menu: MCP opens fuzzel in dmenu mode, the person picks
                    await command(
                        "exec sh -c \"printf 'Cascade windows\\nTile windows\\nClose all\\n' | "
                        f"fuzzel --dmenu --config {FUZZEL_CONFIG} --prompt 'Wyoh: ' > {choice_file}\""
                    )
                    await observe("08a-wyoh-menu", _menu_open)
                    person.press("down")
                    await observe("08b-wyoh-menu-down", lambda image: _menu_open(image))
                    person.press("enter")
                    deadline = time.monotonic() + RENDER_TIMEOUT
                    while _ssh(f"cat {choice_file}").stdout.strip() != "Tile windows":
                        assert time.monotonic() < deadline, f"menu choice: {_ssh(f'cat {choice_file}').stdout!r}"
                        await asyncio.sleep(0.3)
                    await observe("08c-wyoh-menu-chosen", _menu_closed)
                finally:
                    # 9 — MCP closes every window by con_id
                    for item in await windows():
                        await command(f"[con_id={item['id']}] kill")
                    await call("sway_unsubscribe", {"subscription_id": subscription})
                    _ssh(f"rm -f {choice_file}")

                deadline = time.monotonic() + RENDER_TIMEOUT
                while await windows():
                    assert time.monotonic() < deadline, "windows remained after close"
                    await asyncio.sleep(0.3)
                await observe("09-empty", _empty_desktop)

    try:
        asyncio.run(exercise())
    finally:
        person.close()
        (result_dir / "evidence.json").write_text(json.dumps({"steps": steps}, indent=2, sort_keys=True), encoding="utf-8")
