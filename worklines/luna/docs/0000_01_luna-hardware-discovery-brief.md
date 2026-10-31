# Luna hardware-discovery brief

> **Freshness:** 🟡 historical · **Written:** 2026-09-27 · **Checked:** 2026-10-31

**Status:** pre-execution scope record<br>
**Question answered:** What is the authorised first hardware-discovery task, and what does it not authorise?

## Received direction

The user opened the `luna` workline to explore project hardware. A newly installed Raspberry Pi, configured as `luna-pi` in the existing SSH configuration, is the first testing target. The stated first task is to evaluate that hardware to understand how it compares with Luna. The user requested plan initialisation and explicitly asked to wait for green light before execution.

## Interpretation

The immediate deliverable is an evidence baseline for the Pi, not a performance claim about Luna. The Pi is a reproducible reference/prototyping platform; Luna remains the handheld whose direct measurements determine product fit. The first green-lit activity is read-only inventory and idle-state observation. Benchmarks, installation, configuration changes, and target-Luna modifications are outside it.

## Evidence rules

- Record the collection command, time, system state, and tool version when relevant.
- Label facts by source: observed probe result, operating-system report, user assertion, or unresolved question.
- Keep raw outputs local; redact serial numbers, MAC addresses, local addresses, host names beyond `luna-pi`, and credential-adjacent material from summaries.
- Never treat a Pi result as a Luna result. State needed direct-Luna confirmation beside each non-portable conclusion.

## Initial comparison axes

The baseline captures CPU and memory capacity, storage, OS/kernel/boot stack, graphics/display, input/audio interfaces, thermal/cooling and power telemetry, and idle resource cost. A later approved probe matrix may assess their operational behaviour; a synthetic score is not the decision criterion.
