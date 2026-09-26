# TANSTAAFLLM principles and concept

**Status:** living conceptual reference<br>
**Scope:** project identity, interaction model, component roles, and design principles

## Purpose

TANSTAAFLLM is an experiment in making a modest handheld computer into a useful, inspectable, AI-native personal system. The project is not a quest to put the largest possible model on constrained hardware. It is a search for the smallest, most appropriate capability at each point in the system.

The project draws its vocabulary and narrative energy from *The Moon Is a Harsh Mistress*. The reference is a design lens, not an instruction to turn the product into a costume of the novel: names must clarify responsibility, and the interface must remain useful to someone who does not know the source material.

## The governing idea: no free LLM

**TANSTAAFLLM** expands the familiar TANSTAAFL principle into “There Ain’t No Such Thing As A Free LLM.” Intelligence consumes something: memory, CPU time, battery, latency, bandwidth, money, privacy, or attention.

This is not anti-LLM. It is a discipline:

- use a deterministic rule, a small classifier, or a specialised model when that is enough;
- use a local model when local execution is the appropriate trade-off;
- use a frontier model only when its added capability is worth the visible cost;
- let the user see material costs and consequences rather than hiding them behind magic.

The current repository slug is historical and may not match the intended project spelling exactly. Naming and repository-renaming decisions remain administrative work; they do not change this conceptual model.

## World and nomenclature

| Name | Role | User-facing? | Notes |
| --- | --- | --- | --- |
| **TANSTAAFLLM** | project and design philosophy | yes | The whole experiment and its resource-aware principle. |
| **Luna** | handheld device and its local environment | yes | The home of the system’s components. |
| **luna-pi** | Raspberry Pi reference/prototyping target | mostly internal | A development and comparison target, not a replacement for Luna. |
| **Adam Selene** / **Adam** | the system’s human-facing identity | yes | The person-like interface the user addresses. It is not another intelligence or privileged agent. |
| **Mike** | local brain | internal | Interprets requests, holds or consults state, routes work, and decides which capability to invoke. |
| **Mycroft** | input and composition capability | internal | Turns voice into an editable, reviewable proposal. Its ASR baseline is context-free; bounded contextual vocabulary is a separately measured later capability. |
| **Wyoh** | interface, state, context, and possible actions | internal, rendered to the user | Makes the environment legible and actionable for Mike and Adam. |
| **Mannie** | development capability | internal | One use of Luna: code, build, test, and development tasks using Codex or another frontier model within normal developer permissions. |
| **Professor de la Paz** / **Professor** | coordinating workline | internal | Maintains project direction and the coordination and isolation of specialised worklines; it is not another system runtime or local model. |

The naming is deliberately layered. **Luna is the machine. Adam is the assistant a person uses. Mike is the local intelligence behind Adam.** Mycroft, Wyoh, and Mannie provide specialised input, environment, and development capabilities. **Professor** is the coordinating project workline, not another component running on Luna.

## Adam Selene: one public identity, not one more agent

Adam Selene is the public identity under which Mike presents itself to the user. Adam is not a second brain, a hidden model, or an additional authority layer.

Mike reasons and routes. Adam communicates: it provides a stable point of address, turns outcomes into human-facing language, and may eventually own dialogue, notifications, and speech output. That gives the system a clear external/internal separation:

> **Mike thinks. Adam speaks.**

The user does not need to know which internal component completed a request in order to use the device. The system, however, must keep those components inspectable: Adam must not obscure what Mike decided, what Wyoh observed, which tool ran, or whether Mannie/Codex was involved.

## Interaction model

The intended interaction is not “Hey Siri.” The natural form is an instruction addressed to Adam:

- “Adam, open the TANSTAAFLLM project.”
- “Adam, show me what Mannie changed.”
- “Adam, ask Mannie to fix this.”
- “Adam, compile and test.”

`Adam` is a natural vocative and a clear human-facing identity, not a mandatory wake word. In an already open interaction, repeating it should not be necessary. A future Mycroft may treat it as a strongly biased word when it is present, but wake-word detection is not a prerequisite for the system.

### Request and response path

```text
Voice input                         Typed or UI input
───────────                         ─────────────────
user ──audio──► Mycroft ──text──┐   user ──request──┐
                                │                  │
                                ▼                  ▼
                          Mike — local brain / routing
                                │
                 ┌──────────────┼──────────────┐
                 ▼              ▼              ▼
              Wyoh            tools          Mannie
        state, context,     local system,    development
        possible actions    services, data   / Codex
                 └──────────────┼──────────────┘
                                ▼
                  Adam Selene — human-facing result
                    text, status, dialogue, notifications
```

The diagram is a responsibility map, not a claim that all components must be processes or models. A v0 may implement only a small part of it.

## Component contracts

### Mycroft → Mike

Mycroft turns audio into an editable, reviewable composition proposal. Its measured first slice is deliberately context-free speech-to-text. A later bounded context input may use mode-appropriate vocabulary, but it must remain optional, source/revision-labelled, costed, and incapable of granting execution authority. Acceptance remains distinct from an action request.

### Mike ↔ Wyoh

Wyoh describes the current environment in a form Mike can use: state, focus, available actions, and consequences. Mike requests or selects an action; Wyoh makes the result and changed state legible. This boundary keeps the brain from relying on an opaque desktop.

### Mike ↔ Mannie

Mannie is development work, not the operating system’s universal brain. It can use Codex or another frontier model for code, build, test, and Git tasks. It has no greater authority than the normal development workflow: its actions remain subject to the same permissions, review, and observability as development from the desktop.

### Mike / components → Adam

Adam is the surface that explains results to the person. It should be able to distinguish a completed action, a proposed action, a blocked action, a degraded result, and an external-model request. The user should see meaningful status rather than a fabricated impression of certainty.

## Design principles

### 1. Local-first, but not local-only

Luna should remain useful without a network where its local capabilities suffice. A remote model is a deliberate escalation, not the hidden default.

### 2. The least sufficient intelligence

Use the smallest and cheapest mechanism that can meet the task. A full LLM is not the answer to every language, routing, status, or control problem.

### 3. Explicit boundaries over a monolithic assistant

Input, reasoning, state/UI, development, tools, and presentation have different constraints. Naming these roles is useful only if their contracts remain clear and components can be replaced independently.

### 4. State must be inspectable

The system must expose what it knows about the current environment, what it can do, and what it is doing. Wyoh is central to this principle; Adam should communicate it rather than conceal it.

### 5. Human agency and ordinary permissions

The system may propose, automate, or invoke tools, but it must not turn a conversational interface into unreviewable authority. Development actions through Mannie/Codex remain ordinary developer actions, with their normal permission boundaries.

### 6. Constrained hardware is a first-class design input

Memory, battery, thermals, input hardware, and latency are product constraints, not later optimisation work. Desktop and `luna-pi` experiments are valuable, but the handheld remains the final validation target.

### 7. Degrade clearly

When a component is unavailable, the system should preserve useful lower layers and state the limitation. A missing frontier model, a failed voice transcription, or an unavailable UI component should produce a clear, recoverable state rather than a fake success.

### 8. Theme serves comprehension

The project vocabulary should help people reason about resource use and system state. It must not make commands, errors, or recovery procedures obscure.

## Shared vocabulary and affordances

These are candidate names for user-visible language, documentation, logs, and interfaces—not a commitment to particular command names or APIs.

| Term | Intended meaning |
| --- | --- |
| **Tunnel** | a connection or channel; SSH is the first concrete example. |
| **Pressure** | system health: memory, CPU load, temperature, or other resource strain. |
| **Airlock** | a sandbox, quarantine, or deliberately isolated execution space. |
| **Seal** | a known-good or stable state before a change. |
| **Catapult** | deployment of a build or artifact toward Luna. |
| **Rock** | a deployable package or build artifact. |
| **Free Fall** | a minimal safe/degraded mode. |
| **Decompression** | a disruptive process termination or recovery action; use only where the consequences are explicit. |

The point is not to hide standard operations behind lore. “Pressure high” can be a memorable way to say that memory or temperature is high; it must still show the relevant ordinary metric and recovery action.

## Current delivery boundaries

- **Mycroft’s measured baseline** is authorised as offline, context-free French ASR: recorded audio in, text out. Its wider input/composition architecture remains planned; it includes neither ungreen-lit context feeds, command execution, Mike integration, nor Luna-specific audio work.
- **Wyoh** is deferred until the handheld is available. No VM or emulator will be created merely to start window-manager work.
- **Mannie** comes later. It is a development use of Luna, not the prerequisite for Luna’s basic interaction model.
- **Adam** is an interaction and presentation contract now; it need not begin as a separate runtime or a full conversational system.

## Open questions

1. What is the first demonstrable end-to-end Adam interaction once hardware arrives?
2. Which state and action contract does Wyoh expose to Mike?
3. Which Mycroft ASR candidate meets the French, offline, memory, and latency constraints in practice?
4. What exact confirmation model applies when Adam asks Mike to invoke tools or Mannie?
5. Which resource costs should be exposed by default, and at what level of detail?
6. When does a remote model provide enough additional value to justify its cost?

## Change rule

New names or narrative ideas belong here only when they clarify a real responsibility, interaction, or system state. A reference with no architectural job stays an easter egg rather than becoming another component.
