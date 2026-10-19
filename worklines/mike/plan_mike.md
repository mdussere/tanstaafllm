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

- Any work on Luna (the R36 Ultra): no SSH, no deployment, no measurement. `luna-pi` is the furthest target.
- Changing the Wyoh MCP server, Mycroft, or Luna's image. Requests to them go as notes.
- Raw Sway commands or free-text `exec` from the model.
- Multi-step agent loops, a resident service, speech output, Mannie integration.
- **Any training: no fine-tuning, no retraining, no training dataset** (user, 2026-10-13, `docs/0700_02`). Pre-trained models only, zero-shot; a model that does not work as is gets dropped, not trained.
- **Translation between languages** (user, 2026-10-13): the language is chosen at the input; French or English end to end.
- GPU/OpenCL acceleration, unless there is evidence of at least 2× end to end (user, 2026-10-13: not a preferred hypothesis).
- Renaming components in shared documents.

## Key decisions / assumptions

- **Model: LFM2.5-350M** (user decision, 2026-10-11: "350 is impressive and fast"; a big difference from 230M; about 350 MiB is acceptable for now; slim down later).
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

### Step 4 — `luna-pi` measurement
**Status**: ⏳ Pending
- [ ] 4.1 Install the runtime and the shortlisted models on `luna-pi` in a user directory, removable.
- [ ] 4.2 Re-run the evaluation set there (`live` marker); also run with 1 and 2 threads to approach Luna's weaker cores.
- [ ] 4.3 Test prompt caching of the fixed tool list.
- [ ] 4.4 Record figures and their limits (A72 ≠ A35).
- **Acceptance:** `luna-pi` figures recorded with the evidence path; model decision written (`docs/`), or "not good enough" with what would be needed.

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

---

## Time tracking (use `date`) ⏱️

### Time log

| Timestamp (`date`) | Update |
|---|---|
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
