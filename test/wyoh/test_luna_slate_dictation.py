"""Step 12: Mycroft's dictation in the Slate on Luna, with its --fake mode.

Contract: `luna_slate_dictation.feature`. The daemon's `dictate_command` is
switched to `mycroft_dictate.py --fake "bonjour luna"` for the run and restored
afterwards. The person is the MCP virtual gamepad and keyboard.
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

from test_luna_minimal_env import SSH_MUX, HOST, REMOTE_SERVER, REMOTE_VENV, RUNTIME_DIR, _ssh
from test_luna_slate import _slate_open
from test_minimal_env import RENDER_TIMEOUT, Predicate, _app_windows, _tool_payload

CONFIG = "/storage/.local/share/tanstfaafllm/wyoh/deploy/luna/gamepad.toml"
DICTATE = "/storage/.local/share/tanstfaafllm/mycroft/mycroft_dictate.py"
FAKE_TEXT = "bonjour luna"
FAKE = f'dictate_command = ["/usr/bin/python3", "{DICTATE}", "--fake", "{FAKE_TEXT}", "--fake-interval", "0.6"]'


def _use_fake_dictation() -> None:
    script = (f"python3 - <<'EOF'\nimport re\np='{CONFIG}'\ns=open(p).read()\n"
              f"s=re.sub(r'(?ms)^dictate_command = \\[.*?^\\]\\n', {FAKE!r} + '\\n', s, count=1)\n"
              f"open(p,'w').write(s)\nEOF\nsystemctl restart wyoh-gamepad.service")
    result = _ssh(script)
    assert result.returncode == 0, result.stderr


@pytest.mark.live
def test_luna_dictation_into_the_slate() -> None:
    if os.environ.get("WYOH_LUNA_LIVE") != "1":
        pytest.skip("set WYOH_LUNA_LIVE=1; restore with `make wyoh-luna-deploy` if interrupted")
    state = _ssh(f"test -f {DICTATE} && systemctl is-active wyoh-sway.service wyoh-gamepad.service")
    assert state.returncode == 0, state.stdout + state.stderr
    original = _ssh(f"cat {CONFIG}").stdout
    _use_fake_dictation()

    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    result_dir = Path("results/wyoh/luna-slate-dictation") / timestamp
    result_dir.mkdir(parents=True, exist_ok=False)
    target = f"/tmp/wyoh-dictation-{timestamp}"
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
                    await asyncio.sleep(0.2)

                async def status() -> dict[str, Any]:
                    return await call("wyoh_gamepad_status")

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
                    shot = await call("wyoh_capture_screenshot", {"image_format": "jpeg", "quality": 85})
                    path = result_dir / f"{name}.jpg"
                    fetched = subprocess.run(["scp", *SSH_MUX, "-q", f"{HOST}:{shot['path']}", str(path)],
                                             capture_output=True, text=True, timeout=90, check=False)
                    assert fetched.returncode == 0, fetched.stderr
                    with Image.open(path) as image:
                        image = image.convert("RGB")
                    assert predicate(image), f"{name}: unexpected screen"
                    steps.append({"step": name, "status": await status()})
                    return image

                async def dictation_is(state: str) -> bool:
                    return (await status()).get("dictation") == state

                await call("wyoh_dev_gamepad_buttons", {})
                await until("virtual gamepad attached",
                            lambda: _count_devices(status), timeout=2 * RENDER_TIMEOUT)
                await tap("BTN_START")
                await asyncio.sleep(0.8)
                await call("wyoh_dev_keyboard_type", {"text": "term"})
                await tap("BTN_EAST")
                await until("terminal focused", lambda: _focused(windows, "foot"))
                await tap("BTN_TL")
                await until("Slate connected", lambda: _ready(status))
                await call("wyoh_dev_keyboard_type", {"text": "echo "})
                await asyncio.sleep(0.5)
                await observe("01-slate-echo", _slate_open)

                await tap("BTN_TL2")  # L2: start dictation
                await until("dictation listening", lambda: dictation_is("listening"))
                await asyncio.sleep(1.0)  # the fake provider reveals a word every 0.6 s
                await observe("02-listening-provisional", _slate_open)
                await tap("BTN_TL2")  # L2 again: stop, the final text is inserted
                await until("dictation off", lambda: dictation_is("off"))
                await asyncio.sleep(0.5)
                await observe("03-inserted", _slate_open)

                await call("wyoh_dev_keyboard_type", {"text": f" > {target}"})
                await call("wyoh_dev_gamepad_buttons", {"press": ["BTN_MODE"]})
                await tap("BTN_EAST")  # FN+A: send
                await call("wyoh_dev_gamepad_buttons", {"release": ["BTN_MODE"]})
                await until("sent", lambda: _zone_closed(status))
                await tap("BTN_EAST")  # Return in the terminal
                await until(f"{target} written", lambda: _file_holds(target, FAKE_TEXT + "\n"))
                await observe("04-sent")
                await call("wyoh_dev_gamepad_buttons", {"press": ["BTN_MODE"]})
                await tap("BTN_SOUTH")
                await call("wyoh_dev_gamepad_buttons", {"release": ["BTN_MODE"]})

    try:
        asyncio.run(exercise())
    finally:
        restore = subprocess.run(["ssh", *SSH_MUX, HOST, f"cat > {CONFIG} && systemctl restart wyoh-gamepad.service"],
                                 input=original, text=True, capture_output=True, timeout=60, check=False)
        (result_dir / "evidence.json").write_text(json.dumps({"steps": steps, "restored": restore.returncode == 0},
                                                             indent=2, sort_keys=True, ensure_ascii=False),
                                                  encoding="utf-8")
        _ssh(f"rm -f {target}")
    assert restore.returncode == 0, restore.stderr


async def _count_devices(status) -> bool:
    return len((await status()).get("devices", [])) >= 2


async def _focused(windows, app_id: str) -> bool:
    return any(w["app_id"] == app_id and w["focused"] for w in await windows())


async def _ready(status) -> bool:
    return bool((await status()).get("slate_ready"))


async def _zone_closed(status) -> bool:
    return (await status()).get("zone") == "closed"


async def _file_holds(path: str, expected: str) -> bool:
    result = _ssh(f"cat {path}")
    return result.returncode == 0 and result.stdout == expected
