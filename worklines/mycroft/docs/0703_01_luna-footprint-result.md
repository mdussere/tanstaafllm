# Mycroft footprint on Luna — first measurement (plan step 8.1, formerly 7.3b)

> **Freshness:** 🟡 historical · **Written:** 2026-10-13 · **Checked:** 2026-10-31 · **Step:** mycroft 7.3 ✅

**Date:** 2026-10-11
**Green light:** the user, 2026-10-11 (then numbered 7.3b; now plan step 8.1). Luna slot given by Professor at 12:38 (`worklines/luna-access.md`).
**Status:** measured on replay; Luna rebooted and released. Live microphone not measured (Luna Step 8).

## What was run

| Phase | Command | Evidence |
| --- | --- | --- |
| Preflight (read-only) | `MYCROFT_LUNA_LIVE=1 … uv run pytest test/mycroft/test_luna_footprint.py::test_luna_preflight` | `results/mycroft/luna-footprint/20261011T103545Z/` |
| Install | `…::test_luna_install_bundle` | `results/mycroft/luna-footprint/20261011T103603Z/` |
| Measure | `MYCROFT_LUNA_REBOOT=1 …::test_luna_footprint_replay` | `results/mycroft/luna-footprint/20261011T103907Z/` |

**Install.** 10 files (167.7 MB) were placed under `/storage/.local/opt/mycroft/` (prebuilt aarch64 Sherpa libraries, the model's int8 files, tokens, one public WAV) and `/storage/.local/share/tanstfaafllm/mycroft/` (scripts and probe). Every file was checked by SHA-256. The transfer took 179 s, about 0.9 MB/s. No package was installed, and nothing outside `/storage` was changed.

**Device.** ArchR on `archr-9025`: kernel 6.12.94 aarch64, 4 cores, Python 3.13.5, glibc 2.40, libstdc++ up to `GLIBCXX_3.4.33` (Sherpa needs 2.17 / 3.4.19), MemTotal 983 MiB, 25 GB free on `/storage`.

**Measurement.** Luna was rebooted and the 1-minute load waited below 0.5. The probe then ran `mycroft_dictate.py` three times on `common_voice_fr_19364697.wav` (7.13 s, replayed in real time), with the v0 profile: int8, CPU, **one thread**, greedy search. Peak RSS and CPU time come from the kernel at exit (`wait4`). Luna was rebooted again afterwards.

## Results

| Measure | Run 1 | Run 2 | Run 3 | Desk host (x86_64) |
| --- | --- | --- | --- | --- |
| Start → `ready` (model load) | 20.2 s | 17.7 s | 17.7 s | 1.3 s |
| `ready` → first `partial` | 3.1 s | 3.1 s | 3.1 s | 1.3 s |
| `ready` → `final` | 15.3 s | 15.3 s | 15.3 s | 7.1 s |
| Lag after the audio ends | 8.2 s | 8.2 s | 8.2 s | 0.015 s |
| Peak RSS | 252.2 MiB | 251.5 MiB | 253.1 MiB | 216.5 MiB |
| CPU time (user + system) | 31.8 s | 31.1 s | 31.1 s | 2.3 s |
| Share of one core over the run | 88 % | 93 % | 93 % | 23 % |
| Lowest `MemAvailable` during the run | 536 MiB | 545 MiB | 537 MiB | — |

`MemAvailable` before the runs was 795 MiB, so the provider uses about **260 MiB** of the system's free memory. The final text was identical on all three runs and on the desk host: `ce site contient quatre tombeaux de la dynastie ashéménide et sept des sassandides`.

## What this means

- **Memory fits, but is large.** About 250 MiB is a quarter of Luna's RAM. With Sway, the Slate and the gamepad daemon running, about 535 MiB stayed available. Running a second model beside it (for example Mike's, the local brain; named Mannie at the time of this measurement) would be tight.
- **One thread is too slow for live dictation.** Decoding takes about 2.1 times the audio length (15.3 s for 7.1 s), so the text falls further behind the longer one speaks. One core is saturated while three are idle.
- **Loading takes about 18 s** before the first word can be recognised. For dictation started from a button, that is too long to repeat on every press.

## Proposed next measurements (now plan steps 8.2–8.6)

1. **Threads:** the same run with 2 and 4 Sherpa threads. The other three cores are idle, so this is the cheapest lever on real-time speed. It needs a thread setting in the provider. The pinned v0 profile says one thread, so this is a profile change to decide.
2. **Load time:** check where the 18 s goes (ONNX Runtime graph optimisation versus reading 123 MB from the card), and whether keeping the provider warm, a pre-optimised model, or a smaller model removes it.
3. **Live microphone:** once Luna Step 8 locates the microphone.

## Limits

- Replay from a file, not live capture: `arecord` adds a little CPU that is not counted here.
- One 7-second public clip. Longer dictation would show the growing lag more clearly.
- Measured right after a reboot, with Wyoh's session idle. A busy Sway or an app beside it would change the figures.
