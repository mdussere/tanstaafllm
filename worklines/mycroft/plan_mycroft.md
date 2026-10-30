---
**Status**: 🚧 In progress — active: Step 5 (live-microphone check), Step 7 (dictation for the Slate), Step 8 (dictation usable on Luna). Steps 2–4 are reopened for contextual ASR but not active.
**Date**: 2026-09-25 (reordered 2026-10-11)
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
**Status**: ⏸️ Superseded (2026-10-11) — Luna has arrived. Board, firmware, memory and audio characterisation is done by the Luna workline (`worklines/luna/plan_luna.md`; the microphone is Luna Step 8). Mycroft's own on-device validation is Step 8 below. 6.3 (context biasing as a future phase) remains covered by the reopened Steps 2–4. Kept for history.

- [ ] 6.1 On hardware arrival and a separate green light, measure the delivered board/firmware, baseline memory, available audio interfaces, storage, CPU behaviour, thermals, and exposed Mali APIs before installing or changing the firmware.
- [ ] 6.2 Define the later HOLMES-36 validation matrix: microphone/jack availability, audio capture path, latency, memory, CPU, thermal behaviour, and optional GPU/Vulkan support. A GPU test is only valid if it reports total memory impact and beats or usefully complements the CPU baseline.
- [ ] 6.3 Record deferred context biasing as a future Mycroft phase with an explicit privacy, data-source, and bounded-vocabulary design.
- [ ] 6.4 Acceptance: hardware arrival can trigger a bounded validation task rather than reopening v0 design; no target configuration, flashing, or GPU work is implied by this plan.

### Step 7 — Dictation provider for Wyoh's Slate
**Status**: ✅ Done — 7.1–7.5 done (7.5 closed 2026-10-25 on Wyoh 12.4's evidence).
**Green light:** 🟩 go 7.2–7.4 given 2026-10-09 22:40 by Professor on the user's behalf (decision D3, [`0503_01`](../professor/docs/0503_01_delegated-coordination-log-2026-10-09.md)).

User direction: voice input in Wyoh's Slate (dictate, correct, send). The Slate is Wyoh's; Mycroft provides the text. Proposal and Wyoh's reply: [Wyoh note `0600_02`](../wyoh/docs/0600_02_note-from-mycroft-dictation-in-slate.md).

- [x] 7.1 Apply the user's display decisions in Mycroft's console: one text area (no separate hypothesis pane) and lower-case output.
- [x] 7.2 Interface agreed with Wyoh (`0600_02` §6) and recorded: a separate process started by Wyoh's gamepad daemon; `ready`/`partial`/`final`/`error` JSON lines; stop by closing stdin; exit 0/2/3; capture device as `--input`. See `docs/0704_01_dictation-provider.md`.
- [x] 7.3 Runtime chosen by architecture: the official prebuilt `linux-aarch64-shared-cpu-lib` (checksum verified; needs glibc 2.17 and GLIBCXX 3.4.19, no compiler). Confirmed loading and running on Luna by 8.1; the planned `luna-pi` measurement is dropped as superseded.
- [x] 7.4 `scripts/mycroft_dictate.py` with a `--fake` mode for Wyoh; `test/mycroft/dictate.feature` and `test_dictate.py`. Desk host: model load 1.27 s, first partial 1.29 s after `ready`, stop→final under 10 ms, peak RSS 217.5 MiB (`results/mycroft/dictate/20261009T203427Z/`).
- [x] 7.5 Acceptance: dictated text appears in the Slate and can be corrected and sent there; resource cost recorded against the ledger.
  **Closed 2026-10-25** (Professor, at the user's request), on Wyoh's evidence (`plan_wyoh.md` 12.4, 2026-10-15). Resident Kroko is deployed in the Slate and preloaded at session start. L2 dictates, and in the user's voice tests the dictated text appeared in the Slate. Editing and sending the Slate's text were verified live in Wyoh 6.9. Keys pressed *during* dictation (A, FN+A) were fixed and deployed after those tests; the user has not confirmed them since. Resource cost: [`0908_01`](docs/0908_01_resident-kroko-on-luna.md) records it, measured by the replay probe and not inside the Slate session (load 24.4 s once, 151.5 MiB idle, 172 MiB peak). That cost against Wyoh's session is left to 8.8.

### Step 8 — Make dictation usable on Luna (CPU)
**Status**: 🚧 In progress — 8.1–8.4 done. The blocker is decoding speed: RTF 1.32 at best, with 2 threads, so slower than real time. 8.5 proposed; the user reviews `0802_01` before it. 8.6 prepared, waiting for a Luna slot.
**Green light:** 8.1 by the user, 2026-10-11. 8.2, 8.3, 8.4 and 8.6 are the user's decisions after reading 8.1's result, relayed by Professor on 2026-10-11.
**Goal:** on Luna, dictation keeps up with speech and starts quickly enough to be started from a button. CPU only; the GPU is parked (see "Recorded for later").

**Luna rules** (`worklines/luna-access.md`, Professor arbitrates): use Luna only after Professor's "Luna is yours"; install only under `/storage/.local` (no boot, card or ArchR change, no package); measure on recorded WAV files (Luna's microphone is unproven, Luna Step 8); nothing heavy beside a Wyoh process; reboot Luna before and after each test run; to release: reboot, record the state here, send Professor "Luna released".

**Live test:** `test/mycroft/test_luna_footprint.py` (contract `luna_footprint.feature`), run with `MYCROFT_LUNA_LIVE=1 MYCROFT_LUNA_REBOOT=1 MYCROFT_ASSET_ROOT=…`. Evidence goes to `results/mycroft/luna-footprint/<timestamp>/`.

- [x] 8.1 **First footprint on Luna** (formerly 7.3b). Installed under `/storage/.local` (167.7 MB, checked by SHA-256). Three replays of a 7.1 s public French clip, one thread: model load 17.7–20.2 s, peak RSS ~252 MiB (about 260 MiB of `MemAvailable`), decoding 2.1× slower than real time (8.2 s behind at the end), one core saturated, text identical to the desk host. Result: [`0703_01`](docs/0703_01_luna-footprint-result.md).
- [x] 8.2 **Threads 2 and 4** (formerly 7.3c). **Result ([`0802_01`](docs/0802_01_threads-load-compiled-result.md)):** 2 threads is best: decode RTF 1.32 against 2.0 at 1 thread, and 3.6 s lag at the end of the 7.1 s clip in real-time replay. 4 threads is worse than 1 (RTF 2.1–2.5, 2.5× the CPU). Even at 2 threads, the model is slower than real time. The v0 one-thread profile is lifted; Mycroft has the cores to itself while it runs. Prepared: a `--threads` setting in the adapter, `mycroft_dictate.py` and the console (default stays 1 until this measurement sets it). On Luna: unpaced decode at 1, 2 and 4 threads, and real-time replay at 2 and 4. Desk host: 2 threads faster than 1, 4 slower than 2 (to check on Luna's four real cores).
- [x] 8.3 **Load time: break it down, then prepare the model once** — **Result ([`0802_01`](docs/0802_01_threads-load-compiled-result.md)):** creating the ONNX Runtime session takes 16.7–16.9 s warm and 17.8 s cold, independent of threads. Reading the files takes 2.3 s cold and 0.22 s warm, the libraries 0.5 s cold. So the load is CPU work, not I/O. The pre-optimised "extended" model brings session creation down to 13.2 s, with the same text and speed (−21 %). The rest is probably int8 weight pre-packing (unverified). Background (formerly 7.3d a; Professor's note [`0703_02`](docs/0703_02_note-from-professor-onnx-load-time.md)). Prepared: `test/mycroft/sherpa_load_profile.py` times the file read (once with a dropped page cache), the library load, session creation and decoding; `scripts/preoptimise_model.py` builds pre-optimised variants. Desk host: session creation is ~1.1 s of ~1.2 s. The ONNX "extended" variant gives the same text and creates its session in ~0.94 s. The ORT-format variant makes Sherpa abort (exit 134), so it is not usable through Sherpa's C API. Open: the variant was made on x86; `0703_02` advises making it on aarch64 (`luna-pi`), and whether ONNX Runtime can save pre-packed int8 weights is unverified.
- [x] 8.4 **Python against compiled code** (formerly 7.3e). **Result ([`0802_01`](docs/0802_01_threads-load-compiled-result.md)):** the C++ binary has the same load time (17.0 s), is no faster at decoding (RTF 1.5 at 2 threads against Python's 1.32), and uses ~15 MiB less (236 against 252 MiB). Python costs ~15 MiB and nothing measurable in speed, so staying in Python is recommended (decision in 8.7). Sherpa's prebuilt C++ streaming binary, same model, WAV and threads, against `mycroft_dictate.py`: peak RSS, CPU time, load time, real-time factor. Prepared: the binary (same libraries as those installed) and a `--raw` mode in the probe. Desk host: the binary creates its recogniser in 1.16 s (Python 1.13 s) and peaks at 203–208 MiB (Python 216–220 MiB). So the load is ONNX Runtime's, and Python costs ~15 MiB. The result decides whether Mycroft moves to compiled code.
- [ ] ⏸️ 8.5 **int8 against fp32** — parked by the user on 2026-10-11: no more tuning of the current model for now. (proposed by Professor's note `0703_02` §5; not yet green-lit). The Cortex-A35 lacks the int8 dot-product instructions, so int8 may gain less there. One fp32 measurement, if the fp32 model fits in memory.
- [ ] ⏸️ 8.6 **Resident provider and memory pressure; swap measured only** — parked by the user on 2026-10-11 (no more work on the current model); the probe stays ready for a lighter model. (formerly 7.3d b). Prepared: `test/mycroft/resident_probe.py`: load once, idle RSS split into anonymous and file-backed memory, decode before, during and after another process holds memory down to 150 MiB available. Plus a read-only check of Luna's swap and zram support. Enabling swap or zram is a system change outside `/storage` and is **not** authorised: measure and propose only.
- [ ] 8.7 **Choose the Luna profile** from 8.2–8.6: thread count, prepared model or not, resident or on-demand, Python or compiled. Record the decision, and set the defaults in the code.
  **Decision recorded 2026-10-25** (Professor, at the user's request), as deployed by Wyoh 12.4:
  - model: Kroko (`kroko-fr-2025`), prepared once at ONNX Runtime's "extended" level;
  - process: resident (`--resident`), preloaded at session start;
  - threads: 2 (8.2; 0908_01);
  - runtime: Python, since 8.4 showed compiled code saves only ~15 MiB and nothing in speed.

  This profile supersedes the v0 ledger's "no daemon" and "no target Python service" gates, by the user's decisions in 9.3. **Open:** the code defaults are still the old model at 1 thread (`DEFAULT_MODEL`, `DEFAULT_THREADS` in `mycroft_console.py`). Luna gets the profile only through the deployed command's flags. Changing the defaults is a code change and waits for a 🟩 go.
- [x] 8.8 **Acceptance:** on Luna, dictation keeps up with speech (small lag at the end of an utterance), its start time is agreed with the user, and its memory fits the ledger beside Wyoh's session.
  **Status 2026-10-25:**
  - **Keeps up with speech: met.** RTF 0.76–0.79 at 2 threads (9.3), and `final` comes 1.2 s after the audio ends (0908_01).
  - **Start time: open.** The user asked for no wait at the first opening, so Wyoh now preloads Kroko at session start (12.4). The user's confirmation that this start is acceptable is not recorded.
  - **Memory beside Wyoh's session: open.** No measurement of `MemAvailable` with Wyoh's session and resident Kroko together. 0908_01 only had 772.7 MiB available before a probe run. This needs a Luna slot, and the planned Arch Linux ARM root (Mannie Step 7) should come first.
  **Accepted by the user on 2026-10-28** ("Ok, we'll say it's good. It will hold."). Evidence: [`0808_01`](docs/0808_01_slate-session-memory-on-luna.md). On the new root, Wyoh's session with resident Kroko leaves 515–525 MiB available, and Kroko is at 163 MiB. Kroko is preloaded 19 s after boot. The figure during a dictation was not captured, because of a defect in the probe: it saw no "listening" state.

**Next Luna slot:** 8.6 (`test_luna_8_6_resident_and_swap`, about 5 minutes), and 8.5 if green-lit. Luna is rebooted before and after each run.

### Step 9 — A lighter model and known words
**Status**: 🚧 In progress — user decision 2026-10-11: no more tuning of the current model; look for a substantially lighter one (9.3 Kroko, 9.6 Parakeet Redux). 9.1 and 9.2 done (desk host, [`0901_01`](docs/0901_01_known-words-and-lighter-models.md)); 9.3–9.5 proposed, awaiting the user.
**Why:** keeping the current model resident costs ~250 MiB, too much for Luna. The user asks whether a smaller model can do (fine-tuned on their voice, or restricted to one language), and asks to check that the model can be given a list of known words (their first name "Michael", Wyoh, Luna, Mycroft, Wolfenstein…) and recognise them without ambiguity.

- [x] 9.1 **Known words (hotwords) on the current model** — user request: verify. **Result:** supported, with modified beam search plus the tokenizer vocabulary (`bpe.vocab`, from the original Apache-2.0 repository), and a list can be given per utterance. On synthetic speech (Piper) the list found 6/9 known words against 5/9 without it. Michael, Luna and Wolfenstein were already right; Mycroft was fixed once. Wyoh fails, because the list matches spelling, not sound: it needs its pronounced form plus a mapping back. Adapter options added (default unchanged). Test: `test_hotwords.py`. Read Sherpa v1.13.8's code for the conditions, then test on the desk host with and without a word list, on synthetic French speech that contains the words. No private recording.
- [x] 9.2 **Desk review: fine-tuning, one language, smaller models** — **Result:** the current model is already French only, so there is nothing to gain there. Kroko French is ~4× smaller (70 MB fp32 encoder against 293 MB) and probably punctuated; licence to confirm (empty LICENSE file). Fine-tuning the current model is possible (checkpoints published) but doesn't make it smaller. Recommendation: 9.3 first. Background — what each would gain on Luna, with sources. Result doc.
- [ ] 9.3 **Kroko French streaming model** — **Adopted and deployed** (Luna 0908_01, Slate via Wyoh 12.4). Left open only because **the licence is not confirmed**: Banafo's READMEs state CC-BY-SA, but no licence text ships with the weights. That is enough for personal use; redistribution, for example in a Luna image, needs the exact version. — 🟩 the user, 2026-10-11 ("go and look at Kroko or another, for a substantial gain"): about 4× fewer parameters than the current model, with punctuation and lower case in its tokens. Confirm the licence, then compare quality and speed on the desk host and on Luna. Needs a 🟩 go.
  **Desk result ([`0903_01`](docs/0903_01_lighter-candidates-desk-result.md)):** on the user's 130 s reading, Kroko has WER 0.091 against 0.134, RTF 0.035 against 0.065 (about half the CPU), peak RSS 160 against 216 MiB, and punctuation and capitals. On Common Voice clips it is less accurate (the current model was trained on them). Its load is longer: 2.9 s against 1.1 s. **`luna-pi` result ([`0903_02`](docs/0903_02_kroko-on-luna-pi.md)):** at 2 threads, Kroko has RTF 0.20 against 0.37, and 159 against 222 MiB, but loads in 11.0 s against 4.1 s. The cost is in opening the published file, not in graph optimisation. Prepared once on aarch64 ("extended"), it loads in 6.1 s (−44 %) with the same text. **Projection to Luna** (current model's measured ratio): RTF ~0.8 at 2 threads, so it would keep up with speech, but the load would be ~25 s prepared, so it still needs a resident process (~160 MiB). **Next, to decide:** measure it on Luna; licence still to confirm.
  **User decision (2026-10-11):** no load wait is acceptable between opening the Slate and dictating (4, 10 or 15 s are all too long), so the model must be **resident**. If Kroko is real-time on Luna, saves ~40 % memory, and has **the same quality**, it is adopted. Next: the user judges quality live on termidor with the usual console, so the console and provider gain a `--model` choice (the current model stays the default until the decision).
- [ ] 9.4 **Known words on the user's own voice** (proposed): a few consented sentences recorded by the user, kept private, to measure the real effect of the word list. Needs the recordings and a 🟩 go.
- [x] 9.7 **Resident provider for the Slate** (the user's decision relayed by Wyoh, 2026-10-13, note [`0903_03`](docs/0903_03_note-from-wyoh-kroko-resident-in-slate.md); the user: "continue", "we switch to Kroko"). `mycroft_dictate.py --resident` loads the model once and stays idle (microphone closed). stdin `{"op": "start"}` opens capture and sends `listening`, then `partial`; `{"op": "stop"}` sends `final`, resets, and goes back to idle. Closing stdin exits. `--fake` speaks the same protocol. pytest/Gherkin evidence.
  **Done (desk host):** `--resident` in `mycroft_dictate.py` (`start`/`listening`/`stop`, `--fake` too). A capture failure during an utterance sends `error` and keeps the model. 3 deterministic tests and Gherkin scenarios in `dictate.feature`. Found and fixed on the way: the adapter fed no silence after the last audio, so Kroko dropped its last word. `finish()` now pads 1.0 s (0.66 s was measured too short), at a cost of ~0.8 s more before `final` on Luna.
- [x] 9.8 **Kroko on Luna for the Slate**: use Kroko prepared once at ONNX Runtime's portable "extended" level (`0903_02`: −44 % load); install it and the current scripts under `/storage/.local`, replacing the partial `encoder.onnx`; measure the resident provider on Luna (load, idle RSS, start→listening, RTF at 2 threads). Luna through Professor; reboot before and after. Then answer Wyoh's note.
  **Prepared on the desk host:** `sherpa-onnx-streaming-zipformer-fr-kroko-2025-08-06-ort-extended` (ONNX Runtime 1.28.0, portable "extended" level, with a README naming its CC-BY-SA source). Same transcripts as the published files on 3 clips; load 1.7 s against 3.1 s on the desk host. The `kroko-fr-2025` profile now points to it. Desk-host resident run: ready 2.3 s, idle 147 MiB, 168 MiB listening, 0 s start→listening. Luna test `test_luna_9_8_resident_kroko`.
  **Done on Luna ([`0908_01`](docs/0908_01_resident-kroko-on-luna.md)):** prepared Kroko and the current scripts installed; at 2 threads, ready in 24.4 s (published: 47.7 s), idle 151.5 MiB, peak 172 MiB, start→listening 0.002 s on 3 utterances with one load, `final` 1.2 s after the audio ends, last word kept. Wyoh answered in `0903_03`.
- [ ] ⏸️ 9.5 **Fine-tuning on the user's voice** — parked by the user on 2026-10-11 (no tuning for now); a v0 non-goal in any case.
- [ ] 9.6 **Other light candidates suggested by the user and Charlie (2026-10-11)**, same evaluation as 9.3:
  - **Parakeet Redux** (Moondream; Parakeet TDT 0.6B v3 with ternary weights, 178 MB, CC-BY-4.0, French listed): **rejected for Luna**. Its Photon engine's kernels publish no aarch64 Linux build, so `uv pip compile` fails for aarch64; on x86 it pulls PyTorch and CUDA. See [`0903_01`](docs/0903_01_lighter-candidates-desk-result.md).
  - **Phonon-2** (Fermion Research; compressed Parakeet v3, 164 MB download, CC-BY-4.0, English only): **rejected for Luna**, even though the user would accept English. Its Linux engine is PyTorch + Transformers, and ~600 M parameters expanded at load exceed 1 GiB (~30× Kroko's compute). See [`0903_01`](docs/0903_01_lighter-candidates-desk-result.md).

### Recorded for later (not authorised)

- **Re-format action:** one press finishes sentences and adds punctuation and capitals. Candidates are rules, a French punctuation model (existence unverified), or Mike.
- **Input modes:** command line (correct before sending) versus Mike and Mannie (direct dictation, sent as it is).
- **GPU (OpenCL on the Mali-G31), parked by the user on 2026-10-11:** only after Step 8 gives usable CPU dictation. Then look at OpenCL, because "it could be fun to drive OpenCL on the micro GPU", even for a small gain. Facts and candidate engines: [Professor's note `0703_03`](docs/0703_03_note-from-professor-opencl-parked.md).

---

## Progress tracking ✅

- ✅ Workline scope and Mycroft v0 handoff recorded.
- 🧪 Step 1 — Reopened for the microphone/replay interactive-console contract; intent prepared.
- 🧪 Step 2 — Reopened for compact contextual-ASR evidence; baseline shortlist preserved.
- 🧪 Step 3 — Reopened for the matched contextual evaluation protocol; baseline harness preserved.
- 🧪 Step 4 — Reopened; Sherpa remains the context-free reference pending expanded evidence.
- 🚧 Step 5 — 5.5 partial: the user found live dictation on termidor "pas mal"; key-by-key checks and live-input memory not yet recorded.
- ⏸️ Step 6 — Superseded: the hardware has arrived; its board characterisation belongs to the Luna workline, and Mycroft's on-device validation is Step 8.
- 🚧 Step 7 — Dictation provider for the Slate: 7.1–7.4 done; 7.5 waits for Wyoh's Step 12, Step 8, and the user.
- 🚧 Step 8 — Dictation usable on Luna: 8.1–8.4 done. Best is 2 threads at RTF 1.32, still slower than real time. Load is ~17 s of ONNX Runtime CPU work (13 s pre-optimised). Python costs only ~15 MiB. 8.5 awaits the user's review; 8.6 ready; 8.7–8.8 follow.

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
| 2026-10-11 | 5.5 partial: the user ran the console with the real front-panel microphone on termidor (`/dev/snd/pcmC0D0c`) and judged it "pas mal". Key-by-key observations and a foreground RSS reading on live input are not yet recorded. |
| 2026-10-11 | User green-lit 7.3b: install on Luna and measure memory/CPU there, with priority over Wyoh; Luna access to be arranged through Professor; reboot between operations. Preparing the bundle and live test offline; waiting for access. |
| 2026-10-11 | Professor (`tanstfaafllm-80`) set the Luna slot: after Wyoh's current app series (about 13:30 at the latest), Mycroft first in `worklines/luna-access.md`; offline preparation done, waiting for "Luna is yours". |
| 2026-10-11T12:38 | Professor: "Luna is yours" (Wyoh released it after a reboot). Starting 7.3b: preflight, install, measure. |
| 2026-10-11T12:50 | 7.3b done: Mycroft installed on Luna and measured (3 runs). Luna rebooted and released to Professor. |
| 2026-10-11 | The user's decisions after `0703_01`, relayed by Professor: add 7.3c (threads 2/4), 7.3d (load-time breakdown, pre-optimised model, resident provider; swap measured only), 7.3e (Sherpa C++ binary vs Python). Preparing offline; waiting for Luna. |
| 2026-10-11 | Plan reordered at the user's request: Step 7 keeps the Slate provider (7.1–7.5; 7.3 closed, the `luna-pi` measurement superseded by Luna); the Luna performance work becomes **Step 8** (8.1 = former 7.3b, 8.2 = 7.3c, 8.3 = 7.3d a, 8.4 = 7.3e, 8.6 = 7.3d b), with 8.5 (int8 vs fp32, proposed) from Professor's note `0703_02`, and 8.7–8.8 (profile choice, acceptance). File names are unchanged. |
| 2026-10-11 | 🟩 go 8.2, 8.3 and 8.4 from the user, who gave Mycroft Luna directly ("tu as Luna pour toi"). Run those three, then pause for the user to review the results before 8.5. 8.6 is not in this run. |
| 2026-10-11T13:55 | 8.2–8.4 run on Luna (extra files installed, 129.7 MB). Results in `0802_01`. Luna rebooted and released to Professor. Paused for the user's review before 8.5. |
| 2026-10-11 | Professor paused every session (usage limit), then resumed. Mycroft state unchanged: 8.1–8.4 done (`0802_01`). **Waiting for the user:** their review of `0802_01`, a 🟩 go for 8.5 (int8 vs fp32), and whether 8.6 (resident provider) runs in the same Luna slot. Wyoh holds Luna; Mycroft asks Professor for a slot only after the user decides. Nothing started meanwhile. |
| 2026-10-11 | User request: a lighter model and known words. Opened Step 9; 9.1 (hotwords check) and 9.2 (desk review) started on the desk host; 9.3–9.5 proposed. |
| 2026-10-11 | 9.1 and 9.2 done on the desk host (`0901_01`). Hotwords work, but partially: spelling-based, so Wyoh needs its pronounced form. Kroko French is the candidate for a lighter model. 9.3–9.5 await the user's go. |
| 2026-10-11 | User decision: freeze the current model (8.5, 8.6 and 9.5 parked) and look for a substantially lighter one. 9.3 (Kroko) go; 9.6 added for Parakeet Redux (user) and Phonon-2 (Charlie; rejected, English only). Desk-host evaluation first, then Luna through Professor. |
| 2026-10-11 | 9.3 desk result: Kroko is clearly ahead of the current model on the user's voice (WER, CPU, memory, punctuation); its load is longer. 9.6: Parakeet Redux and Phonon-2 rejected for Luna (no aarch64 engine; PyTorch and ~600 M parameters). The user would accept English for an efficient model; noted, though it changes nothing here. The Kroko Luna test is ready; asking Professor for a slot. |
| 2026-10-11T22:34 | Professor gave Luna for 9.3 (~20 min). Running `test_luna_9_3_kroko` with reboots. |
| 2026-10-11 | The user asked to test on `luna-pi` before Luna. The Luna 9.3 run was stopped during the Kroko upload (partial `encoder.onnx` left under `/storage/.local/opt/mycroft`; no measurement). Luna was rebooted and released to Professor, who gave Mycroft `luna-pi`. |
| 2026-10-11 | 9.3 on `luna-pi` (Cortex-A72): Kroko RTF 0.20 at 2 threads against 0.37 for the current model, 159 against 222 MiB, but a 10.9 s load against 4.1 s. Diagnosing Kroko's load there with ONNX Runtime's Python package in a venv under `~/.local/opt` (no system change). |
| 2026-10-11 | Kroko's load diagnosed on `luna-pi`: opening the published encoder costs 5.1 s even with optimisation off. Re-saved on aarch64 at the portable "extended" level, Sherpa loads Kroko in 6.1 s instead of 11.0 s, with the same text and speed. `luna-pi` released to Professor without a reboot (the user's interactive session was open). Results in `0903_02`. |
| 2026-10-11 | User decision: the model must be resident (no load wait at all); Kroko is adopted if it is real-time on Luna, ~40 % lighter, and of the same quality. Added `--model` to the console and provider for the user's live quality test on termidor. |
| 2026-10-11 | User live test on termidor: Kroko's quality is "top", with fewer errors and punctuation. **Decision: Kroko is kept.** Next: measure it on Luna (`test_luna_9_3_kroko`); asking Professor for a slot. |
| 2026-10-11 | **9.3 measured on Luna** (`results/mycroft/luna-footprint/20261011T213949Z/`, rebooted before and after, then released). As published, at 2 threads: Kroko RTF 0.76–0.79 (keeps up with speech) against 1.48–1.54 for the current model; peak RSS 167 against 236 MiB (−29 %); load 47.7 s against 17.5 s. At 1 thread Kroko is at RTF 1.14–1.20. The `luna-pi` projection held (RTF ~0.8, load ~45 s). Next: a resident provider with Kroko, loaded from the aarch64-prepared files. |
| 2026-10-13 | Wyoh's note `0903_03` relays the user's decisions: Kroko for the Slate, kept loaded while the Slate is hidden. Added 9.7 (resident provider) and 9.8 (prepared Kroko installed and measured on Luna). The user said to continue. |
| 2026-10-13 | 9.7 done on the desk host (resident mode, tests). The adapter's missing tail padding (Kroko dropped its last word) was fixed with 1.0 s. Prepared Kroko made and verified; the `kroko-fr-2025` profile uses it. Luna test 9.8 ready; asking Professor for a slot. |
| 2026-10-13 | **Blocked on Luna access:** no Professor session is running, and Wyoh holds Luna (Wolfenstein controls). Mycroft added itself to the `luna-access.md` queue and asked the user. |
| 2026-10-13 | Professor (tanstfaafllm-96) gave Luna for 9.8. **9.8 done** (`0908_01`): resident Kroko on Luna ready in 24.4 s, 151.5 MiB idle, 172 MiB peak, 0.002 s start→listening, keeps up with speech at 2 threads. Luna rebooted and released; reply written in Wyoh's note `0903_03`. |
| 2026-10-15 | User: "put Kroko in the Slate as soon as possible". Mycroft's side is ready; the rest (command line in `gamepad.toml`, deploy, live test) is Wyoh 12.4, in files Wyoh is editing. Professor's session tanstfaafllm-96 is gone, so the message bounced. Note left to Wyoh: `worklines/wyoh/docs/1204_01`. Asked the user which live session is Professor or Wyoh. |
| 2026-10-25 | Professor (tanstfaafllm-2a), at the user's request: close what Wyoh 12.4's delivery settles. Wyoh deployed resident Kroko in the Slate on 2026-10-15, and the user's voice test worked. **7.5 closed.** 8.7: profile recorded (Kroko prepared, resident, 2 threads, Python); code defaults still open. 8.8: speed met; start time and memory beside Wyoh still open. 9.3: adopted; licence still unconfirmed. Luna not touched. |
| 2026-10-25 | User: Professor puts Mycroft in contact with Mannie, who is on Luna and does all operations there; after that Mycroft may talk to Mannie directly. Asked Professor for this. Planned through Mannie: check dictation on the new Arch Linux ARM root (note `worklines/mannie/docs/0700_02`), then 8.8's memory measurement beside Wyoh's session. |
| 2026-10-25 | Professor relayed the request to "Mannie from Luna" (the Claude session on Luna). Mannie runs check 1 and prepares the 8.8 slot. Direct contact waits for the user's confirmation, which Professor asked for; until then Mycroft writes through Professor. Luna's token is with Mannie, so nothing is run on Luna before Mannie says it is ready. |
| 2026-10-25 | User confirmed via Professor: Mycroft may message "Mannie from Luna" directly about Luna operations. **Mannie's check 1 on the new root:** passes, except capture.
- Present: python3 3.14.8 and `arecord`; `michael` is in `audio`.
- The resident Kroko loads its libraries from `/storage` (root, RSS 130 MiB). About 305 MiB is available with Wyoh's session and Kroko resident; this is a first 8.8 figure, not yet measured during a dictation.
- **The USB-C headset is not seen** (no card 1, only the USB root hub), so the resident Kroko captures from card 0, the jack, which gave no signal in Luna 8.2c. Slate dictation therefore cannot hear the user until the headset is back. Mannie asked the user.

8.8 waits on three things from the user: the headset seen as card 1 (or the WAV replay alone accepted), a go for the two reboots, and Mannie stopped during the slot. |
| 2026-10-28 | Rule from the user, relayed by Professor: Mannie on Luna is Luna's operator. Before any SSH to Luna, tell Mannie what will run and get its "go". Never reboot Luna while Mannie runs there. The user plugged the headset back in (card 1). Mannie: "ready for 8.8", user go given, waiting for `mannie stop`. Prepared `test_luna_8_8_slate_session` (`slate_session_probe.py`): it measures memory in the real Slate session (Wyoh's daemon with its resident Kroko, no second load) while the user dictates with L2, with a reboot before and after. |
| 2026-10-28 | **8.8 accepted by the user** (`0808_01`). With Wyoh's session and resident Kroko on the new root, 515–525 MiB is available, and Kroko is at 163 MiB. The probe missed the dictation state, so there is no figure during a dictation; the user judged it not needed. A fix to the harness's reboot wait is included. Mannie was stopped for the slot; the user restarts it. |
| 2026-10-30 | User decision relayed by Professor: sessions may message each other directly (roster in `worklines/agents.md`). Still in force: no SSH to Luna without Mannie on Luna's go. Sent the 8.8 result to Mannie from Luna directly, as it asked. |
| 2026-10-30 | Professor, at the user's request: a coordinated commit, in the order Mike → Mycroft → Luna → Mannie → Professor. Mycroft commits only `test/mycroft/` and `worklines/mycroft/`, and does not push. Script `tmp/commit_mycroft_8_8.sh` is prepared; it waits for Professor's "your turn" and the user's go. |

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
- `worklines/mycroft/docs/0703_01_luna-footprint-result.md` — Step 8.1 (formerly 7.3b): first install and memory/CPU footprint on Luna.
- `worklines/mycroft/docs/0703_02_note-from-professor-onnx-load-time.md` — Professor's note behind 8.3 and 8.5.
- `worklines/mycroft/docs/0802_01_threads-load-compiled-result.md` — Steps 8.2–8.4: threads, load-time breakdown and pre-optimised model, Python against C++ on Luna.
- `worklines/mycroft/docs/0901_01_known-words-and-lighter-models.md` — Steps 9.1–9.2: hotwords on the current model; one language, Kroko, and fine-tuning.
- `worklines/mycroft/docs/0903_01_lighter-candidates-desk-result.md` — Steps 9.3 and 9.6 on the desk host: Kroko against the current model; Parakeet Redux and Phonon-2 rejected for Luna.
- `worklines/mycroft/docs/0903_02_kroko-on-luna-pi.md` — Step 9.3 on `luna-pi`: Kroko against the current model, its load diagnosis, the aarch64-prepared files, and a projection to Luna.
- `worklines/mycroft/docs/0703_03_note-from-professor-opencl-parked.md` — Professor's note on the parked GPU/OpenCL idea.

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
