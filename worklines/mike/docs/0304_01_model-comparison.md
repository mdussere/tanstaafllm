# Step 3.3–3.4 — model comparison and recommendation

> **Freshness:** 🟡 historical · **Written:** 2026-10-13 · **Checked:** 2026-10-31 · **Step:** mike 3.4 ✅

**Question answered:** across every desk-host measurement of Step 3, how do the candidates compare, and which model does Mike use?<br>
**Date:** 2026-10-11<br>
**Status:** consolidates `0302_01` to `0302_05`. Desk host only (Intel i5-4590, x86_64); nothing measured on `luna-pi` or Luna. **Decision: LFM2.5-350M (user, 2026-10-11).** Naming note: the user is reconsidering the Mannie/Mike names; this document does not rename anything. *(Naming settled by D16 on 2026-10-11: this line is Mike, the local brain.)*

## Summary table

| | LFM2.5-350M | LFM2.5-230M | FunctionGemma 270M | Qwen3-0.6B |
| --- | --- | --- | --- | --- |
| File, Q4_K_M | 219 MiB | 146 MiB | 241 MiB | 378 MiB |
| KV cache, 2,048 tokens | 24 MiB (measured) | 24 MiB (from config) | ≈ 13.5 MiB (from config) | 224 MiB (from config) |
| Peak RSS, default (repack, batch 64) | 489–550 MiB | 361–448 MiB | 554–712 MiB | not run |
| **Peak RSS, lean** (no repack, batch 16) | **351 MiB** | **263–309 MiB** | not run | not run |
| Lean, minus Python (≈ 50 MiB) | ≈ 300 MiB | ≈ 215–260 MiB | — | — |
| Smoke set (13), prompt v2 | 10 | 9 | 4–5 | not run |
| Main set (81), v4, constrained, model / adapter | 38 / 48 | 37 / 41 (lean) | not run | not run |
| **Held-out (31), v4, constrained, model / adapter** | 11 / 16 | 15 / 19 (lean) | not run | not run |
| **Held-out, keyword table first** | 20 | 21 (lean) | — | — |
| Time per request, desk, prefix cached | 0.21–0.25 s | 0.15–0.20 s | 0.31–0.74 s | — |
| Time per request, desk, v4 (prefix partly cached) | ≈ 2 s | ≈ 2–2.9 s (lean) | — | — |
| Conversation (`/chat`, by hand) | "impressive" (user) | fluent but wrong (confuses itself with the user, invents tools) | — | — |

Keyword table alone: 14/31 held-out (80/81 on the main set, which it was written on).

Sources: `0302_01` (smoke, memory breakdown), `0302_02` (prompt v2, prefix cache), `0302_03` (full sets, v3/v4), `0302_04` (keyword table first), `0302_05` (lean RAM). The 230M lean full-set run is `results/mike/model-eval/20261011T102103Z/`.

## Measured RAM against the Step 3 estimates

| Model | Estimate (`0301_01`) | Measured, lean, minus Python |
| --- | --- | --- |
| LFM2.5-350M | ≈ 270–300 MiB | ≈ 300 MiB |
| LFM2.5-230M | ≈ 190–220 MiB | ≈ 213 MiB (3 requests) to ≈ 260 MiB (full run, two saved states) |

The estimate held once the avoidable overhead was removed:
- llama.cpp's repacked x86 copy of the weights;
- the compute buffer at batch 64;
- llama-cpp-python's logits array;
- Python itself.

## Load and prompt

- Load time: 0.1–2 s from the desk host's disk. Not representative of Luna's SD card.
- Prompt length: 618 tokens (v1) to about 1,100 tokens (v3/v4). The shared prefix: 924 tokens in v2, 1,135 in v3, but only 401 in v4. LFM's chat template writes the tools after the system text, so v4's desktop line cuts the cached part short.

## Recommendation

1. **LFM2.5-350M**, as the user decided. It is the best conversational model of the set and on a par with the best at choosing a tool.
2. **LFM2.5-230M stays the fallback** if RAM must go lower. With prompt v4 and the keyword table first, it matches 350M on the tool task (21 vs 20 held-out), for about 50 MiB less.
3. **FunctionGemma 270M and Qwen3-0.6B are dropped:** the first without fine-tuning, the second for RAM.
4. **Routing:** keyword table first, model only when the table found an app but no verb (`0302_04`).
5. **Not good enough yet:** 20/31 on new phrasings. The remaining work, in the plan: leave Python and choose a micro-harness (Step 3b), measure on `luna-pi` and Luna, slim the vocabulary (3.8), and possibly fine-tune (option B).
