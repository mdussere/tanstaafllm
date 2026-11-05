"""Integration check for the private Luna reading layout and source coverage."""

import hashlib
import os
import re
from pathlib import Path

import pytest


EXPECTED_SHA256 = "9c07746899fd3bba398d103af91f511e67d362a7c2312ea87b3d698093461af9"
RAW_NAME = "luna-claude-code-2026-10-03_2026-11-01.jsonl"
CONTEXT_ONLY = [(1797, 1823), (2509, 2510), (2598, 2627), (3010, 3102)]
ATOM_NAME = re.compile(r"(\d{4}-\d{2}-\d{2})_(\d{3})_([a-z0-9]+(?:-[a-z0-9]+)*)\.md")
SOURCE_SPAN = re.compile(r"source lines (\d+)–(\d+)")


@pytest.mark.integration
def test_private_luna_reading_layout():
    private_root = os.environ.get("BILL_PRIVATE_REPO")
    if not private_root:
        pytest.skip("Set BILL_PRIVATE_REPO to an accessible private clone")
    repo = Path(private_root)
    luna = repo / "Luna"
    assert {p.name for p in repo.iterdir() if p.name != ".git"} == {"README.md", "Luna"}
    assert {p.name for p in luna.iterdir()} == {"raw", "refined"}

    raw_dir = luna / "raw"
    assert [p.name for p in raw_dir.iterdir()] == [RAW_NAME]
    raw = (raw_dir / RAW_NAME).read_bytes()
    assert len(raw) == 13_451_993
    assert len(raw.splitlines()) == 3714
    assert hashlib.sha256(raw).hexdigest() == EXPECTED_SHA256

    atom_paths = sorted((luna / "refined").iterdir())
    assert len(atom_paths) == 79
    spans = list(CONTEXT_ONLY)
    previous_day = ""
    for number, path in enumerate(atom_paths, 1):
        assert path.is_file()
        match = ATOM_NAME.fullmatch(path.name)
        assert match is not None, path.name
        day, ordinal, _slug = match.groups()
        assert day >= previous_day
        assert int(ordinal) == number
        previous_day = day
        body = path.read_text(encoding="utf-8")
        assert f"../raw/{RAW_NAME}" in body
        assert EXPECTED_SHA256 in body
        assert "**Maturity:** provisional cut; verbatim pending" in body
        assert all(
            f"## {section}" in body
            for section in ("Essence", "Observed state", "Evidence and bounds", "Uncertainty", "Verbatim")
        )
        source = SOURCE_SPAN.search(body)
        assert source is not None, path.name
        start, end = map(int, source.groups())
        assert 1 <= start <= end <= 3714
        spans.append((start, end))

    spans.sort()
    assert spans[0][0] == 1 and spans[-1][1] == 3714
    assert all(right[0] == left[1] + 1 for left, right in zip(spans, spans[1:]))
