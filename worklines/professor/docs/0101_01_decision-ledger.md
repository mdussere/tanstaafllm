# 0101 — Initial-discussion decision ledger

**Question answered:** What did the complete initial discussion actually establish, and what remains a proposal or an unverified claim?

**Status:** review-ready draft, 2026-09-25<br>
**Evidence basis:** the complete 155-message transcript, plus the later repository decisions now recorded in `docs/01_principles.md` and active workline plans. The transcript is evidence of intent and ideas, not independent technical verification.

## Reading rule

This ledger uses four classes:

- **Active decision** — a user direction that remains consistent with newer project records.
- **Strong preference / design direction** — clearly desired, but not yet a delivery commitment or measured fact.
- **Hypothesis / research question** — a claim about hardware, software, models, or feasibility that needs evidence.
- **Superseded / not selected** — historical wording or an assistant proposal that must not guide current work.

Later explicit repository decisions take precedence over earlier transcript wording. In particular, `Luna` supersedes `HOLMES-36` as the active machine name, and the current Mycroft plan supersedes early GPU-first ASR speculation.

## Active decisions

| Area | Decision | Practical consequence |
| --- | --- | --- |
| Project philosophy | TANSTAAFLLM means “There Ain’t No Such Thing As A Free LLM.” | Account for memory, CPU, battery, latency, bandwidth, privacy, cost, and maintenance; use the least sufficient capability. |
| Target identity | The intended handheld is **Luna**. | Target-device conclusions wait for delivered-hardware characterisation. |
| Reference target | The Raspberry Pi 4B is **`luna-pi`**, a reference/prototyping target. | It is useful for development and comparison, but cannot stand in for Luna validation. |
| Development route | Development happens first on the desktop; devices are reached through SSH. | Mannie/Codex has normal developer authority only; Luna is not treated as the primary coding workstation. |
| Public interface | The person addresses **Adam**; Mike remains internal. | “Adam, …” is the interaction identity, not a separate brain or compulsory wake word. |
| Component split | Mike reasons/routes; Mycroft supplies voice input; Wyoh exposes state/actions; Mannie performs development work. | Boundaries and ordinary permissions are mandatory; the names are responsibilities, not required processes. |
| Mycroft v0 | Start with local, context-free French ASR from recorded audio to text. | No TTS, command execution, Mike/Wyoh/Mannie integration, wake word, context biasing, or resident daemon in v0. |
| Resource discipline | A single small, on-demand CPU ASR path is the v0 baseline. | GPU offload and multiple concurrent models are experiments, not v0 dependencies. |
| Wyoh direction | The system must expose structured state and finite available actions rather than depend on screenshot interpretation. | The controller-first HIOM/stock-front-end-first product path remains a separate Wyoh decision track. |
| Scope protection | Do not start Wyoh runtime work with a VM/emulator while hardware is absent. | Pre-hardware Wyoh work is documentation/design only unless its own plan receives a later green light. |
| Repository practice | Documentation and plans are kept in the repository and broadly committed. | Preserve raw source evidence separately from decisions and verified facts. |

## Strong preferences and architectural direction

| Direction | What the discussion supports | Boundary retained now |
| --- | --- | --- |
| Pocket development companion | Luna should eventually support a person directing development, Git interaction, builds/tests, and Codex-mediated work from a constrained handheld. | This is the product ambition, not Mycroft v0 and not a claim that Luna can build every project locally. |
| AI-native control surface | The machine should be more legible than a terminal-only or pixel-scraping interface. | Wyoh owns the state/action contract; no particular window manager or compositor is selected by this statement. |
| Layered intelligence | The early sketch separated ASR, a frugal local system assistant, and a frontier development assistant. | Keep least-sufficient routing as a principle; exact models and deployment remain unselected. |
| Frugal non-LLM reasoning | JEV/BERT-like classifiers or similar small mechanisms are attractive for some “brain” tasks. | This is a future research direction, not an approved Mike implementation or workline. |
| Thematic vocabulary | *The Moon Is a Harsh Mistress* supplies the names and restrained interaction language. | Theme must clarify costs, status, and recovery; it must not hide ordinary technical meaning. |
| Remote services | Frontier reasoning may be worthwhile when its capability justifies the visible cost. | It is a deliberate later escalation; no remote model is mandatory for Mycroft v0. |

## Hardware and technical hypotheses

These are useful research inputs, not accepted facts.

| Topic | Current evidence level | Required next evidence |
| --- | --- | --- |
| Luna hardware profile | User-reported purchase/listing suggests an RK3326/Mali-G31-class, Linux handheld with about 1 GiB RAM and 128 GB storage. Variant, board, firmware, and actual available memory remain unknown. | Inventory the delivered unit before installing, flashing, benchmarking, or relying on any interface. |
| GPU use | The discussion explored using the GPU for ASR or a second non-LLM workload. | Identify the actual driver/API and measure total shared-memory and latency impact against CPU baseline. |
| Audio interfaces | Microphone, jack, Bluetooth, and other integrated sensors were investigated but not established. | Hardware inventory and audio-path test on arrival. |
| Pi capacity | The Pi is known to be a 2018 Pi 4B; its RAM/storage/OS configuration was not verified in the source discussion. | Inventory `luna-pi` before treating it as a constrained reference. |
| Local models and runtimes | `llama.cpp`, Whisper, Zipformer/Sherpa, Moonshine, small LLMs, and BERT/JEV-like systems were discussed. | Current upstream evidence, licence, reproducible install, and measured resource ledger for the precise candidate. |
| Handheld display stack | Numerous WM/compositor options were discussed. | Luna stock-front-end inventory first; then compare only the paths the active Wyoh plan names. |

## Superseded, declined, or deliberately deferred items

- **`HOLMES-36` as the active machine name** is historical; the user later chose **Luna**. Existing occurrences should be treated as legacy wording and corrected only through the owning document/workline.
- **GPU-first voice-to-text** was an early idea. The active Mycroft plan makes CPU-only, native, on-demand ASR the baseline because the target’s shared 1 GiB budget and graphics stack are unverified.
- **A “Mini Scout”/RSS aggregation appliance** was an assistant-proposed Pi direction, not a user-selected product v0. It is not an active delivery track.
- **A multi-agent Docker system**, a physical voice assistant, a VM/emulator for the handheld, and a custom compositor fork are exploratory ideas, not authorised implementation work.
- **Domain purchase** was considered and then declined as too expensive/not useful at this stage.
- **Exact model sizes, performance, and support claims** in the transcript are not decision evidence; they must be re-researched when a workline reaches them.

## Arbitration list for the next review

1. **Project/repository spelling:** retain the current repository slug or make the intended TANSTAAFLLM spelling consistent through a deliberate rename.
2. **Meaning of “v0”:** ratify the proposed split in the charter: Mycroft v0 is the immediate, narrow deliverable; the Adam-capable handheld is the longer product direction.
3. **Post-Mycroft priority:** choose whether hardware characterisation, a Mike/frugal-routing investigation, or a Wyoh interface proof follows once the relevant green lights exist.
4. **Luna inventory authority:** confirm the safe first-arrival protocol and whether any existing firmware must be preserved/imaged before experimentation.
5. **Cost visibility:** decide the minimum user-visible resource/status information Adam should surface in the first integrated experience.

## Reconciliation result

The earlier translated analysis is retained as a historical partial synthesis. This ledger supersedes it as the Professor workline’s decision baseline because it incorporates the full transcript and reconciles it with later, explicit repository decisions.
