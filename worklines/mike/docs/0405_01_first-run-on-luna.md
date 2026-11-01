# Step 4.5 — Mike's first run on Luna

> **Freshness:** 🟡 historical · **Written:** 2026-10-30 · **Checked:** 2026-10-31 · **Step:** mike 4.5 ✅

**Question answered:** does Mike's 3b runtime run on Luna, and how fast and how big is it there?<br>
**Date:** 2026-10-25<br>
**Status:** measured on Luna (R36 Ultra, Cortex-A35 ×4, Arch Linux ARM), as `michael`.
- **Authorisation:** the user, relayed by Professor ("Stop Mannie on Luna and supervise Mike for a first run on Luna."). Professor gave the go after Mannie on Luna had stopped.
- **Conditions:** Wyoh's session and the resident Kroko were left running.
- **Cut short:** the run was stopped after three requests. The user: "one question is enough".

**Evidence:** `results/mike/luna-first-run/20261025T202817Z/` (server log, `console.log` with each request), plus `20261025T203521Z/` for the 2-thread prefix. Test: `test/mike/test_luna_first_run.py` (`luna_first_run.feature`, marker `live`).

## What ran

| Item | Value |
| --- | --- |
| Runtime | llama.cpp b11429 `llama-server` arm64 release (sha256 `ed44c0f7…e00b`), lean: `--no-repack -b 16 -ub 16`, context 2,048, one slot, `--cache-ram 0` |
| Model | LFM2.5-350M Q4_0 (sha256 `85e32858…2f50`) |
| Install | `/home/michael/.local/opt/mike/`: the release, the model and a slot directory; no packages, no services |
| Prompt | v4 (tools, French verb table, desktop state), constrained by the contract grammar. The shared 400-token prefix is saved once and restored before each request |
| Lock | `/tmp/luna-brain.lock` held as `mike <server pid>` for the run, then removed |

## Results (4 threads)

| Measure | Value |
| --- | --- |
| Model load (start to listening) | **3.5 s** |
| Shared prefix (400 tokens), once | 44.1 s (9.1 tokens/s) |
| Server RSS during requests | **about 300–307 MiB** |
| `MemAvailable` | about 650–665 MiB before; **lowest 562 MiB** during requests; 635 MiB after stop |
| Prompt read per request (about 682 tokens after the prefix) | **100–105 s** (6.6–6.8 tokens/s) |
| Answer (11–12 tokens) | 2.6–2.8 s (3.9 tokens/s) |
| **Total per request** | **about 103–108 s** |

At 2 threads, the 400-token prefix took 75.0 s (5.3 tokens/s), against 44.1 s at 4 threads. On this model, 4 threads read the prompt faster, even with Kroko resident.

## The three requests (proposals only; nothing ran on the desktop)

| Request | Expected | Model's call | After the adapter |
| --- | --- | --- | --- |
| ouvre la calculatrice | `launch_app(calculator)` | `focus_window(calculator)` | rewritten to launch, then refused: the calculator's launch command is not known yet (from Wyoh's entry) |
| lance le terminal | `launch_app(terminal)` | `launch_app(terminal)`: right | right |
| démarre l'éditeur de texte | `launch_app(editor)` | `focus_window(editor)` | rewritten to `launch_app(editor)`: right |

## What it means

- **It runs, and memory is not the problem.**
  - The official arm64 build works on the A35. Its backend list includes an ARMv8.0 CPU variant.
  - About 300 MiB of RSS leaves more than 550 MiB available, with Wyoh and Kroko running.
- **Speed is the problem: about 105 s per request, against a budget of 1 s.**
  - **The cause:** almost all of it is reading the ~680 prompt tokens that are not in the restored prefix (the desktop state and the request), at about 6.7 tokens/s.
  - **Compared with the desk host:** the same work takes 3.3 s on the desk (`docs/03b3_01`), so Luna is about 30 times slower here.
- **What would cut it, in order:**
  1. Put the desktop state at the end, so that the restored prefix covers almost the whole prompt. Only the request (about 20–40 tokens) would be read: about 5 s, if the reading speed holds.
  2. A shorter prompt.
  3. The keyword table first, so the model is not called at all for most requests.
  4. Step 7's small decider.
  - None of these is measured on Luna yet.
- **Problems on the way, all fixed in the test and none left on Luna:**
  - the slot directory was missing;
  - a nested noclobber blocked the log;
  - the SSH start hung until the server was detached with `setsid`;
  - an empty case list made the harness run the whole main set; it was stopped after three requests.
  - **Each time:** the server was stopped and the lock removed. A leftover server from an interrupted command was found and stopped too.

**Left on Luna:** the files under `/home/michael/.local/opt/mike/` (about 230 MB), for the next run. No server, no lock.

## 4.6 — the model's base speed, without any harness (user's request, 2026-10-25)

`llama-completion` alone, with no tools, grammar or prefix cache. It reads a fixed French Cluedo scene of 1,056 tokens (`test/mike/cluedo_prompt.txt`) and answers in 23 tokens: greedy, 4 threads, LFM2.5-350M Q4_0.

**Evidence:** `results/mike/raw-speed/` (desk and Luna runs, full logs). Luna had just rebooted; Wyoh's session was starting.

| Host | Setting | Prompt read | Generation | 1,056 tokens + 23 tokens |
| --- | --- | --- | --- | --- |
| Termidor (i5-4590) | lean (no repack, batch 16) | 174 tokens/s | 67 tokens/s | 6.4 s |
| Termidor | repack, default batch | 348 tokens/s | 59 tokens/s | 3.4 s |
| Luna (A35 ×4) | lean | **6.5 tokens/s** | **3.6 tokens/s** | **169 s** |
| Luna | repack, default batch | **6.9 tokens/s** | 2.8 tokens/s | 161 s |

**What it shows:**
- **The harness costs nothing measurable.** The model reads the prompt at the same speed in 4.5 (6.6–6.8 tokens/s) as here.
- **The model is the cost:** on Luna, about 150 ms per prompt token and 300 ms per answer token.
- **Repacking does not help on the A35:** about 6 % faster reading and slower generation, for more memory.
- **What that means for Mike on Luna:** a 1-second budget allows about 6 new prompt tokens and no answer. With 5 s, Mike could read a 20–30-token request and write a 10-token call, but only if everything before the request is restored from a saved state.
- **The answer itself was wrong.** The model repeated the question instead of naming the murderer. This prompt measures speed, not reasoning.
