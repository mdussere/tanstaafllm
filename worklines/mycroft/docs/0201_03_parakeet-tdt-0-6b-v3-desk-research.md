# Parakeet TDT 0.6B v3: desk research for Mycroft v0

**Status:** evidence-only review. No model, runtime, conversion, or benchmark was downloaded or run.

**Question answered:** Is NVIDIA Parakeet TDT 0.6B v3 a viable replacement candidate for Mycroft's offline French ASR on Luna?

## Short answer

It is a strong **desktop-class French ASR** candidate and a materially more appropriate ASR lead than a general audio model such as Gemma. It is nevertheless not viable for the current Luna v0 resource gate. NVIDIA states that it needs at least 2 GB of RAM to load, while Luna's provisional budget is 1 GiB of shared LPDDR3 before Linux, display, audio, and future components consume memory.

It therefore cannot become a third hands-on candidate under the present two-candidate plan. It may be useful later as a quality reference on a desktop, or as a candidate for a materially different device class, but it is not a credible Mycroft v0 deployment path for Luna on present evidence.

## What is promising

| Topic | Published evidence | Relevance |
| --- | --- | --- |
| ASR purpose | A 600-million-parameter multilingual speech-to-text model, rather than a general language model prompted to transcribe. | Good match for Mycroft's narrow audio-to-text boundary. |
| French | French is one of 25 supported European languages; language is detected automatically. | French is an explicitly supported language, not an inference from broad multilingual marketing. |
| Published French WER | NVIDIA reports 5.15% on FLEURS, 4.97% on MLS, and 6.05% on CoVoST, with greedy Transducer decoding and no external language model. Punctuation and capitalization are removed for this scoring. | Promising public quality evidence, but the three datasets and normaliser differ from Mycroft's corpus. These numbers must not be compared numerically with our three-fixture smoke test. |
| Local runtime | NVIDIA documents NeMo-Speech.cpp, a native C++ local runtime, with an official Q8 GGUF asset. | Better deployment shape than a Python-only path. It does not establish ARMv7 or Luna compatibility. |
| Long files | The model card documents long-file transcription. | Appropriate for the future representative recording; not a resource exception. |
| Licence | CC BY 4.0. | Permissive and compatible with local use, subject to attribution obligations. |

## The hard Luna rejection

| Cost signal | Published value | Why it fails the v0 ledger |
| --- | ---: | --- |
| Official stated load requirement | At least 2 GB RAM | Already twice Luna's entire 1 GiB shared-memory budget, before the operating system or application overhead. |
| Official raw weights | 2.51 GB | Storage alone is costly; raw disk size is not RAM, but it reinforces that this is not a small-model path. |
| Official Q8 GGUF asset | 714 MB | It may reduce storage, but it cannot override the published 2 GB load requirement or leave safe runtime headroom in Luna. |
| NIM offline profile | 5.681 GB CPU RAM at batch size 1024 | Not a single-file measurement and therefore not a direct Luna estimate; it is nevertheless directionally consistent with the rejection, not evidence of a fit. |

TANSTAAFL conclusion: no amount of quality advantage pays for memory that the device does not have. A community Q4 or ONNX conversion would be a separate, unverified artifact. It cannot be assumed to retain quality, support the same runtime, or fit in 1 GiB until an exact asset, peak RAM, and output regression are evidenced.

## Runtime and product limits

The official native C++ path is a welcome improvement over a NeMo/PyTorch deployment. However, NVIDIA's documented Parakeet TDT v3 path is **offline whole-utterance recognition**: it does not support cache-aware streaming, and streaming requests are rejected by the native runtime. This is acceptable for Mycroft v0's recorded-file contract, but it is not evidence for a future always-listening interaction design.

NVIDIA's documented model test hardware is NVIDIA GPU hardware; no published RK3326, Cortex-A35, ARMv7, Mali-G31, shared-memory, cold-start, or thermal evidence was found. Native C++ availability is not a target-device performance result.

## How to read a claim that it beats Whisper

The claim is plausible only when the comparison identifies both exact systems. It must state:

1. Parakeet artifact and precision: official Q8 GGUF, raw checkpoint, or a specific community conversion.
2. Runtime, version, CPU/GPU/NPU, threads, peak RAM, and elapsed time.
3. Whisper model and quantisation; Tiny q5_1, Small, Turbo, and Large v3 are not one baseline.
4. The same French audio, reference transcripts, normaliser, WER/CER calculation, and raw outputs.
5. Any punctuation restoration, language setting, voice activity detection, chunking, or post-processing.

Without those controls, an apparent quality win may simply be a much larger model, a stronger decoder, a different corpus, or a punctuation policy.

## Decision for the current plan

Keep Sherpa-ONNX French Zipformer and whisper.cpp Tiny q5_1 as the only approved hands-on candidates. Do not download or run Parakeet for the upcoming representative WAV. If the colleague supplies a controlled comparison that materially changes the quality picture, reopen candidate selection explicitly; Parakeet can only displace a current candidate if it first clears a credible Luna resource path.

## Sources

- [NVIDIA model card: Parakeet TDT 0.6B v3](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3)
- [Official repository assets, including Q8 GGUF](https://huggingface.co/nvidia/parakeet-tdt-0.6b-v3/tree/main)
- [NVIDIA ASR NIM support matrix](https://docs.nvidia.com/nim/speech/26.05.0/reference/support-matrix/asr.html)
- [NVIDIA NeMo-Speech.cpp runtime](https://github.com/NVIDIA/NeMo-Speech.cpp)
- [NeMo-Speech.cpp model documentation](https://github.com/NVIDIA/NeMo-Speech.cpp/blob/main/docs/asr/models.md)
