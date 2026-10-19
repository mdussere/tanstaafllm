# Step 3b — lean runtime and micro-harness: result on the desk host

**Question answered:** without Python, how much RAM does Mike's model need, which quantisation is best, and can a ready-made micro-harness (ZeroClaw, PicoClaw) carry Mike?<br>
**Date:** 2026-10-15<br>
**Status:** measured on the desk host Termidor only (Intel i5-4590, 4 cores, x86-64). Nothing ran on `luna-pi` or Luna. Green light: the user, 2026-10-15 ("go 3b locally on termidor").<br>
**Evidence:**
- `results/mike/server-runtime/20261014T235819Z/`, `20261015T001844Z/`, `20261015T004627Z/` (one JSON report per model and setting, server logs, `summary.jsonl`);
- `results/mike/micro-harness/20261014T235407Z/` (every request each harness sent, every tool call, logs).

**Tests:** `test/mike/test_server_runtime.py` (`server_runtime.feature`) and `test/mike/test_micro_harness.py` (`micro_harness.feature`), both `integration`. The fake MCP server is `test/mike/mike_fake_mcp.py`, with a default-suite test.

## Summary

- **The C++ server is not much lighter than Python.** In the lean setting, `llama-server` peaks at **319 MiB** with Q4_K_M, against 351 MiB in Python (`0302_05`). That is 32 MiB less, not the 50 MiB expected. Of the 319 MiB, about 235 MiB is the memory-mapped model file and 85 MiB is allocated.
- **Q4_0 is the best file.** It is 10 MiB smaller than Q4_K_M (306 MiB peak in lean) and scores better on the main set (55/81 against 45/81 with the adapter). It scores the same on the held-out set (16/31).
- **QAD Q4_0 does not help.** It is no better than Q4_0 on the main set and worse on the held-out set (12–13/31 against 16/31). Liquid AI's model card makes no "near Q5_K_M quality" claim. That claim came from the ChatGPT discussion and is not supported here.
- **The server must be given the prefix state explicitly.** On its own, it re-reads the whole prompt (about 1,085 tokens) for every request, with or without context checkpoints. Saving the shared 400-token prefix to a slot file once and restoring it before each request cuts the lean median from 4.5 s to 3.3 s. It costs no RAM; the file is 4.8 MB.
- **Neither ready-made harness fits Mike as is.**
  - Both are small: about 31–37 MiB, measured on the harness process alone.
  - Both send about 1,500–1,650 tokens per request, against Mike's own 1,085. In each new process, none of it is reused.
  - ZeroClaw asks for approval before running a tool, but its system prompt is fixed, and under it the model fails.
  - PicoClaw's prompt can be trimmed, but **it runs tools without asking**.
- **Recommendation (for the user to decide):** keep Mike's own thin chain and run the model in `llama-server`:
  - **Chain:** keyword table → `llama-server` (grammar, prefix slot restored) → Mike's adapter → MCP client to Wyoh.
  - **Model settings:** Q4_0, lean.
  - **The two harnesses:** keep ZeroClaw and PicoClaw as references, not as Mike's harness.

## 3b.1 — the model in `llama-server` (no Python in the model process)

Official llama.cpp release b11429 (`llama-b11429-bin-ubuntu-x64.tar.gz`, SHA-256 `f6d25dde…3392`), unpacked under `/data/michael/tanstaafllm/mike-tools/`.

**Method:**
- one slot, context 2,048, 4 threads, no web UI, no host-RAM prompt cache;
- prompt v4, constrained by the contract grammar, all 81 + 31 requests;
- the client sends token ids to `/completion`;
- the memory figures are the server process's, from `/proc/<pid>/status`.

| Model | Setting | Peak RSS | File-backed | Allocated | Median per request | Prompt tokens read | Main (model / adapter) | Held-out (model / adapter) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Q4_K_M | default | 487 MiB | 232 | 255 | 3.0 s | 1,083 | 37 / 47 | 12 / 17 |
| Q4_K_M | lean | 319 MiB | 235 | 85 | 4.5 s | 1,083 | 35 / 45 | 12 / 16 |
| Q4_K_M | lean, checkpoints at any distance | 319 MiB | 235 | 85 | 4.9 s | 1,083 | 35 / 45 | 12 / 16 |
| Q4_K_M | lean, prefix slot restored | 319 MiB | 234 | 85 | **3.3 s** | 685 | 36 / 46 | 12 / 16 |
| Q4_0 | default | 494 MiB | 222 | 272 | 3.4 s | 1,083 | 41 / 52 | 12 / 16 |
| Q4_0 | lean | **306 MiB** | 225 | 81 | 5.6 s | 1,083 | 44 / 55 | 12 / 16 |
| Q4_0 | lean, prefix slot restored | **306 MiB** | 225 | 81 | 3.6 s | 685 | 44 / 55 | 12 / 16 |
| QAD Q4_0 | default | 486 MiB | 214 | 272 | 3.2 s | 1,083 | 45 / 52 | 12 / 13 |
| QAD Q4_0 | lean | 306 MiB | 225 | 81 | 5.1 s | 1,083 | 46 / 52 | 11 / 12 |

**For comparison, Python** (`results/mike/model-eval/20261009T213217Z`, Q4_K_M, prompt v4, constrained, not lean):
- 48/81 on the main set and 16/31 held-out, with the adapter;
- median 2.07 s, with the same 400-token prefix restored;
- peak 550 MiB (that process held both modes' states).

**What this shows:**
- **Sorting out the earlier 0.21 s.** That figure (`0302_02`) came from prompt v2, which puts the desktop in the user turn. Prompt v4 puts the open windows in the system turn, so only the first 400 tokens are shared by every request.
- **A prompt change to propose.** Moving the desktop state to the end, after a fixed system turn, would let almost the whole prompt be restored. It would bring the per-request cost close to the request itself. This is not measured yet.
- **The answers differ a little between settings and runtimes** (45–48/81). Different kernels give slightly different numbers. The held-out set stays at 16/31 for Q4_K_M and Q4_0.
- **The speed figures are x86 figures** on a shared desk host. Lean is slower here because x86 loses its repacked layout. Whether ARM makes a repacked copy at all is for Step 4 to check.

## 3b.2 — ready-made micro-harnesses

Official release binaries, checked against the publishers' checksums:
- ZeroClaw 0.8.5 (`zeroclaw-x86_64-unknown-linux-gnu.tar.gz`, `9dbb53af…55f9`, Rust, 61 MB binary);
- PicoClaw 0.3.1 (`picoclaw_Linux_x86_64.tar.gz`, `86f0fe84…9c3f`, Go, 37 MB static binary).

**Method:**
- Each harness runs in a throw-away home and talks to `llama-server` (`--jinja`, context 8,192) through a recording proxy.
- **Its only tools are Mike's six contract tools,** from the fake MCP server, which records each call and touches no desktop.
- The instructions given to both are Mike's short French verb table: ZeroClaw reads it from `AGENTS.md`, PicoClaw from `AGENT.md`.
- **The four requests:** "ouvre l'éditeur", "mets le terminal à gauche", "écris bonjour" and "quel temps fera-t-il demain", one process per request.

| | ZeroClaw 0.8.5 | PicoClaw 0.3.1 |
| --- | --- | --- |
| Right first call (of 4) | 2: the move, and no tool for the weather | 2: `type_text`, and no tool for the weather |
| Wrong answers | "ouvre l'éditeur": no tool call; "écris bonjour": an invalid reply, then an error | "ouvre l'éditeur" and "mets le terminal à gauche": `focus_window` |
| Asks before running a tool | **Yes:** `always_ask` prompts on the terminal; with no terminal, the call was declined and not run | **No:** the MCP tool ran at once |
| Tools sent to the model by default | 58 built-in + MCP, 64 KB of schemas, **18,287 prompt tokens** (over the context) | about 10 built-in plus sample skills |
| After restricting to Mike's tools | 6 tools (`allowed_tools`); about 1,485 prompt tokens | 6 MCP tools + `reaction`; about 1,550–1,680 prompt tokens |
| System prompt | about 2.9 kB of fixed rules ("No tool narration", safety, runtime); cannot be replaced; truncating it drops Mike's instructions | built from workspace files; trimmed to about 2.1 kB; the time to the minute and session notes ("emergency compression…") make it grow from run to run |
| Prompt tokens reused from the previous process | 0 (the model cannot be rolled back, see 3b.1) | 0 |
| Harness's own peak RSS | 36–38 MiB (6–7 MiB anonymous) | 31–32 MiB (7 MiB anonymous) |
| Model access | `llamacpp` provider, OpenAI-compatible | `vllm` provider entry, OpenAI-compatible |

**The point that matters most:** with a short system prompt sent directly, the same model answers "ouvre la calculatrice" with `launch_app(app="calculator")`. Its tool-call format is parsed correctly by `llama-server`. The failures come from the harnesses' long generic prompts, not from the tool-call path.

**Measurement notes:**
- **Time per request:** 8–30 s per model call, on a host loaded by other sessions' tests during the run, so these times say nothing about the harnesses themselves.
- **Forcing a call:** setting `tool_choice = "required"` through ZeroClaw's `provider_extra` made it loop on the model and never finish. It was stopped, and the setting is not used.

**Not done in 3b.2 (left open):**
- three scenarios: loading a terminal skill and proposing `ls ~` (that belongs to Step 7's plan catalogue); a preference remembered across a restart; refusing a forbidden action;
- NanoBot;
- reusing the Zenodo preprint's protocol: the preprint was not read or checked.

## 3b.3 — choice and RAM budget (proposal, for the user)

**Runtime:**
- `llama-server` from the official release, Q4_0, lean (`--no-repack -b 16 -ub 16`);
- one slot, context 2,048, `--cache-ram 0`;
- `--slot-save-path` with the fixed prefix saved once and restored before each request.

**Harness:** Mike's own chain. It is the only one that keeps Mike's rules together:
- one action per order;
- the keyword table first;
- the grammar;
- the adapter's checked templates;
- the user's acceptance before every action.

Today the chain is Python (`src/mike/mike_contract.py` and the tests). It could later be a small Go or Rust binary if the client's RSS matters on Luna.

**Budget on the desk host:**
- model server: about 306 MiB at peak, of which about 225 MiB is the model file, which the kernel can drop and reload;
- harness: Mike's own Python client is not measured as a separate process yet. A Go or Rust client would be in the 10–30 MiB range of the two harnesses above (an estimate);
- **total: about 320–340 MiB.**

**On Luna:** unknown until Step 4 (`luna-pi`), then Luna.

**Next steps to propose:**
- put the desktop state at the end of the prompt, so that the restored prefix covers almost all of it (a prompt change, to be measured);
- measure the same runtime on `luna-pi` (Step 4, needs its green light and a Luna-access slot).
