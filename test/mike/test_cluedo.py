"""Mike 8.0: can the desk models solve a simple Cluedo scene? (`cluedo.feature`)

The scene (about 1,000 tokens, French and English) has one answer: Professor
Plum / le professeur Violet, with the rope / la corde, in the library / la
bibliothèque. Each model is asked through its own chat template
(`llama-server --jinja`, `/v1/chat/completions`), for a short answer and for
brief reasoning then the answer, with greedy and Liquid AI's recommended
sampling.

    uv run pytest test/mike/test_cluedo.py -m integration -s
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

import mike_eval as ev
import mike_server as ms

ASSETS = Path(os.environ.get("MIKE_ASSET_ROOT", "/data/michael/tanstaafllm/mike-assets"))
MODELS = os.environ.get("MIKE_MODELS", "LFM2.5-350M-Q4_K_M.gguf,LFM2.5-350M-Q4_0.gguf,"
                        "LFM2.5-350M-QAD-Q4_0.gguf,LFM2.5-230M-Q4_K_M.gguf").split(",")
HERE = Path(__file__).parent
LANG = {
    "fr": {"scene": (HERE / "cluedo_scene_fr.txt").read_text(),
           "system": "Tu es un détective attentif. Tu lis la scène et tu réponds à la question.",
           "short": "Question : qui est l'assassin, avec quelle arme, et dans quelle pièce ? "
                    "Réponds en une seule ligne : le nom de l'assassin, l'arme, la pièce.",
           "reason": "Question : qui est l'assassin, avec quelle arme, et dans quelle pièce ? "
                     "Raisonne brièvement (100 mots au plus), puis termine par une ligne "
                     "« Réponse : assassin, arme, pièce »."},
    "en": {"scene": (HERE / "cluedo_scene_en.txt").read_text(),
           "system": "You are a careful detective. You read the scene and answer the question.",
           "short": "Question: who is the murderer, with which weapon, and in which room? "
                    "Answer in one line: the murderer's name, the weapon, the room.",
           "reason": "Question: who is the murderer, with which weapon, and in which room? "
                     "Reason briefly (at most 100 words), then end with a line "
                     "\"Answer: murderer, weapon, room\"."},
}
SAMPLING = {"greedy": {"temperature": 0.0, "top_k": 1},
            "liquid": {"temperature": 0.1, "top_k": 50, "repeat_penalty": 1.05}}  # model card
MAX_TOKENS = {"short": 40, "reason": 220}
EXPECTED = {"who": r"violet|plum", "weapon": r"corde|rope|cord", "room": r"biblioth|library"}
RUN_DIR = ev.REPO / "results/mike/cluedo" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def score(text: str) -> dict[str, bool]:
    final = re.split(r"(?i)(r[ée]ponse|answer)\s*:", text)[-1]  # the last answer line, if any
    return {k: bool(re.search(p, final.lower())) for k, p in EXPECTED.items()}


@pytest.mark.integration
@pytest.mark.timeout(1800)
@pytest.mark.parametrize("model", MODELS)
def test_cluedo(model):
    path = ASSETS / model
    if not path.is_file() or not ms.SERVER.is_file():
        pytest.skip(f"{model} or llama-server missing")
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    with ms.Server(str(path), ["--jinja", "-c", "4096"], RUN_DIR / f"{model}.server.log") as server:
        for lang, text in LANG.items():
            for mode in ("short", "reason"):
                for sampling, params in SAMPLING.items():
                    reply = server.post("/v1/chat/completions", {
                        "messages": [{"role": "system", "content": text["system"]},
                                     {"role": "user", "content": text["scene"] + "\n" + text[mode]}],
                        "max_tokens": MAX_TOKENS[mode], "seed": 1, **params,
                        # Qwen3: no hidden thinking, so every model gets the same token budget.
                        "chat_template_kwargs": {"enable_thinking": False}}, timeout=600)
                    answer = reply["choices"][0]["message"].get("content") or ""
                    s = score(answer)
                    rows.append({"model": model, "lang": lang, "mode": mode, "sampling": sampling,
                                 "right": all(s.values()), **s, "answer": answer,
                                 "prompt_tokens": reply["usage"]["prompt_tokens"],
                                 "completion_tokens": reply["usage"]["completion_tokens"]})
                    print(json.dumps({k: rows[-1][k] for k in ("model", "lang", "mode", "sampling", "right",
                                                                 "who", "weapon", "room")}),
                          "|", answer.replace("\n", " ⏎ ")[:300], flush=True)
    with (RUN_DIR / "answers.jsonl").open("a") as out:
        for row in rows:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
    assert len(rows) == 8
