# Mycroft v0 candidate shortlist

> **Freshness:** 🟡 historical · **Written:** 2026-09-27 · **Checked:** 2026-10-31 · **Step:** mycroft 1.2 ✅

**Status:** Step 2 evidence, 2026-09-25. Hands-on candidates are capped at two.

## Decision

| Candidate | Role | Hands-on status | Why |
| --- | --- | --- | --- |
| Sherpa-ONNX streaming French Zipformer | Primary | Admitted | Purpose-built French streaming model; documented native C/C++ APIs and current Linux x64 and Linux aarch64 CPU release artifacts. |
| `whisper.cpp` Tiny, quantised | Challenger | Admitted | Offline native C/C++ inference path and a small multilingual baseline. Its quantised asset must be built/verified and compared; the unquantised Tiny download is not the intended deployment asset. |
| Moonshine Tiny | Evidence only | Deferred | Not allowed to become a third implementation. A French checkpoint, licence, and native ARM/Linux deployable path have not been pinned in this work order. |

## Pinned evaluation sources

| Item | Pin / source | Licence / support evidence | Target-path note |
| --- | --- | --- | --- |
| Sherpa runtime | `k2-fsa/sherpa-onnx` release `v1.13.8`, CPU shared/no-TTS archive | Apache-2.0 repository licence; official C and C++ public APIs. | Release provides `linux-aarch64-shared-cpu` artifact as well as desktop x64. ARMv7/RK3326 compatibility still needs hardware/toolchain verification. |
| French Zipformer asset | `sherpa-onnx-streaming-zipformer-fr-2023-04-14` from the project `asr-models` release | Model card identifies French Common Voice training and Apache-2.0. | 16-bit mono WAVE decoder path documented; exact extracted size/checksum are recorded with test results. |
| Whisper runtime | `ggml-org/whisper.cpp` release `v1.9.4` / source tag | MIT licence. | Native C/C++ project; target build must explicitly disable host-only CPU tuning and be proven on delivered ARM hardware. |
| Whisper Tiny source asset | `ggerganov/whisper.cpp` `ggml-tiny.bin` | Upstream model download documentation lists Tiny at roughly 75 MiB. The underlying Whisper code/model licensing must be retained with deployment evidence. | A local q5 quantisation attempt is part of this comparison; it is not assumed to reduce RSS proportionally. |

Official references: [Sherpa French model guide](https://k2-fsa.github.io/sherpa/onnx/pretrained_models/online-transducer/zipformer-transducer-models.html), [Sherpa native C API](https://k2-fsa.github.io/sherpa/onnx/c-api/html/index.html), [Sherpa release](https://github.com/k2-fsa/sherpa-onnx/releases/tag/v1.13.8), [French model card](https://huggingface.co/shaojieli/icefall-asr-commonvoice-fr-pruned-transducer-stateless7-streaming-2023-04-02), [`whisper.cpp` release](https://github.com/ggml-org/whisper.cpp/releases/tag/v1.9.4), and [`whisper.cpp` model guide](https://github.com/ggml-org/whisper.cpp/blob/master/models/README.md).

## Explicit exclusions

- Cloud and API ASR: violates offline and dependency gates.
- A Python-only deployment path: rejected for target deployment. A desktop-only harness may use standard-library Python to measure native child processes; it is not the product runtime.
- GPU/Vulkan variants: unmeasured, potentially consume shared RAM, and out of v0 scope.
- More models: a third hands-on candidate weakens the evidence while spending build, storage, and comparison time. TANSTAAFL applies to evaluation too.

## What this evidence does not establish

The release availability establishes an aarch64 path, not a working RK3326 build or acceptable 1-GiB memory use. The French asset is from 2023 and is treated as a known, reproducible baseline rather than a claim of current best quality. The Step 4 record will state measured desktop values and retain target compatibility as unproven until hardware validation.
