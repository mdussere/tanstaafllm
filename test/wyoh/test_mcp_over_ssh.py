from __future__ import annotations

import asyncio
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest
from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client


PREFIX = "/home/michael/.local/opt/wyoh-sway-1.10.1-test-20260926/usr"
REMOTE_VENV = "/home/michael/.local/opt/wyoh-mcp-2.2.0"
REMOTE_SERVER = f"{REMOTE_VENV}/wyoh_mcp_server.py"
LOCAL_SERVER = Path("worklines/wyoh/scripts/wyoh_mcp_server.py")


def _jsonable(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value


def _tool_payload(result: Any) -> Any:
    """Recover raw JSON replies that the SDK transports as text for `Any` tools."""
    if result.structured_content is not None:
        return _jsonable(result.structured_content)
    if len(result.content) == 1 and hasattr(result.content[0], "text"):
        text = result.content[0].text
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return text
    return _jsonable(result.content)


def _stage_server(result_dir: Path) -> None:
    completed = subprocess.run(
        ["scp", str(LOCAL_SERVER), f"luna-pi:{REMOTE_SERVER}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        timeout=30,
    )
    (result_dir / "stage.stdout.log").write_bytes(completed.stdout)
    (result_dir / "stage.stderr.log").write_bytes(completed.stderr)
    assert completed.returncode == 0, completed.stderr.decode("utf-8", errors="replace")


async def _exercise(result_dir: Path) -> dict[str, Any]:
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
            REMOTE_SERVER,
            "--full-ipc-development",
            "--sway-binary",
            f"{PREFIX}/bin/sway",
            "--library-path",
            f"{PREFIX}/lib/aarch64-linux-gnu",
        ],
    )
    evidence: dict[str, Any] = {"calls": {}, "events": []}

    with (result_dir / "server.stderr.log").open("w", encoding="utf-8") as stderr_log:
        async with Client(
            stdio_client(parameters, errlog=stderr_log), read_timeout_seconds=15.0
        ) as client:
            async def run_client() -> None:
                discovered = await client.list_tools()
                evidence["protocol_version"] = client.protocol_version
                evidence["tool_names"] = sorted(tool.name for tool in discovered.tools)

                async def call(name: str, arguments: dict[str, Any] | None = None) -> Any:
                    result = await client.call_tool(name, arguments or {})
                    assert not result.is_error, f"{name}: {result.content!r}"
                    payload = _tool_payload(result)
                    evidence["calls"][name] = payload
                    return payload

                for name, arguments in (
                    ("sway_get_workspaces", {}),
                    ("sway_get_outputs", {}),
                    ("sway_get_tree", {}),
                    ("sway_get_marks", {}),
                    ("sway_get_bar_config", {}),
                    ("sway_get_version", {}),
                    ("sway_get_binding_modes", {}),
                    ("sway_get_config", {}),
                    ("sway_sync", {}),
                    ("sway_get_binding_state", {}),
                    ("sway_get_inputs", {}),
                    ("sway_get_seats", {}),
                    ("wyoh_server_status", {}),
                ):
                    await call(name, arguments)

                subscription = await call(
                    "sway_subscribe",
                    {"event_names": ["workspace", "tick", "shutdown"]},
                )
                subscription_id = subscription["subscription_id"]

                async def wait_for(event_name: str, predicate: Any = lambda _: True) -> dict[str, Any]:
                    for _ in range(8):
                        event = await call(
                            "sway_next_event",
                            {"subscription_id": subscription_id, "timeout_seconds": 5.0},
                        )
                        evidence["events"].append(event)
                        if event.get("timeout"):
                            continue
                        if event["event"] == event_name and predicate(event["payload"]):
                            return event
                    raise AssertionError(f"did not observe {event_name}; events={evidence['events']!r}")

                await call("sway_command", {"command": "workspace wyoh-proof"})
                await wait_for("workspace", lambda payload: payload.get("current", {}).get("name") == "wyoh-proof")
                await call("sway_send_tick", {"payload": "wyoh-mcp-live"})
                await wait_for("tick", lambda payload: payload.get("payload") == "wyoh-mcp-live")
                idle_wait = await call(
                    "sway_next_event",
                    {"subscription_id": subscription_id, "timeout_seconds": 0.1},
                )
                assert idle_wait["timeout"] is True

                await call("wyoh_stop_owned_child_for_test")
                await wait_for("shutdown", lambda payload: payload.get("change") == "exit")
                await call("sway_unsubscribe", {"subscription_id": subscription_id})
                await call("wyoh_server_status")
            await run_client()
    return evidence


@pytest.mark.live
def test_luna_pi_full_sway_ipc_mcp_over_ssh() -> None:
    if os.environ.get("WYOH_LIVE") != "1":
        pytest.skip("set WYOH_LIVE=1 to run against luna-pi")
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    result_dir = Path("results/wyoh/mcp-over-ssh") / timestamp
    result_dir.mkdir(parents=True, exist_ok=False)
    _stage_server(result_dir)
    evidence = asyncio.run(_exercise(result_dir))
    (result_dir / "evidence.json").write_text(
        json.dumps(evidence, indent=2, sort_keys=True), encoding="utf-8"
    )

    expected_tools = {
        "sway_command",
        "sway_get_workspaces",
        "sway_subscribe",
        "sway_get_outputs",
        "sway_get_tree",
        "sway_get_marks",
        "sway_get_bar_config",
        "sway_get_version",
        "sway_get_binding_modes",
        "sway_get_config",
        "sway_send_tick",
        "sway_sync",
        "sway_get_binding_state",
        "sway_get_inputs",
        "sway_get_seats",
        "sway_next_event",
        "sway_unsubscribe",
        "wyoh_server_status",
        "wyoh_stop_owned_child_for_test",
    }
    assert set(evidence["tool_names"]) == expected_tools
    assert evidence["calls"]["sway_get_version"]["human_readable"] == "1.10.1"
    assert evidence["calls"]["wyoh_server_status"]["full_ipc_development_mode"] is True
    assert evidence["calls"]["wyoh_server_status"]["sway_child_state"] == "stopped"
    assert {event["event"] for event in evidence["events"] if "event" in event} >= {
        "workspace",
        "tick",
        "shutdown",
    }
