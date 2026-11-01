# A voice for Luna: English text-to-speech on the desk host (plan steps 11.1 and 11.2)

> **Freshness:** 🟢 current · **Written:** 2026-11-01 · **Checked:** 2026-11-01 · **Step:** mycroft 11.2

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
- **Projection to Luna, to verify:** the desk-to-Luna ratio was about 15–20× for speech-to-text. On that basis Piper (RTF ~0.27 here) would be around real time on Luna or slower, so speaking sentence by sentence while the next one is synthesised would matter. Only a Luna run can say.

## For the user

The four voices, the same five sentences each, were sent to the user as `tts-<model>.m4a` to judge how natural they sound. Their choice, plus the round-trip check, decides which voice goes to a Luna measure (11.3, with Mannie's go).
