"""Measure recorded Terra token usage and a standard API-price equivalent.

This reads local Codex session logs but prints only usage counters. It is not
an account invoice or a claim about ChatGPT subscription billing.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PRICES_PER_MILLION_USD = {
    "uncached_input": 1.00,
    "cached_input": 0.05,
    "cache_write_input": 1.25,
    "output": 5.00,
}
LONG_CONTEXT_THRESHOLD = 272_000


def measure_session(path: Path) -> dict:
    """Take the last cumulative token record, not the sum of snapshots."""
    model = None
    latest = None
    calls: list[int] = []
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            payload = row.get("payload")
            if not isinstance(payload, dict):
                continue
            if row.get("type") == "turn_context":
                model = payload.get("model")
            if payload.get("type") == "token_count" and payload.get("info"):
                latest = payload["info"]
                last_usage = latest.get("last_token_usage") or {}
                calls.append(last_usage.get("input_tokens", 0))
    if model != "gpt-6.1-terra" or not latest:
        raise ValueError(f"{path.name}: missing Terra model or token usage")
    if calls and max(calls) > LONG_CONTEXT_THRESHOLD:
        raise ValueError(f"{path.name}: long-context price adjustment required")
    usage = latest["total_token_usage"]
    return {
        "session_log": path.name,
        "model": model,
        "calls_with_usage": len(calls),
        "max_input_tokens_one_call": max(calls, default=0),
        "model_context_window": latest["model_context_window"],
        "input_tokens": usage["input_tokens"],
        "cached_input_tokens": usage["cached_input_tokens"],
        "cache_write_input_tokens": usage.get("cache_write_input_tokens", 0),
        "output_tokens": usage["output_tokens"],
        "reasoning_output_tokens_included": usage.get("reasoning_output_tokens", 0),
    }


def summarize(sessions: list[dict]) -> dict:
    keys = (
        "input_tokens",
        "cached_input_tokens",
        "cache_write_input_tokens",
        "output_tokens",
        "reasoning_output_tokens_included",
        "calls_with_usage",
    )
    totals = {key: sum(item[key] for item in sessions) for key in keys}
    uncached = (
        totals["input_tokens"]
        - totals["cached_input_tokens"]
        - totals["cache_write_input_tokens"]
    )
    if uncached < 0:
        raise ValueError("cached and write tokens exceed total input")
    totals["uncached_input_tokens"] = uncached
    prices = PRICES_PER_MILLION_USD
    usd = (
        uncached * prices["uncached_input"]
        + totals["cached_input_tokens"] * prices["cached_input"]
        + totals["cache_write_input_tokens"] * prices["cache_write_input"]
        + totals["output_tokens"] * prices["output"]
    ) / 1_000_000
    return {
        "model": "gpt-6.1-terra",
        "sessions": sessions,
        "totals": totals,
        "prices_per_million_usd": prices,
        "api_equivalent_usd": round(usd, 6),
        "pricing_basis": "Standard, short-context API prices; 2026-11-05",
        "pricing_source": "https://developers.openai.com/api/docs/models/gpt-6.1-terra",
        "usage_interpretation_source": (
            "https://developers.openai.com/api/docs/guides/agents-api/observability"
        ),
        "limitations": (
            "Local usage is best-effort; this is an API-price equivalent, "
            "not an account bill. Root-agent orchestration and other fees "
            "are excluded."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--session-log", action="append", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = summarize([measure_session(path) for path in args.session_log])
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Measured {len(result['sessions'])} Terra sessions, "
        f"{result['totals']['calls_with_usage']} calls with usage; "
        f"API-price equivalent ${result['api_equivalent_usd']:.6f}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
