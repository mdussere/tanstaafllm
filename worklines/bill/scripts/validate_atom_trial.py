"""Validate the observable Markdown shape of a private atomization-trial result."""

from __future__ import annotations

import argparse
from pathlib import Path


RUN_FIELDS = ("Model", "Started", "Finished", "Scope")
ATOM_FIELDS = ("Start", "End", "Source references", "Sequence", "Uncertainty")


def validate_markdown(path: Path) -> list[str]:
    """Return human-readable shape errors; never print private atom content."""
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []

    if not text.startswith("# Luna atomization trial"):
        errors.append("missing trial title")
    if "## Run" not in text:
        errors.append("missing Run section")
    if "## Atoms" not in text:
        errors.append("missing Atoms section")

    for field in RUN_FIELDS:
        if f"- **{field}:**" not in text:
            errors.append(f"missing run field: {field}")

    atoms = [part for part in text.split("### Atom ")[1:] if part.strip()]
    if not atoms:
        errors.append("no atoms")
    for number, atom in enumerate(atoms, start=1):
        for field in ATOM_FIELDS:
            if f"- **{field}:**" not in atom:
                errors.append(f"atom {number} missing field: {field}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="private atoms.md result to validate")
    path = parser.parse_args().path
    errors = validate_markdown(path)
    if errors:
        print(f"INVALID: {path}")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"VALID: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
