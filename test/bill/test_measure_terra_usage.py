import importlib.util
import json
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "worklines"
    / "bill"
    / "scripts"
    / "measure_terra_usage.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("measure_terra_usage", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_last_cumulative_usage_and_cached_price(tmp_path: Path):
    source = tmp_path / "session.jsonl"
    rows = [
        {"type": "turn_context", "payload": {"model": "gpt-6.1-terra"}},
        {
            "type": "event_msg",
            "payload": {
                "type": "token_count",
                "info": {
                    "total_token_usage": {
                        "input_tokens": 100,
                        "cached_input_tokens": 0,
                        "output_tokens": 10,
                    },
                    "last_token_usage": {"input_tokens": 100},
                    "model_context_window": 475000,
                },
            },
        },
        {
            "type": "event_msg",
            "payload": {
                "type": "token_count",
                "info": {
                    "total_token_usage": {
                        "input_tokens": 1100,
                        "cached_input_tokens": 900,
                        "cache_write_input_tokens": 0,
                        "output_tokens": 30,
                        "reasoning_output_tokens": 5,
                    },
                    "last_token_usage": {"input_tokens": 1000},
                    "model_context_window": 475000,
                },
            },
        },
    ]
    source.write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )

    measured = _load().measure_session(source)
    result = _load().summarize([measured])

    assert measured["calls_with_usage"] == 2
    assert result["totals"]["input_tokens"] == 1100
    assert result["totals"]["uncached_input_tokens"] == 200
    assert result["api_equivalent_usd"] == round(
        (200 * 1 + 900 * 0.05 + 30 * 5) / 1_000_000, 6
    )
