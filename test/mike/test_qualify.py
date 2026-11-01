"""Mike Step 10: qualify a model, 90 % stable on the evaluation cases (`qualify.feature`).

    uv run pytest test/mike/test_qualify.py -m integration -s -k "<model>"

Every case of the main (81) and held-out (31) sets is asked 11 times on one
`llama-server`: greedy twice (the determinism check), then 9 sampled answers
(temperature 0.5, top-p 0.95, seeds 1–9). A case is *stable-right* when at
least 9 of its 10 answers (the first greedy one and the 9 sampled ones) are
right after the adapter. A model is *qualified* when at least 90 % of the
cases are stable-right on each set.

Two prompt formats, both with prompt v4's instructions, examples and desktop line:

- ``plain`` (every model): the tool list as JSON text at the end of the system
  turn, rendered by the model's own chat template without its tool support;
  the answer is constrained to the examples' form ``name(arg="…")``;
- ``native`` (LFM models): prompt v4 exactly as in 3b, the template's own
  tool list and LFM's tool-call tokens.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

import mike_bench as bench
import mike_eval as ev
import mike_eval_model as em
import mike_server as ms
from mike_eval import contract

ASSETS = Path(os.environ.get("MIKE_ASSET_ROOT", "/data/michael/tanstaafllm/mike-assets"))
BITNET_SERVER = ms.TOOLS_ROOT / "bitnet/src/build/bin/llama-server-bitnet"  # renamed: not llama.cpp's release
RUN_DIR = ev.REPO / "results/mike/qualify" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
SAMPLES = 9
GATE = 0.90  # share of stable-right cases needed on each set
STABLE = 9  # right answers out of 10 for a case to be stable-right
LIMIT = int(os.environ.get("MIKE_QUALIFY_LIMIT", "0"))  # smoke runs only: cases per set

# The chat template in BitNet's GGUF drops the system turn; this is the one in the model's
# tokenizer_config.json (microsoft/bitnet-b1.58-2B-4T), with the BOS the tokenizer adds.
TEMPLATES = {
    "bitnet-b1.58-2B-4T-i2_s.gguf": (
        "{{ bos_token }}{% for message in messages %}{{ message['role'] | capitalize + ': ' + message['content'] "
        "| trim + '<|eot_id|>' }}{% endfor %}{% if add_generation_prompt %}{{ 'Assistant: ' }}{% endif %}"),
}

# BitNet's GGUF has no pre-tokenizer type, so the server would fall back to a default one
# that splits text unlike the model's Llama 3 tokenizer (`_app` becomes `_` `app`).
EXTRA_ARGS = {"bitnet-b1.58-2B-4T-i2_s.gguf": ["--override-kv", "tokenizer.ggml.pre=str:llama-bpe"]}

# (GGUF file, formats, server binary)
MODELS = [
    ("LFM2.5-350M-Q4_0.gguf", ("native", "plain"), ms.SERVER),
    ("LFM2.5-230M-Q4_K_M.gguf", ("native", "plain"), ms.SERVER),
    ("Qwen3-0.6B-Q4_K_M.gguf", ("plain",), ms.SERVER),
    ("LFM2-700M-Q4_K_M.gguf", ("native", "plain"), ms.SERVER),
    ("gemma-3-1b-it-Q4_K_M.gguf", ("plain",), ms.SERVER),
    ("LFM2.5-1.2B-Instruct-Q4_K_M.gguf", ("native", "plain"), ms.SERVER),
    ("Qwen3-1.7B-Q4_K_M.gguf", ("plain",), ms.SERVER),
    ("bitnet-b1.58-2B-4T-i2_s.gguf", ("plain",), BITNET_SERVER),
    ("Qwen3-4B-Q4_K_M.gguf", ("plain",), ms.SERVER),
    ("gemma-3-4b-it-Q4_K_M.gguf", ("plain",), ms.SERVER),
]


def plain_grammar() -> str:
    """The contract grammar without LFM's closing bracket: ``name(arg="…")``."""
    return bench.grammar_for(bench.LFM, contract.APP_IDS, contract.PLACES).replace('")]"', '")"')


def render(template: str, bos: str, eos: str, case: ev.EvalCase, fmt: str) -> str:
    if fmt == "native":
        bench.PROMPTS["v4"] = (em.system_v4(case.desktop), contract.TOOLS)
        return bench.render_prompt(template, bos, eos, case.request, "v4") + bench.LFM.opener
    system = em.system_v4(case.desktop) + "\nList of tools: " + json.dumps(contract.TOOLS, ensure_ascii=False)
    messages = [{"role": "system", "content": system}, {"role": "user", "content": case.request}]
    return bench._template_env().from_string(template).render(
        messages=messages, add_generation_prompt=True, enable_thinking=False,
        bos_token=bos, eos_token=eos)


def parse(fmt: str, content: str) -> contract.Call | None:
    text = bench.LFM.opener + content + "]" if fmt == "native" else "[" + content + "]"
    parsed = bench.parse_lfm(text)
    return contract.Call(parsed.tool, parsed.args) if parsed else None


def answers(server: ms.Server, tokens: list[int], grammar: str) -> list[dict]:
    common = {"prompt": tokens, "grammar": grammar, "n_predict": 64, "cache_prompt": True,
              "repeat_penalty": 1.0, "stop": [*bench.STOP_PIECES, "<|eot_id|>"]}
    greedy = {"temperature": 0.0, "top_k": 1}
    out = [server.post("/completion", {**common, **greedy}, timeout=900) for _ in range(2)]
    for seed in range(1, SAMPLES + 1):
        out.append(server.post("/completion", {**common, "temperature": 0.5, "top_p": 0.95, "top_k": 0,
                                               "min_p": 0.0, "seed": seed}, timeout=900))
    return out


def qualify(model: str, fmt: str, binary: Path) -> dict:
    path = ASSETS / model
    run_dir = RUN_DIR / f"{model}.{fmt}"
    run_dir.mkdir(parents=True, exist_ok=True)
    grammar = (bench.grammar_for(bench.LFM, contract.APP_IDS, contract.PLACES) if fmt == "native"
               else plain_grammar())
    report: dict = {"model": model, "format": fmt, "binary": str(binary), "samples": SAMPLES,
                    "sampling": {"temperature": 0.5, "top_p": 0.95}, "sets": {}}
    server = ms.Server(str(path), EXTRA_ARGS.get(model, []), run_dir / "llama-server.log", binary=binary)
    with server:
        props = server.get("/props")
        template = TEMPLATES.get(model, props["chat_template"])
        bos, eos = props.get("bos_token", ""), props.get("eos_token", "")
        report["ready_s"] = round(server.ready_s, 2)
        rows_out = (run_dir / "rows.jsonl").open("w")
        for set_name, set_path in (("main", ev.EVAL_SET), ("holdout", ev.HOLDOUT_SET)):
            rows = []
            cases = ev.load_cases(set_path)
            for case in cases[:LIMIT] if LIMIT else cases:
                text = render(template, bos, eos, case, fmt)
                tokens = server.post("/tokenize", {"content": text, "add_special": False,
                                                   "parse_special": True})["tokens"]
                assert len(tokens) < 2048 - 80, (model, len(tokens))
                replies = answers(server, tokens, grammar)
                raws = [r["content"] for r in replies]
                scores = [ev.score(case, parse(fmt, raw)) for raw in raws]
                right = [s["adapter"] for s in scores]
                counted = [right[0], *right[2:]]  # greedy once, then the samples
                row = {"set": set_name, "request": case.request, "tag": case.tag,
                       "expected": {"tool": case.expected.tool, "args": case.expected.args},
                       "prompt_tokens": len(tokens), "raw": raws,
                       "model_right": [s["model"] for s in scores], "adapter_right": right,
                       "deterministic": raws[0] == raws[1], "right_of_10": sum(counted),
                       "stable_right": sum(counted) >= STABLE,
                       "prompt_ms": replies[0].get("timings", {}).get("prompt_ms"),
                       "predicted_per_s": replies[0].get("timings", {}).get("predicted_per_second")}
                rows.append(row)
                rows_out.write(json.dumps(row, ensure_ascii=False) + "\n")
                rows_out.flush()
            n = len(rows)
            report["sets"][set_name] = {
                "n": n,
                "stable_right": sum(r["stable_right"] for r in rows),
                "stable_share": round(sum(r["stable_right"] for r in rows) / n, 3),
                "greedy_right": sum(r["adapter_right"][0] for r in rows),
                "greedy_model_right": sum(r["model_right"][0] for r in rows),
                "mean_right": round(sum(r["right_of_10"] for r in rows) / (10 * n), 3),
                "never_right": sum(r["right_of_10"] == 0 for r in rows),
                "not_deterministic": [r["request"] for r in rows if not r["deterministic"]],
                "prompt_tokens_median": sorted(r["prompt_tokens"] for r in rows)[n // 2],
            }
        rows_out.close()
        report["status_end_kib"] = server.status()
    report["qualified"] = all(s["stable_share"] >= GATE for s in report["sets"].values())
    (run_dir / "report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False))
    with (RUN_DIR / "summary.jsonl").open("a") as f:
        f.write(json.dumps({k: report[k] for k in ("model", "format", "qualified")} |
                           {s: {k: v[k] for k in ("stable_right", "n", "greedy_right", "mean_right")}
                            for s, v in report["sets"].items()}, ensure_ascii=False) + "\n")
    return report


def test_plain_grammar_closes_without_bracket():
    grammar = plain_grammar()
    assert '")]"' not in grammar and '"list_windows(" ")"' in grammar.replace("  ", " ")


def test_plain_answer_parses():
    assert parse("plain", 'launch_app(app="calculator")') == contract.Call("launch_app", {"app": "calculator"})
    assert parse("native", 'list_windows()]') == contract.Call("list_windows", {})


@pytest.mark.integration
@pytest.mark.timeout(6 * 3600)
@pytest.mark.parametrize("model,fmt,binary", [(m, f, b) for m, fmts, b in MODELS for f in fmts],
                         ids=[f"{m}-{f}" for m, fmts, _ in MODELS for f in fmts])
def test_qualify(model, fmt, binary):
    if not (ASSETS / model).is_file() or not binary.is_file():
        pytest.skip("model or server missing")
    report = qualify(model, fmt, binary)
    print(json.dumps({k: report[k] for k in ("model", "format", "qualified", "sets")}, ensure_ascii=False))
    # A measurement, not a pass/fail on the model: the gate's verdict is in the report.
    if not LIMIT:
        assert report["sets"]["main"]["n"] == 81 and report["sets"]["holdout"]["n"] == 31
