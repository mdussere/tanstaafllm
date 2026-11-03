# ZIPA-T small: phone recognition against eSpeak, on the desk host (plan step 11.5)

> **Freshness:** 🟢 current · **Written:** 2026-11-01 · **Checked:** 2026-11-01 · **Step:** mycroft 11.5 (desk and Luna)

**Date:** 2026-11-01
**Go:** the user, relayed by Professor on 2026-11-01. Phoneme assessment is offline scoring, not live. It must fit in Luna's memory, with Mannie and Mike stopped, and finish a few seconds after a short sentence.
**Scope:** desk host Termidor (x86_64, i5-4590), 2 threads; then Luna, at the end of this record.

## Setup

- **Model:** `anyspeech/zipa-small-noncausal-500k` on Hugging Face, INT8 ONNX: a 70.9 MB encoder, plus the decoder, the joiner and 127 IPA tokens. Licence CC BY 4.0.
- **Runtime: Sherpa-ONNX loads it as is.** Its own `sherpa-onnx-offline` binary (v1.13.8) decodes it as an offline transducer, with no PyTorch or lhotse. On Luna this means the same runtime family as Kroko: the aarch64 build already has the offline binary.
- **Expected phones:** eSpeak NG, `--ipa -v en-us`, from the sentence text.
- **Scoring:** `scripts/phone_score.py` normalises both sides coarsely, so that notation differences are not counted as errors:
  - it drops stress and length marks;
  - it counts the flap ɾ as t, and ɐ as ə;
  - it counts r-coloured vowels as ə˞.

  It then aligns the two sides and gives a phone error rate (PER) and the confusions. Unit tests: `test_phone_score.py`.
- **Harness:** `test/mycroft/test_zipa_phones.py` (integration). Evidence: `results/mycroft/zipa/20261101T165804Z/` (ignored by Git; the private reading's phones are in it).

## Results

| Audio | PER | Decode time / audio | Whole process CPU / audio (incl. load) | Peak RSS |
| --- | --- | --- | --- | --- |
| LibriSpeech clip 0 (6.6 s, native) | 0.097 | 0.037 | 0.57 | **282 MiB** |
| LibriSpeech clip 1 (16.7 s, native) | 0.056 | 0.047 | 0.28 | 363 MiB |
| The user's reading (94 s, one piece) | 0.127 | 0.12 | 0.16 | **3.2 GB** |

- **Native speech sets the floor.** On native clips the PER is 5.6–9.7 %. This floor is the gap between eSpeak's dictionary form and real speech (for example "brothels" /θ/ said as /f/), not ZIPA's errors alone. The user is at 12.7 %, a few points above it.
- **The user's main confusions:**
  - ʌ→ə ×8 and æ→ə ×8: "cut" and "cat" vowels reduced to a neutral one;
  - ə→u ×4, and r dropped ×4;
  - ɪ→i ×2: the "ship/sheep" case.

  These are typical of a French speaker. ZIPA reports them as plain phone pairs, which a tutor can name.
- **Memory grows with length.** ZIPA here is non-streaming: it encodes the whole file at once. A short sentence costs ~280 MiB, 17 s costs 363 MiB, and 94 s in one piece costs 3.2 GB. **On Luna, it must score one sentence at a time.** That suits the tutor anyway.
- **Time:** decoding is fast (0.04 s per second of audio on the desk host). Most of the cost is the load: about 3.5 s of CPU per run. With the usual desk-to-Luna ratio (15–20×, to verify), that would be about a minute to load on Luna. The tutor would load ZIPA once per session, with Mike and Mannie stopped, then score each sentence in seconds.

## On Luna (2026-11-01)

Professor's go, Mannie stopped, no reboot. `test/mycroft/test_luna_footprint.py::test_luna_11_5_zipa_phones` installed Sherpa's `sherpa-onnx-offline` beside the aarch64 runtime under `/storage/.local` and decoded LibriSpeech clip 0 (6.6 s) at 2 threads. Evidence: `results/mycroft/luna-footprint/20261101T171306Z/`.

| | Desk host | Luna |
| --- | --- | --- |
| Load | ~3.5 s CPU | **34.5 s** |
| Decode, 6.6 s clip | 0.25 s | **4.0 s** (0.6 s per second of audio) |
| Peak RSS | 282 MiB | **306 MiB** |

- **It meets the go's bar:** a short sentence is scored about 4 s after it is said, in about 300 MiB, with Mannie and Mike stopped. MemAvailable stayed at 640 MiB afterwards.
- **The load is the cost:** about 35 s, so ZIPA must be loaded once per tutor session and kept, never per sentence. A resident ZIPA beside resident Kroko English (162 MiB) is not measured yet.
- **The desk-to-Luna ratio** came out at about 10× for load and 16× for decoding.
