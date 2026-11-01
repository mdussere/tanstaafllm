"""Step 6.11: Mike's window and FN+B on Luna.

Contract: `luna_mike_window.feature`. Needs Mannie stopped on Luna (agreed with
Mannie or Professor), Mike's files in /home/michael/.local/opt/mike and
/storage/.local/opt/wyoh-mike deployed.

Run with:
    WYOH_LUNA_LIVE=1 uv run pytest -m live test/wyoh/test_luna_mike_window.py
"""

from __future__ import annotations

import asyncio
import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client

from test_luna_minimal_env import HOST, REMOTE_SERVER, REMOTE_VENV, RUNTIME_DIR, SSH_MUX, _ssh
from test_minimal_env import _tool_payload

sys.path.insert(0, str(Path(__file__).parents[2] / "src" / "wyoh"))
import wyoh_gamepad as g  # noqa: E402

pytestmark = pytest.mark.live
QUESTIONS = ("Bonjour Mike, qui es-tu ?", "Et la Lune, tu la connais ?")


def test_fn_b_starts_mike_and_mike_answers() -> None:
    if os.environ.get("WYOH_LUNA_LIVE") != "1":
        pytest.skip("set WYOH_LUNA_LIVE=1 with Mannie stopped on Luna")
    lock = _ssh("cat /tmp/luna-brain.lock 2>/dev/null; pgrep -x claude")
    assert not lock.stdout.strip(), f"Mannie still runs: {lock.stdout}"
    result_dir = Path("results/wyoh/luna-mike-window") / datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    result_dir.mkdir(parents=True, exist_ok=False)
    log: list[dict[str, Any]] = []

    async def exercise() -> None:
        parameters = StdioServerParameters(
            command="ssh",
            args=[*SSH_MUX, "-T", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", HOST,
                  "env", "HOME=/storage", f"XDG_RUNTIME_DIR={RUNTIME_DIR}", f"{REMOTE_VENV}/bin/python", REMOTE_SERVER,
                  "--full-ipc-development", "--shared-vnc-session"])
        with (result_dir / "server.stderr.log").open("w", encoding="utf-8") as stderr_log:
            async with Client(stdio_client(parameters, errlog=stderr_log), read_timeout_seconds=60.0) as client:

                async def call(name: str, arguments: dict[str, Any] | None = None) -> Any:
                    result = await client.call_tool(name, arguments or {})
                    assert not result.is_error, f"{name}: {result.content!r}"
                    return _tool_payload(result)

                async def mike() -> tuple[int, str] | None:
                    return g.find_app_title(await call("sway_get_tree"), "mike")

                async def until(what: str, check, timeout: float) -> Any:
                    deadline = time.monotonic() + timeout
                    while not (value := await check()):
                        assert time.monotonic() < deadline, f"timed out: {what}"
                        await asyncio.sleep(0.5)
                    log.append({"t": time.monotonic(), "reached": what, "value": value})
                    return value

                async def shot(name: str) -> None:
                    taken = await call("wyoh_capture_screenshot", {"image_format": "png"})
                    fetched = subprocess.run(["scp", *SSH_MUX, "-q", f"{HOST}:{taken['path']}", str(result_dir / f"{name}.png")],
                                             capture_output=True, text=True, timeout=90, check=False)
                    assert fetched.returncode == 0, fetched.stderr

                async def ask(question: str, started: bool) -> None:
                    before = (await call("wyoh_gamepad_status"))["deliveries"]
                    await call("wyoh_dev_gamepad_tap", {"buttons": ["BTN_TL"]})
                    await until("the Slate is ready", lambda: _ready(call), 20)
                    await call("wyoh_dev_keyboard_type", {"text": question})
                    await asyncio.sleep(0.5)
                    await call("wyoh_dev_gamepad_buttons", {"press": ["BTN_MODE"]})
                    await call("wyoh_dev_gamepad_tap", {"buttons": ["BTN_SOUTH"]})
                    await call("wyoh_dev_gamepad_buttons", {"release": ["BTN_MODE"]})
                    if started:
                        await until("Mike's window exists", mike, 30)
                        await shot("1-starting")
                    t0 = time.monotonic()

                    async def delivered() -> bool:
                        return (await call("wyoh_gamepad_status"))["deliveries"] > before
                    await until("the question is delivered", delivered, 120)
                    log.append({"question": question, "delivered_after_s": round(time.monotonic() - t0, 1)})

                    async def answered() -> bool:
                        window = await mike()
                        return window is not None and window[1] == "Mike — ready"
                    await asyncio.sleep(1.0)
                    await until("Mike is ready again", answered, 180)
                    log.append({"question": question, "answered_after_s": round(time.monotonic() - t0, 1)})

                assert await mike() is None, "close Mike's window before the test"
                # the test's virtual gamepad appears now; the daemon scans for devices every 5 s
                await call("wyoh_dev_gamepad_buttons", {"release": ["BTN_MODE"]})
                await asyncio.sleep(6.5)
                await ask(QUESTIONS[0], started=True)
                await shot("2-first-answer")
                await ask(QUESTIONS[1], started=False)
                await shot("3-second-answer")
                await call("sway_command", {"command": '[app_id="mike"] kill'})
                await until("Mike's window is closed", lambda: _closed(mike), 20)

    asyncio.run(exercise())
    time.sleep(3)
    left = _ssh("pgrep -a llama-server; cat /tmp/luna-brain.lock 2>/dev/null; grep MemAvailable /proc/meminfo")
    (result_dir / "run.json").write_text(json.dumps({"log": log, "after": left.stdout}, indent=2, default=str),
                                         encoding="utf-8")
    assert "llama-server" not in left.stdout and "mike" not in left.stdout.split("MemAvailable")[0], left.stdout


async def _ready(call) -> bool:
    """The Slate is open, connected and has the focus (typing goes into it)."""
    status = await call("wyoh_gamepad_status")
    return (bool(status.get("slate_ready")) and status.get("zone") == "open"
            and _focused_app(await call("sway_get_tree")) == "wyoh-slate")


def _focused_app(tree: dict[str, Any]) -> str | None:
    if tree.get("focused"):
        return tree.get("app_id")
    for child in tree.get("nodes", []) + tree.get("floating_nodes", []):
        found = _focused_app(child)
        if found is not None:
            return found
    return None


async def _closed(mike) -> bool:
    return await mike() is None
