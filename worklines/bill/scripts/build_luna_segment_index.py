"""Validate and render Terra's private first-pass Luna sequence index."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


KINDS = {"sequence", "context_only"}
STATES = {"completed", "blocked", "open", "continuation"}
REQUIRED = {
    "start_line",
    "end_line",
    "kind",
    "title",
    "summary",
    "state",
    "uncertainty",
    "anchor_lines",
}


def validate(parts: list[list[dict]], first: int = 1, last: int = 3714) -> list[str]:
    """Check the full source is partitioned once and every pointer is in range."""
    errors: list[str] = []
    expected = first
    for part_number, part in enumerate(parts, start=1):
        if not isinstance(part, list) or not part:
            errors.append(f"part {part_number}: missing segment list")
            continue
        for segment_number, item in enumerate(part, start=1):
            label = f"part {part_number} segment {segment_number}"
            if not isinstance(item, dict) or not REQUIRED.issubset(item):
                errors.append(f"{label}: missing required fields")
                continue
            start, end = item["start_line"], item["end_line"]
            if not isinstance(start, int) or not isinstance(end, int):
                errors.append(f"{label}: line bounds must be integers")
                continue
            if start != expected:
                errors.append(f"{label}: expected start line {expected}, got {start}")
            if end < start:
                errors.append(f"{label}: end precedes start")
            expected = end + 1
            if item["kind"] not in KINDS:
                errors.append(f"{label}: invalid kind")
            if item["state"] not in STATES:
                errors.append(f"{label}: invalid state")
            for key in ("title", "summary", "uncertainty"):
                if not isinstance(item[key], str) or not item[key].strip():
                    errors.append(f"{label}: empty {key}")
            anchors = item["anchor_lines"]
            if not isinstance(anchors, list) or any(
                not isinstance(line, int) or not start <= line <= end for line in anchors
            ):
                errors.append(f"{label}: anchors outside declared interval")
            elif anchors != sorted(set(anchors)):
                errors.append(f"{label}: anchors must be unique and chronological")
            if item["kind"] == "sequence" and not anchors:
                errors.append(f"{label}: sequence lacks anchor lines")
    if expected != last + 1:
        errors.append(f"coverage ends at line {expected - 1}, expected {last}")
    return errors


def render_markdown(parts: list[list[dict]], source_sha256: str) -> str:
    """Render the validated index without altering model claims."""
    sequence_count = sum(
        item["kind"] == "sequence" for part in parts for item in part
    )
    context_count = sum(
        item["kind"] == "context_only" for part in parts for item in part
    )
    lines = [
        "# Luna session — Terra first-pass sequence index",
        "",
        f"- **Source SHA-256:** `{source_sha256}`",
        "- **Source rows:** 3,714",
        "- **Model:** GPT-6.1 Terra",
        f"- **Sequence candidates:** {sequence_count}",
        f"- **Context-only spans:** {context_count}",
        "- **Status:** first-pass cut and summary; verbatim-backed atoms remain to be made",
        "- **Semantic review:** [review.md](review.md)",
        "- **Usage and cost:** [cost.json](cost.json)",
        "",
    ]
    number = 0
    for part_number, part in enumerate(parts, start=1):
        lines += [f"## Window {part_number}", ""]
        for item in part:
            start, end = item["start_line"], item["end_line"]
            if item["kind"] == "context_only":
                lines += [f"- Context only, lines {start}–{end}: {item['summary']}"]
                continue
            number += 1
            anchors = ", ".join(str(line) for line in item["anchor_lines"])
            lines += [
                f"### {number}. {item['title']}",
                "",
                f"- **Source:** lines {start}–{end}; anchors {anchors}",
                f"- **State:** {item['state']}",
                f"- **Summary:** {item['summary']}",
                f"- **Uncertainty:** {item['uncertainty']}",
                "",
            ]
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part", action="append", required=True, type=Path)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--output-md", required=True, type=Path)
    args = parser.parse_args()
    parts = [json.loads(path.read_text(encoding="utf-8")) for path in args.part]
    errors = validate(parts)
    if errors:
        for error in errors:
            print(error)
        return 1
    combined = [item for part in parts for item in part]
    args.output_json.write_text(
        json.dumps(combined, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    args.output_md.write_text(
        render_markdown(parts, args.source_sha256), encoding="utf-8"
    )
    print(
        f"Validated {len(combined)} spans covering lines 1–3714; "
        f"wrote {args.output_json} and {args.output_md}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
