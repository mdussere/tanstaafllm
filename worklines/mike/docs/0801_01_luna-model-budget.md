# Step 8.1 — what Luna allows a model: the measured budget

> **Freshness:** 🟡 historical · **Written:** 2026-10-30 · **Checked:** 2026-10-31 · **Step:** mike 8.1 ✅

**Question answered:** how big can a model be, and how many tokens can it read and write per decision, for Mike to answer in about 1 s, 5 s or 10 s on Luna?<br>
**Date:** 2026-10-25<br>
**Status:** derived from two measurements on Luna (`docs/0405_01`, 4.5 and 4.6). The scaling to other models is an **estimate**, to be checked by measuring each candidate (4.6's test works for any GGUF model).

## What was measured on Luna (Cortex-A35 ×4, 4 threads)

| Model | File | Reading the prompt | Writing |
| --- | --- | --- | --- |
| LFM2.5-350M Q4_0, llama.cpp b11429 | 219 MB | 6.5–6.9 tokens/s (about 150 ms per token) | 2.8–3.6 tokens/s (about 300 ms per token) |

- **Model size:** LFM2.5-350M has about 350M parameters. About 67M of them are the vocabulary table (65,536 × 1,024), which costs memory but almost no computation. That leaves **about 283M "working" parameters**.
- **Reading cost:** 283M × 6.7 tokens/s ≈ **1.9 billion parameter-tokens per second**.
- **Writing cost:** writing one token reads the whole weight file once: 219 MB × 3.6 tokens/s ≈ **0.8 GB/s**.
- **Memory:** about 300 MiB of server RSS. `MemAvailable` stayed between about 450 and 560 MiB with Wyoh's session and the resident Kroko running, and was about 720 MiB just after a reboot.

## Rule of thumb (estimate, for llama.cpp-like runtimes on this CPU)

- **Reading N tokens with P working parameters:** about **N × P / 1.9 × 10⁹ seconds**.
- **Writing M tokens with a weight file of S bytes:** about **M × S / 0.8 GB/s seconds**.
- **Caveats:**
  - Small models usually run less efficiently per parameter, so these figures are optimistic for them.
  - An ONNX runtime will differ, by a factor that is unknown until measured.

## What each budget allows

**Per decision, with a 30-token request and the fixed part of the prompt restored from a saved state:**

| Budget | Generative model (reads 30, writes 10 tokens) | Classifier, one pass (text + labels about 60 tokens) | NLI cross-encoder (one pass per label, 10 labels × about 40 tokens) |
| --- | --- | --- | --- |
| 1 s | about **25M** working parameters, file under about **40 MB** | about **30M** working parameters | about **5M** working parameters |
| 5 s | about 150M, file under about 200 MB | about 150M | about 25M |
| 10 s | about 300M, file under about 400 MB | about 300M | about 50M |

**What follows:**
- **Mike's 1-second budget.** Only a model of a few tens of millions of working parameters can meet it, and only if almost nothing but the request is read each time. A decision model that reads the request once (GLiClass-style) fits better than a generative model, which must also write its answer token by token.
- **NLI-style zero-shot classifiers** (one pass per label) are about ten times too slow, unless their working part is tiny.
- **Large vocabularies are cheap in time but not in memory:** a multilingual 250,000-token vocabulary costs RAM, not reading time.
- **LFM2.5-350M on Luna** fits a 10-second budget at best, and only with the restored prefix. Without it, a 1,000-token prompt takes about 160 s, as measured.

## How to use this table

- **Before measuring:** a candidate is worth measuring when its working parameter count and its file size fall inside the column of the chosen budget.
- **When measuring:** measure it on the desk, then on Luna with the 4.6 test (`test/mike/test_raw_speed.py`), before anything else.
