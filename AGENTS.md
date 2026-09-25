# AGENTS.md

## Project orientation

TANSTAAFLLM is a resource-aware, AI-native personal-computing experiment for a constrained handheld. Read [README.md](README.md) and [docs/01_principles.md](docs/01_principles.md) before proposing architectural or naming changes.

Use English by default unless the user switches language. Keep the literary vocabulary useful and secondary to clear technical behaviour.

### Shared component vocabulary

- **Adam** is the human-facing identity the user addresses. It is not a separate brain or privileged agent.
- **Mike** is the local reasoning and routing layer behind Adam.
- **Mycroft** is voice input / ASR. Its current v0 is offline, context-free audio-to-text.
- **Wyoh** is the observable desktop/window-management layer: state, context, and available actions.
- **Mannie** is the development capability; it is one use of the system, not the universal brain.
- **Luna** is the intended handheld environment; `luna-pi` is the Raspberry Pi reference/prototyping target.

Some older records use historical names while nomenclature is consolidated. Follow the active plan and the principles document; do not silently rename components across the repository.

## Mandatory skill

The only repository-mandatory skill at present is **`workplan`**.

Use it whenever work involves a workline, plan, roadmap, multi-step effort, or a new tracked discovery/implementation stream. Read its `SKILL.md` before acting. It defines the canonical workline layout, plan template, green-light protocol, artifact naming, and logbook requirement.

No other skill is mandatory solely because of this repository. Use other available skills only when the user request or task clearly requires them.

## Workline protocol

1. Identify the relevant workline under `worklines/<name>/`.
2. Read `plan_<name>.md` completely before changing that workline or beginning its work.
3. Respect the plan’s non-goals, dependencies, and acceptance criteria.
4. Planning and documentation are allowed by default. Do not implement a plan step unless the user explicitly says **`🟩 go Step N`**.
5. If scope changes materially, update the plan before continuing and add a dated entry to `docs/LOGBOOK.md`.
6. Put workline-local evidence and decisions in `worklines/<name>/docs/`; use the plan’s artifact links to keep them discoverable.

The current active worklines are:

| Workline | Read first | Boundary |
| --- | --- | --- |
| `professor` | `worklines/professor/plan_professor.md` | Project framing, decision ledger, and coordination/isolation of specialist worklines; it does not implement their subsystems. |
| `mycroft` | `worklines/mycroft/plan_mycroft.md` | Pre-hardware ASR v0 only; no TTS, context biasing, command routing, or target-device audio work. |
| `wyoh` | `worklines/wyoh/plan_wyoh.md` | Desktop/WM observability and interface design; no premature compositor fork or target-hardware implementation. |

## Documentation and source of truth

- `docs/01_principles.md` is the cross-project conceptual reference.
- `docs/LOGBOOK.md` records material plan/workline changes.
- `worklines/professor/docs/0001_01_initial_discussion.md` is the complete initial discussion transcript. Treat it as source evidence, not as verified technical documentation.
- A workline plan is the operational source of truth for that workline’s current scope and progress.

Documentation, plans, workline artifacts, and reusable scripts are intended to be committed. Do not commit secrets, `.env` files, virtual environments, caches, generated builds, downloaded model weights, or private recordings.

## Working safely

- Preserve user-authored and other-agent changes; inspect the worktree before editing overlapping files.
- If a request could reasonably belong to more than one workline, or to no clear workline, ask the user to assign its owner before researching, answering with a workline-specific conclusion, or creating/updating artifacts. Do not make a best-effort assignment; an explicitly named workline resolves the ambiguity.
- Do not broaden a workline’s authority into another workline without an explicit cross-workline decision.
- Prefer observable, reversible changes. Never use destructive Git commands to “clean up” the repository.
- Do not claim hardware performance, device compatibility, model support, or external API behaviour without appropriate evidence.
- Keep Adam’s surface honest: distinguish completed actions, proposals, blocked actions, and degraded results.
