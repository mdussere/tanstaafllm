# Mycroft v0 — authorised pre-hardware scope

> **Freshness:** 🟡 historical · **Written:** 2026-09-25 · **Checked:** 2026-10-31

## Question answered

What voice capability can be researched, compared, and implemented before Luna arrives, without emulating the handheld or committing to its audio hardware?

## Direction authorised

Mycroft is the **voice input / automatic speech recognition (ASR)** layer:

```text
audio file or microphone recording → Mycroft → plain text
```

This follows the initial discussion, where Mycroft was defined as “Voice → Text”, ahead of Mike. The phrase “text-to-speech” in the workline request is treated as a terminology slip because it contradicts Mycroft’s input role. If text-to-speech was intended, this plan must be amended before implementation.

## Mycroft v0 boundary

- Input: recorded audio first; live microphone capture is optional only after the file-based path works.
- Output: plain UTF-8 French transcription on standard output or in a simple result file.
- Runtime: local and offline after model assets are installed.
- Context: none. No hotwords, repository/file-list bias, CLI vocabulary injection, speaker adaptation, intent extraction, or command execution.
- Integration: none. Mycroft v0 does not call Mike, Wyoh, Mannie, Codex, or a remote API.
- Target: development desktop and, if useful, `luna-pi`; Luna-specific microphone, jack, GPU, and latency work wait for the hardware.

## Candidate families from the initial discussion

1. **Sherpa-ONNX + French Zipformer** — proposed primary candidate for small-footprint streaming French ASR.
2. **whisper.cpp Tiny, quantised** — proposed multilingual quality baseline.
3. **Moonshine Tiny** — exploratory candidate; French model availability, runtime compatibility, and licence must be verified before it is tested.

These are candidates, not selected models or verified performance claims.

## v0 success condition

Given a small, versioned French audio test set, a user can run one documented local command and obtain a transcript. The selected candidate and all measured results are recorded, and the tool can fail clearly when an audio format or model asset is unavailable.

## Deferred v1+ capabilities

- context biasing from current files, project terms, or CLI vocabulary;
- voice activity detection and continuous listening;
- speech-to-intent or direct command routing;
- integration with Mike, Wyoh, or Mannie;
- hardware microphone / 3.5 mm jack / USB audio validation on Luna;
- GPU/Vulkan optimisation and target-device latency tuning;
- text-to-speech and audible responses.
