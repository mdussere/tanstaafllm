# Step 3.2c result — the shortlist on the full evaluation sets

**Question answered:** on the Step 2 evaluation sets (81 main + 31 held-out requests), how well do the LFM models do with the contract, compared with the keyword baseline?<br>
**Date:** 2026-10-09<br>
**Status:** measured on the desk host only (Intel i5-4590, 4 threads, `n_batch` 64), done under Professor's D13. **The host was shared:** load average about 4 from other sessions, so the times are pessimistic. No claim about Luna or `luna-pi`.

## Runs

| Run | Prompt | Models | Evidence |
| --- | --- | --- | --- |
| 1 | **v3**: rules and examples in the system turn; desktop line `[open: …; focus: …]` at the start of the user turn | LFM2.5-350M, LFM2.5-230M | `results/mike/model-eval/20261009T211424Z/` |
| 2 | **v4**: same rules; desktop as the last line of the system turn; user turn = the request alone | LFM2.5-350M | `results/mike/model-eval/20261009T213217Z/` |

Command: `MIKE_PROMPT=v3|v4 [MIKE_MODELS=…] MIKE_ASSET_ROOT=… uv run --group mike pytest test/mike/test_model_eval.py -m integration`.

Run 1's prefix cache missed, because the prefix was taken from two cases that happened to share a desktop. It was fixed before run 2: the prefix is now the part shared by every case. The answers do not change; only the times of run 1 are affected (about 3.2 s per request instead of a fraction of a second).

## Results

"Model" = the model's own call is right. "Adapter" = right after the adapter's rule "focus on a closed app → launch it" (⚖️, awaiting the user).

| | Main, model | Main, adapter | Held-out, model | Held-out, adapter |
| --- | --- | --- | --- | --- |
| Keyword baseline | 80/81 *(written on this set)* | 80/81 | **14/31** | 14/31 |
| LFM2.5-350M, v3, free | 23 | 32 | 8 | 12 |
| LFM2.5-350M, v3, constrained | 20 | 31 | 9 | 14 |
| LFM2.5-230M, v3, free | 16 | 17 | 5 | 5 |
| LFM2.5-230M, v3, constrained | 14 | 15 | 4 | 4 |
| **LFM2.5-350M, v4, free** | 33 | 39 | 13 | **16** |
| **LFM2.5-350M, v4, constrained** | 38 | **48** (59 %) | 11 | **16** (52 %) |

Time per request (median) and peak RSS:
- LFM2.5-350M v4: about 2.0 s, 550 MiB;
- LFM2.5-230M v3: about 2.0 s (prefix cache missed), 448 MiB.

## What this shows

1. **The smoke result (10/13) was optimistic.** On 112 requests the best setting gets about 52–59 % right, even with the adapter's help. The smoke set was 13 requests and prompt v2 was tuned on it.
2. **The model barely beats the keyword table on new phrasings:** 16/31 against 14/31. That difference is too small to justify about 450 MiB of RAM on Luna.
3. **Where the desktop state goes matters a lot.** With the desktop at the start of the user turn (v3), LFM2.5-350M collapsed into `focus_window` with the first or focused app for almost everything, including weather and e-mail. Put back in the system turn (v4), it recovered about 15 points.
4. **The typical errors (v4 and v3 alike):**
   - "lance / ouvre X" becomes `focus_window`. The adapter rule fixes most of these.
   - `move_window` is almost never chosen; "mets X à gauche" becomes `focus_window(X)`.
   - `type_text` keeps the verb ("tape cd documents" → text "tape cd documents").
   - `none` is rarely chosen; out-of-scope requests become `focus_window` or `type_text`.
5. **v4 costs speed.** LFM's chat template writes the tool list *after* the system text. With the desktop at the end of the system text, only the first 401 tokens are shared, and the tool list is reprocessed for each request (about 2 s here). Prefix caching and "desktop in the system turn" pull in opposite directions with this template. A fix is to place the tools before the rules in a hand-written template; not tried.
6. **LFM2.5-230M is not good enough** with these prompts (4–5/31 held-out). It stays only as a size reference.

## Options (for the user; none started)

| Option | What | Cost | Expectation |
| --- | --- | --- | --- |
| A. Keyword table first, model second | Rules answer what they recognise with certainty; the model only sees the rest | none in RAM when the rules hit | Keeps the 80/81 on known phrasings; the model only adds coverage |
| B. Fine-tune LFM2.5-350M (LoRA) | A few thousand synthetic requests generated from the contract (verbs × apps × desktops); evaluate only on the held-out set and on new phrasings | a training run on the desk host; same RAM at run time | Google reports 58 → 85 % for FunctionGemma after fine-tuning; plausible here, unproven |
| C. Two-stage call | First choose the tool (7 options, grammar), then fill the arguments | two short generations | Should cure the `focus_window` collapse; unproven |
| D. Ask Mannie | Send what Mike cannot handle to the remote model, with the user's consent | money, network, privacy | Not a local answer; already planned as a later, visible escalation |

**Recommendation:** A now (it is cheap and honest), then B, measured only on held-out requests. Decide on C after B. A and C fit Step 3; B is a new step (fine-tuning) and needs the user's green light.
