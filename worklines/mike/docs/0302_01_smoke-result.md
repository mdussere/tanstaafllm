# Step 3.2a–b result — first smoke test of the three shortlisted models

> **Freshness:** 🟡 historical · **Written:** 2026-10-13 · **Checked:** 2026-10-31 · **Step:** mike 3.2 ✅

**Question answered:** out of the box, on the desk host, do the three shortlisted models pick the right Wyoh action for short French requests, how fast, and with how much memory?<br>
**Date:** 2026-10-09<br>
**Status:** measured on the desk host only (Intel i5-4590, 4 threads, x86_64). **No claim about Luna or `luna-pi`.**

## How it was run

- Harness: `test/mike/mike_bench.py`, `test/mike/test_model_smoke.py` (Gherkin: `test/mike/model_smoke.feature`).
- Command: `MIKE_N_BATCH=<512|64> MIKE_ASSET_ROOT=/data/michael/tanstaafllm/mike-assets uv run --group mike pytest test/mike/test_model_smoke.py -m integration`.
- Runtime: `llama-cpp-python==0.3.36` (uv group `mike`), built with `-DGGML_NATIVE=ON`; greedy decoding; context 2,048 tokens.
- 13 French requests (Mycroft-style lower case), the intent's 7 tools, a fixed desktop (terminal and browser open). Nothing executed.
- Two modes: **free** (the model answers as it wants) and **constrained** (call opener prefilled + grammar: only a well-formed call from the list is possible).
- Each model ran alone in a fresh process; peak RSS is that process's `VmHWM`. The Python harness alone is about 50 MiB before loading.
- Evidence: `results/mike/model-comparison/20261009T2036*Z` to `20261009T204134Z/` (one JSON per model and batch size, plus `summary.md`).

Files (SHA-256 in `/data/michael/tanstaafllm/mike-assets/SHA256SUMS`):

| File | Size | SHA-256 (start) |
| --- | --- | --- |
| `LFM2.5-350M-Q4_K_M.gguf` | 229,312,224 B | `7e6f7264…` |
| `LFM2.5-230M-Q4_K_M.gguf` | 153,406,304 B | `7bbd9038…` |
| `functiongemma-270m-it-Q4_K_M.gguf` (unsloth mirror) | 253,127,904 B | `7474135c…` |

## Results

Score = right tool **and** right arguments, out of 13. A text answer counts as `none`.

| Model | Free | Constrained | Prompt tokens | Typical time per request | Peak RSS, `n_batch` 512 | Peak RSS, `n_batch` 64 |
| --- | --- | --- | --- | --- | --- | --- |
| LFM2.5-350M | **6/13** | **6/13** | 618 | 1.6–1.8 s | 529–540 MiB | 492 MiB |
| LFM2.5-230M | 5/13 | 3/13 | 618 | 1.0–1.3 s | 406 MiB | 365 MiB |
| FunctionGemma 270M | 4/13 | 4/13 | 548 | 0.25–0.5 s (free), 0.5–1 s (constrained) | 580 MiB | 554 MiB |

Accuracy did not change with `n_batch`.

## What the answers show

- **None of the three is good enough as is.** About half the requests get the right action at best.
- **LFM2.5-350M is the best and the most consistent.** It always produced a clean call in its own format. Its main error is a bias towards `focus_window`: "ouvre la calculatrice", "ferme le navigateur", "mets le navigateur à gauche" all became `focus_window`. It got `launch_app`, `list_windows`, `type_text` and `focus_window` right when the verb was clear.
- **LFM2.5-230M** often answered in text ("Je suis un modèle d'IA…") or with `list_windows`. Constrained, it fell back to `list_windows` or `focus_window`.
- **FunctionGemma 270M** mixed the formats in free mode (`call:wolfenstein<escape>…`) and refused simple requests ("I cannot assist with…"). That matches Google's warning: it is meant to be fine-tuned.
- **The constrained mode cannot say no well.** With the call opener prefilled, the models rarely chose the `none` tool. "Quel temps fera-t-il demain" became `focus_window(app="wolfenstein")`. Free mode refused these correctly, in text.

## Memory: why the RSS is higher than the estimate

The estimate in `0301_01` was about 270–300 MiB for LFM2.5-350M. The measured peak was 492–540 MiB. llama.cpp's own log gives the breakdown (LFM2.5-350M, `n_batch` 512):

| Part | Size | Note |
| --- | --- | --- |
| Model file, memory-mapped | 214 MiB | as expected |
| **Repacked weights (`CPU_REPACK`)** | **133 MiB** | an x86 copy of part of the weights in a faster layout; those weights are then held twice. Whether ARM does the same depends on the CPU's features; to measure on `luna-pi`. |
| KV cache, 2,048 tokens | 24 MiB | exactly as estimated |
| Recurrent (convolution) state | 0.08 MiB | negligible |
| **Compute buffer** | **132 MiB** | grows with `n_batch` × vocabulary |
| llama-cpp-python logits array | up to 128 MiB | `n_batch` × 65,536 × 4 B, filled as used |
| Python + harness | ≈ 50 MiB | not part of a lean runtime |

So the KV cache was not the issue. The repacked copy, the compute buffer and the Python wrapper were. A lean Luna runtime would avoid most of them: a small `n_batch`, no repack, and the C library or `llama-server` instead of Python. That is a hypothesis to measure, not a result.

FunctionGemma's vocabulary is four times larger (262,144 entries), so its logits and compute buffers are larger too.

## Speed: prompt caching does not help the LFM models here

All three models get the same ~610-token prefix (system text + tools) for every request.

- **FunctionGemma** (a plain transformer) reuses it: the first request took 1.2 s, the next ones 0.25–0.5 s.
- **LFM2.5** (hybrid) reprocessed the whole prompt each time (about 1.5 s on this desk CPU). llama-cpp-python cannot rewind a convolution state, so it starts over. Saving the state right after the fixed prefix and restoring it before each request should fix this; to test.

On Luna's Cortex-A35 cores, prompt processing will be many times slower than on this desk CPU. So prompt caching matters more than the model choice for speed.

## What this means for the next step

1. **Improve the prompt before judging the models:** tool descriptions with French verbs ("ouvrir, lancer → launch_app; fermer → close_window"), one or two short examples, and the open windows given in a clearer form. This is cheap and may move the score a lot.
2. **Give the constrained mode a real way to say no:** let the grammar allow a short text answer as well as a call, or run a first "is there a tool for this?" choice.
3. **State save/restore for the LFM prefix,** then measure the time per request again.
4. **Then the real evaluation set (Step 2),** so that 13 requests do not drive the decision.
5. **Fine-tuning** (LFM2.5-350M or FunctionGemma) only if 1–3 are not enough.

Current recommendation: keep **LFM2.5-350M** as the lead candidate and **LFM2.5-230M** as the lighter fallback. FunctionGemma only makes sense with fine-tuning.
