from pathlib import Path

from worklines.bill.scripts.validate_atom_trial import validate_markdown


def test_validator_accepts_a_traceable_bounded_atom(tmp_path: Path):
    result = tmp_path / "atoms.md"
    result.write_text(
        "# Luna atomization trial — example\n\n"
        "## Run\n"
        "- **Model:** example\n"
        "- **Started:** 2026-11-05T00:00:00Z\n"
        "- **Finished:** 2026-11-05T00:00:01Z\n"
        "- **Scope:** two source days\n\n"
        "## Atoms\n"
        "### Atom 1 — example\n"
        "- **Start:** line 1\n"
        "- **End:** line 2\n"
        "- **Source references:** line 1; line 2\n"
        "- **Sequence:** bounded example\n"
        "- **Uncertainty:** illustrative fixture\n",
        encoding="utf-8",
    )

    assert validate_markdown(result) == []


def test_validator_reports_missing_atom_trace_fields(tmp_path: Path):
    result = tmp_path / "atoms.md"
    result.write_text("# Luna atomization trial\n\n## Run\n\n## Atoms\n### Atom 1\n", encoding="utf-8")

    errors = validate_markdown(result)

    assert "missing run field: Model" in errors
    assert "atom 1 missing field: Source references" in errors
