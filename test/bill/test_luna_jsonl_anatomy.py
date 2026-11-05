import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "worklines" / "bill" / "scripts" / "inspect_luna_jsonl.py"


def load_module():
    spec = importlib.util.spec_from_file_location("inspect_luna_jsonl", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_structural_report_redacts_message_content(tmp_path):
    source = tmp_path / "luna.jsonl"
    source.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "type": "user",
                        "timestamp": "2026-11-01T09:00:00Z",
                        "uuid": "u1",
                        "message": {"role": "user", "content": "SECRET LUNA MESSAGE"},
                    }
                ),
                json.dumps(
                    {
                        "type": "assistant",
                        "timestamp": "2026-11-01T09:00:02Z",
                        "uuid": "a1",
                        "parentUuid": "u1",
                        "isCompactSummary": True,
                        "message": {
                            "role": "assistant",
                            "content": [{"type": "tool_use", "input": "SECRET TOOL INPUT"}],
                        },
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    report = load_module().inspect_jsonl(source)
    rendered = json.dumps(report)

    assert report["source"]["bytes"] == source.stat().st_size
    assert report["lines"]["total"] == 2
    assert report["structure"]["message_role_counts"] == {"assistant": 1, "user": 1}
    assert report["structure"]["content_item_type_counts"] == {"tool_use": 1}
    assert report["structure"]["explicit_marker_counts"] == {"isCompactSummary": 1}
    assert report["time"]["records_by_iso_day"] == {"2026-11-01": 2}
    assert "SECRET" not in rendered
    assert any("user→assistant" in item for item in report["candidate_natural_boundaries"])
