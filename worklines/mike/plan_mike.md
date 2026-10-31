---
**Status**: 📋 Draft
**Date**: 2026-10-09
**Priority**: Medium
**Maintained**: Yes
---

> **Renamed on 2026-10-11 (user decision, back to the original vocabulary).** From 2026-10-09 to 2026-10-11, the two lines had inverted names: this directory was `worklines/mannie/`. The user restored the original split of the initial discussion (`worklines/professor/docs/0001_01_initial_discussion.md`, lines 2926 and 3006–3024): **Mike is the local brain on Luna, and Mannie is the frontier-model capability.** Professor swapped every name in this directory, its tests, and its code, including earlier time-log rows. Session names in old rows are the names at the time: the user kept both sessions and swapped their names (session [5832e9] is now `mike`, session [11ad42] is now `mannie`). User quotes from that period were reworded to fit the new names.

# Mike — small local model that drives Wyoh through MCP (workline `mike`)

## Overview

Today the Wyoh command line talks to Luna's desktop through the Wyoh MCP server, and that works. The user wants to talk to the machine instead: speak through Mycroft, have Mycroft pass the accepted text to **Mike**, and have Mike use the Wyoh MCP server to act on the desktop.

Mike is a **small local language model** (model file 300–400 MB at most) with just enough skill to choose one Wyoh action from a short list. This workline finds out whether such a model exists and is good enough, first on the desk host, then on `luna-pi`. It does not touch Luna.

Done means: a measured choice of model (or a measured "not good enough"), and a `mike-console` on the desk host that turns a typed French request into one proposed Wyoh action, runs it only after the user accepts, and has been checked against the real Wyoh MCP server on `luna-pi`.

## Naming

**Mike** is the small local model on Luna that proposes Wyoh actions through MCP. **Mannie** is the frontier model (Claude, Codex, …) reached remotely: requests too hard for Mike escalate to Mannie. This is the original vocabulary of the initial discussion, restored by the user on 2026-10-11 after two days of inverted names (D1 in `worklines/professor/docs/0503_01`, reverted by D16).

## Workline directory layout

- Plan (this file): `worklines/mike/plan_mike.md`
- Produced docs: `worklines/mike/docs/`
- Tests and experiments: `test/mike/` (`mike_bench.py`, `test_mike_bench.py`, `test_model_smoke.py`, `model_smoke.feature`; Step 3b: `mike_server.py`, `test_server_runtime.py`, `mike_harness.py`, `test_micro_harness.py`, `mike_fake_mcp.py`)
- Runtime and harness binaries: `/data/michael/tanstaafllm/mike-tools/` (official releases, outside the repository)
- Results: `results/mike/<topic>/<timestamp>/` (not committed)
- Code: `src/mike/mike_contract.py` (contract and adapter, Step 2)
- Model files: outside the repository, never committed

## Goals ✅

- Choose, by measurement, a local model of at most about 400 MB that maps short French requests to the right Wyoh action.
- Give the model a short, safe, task-level tool list, mapped by Mike's adapter onto the existing Wyoh MCP tools.
- Build `mike-console`: typed request → proposed action → user accepts → Wyoh MCP → honest result.
- Measure accuracy, time to first token, total time and peak RSS on the desk host and on `luna-pi`.
- Design the hand-off from Mycroft (accepted text in) and to Mannie (escalation out), without building them yet.

## Non-goals ❌

- Any work on Luna (the R36 Ultra): no SSH, no deployment, no measurement. `luna-pi` is the furthest target. **Exception:** the supervised first run of 4.5 (user, 2026-10-25), within its scope.
- Changing the Wyoh MCP server, Mycroft, or Luna's image. Requests to them go as notes.
- Raw Sway commands or free-text `exec` from the model.
- Multi-step agent loops, a resident service, speech output, Mannie integration.
- **Any training: no fine-tuning, no retraining, no training dataset** (user, 2026-10-13, `docs/0700_02`). Pre-trained models only, zero-shot; a model that does not work as is gets dropped, not trained. **Lifted for Step 11 only** (user, 2026-10-30: "do the experiment anyway"): training experiments on the desk host; nothing trained goes to Luna without a new decision.
- **Translation between languages** (user, 2026-10-13): the language is chosen at the input; French or English end to end.
- GPU/OpenCL acceleration, unless there is evidence of at least 2× end to end (user, 2026-10-13: not a preferred hypothesis).
- Renaming components in shared documents.

## Key decisions / assumptions

- **Qualification gate (user, 2026-10-29): no model is used, optimised or run on Luna before it is qualified.** "Before we even think about optimisation, I need a stable performance of something like 90 % on our cases, which are very simple, to think of using Mike." LFM2.5-350M is **not qualified** (best 55/81 main and 16/31 held-out, one draw, unstable: another quantisation changes about 40 % of its answers). Qualifying a model is the priority (Step 10); PreStaC 9.3 and 9.4 wait.
- **LFM2.5-350M is not usable on Luna as it is** (user, 2026-10-25, after 4.5 and 4.6: about 105 s per request; 6.5–6.9 prompt tokens/s). Luna is left to Mannie; Mike goes back to desk studies (Step 8).
- **Model (desk host): LFM2.5-350M** (user decision, 2026-10-11: "350 is impressive and fast"; a big difference from 230M; about 350 MiB is acceptable for now; slim down later).
- One call per request; the user accepts every action before it runs.
- **Mike does one action per order** (user, 2026-10-13): no autonomous planning or composition. A decider may **select a predefined plan** by case; selecting is not planning.
- **English is allowed** if it makes Mike lighter or better and if the English speech-to-text handles the user's accent (Mycroft's evaluation). French is a bonus, not a requirement.
- **Decision latency budget on Luna** (user, 2026-10-13): < 200 ms excellent, ≤ 500 ms acceptable, < 1 s tolerated, per decision and as a function of the number of classes. Embedding-similarity scores are not accepted as decisions; at most as a pre-filter.
- No Adam for now (user, 2026-10-09): Mike reports to the user directly.
- The adapter, not the model, writes Sway commands, from fixed templates with checked arguments.
- Constrained decoding (llama.cpp grammar / JSON Schema) is the default; results without it are kept for comparison.
- llama.cpp (through its Python binding or `llama-server`) is the default runtime: it runs GGUF on ARM CPUs. To confirm in Step 3.
- The tests use a fake Wyoh MCP server; the real one on `luna-pi` is used only in `live` tests.
- Rules before models: a keyword table is measured as the baseline the model must beat.

## Risks / constraints

- **Luna's RAM (about 977 MiB)** may not hold Mycroft and Mike at once. Plan for one model at a time; record both RSS figures.
- **Prompt reading is slow on a Cortex-A35.** Keep the tool list short; measure prompt tokens; test prompt caching.
- **`luna-pi` is not Luna.** A Cortex-A72 is much faster than a Cortex-A35. `luna-pi` numbers are an upper bound.
- **Small models are unreliable.** Out of the box FunctionGemma is reported at 58 % on Google's own task. The result may be "not good enough without fine-tuning"; that is a valid outcome.
- **Licences.** LFM models use the LFM Open License v1.0 and Gemma models the Gemma terms; check them before choosing.
- **Model downloads** are large and some are gated; they stay outside the repository.

## 🚦 Green light protocol

- Default: planning and documentation only until the user says **🟩 go Step N**.
- Model downloads start at Step 3. Any `luna-pi` access starts at Step 4.
- If scope changes materially, update this plan and `docs/LOGBOOK.md` first.

## Plan steps (no execution until green light)

### Step 0 — Workline set-up and desk research
**Status**: ✅ Done (2026-10-09, documentation only)
- [x] 0.1 Plan created; session registered in `worklines/agents.md`.
- [x] 0.2 Desk survey of small tool-calling models with verified file sizes (`docs/0000_01`).
- [x] 0.3 Intent of Mike v0 written (`docs/0101_01`).
- [x] 0.4 Naming conflict sent to Professor as a note.

### Step 1 — Intent and tool contract
**Status**: 🧪 Draft done, awaiting the user's approval (1.5) — 1.2–1.4 green-lit by Professor's decision **D13** on the user's behalf (2026-10-09 ≈22:50, desk host only; `worklines/professor/docs/0503_01`). Acceptance stays open: the user approves the contract on return.
- [x] 1.1 User reviewed the intent (`docs/0101_01`) on 2026-10-09: agreed with the diagram and the intent; Adam removed from the picture.
- [x] 1.2 Fix the curated tool list: names, arguments, allowed values, Wyoh MCP mapping, risk level of each. Draft: `docs/0102_01` (7 tools, adapter templates, refusals).
- [x] 1.3 Fix the launch allowlist (from Wyoh's menu entries, read-only) and the place names for `move_window`. Draft: 10 apps (5 available, 5 planned in Wyoh Step 9) from Wyoh's entries, read only; `top`/`bottom` → Sway `up`/`down`.
- [x] 1.4 Decide what Mike receives from Mycroft (plain accepted text, language tag) and what it sends to Mannie (request + reason), in writing only. Draft: contract section 4.
- [ ] 1.5 **User approval of the contract**, including the two ⚖️ items: "focus on a closed app → launch it" and relative `move_window` places.
- **Acceptance:** a tool-contract doc that the user approves; every tool maps to an existing Wyoh MCP tool, with no raw `sway_command` or free `exec` exposed to the model.

### Step 2 — Evaluation set and harness (no model yet)
**Status**: ✅ Done (2026-10-09, under D13). `uv run --group mike pytest test/mike -m "not live and not integration"`: 53 passed.
- [x] 2.1 Write 60–100 French requests with their expected call (including `none` cases, typos, Mycroft-style lower-case text without punctuation). Done: 81 main + 31 held-out (`docs/0201_01`).
- [x] 2.2 Write a fake Wyoh MCP server with a scripted desktop state, and the adapter's mapping tests. Done: `test/mike/fake_wyoh.py`, `src/mike/mike_contract.py`, `test/mike/test_mike_contract.py`.
- [x] 2.3 Write the scoring harness in `test/mike/` (right tool, right arguments, refused when it should be) with a model adapter seam.
- [x] 2.4 Score the keyword-rule baseline: 80/81 main (written on it, optimistic), **14/31 held-out**.
- **Acceptance:** `uv run pytest test/mike -m "not live and not integration"` passes with no model installed; the baseline score is recorded.

### Step 3 — Desk-host model comparison (done first)
**Status**: 🧪 In progress — green-lit by the user ("go", 2026-10-09)

The user chose to start here, before Steps 1 and 2: first see which models fit the memory budget, then build the contract and the full evaluation set. Until Step 2 exists, a smoke set of a dozen requests stands in for it.

- [x] 3.0 Step 3 intent: models, file sizes, estimated RAM, shortlist of three (`docs/0301_01`). Shortlist: **LFM2.5-350M** (first), **LFM2.5-230M**, **FunctionGemma 270M**. Qwen3-0.6B left out: its KV cache puts it at about 650 MiB of RAM.
- [x] 3.1 Add the optional uv group `mike` (`llama-cpp-python`); download the shortlisted GGUF files to `/data/michael/tanstaafllm/mike-assets/`, record their SHA-256. Done: `llama-cpp-python==0.3.36`; checksums in `mike-assets/SHA256SUMS` and `docs/0302_01`.
- [x] 3.2a Smoke test of LFM2.5-350M Q4_K_M: load time, peak RSS, a dozen French requests with the intent's tool list, constrained and unconstrained (`integration` marker).
- [x] 3.2b Same smoke test on LFM2.5-230M and FunctionGemma 270M. Result (`docs/0302_01`): best 6/13 (LFM2.5-350M), 5/13 and 4/13 for the others; peak RSS 365–580 MiB on x86, mostly repacked weights, compute buffer and Python, not the KV cache. None is good enough out of the box.
- [x] 3.2d Prompt v2: French verbs, the desktop state, six examples that are not smoke requests. LFM2.5-350M 6 → 10/13, LFM2.5-230M 5 → 9/13, FunctionGemma 4 → 4–5/13 (`docs/0302_02`).
- [x] 3.2e Constrained mode that can refuse: not needed for the smoke set; with prompt v2 the constrained mode chose `none` for both no-tool requests. To recheck on the Step 2 set.
- [x] 3.2f Prefix state save/restore: LFM2.5-350M 2.4 s → 0.21 s per request on the desk host, same answers, +54 MiB peak RSS with two saved states.
- [x] 3.2c Full evaluation sets on the LFM models (`docs/0302_03`): best LFM2.5-350M with prompt v4, constrained, 48/81 main and 16/31 held-out with the adapter rule. That barely beats the keyword table (14/31) on new phrasings. Not good enough yet.
- [x] 3.6 Option A measured on the saved answers (`docs/0302_04`): "keyword table first, model on app only", constrained, with the adapter: **20/31 held-out** (table 14, model 16) and 79/81 main; the model answers 15/31 held-out requests.
- [x] 3.7 Lean RAM (user: 500 MiB is too much) (`docs/0302_05`): no repacked copy and batch 16 → 350M 351 MiB peak (301 MiB above Python), 230M 263 MiB (213 MiB); slower on x86; answers can change. `mike_chat.py --lean`.
- [x] 3.9 LFM2.5-230M, lean, prompt v4, full sets (`results/mike/model-eval/20261011T102103Z/LFM2.5-230M-Q4_K_M.gguf.v4.lean.json`): constrained 37/81 main and 15/31 held-out (19 with the adapter); with the keyword table first, 21/31. On the tool task this is as good as 350M with v4 (38/81, 16/31, hybrid 20/31). The earlier weak 230M figures used prompt v3. The user's preference for 350M rests on its replies in conversation.
- [ ] 3.8 Vocabulary pruning (user's idea; proposed, not started).
  - Measured: both LFM models are text-only (not multimodal); vocabulary 65,536 tokens; the embedding is tied with the output layer, one 65,536 × 1,024 Q6_K matrix ≈ 52 MiB.
  - By writing system: ASCII 49,945; CJK/kana 4,907; Cyrillic 4,396; accented Latin 3,298; Hangul 1,038; Arabic 779; byte pieces 755; other 418.
  - Dropping CJK, Cyrillic, Hangul and Arabic (11,120 tokens, 17 %) would save ≈ 9 MiB of file and ≈ 17 % of the output layer's work per token. Re-quantising the embedding Q6_K → Q4_K would save ≈ 16 MiB more.
  - Needs tokenizer surgery and a GGUF rebuild, then re-measurement of accuracy.
- [ ] 3.5 **Decision for the user** (`docs/0302_03`, options): A keyword table first and the model second (fits Step 3); B LoRA fine-tuning of LFM2.5-350M (a new step, needs a green light); C two-stage call; D Mannie. Recommended: A, then B. A measured (3.6): adopt it as v0 routing, subject to the user's approval. **B is dropped** (user, 2026-10-13: no fine-tuning); the remaining choice is A, possibly with C or the Step 7 decider.
- [x] 3.3 Record accuracy, prompt tokens, time to first token, total time, peak RSS, load time; compare measured RAM with the estimates (`docs/0304_01`).
- [x] 3.4 Write the comparison and recommend one or two models (`docs/0304_01`): LFM2.5-350M (user decision), LFM2.5-230M as the fallback.
- **Acceptance:** results under `results/mike/model-comparison/<timestamp>/` and a doc in `docs/`; no claim about Luna.

### Step 3b — Lean runtime and micro-harness (proposed by the user, 2026-10-11)
**Status**: ✅ Done on the desk host (2026-10-15), awaiting the user's choice — green-lit by the user on 2026-10-15 ("go 3b locally on termidor"): desk host Termidor (x86-64) only; no `luna-pi`, no Luna. The aarch64 build of 3b.1 waits for Step 4.
- [x] 3b.1 Leave Python: LFM2.5-350M in `llama-server` (official release b11429, x86-64; the aarch64 build waits for Step 4). Lean peak 319 MiB (Q4_K_M) and 306 MiB (Q4_0), against 351 MiB in Python; the server re-reads the whole prompt unless the shared prefix is saved to a slot file and restored (lean 4.5 → 3.3 s median). Result `docs/03b3_01`.
- [x] 3b.2 Survey and choose a micro-harness: keyword table → model → adapter → MCP client to Wyoh, plus a few "skills" exposed as fixed, checked tools (for example, read a file or list a folder under allowlisted roots; writes need acceptance).
  - Candidates: our own small Go or Rust binary, MCPHost (Go, possibly archived), `mcp-cli` (Python), llama.cpp's web UI MCP host.
  - **Added 2026-10-13 (`docs/0700_02`):** **ZeroClaw** (Rust; native llama.cpp provider; `local_small` profile; readonly/supervised/full modes), **PicoClaw** (Go, Sipeed; MCP; `SKILL.md`), NanoBot as a functional reference.
  - **Measured 2026-10-15 (`docs/03b3_01`):** ZeroClaw 0.8.5 and PicoClaw 0.3.1 on Mike's six tools (fake MCP), four French requests: 2/4 each; about 31–37 MiB each; about 1,500–1,650 prompt tokens per request. ZeroClaw asks before running a tool, but its prompt is fixed and the model fails under it. PicoClaw's prompt can be trimmed, but it runs tools without asking. Recommendation: Mike's own thin chain; the two harnesses stay references.
  - Not done: the `ls ~` skill (Step 7), memory across a restart, refusing a forbidden action, NanoBot, and the Zenodo preprint's protocol.
- [x] 3b.4 Liquid AI's QAD Q4_0 build measured with the plain Q4_0: Q4_0 is the best file (main 55/81, held-out 16/31, lean 306 MiB); QAD is not better on the main set and worse held-out (12–13/31). The card makes no "near Q5_K_M" claim. Files and checksums in `mike-assets/SHA256SUMS`.
- [x] 3b.3 Choice and RAM budget written (`docs/03b3_01`, proposal): `llama-server` Q4_0 lean with the prefix slot restored, and Mike's own chain; about 320–340 MiB on the desk host. Open for the user: adopt it; move the desktop state to the end of the prompt (to measure); Step 4 on `luna-pi`.

### Step 7 — Zero-shot decider and predefined plans (from the user's discussion of 2026-10-13; design only until green-lit)
**Status**: ⏳ Pending — source `docs/0700_01` (raw) and `docs/0700_02` (cleaned)

Goal: find out whether a small pre-trained zero-shot classifier can make Mike's closed decisions faster and lighter than LFM2.5-350M, without any training:
- the context (terminal, desktop, plain input);
- the predefined plan (inject text, translate into a shell command, Wyoh action, ask for clarification);
- the operation within it.

LFM stays for what needs generation. Done means a measured verdict per candidate against the latency and memory budget, on the desk host first.

- [ ] 7.1 Check the claims of `0700_02` against primary sources: the model cards, sizes, licences, and the ONNX / C / ARM64 runtimes.
  - Candidates: GLiClass Edge v3.0 (32.7M), GLiClass Small/Instruct (144M) and GLiClass.c, multilingual MiniLMv2-L6 XNLI, Laya multilingual (322M) as an upper reference.
  - Record what is verified and what is not.
- [ ] 7.2 Write the plan catalogue and decision tree.
  - The order of decisions: context → plan → operation. Use what Wyoh already knows (focused app, whether the Slate was opened from a terminal or from Mannie, whether the text was hand-edited) instead of asking a model.
  - Include the terminal case: natural language → a *proposed* command (for example "ls of my home dir" → `ls ~`), typed without Enter, after confirmation.
  - Include the Slate's two outputs, *input* and *Mike*.
  - Design only; the Slate itself is Wyoh's.
- [ ] 7.3 Write the decider evaluation, without using any example for training.
  - Reuse the 81 + 31 requests, add plan-selection and terminal cases, and English versions of each.
- [ ] 7.4 Desk-host benchmark of the shortlist as is (ONNX or C runtime; INT8 where available).
  - Accuracy and out-of-scope refusal.
  - Warm latency p50/p95 with 1, 3, 5, 10 and 20 classes; cold load; peak RSS.
  - Three prompt strategies, to check whether the prompt really changes the decision.
  - French and English.
- [ ] 7.5 End-to-end comparison: keyword table → decider → LFM only when generation is needed, against the Step 3 hybrid (20/31 held-out). Measure how often LFM is avoided, and total RAM when the decider stays resident.
- [ ] 7.6 Write the verdict. Then, as a separate step through Professor and `worklines/luna-access.md`, measure on `luna-pi` and Luna. The desk → Luna factor (≈ 20× for Mycroft's ASR) is a hint, not a substitute for measurement.
- **Acceptance:** a doc with a verdict per candidate against the budget (decision ≤ 500 ms acceptable and < 200 ms excellent, on Luna, to be confirmed there; memory < 50 MiB excellent and 100–150 MiB acceptable); no training of any kind; claims marked verified or unverified.

### Step 8 — Find a model that fits Luna (user, 2026-10-25; desk study first)
**Status**: 🧪 Study in progress (desk research and documentation only; any download or measurement needs a green light)

User, 2026-10-25: "As it stands, this model is not usable. We leave Luna for now, to Mannie. And we go back to studies, to try to find an LLM or a decision model (SLM) that lets us do something within Luna's constraints."

- [x] 8.0 **Trust check first (user, 2026-10-25):** "on the Cluedo case I expect a relevant result; if we do not even get a relevant result for that, it is unusable. So first we redo the test locally: do we get the Cluedo answer, on Termidor?" Expected answer: professeur Violet, la corde, la bibliothèque. Models already on the desk (LFM2.5-350M Q4_K_M, Q4_0, QAD Q4_0; LFM2.5-230M), through the model's own chat template; French and English; a short answer, and about 100 tokens of reasoning then the answer; greedy and Liquid AI's recommended sampling. Test `test/mike/test_cluedo.py` (`integration`).
  - **Result (`results/mike/cluedo/20261025T213010Z/`): 0 of 32 answers right** (four LFM files × French/English × short/reasoning × two samplings). The murderer is named in 6 (all English short answers: "Professor Plum", without weapon or room); the rope in 3; the library in 3. Typical answers: "le colonel Moutarde, le chandelier, et le hall"; "Colonel Mustard, cigar, library"; the question's own words repeated. The test is fair (one consistent answer); the models do not reason over a 1,000-token scene. Next, with a green light for downloads: calibrate with larger models on the desk to find the size where the answer becomes right.
- [x] 8.0b **Calibration with larger models (user, 2026-10-25: "tests a bit with larger models")**, on the desk only: the same Cluedo test with Qwen3-0.6B, LFM2-700M, Gemma 3 1B, LFM2.5-1.2B-Instruct and Qwen3-1.7B (Q4_K_M GGUF, about 3.5 GB in all, under `mike-assets/`, checksums recorded). Qwen3's thinking mode is turned off, so that every model gets the same token budget.
  - **Result (`results/mike/cluedo/20261025T214118Z/`):** right (murderer, weapon and room) **1 of 40**: LFM2.5-1.2B-Instruct, French, reasoning, sampled.
    - **LFM2-700M** names the murderer 8 of 8 times, but never the weapon.
    - **Gemma 3 1B** gets the room 8 of 8 times, but names the victim as the murderer.
    - **Qwen3-1.7B** gets the room 7/8 and the murderer 4/8; the weapon only once.
    - **Qwen3-0.6B** never names the murderer.
    - **The weapon is the hard part:** the curtain cord has to be read as the rope.
    - Up to 1.7B parameters, no model is reliable on this scene. A 4B reference would show whether the scene itself is too hard.
- [x] 8.0c **One-liner test (user, 2026-10-25):** "generate a bash one-liner to find the disk usage", plus four similar everyday commands, each with its accepted answers; French and English; the nine desk models; greedy and Liquid AI's sampling. Test `test/mike/test_oneliner.py` (`integration`).
  - **Result (`results/mike/oneliner/20261025T215449Z/`, `rescored.json` after fixing the scoring both ways): disk usage is answered right (`df -h`) by almost every model; the other four tasks mostly fail.**
    - **Totals out of 20:** Gemma 3 1B and Qwen3-1.7B 10; LFM2-700M 8; LFM2.5-1.2B 7; Qwen3-0.6B 5; LFM2.5-350M 2–4; LFM2.5-230M 3.
    - **Typical misses:**
      - `ls -S` without the home directory;
      - `find … -mtime +1` (the wrong direction);
      - `ps aux | grep mem` instead of a sort;
      - for "count the lines of notes.txt", answers such as `trace` (LFM2.5-350M).
    - **Reading:** common commands seen often in training are recalled; anything that combines two details is unreliable below about 1B parameters, and only half right at 1–1.7B.
- [x] 8.1 Write Luna's measured budget for a model (`docs/0801_01`): speed per parameter and per token on the A35 (from 4.5 and 4.6), memory, and what a 1-second, 5-second or 10-second decision allows. Done: about 1.9 × 10⁹ parameter-tokens/s for reading and 0.8 GB/s of weights for writing; a 1-second decision allows about 25–30M working parameters with only the request read.
- [ ] 8.2 Survey candidates against that budget, without training (non-goal kept): small decision or classifier models (Step 7's list and others), small generative models under about 150M parameters, and the prompt shapes that keep new tokens per request very small.
  - **bitnet.cpp (user's question, 2026-10-29; desk reading of the repository and model cards, nothing run):** Microsoft's runtime for ternary (1.58-bit) models, built on llama.cpp.
    - **Kernels:** its ARM kernels (I2_S with a NEON path without dot-product, TL1 with table lookups) should run on the A35 (to check).
    - **Claimed speed-up:** 1.37–5.07× on ARM, measured on Apple M2, larger models gaining more; not measured on an A35.
    - **The models do not fit Luna:**
      - BitNet b1.58 2B4T (2.4B parameters): GGUF 1.19 GB, against about 977 MiB of RAM;
      - Falcon3-1B-Instruct-1.58bit: 1.36 GB of safetensors, with a 131,072-token vocabulary whose untied embedding and output matrices are not ternary;
      - the smaller ternary models are base models (bitnet_b1_58-large, 0.7B) or embedding models (embeddings are not accepted as deciders).
    - **Verdict:** not usable now; to revisit if a ternary instruct model under about 500M parameters appears. Also noted: VibeASR.cpp (BitNet ASR, 2026-07), possibly of interest to Mycroft.
- [ ] 8.3 Shortlist and propose desk measurements (Step 7.4 for deciders; the same raw-speed test as 4.6 for generative models), then a Luna run through Professor and Mannie.
- **Acceptance:** a budget doc and a survey doc with a shortlist, every claim marked verified or unverified; no download without a green light.

### Step 9 — PreStaC, the Prefetch Stack Cache (user, 2026-10-26)
**Status**: 🧪 9.2 done on the desk host (green-lit by the user on 2026-10-29); **9.3 and 9.4 wait for a qualified model** (Step 10, user decision 2026-10-29)

User, 2026-10-26: "the context is almost built during navigation, and Mycroft adds the star at the top of the tree: the question. A very simple file-based cache organised as a stack: when navigating, push and pop context, prefetching the load layer by layer." No Redis or server-class cache (too heavy). "We prepare PreStaC first; we will optimise the layers afterwards." "PreStaC is a step of its own."

Why: on Luna the model reads about 6.7 tokens/s (`docs/0405_01`), so Mike is fast only if almost all of the prompt is restored from saved state; the question itself is 2–14 tokens (median 6).

- [x] 9.1 **In-depth study** (`docs/0901_01`, documentation only; user request, 2026-10-26): the basic primitives; how PreStaC fits with Mike's other layers and with Wyoh, Mycroft, Mannie and Luna; who calls whom; asynchrony (prefetch, cancellation, the question arriving early, sharing the CPU with Kroko); file layout, keys and eviction; failure modes; what to measure.
- [x] 9.2 Desk prototype on `llama-server`'s slot save/restore, with a simulated navigation path (green-lit 2026-10-29, desk only).
  - Library `src/mike/prestac.py`: store, engine and stack (`docs/0901_01` § 5); reads are chunked so that a stale prefetch stops between chunks instead of relying on the server's cancellation.
  - Layers for the prototype: L0 = the fixed instructions with the tool JSON (the chat template's own order), then the desktop, then an app layer when there is one; the question last. This already moves the desktop after the tool JSON (a 9.4 change, needed to measure).
  - Default-suite tests with a fake engine; an `integration` test against `llama-server`: (1) the same answers as without the cache, (2) the share of tokens restored and the time from question to answer on a simulated navigation path, (3) state file size against tokens.
  - **Result (`docs/0902_01`, `results/mike/prestac-desk/20261029T073748Z/`):**
    - **Restored:** 98.3 % of all prompt tokens over 117 questions, at least 97.1 % per question; a median of 18 tokens read per question.
    - **Answers:** identical with and without the cache (28/28).
    - **Time:** 0.32 s median per question on the desk.
    - **Frame size:** about 12.4 KB per token, 13 MB for L0.
    - **But:** the desktop placed after the tool JSON lowers the scores (adapter 45/81 and 15/31, against 55/81 and 16/31 with prompt v4) — for 9.4.
- [ ] 9.3 Short Luna run through Professor and Mannie (needs a green light and a slot).
- [ ] 9.4 Layer optimisation afterwards (order, the tool JSON, compact rules), measured on the 112 requests.
- **Acceptance:** the study doc (9.1); then a desk prototype that restores at least 95 % of the prompt tokens on a simulated navigation path, with the time from question to answer measured (9.2).

### Step 10 — Qualify a model: 90 % stable on the evaluation cases (user, 2026-10-29)
**Status**: 🧪 green-lit by the user on 2026-10-29 ("go, do it; the priority is to qualify the model"); desk host Termidor only

User, 2026-10-29: answers are not stable ("ask the same question ten times… you will not get ten times the same answer"); single-draw scores do not account for it. Then: "I need a stable performance of something like 90 % on our cases… the base model, not even optimised, is not qualified." And: "at the same time, test Microsoft's ternary model; we need a viable candidate."

- **Gate (proposed definition, the user may change it):** on the 112 cases (81 main, 31 held-out), each case is asked **10 times**: once greedy and 9 times sampled (temperature 0.5, top-p 0.95, seeds 1–9). A case is **stable-right** when at least 9 of its 10 answers are right (the adapter's final call). A model is **qualified** when at least 90 % of the cases are stable-right on the main set **and** on the held-out set. Mean and greedy accuracy are reported too.
- **Same prompt for every model:** prompt v4's instructions and examples, the desktop line, and the tool list as text in the system turn, rendered with the model's own chat template; the answer is constrained by the contract grammar to the examples' form `name(arg="…")`. LFM models also run in their native tool format (v4), for continuity with 3b. Thinking modes are off.
- [x] 10.1 Harness `test/mike/test_qualify.py` (`integration`, `qualify.feature`), any GGUF on `llama-server`; a determinism check (greedy asked twice per case); results under `results/mike/qualify/<timestamp>/`.
- [x] 10.2 The models already on the desk: LFM2.5-350M (reference), LFM2.5-230M, Qwen3-0.6B, LFM2-700M, Gemma 3 1B, LFM2.5-1.2B, Qwen3-1.7B.
- [x] 10.3 **Ceiling:** larger models on Termidor, with no regard for Luna, to learn whether the cases are solvable at 90 % at all: Qwen3-4B and Gemma 3 4B (Q4_K_M, about 2.5 GB each). Termidor has 7.6 GiB of RAM with little free, so 8B models are left out unless the user frees memory. If even the ceiling misses the gate, the cases, the contract or the scoring are examined (failures listed for the user; expected answers are not changed without the user).
- [x] 10.4 **BitNet b1.58 2B4T** (Microsoft, ternary) through bitnet.cpp, built under the user's directories; the same gate. It does not fit Luna's RAM (1.19 GB GGUF, `docs/` 8.2 note); it is measured as a candidate family.
  - **Measured 2026-10-29 (`docs/1005_01`):** 2/81 main and 0/31 held-out stable-right, the worst of all; mostly answers about "dino". The GGUF needed two fixes (chat template, pre-tokenizer). Not a candidate.
- **Measured 2026-10-29 (`docs/1005_01`), 10.1–10.3:** no model is qualified.
  - **Closest:** Qwen3-4B (92.6 % main, 83.9 % held-out) and Gemma 3 4B (87.7 %, 93.5 %).
  - **Smaller:** Qwen3-1.7B 86 % and 81 %; Qwen3-0.6B 70 % and 65 %; the LFM models 36–54 % (native format) and 3–20 % (plain).
  - **Greedy is not deterministic** for Qwen and Gemma (2–14 cases changed between two identical requests).
  - **Arguable expected answers** in the ceiling's failures (Spotify and YouTube → browser; « mets-moi la calculatrice ») are listed for the user.
- [x] 10.6 **Chat-GBC (user, 2026-10-29: "look at it and try to reproduce it on Termidor, not in an emulator"):** github.com/rudydel/Chat-GBC (commit `db83f9b`), a 2-layer transformer of 21k–138k parameters with int7 weights that runs on a 1989 Game Boy. Reproduce on the desk host only, with its shipped checkpoints (`tiny`, `micro`): its own evaluation (`llm.evaluate`, float and the bit-exact integer simulator; claimed 100 % of training questions, 32 % and 40 % of held-out phrasings, 73 % and 80 % of off-topic questions declined) and a few chat questions, timed. Installed under `mike-tools/chat-gbc/` (clone and a private venv with CPU PyTorch). **Not done:** its training (`make train`, `make finetune`), because Mike's non-goal excludes training; the ROM and the emulator.
  - **Done (`docs/1006_01`):** its evaluation reproduces its training logs exactly (4 of 4 runs: tiny and micro, float and integer): 100 % of training questions, 32 % (tiny) and 40 % (micro) of held-out phrasings, 73 % and 80 % of off-topic questions declined. Mike's requests get "sorry, i only know about the game boy". It is a trained specialist: useful to Mike only if the user lifts the no-training non-goal, and still far from the 90 % gate on new phrasings.
- [ ] 10.5 Result doc: the smallest qualified model, if any, set against Luna's budget (`docs/0801_01`).
- **Acceptance:** every model above measured with the gate, or its failure to run recorded; a result doc with per-case stability and the failures listed.

### Step 11 — Train tiny models on natural language → shell (user, 2026-10-30)
**Status**: ✅ Done 2026-10-31 (`docs/1101_01`): 0/300 (tiny) and 1/300 (micro) exact; LFM2.5-350M untrained 6/300. Green-lit 2026-10-30 ("do the experiment anyway"). **Line closed by the user, 2026-10-31:** text to shell needs exact commands, which neither micro-models nor pre-trained models of Luna's size give; no follow-up step (story: `docs/05_text-to-shell-story.md`).

Why: general small models stay below the gate (Step 10). The user asks whether ridiculously small trained models give something "not delirious" on commands; if so, several of them could be combined (a decision model routing to one model per command or class of commands). Training lifts the non-goal for this step only, on Termidor (`docs/1007_01`).

- [x] 11.1 Data: NL2SH-ALFA (MIT ALFA, NAACL 2025; 40,939 training pairs, 300 test requests with two accepted commands each (the paper counts 600 pairs)), downloaded outside the repository; pairs too long for the model's context dropped and counted.
- [x] 11.2 Rudy's Chat-GBC models (`db83f9b`), modified for shell: the base vocabulary extended to every printable ASCII character and case kept (his tokenizer lower-cases and drops `| * ~ $ > < = _ [ ] { } +`); the patch kept in the repository; trained from scratch with his recipe (pre-train then fine-tune, his augmentation) on the NL2SH training pairs; tiny and micro configurations, CPU only.
- [x] 11.3 Measure on the NL2SH test set (300 requests): exact match against either accepted command (greedy), character error rate, a few samples read by hand; training time recorded.
  - **Baseline (user, 2026-10-31: "compute LFM2.5's accuracy on NL2SH's test set"):** LFM2.5-350M Q4_0, untrained, greedy, a one-line system prompt (`test/mike/test_nl2sh_baseline.py`, `results/mike/nl2sh-baseline/`): **6/300 exact** (all at difficulty 0), 22/300 with the right first command; it puts `sudo` in front of 158 answers; without that `sudo`, 11/300 exact and 83/300 right first command. 203 s for 300 requests on 2 threads.
  - **Tiny, trained (`results/mike/chat-gbc-nl2sh/20261030T223755Z/tiny/`):** 66k parameters, about 33 min of training on 2 threads; **0/300 exact**, 106/300 right first command, mostly by answering `find` (119 times; `find` is the expected command of 109 requests); final losses about 2.0 (pre-training) and 2.0 (fine-tuning) against Rudy's 0.2 on the Game Boy facts.
  - **Micro, trained:** 136,640 parameters, 57 min on 2 threads; **1/300 exact**, 104/300 right first command (`find` 115 times); losses about 1.7.
- [x] 11.4 Result doc: what such a model gets right, and whether the idea (tiny models per command class, man pages as training text, a light FR→EN translator before the model) is worth a next step. Those three ideas are recorded here only; not green-lit.
- **Non-goals:** nothing deployed to Luna; no GPU required; no model weights or datasets in the repository.
- **Acceptance:** both configurations trained and measured on the 300 test requests, with the patch, the command lines and complete logs kept.

### Step 12 — Small talk with the untrained model, made fluid (user, 2026-10-31)
**Status**: 🟩 Green-lit as a whole by the user, 2026-10-31 12:00, before going out: "work independently, manage; Luna is yours; delegate if needed". Mike leads this phase and holds the plan. Conditions from the user: Luna operations go through Mannie on Luna, who works there; questions about operating Luna (MCP and the rest) go to Wyoh first, who did most of the work there; sessions may talk and help each other; Python first, nothing ruled out afterwards; installing dependencies on Termidor or Luna is allowed; **no fine-tuning**; any real change of direction is notified to the user's phone. Step 12.4 builds on the Slate: FN+B already sends its text to Mike (`docs/1204_02`), and the Slate already dictates with Kroko.

User, 2026-10-31: no training from scratch (that is Rudy's size, far too small) and no fine-tuning, even of a 300 MB model. Keep Mike's chosen model, LFM2.5-350M, raw. Take the favourable, non-committing case: **chat, no action**. "I take Luna out of my pocket, press a button, small talk, ask about a subject I know is in its training corpus, and see what it gives." The goal is an experience acceptable to a human, above all in speed. Work on PreStaC first, then possibly the whole harness: much of the problem was the thousand prompt tokens read before every answer. A few tools may come later; chat first.

Why it may work where Step 10 did not: a chat answer is not judged right or wrong like a tool call, so the 90 % gate does not apply (nothing runs). What remains is time. On Luna the model reads about 6.5 tokens/s and writes about 3.6 tokens/s (`docs/0405_01`, `0801_01`):
- **Before the first word:** with the prompt restored from PreStaC, only the new turn is read (about 16–20 tokens, `docs/0902_01`), so about 3 s (estimate, not measured).
- **While it writes:** 3.6 tokens/s is about 2.5 words/s, close to a slow reading pace, if the text is shown as it comes (streaming). A 60-token answer takes about 17 s to finish, so answers must stay short.

- [x] 12.1 **Desk baseline** (done 2026-10-31, `docs/1201_01`; follow-ups read 14–26 tokens except one re-tokenisation miss at 59; the model is fluent and often wrong on facts): LFM2.5-350M Q4_0 raw, a short chat system prompt (tens of tokens, not the 1,053 of Mike's tool prompt), French and English; a dozen questions on general subjects, answers read by the user. Measure time to first token, tokens/s written, answer length; streaming through `llama-server`.
- [x] 12.2 **The conversation as a PreStaC stack** (done 2026-10-31, `src/mike/smalltalk.py`, `docs/1201_01`: history kept as token ids, so no follow-up reads more than 26 tokens; L0 restored from its frame after a restart, so the first question reads 14–20): L0 = the chat system prompt; each finished turn pushed as a frame, so the next question reads only itself; prefetch while the user speaks is paused (Kroko shares the CPU, `docs/0901_01` § 7). Compare with `llama-server`'s own prompt cache, which already keeps the slot's last conversation; PreStaC's value is restart, switching topics and returning to an earlier conversation.
- [ ] 12.3 **Harness trimmed for chat:** what else sits between the question and the first word (Python start-up, template, sampling settings, answer length limits).
- [ ] 12.4 **A small chat interface with push-to-talk** (subcontracted to Wyoh, user 2026-10-31: Wyoh plan 6.11, waiting for Wyoh's green light; app id "mike", title "Mike — ready", FN+B types the Slate text into the window; MIKE_HOME `/home/michael/.local/opt/mike`): a button starts Mycroft's dictation, the text goes to Mike, the answer is shown as it comes. **Ownership to settle with the user:** the button and the dictation belong to Wyoh (gamepad daemon) and Mycroft; Mike would own the chat loop. Desk first.
- [ ] 12.5 **Luna run** through Mannie (Luna's operator), measured from the button press to the first word and to the last. Mannie on Luna (12:05): files still in `/home/michael/.local/opt/mike/` (model SHA-256 checked); `smalltalk.py` copied (go for read and copy). The run itself needs Mannie stopped (`mannie stop --save`, Professor's or the user's call) and the brain lock free; test `test/mike/test_smalltalk_luna.py` (`live`), four runs of the 12.1 questions (French cold, English cold, French warm, French with repacked weights), about 15–20 min.
- **Non-goals:** no training; no action run from chat (tools only by a later decision); no speech output; nothing on Luna before 12.5's green light.
- **Acceptance (proposal):** on Luna, first word shown within about 3 s of the end of dictation, with the text streamed; numbers from the desk first.

### Step 4 — `luna-pi` measurement
**Status**: ⏳ Pending
- [ ] 4.1 Install the runtime and the shortlisted models on `luna-pi` in a user directory, removable.
- [ ] 4.2 Re-run the evaluation set there (`live` marker); also run with 1 and 2 threads to approach Luna's weaker cores.
- [ ] 4.3 Test prompt caching of the fixed tool list.
- [ ] 4.4 Record figures and their limits (A72 ≠ A35).
- **Acceptance:** `luna-pi` figures recorded with the evidence path; model decision written (`docs/`), or "not good enough" with what would be needed.
- [x] 4.5 **First run on Luna** (user, 2026-10-25, relayed by Professor tanstfaafllm-2a: "Stop Mannie on Luna and supervise Mike for a first run on Luna."; Professor supervises). Evidence for the 3b choice, which the user has not formally made.
  - Runtime: official llama.cpp b11429 `llama-server` arm64 release, lean (`--no-repack -b 16 -ub 16`), LFM2.5-350M Q4_0, checksums recorded; prefix slot saved and restored.
  - Install as `michael` under `/home/michael/.local/opt/mike/` only: no packages, no services, nothing in the system.
  - Measure load time, server RSS and `MemAvailable` before, during and after (Wyoh's session and resident Kroko left as they are), time per request, and a handful of evaluation requests through the thin chain. Proposals only: nothing is executed on the desktop.
  - Order: wait for Professor's "go" (Mannie on Luna saves and stops first); take `/tmp/luna-brain.lock` (`mike <pid>`, noclobber; stop if held by a live pid); no reboot; stop at < 150 MiB available, OOM or a hang. At the end: stop the server, remove the lock, leave Luna as found, tell Professor "done".
  - Results `results/mike/luna-first-run/<timestamp>/` and a short doc in `docs/`.
  - **Done 2026-10-25 (`docs/0405_01`), stopped after three requests (user: "one question is enough"):** load 3.5 s; RSS about 300–307 MiB; MemAvailable lowest 562 MiB; **about 105 s per request** (about 682 prompt tokens read at 6.7 tokens/s); 2 of 3 right after the adapter. Luna left clean (no server, no lock; files kept under `~/.local/opt/mike/`).
- [x] 4.6 **Raw model speed on Luna, without any harness** (user, 2026-10-25: "a prompt of similar size, about a thousand tokens, a little Cluedo-like game scene, asking for an answer of a few tokens: who is the murderer, or in which room; to see the model's base speed"). `llama-completion` alone, LFM2.5-350M Q4_0, 4 threads, greedy, on a fixed French Cluedo prompt (`test/mike/cluedo_prompt.txt`), with weight repacking off (as in lean) and on. Same desk-host run for comparison. Under the brain lock; Luna free and Mannie on Luna stopped (`luna-access.md`), at the user's direct request.
  - **Done (`docs/0405_01` § 4.6):** Luna reads 6.5 tokens/s (lean) or 6.9 (repack) and generates 3.6 or 2.8 tokens/s; 1,056 + 23 tokens take about 160–170 s. Termidor: 174–348 and 59–67 tokens/s. The harness adds nothing measurable; repacking barely helps on the A35.
- **Luna target (Professor relay of Luna's note `worklines/professor/docs/0000_04`, 2026-10-25):** Luna has a new user `michael`, and the user decided on 2026-10-25 to replace ArchR's root with Arch Linux ARM (`plan_mannie.md` Step 7; `/storage` and `/home` kept). When Mike reaches Luna (after Step 4, at Step 5), it runs as `michael` on the new root. Nothing of Mike is on Luna today.
- **Luna operation rules (user rule of 2026-10-25, relayed by Professor; in `skills/cell-coordination`, `AGENTS.md` and `worklines/luna-access.md`):** Mannie runs on Luna as its operator ("Mannie from Luna"); Mike may message it directly about Luna operations. No SSH to Luna without Mannie's "go", and no reboot while Mannie runs there. **Mannie and Mike never run together on Luna:** the launcher takes the shared lock `/tmp/luna-brain.lock` (content `name pid`); Mike's Step 5 launcher must take and honour it. Applies to Steps 4 (any Luna step after `luna-pi`) and 5.

### Step 5 — `mike-console` v0
**Status**: ⏳ Pending
- [ ] 5.1 Console per the intent: request, proposed action, `Enter`/`Esc`, honest result.
- [ ] 5.2 Gherkin scenario + pytest with the fake Wyoh (deterministic) and with the chosen model (`integration`).
- [ ] 5.3 Live scenario against the real Wyoh MCP server on `luna-pi` over SSH, with screenshots inspected (`live`).
- [ ] 5.4 **Wyoh's request (`docs/1204_02`, 2026-10-15, carrying a user decision: the Slate's FN+B sends text to Mike):** when Mike runs on Luna, choose and document how a request reaches Mike (for example a Unix socket, or stdin), what Mike shows while it works, and where its proposed actions appear for acceptance; answer in a reply section of that note. Nothing is due before Step 5.
- **Acceptance:** typed request → accepted action → visible change on `luna-pi`'s desktop, with screenshots; a refused action runs nothing.

### Step 6 — Hand-offs (design only)
**Status**: ⏳ Pending
- [ ] 6.1 Note to Mycroft: how accepted text reaches Mike.
- [ ] 6.2 Note to Wyoh: whether task-level tools should live in Wyoh's MCP server.
- [ ] 6.3 Mannie escalation design: what triggers it, what the user sees and pays.
- **Acceptance:** notes left in the receiving worklines' `docs/`; no change made in their code.

---

## Progress tracking ✅

- ✅ Step 0 — Workline set-up and desk research
- 🧪 Step 1 — Intent and tool contract (1.1–1.4 done; 1.5 user approval open)
- ✅ Step 2 — Evaluation set and harness (D13)
- 🧪 Step 3 — Desk-host model comparison (3.0–3.2f done; 3.5 decision open)
- ✅ Step 3b — Lean runtime and micro-harness (Termidor only; choice open for the user)
- ⏳ Step 4 — `luna-pi` measurement
- ⏳ Step 5 — `mike-console` v0
- ⏳ Step 6 — Hand-offs (design only)
- ⏳ Step 7 — Zero-shot decider and predefined plans (proposed, 2026-10-13)
- 🧪 Step 8 — Find a model that fits Luna (study, 2026-10-25)
- 🧪 Step 9 — PreStaC, the Prefetch Stack Cache (9.2 done; 9.3–9.4 wait for Step 10)
- 🧪 Step 10 — Qualify a model: 90 % stable (green-lit 2026-10-29; priority)
- ✅ Step 11 — Train tiny models on natural language → shell (done 2026-10-31: 0–1/300 exact)

---

## Time tracking (use `date`) ⏱️

### Time log

| Timestamp (`date`) | Update |
|---|---|
| sam. 31 oct 2026 12:08 CET | 12.1 and 12.2 done on the desk (`docs/1201_01`). Interface subcontracted to Wyoh (6.11, user's word). Mannie on Luna: go for checking and copying, done; the Luna run waits for Mannie to be stopped through Professor. Professor relays the user's new routine: commit, push, give GitHub links. |
| sam. 31 oct 2026 12:00 CET | User, leaving: Step 12 green-lit as a whole, to run independently; Luna through Mannie, Luna questions to Wyoh first; no fine-tuning; notify the phone on a real change of direction. |
| sam. 31 oct 2026 11:54 CET | User: next, a use case that fits: small talk with LFM2.5-350M raw (no training, no fine-tuning), push-to-talk through Mycroft, made fluid with PreStaC and then a trimmed harness. Step 12 proposed, not green-lit; the qualification gate does not apply to chat, where nothing runs. |
| sam. 31 oct 2026 11:45 CET | User: the text-to-shell line stops here. A command must be exact to be useful; micro-models only recall their corpus, and pre-trained models, even beyond Luna's size, are not precise enough. Story written (`docs/05_text-to-shell-story.md`). The router, man-page and translator ideas are not pursued. |
| sam. 31 oct 2026 06:05 CET | Step 11 done (`docs/1101_01`): micro 1/300 exact (finished about 01:10), tiny 0/300, LFM2.5-350M untrained 6/300; the tiny models answer `find` by habit. |
| sam. 31 oct 2026 00:37 CET | 11.3 so far: tiny trained 0/300 exact (106 right first command, mostly `find`); micro running. User: compute LFM2.5-350M's accuracy on the NL2SH test set: 6/300 exact untrained (11 without its `sudo`). Termidor's GPU (GTX 760, Kepler, nouveau driver) cannot train; CPU-only estimate for a LoRA pass of LFM2.5-350M on 40k pairs: 6–10 h. |
| ven. 30 oct 2026 23:28 CET | User: "do the experiment anyway" with Rudy's models (Chat-GBC, the user's colleague) and the NL2SH training data, vocabulary extended. Step 11 added and green-lit; the no-training non-goal lifted for Step 11 only. Ideas recorded, not green-lit: one tiny model per command class behind a router, man pages as training text, a light FR→EN translator. |
| ven. 30 oct 2026 22:40 CET | User: general models will not do; asks whether a model can be retrained on bash one-liners (requests described → command), narrowing the use case, and asks for an existing "speech to command line" project. Survey written (`docs/1007_01`). Training stays a non-goal until the user decides explicitly. |
| ven. 30 oct 2026 22:10 CET | Professor (user request): commit everything, coordinated; Mike first. Mike's own files only (no LOGBOOK, agents.md, pyproject, uv.lock), no push. Script `tmp/commit_mike.sh` (5 commits) waits for the user's go. |
| jeu. 29 oct 2026 21:26 CET | 10.4 done: BitNet b1.58 2B4T 2/81 and 0/31 stable-right; not a candidate. |
| jeu. 29 oct 2026 20:38 CET | 10.1–10.3 done (`docs/1005_01`): no model qualified; Qwen3-4B 92.6/83.9 %, Gemma 3 4B 87.7/93.5 %, Qwen3-1.7B 86/81 %, Qwen3-0.6B 70/65 %, LFM 36–54 %. BitNet run started. |
| jeu. 29 oct 2026 14:35 CET | 10.6 done (`docs/1006_01`): Chat-GBC's evaluation reproduces its logs exactly on Termidor (no emulator); 32–40 % of held-out phrasings; a trained specialist, so outside Mike's no-training scope. |
| jeu. 29 oct 2026 14:16 CET | User: look at Chat-GBC and reproduce it on Termidor, not in an emulator. Recorded as 10.6 (shipped checkpoints only; training excluded). BitNet 2B4T smoke: template and pre-tokenizer fixed; still answers "dino" on 4/4 cases. |
| jeu. 29 oct 2026 12:49 CET | User: answers are unstable and single draws do not show it; a model needs about 90 % stable on the cases before any optimisation; LFM2.5-350M not qualified. "Go": Step 10 (qualification, priority) with BitNet b1.58 2B4T; 9.3–9.4 wait. |
| jeu. 29 oct 2026 08:43 CET | 9.2 done (`docs/0902_01`): 98.3 % of prompt tokens restored, median 18 read per question, answers identical with and without the cache; 0.32 s per question on the desk; frames 13 MB; the desktop-after-tools order loses 10 main-set answers (for 9.4). |
| jeu. 29 oct 2026 08:34 CET | User: "Go" for 9.2 (desk prototype of PreStaC). Started. |
| jeu. 29 oct 2026 08:28 CET | User asked about bitnet.cpp: desk reading only; runs on ARMv8.0 (to check), up to 5× claimed, but its models (2.4B, 1B) do not fit Luna's RAM. Recorded under 8.2. |
| lun. 26 oct 2026 08:26 CET | 9.1 written (`docs/0901_01`): three levels of primitives, the Wyoh–Mike–PreStaC–llama-server chain, one coalesced worker, dictation pause, files keyed by token ids, seven open questions for 9.2. |
| lun. 26 oct 2026 08:24 CET | User: name the cache PreStaC (Prefetch Stack Cache); prepare it first and optimise the layers afterwards; asked for an in-depth study (primitives, integration, who calls whom, asynchrony). 8.4 restructured into 8.4.1–8.4.4; study under way. Then the user: "PreStaC is a step of its own": moved to Step 9 (9.1–9.4); study doc `docs/0901_01`. |
| lun. 26 oct 2026 08:02 CET | User: context caching is the way; Anthropic gives 80–90 % cached at work; for Mike the key is prefetch: a simple file-based stack of context layers, built during navigation, the question added on top by Mycroft. Recorded as 8.4 (design; prototype needs a green light). |
| dim. 25 oct 2026 22:59 CET | 8.0c: one-liners on nine desk models: disk usage right almost everywhere; overall 2–4/20 for LFM2.5-350M, 10/20 at best (Gemma 3 1B, Qwen3-1.7B). |
| dim. 25 oct 2026 22:54 CET | User: try a one-liner task (disk usage). Recorded as 8.0c. |
| dim. 25 oct 2026 22:46 CET | 8.0b: five larger models (0.6–1.7B) on the Cluedo: 1/40 fully right; LFM2-700M always finds the murderer; the weapon (cord → rope) is the hard part. |
| dim. 25 oct 2026 22:33 CET | User: "tests a bit with larger models". Recorded as 8.0b; five GGUF downloads to `mike-assets/`. |
| dim. 25 oct 2026 22:31 CET | 8.0 on Termidor: 0/32 right for LFM2.5-350M (three files) and 230M, French and English, short and reasoning, two samplings. Not usable for this kind of decision. |
| dim. 25 oct 2026 22:29 CET | User: trust problem; the Cluedo answer must be relevant, or the model is unusable; redo it on Termidor first. Recorded as 8.0. |
| dim. 25 oct 2026 22:20 CET | User: LFM2.5-350M not usable on Luna as it is; Luna left to Mannie; back to studies for an LLM or decision SLM within Luna's constraints. Step 8 added (desk study). Professor informed. |
| dim. 25 oct 2026 22:18 CET | 4.6 done: Luna 6.5–6.9 prompt tokens/s, 2.8–3.6 generated tokens/s, without any harness; the model, not the harness, sets Mike's speed. Luna rebooted at 22:11 (not by Mike) between the desk and Luna runs; the run took the brain lock and freed it. |
| dim. 25 oct 2026 22:08 CET | User: measure the model's base speed without the harness (a ~1,000-token Cluedo scene, a few-token answer). Recorded as 4.6; run on Luna (free, Mannie on Luna stopped) at the user's direct request, repack off and on. |
| dim. 25 oct 2026 21:43 CET | 4.5 done (`docs/0405_01`): it runs on Luna, about 300 MiB, but about 105 s per request. Three test-script failures fixed on the way; a server left by an interrupted command found and stopped; Luna clean. User: "one question is enough; then we move to the harness". Reported to Professor. |
| dim. 25 oct 2026 21:21 CET | Professor: "go for 4.5 as planned"; Mannie on Luna stopped (17:40), lock free, MemAvailable 654 MiB; Mike named holder in `luna-access.md`; SSH as `michael` covered by the user's instruction. Adjustments: if slow at `-t 4`, rerun one request at `-t 2`; sample MemAvailable before start, after load, at each request's peak and after stop. 4.5 started. |
| dim. 25 oct 2026 21:20 CET | Professor relayed the user: "Stop Mannie on Luna and supervise Mike for a first run on Luna." Recorded as 4.5 (scope, order and stop conditions as sent by Professor); the Luna non-goal gets a 4.5 exception. Waiting for Professor's "go" after Mannie stops. |
| dim. 25 oct 2026 13:45 CET | Professor relayed the user's rule of 2026-10-25: Mannie is Luna's operator; Mike may message it about Luna operations; no SSH to Luna without its "go", no reboot while it runs; Mannie and Mike never run together (shared lock `/tmp/luna-brain.lock`). Recorded under Step 4 for Steps 4 and 5; no reply needed. |
| dim. 25 oct 2026 13:41 CET | Professor (tanstfaafllm-2a) asked for this session's workline: replied `mike`, row updated in `worklines/agents.md` (tanstfaafllm-02 [effb91]). Professor relayed Luna's change (user decision, 2026-10-25: user `michael`, ArchR root replaced by Arch Linux ARM): noted under Step 4 for when Mike reaches Luna; no reply needed. 3b's choice stays with the user. |
| jeu. 15 oct 2026 03:03 CEST | Wyoh's note `docs/1204_02` received (the Slate's FN+B will send text to Mike; user decision): recorded as 5.4, nothing due before Step 5. |
| jeu. 15 oct 2026 03:01 CEST | Step 3b measured on Termidor (`docs/03b3_01`). `llama-server` lean: 319 MiB (Q4_K_M), 306 MiB (Q4_0), against 351 MiB in Python; prefix slot restore lean 4.5 → 3.3 s. Q4_0 best; QAD not better. ZeroClaw and PicoClaw: 2/4 each, about 1,500–1,650 prompt tokens; ZeroClaw asks before tools, PicoClaw does not. Recommended: Mike's own chain on `llama-server` Q4_0 lean. The Python reference run was stopped (host loaded by other sessions; the first model hit the test timeout). Open for the user: adopt 3b.3; prompt with the desktop at the end; Step 4. |
| jeu. 15 oct 2026 01:14 CEST | User: "go 3b locally on termidor". Step 3b green-lit on the desk host only. Termidor has no cmake, Go or Rust toolchain; prebuilt release binaries are preferred, kept outside the repository with their checksums. |
| mar. 13 oct 2026 22:47 CEST | User request: capture and clean the ChatGPT discussion <https://chatgpt.com/share/6ace95fc-0800-83eb-bd5f-9d86b7257744> and prepare a step for it. Raw export `docs/0700_01` (77 messages; the scraper now keeps the most complete version of each message, after the first run lost text). Cleaned record `docs/0700_02` (two transcription points confirmed by the user: "GF" = JEV, "en BD" = embedded). User decisions recorded: one action per order, predefined plans allowed, **no training of any kind (option B dropped)**, no translation, English allowed, OpenCL not preferred, decision latency budget. Step 7 added and Step 3b extended (ZeroClaw/PicoClaw, QAD Q4_0); design only. Notes left for Mycroft (English ASR) and Wyoh (Slate outputs). |
| dim. 11 oct 2026 22:12 CEST | Session resumed as **Mike** after the rename (Professor D16, for the user). Checked after the swap: `uv run --group mike pytest test/mike -m "not live and not integration"` gives 55 passed; `worklines/mike/scripts/mike_chat.py --lean` loads LFM2.5-350M from `mike-assets` (295 MiB) and answers. Nothing else green-lit. Open for the user: 1.5, 3.5, 3.8, Step 3b. |
| dim. 11 oct 2026 20:59 CEST | Professor: pause (usage limit), then resume within the existing green lights, desk host only. The user is reconsidering the Mannie/Mike naming: rename nothing until they decide. Resumed: 3.3–3.4 closed with `docs/0304_01`. **State:** Step 3 measurements are complete. Open for the user: 1.5 (contract), 3.5 (routing A, option B), 3.8 (vocabulary pruning), Step 3b (green light). Nothing else green-lit; stopped. |
| dim. 11 oct 2026 12:33 CEST | Professor (tanstfaafllm-80) asked every session to update its row after the restarts: Mike is now tanstfaafllm-20 [5832e9] in `worklines/agents.md`. The rest of that message was for Wyoh; nothing for Mike. |
| dim. 11 oct 2026 12:31 CEST | 3.9: lean LFM2.5-230M on the full sets with v4 ≈ 350M on the tool task (hybrid 21/31 vs 20/31). Reported to the user; the 350M decision stands unless the user revises it. |
| dim. 11 oct 2026 12:31 CEST | User decision: **LFM2.5-350M** (about 350 MiB accepted for now). Next interest: leave Python (C++/Rust runtime) and a very restricted micro-harness with a few skills and filesystem access. Step 3b proposed (design only). A lean full evaluation of 230M was still running in the background. |
| dim. 11 oct 2026 12:18 CEST | User tried `mike_chat.py` in tool mode and saw no answer: the grammar forces one of the 7 actions. Added in-session `/outils`, `/libre`, `/chat`. The grammar's text limit is raised from 80 to 200 characters, matching the contract. Chat check: LFM2.5-230M answers fluently but wrongly (confuses itself with the user, invents tools); 79 tokens/s on the desk. |
| dim. 11 oct 2026 12:12 CEST | User asked whether vocabulary pruning and removing a vision part could slim the model. Checked: text-only; 17 % of the vocabulary is CJK/Cyrillic/Hangul/Arabic, about 9 MiB of file; 3.8 proposed. |
| dim. 11 oct 2026 12:09 CEST | User: 500 MiB is too much for Mike alone. Measured a lean setting (3.7): 350M ≈ 300 MiB, 230M ≈ 215 MiB above Python. Added `--lean` to `mike_chat.py`. The user tests 350M by hand, then we discuss. |
| dim. 11 oct 2026 12:03 CEST | User direction: pause the system interaction (Step 5) and fine-tuning; first see how the models behave by hand, then how fast they run **on Luna**. Added `scripts/mike_chat.py` (manual try, nothing executed). Running on Luna is outside the current non-goals: proposed as a new step, awaiting a green light. |
| dim. 11 oct 2026 11:59 CEST | Session resumed after a token stop; nothing was lost (plan, logbook, 53 tests intact). Option A (3.6) measured from saved runs, no new model run: 20/31 held-out. Still open for the user: 1.5 contract, 3.5 A adoption and B green light. |
| ven. 09 oct 2026 23:43 CEST | **Stopped for the night (D13 limit: midnight).** Done: contract draft (`docs/0102_01`), Step 2 (`docs/0201_01`), 3.2c (`docs/0302_03`). **State:** the best setting gets 52–59 % right and barely beats the keyword table on held-out requests. **Open for the user:** 1.5 approve the contract and its two ⚖️ items; 3.5 choose A/B/C/D (recommended A then B; B needs a green light). Nothing on `luna-pi` or Luna; no commit. |
| ven. 09 oct 2026 22:50 CEST | Professor's decision D13 (delegated by the user): 🟩 go Step 1 (1.2–1.4) and Step 2 (2.1–2.4), desk host only; Wyoh read only; the "focus a closed app → launch it" rule is a contract proposal for the user's approval; no `luna-pi`, no Luna, no commit; stop at midnight or when blocked. |
| ven. 09 oct 2026 22:47 CEST | 3.2d–f done: prompt v2 and prefix-state cache. LFM2.5-350M 10/13 at 0.21 s per request (desk host); FunctionGemma dropped. Proposal for Step 1: the adapter turns "focus an app that is not open" into "launch it" (would give 12/13). Result `docs/0302_02`. Stopping here: the next steps (Step 2 evaluation set, Step 4 `luna-pi`) need a green light. |
| ven. 09 oct 2026 22:45 CEST | Professor's decision D1 recorded (naming follows the user; Adam on hold). Reply sent to Professor: Step 3 status, no open question, next 3.2d–f under the Step 3 green light. |
| ven. 09 oct 2026 22:43 CEST | 3.1–3.2b done on the desk host: three models downloaded and smoke-tested (13 French requests, free and constrained). Best LFM2.5-350M 6/13; RSS higher than estimated (repack + compute buffer + Python). Result `docs/0302_01`; sub-steps 3.2d–f proposed. |
| ven. 09 oct 2026 22:23 CEST | User asked to start with Step 3, then said "go". Step 3 intent written (`docs/0301_01`): shortlist LFM2.5-350M, LFM2.5-230M, FunctionGemma 270M; Qwen3-0.6B left out for RAM (KV cache 112 KiB/token). Starting 3.1. |
| ven. 09 oct 2026 22:20 CEST | User reviewed the intent: diagram and intent agreed; Adam removed from the picture ("pour l'instant, je vois pas Adam"). Intent and note to Professor updated. |
| ven. 09 oct 2026 22:13 CEST | Workline created at the user's request (first called Mike, corrected to Mannie by the user (D1; reverted to Mike by D16 on 2026-10-11)). Desk survey, intent and plan written; naming note sent to Professor. No download, no device access. |

---

## Workline artifacts

- [`docs/1005_01_qualification-result.md`](docs/1005_01_qualification-result.md) — Step 10: the 90 % stable gate on 13 model–format pairs; none qualified, the 4B models come close; the ceiling's failures listed.
- [`docs/1101_01_tiny-shell-models.md`](docs/1101_01_tiny-shell-models.md) — Step 11: Rudy's tiny and micro trained on NL2SH: 0 and 1 exact of 300; LFM2.5-350M untrained 6.
- [`docs/1201_01_smalltalk-desk-result.md`](docs/1201_01_smalltalk-desk-result.md) — Step 12.1–12.2: small talk on the desk; history kept as tokens, 14–26 tokens read per question; Luna estimate 2–4 s before the first word.
- [`docs/1007_01_speech-to-command-line-survey.md`](docs/1007_01_speech-to-command-line-survey.md) — speech/NL to command line: existing projects (Vox, NL2Shell, BashGemma), the MIT NL2SH data and results; training helps small models but open bash stays far from 90 %.
- [`docs/1006_01_chat-gbc-on-the-desk.md`](docs/1006_01_chat-gbc-on-the-desk.md) — 10.6: Chat-GBC's shipped models reproduce their own numbers on Termidor; a trained specialist that generalises to 32–40 % of new phrasings.
- [`docs/0902_01_prestac-desk-result.md`](docs/0902_01_prestac-desk-result.md) — Step 9.2: PreStaC on the desk: 98.3 % restored, 18 tokens read per question, same answers; the layer order costs accuracy.
- [`docs/0901_01_prestac-study.md`](docs/0901_01_prestac-study.md) — Step 9.1: PreStaC study: primitives (engine, store, stack), who calls whom, asynchrony, files, failure modes, open questions.
- [`docs/0801_01_luna-model-budget.md`](docs/0801_01_luna-model-budget.md) — 8.1: what Luna allows a model (parameters, tokens, file size) for a 1 s, 5 s or 10 s decision.
- [`docs/0405_01_first-run-on-luna.md`](docs/0405_01_first-run-on-luna.md) — 4.5: first run on Luna: 3.5 s load, about 300 MiB, about 105 s per request; what would cut it.
- [`docs/1204_02_note-from-wyoh-slate-sends-to-mike.md`](docs/1204_02_note-from-wyoh-slate-sends-to-mike.md) — from Wyoh: FN+B in the Slate sends text to Mike; Mike's hand-off to choose at Step 5 (5.4).
- [`docs/03b3_01_lean-runtime-and-micro-harness-result.md`](docs/03b3_01_lean-runtime-and-micro-harness-result.md) — Step 3b: `llama-server` RAM and speed, Q4_0/QAD, ZeroClaw and PicoClaw on Mike's tools; proposed runtime and budget.
- [`docs/0700_02_harness-and-decider-discussion.md`](docs/0700_02_harness-and-decider-discussion.md) — cleaned record of the 2026-10-13 discussion: user decisions, assistant proposals, unverified claims; the source of Step 7.
- [`docs/0700_01_harness-and-decider-discussion-raw.md`](docs/0700_01_harness-and-decider-discussion-raw.md) — raw export of that discussion (primary reference).

- [`docs/0000_01_small-tool-calling-model-survey.md`](docs/0000_01_small-tool-calling-model-survey.md) — candidate models ≤ 400 MB, verified sizes, what to measure.
- [`docs/0304_01_model-comparison.md`](docs/0304_01_model-comparison.md) — Step 3 summary: every model, RAM, accuracy, speed; recommendation.
- [`docs/0302_05_lean-memory.md`](docs/0302_05_lean-memory.md) — where the RAM goes; lean setting: ~300 MiB (350M), ~215 MiB (230M).
- [`scripts/mike_chat.py`](scripts/mike_chat.py) — interactive try of a model with the contract tools (or `--chat`); shows the keyword table, the model's call, the adapter's proposal and timings.
- [`docs/0302_04_keywords-first-result.md`](docs/0302_04_keywords-first-result.md) — option A: keyword table first, model second: 20/31 held-out.
- [`docs/0302_03_evaluation-set-result.md`](docs/0302_03_evaluation-set-result.md) — LFM models on 81 + 31 requests: 52–59 %, barely above the keyword table; options A–D.
- [`docs/0201_01_evaluation-set-and-baseline.md`](docs/0201_01_evaluation-set-and-baseline.md) — evaluation sets, fake Wyoh, scoring, keyword baseline.
- [`docs/0102_01_tool-contract.md`](docs/0102_01_tool-contract.md) — the tool contract (draft, awaiting approval).
- [`docs/0302_02_prompt-and-prefix-cache-result.md`](docs/0302_02_prompt-and-prefix-cache-result.md) — prompt v2 and prefix cache: 10/13 at 0.21 s for LFM2.5-350M; recommendation.
- [`docs/0302_01_smoke-result.md`](docs/0302_01_smoke-result.md) — first smoke test of the three models: scores, memory breakdown, speed, next steps.
- [`docs/0301_01_model-comparison-intent.md`](docs/0301_01_model-comparison-intent.md) — Step 3 intent: shortlist, sizes, estimated RAM, first test.
- [`docs/0101_01_mike-intent.md`](docs/0101_01_mike-intent.md) — what Mike v0 does as the user sees it; the curated tool list.
- [`../professor/docs/0000_02_note-from-mannie-naming.md`](../professor/docs/0000_02_note-from-mannie-naming.md) — naming conflict (Mannie/Mike) for Professor.
