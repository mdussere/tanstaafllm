# Kroko on luna-pi, with a projection to Luna (plan step 9.3)

**Date:** 2026-10-11
**Context:** the user asked to measure on `luna-pi` before Luna. `luna-pi` is aarch64 like Luna, nobody was using it, and Professor gave it to Mycroft. The Luna run was stopped during its upload; Luna was rebooted and released.
**Machine:** `luna-pi`, Raspberry Pi 4: 4 × Cortex-A72 at up to 1.8 GHz, 8 GB RAM, Debian kernel 6.18 aarch64, Python 3.13.5, glibc 2.41. The user's own SSH session (with an idle `claude` process) was open, so `luna-pi` was **not rebooted**.
**Install:** everything under `~/.local/opt/mycroft` and `~/.local/share/tanstfaafllm/mycroft`, checked by SHA-256. ONNX Runtime 1.28.0's Python package was installed for diagnosis in a venv, `~/.local/opt/mycroft-ort-venv`. No system change.

## 1. Kroko against the current model (Sherpa's C++ binary)

Command: `MYCROFT_TARGET=luna-pi MYCROFT_LUNA_LIVE=1 MYCROFT_ASSET_ROOT=… uv run pytest test/mycroft/test_luna_footprint.py::test_luna_9_3_kroko`. Evidence: `results/mycroft/luna-pi-footprint/20261011T203640Z/step-9-3-kroko.json`.

Each value is the mean of 2 runs on 2 clips (the 7.1 s Common Voice clip and Kroko's own 0.wav). Text was identical across runs.

| | Current, 1 thread | Current, 2 threads | Kroko, 1 thread | Kroko, 2 threads |
| --- | --- | --- | --- | --- |
| Real-time factor | 0.52 | 0.37 | 0.27 | **0.20** |
| Load (recogniser created) | 4.1 s | 4.1 s | 10.7 s | 11.0 s |
| Peak RSS | 222 MiB | 222 MiB | 158 MiB | 159 MiB |

Kroko decodes **1.9× faster** and uses **63 MiB less**, but **loads 2.6× more slowly**. That is the same pattern as on the desk host (`0903_01`).

## 2. Why Kroko loads slowly

`test/mycroft/ort_session_profile.py`, run in the venv on `luna-pi`, times session creation with one thread:

| File | Optimisation off | Basic | Extended | All | All-optimised file saved here, reloaded with optimisation off |
| --- | --- | --- | --- | --- | --- |
| Kroko `encoder.onnx` (70 MB, fp32) | **5.09 s** | 5.94 s | 5.70 s | 5.74 s | **2.41 s** |
| Kroko decoder and joiner | < 0.01 s | | | | |
| Current int8 encoder (127 MB) | 1.68 s | 1.94 s | 2.05 s | 2.07 s | 1.24 s |

- **The time is not graph optimisation.** Kroko's encoder takes 5.1 s even with optimisation off.
- **The file as published is costly to open.** The same graph saved again by ONNX Runtime on this machine opens in 2.4 s. The cause inside the file was not identified; constant folding baked in at save time is a likely candidate.
- Sherpa takes about twice the time of a bare ONNX Runtime session for both models (11.0 s against 5.7 s for Kroko, and 4.1 s against 2.1 s for the current model). The reason is not identified.

### Kroko prepared once on aarch64, then used by Sherpa

The three files were saved at the portable "extended" level on `luna-pi` (`~/.local/opt/mycroft/kroko-extended-aarch64/`, tokens copied) and decoded by the same binary at 2 threads:

| Kroko files | Load | RTF | Text |
| --- | --- | --- | --- |
| As published | 10.98 s, 11.03 s | 0.20 | identical |
| Prepared on aarch64 | **6.14 s, 6.10 s** | 0.19–0.20 | identical |

**The load is 44 % shorter, at no cost.** The "all" level was not used for this file, because ONNX Runtime warns that it may contain hardware-specific layouts.

## 3. Projection to Luna (estimate, not a measurement)

For the current model, the same C++ binary is **4.1–4.4× slower** to decode on Luna than on `luna-pi` (RTF 2.3/0.52 at 1 thread, 1.5/0.37 at 2 threads, from `0802_01`), and **4.15× slower** to load (17.0 s against 4.1 s). Applying the same ratios to Kroko:

| Kroko on Luna (estimated) | 1 thread | 2 threads |
| --- | --- | --- |
| Real-time factor | ~1.2 | **~0.8** |
| Load as published | ~45 s | ~45 s |
| Load prepared on aarch64 | ~25 s | ~25 s |
| Peak RSS | ~160 MiB | ~160 MiB |

If it holds, Kroko at 2 threads would be the first model to **keep up with speech on Luna** (the current model is at 1.5). But at ~25 s, the load would still force a **resident** process, costing ~160 MiB instead of ~250 MiB. The estimate assumes Kroko scales between the A72 and the A35 like the current model, which only a Luna run can confirm.

## Next (to decide with the user)

1. Measure Kroko on Luna, as published and prepared, at 2 threads: load, RTF, RSS.
2. If the projection holds: adapt Mycroft's adapter to Kroko's files and output (punctuation and case), and confirm its licence.
3. Then the resident provider (the 8.6 probe, applied to Kroko), and known words on Kroko.
