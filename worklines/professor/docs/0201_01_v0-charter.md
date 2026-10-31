# 0201 — TANSTAAFLLM v0 charter

> **Freshness:** 🟡 historical · **Written:** 2026-09-27 · **Checked:** 2026-10-31 · **Step:** professor 2.1 ✅

**Question answered:** What is the one immediate v0 outcome, where does it run, and how will we know it is useful without pretending the whole handheld system already exists?

**Status:** review-ready draft, 2026-09-25<br>
**Decision proposed for ratification:** the project’s immediate v0 is **Mycroft v0: offline French audio-file transcription to text**. The longer product direction is an inspectable, AI-native handheld development companion presented as Adam; it is not the deliverable called “v0” here.

## Why this is the v0

It is the only currently authorised path that can be completed and measured before Luna arrives. It validates a foundational input capability without assuming a microphone, GPU driver, UI stack, always-listening service, local LLM, or remote model. It also gives the project a concrete way to practice TANSTAAFL: model and dependency costs are measured rather than narrated.

## Outcome statement

A clean developer environment can install one documented local runtime and model asset, run a narrow CLI on a recorded French audio file, and receive a UTF-8 transcript while recording the model/runtime version and measured resource cost. The command works without network access after installation and asset acquisition.

This v0 does **not** claim to be a voice assistant. It is intentionally:

```text
audio file → Mycroft → text
```

It is not yet:

```text
microphone → Mycroft → Mike → Wyoh/tools/Mannie → Adam speech or dialogue
```

## System boundary

| Location | Permitted v0 role | Explicitly not claimed |
| --- | --- | --- |
| Desktop development machine | Documentation, candidate research, consented test corpus, reproducible harness, and local evaluation. Codex/Mannie-style development may use normal desktop permissions. | Evidence that a desktop benchmark fits Luna; a VM/emulator that pretends to be Luna. |
| `luna-pi` (Pi 4B) | Optional supplementary measurement/reference target after inventory, reached through SSH. | A substitute for Luna hardware, or a required v0 dependency. |
| Luna | No implementation or configuration work before delivery and inventory. Later it validates the selected path against real memory, audio, thermal, battery, and driver facts. | Assumed microphone, GPU, storage, or OS behaviour. |
| Remote services | None required at runtime. Network access may be used to obtain pinned dependencies/assets during setup, with provenance recorded. | Remote transcription, hidden fallback, or mandatory frontier-model reasoning. |

## Operational requirements

- **Language:** French is primary. English and mixed technical vocabulary are secondary evaluation cases.
- **Execution mode:** one model/runtime, loaded on demand for an audio file and then exits.
- **Offline property:** after documented installation and local asset acquisition, transcription has no network dependency.
- **Input/output:** recorded audio in; plain UTF-8 text out. Exact formats, timestamps, punctuation, and error behaviour are frozen by Mycroft Step 1.
- **Evidence:** every trial records candidate/runtime/asset identity, input fixture, transcript, elapsed time or real-time factor, peak memory where measurable, disk/dependency footprint, and errors.
- **Data restraint:** use a small consented corpus; do not retain recordings by default outside the defined test material.
- **Target honesty:** desktop and Pi results are labelled non-target evidence. No target-fit assertion is valid until Luna is measured.

## Success measures and gates

| Dimension | v0 success condition | Deferred measurement / decision |
| --- | --- | --- |
| Usability | One documented command produces readable French text from an agreed fixture and reports a clear failure for invalid input. | Live microphone, wake word, dialogue, and response presentation. |
| Reproducibility | A clean developer environment follows documented setup and repeats the result with the pinned asset/runtime. | Packaging/distribution for Luna. |
| Quality | The selected model is compared against one challenger on the same consented corpus; qualitative errors and technical-term failures are recorded. | Context biasing, personal-voice adaptation, and a production accuracy threshold. |
| Resource cost | Resource ledger records model asset, installed/runtime footprint, peak RSS, CPU time, cold start, storage, and any GPU/shared-memory allocation. | Exact Luna memory reservation after hardware inventory. |
| Responsiveness | Cold start and elapsed time/real-time factor are measured and published. | A hard handheld interactive-latency target, which requires the delivered audio path and device measurements. |
| Battery/thermal | No pre-hardware claim. | Real Luna battery, thermals, and sustained-load behaviour. |
| Learning goal | The project can explain why the chosen candidate won, what it costs, and what was excluded. | A general Mike/assistant architecture. |

A candidate fails v0 selection if it requires remote inference, cannot be reproduced, has unclear licence/provenance, exceeds the agreed resource ledger, or needs an unbounded runtime/dependency chain. No numeric target budget is invented before Step 1 defines the ledger and Luna is inventoried.

## Explicit exclusions

- Text-to-speech, Adam persona/dialogue, and spoken replies.
- Context biasing from files, Git, CLI state, or Wyoh.
- Intent detection, command routing, tool use, shell access, and development automation.
- Always-listening or resident voice processes; parallel ASR models.
- GPU/Vulkan dependence, target flashing, firmware changes, and target-specific audio work.
- A local LLM, JEV-like router, or Codex/Claude integration as a runtime requirement.
- Any claim that `luna-pi` or desktop measurements certify Luna compatibility.

## After v0

The immediate next action is **not automatically an implementation expansion**. After review of this charter and Mycroft results, the user chooses the next green-lit workline step. Likely candidates are Luna hardware characterisation on arrival, a bounded Mike/frugal-routing research line, or a Wyoh HIOM proof; the decision remains with the user.
