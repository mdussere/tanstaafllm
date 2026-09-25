# 0001 — Initial discussion analysis

> Translation note: this is the English translation of the earlier synthesis. It was written before the complete 155-message transcript was recovered, so it is a useful working baseline—not yet the authoritative project decision record.

## Purpose and scope

This note synthesises the initial conversation about using an unused Raspberry Pi in **TANSTAAFLLM**. It distinguishes points established in the discussion from recommendations and technical assumptions that still need validation on the actual machine.

The four images shared in the conversation were not available in the text export, so their contents cannot be treated as established evidence.

## Executive summary

The Raspberry Pi should primarily be treated as a small, always-on, low-power ARM appliance—not as a machine for ambitious LLM inference. Its most promising role is as a **reference and prototyping target** for the future device, Luna, and potentially as the local node of a hybrid LLM system: storage, collection, tools, scheduling, and API services run locally; expensive reasoning can be delegated to a remote LLM API when needed.

The proposed name for this prototype is `luna-pi`. SSH is the planned administration path; Raspberry Pi Connect is deliberately kept as an optional fallback.

## Hardware baseline

### Reported information

| Topic | Status | Detail |
| --- | --- | --- |
| Machine | to confirm | It was first described as a Raspberry Pi 4 with 4 GB, then as a Pi 4B whose specifications were not available. |
| Previous use | reported | It may have been used professionally to boot or provision servers in a datacentre. |
| Cooling | observed / interpreted | A large heatsink and two fans were mentioned. This is consistent with continuous operation, but does not reliably indicate RAM capacity. |
| Likely memory | hypothesis | 2 GB was considered plausible; 4 GB remains possible if the organisation standardised on that configuration. Neither value was verified. |

### Consequences retained from the discussion

- The architecture must not rely on the 4 GB assumption before hardware verification.
- A 2 GB target remains useful: it is sufficient for light services while being close enough to Luna’s stated 1 GB constraint to expose resource limits early.
- The priorities are memory efficiency, reliable 24/7 operation, and observable services—not the largest possible local model.

### Checks required before committing to a design

1. Identify the exact board model, RAM capacity, and available storage.
2. Record the OS, kernel version, CPU architecture, and idle/load temperatures.
3. Check power, networking, and fan behaviour.
4. Establish an actual memory and CPU budget before selecting models or multiplying services.

## Raspberry Pi role in the project

### Preferred direction

The preferred direction is not to run “the largest possible Llama”, but to make the Pi an **LLM appliance**. It can stay online continuously and provide functions that benefit from a local presence without requiring a powerful GPU:

- a local API, for example FastAPI;
- scheduled and periodic jobs;
- light persistence, for example SQLite;
- source collection and storage;
- small-scale embeddings, indexing, or clustering;
- tools exposed to a remote model;
- metrics, logging, and experimentation.

Expensive reasoning can be delegated to an LLM API. This separation keeps the system useful even when local inference is slow or memory-constrained.

### Position relative to Luna

```text
luna-pi  = reference and prototyping target
luna     = final RK3326 handheld target
```

`luna-pi` is therefore not a disposable machine used only until Luna arrives. It should remain the development, validation, and comparison bench for the final target. That continuity makes it important to document hardware differences and test constraints early.

## Functional directions discussed

### 1. Lightweight local inference

This direction is useful for learning and measurement, but was not considered the primary objective.

- Proposed runtime: `llama.cpp`.
- Proposed formats: quantised GGUF models.
- Discussed range for a Pi 4 with 4 GB: 0.5B–1.5B parameter models; a 3B Q4 model might be attempted, but with slow performance and tight memory.
- Named candidates: Qwen 2.5 0.5B / 1.5B, SmolLM2 1.7B, and TinyLlama 1.1B.

Useful experiments would compare tokens per second, quantisation, RAM use, CPU temperature, context size, and generation parameters. Simplified tool calling, embeddings, and tokenisation were also identified as learning topics.

These model sizes and performance expectations are discussion estimates, not benchmarks on the real machine.

### 2. Mini Scout at home — recommended direction

The preferred project idea was a local monitoring and aggregation pipeline:

```text
collect → embed → cluster → name → aggregate / summarise
```

Possible inputs include RSS feeds, selected web pages, local documents, and possibly MQTT or home-automation data. The Pi stores and prepares the data; an LLM can name and summarise the resulting information clusters.

This is aligned with the Pi’s capabilities and would exercise persistence, scheduling, embeddings, clustering, RAG, APIs, agents, and evaluation together.

### 3. Multi-agent orchestration

Another idea was to run several Docker services with distinct roles, memories, and tools. They would answer independently, critique one another, and then a final agent would arbitrate.

The Pi would orchestrate the system while models could be accessed through APIs. This remains an idea, not a selected project or validated architecture.

### 4. Hardware voice assistant

The proposed physical chain was:

```text
microphone → Whisper / whisper.cpp → LLM → tools → Piper TTS → speaker
```

Speech recognition and synthesis could be local while reasoning used an API. This remains exploratory: no microphone, speaker, STT/TTS model, or latency target has been selected.

## Identity and naming

### Prototype name

`luna-pi` is the preferred prototype name because it explicitly identifies the Raspberry Pi prototype of Luna without conflating it with the final device.

| Element | Proposal |
| --- | --- |
| Prototype name and hostname | `luna-pi` |
| Final product / target | `luna` |
| Announced final platform | RK3326 handheld |

Alternatives mentioned were `luna-proto`, `little-luna`, `luna-0`, `luna-earth`, and `terraluna`. None displaced `luna-pi`; `terraluna` was explicitly discouraged because of its crypto association.

### Domain name

Buying a domain was considered, but no domain name, registrar, intended use, or purchase decision was made.

## Remote access and operations

### Direction retained

```text
Desktop PC / Codex
        │
       SSH
        │
        ▼
     luna-pi
```

SSH is preferred because it is standard, lightweight, automatable, and close to the access model expected for Luna. It should be the foundation for administration, deployment, and automation.

### Raspberry Pi Connect

Raspberry Pi Connect was identified as an official browser-based remote-access service, offering shell access and—in desktop installations—screen sharing. It was not selected as an initial TANSTAAFLLM dependency.

It could become a fallback access path, for example from a phone, if that need is confirmed. Activating it is neither necessary nor a priority at the start.

## Decisions, recommendations, and open questions

| Category | Item | Status |
| --- | --- | --- |
| Name | Use `luna-pi` for the prototype | strongly preferred proposal; explicit confirmation still needed |
| Role | Keep the Pi as the reference/prototyping target | established direction |
| Access | Use SSH as the primary route | established direction |
| Connect | Do not add it to the initial dependency set | retained recommendation |
| LLM workload | Prefer orchestration and lightweight services to a large local model | established direction |
| First use case | Explore a Mini Scout at home | priority recommendation; not a delivery decision |
| Hardware | Exact RAM, storage, and device condition | unverified |
| Inference | Model, quantisation, runtime, and metrics | unselected |
| Infrastructure | Docker, FastAPI, SQLite, data schema, external API | suggested; unvalidated |
| Domain | Purchase, name, and purpose | open |

## Coherent starting sequence from the discussion

1. Inventory the hardware and install or configure a minimal OS.
2. Set the `luna-pi` hostname if the name is confirmed.
3. Establish SSH key access and document connection from the development machine.
4. Measure available resources, then test a small quantised local model with `llama.cpp`.
5. Select one simple vertical, such as RSS collection + SQLite + remote summarisation.
6. Add embeddings, clustering, and automation progressively while measuring memory, temperature, latency, and reliability.
7. Keep the system light and reproducible so it remains a credible reference for Luna.

## Limits of this synthesis

- It reflects what was said, not the actual state of the hardware.
- Model, memory, and performance claims must be revalidated on `luna-pi`.
- The conversation images are not analysed.
- No final choice of product scope, full stack, domain, or LLM provider has been made.
- It does not incorporate the remainder of the recovered 155-message transcript; resolving that gap is the first action proposed in the Professor workline plan.
