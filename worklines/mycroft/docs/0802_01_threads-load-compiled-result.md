# Mycroft on Luna — threads, load time, compiled code (plan steps 8.2, 8.3, 8.4)

**Date:** 2026-10-11
**Green light:** the user, 2026-10-11 ("go" 8.2, 8.3, 8.4; Luna given directly, confirmed by Professor).
**Status:** measured. Luna rebooted before and after, then released. The user reviews this before 8.5.
**Evidence:** `results/mycroft/luna-footprint/20261011T113040Z/` (extra files installed by `…/20261011T112530Z/`: 10 files, 129.7 MB, checked by SHA-256).
**Command:** `MYCROFT_LUNA_LIVE=1 MYCROFT_LUNA_REBOOT=1 MYCROFT_ASSET_ROOT=… uv run pytest test/mycroft/test_luna_footprint.py::test_luna_8_2_to_8_4_threads_load_compiled`

Same clip as 8.1: `common_voice_fr_19364697.wav`, 7.13 s. **Every run, at every thread count, in Python and in C++, with both models, gave the same text:** `ce site contient quatre tombeaux de la dynastie ashéménide et sept des sassandides`.

"RTF" is the real-time factor: decoding time divided by the audio length. Below 1, dictation keeps up with speech; above 1, it falls behind.

## 8.2 Threads

Python provider, decoding as fast as possible (two runs each):

| Threads | Decode | RTF | CPU time | Peak RSS |
| --- | --- | --- | --- | --- |
| 1 | 14.2–14.3 s | **2.0** | 30.6–31.7 s | 251–252 MiB |
| 2 | 9.4 s | **1.32** | 43.0 s | 253 MiB |
| 4 | 14.9–17.5 s | **2.1–2.5** | 72–78 s | 251 MiB |

Real-time replay through `mycroft_dictate.py` (what dictation would feel like):

| Threads | `ready` → first text | Lag at the end of the clip | CPU (share of one core) |
| --- | --- | --- | --- |
| 1 (8.1) | 3.1 s | 8.2 s | 0.9 |
| 2 | 2.2 s | **3.5–3.7 s** | 1.5 |
| 4 | 2.6–3.0 s | 9.2–9.5 s | 2.2 |

- **2 threads is the best setting**: a third faster than 1 thread.
- **4 threads is worse than 1**: it burns 2.5 times the CPU for slower decoding. Likely causes are the A35's shared memory bandwidth and ONNX Runtime's thread pool spinning. The cause wasn't investigated.
- **Even at 2 threads, the model is slower than real time** (RTF 1.32). On a 7-second sentence the text ends 3.6 s after the speaker stops, and the lag grows with longer speech.

## 8.3 Load time

Breakdown at 1 thread (the session creation doesn't depend on the thread count: 16.9–17.0 s at 1, 2 and 4):

| Phase | Cold (page cache dropped) | Warm |
| --- | --- | --- |
| Read the 123 MB of model files | 2.3 s | 0.22 s |
| Load the libraries | 0.5 s | 0.02 s |
| **Create the ONNX Runtime session** | **17.8 s** | **16.7–16.9 s** |

**The load is CPU work in ONNX Runtime's session creation, not I/O.** This confirms the user's doubt and Professor's note `0703_02`.

The pre-optimised "onnx-extended" model (graph optimised once on the desk host, then loaded by the same Sherpa) gave the same text and the same decoding speed:

| Model | Session creation | Decode RTF | Peak RSS |
| --- | --- | --- | --- |
| Original | 16.7–16.9 s | 2.0 | 251–252 MiB |
| Pre-optimised "extended" | **13.2–13.3 s** | 2.0 | 248–251 MiB |

It saves **3.6 s (about 21 %)**. The remaining ~13 s is probably the int8 weight pre-packing, which ONNX Runtime redoes at each start. Whether it can be saved ahead of time is unverified (note `0703_02` §3.3). The variant was made on x86; making it on aarch64, as `0703_02` advises, was not tried.

## 8.4 Python against compiled code

Sherpa's own prebuilt C++ binary (`bin/sherpa-onnx`, same libraries, model, clip and threads), two runs each:

| Threads | Recogniser created | Decode | RTF | Peak RSS | CPU time |
| --- | --- | --- | --- | --- | --- |
| 1 | 17.0 s | 16 s | 2.3 | 235–238 MiB | 32.0 s |
| 2 | 17.0 s | 10–11 s | 1.5 | 235–238 MiB | 44.8 s |
| 4 | 17.0–17.1 s | 19 s | 2.6–2.7 | 236–238 MiB | 81–86 s |

Compared with Python at the same thread count:

- **load time:** the same (17.0 s against 16.7–17.0 s);
- **decoding:** not faster; slightly slower in the binary, which feeds the audio differently;
- **memory:** the binary uses **about 15 MiB less** (236 against 252 MiB).

**Python costs about 15 MiB and nothing measurable in speed.** The heavy work is in ONNX Runtime's compiled kernels either way. Moving Mycroft to compiled code would save 15 MiB and fix neither the load time nor the real-time speed.

## Conclusions for 8.7 (to decide with the user)

1. **Threads:** 2 is the right default on Luna. Not yet set in the code; that is 8.7's job.
2. **Load:** pre-optimising saves ~3.6 s but leaves ~13 s, still too long for a button. Only a **resident provider** (8.6) removes it from the user's wait, at the cost of ~250 MiB kept in memory.
3. **Compiled code:** not worth it for speed; only 15 MiB.
4. **The real blocker is decoding speed.** At RTF 1.32 with 2 threads, this model can't keep up with speech on the A35. Candidates for later steps:
   - int8 against fp32 (8.5): the A35 lacks int8 dot-product instructions;
   - a smaller or faster French model;
   - ONNX Runtime thread settings (spinning);
   - the parked GPU route.
