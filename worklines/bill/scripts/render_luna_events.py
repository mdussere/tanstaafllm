"""Render a bounded, line-numbered reading view of a private Claude JSONL.

The view is lossy and may contain private message/tool text. Keep it alongside
private working material, never in this public repository.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _compact(value: object) -> str:
    if not isinstance(value, str):
        value = json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return " ".join(value.split())


def _content(message: object) -> str:
    if not isinstance(message, dict):
        return ""
    blocks = message.get("content")
    if isinstance(blocks, str):
        return _compact(blocks)
    if not isinstance(blocks, list):
        return ""
    parts: list[str] = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        kind = block.get("type", "?")
        if kind == "text":
            parts.append(f"text={_compact(block.get('text', ''))}")
        elif kind == "tool_use":
            parts.append(
                f"tool_use={_compact(block.get('name', '?'))} "
                f"input={_compact(block.get('input', ''))}"
            )
        elif kind == "tool_result":
            parts.append(f"tool_result={_compact(block.get('content', ''))}")
        elif kind == "image":
            parts.append("[image block; inspect raw source]")
        elif kind == "thinking":
            parts.append("[thinking block omitted from reading view]")
        else:
            parts.append(f"[{kind} block; inspect raw source]")
    return " | ".join(parts)


def render_range(source: Path, start: int, end: int, max_chars: int = 1200) -> str:
    """Return one indexed line per source row, retaining absolute line numbers."""
    if start < 1 or end < start or max_chars < 40:
        raise ValueError("invalid line range or preview limit")
    rendered: list[str] = []
    with source.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, start=1):
            if number > end:
                break
            if number < start:
                continue
            row = json.loads(line)
            message = row.get("message")
            role = message.get("role", "-") if isinstance(message, dict) else "-"
            preview = _content(message)
            if len(preview) > max_chars:
                preview = f"{preview[:max_chars]} [truncated; inspect raw line {number}]"
            rendered.append(
                f"L{number:04d} {row.get('timestamp', '-')} "
                f"{row.get('type', '?')}/{role}: {preview}"
            )
    if len(rendered) != end - start + 1:
        raise ValueError("requested range extends beyond source")
    return "\n".join(rendered) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--start", required=True, type=int)
    parser.add_argument("--end", required=True, type=int)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--max-chars", type=int, default=1200)
    args = parser.parse_args()
    result = render_range(args.source, args.start, args.end, args.max_chars)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result, encoding="utf-8")
    print(f"Rendered {args.end - args.start + 1} source rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
