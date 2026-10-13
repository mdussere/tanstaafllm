"""A scripted stand-in for the Wyoh MCP server (Mike Step 2.2).

It answers the few Wyoh MCP tools Mike's adapter uses, with the same names
and argument names as `src/wyoh/wyoh_mcp_server.py`, keeps a tiny desktop
state, and records every request. Any other tool name is an error, so a test
fails if the adapter strays outside the contract. The real MCP transport is
exercised against Wyoh itself in Mike Step 5.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parents[2] / "src" / "mike"))
import mike_contract as contract  # noqa: E402


WYOH_TOOLS = {"sway_get_tree", "sway_command", "wyoh_dev_keyboard_type"}


class FakeWyoh:
    def __init__(self, desktop: contract.Desktop):
        self.open = list(desktop.open)
        self.focus = desktop.focus
        self.fullscreen: set[str] = set()
        self.typed: list[str] = []
        self.requests: list[tuple[str, dict[str, Any]]] = []
        self._by_app_id = {app.app_id: app.id for app in contract.ALLOWLIST if app.app_id}
        self._by_exec = {app.exec: app.id for app in contract.ALLOWLIST if app.exec}

    def call_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        self.requests.append((name, dict(arguments)))
        if name not in WYOH_TOOLS:
            raise ValueError(f"fake Wyoh: unexpected tool {name!r}")
        if name == "sway_get_tree":
            return self.tree()
        if name == "wyoh_dev_keyboard_type":
            self.typed.append(arguments["text"])
            return {"typed_characters": len(arguments["text"])}
        return self._command(arguments["command"])

    def tree(self) -> dict[str, Any]:
        windows = [{"type": "con", "app_id": contract.APPS[i].app_id, "focused": i == self.focus,
                    "nodes": [], "floating_nodes": []} for i in self.open]
        return {"type": "root", "nodes": [{"type": "workspace", "nodes": windows, "floating_nodes": []}],
                "floating_nodes": []}

    def _command(self, command: str) -> list[dict[str, Any]]:
        if command.startswith("exec "):
            app = self._by_exec.get(command[5:])
            if app is None:
                return [{"success": False, "error": "fake Wyoh: unknown exec"}]
            if app not in self.open:
                self.open.append(app)
            self.focus = app
            return [{"success": True}]
        match = re.fullmatch(r'\[app_id="([^"]+)"\] (focus|kill|fullscreen toggle)', command)
        if match:
            app = self._by_app_id.get(match.group(1))
            if app not in self.open:
                return [{"success": False, "error": "No matching node."}]
            action = match.group(2)
            if action == "kill":
                self.open.remove(app)
                self.focus = self.open[-1] if self.open else None
            elif action == "fullscreen toggle":
                self.fullscreen ^= {app}
            else:
                self.focus = app
            return [{"success": True}]
        if re.fullmatch(r"move (left|right|up|down)", command):
            return [{"success": True}]
        return [{"success": False, "error": f"fake Wyoh: unsupported command {command!r}"}]
