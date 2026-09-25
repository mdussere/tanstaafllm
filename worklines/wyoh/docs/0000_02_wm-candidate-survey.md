# Wyoh WM/compositor candidate survey

> **Superseded for product selection:** `0000_05_controller-first-handheld-model.md` establishes that Wyoh’s default product model is controller-first, not a general desktop. Keep this survey only as an implementation reference if a later stock bridge or native full-screen shell demonstrably requires compositor work.

> **Current order:** stock EmuELEC/EmulationStation bridge → native full-screen HIOM shell → custom compositor. Qtile/labwc are not default product candidates.

## Question answered

Which current open-source bases are credible for Wyoh, and which should be tried, forked, or rejected before Luna arrives?

## Constraints used

- Luna is only a hypothesised 1-GB-class Linux handheld until hardware characterisation.
- Early development needs a short desktop/Codex-over-SSH feedback loop.
- Wyoh must provide structured state, declared actions, and events; ordinary Wayland client internals are out of scope.
- The handheld UI is likely one-screen, controller-first, and sparse—not a conventional multi-window desktop.
- A final choice needs a safe recovery route after a display-session crash.

## Survey

| Candidate | What upstream provides today | Fit for Wyoh | Recommendation |
|---|---|---|---|
| **Qtile** | Python-configured tiling WM with X11 and Wayland backends, plus a command graph for remote inspection/control. | Best pre-hardware experiment: the command model maps to `describe`/actions and keeps iteration in Python. It is broader than a handheld needs; Wayland must be measured on Luna. | **First proof base; do not fork yet.** Use a config/adapter on X11, then retain only if target evidence justifies it. |
| **Cagebreak** | MIT wlroots tiling compositor, keyboard-first and controllable through a Unix socket; runs nested or from a TTY. | Strongest direct-fork candidate: socket control and task/workspace policy are close to agent control. Manual tiling and C need deliberate gamepad/API design. | **Production-fork shortlist.** Re-evaluate after Luna’s wlroots/KMS path is verified. |
| **dwl** | Compact C/wlroots compositor limited to 2,200 SLOC, with status information sent to an external process. | Easiest entire compositor to understand and own. Its configuration is compile-time and status is read-oriented, so Wyoh must add a versioned control socket, events, and handheld policy. | **Minimal custom-path shortlist.** Choose if ownership/minimalism outweigh faster Python iteration. |
| **Cage** | Small MIT Wayland kiosk that runs one maximised application; supports nested and TTY/KMS operation. | Excellent appliance fallback/recovery reference. It deliberately has no workspace/window-navigation model, so it does not directly provide Wyoh’s core behaviour. | **Fallback/reference, not primary fork.** Relevant if Luna becomes one native full-screen shell app. |
| **labwc** | Lightweight Openbox-inspired stacking wlroots compositor with reconfiguration and desktop-component integration. | More desktop policy than Wyoh needs; stacking/decorations are misaligned with a controller-first agent shell. | **Do not fork for v0.** Reconsider only if conventional desktop compatibility becomes necessary. |
| **river** | Separates compositor from WM policy through a stable protocol and supports hot-swapping WMs. | Architecturally excellent for a high-level Wyoh controller. However, upstream explicitly prohibits generative-AI/LLM contributions, while this project uses Codex. | **Excluded.** Respect upstream’s stated policy. |

## Decision tree

```text
Need to prove Mike ↔ Wyoh semantics before Luna?
    └─ Yes → Qtile/X11 + thin Wyoh adapter (no upstream fork)

Luna supports the Wayland/DRM path and the proof is useful?
    ├─ Smallest owned product core → evaluate dwl
    ├─ Existing socket-driven tiling policy → evaluate Cagebreak
    └─ Conventional desktop compatibility → reassess Qtile or labwc

Product becomes one native full-screen shell?
    └─ Cage becomes the relevant base
```

## Proposed ranking

1. **Qtile/X11 adapter** — fastest interface validation; no permanent fork decision.
2. **Cagebreak** — preferred future direct fork, due to its existing Unix-socket model.
3. **dwl** — alternative when minimal owned code is more valuable than runtime control primitives.
4. **Cage** — kiosk/recovery reference.
5. **labwc** — complete but misaligned.
6. **river** — attractive architecture, excluded by upstream policy.

## Evidence and current upstream references

- [Qtile repository](https://github.com/qtile/qtile) — Python configuration, X11/Wayland, remote command shell, MIT licence.
- [Qtile command graph](https://docs.qtile.org/en/stable/manual/commands/api/backend.html) — introspectable commands and Wayland window-tree operations.
- [Cagebreak repository](https://github.com/project-repo/cagebreak) — wlroots, TTY/nested operation, keyboard-first behaviour, socket control, MIT licence.
- [dwl README](https://github.com/djpohly/dwl/blob/main/README.md) — compact C goal, wlroots, TTY/nested operation, status output, compile-time configuration. Upstream says it migrated to Codeberg; verify the canonical URL before pinning.
- [Cage repository](https://github.com/cage-kiosk/cage) and [configuration documentation](https://github.com/cage-kiosk/cage/wiki/Configuration) — kiosk model and nested/TTY operation.
- [labwc repository](https://github.com/labwc/labwc) and [manual](https://labwc.github.io/labwc.1.html) — stacking scope and reconfiguration.
- [river repository](https://github.com/riverwm/river) — split design and explicit no-LLM contribution policy.

All claims were checked on 2026-09-25. Package availability and graphics compatibility still need target-device validation.
