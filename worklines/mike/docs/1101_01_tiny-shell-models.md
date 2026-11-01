# Step 11 — Rudy's tiny models trained on natural language → shell

> **Freshness:** 🟡 historical · **Written:** 2026-10-31 · **Checked:** 2026-10-31 · **Step:** mike 11.1 ✅

**Question answered:** do Chat-GBC's tiny and micro models, trained from scratch on the NL2SH-ALFA pairs, give usable shell commands, and how does that compare with LFM2.5-350M untrained?<br>
**Date:** 2026-10-31<br>
**Status:** measured on Termidor (CPU only). User request, 2026-10-30: "do the experiment anyway".

- **Code:** Chat-GBC `db83f9b` with a tokenizer that keeps case and every printable ASCII character (`test/mike/chat_gbc_nl2sh.patch`); configurations `tiny-sh` and `micro-sh` keep Rudy's layer sizes and still fit his ROM-bank limits.
- **Tests:** `test/mike/test_chat_gbc_nl2sh.py` with `chat_gbc_nl2sh_eval.py` (`chat_gbc_nl2sh.feature`); `test/mike/test_nl2sh_baseline.py` (`nl2sh_baseline.feature`).
- **Evidence:** `results/mike/chat-gbc-nl2sh/20261030T223755Z/` and `results/mike/nl2sh-baseline/`. Checkpoints under `mike-tools/chat-gbc/runs/`, dataset under `mike-assets/datasets/NL2SH-ALFA/` (MIT licence), neither in the repository.

## Method

- **Training data:** 39,549 NL2SH-ALFA training pairs; 1,090 longer than 250 characters (request + command) dropped because they do not fit a 112–128-token context.
- **Recipe:** Rudy's, unchanged: subword vocabulary learned from the data, 12,000 pre-training steps, then 8,000 fine-tuning steps on the answers, batch 32. His question augmentation is off: it removes punctuation, words and sentence ends that carry a command's paths and arguments. 2 threads each, both runs in parallel.
- **Test:** the 300 NL2SH-ALFA test requests, each with two accepted commands (the paper counts 600 pairs), asked once, greedy.
- **Measures:** exact match against either command (spaces squeezed), same first word as either command, character error rate. Exact match undercounts: an equivalent command written differently counts as wrong. The paper judges by running the commands.

## Results

| Model | Parameters | Training time | Exact | Right first command | Mean character error |
| --- | --- | --- | --- | --- | --- |
| Chat-GBC tiny-sh, trained | 66,000 | 35 min (2 threads) | **0/300** | 106/300 | 1.17 |
| Chat-GBC micro-sh, trained | 136,640 | 57 min (2 threads) | **1/300** | 104/300 | 1.09 |
| LFM2.5-350M Q4_0, untrained | 350M | — | **6/300** | 22/300 | 0.86 |
| same, its leading `sudo` removed | | | 11/300 | 83/300 | |

- **The tiny models answer by habit, not by meaning.** tiny answers `find` 119 times and micro 115 times; `find` is the expected command of 109 requests, so most of their "right first command" comes from that. Examples (micro): "list files in the current directory" → `find . -name "*.*"`; "create a directory /testbed/test_dir" → `create -r /test_name/test_temp_dir/…`.
- **Losses stay high:** about 2.0 (tiny) and 1.7 (micro) at the end of each phase, against Rudy's 0.2 on 405 Game Boy facts. A loss of 2 means about 14 % average probability on the right next token (e^-2).
- **LFM2.5-350M untrained:** puts `sudo` in front of 158 answers and invents commands (`sudo filelist`); its 6 exact answers are all easy (`date`, `mkdir /testbed/test_dir`). 203 s for 300 requests on 2 threads.
- **For scale (published, not measured here):** fine-tuned with LoRA, Qwen2.5-Coder-0.5B reaches 27 % and Llama-3.2-1B 37 % on the paper's execution-based measure (`docs/1007_01`).

## What it means for Mike

1. **At 66k–137k parameters, trained from scratch, open bash is out of reach:** 0–1 exact out of 300. More steps would lower the loss somewhat; the gap to Rudy's 0.2 is the gap between memorising 405 answers and generalising over 40,000 different commands.
2. **An untrained 350M model is not better at exact commands** (2–4 %). Training a pre-trained model is the remaining route; Termidor's GPU (GTX 760, Kepler, nouveau driver) cannot be used, and a LoRA pass of LFM2.5-350M over 40,000 pairs is estimated at 6–10 h on its CPU (not measured).
3. **The user's narrower ideas remain open, not tested:** one tiny model per command class behind a router, man or tldr pages as pre-training text, a light FR→EN translator before the model. A narrow class (for example only `find`, or Mike's six tool calls) is the setting where a model of Rudy's size could memorise enough.
