# Step 3.7 — how much RAM does Mike really need?

> **Freshness:** 🟡 historical · **Written:** 2026-10-13 · **Checked:** 2026-10-31 · **Step:** mike 3.2 ✅

**Question answered:** the user finds about 500 MiB far too much. How much of it is the model, and how much is avoidable overhead?<br>
**Date:** 2026-10-11<br>
**Status:** measured on the desk host (x86_64) only. Evidence: `results/mike/lean-memory/20261011T100738Z/summary.jsonl`; test `test/mike/test_lean_memory.py` (`integration`). Three requests per run, prompt v4, constrained, context 2,048.

| Model | Setting | Peak RSS | Peak minus Python (≈ 50 MiB) | Of which the model file (memory-mapped) | Allocated (incl. Python) |
| --- | --- | --- | --- | --- | --- |
| LFM2.5-350M | default (repacked weights, batch 64) | 489 MiB | 439 MiB | 238 MiB | 234 MiB |
| LFM2.5-350M | **lean** (no repack, batch 16) | **351 MiB** | **301 MiB** | 240 MiB | 92 MiB |
| LFM2.5-230M | default | 361 MiB | 311 MiB | 164 MiB | 173 MiB |
| LFM2.5-230M | **lean** | **263 MiB** | **213 MiB** | 168 MiB | 92 MiB |

- **"Lean"** turns off llama.cpp's repacked copy of the weights (`use_extra_bufts = False`) and uses a batch of 16 instead of 64. The repacked copy is an x86 speed layout. Whether llama.cpp makes one on Luna's Cortex-A35 depends on CPU features it lacks (no dot-product); to check on the device.
- **The cost of lean on x86:** about 1.5–2 times slower (3–6 s per request here, on a shared host).
- **The answers can change:** lean LFM2.5-230M answered `focus_window` instead of `none` to "quel temps fera-t-il demain", because the different kernels give slightly different numbers. Accuracy must be measured in the lean setting, not assumed.
- **Without Python** (a C runtime such as `llama-server` or `llama-cli`), about 50 MiB less again. Expected: **~300 MiB for 350M and ~215 MiB for 230M.** That is a hypothesis to measure on Luna.
- **File-backed memory** (the model file) can be dropped by the kernel under pressure and read back from the card, at the cost of speed.
- **Smaller still:** LFM2.5-230M is the smallest model found with tool-calling training (`0000_01`). Below it, the options are the keyword table alone (no RAM) or loading the model only when the table is unsure, and unloading it afterwards.
