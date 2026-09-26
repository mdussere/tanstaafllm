# Testing and experimental evidence

**Status:** project-wide operating rule<br>
**Scope:** every implementation, experiment, benchmark, hardware diagnostic, and UI check in TANSTAAFLLM.

## The rule

A result is only useful if another person or agent can rerun it, inspect what happened, and understand its limits. Therefore **pytest is the default execution framework for every test and experiment**.

Put workline-owned tests under:

```text
test/<workline>/
```

Examples:

```text
test/mycroft/test_console.py
test/wyoh/test_sway_ipc.py
test/luna/test_vnc_screenshot.py
```

Do not leave durable experiments in `tmp/`, a personal shell history, an ad-hoc notebook, or an untracked one-off script. `tmp/` is for disposable local inspection only, never the authoritative experiment harness.

## Python first

Use Python tests and library/SDK interfaces by default:

- express setup, actions, assertions, fixtures, cleanup, and result capture in pytest;
- call a Python SDK or protocol library directly when one exists;
- keep deterministic seams (clock, filesystem, network transport, model adapter) injectable so ordinary tests do not need real hardware or sleeps;
- use `subprocess` only when the CLI or external executable is itself the boundary being tested, and preserve its complete output as evidence.

A Bash script or bare CLI invocation is not an experiment framework. It may be a documented operational command, but the repeatable check belongs in `test/<workline>/`.

## Deterministic tests first; live tests honestly separate

The ordinary project suite is `pytest -m "not live and not integration"`. It must remain fast and deterministic: no private recordings, reachable devices, model downloads, real APIs, or graphical session required. Do not treat bare `pytest` as the safe suite until a future configuration change enforces that selection.

Use the existing markers for exceptional cases:

- `@pytest.mark.live` — a reachable device, graphical session, network service, or other external state is required. Run only by explicit selection, for example `pytest -m live test/luna`.
- `@pytest.mark.integration` — installed pinned assets or an external runtime is required. It is also excluded from the ordinary lightweight run.

A live failure is evidence, not a reason to weaken the assertion. Preserve the logs and artifacts, state what was observed, and keep target-specific conclusions separate from desktop or `luna-pi` evidence.

## Gherkin for complex behaviour

For any test that is non-deterministic, graphical, interactive, multi-step, or difficult to understand from code alone, write a Gherkin feature beside the pytest tests:

```text
test/luna/vnc_desktop.feature
test/luna/test_vnc_screenshot.py
```

The `.feature` file is the readable behavioural contract. It states the preconditions, action, visible/observable end state, and evidence the scenario must preserve. The pytest code is its execution mechanism. A Gherkin scenario does not require a dedicated BDD runner unless a workline explicitly adopts one; the correspondence to the pytest test must be obvious by name and documentation.

Use Gherkin when it helps clarify one or more of these:

- a real CLI or service boundary;
- a graphical, VNC, desktop, audio, or controller interaction;
- asynchronous state changes and the condition that proves completion;
- a live or non-deterministic experiment;
- a safety/recovery path where “it passed” is not enough explanation.

Write `Given / When / Then` around observed states, not arbitrary delays. Wait for predicates, events, or a visible end state; do not make `sleep()` correctness logic.

## Evidence and artifacts

Every live, graphical, or diagnostic test creates a dated result directory:

```text
results/<workline>/<topic>/<timestamp>/
```

Store the complete captured output there. For graphical tests, always retain a screenshot; where supported, retain a trace or equivalent event/log record. Inspect the screenshot or artifact before declaring success. A green pytest result without visual evidence does not establish that a rendered interface is usable.

`results/` and private source data are ignored by Git unless a workline explicitly selects a small, non-sensitive fixture for version control. Never commit private recordings, credentials, downloaded model weights, or bulk generated evidence.

## Before calling an experiment complete

- Is its executable form a pytest test under `test/<workline>/`?
- Is the scenario deterministic, or clearly marked `live`/`integration`?
- Does it use Python/SDK interfaces unless a CLI boundary is the thing under test?
- Does it preserve full logs and relevant artifacts outside `tmp/`?
- For complex or graphical behaviour, is there a readable Gherkin scenario and inspected visual evidence?
- Does the associated workline record what the result proves, what it does not prove, and the command/marker used?

## Required skill for UI evidence

Before creating or running browser, graphical, desktop, VNC, or other rendered-interface tests, load the **`testing-web-frontends`** skill. Apply its evidence discipline even when the UI is not a web page: readable Gherkin/Markdown scenarios, persisted logs, screenshots inspected by an agent or person, real end-state waits rather than fixed sleeps, and clear separation of live tests from the default run.
