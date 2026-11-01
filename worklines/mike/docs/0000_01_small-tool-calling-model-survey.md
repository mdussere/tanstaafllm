# Small tool-calling model survey (desk research)

> **Freshness:** 🟡 historical · **Written:** 2026-10-13 · **Checked:** 2026-10-31

**Question answered:** which local language models of at most about 400 MB could let Mike turn a typed or dictated French request into a Wyoh MCP tool call, and what must be measured before choosing one?<br>
**Date:** 2026-10-09<br>
**Status:** desk research only. Nothing was downloaded or run. File sizes come from the Hugging Face file listings on 2026-10-09; capability claims come from model cards and vendor posts and are **not verified** here.

## The constraint

| Item | Recorded value | Source |
| --- | --- | --- |
| Luna CPU | Rockchip RK3326, four Cortex-A35 cores (ARMv8.0-A: NEON, no dot-product instructions) | `worklines/luna/docs/0508_03`, `worklines/wyoh/docs/0405_01` |
| Luna RAM | `MemTotal: 1,000,004 kB` (about 977 MiB), no swap on the stock card; zram 512 MiB–1 GiB planned | `worklines/wyoh/docs/0405_01`, `worklines/luna/docs/0000_07` |
| Mycroft peak RSS | 218.7 MiB on x86_64 (Sherpa console) | `docs/LOGBOOK.md`, 2026-10-09 |
| `luna-pi` | Raspberry Pi 4B, Cortex-A72, about 8 GiB | `worklines/luna/docs/0101_01` |
| User budget | model file 300–400 MB at most | user, 2026-10-09 |

Mycroft plus a 400 MB model plus Sway is already most of Luna's RAM. Running both at the same time is not a safe assumption. Loading one model at a time, on demand, is the default hypothesis.

On a Cortex-A35, **reading the prompt** is likely to cost more than writing the answer: every tool schema in the prompt is processed before the first output token. The Wyoh MCP server exposes about 27 tools today. Giving all of them to a small model is probably too slow and too confusing. A short, curated tool list is the main design lever (see the intent, `0101_01`).

## Candidates

| Model | Params | GGUF Q4_K_M | Q4_0 | Q8_0 | Tool calling (claimed) | French (claimed) | Licence | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **LiquidAI LFM2.5-230M** | 230M | 146.3 MiB | 142.2 MiB | 235.2 MiB | yes, "built for agentic tasks", RL-refined for tool use | listed | LFM Open License v1.0 (to review) | Hybrid conv + attention: smaller KV cache, faster decode than a same-size transformer. Pythonic tool calls between special tokens. |
| **LiquidAI LFM2.5-350M** | 350M | 218.7 MiB | 209.2 MiB | 361.7 MiB | yes; card recommends it for structured output and tool use, not for knowledge or code | listed | LFM Open License v1.0 (to review) | Same family; Q8_0 still fits the budget. |
| **Google FunctionGemma 270M** | 270M | 241.4 MiB | 230.4 MiB | 278.1 MiB | yes, the model's only purpose | not verified | Gemma terms | Released Dec 2025 as a base for fine-tuning: Google reports 58 % out of the box, 85 % after fine-tuning on its Mobile Actions task. Own call format (`<start_function_call>call:name{…}<end_function_call>`). Repository gated. |
| **Qwen3-0.6B** | 0.6B | 378.3 MiB | 364.5 MiB | 609.8 MiB | yes (Hermes-style `<tool_call>` JSON) | multilingual | Apache 2.0 | At the edge of the budget at 4 bits. Has a "thinking" mode that must be turned off for latency. |
| Qwen3.5-0.8B | 0.8B | 507.8 MiB | 483.7 MiB | 774.2 MiB | yes | multilingual | Apache 2.0 (to confirm) | **Over budget.** Kept only as an upper reference on the desk host. |

Rejected without measurement: anything above about 1B parameters (does not fit with Mycroft), and SmolLM2-135M/360M (no tool-calling training claimed; English-first).

## Techniques that matter more than the model

1. **Constrained decoding.** llama.cpp can force output to match a grammar (GBNF) or a JSON Schema. With it, a small model can only produce a well-formed call to one of the offered tools. The open question is whether it picks the *right* tool and arguments.
2. **A short tool list with short descriptions.** Five to eight tools, each with one or two arguments, instead of the full Sway IPC surface.
3. **Prompt caching.** The fixed part of the prompt (system text + tool list) can be computed once and its KV state reused, so each request pays only for the user's words.
4. **Fine-tuning as a later step.** FunctionGemma's published numbers suggest a small model gains a lot from a task-specific fine-tune. This is a possible later step, not the first one.
5. **Rules first.** Some requests ("ouvre la calculatrice") may be handled by a keyword table without any model. The least sufficient mechanism should be measured too.

## What must be measured (not claimed)

- Accuracy on a French request → expected tool call set, with and without constrained decoding.
- Prompt tokens of the curated tool list, and time to first token.
- Peak RSS and load time on the desk host, then on `luna-pi`.
- Luna figures only when Luna is in scope; `luna-pi` (Cortex-A72) is faster than Luna and cannot stand in for it.

## Sources

- File sizes: Hugging Face API, `LiquidAI/LFM2.5-230M-GGUF`, `LiquidAI/LFM2.5-350M-GGUF`, `unsloth/functiongemma-270m-it-GGUF`, `unsloth/Qwen3-0.6B-GGUF`, `unsloth/Qwen3.5-0.8B-GGUF` (queried 2026-10-09).
- [LFM2.5-230M model card](https://huggingface.co/LiquidAI/LFM2.5-230M), [LFM2.5-350M model card](https://huggingface.co/LiquidAI/LFM2.5-350M), [vLLM recipe for LFM2.5-350M](https://recipes.vllm.ai/LiquidAI/LFM2.5-350M).
- [FunctionGemma announcement](https://blog.google/technology/developers/functiongemma/), [InfoQ on FunctionGemma](https://infoq.com/news/2026/01/functiongemma-edge-function-call).
- [bartowski Qwen3-0.6B GGUF](https://huggingface.co/bartowski/Qwen_Qwen3-0.6B-GGUF).
