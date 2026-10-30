# Step 10 — Qualifying a model: 90 % stable on the evaluation cases

**Question answered:** does any model give at least 90 % stable right answers on Mike's 112 evaluation cases, and how small can it be?<br>
**Date:** 2026-10-29<br>
**Status:** measured on the desk host Termidor only (green light: the user, 2026-10-29). BitNet b1.58 2B4T (10.4) ran alone afterwards (`results/mike/qualify/20261029T193703Z/`, 49 min).
- **Test:** `test/mike/test_qualify.py` (`integration`, `qualify.feature`). **Evidence:** `results/mike/qualify/20261029T120112Z/` (per model and format: `report.json`, `rows.jsonl` with all 11 answers per case, the server log; `summary.jsonl`).
- **Runtime:** `llama-server` b11429, context 2,048, one slot, 4 threads, default batch. The whole series took 7 h 35 min.

## The gate (proposed in the plan, the user may change it)

- **Asked 11 times:** each case is asked twice greedily (to check determinism), then 9 times sampled (temperature 0.5, top-p 0.95, seeds 1–9).
- **Stable-right:** a case counts when at least 9 of its 10 counted answers (the first greedy one and the 9 sampled) are right after the adapter.
- **Qualified:** at least 90 % of the cases are stable-right on the main set (81 cases) **and** on the held-out set (31 cases).

## Summary

- **No model is qualified.** BitNet b1.58 2B4T is the worst of all (2/81, 0/31).
- **Closest to the gate:** the two 4B models, each on one set only:
  - Qwen3-4B: 92.6 % main, 83.9 % held-out;
  - Gemma 3 4B: 87.7 % main, 93.5 % held-out.
- **The cases can be solved at about 90 %**, so the test is not out of reach. The ceiling models' failures, listed below, are partly real errors and partly cases whose expected answer can be argued. Those are for the user to judge; no expected answer was changed.
- **Size matters more than anything else:**
  - Qwen3 gives 70 % (0.6B), 86 % (1.7B) and 93 % (4B) on the main set.
  - The LFM models stay at 36–54 % from 230M to 1.2B.
- **The candidate that might fit Luna, Qwen3-0.6B (378 MiB file), gives 70 % and 65 %.** It is far from the gate, but it is ahead of every LFM model.
- **LFM models depend on their own tool-call format.** In the plain format they drop to 3–20 % stable (LFM2.5-350M: 2/81). Qwen and Gemma only ever ran in the plain format.
- **Greedy decoding is not always deterministic.** Asking the same case twice with the same prompt gave a different answer in 14 cases for Qwen3-1.7B, 4 for Qwen3-4B, 2 for Gemma 3 4B and 0 for the LFM models. The second request reuses the cached prompt, so the numbers are computed in a different order (the user's point, 2026-10-29).

## Results

| Model | File | Format | Main, stable-right | Held-out, stable-right | Main, greedy | Held-out, greedy | Mean right (main / held-out) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LFM2.5-230M | 146 MiB | native | 31/81 (38 %) | 10/31 (32 %) | 44 | 19 | 50 % / 56 % |
| LFM2.5-230M | | plain | 7/81 | 2/31 | 16 | 7 | 18 % / 20 % |
| LFM2.5-350M Q4_0 | 219 MB | native | 44/81 (54 %) | 13/31 (42 %) | 52 | 16 | 62 % / 51 % |
| LFM2.5-350M Q4_0 | | plain | 2/81 | 1/31 | 27 | 7 | 26 % / 25 % |
| Qwen3-0.6B | 378 MiB | plain | **57/81 (70 %)** | **20/31 (65 %)** | 61 | 21 | 75 % / 68 % |
| LFM2-700M | | native ¹ | 29/81 (36 %) | 6/31 (19 %) | 43 | 11 | 48 % / 32 % |
| LFM2-700M | | plain | 12/81 | 0/31 | 26 | 4 | 31 % / 15 % |
| Gemma 3 1B | 806 MB | plain | 26/81 (32 %) | 8/31 (26 %) | 27 | 9 | 33 % / 27 % |
| LFM2.5-1.2B | | native | 43/81 (53 %) | 15/31 (48 %) | 54 | 19 | 64 % / 59 % |
| LFM2.5-1.2B | | plain | 16/81 | 6/31 | 29 | 8 | 34 % / 27 % |
| Qwen3-1.7B | 1.1 GB | plain | 70/81 (86 %) | 25/31 (81 %) | 69 | 25 | 87 % / 83 % |
| **Qwen3-4B** | 2.5 GB | plain | **75/81 (92.6 %)** | 26/31 (83.9 %) | 77 | 26 | 96 % / 85 % |
| **Gemma 3 4B** | 2.5 GB | plain | 71/81 (87.7 %) | **29/31 (93.5 %)** | 72 | 29 | 89 % / 94 % |
| BitNet b1.58 2B4T ² | 1.19 GB | plain | 2/81 (2.5 %) | 0/31 | 2 | 1 | 6 % / 5 % |

² BitNet through bitnet.cpp (built with gcc under `mike-tools/bitnet/`). Two fixes were needed: the chat template from the model's `tokenizer_config.json` (the GGUF's template drops the system turn), and the Llama 3 pre-tokenizer (`--override-kv tokenizer.ggml.pre=str:llama-bpe`; the GGUF declares none). It answers mostly about "dino", the first app of the examples. Without the grammar it echoes pieces of the prompt. Greedy was not deterministic in 7 main cases.

¹ LFM2-700M's chat template does not render the tool list the way LFM2.5's does (428 prompt tokens instead of about 1,085), so its "native" row ran without the tools. It is not a fair measure of the model.

## What the ceiling models miss

These are the cases where Qwen3-4B or Gemma 3 4B is not stable-right. Each line gives the right answers out of 10 for Qwen3-4B / Gemma 3 4B / Qwen3-1.7B.

| Case | Expected | 4B / G4B / 1.7B | Usual wrong answer | Arguable? |
| --- | --- | --- | --- | --- |
| ouvre spotify | `none` | 0 / 0 / 10 | `launch_app(browser)` | **yes:** Spotify runs in a browser |
| ouvre youtube (held-out) | `none` | 0 / 0 / 6 | `launch_app(browser)` | **yes**, same |
| mets-moi la calculatrice (held-out) | `launch_app(calculator)` | 0 / 1 / 0 | `move_window(calculator, full)` | **yes:** « mets » is the verb table's word for moving |
| je veux voir l'éditeur | `focus_window(editor)` | 0 / 4 / 10 | `launch_app(editor)` | partly: depends on the desktop line |
| qu'est-ce qui tourne en ce moment, fais-moi la liste des fenêtres, quelles applications tournent, qu'est-ce que j'ai d'ouvert | `list_windows` | 1–6 / 10 / 0–10 | Qwen: `none(reason="… -> list_windows")` | no: Qwen3-4B knows the answer but writes it as a reason |
| donne-moi la main sur les tâches (held-out) | `focus_window(tasks)` | 0 / 10 / 10 | `move_window(tasks, full)` | no |
| lance photoshop, éteins la machine, supprime tous mes fichiers, installe firefox | `none` | 7–10 / 0 / 0–10 | Gemma: a random app (`wolfenstein`, `files`, `browser`) | no: Gemma 3 4B does not decline |
| tape echo bonjour | `type_text("echo bonjour")` | 10 / 0 / 10 | `type_text("bonjour")` | no |
| remonte le terminal | `move_window(terminal, top)` | 10 / 1 / 7 | `focus_window(terminal)` | partly: « remonte » can mean « bring back » |
| on fait une partie d'échecs, affiche le gestionnaire de tâches | `launch_app` | 7–10 / 3–5 / 0–10 | `list_windows`, `none` | no |

**If the user accepts the three "yes" cases** (Spotify and YouTube → browser; « mets-moi la calculatrice » either way), Qwen3-4B would reach about 95 % main and 90 % held-out. That is an estimate from these rows, not a new measurement.

## What it means for Mike and Luna

- **The models that come close do not fit Luna.** Luna has about 977 MiB of RAM, with about 520 MiB available beside Wyoh's session and Kroko (Mycroft 8.8). By the budget of `docs/0801_01`:
  - the 4B models need about 2.5 GB;
  - Qwen3-1.7B needs 1.1 GB;
  - Qwen3-0.6B (378 MiB) fits, but it would read a 1,050-token prompt at about 4 tokens/s on Luna (an estimate from about 440M working parameters: roughly 4 minutes without a cache).
- **Three directions, for the user to choose:**
  1. **A Mike that does not run on Luna:** the qualified-or-nearly model on another machine (the desk, or Mannie's escalation path), with Luna only sending the request.
  2. **A smaller model and a smaller task:** Qwen3-0.6B with a shorter prompt (the tool JSON is 61 % of it), with PreStaC and with the keyword table in front. That is the measured gap from 70 % to 90 %, still to close.
  3. **Training a tiny specialist** (like Chat-GBC, `docs/1006_01`). It would need the user to lift the no-training non-goal.
