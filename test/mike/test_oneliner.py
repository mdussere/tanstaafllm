"""Mike 8.0c: can the desk models write a correct bash one-liner? (`oneliner.feature`)

Five everyday requests, each with the commands accepted as right (regular
expressions on the first command line of the answer). Asked through each
model's chat template, French and English, greedy and Liquid AI's sampling.

    uv run pytest test/mike/test_oneliner.py -m integration -s
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
MODELS = os.environ.get("MIKE_MODELS", ",".join([
    "LFM2.5-230M-Q4_K_M.gguf", "LFM2.5-350M-Q4_K_M.gguf", "LFM2.5-350M-Q4_0.gguf", "LFM2.5-350M-QAD-Q4_0.gguf",
    "Qwen3-0.6B-Q4_K_M.gguf", "LFM2-700M-Q4_K_M.gguf", "gemma-3-1b-it-Q4_K_M.gguf",
    "LFM2.5-1.2B-Instruct-Q4_K_M.gguf", "Qwen3-1.7B-Q4_K_M.gguf"])).split(",")
SYSTEM = {"fr": "Tu es un assistant Linux. Réponds uniquement par une seule ligne de commande bash, sans explication.",
          "en": "You are a Linux assistant. Answer with a single bash command line only, no explanation."}
# (French request, English request, accepted command patterns)
TASKS = [
    ("Génère un one-liner bash pour connaître l'occupation du disque.",
     "Generate a bash one-liner to show disk usage.",
     [r"^\s*(sudo\s+)?df\b", r"^\s*(sudo\s+)?du\b.*-[a-z]*s"]),
    ("Génère un one-liner bash pour lister les fichiers de mon dossier personnel, triés par taille.",
     "Generate a bash one-liner to list the files in my home directory, sorted by size.",
     [r"^\s*ls\b[^|]*-[a-zA-Z]*S[^|]*(~|\$HOME|/home)", r"^\s*du\b.*(~|\$HOME|/home).*\|\s*sort\b"]),
    ("Génère un one-liner bash pour trouver les fichiers .log modifiés depuis moins d'un jour.",
     "Generate a bash one-liner to find the .log files modified less than a day ago.",
     [r"^\s*find\b.*-name\s+['\"]?\*\.log['\"]?.*-mtime\s+(-1|0)\b", r"^\s*find\b.*-mtime\s+(-1|0)\b.*-name\s+['\"]?\*\.log",
      r"^\s*find\b.*\*\.log.*-(mmin\s+-1440|newermt)"]),
    ("Génère un one-liner bash pour compter les lignes du fichier notes.txt.",
     "Generate a bash one-liner to count the lines of the file notes.txt.",
     [r"^\s*wc\s+-l\s+(<\s*)?notes\.txt\s*$", r"^\s*cat\s+notes\.txt\s*\|\s*wc\s+-l\s*$",
      r"^\s*\w+=\$\(wc\s+-l\s+(<\s*)?notes\.txt\)\s*$"]),
    ("Génère un one-liner bash pour afficher les 5 processus qui utilisent le plus de mémoire.",
     "Generate a bash one-liner to show the 5 processes using the most memory.",
     [r"^\s*ps\b.*--sort[= ]-?(%mem|-?rss)\b.*\|\s*head\b", r"^\s*ps\b(?!.*grep).*\|\s*sort\b.*\|\s*head\b",
      r"^\s*top\b.*-o\s*%?mem.*\|\s*head\b"]),
]
SAMPLING = {"greedy": {"temperature": 0.0, "top_k": 1},
            "liquid": {"temperature": 0.1, "top_k": 50, "repeat_penalty": 1.05}}
RUN_DIR = ev.REPO / "results/mike/oneliner" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def first_command(answer: str) -> str:
    """The first non-empty line, outside a Markdown fence and without a `$ ` prompt."""
    lines = [l for l in answer.strip().splitlines() if l.strip() and not l.strip().startswith("```")]
    line = lines[0].strip() if lines else ""
    return re.sub(r"^\$\s+", "", line.strip("`"))


# Commands that match a pattern but do something else are not right.
REJECT = [r"\|\s*grep\s+['\"]?(mem|memory)['\"]?", r"-exec\s+grep\b", r"\bwmic\b"]


def right(command: str, patterns: list[str]) -> bool:
    return any(re.search(p, command) for p in patterns) and not any(re.search(r, command) for r in REJECT)


@pytest.mark.integration
@pytest.mark.timeout(1800)
@pytest.mark.parametrize("model", MODELS)
def test_oneliner(model):
    path = ASSETS / model
    if not path.is_file() or not ms.SERVER.is_file():
        pytest.skip(f"{model} or llama-server missing")
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    with ms.Server(str(path), ["--jinja", "-c", "2048"], RUN_DIR / f"{model}.server.log") as server:
        for index, (fr, en, patterns) in enumerate(TASKS):
            for lang, request in (("fr", fr), ("en", en)):
                for sampling, params in SAMPLING.items():
                    reply = server.post("/v1/chat/completions", {
                        "messages": [{"role": "system", "content": SYSTEM[lang]},
                                     {"role": "user", "content": request}],
                        "max_tokens": 80, "seed": 1, **params,
                        "chat_template_kwargs": {"enable_thinking": False}}, timeout=300)
                    answer = reply["choices"][0]["message"].get("content") or ""
                    command = first_command(answer)
                    rows.append({"model": model, "task": index, "lang": lang, "sampling": sampling,
                                 "right": right(command, patterns), "command": command, "answer": answer,
                                 "one_line": len([l for l in answer.strip().splitlines()
                                                  if l.strip() and not l.strip().startswith("```")]) == 1})
                    print(json.dumps({k: rows[-1][k] for k in ("model", "task", "lang", "sampling", "right")}),
                          "|", command[:150], flush=True)
    with (RUN_DIR / "answers.jsonl").open("a") as out:
        for row in rows:
            out.write(json.dumps(row, ensure_ascii=False) + "\n")
    assert len(rows) == 4 * len(TASKS)
