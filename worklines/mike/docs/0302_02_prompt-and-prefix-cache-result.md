# Step 3.2d–f result — a better prompt and a cached prefix

> **Freshness:** 🟡 historical · **Written:** 2026-10-13 · **Checked:** 2026-10-31 · **Step:** mike 3.2 ✅

**Question answered:** how much do a better prompt (3.2d) and a cached prompt prefix (3.2f) change accuracy and speed, and does the constrained mode still fail to refuse (3.2e)?<br>
**Date:** 2026-10-09<br>
**Status:** measured on the desk host only (Intel i5-4590, 4 threads, `n_batch` 64, context 2,048). Same 13 smoke requests as `0302_01`. **No claim about Luna or `luna-pi`.**

## What changed

- **Prompt v2** (`SYSTEM_PROMPT_V2`, `TOOLS_V2` in `test/mike/mike_bench.py`). It adds:
  - the French verbs that ask for each tool ("ouvre, lance, démarre → launch_app");
  - the list of open windows, the focused window and the apps that can be started;
  - six short examples. A unit test checks that none of them is a smoke request.

  The tools and their arguments are the same. The prompt grows from about 618 to 934 tokens.
- **Prefix cache.** The part of the prompt that every request shares (924 tokens) is evaluated once. The model state is saved and restored before each request, so only the user's words (about 10 tokens) are processed. This is the only way to reuse the prefix with LFM's hybrid layers, whose state cannot be truncated.

Commands: `MIKE_PROMPT=v2 [MIKE_PREFIX_CACHE=1] MIKE_N_BATCH=64 MIKE_ASSET_ROOT=… uv run --group mike pytest test/mike/test_model_smoke.py -m integration`.
Evidence:
- `results/mike/model-comparison/20261009T204444Z/`: v2 with the cache, all three models;
- `results/mike/model-comparison/20261009T204535Z/`: v2 without the cache, LFM2.5-350M.

## Results

Score = right tool and right arguments, out of 13.

| Model | v1 free / constrained (`0302_01`) | **v2 free / constrained** | Time per request, v2, no cache | **Time per request, v2, cached** | Prefix: one-off cost | Peak RSS, v2 cached |
| --- | --- | --- | --- | --- | --- | --- |
| LFM2.5-350M | 6 / 6 | **10 / 10** | 2.4–2.5 s | **0.21–0.25 s** | 2.3 s, state 10.9 MiB | 550 MiB (495 without the cache) |
| LFM2.5-230M | 5 / 3 | **9 / 9** | — | **0.15–0.20 s** | 1.5 s, state 10.9 MiB | 418 MiB |
| FunctionGemma 270M | 4 / 4 | 4 / 5 | — | 0.31–0.74 s | 1.6 s, state 14.8 MiB | 712 MiB |

LFM2.5-350M gave the same answers with and without the cache: the cache changes speed only.

## What this shows

- **The prompt mattered more than the model.** Both LFM models gained 4–6 correct answers. FunctionGemma did not improve; without fine-tuning it is not a candidate.
- **The prefix cache makes the LFM models ten times faster here.** Only the request's own tokens are processed, and they are a few dozen at most. On Luna's slower cores this is the difference between waiting several seconds and waiting tens of seconds for each request. It is still to be measured on `luna-pi`.
- **It costs memory.** Each saved state is about 11 MiB, but llama-cpp-python's copy also holds a logits array. Here the peak rose by about 54 MiB with two saved states (one per mode). A runtime keeping a single state would pay less.
- **3.2e is no longer needed for this smoke set.** With prompt v2, the constrained mode chose `none` for both requests with no tool ("quel temps fera-t-il demain", "envoie un mail à paul"). To recheck on the real evaluation set.

## LFM2.5-350M's three remaining errors

| Request | Answer | Expected |
| --- | --- | --- |
| ouvre la calculatrice | `focus_window(app="calculator")` | `launch_app` |
| ouvre le gestionnaire de fichiers | `focus_window(app="files")` | `launch_app` |
| mets le terminal en plein écran | `focus_window(app="terminal")` | `move_window(…, place="full")` |

Two of the three ask to bring forward an app that is **not open**. The adapter knows which windows are open, so it could turn "focus an app that is not open" into "launch it". It would show that change, and the user would still accept. With that rule, LFM2.5-350M would be at 12/13 on this set. **This is a proposal for the tool contract (Step 1), not applied to the scores.**

## Recommendation

- **Lead candidate: LFM2.5-350M**, with prompt v2 and the prefix cache.
- **Lighter fallback: LFM2.5-230M**, 9/13 in about 130 MiB less RAM.
- **Drop FunctionGemma 270M** unless a fine-tuning step is opened.
- **Next:** build the real evaluation set (Step 2), so that the decision does not rest on 13 requests that the prompt was tuned against. Then measure on `luna-pi` (Step 4; needs `🟩 go Step 4` and `luna-pi` switched on).
