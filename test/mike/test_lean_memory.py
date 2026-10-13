"""Mike: how much RAM does a model really need once the avoidable overhead is removed?

Each configuration runs alone in a spawned process, answers three requests
with prompt v4 (constrained), and reports its peak RSS, split into
anonymous memory (allocated) and file-backed memory (the memory-mapped model
file, which the kernel can drop and reload). The Python interpreter's own
footprint before loading is measured and reported separately.

    MIKE_ASSET_ROOT=/data/michael/tanstaafllm/mike-assets \
        uv run --group mike pytest test/mike/test_lean_memory.py -m integration -s
"""

from __future__ import annotations

import json
import multiprocessing
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

import mike_eval as ev

MODELS = ["LFM2.5-350M-Q4_K_M.gguf", "LFM2.5-230M-Q4_K_M.gguf"]
CONFIGS = {
    # as in Step 3: llama.cpp defaults, n_batch 64
    "default": {"repack": True, "n_batch": 64, "n_ctx": 2048},
    # no x86 repacked copy of the weights, small batch
    "lean": {"repack": False, "n_batch": 16, "n_ctx": 2048},
}
REQUESTS = ["ouvre la calculatrice", "mets le terminal en plein écran", "quel temps fera-t-il demain"]
RUN_DIR = ev.REPO / "results/mike/lean-memory" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _status() -> dict[str, int]:
    out = {}
    for line in Path("/proc/self/status").read_text().splitlines():
        key, _, value = line.partition(":")
        if key in ("VmHWM", "VmRSS", "RssAnon", "RssFile"):
            out[key] = int(value.split()[0])
    return out


def _child(model_path: str, config: dict, queue) -> None:
    try:
        import llama_cpp as lc
        from llama_cpp import Llama, LlamaGrammar

        import mike_bench as bench
        import mike_eval_model as em
        from mike_eval import contract

        before = _status()
        if not config["repack"]:
            default = lc.llama_cpp.llama_model_default_params

            def no_repack():
                params = default()
                params.use_extra_bufts = False
                return params

            lc.llama_cpp.llama_model_default_params = no_repack
            lc.llama.llama_cpp.llama_model_default_params = no_repack
        llm = Llama(model_path=model_path, n_ctx=config["n_ctx"], n_batch=config["n_batch"],
                    n_ubatch=config["n_batch"], n_threads=4, verbose=False)
        loaded = _status()
        template = llm.metadata["tokenizer.chat_template"]
        bos = llm.detokenize([llm.token_bos()], special=True).decode() if llm.token_bos() >= 0 else ""
        eos = llm.detokenize([llm.token_eos()], special=True).decode()
        fmt = bench.format_for(Path(model_path).name)
        grammar = LlamaGrammar.from_string(bench.grammar_for(fmt, contract.APP_IDS, contract.PLACES), verbose=False)
        desktop = contract.Desktop(("terminal", "calculator"), "calculator")
        bench.PROMPTS["v4"] = (em.system_v4(desktop), contract.TOOLS)
        answers = []
        for request in REQUESTS:
            prompt = bench.render_prompt(template, bos, eos, request, "v4") + fmt.opener
            tokens = llm.tokenize(prompt.encode(), add_bos=False, special=True)
            t0 = time.perf_counter()
            out = []
            for token in llm.generate(tokens, temp=0.0, top_k=1, repeat_penalty=1.0, grammar=grammar):
                out.append(token)
                text = llm.detokenize(out, special=True).decode(errors="replace")
                if len(out) >= 40 or text.endswith(fmt.closer[0]):
                    break
            answers.append({"request": request, "raw": text, "prompt_tokens": len(tokens),
                            "s": round(time.perf_counter() - t0, 2)})
        queue.put({"before": before, "loaded": loaded, "after": _status(), "answers": answers})
    except BaseException as error:  # report, never hang the parent
        queue.put({"error": repr(error)})


@pytest.mark.integration
@pytest.mark.timeout(900)
@pytest.mark.parametrize("config", CONFIGS)
@pytest.mark.parametrize("model", MODELS)
def test_lean_memory(model, config):
    pytest.importorskip("llama_cpp")
    root = os.environ.get("MIKE_ASSET_ROOT")
    if not root or not (Path(root) / model).is_file():
        pytest.skip(f"{model} not found under MIKE_ASSET_ROOT")
    context = multiprocessing.get_context("spawn")
    queue = context.Queue()
    process = context.Process(target=_child, args=(str(Path(root) / model), CONFIGS[config], queue))
    process.start()
    report = queue.get(timeout=850)
    process.join(30)
    assert "error" not in report, report.get("error")
    mib = lambda kib: round(kib / 1024, 1)  # noqa: E731
    after, before = report["after"], report["before"]
    summary = {
        "model": model, "config": config, **CONFIGS[config],
        "python_before_mib": mib(before["VmHWM"]),
        "peak_mib": mib(after["VmHWM"]),
        "peak_minus_python_mib": mib(after["VmHWM"] - before["VmHWM"]),
        "rss_anon_mib": mib(after["RssAnon"]), "rss_file_mib": mib(after["RssFile"]),
        "answers": [(a["request"], a["raw"], a["s"]) for a in report["answers"]],
    }
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    with (RUN_DIR / "summary.jsonl").open("a") as out:
        out.write(json.dumps(summary, ensure_ascii=False) + "\n")
    print(json.dumps(summary, ensure_ascii=False))
    assert summary["peak_mib"] > 0
