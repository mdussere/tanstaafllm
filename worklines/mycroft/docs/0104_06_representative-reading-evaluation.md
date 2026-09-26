# Representative-reading evaluation: one private long-form French recording

**Status:** Step 4 evidence supplement, 2026-09-25. This is one consented, private recording; it strengthens the desktop comparison but is not a French population-accuracy or Luna-fit claim.

**Question answered:** How do the two approved candidates behave on one long recording designed around Mycroft's likely CLI, code-editing, and controller-interface vocabulary?

## Input and privacy boundary

The speaker supplied the recording after reading the canonical 13-phrase script in [0105_01_representative-reading-script.md](0105_01_representative-reading-script.md). The source was a 2 min 10.07 s AAC M4A, stereo at 48 kHz. It was converted explicitly to mono, 16 kHz, signed 16-bit PCM WAV for the existing harness.

The original M4A, converted WAV, manifest, JSON Lines, and full logs are private temporary evidence, not repository artifacts. The source audio remains unmodified. `worklines/mycroft/data/.gitignore` blocks M4A and WAV files from an accidental commit.

## Equal conditions

- Host: Linux x86_64, four-core Intel i5-4590.
- One cold local CPU process per candidate, run sequentially; two decoder threads; no GPU, network, prompt, hotword list, or context biasing.
- Candidates: Sherpa-ONNX v1.13.8 / French int8 Zipformer and whisper.cpp v1.9.4 / ggml-tiny-q5_1, French fixed for Whisper.
- The existing harness used the canonical script as reference and its normalised word-error rate: Unicode NFC, lowercase, accents retained, punctuation and whitespace ignored, then word-level Levenshtein distance.
- Temporary commands and full records: `/tmp/tanstfaafllm-mycroft/representative-{sherpa,whisper}-20260925.jsonl`; full logs carry the timestamp `20260925_220622` in the same directory.

## Results

| Candidate | WER (lower is better) | Elapsed | RTF | Sampled peak RSS |
| --- | ---: | ---: | ---: | ---: |
| Sherpa-ONNX French Zipformer int8 | **0.134** | **11.460 s** | **0.088** | **221,244 KiB** (about 216 MiB) |
| whisper.cpp Tiny q5_1 | 0.427 | 13.704 s | 0.105 | 235,496 KiB (about 230 MiB) |

On this recording, Sherpa has a 0.293 absolute WER advantage, or about a 68.5% relative reduction in WER over Whisper Tiny q5_1. It was also 2.24 s faster. These are desktop screening measurements only. They do not predict RK3326 latency, thermal behaviour, or available Luna memory.

The long file changes the desktop memory picture: Whisper's sampled RSS is about 230 MiB here, rather than its roughly 133 MiB on the three 4–7 second public smoke clips. That is an observed workload difference, not a target-memory conclusion. Sherpa remains near its earlier roughly 214 MiB desktop range.

## Qualitative comparison by script group

| Script group | Sherpa observation | Whisper Tiny observation |
| --- | --- | --- |
| 01 — CLI | Preserves every sentence and the command structure. It phonetically distorts `git status`, `README`, and `WAV`. | Keeps the broad meaning of the first sentence, but strongly distorts spoken file spelling and several command words. |
| 02 — Code editing | Preserves all three sentences. `benchmark underscore ASR point py` and `WER` are phonetically distorted, but the surrounding action is retained. | Omits 02.1 and 02.2 altogether, jumping from the CLI safety instruction to a degraded version of 02.3. |
| 03 — Interface | Preserves navigation, selection, dialog, and observation actions with small inflection errors. | Preserves more of this ordinary French group, but alters verbs and several nouns. |
| 04 — General and stress vocabulary | Preserves the constraint sentence and most of the Saint-Pierre-et-Miquelon sentence; it misses or changes `TANSTAAFL`, `RAM`, and some uncommon proper nouns. | `TANSTAAFL`, `Luna`, the uncommon names, and the final geographic/historical sentence become mostly unrelated phonetic text. |

Neither candidate reliably transcribes deliberately spoken punctuation names such as `underscore` and `point`, or project-specific identifiers, without vocabulary biasing. That is an honest baseline limitation: Mycroft v0 deliberately has no contextual vocabulary injection. A later command layer may address a bounded vocabulary, but it must be evaluated as a separate feature rather than silently counted as ASR quality.

## Decision impact

The result strengthens, but does not reopen, the provisional Step 4 choice of Sherpa-ONNX French Zipformer over Whisper Tiny q5_1:

1. Sherpa is lower-WER, faster, and preserves all 13 intended instructions on this longer, representative recording.
2. Whisper's prior short-clip memory advantage is not reproduced on this 130-second input; it is slightly higher in the current desktop sample.
3. One speaker, one microphone, quiet conditions, and a scripted reading are insufficient to claim general French accuracy. The later corpus still needs additional speakers and ordinary-room/noise variation.
4. Neither result clears the separate Luna resource gate. Target fit remains unproven.
