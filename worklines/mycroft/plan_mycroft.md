---
**Status**: 📋 Draft
**Date**: 2026-09-25
**Priority**: High
**Maintained**: Yes
---

# Mycroft — offline French ASR v0 (workline `mycroft`)

## Overview

Mycroft is HOLMES-36’s voice-input layer. It converts audio into text and will eventually provide Mike with a reliable voice channel. While the hardware is still in transit, this workline focuses on the part that does not need the handheld: requirements, candidate selection, reproducible desktop or `luna-pi` tests, and a minimal local transcription tool.

**v0 is speech-to-text (ASR), not text-to-speech.** It deliberately transcribes audio without contextual biasing, intent detection, command execution, or integration with Mike, Wyoh, Mannie, or Codex. Done means that one selected local model is wrapped in a documented command-line tool that transcribes a small French test corpus and records its measured behaviour.

TANSTAAFL is a design constraint: model weights, RAM, shared GPU memory, battery, storage, dependencies, cold-start time, and permanently running processes all have a cost. Mycroft v0 therefore proves a small, on-demand CPU path first; it does not spend the future HOLMES-36 budget on speculation.

## Workline directory layout

- Plan (this file): `worklines/mycroft/plan_mycroft.md`
- Produced docs: `worklines/mycroft/docs/`
- Scripts: `worklines/mycroft/scripts/` if a reusable benchmark or v0 tool is approved

## Goals ✅

- Define measurable ASR v0 requirements before choosing a model.
- Establish a resource ledger and hard selection gates before choosing a model.
- Select a practical French ASR candidate using evidence rather than memory or marketing claims.
- Test a small candidate set locally and record reproducible results.
- Deliver a minimal, on-demand offline audio-to-text CLI with one chosen candidate.

## Non-goals ❌

- Text-to-speech, spoken replies, or a voice assistant persona.
- Context biasing, CLI/project vocabulary injection, speaker adaptation, or fine-tuning.
- Intent classification, tool calling, command execution, or routing to Mike.
- Wyoh UI/status/action work and Mannie/Codex development workflow work.
- Luna-specific audio, GPU, battery, and thermal optimisation before the device arrives.
- A VM or emulator intended to imitate the handheld.
- Buying accessories, storage, cloud inference, a subscription, or target-device build tooling solely for Mycroft v0.
- A resident voice daemon, simultaneous ASR models, or retaining recordings by default.

## Key decisions / assumptions

- Mycroft is the voice **input** layer: `audio → text → (future Mike)`.
- v0 begins with recorded audio files so it can be built without a confirmed target microphone or audio jack capability.
- v0 must run locally after installation; remote transcription APIs are not a v0 dependency.
- French is the primary language; English and mixed technical terms are useful secondary evaluation cases.
- The reported HOLMES-36 target is a RK3326 with four Cortex-A35 cores, Mali-G31 MP2, and **1 GiB shared LPDDR3**. These are provisional until the delivered device, firmware, and available memory are measured. Storage capacity is not treated as RAM capacity.
- CPU-only, native inference is the baseline. GPU/Vulkan is an optional later experiment only when the delivered firmware exposes a supported driver and it earns its memory and latency cost against the CPU baseline.
- The primary research path is Sherpa-ONNX with a French Zipformer model. `whisper.cpp` Tiny quantised is the single quality/challenger baseline, admitted only if its measured resource cost fits the agreed ledger. Moonshine remains desk research until a reproducible French asset, licence, and target-compatible runtime are evidenced.
- v0 has one selected runtime and one selected model asset. It loads on demand for file transcription and exits afterwards; later always-listening behaviour is a separate, explicitly budgeted phase.
- Dynamic context biasing from files, WM state, Git, or CLI vocabulary is valuable for the eventual voice-to-command system, but remains outside v0 so that its baseline quality and cost are measurable.
- `luna-pi` may be used for supplementary measurements, but no result on it substitutes for later Luna validation.

## Risks / constraints

- The intended device has only 1 GiB of memory shared by the OS, future WM/Mike work, ASR, and potentially the GPU, and its hardware/firmware may vary. **Mitigation:** maintain a resource ledger; do not infer target fit from desktop results, parameter count, or disk size.
- GPU offload can consume the same scarce RAM and may be slower or unavailable on the delivered Mali stack. **Mitigation:** it cannot be required by v0, and any later GPU trial compares like-for-like CPU and GPU measurements before it is retained.
- Model repositories, licences, French checkpoints, and runtimes can change. **Mitigation:** record exact versions, asset sources, licences, and checksums where practical.
- A tiny test set can overfit to a single voice or quiet room. **Mitigation:** define a varied but small, consented test corpus and preserve the protocol.
- “No context” can be confused with poor output quality. **Mitigation:** treat context-free transcription as the baseline; biasing belongs to a distinct later phase.

## 🚦 Green light protocol

- Default: planning and documentation only until you explicitly say **“🟩 go Step N”**.
- Each green-lit step produces the stated artifact before the next step is considered.
- Hardware-specific scope remains deferred even if it appears convenient to speculate about it.
- A request to add context, commands, Mike, Wyoh, or speech output is a scope change and requires a plan update.

## Plan steps (no execution until green light)

### Step 1 — Freeze Mycroft v0 requirements and test protocol
**Status**: ⏳ Pending

- [ ] 1.1 Confirm that v0 means speech-to-text, resolving the text-to-speech wording if necessary.
- [ ] 1.2 Specify the input contract: supported audio formats, mono/stereo handling, sample-rate policy, language selection, and error behaviour.
- [ ] 1.3 Define output expectations: plain text, timestamps yes/no, punctuation/casing policy, and how uncertain output is reported.
- [ ] 1.4 Create a resource ledger: model asset, runtime/dependency footprint, peak RSS, CPU time, startup time, storage, and any GPU/shared-memory allocation. Mark desktop values as non-target evidence and state the target budget that must remain for Linux and future HOLMES-36 components.
- [ ] 1.5 Define a small, consented French test corpus covering clean speech, ordinary room noise, technical terms, and short command-like phrases—without context biasing or an unnecessarily large dataset.
- [ ] 1.6 Define comparison measures: transcription quality, cold-start time, real-time factor or latency, peak memory, disk footprint, CPU use, installation friction, licence, and whether the result meets the resource ledger.
- [ ] 1.7 Acceptance: an approved requirements-and-test-protocol document allows two candidates to be compared consistently and rejects a candidate that cannot account for its cost.

### Step 2 — Evidence-based candidate shortlist
**Status**: ⏳ Pending

- [ ] 2.1 Verify current supported platforms, French support, licence, model/runtime sizes, native ARM/Linux path, and maintenance status for Sherpa-ONNX / French Zipformer and `whisper.cpp` Tiny quantised.
- [ ] 2.2 Reject candidates that need network inference, an unbounded build/runtime dependency chain, unsupported target hardware, or a resource cost that conflicts with the Step 1 ledger. Moonshine remains evidence-only until its French asset, licence, and target-compatible runtime are verified.
- [ ] 2.3 Select at most a primary candidate and one challenger for hands-on tests, pinning their versions and assets.
- [ ] 2.4 Acceptance: a shortlist document accounts for each candidate's inclusion, exclusion, or deferral, its reproducible install source, and its expected cost against the ledger.

### Step 3 — Build the pre-hardware evaluation harness
**Status**: ⏳ Pending

- [ ] 3.1 Create a minimal, documented harness that feeds the same audio files to every shortlisted candidate.
- [ ] 3.2 Capture transcript, elapsed time, peak memory when measurable, model/runtime version, installed dependency footprint, execution errors, and the resource-ledger verdict in a machine-readable result format.
- [ ] 3.3 Keep the harness small and disposable: it must not become a resident service or introduce a heavyweight target runtime. Make it runnable on the desktop without creating a VM; add an optional `luna-pi` target only if it is already available.
- [ ] 3.4 Acceptance: one documented command produces comparable, resource-accounted results for at least one candidate and one fixture.

### Step 4 — Test and choose the v0 model
**Status**: ⏳ Pending

- [ ] 4.1 Run all shortlisted candidates against the agreed corpus.
- [ ] 4.2 Review qualitative errors, technical-term behaviour, and measured resource use against the protocol; a quality advantage does not outweigh a ledger failure.
- [ ] 4.3 Choose the smallest candidate that meets the agreed quality and cost gates, or document why no current candidate is acceptable.
- [ ] 4.4 Acceptance: a decision record names the v0 model, exact assets/runtime, measured costs, known limits, and rejected alternatives.

### Step 5 — Deliver Mycroft v0
**Status**: ⏳ Pending

- [ ] 5.1 Implement a narrow local CLI: audio file in, UTF-8 transcript out.
- [ ] 5.2 Ensure the target path invokes one model on demand and does not require a full development toolchain or a permanently running Python service on HOLMES-36.
- [ ] 5.3 Provide clear setup, model-asset, usage, resource-cost, and failure documentation.
- [ ] 5.4 Add automated checks for the CLI contract and regression fixtures where licences/consent permit retaining audio.
- [ ] 5.5 Acceptance: a clean developer environment can install the documented dependencies, transcribe a fixture offline, reproduce the recorded result, and account for the selected runtime's resource cost.

### Step 6 — Hand off target-hardware validation
**Status**: ⏳ Pending

- [ ] 6.1 On hardware arrival and a separate green light, measure the delivered board/firmware, baseline memory, available audio interfaces, storage, CPU behaviour, thermals, and exposed Mali APIs before installing or changing the firmware.
- [ ] 6.2 Define the later HOLMES-36 validation matrix: microphone/jack availability, audio capture path, latency, memory, CPU, thermal behaviour, and optional GPU/Vulkan support. A GPU test is only valid if it reports total memory impact and beats or usefully complements the CPU baseline.
- [ ] 6.3 Record deferred context biasing as a future Mycroft phase with an explicit privacy, data-source, and bounded-vocabulary design.
- [ ] 6.4 Acceptance: hardware arrival can trigger a bounded validation task rather than reopening v0 design; no target configuration, flashing, or GPU work is implied by this plan.

---

## Progress tracking ✅

- ✅ Workline scope and Mycroft v0 handoff recorded.
- ⏳ Step 1 — Freeze requirements and test protocol.
- ⏳ Step 2 — Evidence-based candidate shortlist.
- ⏳ Step 3 — Pre-hardware evaluation harness.
- ⏳ Step 4 — Test and choose the v0 model.
- ⏳ Step 5 — Deliver Mycroft v0.
- ⏳ Step 6 — Hand off target-hardware validation.

---

## Time tracking (use `date`) ⏱️

```bash
date
```

### Time log

| Timestamp (`date`) | Update |
|---|---|
| 2026-09-25 | Workline created by explicit user direction; scope restricted to pre-hardware ASR v0 planning and later green-lit work. |
| 2026-09-25T00:37:30+02:00 | Revised plan after review of the full project discussion and Mycroft handoff. Added TANSTAAFL resource ledger, CPU-first/no-resident-runtime rule, two-candidate cap, and explicit shared-1-GiB/GPU gates; no execution was authorised or performed. |

---

## Workline artifacts

- `worklines/mycroft/docs/0000_01_mycroft_v0_handoff.md` — authorised v0 boundary, model candidates, and deferred scope.
- `worklines/professor/docs/0001_01_initial_discussion.md` — source discussion containing Mycroft’s voice-to-text role and candidate directions.
