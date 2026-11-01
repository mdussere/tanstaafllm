# A voice for Luna: English text-to-speech on the desk host (plan steps 11.1 and 11.2)

> **Freshness:** 🟢 current · **Written:** 2026-11-01 · **Checked:** 2026-11-01 · **Step:** mycroft 11.2–11.3

**Date:** 2026-11-01
**Go:** the user, relayed by Professor on 2026-11-01: "first text-to-speech tests… small offline TTS for English on the desk first… record samples for the user to judge".
**Scope:** desk host Termidor (x86_64, i5-4590), 2 threads. Nothing on Luna.

## 11.1 Shortlist

Sherpa-ONNX's `tts-models` release (checked 2026-11-01) packages every family named in the go, so one runtime covers them all. On Luna that means Sherpa's aarch64 build *with* TTS: Mycroft installed the `no-tts` build. Four English candidates were taken, smallest first:

| Model | Archive (SHA-256 prefix) | On disk | Licence |
| --- | --- | --- | --- |
| Piper `en_US-lessac-medium`, int8 (VITS) | 21.0 MB (`f1c6d029`) | 37 MB | Lessac voice: Blizzard 2013 licence, **to check before any redistribution** |
| Piper `en_GB-alan-medium`, int8 (VITS) | 21.1 MB (`f0b2526c`) | 37 MB | model card says "See URL": **to check** |
| Kitten TTS nano v0.8, int8 | 31.2 MB (`6fa5be85`) | 45 MB | Apache-2.0 (LICENSE shipped) |
| Kokoro v0.19, int8 | 103.2 MB (`c9f0dd39`) | 152 MB | Apache-2.0 (LICENSE shipped) |

Not taken this round: Matcha (needs a separate vocoder), Supertonic and Pocket TTS (85–100 MB int8), Kokoro multi-lingual (130+ MB), and the French Piper voices (French is second).

## 11.2 Desk measures

`test/mycroft/test_tts_candidates.py` (marker `integration`) runs each model in its own process (`tts_probe.py`, Sherpa-ONNX 1.13.8's Python wheel), on five sentences of Mike's and the tutor's kind, including Mycroft, Wyoh and Luna. Then Kroko English transcribes each WAV back: a cheap, automatic intelligibility check (round-trip WER). Evidence: `results/mycroft/tts/20261101T163339Z/` (ignored by Git; WAVs and report).

| | Piper Lessac | Piper Alan | Kitten nano | Kokoro |
| --- | --- | --- | --- | --- |
| Load | 2.2 s | 3.0 s | **1.1 s** | 2.4 s |
| Real-time factor (synthesis time / audio time) | 0.28 | **0.26** | 0.44 | 1.94 |
| Peak RSS (whole Python process) | **175 MiB** | 191 MiB | 183 MiB | 332 MiB |
| Round-trip WER through Kroko English | 0.066 | 0.056 | **0.052** | 0.100 |
| Sample rate | 22.05 kHz | 22.05 kHz | 24 kHz | 24 kHz |

- **Kokoro is out for Luna:** slower than real time already on the desk host (RTF 1.9), and twice the memory.
- **Piper and Kitten nano are the Luna candidates.** All three are understood by Kroko almost perfectly; the shared errors are the project names ("McRoft", "Wyo") and "in ship" heard as "and ship".
- **The RSS includes Python and the wheel** (~100 MiB of it is not the model); Mycroft's ctypes path would be lighter, as it was for Kroko.
- **Projection to Luna, to verify:** the desk-to-Luna ratio was about 16× for Kroko and ZIPA. On that basis Piper (RTF ~0.27 here) would take about 4–5 s per second of speech on Luna, so synthesising the next sentence while one is spoken, or a short wait, would matter; Kokoro would take about 30 s. Only a Luna run can say. (Corrected 2026-11-01: an earlier version said "around real time".)

## For the user

The four voices, the same five sentences each, were sent to the user as `tts-<model>.m4a` to judge how natural they sound. Their choice, plus the round-trip check, decides which voice goes to a Luna measure (11.3, with Mannie's go).

**The user's choice (2026-11-01):** by ear, Kokoro and Piper Lessac sound best. Kokoro costs about 7× Piper's CPU and 3× its model memory, and neither Alan nor Kitten nano is much lighter than Lessac, so **Piper Lessac is the voice for Luna**. Its licence (Blizzard 2013) must be checked before any redistribution.

## 11.3 Piper Lessac on Luna (2026-11-01)

The user's go ("measure, only Piper"), Professor's slot. Mannie on Luna stopped; the user's Mike window was open and idle (llama-server ~285 MiB resident, no request), so MemAvailable started at ~500 MiB instead of ~640. No reboot, no service touched. Sherpa's aarch64 `sherpa-onnx-offline-tts` (same libraries as the speech-to-text runtime already on Luna) and the Piper files (~40 MB) were installed under `/storage/.local`. `test_luna_footprint.py::test_luna_11_3_piper_lessac`: one fresh process per sentence, 2 threads, the five sentences above. Evidence: `results/mycroft/luna-footprint/20261101T192549Z/` (WAVs included).

| Measure | Luna |
| --- | --- |
| Load (process start to model ready, wall minus synthesis) | ~20 s |
| Synthesis time / audio time | 3.0–3.9 (about 10 s for a 3.0–3.4 s sentence) |
| Peak RSS (the binary, no Python) | 103–147 MiB |
| Lowest MemAvailable during a run | 352 MiB |
| CPU used | ~1.27 cores of 4 |

- **Close to the projection** (4–5×): Luna is about 11–13× slower than the desk host here.
- **For Mike, Piper must be resident** (load once, ~20 s) and speak sentence by sentence: the first sentence is heard about 3× its own length after the text is ready, and each next sentence can be synthesised while the previous one plays. Short first sentences matter.
- **Memory fits** beside resident Kroko English (162 MiB) and an idle Mike, with ~350 MiB left; not measured all three at once.
- **For the tutor**, model sentences can be synthesised ahead of time and kept.
