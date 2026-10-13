# AGENTS.md

## Project orientation

TANSTAAFLLM is a resource-aware, AI-native personal-computing experiment for a constrained handheld. Read [README.md](README.md) and [docs/01_principles.md](docs/01_principles.md) before proposing architectural or naming changes.

Language: write everything in English (code, docs, plans, notes, commit messages, messages between sessions), and talk to the user in French, even when they write or dictate in English (user rule, 2026-10-11). Keep the literary vocabulary useful and secondary to clear technical behaviour.

### Shared component vocabulary

- **Adam** is the human-facing identity the user addresses. It is not a separate brain or privileged agent. **On hold** since 2026-10-09: results go to the user directly.
- **Mike** is the local reasoning and routing layer: a small local model on Luna that proposes Wyoh actions.
- **Mycroft** is Luna’s interactive input and composition capability. Its measured ASR baseline is offline, context-free audio-to-text; bounded contextualisation and the composition interface are separate, explicitly planned stages.
- **Wyoh** is the observable desktop/window-management layer: state, context, and available actions.
- **Mannie** is the frontier-model capability (Claude, Codex…): development work and Mike's costed escalation; not the universal brain.
- **Luna** is the intended handheld environment; `luna-pi` is the Raspberry Pi reference/prototyping target.

Some older records use historical names while nomenclature is consolidated. Follow the active plan and the principles document; do not silently rename components across the repository.

## Mandatory skill

The first repository-mandatory skill is **`workplan`**.

Use it whenever work involves a workline, plan, roadmap, multi-step effort, or a new tracked discovery/implementation stream. Read its `SKILL.md` before acting. It defines the canonical workline layout, plan template, green-light protocol, artifact naming, and logbook requirement.

The second mandatory skill is **`cell-coordination`** (`skills/cell-coordination/SKILL.md`). Read it before sending or answering any cross-session message, or before writing a note for another workline. In short, Professor coordinates the cell. Other sessions message only Professor and never each other; between worklines they leave notes. Every request goes into the receiving plan, and a blocked session records its state in its plan and asks the user in its own console. `worklines/agents.md` lists the running sessions.

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
| `mycroft` | `worklines/mycroft/plan_mycroft.md` | Input/composition architecture and its pre-hardware ASR baseline; no ungreen-lit context feed, command routing, target-device audio work, or implementation. |
| `wyoh` | `worklines/wyoh/plan_wyoh.md` | Desktop/WM observability and interface design; no premature compositor fork or target-hardware implementation. |
| `luna` | `worklines/luna/plan_luna.md` | `luna-pi` reference setup and physical-Luna characterisation, imaging, and boot/network bring-up on disposable cards; no Mycroft/Wyoh/Mike implementation outside a green-lit step. |
| `mike` | `worklines/mike/plan_mike.md` | Mike, the local brain: the small local model that proposes Wyoh actions through MCP. Desk host and `luna-pi` first; every action runs only after the user accepts it. |
| `mannie` | `worklines/mannie/plan_mannie.md` | Mannie, the frontier-model capability: Claude Code on Luna, measured on `luna-pi` first. No secrets in the repository and no unattended mode. |

## Tests and experiments

Read [docs/02_testing.md](docs/02_testing.md) before creating or running a test or experiment.

- **pytest is mandatory by default, run through uv** (`uv sync`, then `uv run pytest …`). Store every repeatable test and experiment in `test/<workline>/`; do not make `tmp/`, Bash snippets, one-off CLIs, or local notebooks the authoritative harness.
- Prefer Python and SDK/protocol interfaces. Use a CLI/subprocess only when the executable boundary itself is under test, and preserve its complete output.
- Keep the default suite deterministic. Mark device, network, model-asset, audio, graphical, or other external-state checks with `@pytest.mark.live` or `@pytest.mark.integration`, and run them explicitly.
- Use a neighbouring Gherkin `.feature` file as the readable behavioural contract for graphical, interactive, multi-step, non-deterministic, or otherwise complex tests. Pytest remains the execution mechanism.
- Persist logs and artifacts under `results/<workline>/<topic>/<timestamp>/`; screenshots are mandatory evidence for rendered UI tests and must be inspected before claiming success.
- Load the **`testing-web-frontends`** skill before creating or running browser, graphical, desktop, VNC, or other rendered-interface tests.

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
