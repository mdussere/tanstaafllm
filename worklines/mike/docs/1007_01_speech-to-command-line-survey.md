# Survey — speech or natural language to a command line, with a small trained model

**Question answered:** has someone already built "speech to command line" or a small model trained on natural-language-to-bash, and what does it say about training a narrow model for Mike?<br>
**Date:** 2026-10-30<br>
**Status:** web survey only; nothing downloaded, run or trained. Figures are the authors' own, not measured here (user request, 2026-10-30: "find speech to command line; some geek must have done it").

## Summary

- **Speech to command line exists, but only as glue:** speech recognition, then a local model that proposes a command, then a confirmation. No project found trains a model for voice requests specifically.
- **Natural language to bash, with a small fine-tuned model, has been done several times:** public training data (about 41,000 pairs), a public benchmark, and fine-tunes from 60M to 1B parameters.
- **Fine-tuning helps small models a lot, but open-ended bash stays far from 90 %:** about 27–51 % for 0.5B–3B models on the MIT benchmark, 57 % for a 270M Gemma (one blog post).
- **For Mike, this argues for a narrow task:** a closed list of commands or tool calls, not all of bash. Chat-GBC (`1006_01`) shows that a trained specialist recites its own task well and generalises poorly to new phrasings, so the held-out set must stay the judge.

## Projects found

| Project | What it is | Model | Reported result | Notes |
| --- | --- | --- | --- | --- |
| [nl2shell/vox](https://github.com/nl2shell/vox) | "Talk to your terminal": spoken or typed request → shell command, asks "Run it? [Y/n/c]" | NL2Shell (below), through Ollama | none | Closest to "speech to command line"; speech engine not named; 0 stars; MIT |
| [nl2shell/nl2shell](https://github.com/nl2shell/nl2shell) | Qwen3.5-0.8B fine-tuned (QLoRA) on about 11,900 NL→bash pairs | 0.8B, GGUF Q4_K_M about 400 MB | "pending" | Claims "runs on a Raspberry Pi 4" but asks for Pi testers; 1 star; MIT; weights [AryaYT/nl2shell-0.8b](https://huggingface.co/AryaYT/nl2shell-0.8b) |
| [BashGemma](https://jajags-tech.pages.dev/research/bashgemma) | FunctionGemma 270M + LoRA, 9,153 examples, 36 min on a MacBook M4 Max | 270M, about 540 MB | 4.5 % → 57.4 % (NLC2CMD metric), about 32 % exact | One blog post; weights [thinkthink-dev/bashgemma-270m](https://huggingface.co/thinkthink-dev/bashgemma-270m); FunctionGemma 270M is already in Mike's assets |
| [codet5-small-nl2cmd](https://huggingface.co/diethylene/codet5-small-nl2cmd) | CodeT5-small on NL2SH-ALFA + tldr-pages + synthetic | 60M | none | Apache-2.0; "will happily issue destructive commands" |
| [T5-nl2cmd](https://huggingface.co/Edoigtrd/T5-nl2cmd), [byt5-small English-to-BASH](https://huggingface.co/kevinum/byt5-small-finetuned-English-to-BASH) | T5 fine-tunes on nl2bash and tldr | about 250M / 300M | T5: exact match 6.4 % | Older seq2seq approach |
| [talk-llama](https://news.ycombinator.com/item?id=37228889) ([fast fork](https://github.com/Mozer/talk-llama-fast)), [offline-voice-chat](https://github.com/simplay/offline-voice-chat) | whisper.cpp or Moonshine + llama.cpp voice assistants | any GGUF | none | Voice chat, not command generation; the usual building blocks |

## Research results

**Westenfelder et al., MIT ALFA, NAACL 2025** ([arXiv 2502.06858](https://arxiv.org/html/2502.06858v1); data [NL2SH-ALFA](https://huggingface.co/datasets/westenfelder/NL2SH-ALFA)): 40,939 training pairs (nl2bash, NL2CMD, LinuxCommands, text_to_bash, tldr-pages), 600 hand-checked test pairs, execution-based scoring. LoRA on one RTX A6000. Accuracy on InterCode-ALFA:

| Model | Base | Constrained decoding | Fine-tuned (LoRA) |
| --- | --- | --- | --- |
| Qwen2.5-Coder-0.5B | 0.10 | 0.05 | **0.27** |
| Llama-3.2-1B | 0.12 | 0.19 | **0.37** |
| Qwen2.5-Coder-1.5B | 0.21 | 0.06 | 0.19 |
| Llama-3.2-3B | 0.17 | 0.39 | **0.47** |
| Qwen2.5-Coder-3B | 0.26 | 0.06 | **0.51** |

**Jacobs, Lapon, Naessens, KU Leuven, LAST-X 2026** ([PDF](https://www.ndss-symposium.org/wp-content/uploads/lastx2026-49.pdf), [code](https://github.com/JefJacobs00/Local-LLMs-4-Bash)): 22 open models from 1B to 32B, no fine-tuning, 10 prompting styles, majority of 3 attempts must succeed. Smallest tier (simple prompt): Qwen2.5-1.5B 0.44, Llama-3.2-1B 0.21; Qwen3-4B 0.73; best overall about 0.80 (Qwen3-14B). Role-play prompts help small models; chain of thought and retrieval often hurt them.

## Mike's own measure

Mike's 8.0c one-liner test (`plan_mike.md`, 2026-10-25): five everyday requests on nine desk models, untrained. Disk usage (`df -h`) is right almost everywhere; the other four mostly fail; 10/20 at best (Gemma 3 1B, Qwen3-1.7B), 2–4/20 for LFM2.5-350M.

## Game Boy against Luna (user question, 2026-10-30)

| | Game Boy DMG (Chat-GBC) | Luna (RK3326) | Ratio |
| --- | --- | --- | --- |
| CPU | Sharp SM83, 8-bit, about 1.05 M cycles/s, no multiply | 4 × Cortex-A35, 64-bit, NEON (clock up to 1.5 GHz per Rockchip, not measured here) | about 6,000× in raw cycles |
| Measured model throughput | 62k parameters at about 2 s per token ≈ 30k parameter-tokens/s (Chat-GBC's `ARCHITECTURE.md`) | about 1.9 × 10⁹ parameter-tokens/s reading (`0801_01`) | about 60,000× |
| Working memory | 8 KiB work RAM + up to 128 KiB cartridge SRAM | about 450–550 MiB available with the desktop and dictation | about 4,000× |
| Weight storage | up to 8 MiB ROM (int7) | the SD card; RAM is the limit | — |
| Model size used | 62k–136k parameters | 350M runs (about 300 MiB RSS) | about 2,500–5,500× |

Chat-GBC trains from scratch because nothing pre-trained exists at 62k parameters with a 255-token vocabulary that fits a ROM bank. Luna's room is 10–350M parameters, where pre-trained small models exist (LFM2.5-230M/350M, FunctionGemma 270M, SmolLM2-135M, CodeT5-small 60M); fine-tuning one of them is the natural route there. A fine-tuned model also needs no long instruction prompt: a request of about 10 tokens (plus about 20 of chat template) and an answer of about 15 would take an estimated 6–9 s on Luna for a 350M model (6.7 tokens/s read, 3.6 written, `0405_01`), less for a 135M one, against about 105 s with prompt v4; not measured.

## What it means for Mike

1. **Training is the only route that has moved small models a lot** on this task (0.10 → 0.27 at 0.5B; 0.045 → 0.57 at 270M), with modest hardware (a laptop, one workstation GPU, 0.5–4 h).
2. **Open bash is too wide for the 90 % gate.** The narrower the output space (Mike's six tool calls, or a closed catalogue of one-liners with slots), the closer a small model can get; a grammar can still force the output into that catalogue.
3. **The data exist:** NL2SH-ALFA (MIT licence per its card), tldr-pages (CC BY 4.0), nl2bash; French phrasings would have to be generated.
4. **Training is outside Mike's scope today** ("no training of any kind"). This survey does not change that; only the user's explicit decision does, followed by a planned, green-lit step.
