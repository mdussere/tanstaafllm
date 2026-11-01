# Small tools for automatic speech assessment (plan step 11.4, survey)

> **Freshness:** 🟢 current · **Written:** 2026-11-01 · **Checked:** 2026-11-01 · **Step:** mycroft 11.4

**Date:** 2026-11-01
**Go:** the user, relayed by Professor on 2026-11-01. Desk survey only; nothing installed on Luna or deployed.
**Two uses:** judge Luna's own text-to-speech automatically (`1102_01`), and score the user's spoken English for the tutor idea. Reusable later by Camp Currie L-CAT (`worklines/project/camp-currie/`).
**Evidence level:** sizes and licences below come from the projects' own pages as known on 2026-11-01 and were **not re-checked or measured here**, except where a row says "measured". Anything marked "verify" must be confirmed before adoption.

## What each family really measures

| Need | Tool | What it measures, really | Size / CPU | Licence | ARM / Luna fit |
| --- | --- | --- | --- | --- | --- |
| **Intelligibility** | Kroko English round-trip (Mycroft) | Whether an ASR recovers the intended words; word-level, not phonemes | already resident on Luna, 152 MiB; **measured** (`1102_01`, and the user's reading in `1001_01`) | CC-BY-SA stated, text missing (9.3) | **Yes, today** |
| **Rhythm: pauses, speech rate** | Kroko's own result fields (`tokens`, `timestamps`, proposed 9.9) | Word timing, so words per second and pause lengths | free: the same decode | as above | **Yes**, once 9.9 reads the fields |
| | Silero VAD | Speech / non-speech per 30 ms frame, so pauses and speaking time | ~2 MB ONNX; tiny CPU | MIT | **Yes**: Sherpa-ONNX supports it on the same runtime (verify in 1.13.8's C API) |
| **Intonation (F0)** | pYIN (librosa) | Pitch contour and voicing; compare the user's contour with the TTS reference sentence | numpy only, light | ISC | Possible, but adds numpy/librosa to Luna's Python, which today is stdlib-only |
| | Parselmouth (Praat in Python) | F0, intensity, formants, jitter/shimmer; Praat's syllable-nuclei script gives speech rate | a few MB, light | **GPL-3.0** | Desk first; the licence matters if it ships |
| | CREPE (tiny) | Neural F0, more robust in noise than pYIN | small (tiny variant); needs TensorFlow/PyTorch or an ONNX export | MIT | Only via an ONNX export (verify) |
| **Timbre** | MFCC (librosa, `python_speech_features`) | Spectral envelope; a voice-quality fingerprint, not a judgement | trivial | ISC / MIT | Yes, with numpy |
| | Speaker embeddings in Sherpa-ONNX (3D-Speaker, WeSpeaker, NeMo TitaNet small) | Who is speaking; distance between two voices | ~7–30 MB ONNX (verify) | Apache-2.0 for most (verify per model) | **Yes**, same runtime; useful to check the TTS voice stays consistent, little use for teaching |
| **Overall quality / naturalness** | UTMOS (22 "strong", v2) | Predicted MOS of synthetic speech, trained on TTS listening tests: **the right tool for judging our TTS** | wav2vec2-based, ~100 M parameters and more; PyTorch | MIT (verify) | **Desk only** |
| | DNSMOS (P.835) | Signal, background noise, overall quality, trained for **noise suppression**, not TTS naturalness | small ONNX models | verify (Microsoft DNS Challenge repo) | Possible, but measures the wrong thing for us |
| | torchaudio SQUIM (objective / subjective) | Reference-free STOI/PESQ/SI-SDR estimates; MOS with a non-matching reference | PyTorch | BSD-2 (torchaudio) | **Desk only** (PyTorch) |
| **Pronunciation** | Phoneme recogniser: wav2vec2 fine-tuned on eSpeak phonemes (e.g. `facebook/wav2vec2-lv-60-espeak-cv-ft`) | Which phonemes were said, against eSpeak's expected phonemes for the sentence; basis for goodness-of-pronunciation (GOP) per phoneme | ~300 M parameters; PyTorch | Apache-2.0 (verify) | **Desk only** |
| | GOP from Kaldi or CTC posteriors | Per-phoneme confidence that the expected phoneme was said: "ship" vs "sheep" | depends on the acoustic model | Kaldi: Apache-2.0 | Desk; on Luna only with a small phoneme model, none found yet |
| | Allosaurus | Universal phone recogniser, language-independent | small; PyTorch | **GPL-3.0** (verify) | Desk |

## Recommendation

1. **On Luna, now, at almost no cost:** intelligibility by Kroko English round-trip, plus rhythm from Kroko's timestamps (9.9) or Silero VAD. That already answers "did Luna understand you, and how fluent was it" for the tutor, and "is our TTS intelligible" for the voice choice.
2. **For intonation:** pYIN on the user's sentence against the same sentence spoken by Luna's TTS voice, compared as contours. Worth one desk experiment; it needs numpy on Luna, which is a dependency decision for Mannie.
3. **On the desk only, to choose the TTS voice:** UTMOS, on the samples of `1102_01`, beside the user's own listening. Not for Luna.
4. **Pronunciation scoring ("ship" vs "sheep")** needs a phoneme recogniser, and the good ones are ~300 M parameters: desk or Mannie, not Luna. A small phoneme model for Sherpa would change that; none was found in this survey.
5. **Skip for now:** DNSMOS (measures noise suppression), SQUIM (PyTorch, no gain over UTMOS for us), speaker embeddings (no teaching value).

**Next, if the user wants it:** one desk experiment combining 1–3 on the user's English reading (`1003_01`) and the four TTS voices.
