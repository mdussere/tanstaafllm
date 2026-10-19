"""Mike Step 3b.2: a stdio MCP server with Mike's contract tools, for trying micro-harnesses.

Each tool runs the contract's adapter (`propose`) against a scripted desktop
and returns the proposal as text; nothing reaches a real desktop. Every call
is appended to the JSON-lines file named by `MIKE_FAKE_MCP_LOG`, so a test can
check which tool a harness called, with which arguments.

    uv run python test/mike/mike_fake_mcp.py   # speaks MCP on stdin/stdout
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).parents[2] / "src" / "mike"))
import mike_contract as contract  # noqa: E402
from mcp.server import MCPServer  # noqa: E402

DESKTOP = contract.Desktop(("terminal",), "terminal")
App = Literal[tuple(contract.APP_IDS)]  # type: ignore[valid-type]
Place = Literal[tuple(contract.PLACES)]  # type: ignore[valid-type]

mcp = MCPServer("mike-fake-wyoh", version="0.1.0",
                instructions="Mike's desktop tools. Each call is a proposal; the user accepts it before it runs.")


def _record(tool: str, args: dict[str, str]) -> str:
    proposal = contract.propose(contract.Call(tool, args), DESKTOP)
    log = os.environ.get("MIKE_FAKE_MCP_LOG")
    if log:
        with open(log, "a") as out:
            out.write(json.dumps({"t": time.time(), "tool": tool, "args": args, "kind": proposal.kind,
                                  "message": proposal.message}, ensure_ascii=False) + "\n")
    return f"{proposal.kind}: {proposal.message}"


@mcp.tool()
def list_windows() -> str:
    """List the open windows (quelles fenêtres sont ouvertes)."""
    return _record("list_windows", {})


@mcp.tool()
def focus_window(app: App) -> str:
    """Bring an already open window to the front (passe sur, va sur)."""
    return _record("focus_window", {"app": app})


@mcp.tool()
def launch_app(app: App) -> str:
    """Start an application (ouvre, lance, démarre)."""
    return _record("launch_app", {"app": app})


@mcp.tool()
def close_window(app: App) -> str:
    """Close an open window (ferme, quitte)."""
    return _record("close_window", {"app": app})


@mcp.tool()
def move_window(app: App, place: Place) -> str:
    """Move a window left, right, up or down, or make it full screen (mets, place)."""
    return _record("move_window", {"app": app, "place": place})


@mcp.tool()
def type_text(text: str) -> str:
    """Type the given text into the focused window (écris, tape, saisis)."""
    return _record("type_text", {"text": text})


if __name__ == "__main__":
    mcp.run(transport="stdio")
