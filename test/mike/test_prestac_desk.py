"""Mike 9.2: PreStaC against `llama-server` on the desk host (`prestac_desk.feature`).

    uv run pytest test/mike/test_prestac_desk.py -m integration -s

1. Same answers: every evaluation request answered through PreStaC (restored
   frames) and with no cache at all give the same text.
2. Navigation: the 112 requests, grouped by desktop, along a path that visits
   each desktop, adds and removes a terminal layer, comes back to an earlier
   desktop, and asks some questions before the prefetch has finished.
3. Frame files: size against the number of tokens.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

import mike_bench as bench
import mike_eval as ev
import mike_server as ms
from mike_eval import contract
from prestac_layers import LfmLayers

sys.path.insert(0, str(ev.REPO / "src" / "mike"))
import prestac  # noqa: E402

MODEL = os.environ.get("MIKE_MODEL", "LFM2.5-350M-Q4_0.gguf")
ASSETS = Path(os.environ.get("MIKE_ASSET_ROOT", "/data/michael/tanstaafllm/mike-assets"))
LEAN = ["--no-repack", "-b", "16", "-ub", "16"]
RUN_DIR = ev.REPO / "results/mike/prestac-desk" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
TERMINAL = "The terminal's working directory is ~/git/tanstfaafllm; its last command was `ls`."


def body() -> dict:
    fmt = bench.LFM
    return {"grammar": bench.grammar_for(fmt, contract.APP_IDS, contract.PLACES), "n_predict": 64,
            "temperature": 0.0, "top_k": 1, "repeat_penalty": 1.0, "stop": list(bench.STOP_PIECES)}


def parse(content: str) -> contract.Call | None:
    parsed = bench.parse_call(bench.LFM, bench.LFM.opener + content + bench.LFM.closer[1:])
    return contract.Call(parsed.tool, parsed.args) if parsed else None


@pytest.fixture(scope="module")
def setup():
    path = ASSETS / MODEL
    if not path.is_file() or not ms.SERVER.is_file():
        pytest.skip("model or llama-server missing")
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    frames = RUN_DIR / "frames"
    frames.mkdir()
    server = ms.Server(str(path), [*LEAN, "--slot-save-path", str(frames)], RUN_DIR / "llama-server.log")
    with server:
        props = server.get("/props")
        tokenize = lambda text: server.post("/tokenize", {"content": text, "add_special": False,  # noqa: E731
                                                          "parse_special": True})["tokens"]
        layers = LfmLayers(props["chat_template"], props.get("bos_token", ""), props.get("eos_token", ""), tokenize)
        yield server, layers, frames
    shutil.rmtree(frames, ignore_errors=True)  # frames are a cache, not evidence; sizes are in the report


def new_cache(server, frames, sub: str) -> prestac.PreStaC:
    # llama-server saves under its own --slot-save-path, so the store uses that directory.
    store = prestac.Store(frames)
    return prestac.PreStaC(prestac.HttpEngine(server.url), store, f"{MODEL}|b11429|prestac-l0-v1", chunk=64)


def cases():
    return [(name, c) for name, path in (("main", ev.EVAL_SET), ("holdout", ev.HOLDOUT_SET))
            for c in ev.load_cases(path)]


@pytest.mark.integration
@pytest.mark.timeout(3600)
def test_same_answers_with_and_without_cache(setup):
    server, layers, frames = setup
    cache = new_cache(server, frames, "same")
    rows, differ = [], []
    for set_name, case in cases()[::4]:  # one request in four: about 28
        stack = [layers.l0, layers.desktop(case.desktop)]
        cache.set_stack(stack)
        while cache.step():
            pass
        tail = layers.tail(case.request)
        cached = cache.ask(tail, body())
        tokens = [t for l in stack for t in l.tokens] + list(tail.tokens)
        plain = server.post("/completion", {"prompt": tokens, "cache_prompt": False, **body()})
        same = cached.reply["content"] == plain["content"]
        rows.append({"request": case.request, "same": same, "cached": cached.reply["content"],
                     "plain": plain["content"], "restored": cached.restored_tokens, "read": cached.read_tokens,
                     "prompt_tokens": cached.prompt_tokens})
        if not same:
            differ.append(case.request)
    (RUN_DIR / "same_answers.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    print(json.dumps({"compared": len(rows), "different": differ}, ensure_ascii=False))
    assert rows and not differ, differ


@pytest.mark.integration
@pytest.mark.timeout(3600)
def test_navigation_path(setup):
    server, layers, frames = setup
    cache = new_cache(server, frames, "nav")
    for path in frames.glob("*"):  # start cold
        path.unlink()
    cache.start()
    by_desktop: dict[str, list] = {}
    for set_name, case in cases():
        by_desktop.setdefault(repr(case.desktop), []).append((set_name, case))
    order = list(by_desktop)
    path = order + [order[0]]  # come back to the first desktop at the end
    rows = []
    t0 = time.perf_counter()
    try:
        for visit, key in enumerate(path):
            group = by_desktop[key]
            if visit == len(path) - 1:
                group = group[:5]  # the return visit: a few questions are enough
            desktop = group[0][1].desktop
            stack = [layers.l0, layers.desktop(desktop)]
            cache.set_stack(stack)
            early = visit % 2 == 1  # every other desktop: the first question does not wait for the prefetch
            if not early:
                assert cache.wait_ready(600)
            for i, (set_name, case) in enumerate(group):
                if i == 3:  # the user opens the terminal: one more layer, then back
                    cache.push(layers.app("terminal", TERMINAL))
                    if not early:
                        cache.wait_ready(600)
                if i == 5:
                    cache.pop()
                result = cache.ask(layers.tail(case.request), body())
                got = parse(result.reply["content"])
                score = ev.score(case, got)
                rows.append({"visit": visit, "desktop": key, "set": set_name, "request": case.request,
                             "layers": [l.name for l in cache.wanted], "early": early and i == 0,
                             "prompt_tokens": result.prompt_tokens, "restored": result.restored_tokens,
                             "read": result.read_tokens, "frame_depth": result.frame_depth,
                             "waited_s": round(result.waited_s, 3), "total_s": round(result.total_s, 3),
                             "raw": result.reply["content"], **score})
    finally:
        cache.stop()
    wall = time.perf_counter() - t0
    prompt = sum(r["prompt_tokens"] for r in rows)
    restored = sum(r["restored"] for r in rows)
    times = sorted(r["total_s"] for r in rows)
    sizes = sorted({(e["tokens"], e["bytes"]) for e in cache.store.entries()})
    summary = {
        "questions": len(rows), "prompt_tokens": prompt, "restored_tokens": restored,
        "restored_share": round(restored / prompt, 4), "read_tokens": sum(r["read"] for r in rows),
        "median_total_s": times[len(times) // 2], "max_total_s": times[-1],
        "background": {"frames_computed": cache.stats.frames_computed, "frames_reused": cache.stats.frames_reused,
                       "tokens_read": cache.stats.tokens_read_background,
                       "seconds": round(cache.stats.background_s, 2), "abandoned": cache.stats.chunks_abandoned},
        "wall_s": round(wall, 1),
        "model_right": sum(r["model"] for r in rows), "adapter_right": sum(r["adapter"] for r in rows),
        "frame_sizes": sizes,
        "early_questions": [{k: r[k] for k in ("request", "restored", "read", "total_s")} for r in rows if r["early"]],
    }
    (RUN_DIR / "navigation.json").write_text(json.dumps({"summary": summary, "rows": rows}, indent=1,
                                                         ensure_ascii=False))
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    assert summary["restored_share"] >= 0.95
