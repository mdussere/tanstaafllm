"""Mike Step 11: ask a Chat-GBC shell checkpoint every NL2SH test request (greedy).

Run by `test_chat_gbc_nl2sh.py` with Chat-GBC's own venv, from the patched clone:

    <venv>/bin/python <this file> <ckpt.pt> <test.jsonl> <out_dir>

Each test line holds the request and its two accepted commands. Writes
`rows.jsonl` (one row per request) and `eval.json` (totals) to <out_dir>.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))  # the patched clone

from llm import tokenizer as tok  # noqa: E402
from llm.evaluate import edit_distance, float_replier  # noqa: E402
from llm.model import load_checkpoint  # noqa: E402


def squeeze(command: str) -> str:
    return " ".join(command.split())


def main(ckpt: str, test: str, out: str) -> None:
    model, _ = load_checkpoint(ckpt)  # installs the checkpoint's vocabulary
    reply = float_replier(model, max_new=model.cfg.ctx)
    out_dir = Path(out)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    started = time.perf_counter()
    with (out_dir / "rows.jsonl").open("w") as f:
        for line in Path(test).read_text().splitlines():
            item = json.loads(line)
            golds = [tok.normalize(g) for g in item["bash"]]
            prompt_tokens = len(tok.format_turn(item["nl"]))
            got = reply(item["nl"]).strip()
            row = {"nl": item["nl"], "golds": golds, "got": got, "difficulty": item["difficulty"],
                   "prompt_tokens": prompt_tokens,
                   "gold_tokens": min(len(tok.encode(g)) for g in golds),
                   "exact": any(got == g for g in golds),
                   "exact_spaces": any(squeeze(got) == squeeze(g) for g in golds),
                   "utility": any(got.split()[:1] == g.split()[:1] for g in golds),  # same first command
                   "cer": round(min(edit_distance(got, g) / max(1, len(g)) for g in golds), 3)}
            rows.append(row)
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    n = len(rows)
    fits = [r for r in rows if r["prompt_tokens"] + r["gold_tokens"] + 1 <= model.cfg.ctx]
    result = {"ckpt": ckpt, "n": n, "params": model.num_params(), "ctx": model.cfg.ctx,
              "seconds": round(time.perf_counter() - started, 1),
              "exact": sum(r["exact"] for r in rows), "exact_spaces": sum(r["exact_spaces"] for r in rows),
              "utility": sum(r["utility"] for r in rows), "cer_mean": round(sum(r["cer"] for r in rows) / n, 3),
              "fits_ctx": len(fits), "exact_when_fits": sum(r["exact"] for r in fits),
              "by_difficulty": {}}
    for d in sorted({r["difficulty"] for r in rows}):
        group = [r for r in rows if r["difficulty"] == d]
        result["by_difficulty"][d] = {"n": len(group), "exact": sum(r["exact"] for r in group),
                                      "utility": sum(r["utility"] for r in group)}
    (out_dir / "eval.json").write_text(json.dumps(result, indent=1))
    print(json.dumps(result))


if __name__ == "__main__":
    main(*sys.argv[1:4])
