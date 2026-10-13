# Step 3 intent — which small models, how big, how much memory

**Question answered:** which three models do we test first, what will they cost in file size and RAM, and how is the first test run?<br>
**Date:** 2026-10-09<br>
**Status:** shortlist proposed; Step 3 green-lit by the user ("go", 2026-10-09). RAM figures below are **estimates** from each model's published architecture; the measured figures are in `0302_01`.

## Budget

- Model file: 300–400 MB at most (user).
- Luna has about 977 MiB of RAM in total, and Mycroft already peaks at about 219 MiB. A model that needs more than about 300 MiB of RAM in use is unlikely to live next to Mycroft and Sway.

## How memory adds up

RAM in use ≈ **model weights** (the GGUF file, memory-mapped) + **KV cache** (grows with the context length) + **compute buffers** + the runtime itself.

The KV cache is the hidden cost. It depends on how many layers use attention, and on their size:

| Model | Attention layers | KV per token (f16) | KV at 2,048 tokens | KV at 4,096 tokens |
| --- | --- | --- | --- | --- |
| LFM2.5-230M | 6 of 14 (the rest are short convolutions with a tiny fixed state) | 12 KiB | 24 MiB | 48 MiB |
| LFM2.5-350M | 6 of 16 | 12 KiB | 24 MiB | 48 MiB |
| FunctionGemma 270M | 3 full + 15 sliding-window (512 tokens) | 3 KiB + fixed 7.5 MiB | 13.5 MiB | 19.5 MiB |
| Qwen3-0.6B | 28 of 28 | **112 KiB** | **224 MiB** | **448 MiB** |

Computed from each model's `config.json` (layers, KV heads, head size), K and V in 16-bit.

A short tool list and one request should fit in about 1,000–2,000 tokens, so 2,048 is the working context.

## The models

| | LFM2.5-350M | LFM2.5-230M | FunctionGemma 270M | Qwen3-0.6B |
| --- | --- | --- | --- | --- |
| Maker | Liquid AI | Liquid AI | Google | Alibaba (Qwen) |
| File, Q4_K_M | 218.7 MiB | 146.3 MiB | 241.4 MiB | 378.3 MiB |
| File, Q8_0 | 361.7 MiB | 235.2 MiB | 278.1 MiB | 609.8 MiB |
| Estimated RAM in use, Q4_K_M, 2,048 tokens | ≈ 270–300 MiB | ≈ 190–220 MiB | ≈ 280–310 MiB | ≈ 640–700 MiB |
| Tool calling | trained for it; recommended for "data extraction, structured outputs, tool use" | distilled from 350M, RL-refined "for agentic tasks" | its only purpose, but made to be fine-tuned: 58 % out of the box on Google's task | trained for it |
| French | listed | listed | not stated | multilingual |
| Architecture | hybrid convolution + attention, built for CPUs | same | Gemma 3; 168M of its 270M parameters are the 262k-word vocabulary table | plain transformer |
| Licence | LFM Open License v1.0 | LFM Open License v1.0 | Gemma terms | Apache 2.0 |
| Call format | Python-like call between special tokens | same | own special-token format | JSON in `<tool_call>` |

The RAM estimate is file + KV + about 30–50 MiB of buffers and runtime. It is a prediction to check, not a result.

**Measured (2026-10-09, desk host, `0302_01`):** the KV estimate was right, but the total was not: 365–580 MiB peak, because of repacked weights, the compute buffer and the Python wrapper.

## Shortlist: the three to test

1. **LFM2.5-350M — the best candidate, tested first.** Within budget even at Q8_0, built for tool use and for CPUs, French listed, small KV cache. Its hybrid design should also make it the fastest of its size on Luna's weak cores.
2. **LFM2.5-230M — the fallback if 350M is too heavy or too slow.** Same family and format, two thirds of the size. Tells us how much accuracy we lose by going smaller.
3. **FunctionGemma 270M — a different maker and approach.** Specialised in function calls only. Weak out of the box by Google's own figure, so it shows whether a fine-tuning step would be worth it later.

**Not shortlisted: Qwen3-0.6B.** The file fits (378 MiB at Q4_K_M), but its KV cache is about ten times larger (112 KiB per token): about 650 MiB of RAM in use at 2,048 tokens. That is two thirds of Luna, so it is not worth it for Luna. It may still be run once on the desk host as a reference for accuracy.

The licences (LFM Open License, Gemma terms) are to be read before a final choice; they do not block testing.

## How the first test is run

- **Where:** the desk host only (Intel i5-4590, four cores, AVX2). No `luna-pi`, no Luna.
- **Runtime:** llama.cpp through its Python binding `llama-cpp-python`, in an optional uv dependency group `mike`, so other worklines do not build it.
- **Files:** downloaded to `/data/michael/tanstaafllm/mike-assets/` (outside the repository), with SHA-256 recorded.
- **First test (3.2a):** LFM2.5-350M Q4_K_M only.
  - Load the model in a separate process; measure load time and peak RSS (`VmHWM`).
  - Give it the intent's tool list and a dozen short French requests. Check: the right tool, the right arguments, and `none` when nothing fits.
  - Record prompt tokens, time to first token and total time per request.
  - Results under `results/mike/model-comparison/<timestamp>/`.
- **Then:** the same on LFM2.5-230M and FunctionGemma 270M, and the full evaluation set of Step 2 when it exists.

The dozen requests are a smoke set, not the evaluation set: they show whether the model works at all, not how well.
