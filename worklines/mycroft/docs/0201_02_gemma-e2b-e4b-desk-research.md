# Gemma E2B/E4B: desk research for Mycroft v0

> **Freshness:** 🟡 historical · **Written:** 2026-09-27 · **Checked:** 2026-10-31 · **Step:** mycroft 2.1 ✅

**Status:** evidence-only review. No model was downloaded, run, or added to the candidate benchmark.

## Question

Could the Gemma E2B/E4B models reported as outperforming Whisper replace Mycroft's offline French ASR v0 on Luna?

## Short answer

No, not within the current Mycroft v0 scope and resource gate. The likely reference, Gemma 3n E2B/E4B, accepts audio and can produce a transcript, but it is a general multimodal generative model rather than a small, dedicated ASR engine. Google's published minimum memory footprints are about 2 GB for E2B and 3 GB for E4B. Luna's provisional budget is 1 GiB shared LPDDR3 before the operating system, audio stack, and application have used any memory.

The name is ambiguous: current Gemma 4 also has E2B/E4B variants. That does not improve the fit. Google's Gemma 4 overview lists 2.9 GB of Q4 weight memory for E2B, before runtime overhead; its separate mobile estimate is still 1.1 GB for audio-capable E2B. Neither is a credible fit for a 1 GiB shared-memory target.

## What the published material establishes

| Topic | Gemma 3n E2B/E4B | Relevance to Mycroft v0 |
| --- | --- | --- |
| Input and output | Native text, image, video, and single-channel audio input; text output. | It can be prompted to transcribe, but its normal interface is generated text, not a narrowly constrained audio-to-text decoder. |
| Model purpose | General-purpose multimodal model. | A prompt and output policy become part of the transcription system; this is additional variability and cost compared with the v0 contract. |
| Audio window | The launch implementation describes 30-second audio clips, although its encoder could support later streaming work. | The current capture is longer than 30 seconds; chunking and stitching would become additional engineering, with unknown quality impact. |
| Memory claim | Google reports minimum footprints of about 2 GB (E2B) and 3 GB (E4B). | Hard resource-gate failure for Luna, independent of accuracy. |
| Runtime path | Google documents Python, PyTorch, Accelerate, and Transformers examples; it also notes ecosystem support such as llama.cpp. | No target-device ARM/RK3326 latency, RAM, or offline deployment evidence has been supplied. |
| French ASR quality | The model card describes broad multilingual training, but no directly comparable official French WER result against Whisper was located. | Multilingual capability is not proof of a French transcription win under the v0 protocol. |
| Licence | Open weights under the Gemma Terms, including use restrictions and notice obligations. | This is not an OSI-style fully open-source licence, so it also needs a licence review if reconsidered later. |

## Interpreting the colleague's result

It is entirely plausible that a prompted multimodal language model makes a more readable transcript of a difficult recording than a small Whisper model. That would be a semantic, context-sensitive result. It does not yet establish a better ASR candidate for Mycroft v0, whose baseline is context-free audio to plain text and whose decisive constraint is Luna's memory budget.

Before accepting a Whisper comparison, request the following evidence:

1. Exact model family and identifier: Gemma 3n or Gemma 4; E2B or E4B; instruction-tuned variant; quantisation; runtime and version.
2. Exact transcription prompt, decoding parameters, audio chunk length, overlap, and any language hint or post-processing.
3. Test corpus, language mix, references, audio sample rate, and whether samples exceeded the model's audio window.
4. Per-sample raw outputs plus WER or CER computed against the same references used for Whisper.
5. The Whisper model, quantisation, runtime, prompt/language setting, and decoding configuration.
6. Hardware, peak RAM, wall-clock latency, CPU/GPU/NPU use, model-storage size, and whether any service stayed resident.
7. Licence and distribution assumptions.

An evaluation that improves only the text's apparent fluency can conceal dropped, inserted, or invented words. WER/CER and raw transcripts are required alongside qualitative readability.

## Decision for the current plan

Keep the two approved hands-on candidates unchanged: Sherpa-ONNX French Zipformer and whisper.cpp Tiny q5_1. Gemma is not a third candidate and must not be downloaded or benchmarked under this plan. It could only displace a candidate after a material plan revision, an evidence-backed resource exception, and an explicit green light.

The study is still useful: it may identify a later, desktop-class multimodal direction for Mike or a separate post-v0 workline. It is not a viable Luna ASR v0 path on the evidence available today.

## Sources

- [Gemma 3n model card](https://ai.google.dev/gemma/docs/core/model_card_3n)
- [Gemma 3n developer guide](https://ai.google.dev/gemma/docs/get_started)
- [Gemma 3n technical announcement](https://developers.googleblog.com/en/introducing-gemma-3n-developer-guide/)
- [Gemma audio understanding guide](https://ai.google.dev/gemma/docs/audio)
- [Gemma 4 overview and memory table](https://ai.google.dev/gemma/docs/core)
- [Gemma Terms of Use](https://ai.google.dev/gemma/terms)
