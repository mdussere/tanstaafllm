# Mycroft v0 model decision: Sherpa-ONNX French Zipformer (provisional)

**Status:** Step 4 complete, 2026-09-25. This is a pre-hardware v0 selection, not a Luna compatibility claim.

## Decision

Select **Sherpa-ONNX `v1.13.8` with the int8 French streaming Zipformer asset `sherpa-onnx-streaming-zipformer-fr-2023-04-14`** as the one Mycroft v0 model/runtime path to carry into Step 5. The deployed selection is the int8 encoder, decoder, joiner, and `tokens.txt` only; the full downloaded archive's fp32 files are not part of the selected asset set.

Keep `whisper.cpp v1.9.4` with `ggml-tiny-q5_1.bin` as the measured rejected challenger. Moonshine remains deferred evidence only.

This selection approves no product CLI, target build, target installation, microphone capture, service, GPU trial, or hardware change. Those need their own greenlights.

## Measurement environment and protocol

- Host: Linux x86_64, Intel Core i5-4590 (four cores, 3.30 GHz).
- Both commands: local native CPU decoder, French language/model, two threads, one cold process per fixture, no contextual prompt/hotword input, no GPU.
- Corpus: three included public Common Voice French WAVs (3.816 s, 6.336 s, and 7.128 s), mono 16-bit PCM at 16 kHz, with upstream references.
- Metrics: wall duration from child start to exit, 10 ms `/proc` RSS sampling, RTF from file duration, and lowercased Unicode word-error rate that ignores punctuation/whitespace.
- Values below are **desktop screening measurements**. They are not target latency, memory, battery, thermal, or target-fit results.

## Results

| Candidate | Fixture | WER | Elapsed | RTF | Sampled peak RSS |
| --- | --- | ---: | ---: | ---: | ---: |
| Sherpa int8 French Zipformer | 19364697 | 0.154 | 1.329 s | 0.186 | 213,668 KiB |
| Sherpa int8 French Zipformer | 19738183 | 0.182 | 1.153 s | 0.302 | 214,232 KiB |
| Sherpa int8 French Zipformer | 27024649 | 0.000 | 1.345 s | 0.212 | 213,392 KiB |
| Whisper Tiny q5_1 | 19364697 | 0.385 | 1.517 s | 0.213 | 133,308 KiB |
| Whisper Tiny q5_1 | 19738183 | 0.182 | 1.295 s | 0.339 | 132,856 KiB |
| Whisper Tiny q5_1 | 27024649 | 0.833 | 1.542 s | 0.243 | 133,252 KiB |

Sherpa was credible on all three upstream references, including the geographic-term clip; its remaining errors were a spelling/phonetic substitution (`ACHÉMÉNIDE` → `ASHÉMÉNIDE`) and tense/auxiliary loss. Whisper used about 80 MiB less sampled desktop RSS but distorted the geography-heavy fixture severely (`actionnaire majoritaire… conseil territorial… Miquelon` became largely unrelated text). Its memory advantage does not buy acceptance when the output fails the modest functional quality gate.

## Subsequent representative reading (private, 2026-09-25)
The same two pinned candidates were run sequentially on one consented 130-second French reading covering CLI interaction, code editing, interface navigation, and uncommon project terms. Sherpa recorded WER 0.134, 11.460 s elapsed, and 221,244 KiB sampled RSS; Whisper Tiny q5_1 recorded WER 0.427, 13.704 s, and 235,496 KiB.
Sherpa preserved all 13 instructions; Whisper omitted two code-editing instructions and degraded sharply on the final proper-noun stress sentence. This strengthens the provisional Sherpa selection, while remaining one private speaker/microphone and desktop measurement. It does not establish target fit or a general French WER.
The audio, raw transcripts, logs, and conversion are private temporary evidence; the auditable summary is [the representative-reading evaluation](0104_06_representative-reading-evaluation.md).
## Resource ledger

| Candidate | Evaluated runtime disk | Selected model disk | Total (desktop build/install) | Desktop RSS verdict | Selection verdict |
| --- | ---: | ---: | ---: | --- | --- |
| Sherpa | 75,000 KiB | 125,232 KiB (int8 components + tokens) | 200,232 KiB | ~214 MiB sampled | Selected for quality; target fit unproven |
| Whisper | 6,952 KiB (`bin/` only) | 31,400 KiB | 38,352 KiB | ~133 MiB sampled | Rejected: quality gate failure |

These totals are accounting aids, not a promise of package-minimised deployment size. The Sherpa release archive contains unrelated binaries and shared libraries; an eventual target package must inventory the exact required runtime files. Neither desktop RSS value proves sufficient OS/WM/Mike/Wyoh headroom within 1 GiB shared LPDDR3.

## Pinned artifacts

| Artifact | SHA-256 | Retrieval source |
| --- | --- | --- |
| Sherpa x64 CPU/no-TTS runtime archive `v1.13.8` | `d0f96c8b65c6cd0974fada22737e337de81bc8cd2abbec2e39caf358b1eec5fc` | [official release](https://github.com/k2-fsa/sherpa-onnx/releases/tag/v1.13.8) |
| French Zipformer archive | `77d4cbd61dcfa55fd2c14efc0ce5c6798be5931c05f35df5bab60c921950bb8c` | [official ASR models release](https://github.com/k2-fsa/sherpa-onnx/releases/tag/asr-models) |
| `whisper.cpp` source `v1.9.4` | `57e280cee375ab02425b806ad5146b99f6eb9357e3c2b31357c8a6af2e2e44ae` | [official source tag](https://github.com/ggml-org/whisper.cpp/tree/v1.9.4) |
| `ggml-tiny-q5_1.bin` | `818710568da3ca15689e31a743197b520007872ff9576237bda97bd1b469c3d7` | [upstream model repository](https://huggingface.co/ggerganov/whisper.cpp) |

The model/runtime and source licenses are recorded in the shortlist. Downloaded archives, weights, builds, and logs stay outside the repository.

## Limits and next evidence

1. The corpus is too small, too upstream-aligned, and lacks controlled ordinary-room noise and command-like speech. Do not infer French WER, accent coverage, or context-free command accuracy from it.
2. The current target description may mean RK3326/ARMv7 rather than AArch64. An aarch64 release artifact is evidence of a native ARM path, **not** proof of a compatible 32-bit distribution. Step 6 must identify delivered userland and toolchain before an ARM package is chosen.
3. The selected model's ~214 MiB desktop RSS could be unacceptable after Linux, frontend/WM, graphics, and future components take their shares. A selection only says it was the smallest candidate that cleared the present quality bar; it is not an exemption from the future headroom gate.
4. Step 5 should make one narrow on-demand, file-to-UTF-8 command around this selected native path. It must preserve this input/error contract and must not add context, a Python service, model downloads, or a resident process.
