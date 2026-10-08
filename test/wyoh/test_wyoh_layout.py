"""Deterministic tests for the Wyoh four-tile layout policy (user requirement 2026-10-08)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "src" / "wyoh"))
import wyoh_layout as layout  # noqa: E402

T = layout.Tile
M = layout.MARK


def test_first_window_needs_nothing():
    assert layout.plan([], 1) == layout.Plan(())


def test_second_window_splits_vertically_and_goes_on_top():
    assert layout.plan([T(1, 0, 22, 720, 698)], 2).commands == (
        "[con_id=1] splitv", f"[con_id=1] mark --add {M}", f"[con_id=2] move to mark {M}",
        "[con_id=2] move up", f"[con_id=1] unmark {M}", "[con_id=2] focus",
    )


def test_third_window_goes_top_right():
    top, bottom = T(2, 0, 22, 720, 349), T(1, 0, 371, 720, 349)
    assert layout.plan([bottom, top], 3).commands == (
        "[con_id=2] splith", f"[con_id=2] mark --add {M}", f"[con_id=3] move to mark {M}", f"[con_id=2] unmark {M}",
        "[con_id=3] focus",
    )


def test_fourth_window_goes_bottom_right():
    tiles = [T(2, 0, 22, 360, 349), T(3, 360, 22, 360, 349), T(1, 0, 371, 720, 349)]
    assert layout.plan(tiles, 4).commands == (
        "[con_id=1] splith", f"[con_id=1] mark --add {M}", f"[con_id=4] move to mark {M}", f"[con_id=1] unmark {M}",
        "[con_id=4] focus",
    )


def test_fifth_window_is_refused_and_closed():
    tiles = [T(2, 0, 22, 360, 349), T(3, 360, 22, 360, 349), T(1, 0, 371, 360, 349), T(4, 360, 371, 360, 349)]
    decision = layout.plan(tiles, 5)
    assert decision.refused and decision.commands == ("[con_id=5] kill",)


def test_after_closing_a_top_tile_the_top_row_is_refilled_first():
    # 2 and 3 on top, 1 and 4 below; 3 closed -> top row single again
    tiles = [T(2, 0, 22, 720, 349), T(1, 0, 371, 360, 349), T(4, 360, 371, 360, 349)]
    assert layout.plan(tiles, 5).commands[0] == "[con_id=2] splith"


def test_two_tiles_side_by_side_get_a_new_row_below():
    tiles = [T(1, 0, 22, 360, 698), T(2, 360, 22, 360, 698)]
    assert layout.plan(tiles, 3).commands == ("[con_id=3] move down", "[con_id=3] focus")


def test_rows_tolerate_small_offsets():
    rows = layout._rows([T(1, 0, 22, 360, 349), T(2, 360, 24, 360, 349), T(3, 0, 371, 720, 349)])
    assert [[t.con_id for t in row] for row in rows] == [[1, 2], [3]]


def _tree(*workspaces):
    return {"type": "root", "id": 0, "nodes": [{"type": "output", "id": 9, "nodes": list(workspaces)}]}


def _ws(ws_id, tiled, floating=()):
    return {"type": "workspace", "id": ws_id, "nodes": list(tiled), "floating_nodes": list(floating)}


def _con(con_id, x=0, y=22, w=720, h=698, kind="con"):
    return {"type": kind, "id": con_id, "pid": 100 + con_id, "rect": {"x": x, "y": y, "width": w, "height": h},
            "nodes": [], "floating_nodes": []}


def test_only_tiles_of_the_new_windows_workspace_are_counted():
    tree = _tree(_ws(10, [_con(1), _con(2)]), _ws(11, [_con(3), _con(4), _con(5), _con(6)]))
    tiles, tiled = layout._workspace_tiles(tree, 2)
    assert [t.con_id for t in tiles] == [1] and tiled


def test_floating_windows_are_not_tiles():
    tree = _tree(_ws(10, [_con(1)], floating=[_con(7, kind="floating_con")]))
    tiles, tiled = layout._workspace_tiles(tree, 7)
    assert [t.con_id for t in tiles] == [1] and not tiled


def test_nested_containers_are_walked():
    container = {"type": "con", "id": 50, "pid": None, "rect": {}, "nodes": [_con(2), _con(3)], "floating_nodes": []}
    tree = _tree(_ws(10, [container, _con(1, y=371)]))
    tiles, _ = layout._workspace_tiles(tree, 3)
    assert sorted(t.con_id for t in tiles) == [1, 2]
