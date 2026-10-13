"""Mike v0 tool contract and adapter (worklines/mike/docs/0102_01).

The model sees seven task-level tools with closed value lists. The adapter
checks a proposed call against the current desktop and turns it into Wyoh MCP
requests from fixed templates: nothing the model writes reaches Sway as is.

Standard library only. `propose()` is pure; `run()` sends the planned
requests to any object with `call_tool(name, arguments)` (the real Wyoh MCP
client in Step 5, a fake in the tests).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class App:
    id: str
    names_fr: tuple[str, ...]
    app_id: str | None  # Sway app_id; None until Wyoh's manifest exists
    exec: str | None  # the Wyoh entry's Exec= line
    source: str
    available: bool


# Contract section 2, copied from Wyoh's entries on 2026-10-09. Wyoh apps
# (calculator and the planned ones) take their Exec= from the `.desktop` entry
# Wyoh generates on the device (`<app dir>/run`), so it is unknown here; the
# allowlist is to be generated from those entries (contract section 2).
ALLOWLIST: tuple[App, ...] = (
    App("terminal", ("terminal", "console"), "foot", "foot", "wyoh-terminal.desktop", True),
    App("editor", ("éditeur", "éditeur de texte"), "wyoh-editor", "foot -a wyoh-editor vim",
        "wyoh-editor.desktop", True),
    App("images", ("visionneuse", "images", "photos"), "swayimg",
        "env -u SWAYSOCK -u I3SOCK swayimg -c general.background=#202020 "
        "/usr/share/retroarch-assets/rgui/wallpaper/leaves.png", "wyoh-imageviewer.desktop", True),
    App("tasks", ("gestionnaire de tâches", "tâches", "processus"), "wyoh-htop", "foot -a wyoh-htop htop",
        "wyoh-taskmanager.desktop", True),
    App("calculator", ("calculatrice", "calculette"), "wyoh-calculator", None, "Wyoh app calculator", True),
    App("browser", ("navigateur", "internet", "netsurf"), None, None, "planned Wyoh app (NetSurf)", False),
    App("files", ("gestionnaire de fichiers", "fichiers", "commander"), None, None,
        "planned Wyoh app (Commander)", False),
    App("chess", ("échecs",), None, None, "planned Wyoh app (pygameUCI + Stockfish)", False),
    App("wolfenstein", ("wolfenstein", "wolf"), None, None, "planned Wyoh app (PortMaster)", False),
    App("dino", ("dino", "dinosaure", "jeu du dinosaure"), None, None, "planned Wyoh app (Dino)", False),
)
APPS: dict[str, App] = {app.id: app for app in ALLOWLIST}
APP_IDS: list[str] = [app.id for app in ALLOWLIST]
PLACES: list[str] = ["left", "right", "top", "bottom", "full"]
SWAY_DIRECTION = {"left": "left", "right": "right", "top": "up", "bottom": "down"}  # Sway: move <direction>
TEXT_MAX = 200
REASON_MAX = 120


def _tool(name: str, description: str, properties: dict[str, Any]) -> dict[str, Any]:
    return {"type": "function", "function": {
        "name": name, "description": description,
        "parameters": {"type": "object", "properties": properties, "required": list(properties)},
    }}


_APP = {"type": "string", "enum": APP_IDS}
TOOLS: list[dict[str, Any]] = [
    _tool("list_windows", "List the open windows (quelles fenêtres sont ouvertes).", {}),
    _tool("focus_window", "Bring an already open window to the front (passe sur, va sur).", {"app": _APP}),
    _tool("launch_app", "Start an application (ouvre, lance, démarre).", {"app": _APP}),
    _tool("close_window", "Close an open window (ferme, quitte).", {"app": _APP}),
    _tool("move_window", "Move a window left, right, up or down, or make it full screen (mets, place).",
          {"app": _APP, "place": {"type": "string", "enum": PLACES}}),
    _tool("type_text", "Type the given text into the focused window (écris, tape, saisis).",
          {"text": {"type": "string"}}),
    _tool("none", "Use when no other tool fits (questions, messages, weather).", {"reason": {"type": "string"}}),
]
TOOL_NAMES: list[str] = [tool["function"]["name"] for tool in TOOLS]
NEEDS_OPEN = {"focus_window", "close_window", "move_window"}


@dataclass(frozen=True)
class Call:
    tool: str
    args: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Desktop:
    open: tuple[str, ...]  # Mike ids of open windows
    focus: str | None = None
    installed: frozenset[str] = frozenset(app.id for app in ALLOWLIST if app.available)


@dataclass(frozen=True)
class Proposal:
    """What the console shows. `kind`: run, ask (needs acceptance), refuse, nothing."""

    kind: str
    call: Call  # the call that would run (after any rewrite)
    message: str
    requests: tuple[tuple[str, dict[str, Any]], ...] = ()
    rewritten_from: Call | None = None
    confirm_twice: bool = False


def _criteria(app: App) -> str:
    return f'[app_id="{app.app_id}"]'


def propose(call: Call, desktop: Desktop) -> Proposal:
    """Check `call` against the contract and the desktop; plan its Wyoh MCP requests."""
    if call.tool not in TOOL_NAMES:
        return Proposal("refuse", call, f"unknown tool {call.tool!r}")
    expected = set(next(t for t in TOOLS if t["function"]["name"] == call.tool)["function"]["parameters"]["properties"])
    if set(call.args) != expected:
        return Proposal("refuse", call, f"{call.tool} takes {sorted(expected)}, got {sorted(call.args)}")

    if call.tool == "none":
        reason = call.args["reason"].strip()[:REASON_MAX] or "no tool fits"
        return Proposal("nothing", call, f"Mike cannot do this: {reason}")
    if call.tool == "list_windows":
        return Proposal("run", call, "list the open windows", (("sway_get_tree", {}),))
    if call.tool == "type_text":
        text = call.args["text"]
        if not text.strip() or len(text) > TEXT_MAX or "\n" in text:
            return Proposal("refuse", call, f"text must be one line of 1–{TEXT_MAX} characters")
        if desktop.focus is None:
            return Proposal("refuse", call, "no window has focus")
        return Proposal("ask", call, f"type {text!r} into {desktop.focus}",
                        (("wyoh_dev_keyboard_type", {"text": text}),))

    name = call.args["app"]
    app = APPS.get(name)
    if app is None:
        return Proposal("refuse", call, f"{name!r} is not on the allowlist")
    if call.tool == "move_window" and call.args["place"] not in PLACES:
        return Proposal("refuse", call, f"place must be one of {PLACES}")

    rewritten_from = None
    if call.tool == "focus_window" and name not in desktop.open:
        # Contract rule 2 (awaiting the user's approval): focus a closed app → launch it.
        rewritten_from, call = call, Call("launch_app", {"app": name})

    if call.tool == "launch_app":
        if name not in desktop.installed:
            return Proposal("refuse", call, f"{name} is not installed", rewritten_from=rewritten_from)
        if app.exec is None:
            return Proposal("refuse", call, f"{name}'s launch command is not known yet (from Wyoh's entry)",
                            rewritten_from=rewritten_from)
        command = app.exec
        prefix = f"{name} is not open: " if rewritten_from else ""
        return Proposal("ask", call, f"{prefix}launch {name}", (("sway_command", {"command": f"exec {command}"}),),
                        rewritten_from=rewritten_from)

    if name not in desktop.open:
        return Proposal("refuse", call, f"{name} is not open")
    if app.app_id is None:
        return Proposal("refuse", call, f"{name} has no known window id")
    if call.tool == "focus_window":
        return Proposal("ask", call, f"bring {name} to the front",
                        (("sway_command", {"command": f"{_criteria(app)} focus"}),))
    if call.tool == "close_window":
        return Proposal("ask", call, f"close {name}? unsaved work may be lost",
                        (("sway_command", {"command": f"{_criteria(app)} kill"}),), confirm_twice=True)
    place = call.args["place"]
    if place == "full":
        return Proposal("ask", call, f"make {name} full screen",
                        (("sway_command", {"command": f"{_criteria(app)} fullscreen toggle"}),))
    return Proposal("ask", call, f"move {name} one step {place}",
                    (("sway_command", {"command": f"{_criteria(app)} focus"}),
                     ("sway_command", {"command": f"move {SWAY_DIRECTION[place]}"})))


class ToolClient(Protocol):
    def call_tool(self, name: str, arguments: dict[str, Any]) -> Any: ...


def run(proposal: Proposal, client: ToolClient, accepted: bool) -> list[Any]:
    """Send the planned requests; `ask` proposals only once the user accepted."""
    if proposal.kind in ("refuse", "nothing"):
        return []
    if proposal.kind == "ask" and not accepted:
        return []
    return [client.call_tool(name, arguments) for name, arguments in proposal.requests]


def windows_from_tree(tree: dict[str, Any]) -> Desktop:
    """Map a Sway GET_TREE reply to open Mike ids and the focused one."""
    by_app_id = {app.app_id: app.id for app in ALLOWLIST if app.app_id}
    open_: list[str] = []
    focus = None

    def walk(node: dict[str, Any]) -> None:
        nonlocal focus
        mike_id = by_app_id.get(node.get("app_id") or "")
        if mike_id and node.get("type") in ("con", "floating_con"):
            if mike_id not in open_:
                open_.append(mike_id)
            if node.get("focused"):
                focus = mike_id
        for child in node.get("nodes", []) + node.get("floating_nodes", []):
            walk(child)

    walk(tree)
    return Desktop(tuple(open_), focus)


def desktop_line(desktop: Desktop) -> str:
    """The desktop state as given to the model at the start of the user turn."""
    opened = ", ".join(desktop.open) or "none"
    return f"[open: {opened}; focus: {desktop.focus or 'none'}]"
