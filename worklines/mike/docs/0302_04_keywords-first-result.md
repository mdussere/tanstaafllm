# Step 3.6 result — option A: keyword table first, model second

> **Freshness:** 🟡 historical · **Written:** 2026-10-13 · **Checked:** 2026-10-31 · **Step:** mike 3.2 ✅

**Question answered:** if the keyword table answers what it recognises and the model answers only the rest, how much better is that than either alone?<br>
**Date:** 2026-10-11<br>
**Status:** computed from saved model answers: no model was run again. Inside the Step 3 green light. Desk-host answers only.

## How

- **Source:** the saved LFM2.5-350M runs of `0302_03`:
  - v4: `results/mike/model-eval/20261009T213217Z/LFM2.5-350M-Q4_K_M.gguf.v4.json`;
  - v3: `results/mike/model-eval/20261009T211424Z/LFM2.5-350M-Q4_K_M.gguf.json`.
- **Code:** `hybrid()` and `hybrid_from_run()` in `test/mike/mike_eval.py`; `test/mike/test_hybrid.py`.
  - The deterministic routing tests are in the default suite.
  - The re-scoring is run with `MIKE_EVAL_RUN=<report> uv run pytest test/mike/test_hybrid.py -m integration -s`.
  - It writes `hybrid.<variant>.json` next to the report.
- **Two routings:**
  - **model on any miss:** the model answers whenever the table recognises nothing;
  - **model on app only:** the model answers only when the table found an app but no verb it knows. If the table finds no app at all, the answer stays `none`.

## Results (LFM2.5-350M, prompt v4)

Right calls; "+ adapter" includes the ⚖️ rule "focus on a closed app → launch it".

| | Held-out (31) | Held-out + adapter | Main (81) | Requests sent to the model (held-out / main) |
| --- | --- | --- | --- | --- |
| Keyword table alone | 14 | 14 | 80 *(written on it)* | 0 / 0 |
| Model alone, constrained | 11 | 16 | 38 | 31 / 81 |
| Model alone, free | 13 | 16 | 33 | 31 / 81 |
| Model on any miss, constrained | 15 | 18 | 72 | 22 / 16 |
| Model on any miss, free | 18 | 19 | 76 | 22 / 16 |
| **Model on app only, constrained** | 17 | **20** (65 %) | 79 | 15 / 1 |
| Model on app only, free | 17 | 18 | 80 | 15 / 1 |

With prompt v3 the "app only" routing gives 16–17 on the held-out set, so v4 is the better prompt here too.

## What this shows

- **Combining them is better than either alone:** 20/31 on new phrasings, against 14 (table) and 16 (model) alone. It also keeps the table's near-perfect score on the phrasings it knows (79–80/81).
- **"Model on app only" is the safer routing.** When the table finds no app, the request is usually out of scope ("réserve un train pour lyon"). Sending it to the model mostly produced a wrong action, so keeping `none` is both safer and more often right.
- **The model is called less.** It answered 15 of 31 held-out requests and 1 of 81 main ones. On Luna, each call it skips saves about 2 s here, and more on Luna's cores. Mike must still load the model for the requests that need it, so RAM is unchanged when it is resident.
- **It is still not good enough as a product:** one held-out request in three is wrong. The rest of the gap is the model's: it cannot pick `move_window`, it keeps the verb in `type_text`, and it seldom chooses `none`.

## Recommendation

Adopt "keyword table first, model on app only" as Mike's v0 routing, **subject to the user's approval**. It changes the contract's flow, not its tools. Then:
- **B (LoRA fine-tuning of LFM2.5-350M):** the remaining errors are exactly what a contract-generated training set would teach. It is a new step and needs `🟩 go`.
- **C (two-stage call)** stays a cheaper alternative to try within Step 3.

Every evaluation should keep scoring on the held-out set, and on new phrasings written after each change.
