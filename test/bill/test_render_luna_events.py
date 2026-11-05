import importlib.util
import json
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "worklines"
    / "bill"
    / "scripts"
    / "render_luna_events.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("render_luna_events", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_render_range_keeps_absolute_lines_and_marks_omissions(tmp_path: Path):
    source = tmp_path / "session.jsonl"
    rows = [
        {"type": "mode"},
        {
            "type": "assistant",
            "timestamp": "2026-10-03T10:00:00Z",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "thinking", "thinking": "PRIVATE REASONING"},
                    {"type": "text", "text": "Observed result"},
                    {"type": "tool_use", "name": "Read", "input": {"path": "file.txt"}},
                ],
            },
        },
        {"type": "attachment"},
    ]
    source.write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )

    view = _load().render_range(source, 2, 3)

    assert view.startswith("L0002 2026-10-03T10:00:00Z assistant/assistant:")
    assert "Observed result" in view
    assert "tool_use=Read" in view
    assert "L0003 - attachment/-:" in view
    assert "PRIVATE REASONING" not in view
    assert "[thinking block omitted" in view


def test_render_range_rejects_missing_rows(tmp_path: Path):
    source = tmp_path / "session.jsonl"
    source.write_text('{"type":"user"}\n', encoding="utf-8")

    try:
        _load().render_range(source, 1, 2)
    except ValueError as exc:
        assert "beyond source" in str(exc)
    else:
        raise AssertionError("expected missing-row error")
