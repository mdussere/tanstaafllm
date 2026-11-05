#!/usr/bin/env python3
"""Inspect Claude Code JSONL structure without emitting message content."""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import hashlib
import json
import re
from pathlib import Path
from typing import Any


SAFE_LABEL = re.compile(r"^[a-zA-Z0-9_.:/-]{1,80}$")
ID_FIELDS = ("uuid", "sessionId", "parentUuid", "id", "requestId")


def label(value: Any) -> str:
    """Return enum-like metadata while preventing text from entering a report."""
    if isinstance(value, str) and SAFE_LABEL.fullmatch(value):
        return value
    if value is None:
        return "<missing>"
    return "<non-enum>"


def iso_day(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return None


def increment(counter: collections.Counter[str], value: Any) -> None:
    counter[label(value)] += 1


def inspect_jsonl(source: Path) -> dict[str, Any]:
    """Return a content-redacted structural summary of a JSONL file."""
    top_level_keys: collections.Counter[str] = collections.Counter()
    record_types: collections.Counter[str] = collections.Counter()
    keys_by_record_type: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    message_roles: collections.Counter[str] = collections.Counter()
    keys_by_message_role: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    content_item_types: collections.Counter[str] = collections.Counter()
    keys_by_content_item_type: dict[str, collections.Counter[str]] = collections.defaultdict(collections.Counter)
    id_presence: collections.Counter[str] = collections.Counter()
    marker_counts: collections.Counter[str] = collections.Counter()
    day_counts: collections.Counter[str] = collections.Counter()
    role_transitions: collections.Counter[str] = collections.Counter()
    root_kinds: collections.Counter[str] = collections.Counter()
    malformed_lines = 0
    blank_lines = 0
    total_lines = 0
    previous_role: str | None = None

    digest = hashlib.sha256()
    with source.open("rb") as binary_file:
        for raw_line in binary_file:
            digest.update(raw_line)
            total_lines += 1
            if not raw_line.strip():
                blank_lines += 1
                continue
            try:
                record = json.loads(raw_line)
            except (UnicodeDecodeError, json.JSONDecodeError):
                malformed_lines += 1
                continue

            if not isinstance(record, dict):
                root_kinds[type(record).__name__] += 1
                continue

            root_kinds["object"] += 1
            top_level_keys.update(record.keys())
            record_type = label(record.get("type"))
            record_types[record_type] += 1
            keys_by_record_type[record_type].update(record.keys())
            for field in ID_FIELDS:
                if field in record:
                    id_presence[field] += 1
            if record.get("isCompactSummary") is True:
                marker_counts["isCompactSummary"] += 1
            if "compactMetadata" in record:
                marker_counts["compactMetadata"] += 1
            if record.get("isSidechain") is True:
                marker_counts["isSidechain"] += 1
            if record.get("isVisibleInTranscriptOnly") is True:
                marker_counts["isVisibleInTranscriptOnly"] += 1

            day = iso_day(record.get("timestamp"))
            if day:
                day_counts[day] += 1

            message = record.get("message")
            if isinstance(message, dict):
                role = label(message.get("role"))
                message_roles[role] += 1
                keys_by_message_role[role].update(message.keys())
                if previous_role is not None:
                    role_transitions[f"{previous_role}→{role}"] += 1
                previous_role = role

                content = message.get("content")
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict):
                            item_type = label(item.get("type"))
                            content_item_types[item_type] += 1
                            keys_by_content_item_type[item_type].update(item.keys())

    natural_boundaries: list[str] = ["The JSONL file itself is an immutable session boundary."]
    if day_counts:
        natural_boundaries.append("ISO calendar-day boundaries are present in root `timestamp` values.")
    if message_roles.get("user") and message_roles.get("assistant"):
        natural_boundaries.append(
            "`message.role` user→assistant transitions are candidate request/response boundaries."
        )
    if id_presence.get("uuid") and id_presence.get("parentUuid"):
        natural_boundaries.append("`uuid`/`parentUuid` links are candidate causal-turn boundaries.")
    if content_item_types.get("tool_use") or content_item_types.get("tool_result"):
        natural_boundaries.append("Tool-use/result items are candidate sub-boundaries within an assistant turn.")
    if marker_counts.get("isCompactSummary") or marker_counts.get("compactMetadata"):
        natural_boundaries.append("Summary or compaction record types are explicit candidate archive boundaries.")

    return {
        "privacy": {
            "message_content_emitted": False,
            "only_safe_enum_labels_emitted": True,
        },
        "source": {
            "path": str(source),
            "bytes": source.stat().st_size,
            "sha256": digest.hexdigest(),
        },
        "lines": {
            "total": total_lines,
            "blank": blank_lines,
            "malformed": malformed_lines,
            "root_kinds": dict(sorted(root_kinds.items())),
        },
        "structure": {
            "top_level_key_counts": dict(sorted(top_level_keys.items())),
            "record_type_counts": dict(sorted(record_types.items())),
            "top_level_keys_by_record_type": {
                record_type: dict(sorted(keys.items()))
                for record_type, keys in sorted(keys_by_record_type.items())
            },
            "message_role_counts": dict(sorted(message_roles.items())),
            "message_keys_by_role": {
                role: dict(sorted(keys.items())) for role, keys in sorted(keys_by_message_role.items())
            },
            "content_item_type_counts": dict(sorted(content_item_types.items())),
            "content_item_keys_by_type": {
                item_type: dict(sorted(keys.items()))
                for item_type, keys in sorted(keys_by_content_item_type.items())
            },
            "identifier_field_presence": dict(sorted(id_presence.items())),
            "explicit_marker_counts": dict(sorted(marker_counts.items())),
        },
        "time": {"records_by_iso_day": dict(sorted(day_counts.items()))},
        "turns": {"role_transition_counts": dict(sorted(role_transitions.items()))},
        "candidate_natural_boundaries": natural_boundaries,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Claude Code JSONL session to inspect")
    parser.add_argument("--output", type=Path, required=True, help="Redacted JSON report path")
    args = parser.parse_args()

    report = inspect_jsonl(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
