#!/usr/bin/env python3
"""Wyoh layout policy: at most four tiles per workspace, in a fixed order.

User requirement (2026-10-08): "limit the number of splits of the frontend to
4 windows. First do a vertical split (new window on top); second, a
horizontal split of the top (new window on the top right); third, a
horizontal split of the bottom (new window on the bottom right); after that
an error pops up: 'Too many tiles'."

The policy works from the current geometry, not from the order windows were
opened, so it stays coherent after windows close: a new window goes beside the
window that is alone in its row (top row first when building up), and a fifth
tile is refused. Floating windows are not tiles and are left alone.

Standard library only. `plan()` is pure; `main()` subscribes to Sway window
events and applies it.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import struct
import subprocess
import sys
from dataclasses import dataclass
from typing import Any

from wyoh_gamepad import DESCRIPTOR, SwayClient

MAX_TILES = 4
MARK = "_wyoh_layout_anchor"
ROW_TOLERANCE = 4  # px


@dataclass(frozen=True)
class Tile:
    con_id: int
    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class Plan:
    commands: tuple[str, ...]
    refused: bool = False


def _rows(tiles: list[Tile]) -> list[list[Tile]]:
    """Group tiles into rows by their top edge, top row first, left to right."""
    rows: list[list[Tile]] = []
    for tile in sorted(tiles, key=lambda t: (t.y, t.x)):
        if rows and abs(rows[-1][0].y - tile.y) <= ROW_TOLERANCE:
            rows[-1].append(tile)
        else:
            rows.append([tile])
    return rows


def _beside(anchor: int, new: int) -> tuple[str, ...]:
    """Split `anchor` horizontally and put `new` to its right."""
    return (
        f"[con_id={anchor}] splith",
        f"[con_id={anchor}] mark --add {MARK}",
        f"[con_id={new}] move to mark {MARK}",
        f"[con_id={anchor}] unmark {MARK}",
        f"[con_id={new}] focus",  # the new window keeps the focus after being moved
    )


def plan(existing: list[Tile], new: int) -> Plan:
    """Commands that place tile `new` among `existing` tiles of its workspace."""
    count = len(existing)
    if count == 0:
        return Plan(())
    if count >= MAX_TILES:
        return Plan((f"[con_id={new}] kill",), refused=True)
    rows = _rows(existing)
    if count == 1:  # vertical split, new window on top
        only = existing[0].con_id
        return Plan((
            f"[con_id={only}] splitv",
            f"[con_id={only}] mark --add {MARK}",
            f"[con_id={new}] move to mark {MARK}",
            f"[con_id={new}] move up",
            f"[con_id={only}] unmark {MARK}",
            f"[con_id={new}] focus",
        ))
    singles = [row[0] for row in rows if len(row) == 1]
    if singles:
        # count 2: the top row first; count 3: the remaining single (bottom).
        anchor = singles[0] if count == 2 else singles[-1]
        return Plan(_beside(anchor.con_id, new))
    # Every row already holds two tiles (e.g. after closing): start a new row below.
    return Plan((f"[con_id={new}] move down", f"[con_id={new}] focus"))


# --- Sway adapter -------------------------------------------------------------

def _workspace_tiles(tree: dict[str, Any], new: int) -> tuple[list[Tile], bool] | None:
    """Tiles on the workspace holding `new`, and whether `new` is tiled."""
    def walk(node: dict[str, Any], workspace: dict[str, Any] | None):
        if node.get("type") == "workspace":
            workspace = node
        if node.get("id") == new:
            return workspace, node.get("type") == "con"
        for child in node.get("nodes", []) + node.get("floating_nodes", []):
            found = walk(child, workspace)
            if found:
                return found
        return None

    found = walk(tree, None)
    if not found or found[0] is None:
        return None
    workspace, tiled = found
    tiles: list[Tile] = []

    def collect(node: dict[str, Any]) -> None:
        if node.get("type") == "con" and node.get("pid") and node["id"] != new:
            rect = node["rect"]
            tiles.append(Tile(node["id"], rect["x"], rect["y"], rect["width"], rect["height"]))
        for child in node.get("nodes", []):  # tiled children only
            collect(child)

    collect(workspace)
    return tiles, tiled


class Layout:
    def __init__(self, sway: SwayClient, popup: list[str]) -> None:
        self.sway = sway
        self.popup_command = popup
        self.popup: subprocess.Popen[bytes] | None = None

    def on_new_window(self, con_id: int) -> Plan | None:
        found = _workspace_tiles(self.sway.request(4), con_id)
        if found is None or not found[1]:
            return None  # gone already, or floating: not a tile
        decision = plan(found[0], con_id)
        if decision.commands:
            self.sway.command("; ".join(decision.commands))
        if decision.refused:
            self.show_popup()
        return decision

    def show_popup(self) -> None:
        if self.popup is not None and self.popup.poll() is None:
            return
        env = dict(os.environ)
        display = self.sway.wayland_display()
        if display:
            env["WAYLAND_DISPLAY"] = display
        self.popup = subprocess.Popen(self.popup_command, env=env, stdin=subprocess.DEVNULL,
                                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def _subscribe(socket_path: str) -> socket.socket:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)
    body = json.dumps(["window"]).encode()
    sock.sendall(SwayClient.MAGIC + struct.pack("=II", len(body), 2) + body)
    header = SwayClient._recv(sock, len(SwayClient.MAGIC) + 8)
    length, _ = struct.unpack("=II", header[len(SwayClient.MAGIC):])
    reply = json.loads(SwayClient._recv(sock, length))
    if not reply.get("success"):
        raise ConnectionError(f"Sway refused the subscription: {reply}")
    return sock


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("popup", nargs=argparse.REMAINDER,
                        help="after --: the command showing the 'Too many tiles' message")
    args = parser.parse_args()
    if args.popup[:1] == ["--"]:
        args.popup = args.popup[1:]
    if not args.popup:
        parser.error("a pop-up command is required after --")
    sway = SwayClient(DESCRIPTOR)
    socket_path = json.loads(DESCRIPTOR.read_text(encoding="utf-8"))["sway_socket"]
    layout = Layout(sway, args.popup)
    sock = _subscribe(socket_path)
    print("wyoh-layout: watching window events", file=sys.stderr, flush=True)
    while True:
        header = SwayClient._recv(sock, len(SwayClient.MAGIC) + 8)
        length, _ = struct.unpack("=II", header[len(SwayClient.MAGIC):])
        event = json.loads(SwayClient._recv(sock, length))
        if event.get("change") != "new":
            continue
        try:
            decision = layout.on_new_window(event["container"]["id"])
            if decision and decision.refused:
                print("wyoh-layout: refused a fifth tile", file=sys.stderr, flush=True)
        except (OSError, ConnectionError, KeyError, ValueError) as error:
            print(f"wyoh-layout: {error}", file=sys.stderr, flush=True)


if __name__ == "__main__":
    raise SystemExit(main())
