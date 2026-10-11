---
**Status**: 🚧 In progress — Sherpa baseline retained; Steps 2–4 reopened for the context/composition revision
**Date**: 2026-09-25
**Priority**: High
**Maintained**: Yes
---

# Mycroft — offline French ASR v0 (workline `mycroft`)

## Overview

Mycroft is Luna’s interactive input-and-composition capability. Mycroft v0 is a foreground, text-only console: it accepts either a live microphone stream or a replayed audio file as a pseudo stream, displays incremental transcription, and gives the user an editable draft to supplement, accept, or discard.

The existing Sherpa result remains the single-model, context-free ASR reference. v0 proves the interaction contract around it: capture → visible hypotheses → editable text → explicit acceptance. It does not execute accepted text, integrate with Mike/Wyoh, inject context, or claim handheld microphone compatibility. Done means the pinned local model drives the documented console with microphone and replay inputs, explicit keyboard actions, and a reproducible test harness.

TANSTAAFL applies to model weights, RAM, shared GPU memory, battery, storage, dependencies, cold-start time, and permanently running processes. v0 is one on-demand foreground model, not a resident service or a multi-model system.

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
**Status**: 🧪 Reopened — audio-file baseline preserved; interactive microphone/replay contract added

- [x] 1.1 Confirm that v0 means speech-to-text, resolving the text-to-speech wording if necessary.
- [x] 1.2 Specify the input contract: supported audio formats, mono/stereo handling, sample-rate policy, language selection, and error behaviour.
- [x] 1.3 Define output expectations: plain text, timestamps yes/no, punctuation/casing policy, and how uncertain output is reported.
- [x] 1.4 Create a resource ledger: model asset, runtime/dependency footprint, peak RSS, CPU time, startup time, storage, and any GPU/shared-memory allocation. Mark desktop values as non-target evidence and state the target budget that must remain for Linux and future HOLMES-36 components.
- [x] 1.5 Define a small, consented French test corpus covering clean speech, ordinary room noise, technical terms, and short command-like phrases—without context biasing or an unnecessarily large dataset.
- [x] 1.6 Define comparison measures: transcription quality, cold-start time, real-time factor or latency, peak memory, disk footprint, CPU use, installation friction, licence, and whether the result meets the resource ledger.
- [x] 1.7 Historical acceptance: the ASR-only protocol supports a comparable context-free baseline.
- [x] 1.8 Define the Mycroft v0 text-console intent: a single --input PATH source contract for device/replay paths, visible streaming draft, editing, start/stop/accept/discard bindings, one-model policy, implementation path, and testing policy.
- [x] 1.9 Acceptance: the intent was reviewed through the explicit Step 5 green light; the revised input/interaction contract is authorised without expanding Mycroft scope.

### Step 2 — Evidence-based candidate shortlist
**Status**: 🧪 Reopened — baseline shortlist preserved; compact contextual candidates require fresh evidence

- [x] 2.1 Verify current supported platforms, French support, licence, model/runtime sizes, native ARM/Linux path, and maintenance status for Sherpa-ONNX / French Zipformer and `whisper.cpp` Tiny quantised.
- [x] 2.2 Reject candidates that need network inference, an unbounded build/runtime dependency chain, unsupported target hardware, or a resource cost that conflicts with the Step 1 ledger. Moonshine remains evidence-only until its French asset, licence, and target-compatible runtime are verified.
- [x] 2.3 Select at most a primary candidate and one challenger for hands-on tests, pinning their versions and assets.
- [x] 2.4 Acceptance: a shortlist document accounts for each candidate's inclusion, exclusion, or deferral, its reproducible install source, and its expected cost against the ledger.

### Step 3 — Build the pre-hardware evaluation harness
**Status**: 🧪 Reopened — baseline harness preserved; matched contextual protocol remains incomplete

- [x] 3.1 Create a minimal, documented harness that feeds the same audio files to every shortlisted candidate.
- [x] 3.2 Capture transcript, elapsed time, peak memory when measurable, model/runtime version, installed dependency footprint, execution errors, and the resource-ledger verdict in a machine-readable result format.
- [x] 3.3 Keep the harness small and disposable: it must not become a resident service or introduce a heavyweight target runtime. Make it runnable on the desktop without creating a VM; add an optional `luna-pi` target only if it is already available.
- [x] 3.4 Acceptance: one documented command produces comparable, resource-accounted results for at least one candidate and one fixture.

### Step 4 — Test and choose the v0 model
**Status**: 🧪 Reopened — Sherpa reference retained; expanded candidate decision remains incomplete

- [x] 4.1 Run all shortlisted candidates against the agreed corpus.
- [x] 4.2 Review qualitative errors, technical-term behaviour, and measured resource use against the protocol; a quality advantage does not outweigh a ledger failure.
- [x] 4.3 Choose the smallest candidate that meets the agreed quality and cost gates, or document why no current candidate is acceptable.
- [x] 4.4 Acceptance: a decision record names the v0 model, exact assets/runtime, measured costs, known limits, and rejected alternatives.

### Step 5 — Deliver Mycroft v0 text console
**Status**: 🚧 In progress — console and automated replay evidence complete; live microphone acceptance remains

- [x] 5.1 Write the intent before implementation: commands/parameters, state scenarios, terminal bindings, draft ownership, one-model policy, implementation seams, and test policy.
- [x] 5.2 Implement the foreground text console with mic and deterministic replay audio-source adapters, incremental hypotheses, and an editable draft.
- [x] 5.3 Implement the Space start/stop (originally F5/F6; changed 2026-10-09 because editor terminals capture function keys), Enter accept, Esc discard, and safe quit semantics; accepting emits text only and never executes it.
- [x] 5.4 Keep exactly one pinned ASR model/runtime in v0, loaded by the foreground process; document the future-compatible model-profile seam without adding a runtime picker.
- [ ] 5.5 Complete live-microphone/manual-terminal smoke and foreground resource evidence. State-machine, renderer, replay-contract, and recogniser-adapter pytest coverage is implemented and passing; no real-device claim is made.
- [ ] 5.6 Acceptance: microphone and replay drive the same visible composition flow; edits survive; accept emits exactly once; discard has no side effect; tests and resource evidence pass with one pinned local model.

### Step 6 — Hand off target-hardware validation
**Status**: ⏳ Pending

- [ ] 6.1 On hardware arrival and a separate green light, measure the delivered board/firmware, baseline memory, available audio interfaces, storage, CPU behaviour, thermals, and exposed Mali APIs before installing or changing the firmware.
- [ ] 6.2 Define the later HOLMES-36 validation matrix: microphone/jack availability, audio capture path, latency, memory, CPU, thermal behaviour, and optional GPU/Vulkan support. A GPU test is only valid if it reports total memory impact and beats or usefully complements the CPU baseline.
- [ ] 6.3 Record deferred context biasing as a future Mycroft phase with an explicit privacy, data-source, and bounded-vocabulary design.
- [ ] 6.4 Acceptance: hardware arrival can trigger a bounded validation task rather than reopening v0 design; no target configuration, flashing, or GPU work is implied by this plan.

### Step 7 — Dictation provider for Wyoh's Slate
**Status**: 🚧 In progress — 🟩 go 7.2–7.4 given 2026-10-09 22:40 by Professor on the user's behalf (decision D3, [`0503_01`](../professor/docs/0503_01_delegated-coordination-log-2026-10-09.md)). Limits: the `luna-pi` measurement in 7.3 waits until `luna-pi` is back on; no Luna install, no Slate code, no commit.

User direction: try voice input in Wyoh's Slate (dictate, correct, send). The Slate is Wyoh's; Mycroft provides the text. Proposal and open questions: [Wyoh note `0600_02`](../wyoh/docs/0600_02_note-from-mycroft-dictation-in-slate.md).

- [x] 7.1 Apply the user's display decisions in Mycroft's console: one text area (no separate hypothesis pane) and lower-case output.
- [x] 7.2 Interface agreed with Wyoh (`0600_02` §6) and recorded: a separate process started by Wyoh's gamepad daemon; `ready`/`partial`/`final`/`error` JSON lines; stop by closing stdin; exit 0/2/3; capture device as `--input`. See `docs/0704_01_dictation-provider.md`.
- [~] 7.3 Runtime selected by architecture: the official prebuilt `linux-aarch64-shared-cpu-lib` (checksum verified; needs glibc 2.17 and GLIBCXX 3.4.19, no compiler). **Open:** load and measure on `luna-pi` (off on 2026-10-09), then on Luna once Luna Step 8 locates the microphone.
- [x] 7.4 `scripts/mycroft_dictate.py` with a `--fake` mode for Wyoh; `test/mycroft/dictate.feature` and `test_dictate.py`. Desk host: model load 1.27 s, first partial 1.29 s after `ready`, stop→final under 10 ms, peak RSS 217.5 MiB (`results/mycroft/dictate/20261009T203427Z/`).
- [ ] 7.5 Acceptance: dictated text appears in the Slate and can be corrected and sent there; resource cost recorded against the ledger.

**Recorded for later (not authorised):**
- **Re-format action:** one press finishes sentences and adds punctuation and capitals. Candidates are rules, a French punctuation model (existence unverified), or Mike.
- **Input modes:** command line (correct before sending) versus Mike and Mannie (direct dictation, sent as it is).

---

## Progress tracking ✅

- ✅ Workline scope and Mycroft v0 handoff recorded.
- 🧪 Step 1 — Reopened for the microphone/replay interactive-console contract; intent prepared.
- 🧪 Step 2 — Reopened for compact contextual-ASR evidence; baseline shortlist preserved.
- 🧪 Step 3 — Reopened for the matched contextual evaluation protocol; baseline harness preserved.
- 🧪 Step 4 — Reopened; Sherpa remains the context-free reference pending expanded evidence.
- 🚧 Step 5 — Console test coverage comprises 20 asset-free checks plus 3 optional pinned-asset integrations, including a real-terminal scenario; live-microphone smoke and foreground resource evidence remain.
- ⏳ Step 6 — Hand off target-hardware validation.
- 🚧 Step 7 — Dictation provider: 7.1, 7.2, 7.4 done; 7.3 done on the desk host, `luna-pi` measurement waiting; 7.5 needs Wyoh's Step 12 and the user.

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
| 2026-09-25T10:50:00+02:00 | User green-lit Steps 1–4. Completed the protocol and ledger, limited shortlist, native desktop harness, and matched two-candidate benchmark. Selected Sherpa-ONNX French Zipformer provisionally; target fit remains unproven pending hardware validation. |
| 2026-09-25T12:13:21+02:00 | Added a transparent, raw-transcript supplement to the completed Step 4 evidence and a desk review of Gemma E2B/E4B. No model, benchmark, or target-hardware work was added. |
| 2026-09-25T12:18:38+02:00 | Prepared a consented, long representative French reading script with numbered coverage groups and canonical ground truth. Recording and any evaluation remain pending. |
| 2026-09-25T12:28:48+02:00 | Revised the prepared script before recording: reduced it from 39 to 13 phrases and concentrated it on CLI interaction, code editing, interface navigation, and a small set of ASR stress cases. |
| 2026-09-25T16:14:42+02:00 | Reviewed Parakeet TDT 0.6B v3 as evidence only. Its French ASR results are promising, but NVIDIA states a 2 GB minimum RAM requirement, excluding it from the 1 GiB shared-memory Luna v0 path; no download or benchmark was authorised. |
| 2026-09-25T22:08:52+02:00 | User supplied a consented 130-second representative recording. Ran only the two approved desktop candidates on an explicit temporary 16 kHz mono conversion: Sherpa WER 0.134 versus Whisper Tiny q5_1 WER 0.427. The private audio and raw logs remain uncommitted; target fit remains unproven. |
| 2026-09-25T23:30:00+02:00 | Reframed Mycroft v0 as a text-only microphone/replay composition console. Wrote the required intent before implementation; Step 1 is reopened and Step 5 is paused after the intent pending a new green light. |
| 2026-09-26 | Step 5 was green-lit. Implemented the one-profile foreground console and pytest evidence under `test/mycroft/`: 15 asset-free checks pass, while 2 pinned-C-API/public-WAV integrations pass only when their external assets are installed and otherwise skip. Live microphone/terminal and foreground resource validation remain open; no Luna claim is made. |
| 2026-10-09 | User reported the console filling the terminal with repeated frames. Reproduced in a pseudo-terminal and fixed within the green-lit Step 5: staircase/scrolling redraws, unresponsive lone Esc, `q` losing an editable draft, invisible accepted text, and a model reload on every F5. Added a real-terminal integration scenario (`test/mycroft/console_terminal.feature`). Live microphone acceptance (5.5) remains open. |
| 2026-10-09 | User found that VS Code's terminal captures F5 (debugger). Replaced F5/F6 with a Space start/stop toggle (ordinary text inside a stopped draft) and made the key decoder ignore unbound escape sequences. Intent `0501_01` amended. |
| 2026-10-09 | User direction: one text area and lower case (done in the console; peak RSS 218.7 MiB on x86_64), a later re-format action, per-destination input modes, and a Slate dictation trial. Proposed Step 7 and sent Wyoh note `0600_02`; no Slate code touched. |
| 2026-10-09T22:45 | Wyoh accepted the separate dictation process (`0600_02` §6, its Step 12). Professor gave 🟩 go 7.2–7.4 on the user's behalf (D3 in `worklines/professor/docs/0503_01_delegated-coordination-log-2026-10-09.md`); desk-host work only, `luna-pi` measurement deferred while it is off, no commit. |
| 2026-10-09T22:40–23:00 | Did 7.2–7.4 under D3: interface recorded, aarch64 runtime selected and inspected, `mycroft_dictate.py` with fake mode and tests (31 passed + 4 integration passed; default suite 292 passed). Blocked: the `luna-pi` part of 7.3 (`luna-pi` off). Stopped as instructed; no commit. |

---

## Workline artifacts

- `worklines/mycroft/docs/0000_01_mycroft_v0_handoff.md` — authorised v0 boundary, model candidates, and deferred scope.
- `worklines/professor/docs/0001_01_initial_discussion.md` — source discussion containing Mycroft’s voice-to-text role and candidate directions.
- `worklines/mycroft/docs/0101_01_requirements-and-test-protocol.md` — frozen v0 contract, ledger, corpus, and measures.
- `worklines/mycroft/docs/0102_02_candidate-shortlist.md` — pinning and two-candidate admission decision.
- `worklines/mycroft/docs/0103_03_evaluation-harness.md` — reproducible native-decoder harness and its limits.
- `worklines/mycroft/docs/0104_04_model-decision.md` — desktop benchmark result and provisional v0 model selection.
- `worklines/mycroft/docs/0104_05_candidate-transcript-comparison.md` — exact smoke-fixture references, raw candidate transcripts, WER method, and external-benchmark assessment.
- `worklines/mycroft/docs/0104_06_representative-reading-evaluation.md` — private long-form representative recording, matched two-candidate result, and privacy boundary.
- `worklines/mycroft/docs/0105_01_representative-reading-script.md` — numbered, annotated recording script and canonical ground truth for a future consented long-form evaluation WAV.
- `worklines/mycroft/docs/0201_02_gemma-e2b-e4b-desk-research.md` — evidence-only resource and licence review of the proposed Gemma direction.
- `worklines/mycroft/docs/0201_03_parakeet-tdt-0-6b-v3-desk-research.md` — evidence-only quality, runtime, licence, and Luna resource-gate review of Parakeet TDT 0.6B v3.

- `worklines/mycroft/docs/0501_01_text-console-intent.md` — required v0 console intent: sources, interactions, state behaviour, implementation seams, one-model policy, and test harness.
- `worklines/mycroft/docs/0502_02_text-console-implementation.md` — v0 implementation boundary, pytest evidence, and explicit remaining live-input/resource acceptance.
- `worklines/wyoh/docs/0600_02_note-from-mycroft-dictation-in-slate.md` — Step 7 proposal to Wyoh: dictation into the Slate, with Wyoh's reply.
- `worklines/mycroft/docs/0704_01_dictation-provider.md` — Steps 7.2–7.4: interface, aarch64 runtime, implementation and desk-host evidence.

## Active architecture and reopened evidence — 2026-09-25

Mycroft is Luna’s input-and-composition capability. The completed Sherpa work remains the context-free ASR baseline, not the full product choice. The active product path is `capture → ASR hypotheses → editable composition buffer → explicit acceptance → destination`. A backend must behave correctly with `context = []` and `alternatives = []`; context is optional, bounded, revision-labelled, and never grants execution authority.

- **Step 2 is reopened:** verify compact, FOSS candidates and their exact licensing, ARM path, asset/runtime cost, and dynamic-vocabulary behaviour. Do not adopt unverified Vosk or hotword claims.
- **Step 3 is reopened:** specify matched no-context/contextual fixtures and a context-size, latency, RSS, and privacy ledger. Use static fixtures until a separately approved Wyoh provider exists.
- **Step 4 is reopened:** retain Sherpa as the reference quality result, then determine whether a compact contextual candidate earns a separate role. Do not conflate generic WER with contextual benefit.
- Modes, physical controls, alternatives, and closed-set local ranking are planned interfaces and idea-box work only. No model download, context feed, command routing, or implementation is authorised by this amendment.

See [the Professor decision record](../professor/docs/0102_03_shared-chatgpt-options-decision.md) and [the architecture note](docs/0106_01_input-composition-architecture.md).

### Amendment log

| Timestamp (`date`) | Update |
|---|---|
| 2026-09-25T23:10:00+02:00 | Incorporated the canonical shared ChatGPT discussion; retained Sherpa as context-free reference and reopened candidate, harness, and selection evidence for the later compact contextual-ASR path. |

## Additional workline artifact

- `worklines/mycroft/docs/0106_01_input-composition-architecture.md` — staged composition architecture and context boundary.
