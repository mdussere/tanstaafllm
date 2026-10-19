"""Mike Step 3b.2: the fake MCP server answers over real stdio MCP and records each call."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

from mcp import Client, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = Path(__file__).with_name("mike_fake_mcp.py")


def test_fake_mcp_lists_tools_and_records_a_call(tmp_path):
    log = tmp_path / "calls.jsonl"

    async def exercise():
        parameters = StdioServerParameters(command=sys.executable, args=[str(SERVER)],
                                           env={"MIKE_FAKE_MCP_LOG": str(log)})
        async with Client(stdio_client(parameters), read_timeout_seconds=30.0) as client:
            tools = sorted(tool.name for tool in (await client.list_tools()).tools)
            result = await client.call_tool("launch_app", {"app": "calculator"})
            return tools, result

    tools, result = asyncio.run(exercise())
    assert tools == ["close_window", "focus_window", "launch_app", "list_windows", "move_window", "type_text"]
    assert not result.is_error
    calls = [json.loads(line) for line in log.read_text().splitlines()]
    assert [(c["tool"], c["args"]) for c in calls] == [("launch_app", {"app": "calculator"})]
