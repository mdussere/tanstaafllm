"""Mike Step 17: small-talk quality, assessed with nothing changed (`mike_assessment.feature`).

    uv run pytest test/mike/test_mike_assessment.py -m integration -s

Plays `assessment_scenarios.json` through Mike's own client code on Termidor
(`Conversation`, `answer`, `L0Frame`, `SYSTEM`, `SAMPLING`, `MAX_TOKENS`,
`KEEP_CTX`), for Mike's model only (the user, 2026-11-01, dropped the 1.2B and
Qwen3-4B references). Each scenario starts a new
conversation, as `/new` does. Runs: one greedy (temperature 0) and three with
the client's sampling and a fixed seed. Nothing is graded here; Professor
grades the transcripts.

The harness is the client's: nothing is adapted.
"""

from __future__ import annotations

import io
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[2] / "src" / "mike"))
import mike as st  # noqa: E402

import mike_eval as ev  # noqa: E402
import mike_server as ms  # noqa: E402
from test_mike_client import _port  # noqa: E402

ASSETS = Path(os.environ.get("MIKE_ASSET_ROOT", "/data/michael/tanstaafllm/mike-assets"))
MODELS = {"lfm2.5-350m": "LFM2.5-350M-Q4_0.gguf"}
SCENARIOS = json.loads((Path(__file__).with_name("assessment_scenarios.json")).read_text())["scenarios"]
RUNS = {"greedy": {"temperature": 0.0, "top_k": 1, "repeat_penalty": st.SAMPLING["repeat_penalty"], "seed": 0},
        **{f"seed{s}": {**st.SAMPLING, "seed": s} for s in (1, 2, 3)}}
THREADS = int(os.environ.get("MIKE_THREADS", "8"))  # desk speed only; it does not change the answers' quality
STAMP = os.environ.get("MIKE_ASSESS_STAMP", datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
RUN_DIR = ev.REPO / "results/mike/assessment" / STAMP


def transcript(model: str, scenario: str, lang: str, run: str, rows: list[dict]) -> str:
    out = [f"# {model} · {scenario} · {lang} · {run}\n",
           f"System prompt: {st.SYSTEM[lang]}  \nSampling: `{json.dumps(RUNS[run])}`\n"]
    for r in rows:
        out.append(f"**Q{r['turn'] + 1}:** {r['question']}\n\n**A:** {r['answer']}\n\n"
                   f"<sub>first token {r['first_s']} s · total {r['total_s']} s · read {r['prompt_n']}"
                   f" · wrote {r['predicted_n']} · stop {r['stop']}"
                   f"{' · ROLLED OVER after this turn' if r['rolled_over'] else ''}</sub>\n")
    return "\n".join(out)


@pytest.mark.integration
@pytest.mark.timeout(4 * 3600)
@pytest.mark.parametrize("model", list(MODELS))
def test_assessment(model, monkeypatch):
    path = ASSETS / MODELS[model]
    if not path.is_file():
        pytest.skip(f"{path} missing")
    out_dir = RUN_DIR / model
    out_dir.mkdir(parents=True, exist_ok=True)
    server = st.Server(_port(), str(ms.SERVER), str(path), out_dir / "slots", THREADS, out_dir / "llama-server.log")
    server.start(out_dir / "brain.lock")
    rows = []
    try:
        for run, sampling in RUNS.items():
            monkeypatch.setattr(st, "SAMPLING", sampling)
            for scenario, spec in SCENARIOS.items():
                for lang in ("fr", "en"):
                    conv = st.Conversation(server.tokenize, st.SYSTEM[lang], server.template())
                    frame = st.L0Frame(server, conv.l0)
                    frame.put_back()
                    mine = []
                    for t, q in enumerate(spec[lang]):
                        r = st.answer(server, conv, q, io.StringIO(), lang=lang)
                        if r["rolled_over"]:  # as the client does
                            frame.put_back()
                        mine.append(r | {"model": model, "file": path.name, "scenario": scenario, "lang": lang,
                                         "run": run, "turn": t})
                    (out_dir / f"{scenario}-{lang}-{run}.md").write_text(transcript(model, scenario, lang, run, mine))
                    rows += mine
                    with (out_dir / "turns.jsonl").open("a", encoding="utf-8") as f:
                        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in mine)
    finally:
        server.stop()
    expected = len(RUNS) * 2 * sum(len(s["fr"]) for s in SCENARIOS.values())
    assert len(rows) == expected and all(r["answer"] or r["stop"] for r in rows)
