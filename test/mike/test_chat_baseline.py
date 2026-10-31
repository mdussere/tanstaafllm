"""Mike Step 12.1: small talk with LFM2.5-350M raw (`chat_baseline.feature`).

    uv run pytest test/mike/test_chat_baseline.py -m integration -s

Short conversations, French and English, on subjects surely in the model's
training corpus, through `llama-server`'s chat endpoint with the whole
history sent each turn (as any chat client does). Nothing is scored: the
answers go to `answers.md` for the user to read. What is measured is how many
prompt tokens the server really reads per turn (`timings.prompt_n`), how many
it writes, and what that would cost on Luna at its measured speeds. Two
settings: `lean`, and `lean-ckpt`, which lets the hybrid LFM2 model reuse the
conversation already read (`mike_server.CONFIGS`).
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

import mike_eval as ev
import mike_server as ms

ASSETS = Path(os.environ.get("MIKE_ASSET_ROOT", "/data/michael/tanstaafllm/mike-assets"))
MODEL = ASSETS / "LFM2.5-350M-Q4_0.gguf"
RUN_DIR = ev.REPO / "results/mike/chat-baseline" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
LUNA_READ, LUNA_WRITE = 6.5, 3.6  # tokens/s, docs/0405_01 and 0801_01
SAMPLING = {"temperature": 0.1, "top_k": 50, "repeat_penalty": 1.05, "seed": 0}  # model card
MAX_TOKENS = 120

SYSTEM = {
    "fr": "Tu es Mike, un petit assistant qui bavarde. Réponds en français, en deux ou trois phrases courtes.",
    "en": "You are Mike, a small assistant for casual chat. Answer in English, in two or three short sentences.",
}

CONVERSATIONS = [
    ("fr", ["Bonjour Mike, comment vas-tu ?",
            "Qu'est-ce que la photosynthèse ?",
            "Et pourquoi les feuilles changent-elles de couleur en automne ?"]),
    ("fr", ["Qui était Marie Curie ?",
            "Qu'a-t-elle découvert ?",
            "Merci, une dernière chose : elle a eu combien de prix Nobel ?"]),
    ("en", ["Who wrote The Moon Is a Harsh Mistress?",
            "What is the book about?",
            "Who is Mike in that book?"]),
    ("en", ["Tell me about the Apollo 11 mission.",
            "Who stayed in orbit?",
            "How long did they stay on the Moon?"]),
    ("fr", ["Explique-moi ce qu'est un Raspberry Pi.",
            "Et Linux, c'est quoi ?"]),
    ("en", ["What is the capital of Australia?",
            "Why not Sydney?"]),
]


def luna_estimate(prompt_n: int, predicted_n: int) -> dict[str, float]:
    """Luna's time to the first and the last word, from token counts alone (not measured)."""
    first = prompt_n / LUNA_READ + 1 / LUNA_WRITE
    return {"luna_first_s": round(first, 1), "luna_last_s": round(first + max(0, predicted_n - 1) / LUNA_WRITE, 1)}


def test_luna_estimate():
    assert luna_estimate(13, 37) == {"luna_first_s": 2.3, "luna_last_s": 12.3}


@pytest.mark.integration
@pytest.mark.timeout(3600)
@pytest.mark.parametrize("config", ["lean", "lean-ckpt"])
def test_chat_baseline(config):
    if not MODEL.is_file():
        pytest.skip("model missing")
    out = RUN_DIR / config
    out.mkdir(parents=True, exist_ok=True)
    turns = []
    with ms.Server(str(MODEL), ms.CONFIGS[config], out / "llama-server.log") as server, \
            (out / "turns.jsonl").open("w") as f:
        for c, (lang, questions) in enumerate(CONVERSATIONS):
            messages = [{"role": "system", "content": SYSTEM[lang]}]
            for t, question in enumerate(questions):
                messages.append({"role": "user", "content": question})
                started = time.perf_counter()
                reply = server.post("/v1/chat/completions", {
                    "messages": messages, "max_tokens": MAX_TOKENS, "cache_prompt": True, **SAMPLING}, timeout=600)
                wall = time.perf_counter() - started
                answer = reply["choices"][0]["message"]["content"].strip()
                messages.append({"role": "assistant", "content": answer})
                tm = reply["timings"]
                row = {"conversation": c, "turn": t, "lang": lang, "question": question, "answer": answer,
                       "finish": reply["choices"][0]["finish_reason"],
                       "prompt_tokens": reply["usage"]["prompt_tokens"], "prompt_n": tm["prompt_n"],
                       "cached": reply["usage"]["prompt_tokens"] - tm["prompt_n"],
                       "predicted_n": tm["predicted_n"], "prompt_ms": round(tm["prompt_ms"]),
                       "predicted_ms": round(tm["predicted_ms"]), "wall_s": round(wall, 2),
                       **luna_estimate(tm["prompt_n"], tm["predicted_n"])}
                turns.append(row)
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                f.flush()
        rss = server.status()

    def median(xs):
        xs = sorted(xs)
        return xs[len(xs) // 2] if xs else None

    first, follow = [r for r in turns if r["turn"] == 0], [r for r in turns if r["turn"] > 0]
    result = {"config": config, "model": MODEL.name, "turns": len(turns), "max_tokens": MAX_TOKENS,
              "sampling": SAMPLING, "rss_kib": rss,
              "first_turn": {"prompt_n_median": median([r["prompt_n"] for r in first])},
              "follow_up": {"prompt_tokens_median": median([r["prompt_tokens"] for r in follow]),
                            "prompt_n_median": median([r["prompt_n"] for r in follow])},
              "predicted_n_median": median([r["predicted_n"] for r in turns]),
              "cut_by_max_tokens": sum(r["finish"] == "length" for r in turns),
              "luna_first_s_median": median([r["luna_first_s"] for r in turns]),
              "luna_last_s_median": median([r["luna_last_s"] for r in turns]),
              "luna_last_s_max": max(r["luna_last_s"] for r in turns)}
    (out / "result.json").write_text(json.dumps(result, indent=1))
    lines = [f"# Chat baseline, {config}\n"]
    for r in turns:
        if r["turn"] == 0:
            lines.append(f"\n## Conversation {r['conversation'] + 1} ({r['lang']})\n")
        lines.append(f"\n**Q:** {r['question']}\n\n**A:** {r['answer']}\n\n"
                     f"<sub>read {r['prompt_n']} of {r['prompt_tokens']} tokens, wrote {r['predicted_n']}; "
                     f"Luna estimate: first word {r['luna_first_s']} s, last {r['luna_last_s']} s</sub>\n")
    (out / "answers.md").write_text("".join(lines))
    print(json.dumps(result))
    assert len(turns) == sum(len(q) for _, q in CONVERSATIONS)
