"""Integration check for the private, complete Luna raw and derived snapshot."""

import hashlib
import importlib.util
import json
import os
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "worklines" / "bill" / "scripts" / "build_luna_segment_index.py"
SESSION_ID = "08421a9a-b5dc-435e-a293-8497430d722a"
EXPECTED_SHA256 = "9c07746899fd3bba398d103af91f511e67d362a7c2312ea87b3d698093461af9"


def _validator():
    spec = importlib.util.spec_from_file_location("build_luna_segment_index", VALIDATOR)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.integration
def test_private_full_session_snapshot_and_index():
    private_root = os.environ.get("BILL_PRIVATE_REPO")
    if not private_root:
        pytest.skip("Set BILL_PRIVATE_REPO to an accessible private clone")
    repo = Path(private_root)
    raw_dir = repo / "raw" / "claude-code" / "luna" / SESSION_ID
    derived_dir = repo / "derived" / "claude-code" / "luna" / SESSION_ID

    raw = (raw_dir / "session.jsonl").read_bytes()
    raw_manifest = json.loads((raw_dir / "manifest.json").read_text(encoding="utf-8"))
    derived_manifest = json.loads(
        (derived_dir / "manifest.json").read_text(encoding="utf-8")
    )
    parts = [
        json.loads((derived_dir / "segments" / f"part-{name}.json").read_text(encoding="utf-8"))
        for name in "abc"
    ]
    combined = json.loads((derived_dir / "segments.json").read_text(encoding="utf-8"))
    cost = json.loads((derived_dir / "cost.json").read_text(encoding="utf-8"))

    assert len(raw) == raw_manifest["bytes"] == 13_451_993
    assert len(raw.splitlines()) == raw_manifest["jsonl_records"] == 3714
    assert hashlib.sha256(raw).hexdigest() == raw_manifest["sha256"] == EXPECTED_SHA256
    assert derived_manifest["source_sha256"] == EXPECTED_SHA256
    assert _validator().validate(parts) == []
    assert combined == [item for part in parts for item in part]
    assert len(combined) == derived_manifest["index"]["source_spans"]
    assert sum(item["kind"] == "sequence" for item in combined) == 79
    assert (derived_dir / "index.md").exists()
    assert (derived_dir / "review.md").exists()
    assert cost["model"] == "gpt-6.1-terra"
    assert cost["totals"]["input_tokens"] >= cost["totals"]["cached_input_tokens"]
