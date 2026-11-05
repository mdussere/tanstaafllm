import importlib.util
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "worklines"
    / "bill"
    / "scripts"
    / "build_luna_segment_index.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("build_luna_segment_index", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _segment(start, end, kind="sequence"):
    return {
        "start_line": start,
        "end_line": end,
        "kind": kind,
        "title": "Example",
        "summary": "A bounded event sequence.",
        "state": "completed",
        "uncertainty": "The fixture does not prove a device outcome.",
        "anchor_lines": [start] if kind == "sequence" else [],
    }


def test_valid_index_covers_each_source_line_once():
    module = _load()
    parts = [[_segment(1, 2)], [_segment(3, 3, "context_only")]]

    assert module.validate(parts, first=1, last=3) == []
    rendered = module.render_markdown(parts, "a" * 64)
    assert "Sequence candidates:** 1" in rendered
    assert "Context only, lines 3–3" in rendered


def test_gap_and_bad_anchor_are_reported():
    module = _load()
    parts = [[_segment(1, 2), _segment(4, 5)]]
    parts[0][1]["anchor_lines"] = [99]

    errors = module.validate(parts, first=1, last=5)

    assert any("expected start line 3" in error for error in errors)
    assert any("anchors outside declared interval" in error for error in errors)


def test_out_of_order_anchors_are_reported():
    module = _load()
    segment = _segment(1, 3)
    segment["anchor_lines"] = [3, 1]

    assert any(
        "anchors must be unique and chronological" in error
        for error in module.validate([[segment]], first=1, last=3)
    )
