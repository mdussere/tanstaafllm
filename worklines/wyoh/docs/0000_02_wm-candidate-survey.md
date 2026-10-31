> **Current status (2026-09-25):** Sway is the v0 candidate: first use its unmodified IPC, then introduce a thin Wyoh adapter/capability mediator only on demonstrated need; an IPC extension or fork is a later fallback. Validate Sway on `luna-pi` and Luna before adoption.
>
> **Why Sway has an advantage:** ROCKNIX documents a `Sway + EmulationStation` session, so Sway is already proven as technical plumbing in a comparable handheld distribution family. This is selection evidence, not proof of Luna's preinstalled image; the delivered distribution and compositor remain Step 4 inventory facts.
>
> The Qtile-first ranking and stock-frontend/native-shell/custom-compositor product order below are superseded for the agent-native workspace path; the comparative evidence remains useful.

# Wyoh WM/compositor candidate survey

> **Freshness:** 🟡 historical · **Written:** 2026-09-25 · **Checked:** 2026-10-31

> **Current product-selection record:** Sway is the proposed v0 session engine. The controller-first document remains evidence about the delivered stock console and recovery surfaces, not the full Wyoh workspace contract.

> **Current order:** unmodified Sway IPC → thin Wyoh adapter/capability mediator → Sway IPC extension or downstream fork only on demonstrated need. Qtile/labwc are comparative references, not v0 candidates.

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
| **Sway** | MIT-licensed C Wayland compositor on wlroots; JSON IPC exposes tree, workspaces, outputs, inputs, seats, events, and commands. ROCKNIX documents it beneath an EmulationStation session. | Supplies the v0 window/focus/workspace/layout engine and observable state. A mediator still limits which operations Mike or a later consumer may request. Its documented use in a comparable handheld distribution family is a practical selection advantage. | **Primary v0 candidate.** Validate unmodified Sway and Luna's actual shipped stack before adding Wyoh code or considering a fork. |
| **Qtile** | Python-configured tiling WM with X11 and Wayland backends, plus a command graph for remote inspection/control. | Best pre-hardware experiment: the command model maps to `describe`/actions and keeps iteration in Python. It is broader than a handheld needs; Wayland must be measured on Luna. | **First proof base; do not fork yet.** Use a config/adapter on X11, then retain only if target evidence justifies it. |
| **Cagebreak** | MIT wlroots tiling compositor, keyboard-first and controllable through a Unix socket; runs nested or from a TTY. | Strongest direct-fork candidate: socket control and task/workspace policy are close to agent control. Manual tiling and C need deliberate gamepad/API design. | **Production-fork shortlist.** Re-evaluate after Luna’s wlroots/KMS path is verified. |
| **dwl** | Compact C/wlroots compositor limited to 2,200 SLOC, with status information sent to an external process. | Easiest entire compositor to understand and own. Its configuration is compile-time and status is read-oriented, so Wyoh must add a versioned control socket, events, and handheld policy. | **Minimal custom-path shortlist.** Choose if ownership/minimalism outweigh faster Python iteration. |
| **Cage** | Small MIT Wayland kiosk that runs one maximised application; supports nested and TTY/KMS operation. | Excellent appliance fallback/recovery reference. It deliberately has no workspace/window-navigation model, so it does not directly provide Wyoh’s core behaviour. | **Fallback/reference, not primary fork.** Relevant if Luna becomes one native full-screen shell app. |
| **labwc** | Lightweight Openbox-inspired stacking wlroots compositor with reconfiguration and desktop-component integration. | More desktop policy than Wyoh needs; stacking/decorations are misaligned with a controller-first agent shell. | **Do not fork for v0.** Reconsider only if conventional desktop compatibility becomes necessary. |
| **river** | Separates compositor from WM policy through a stable protocol and supports hot-swapping WMs. | Architecturally excellent for a high-level Wyoh controller. However, upstream explicitly prohibits generative-AI/LLM contributions, while this project uses Codex. | **Excluded.** Respect upstream’s stated policy. |

## Additional verified IPC-capable candidates

These candidates have a documented process-external control/observation interface comparable in shape to Sway’s IPC. “IPC-capable” alone is not a recommendation: Luna fit still depends on memory, DRM/KMS, input, recovery, and the ability to constrain consumer authority.

| Candidate | Documented IPC-like feature | Wyoh relevance | Recommendation |
|---|---|---|---|
| **Hyprland** | Two Unix sockets: a request/control socket for `hyprctl`-style commands and an event socket that streams live events. | Strong external control/event model, but its visual-effects/desktop orientation makes it a poor unmeasured fit for a 1-GB handheld. | **Reference only.** Do not substitute for Sway without target evidence. |
| **niri** | `$NIRI_SOCKET` accepts direct JSON requests; its event stream provides initial state followed by updates. | Particularly interesting semantic/event model, including an explicit atomicity caveat. IPC and compositor evolve together, so the exact version must be pinned. | **Wayland comparison candidate.** Evaluate only if Sway’s layout model proves unsuitable. |
| **Wayfire** | The optional `ipc` plugin supplies a socket framework; plugins such as `ipc-rules`, `wm-actions`, and `grid` provide commands/events. | Extensible without a compositor fork, but the useful interface depends on enabled plugins and plugin API/version compatibility. | **Plugin-architecture reference.** Not a minimal v0 default. |
| **i3** | Unix-socket IPC supports commands, tree/workspace/output queries, JSON replies, and event subscriptions. | Sway deliberately shares the i3 IPC framing, making i3 useful for protocol tooling and desktop proof work. | **X11-only reference.** Not a Luna production candidate. |
| **bspwm** | `bspc` communicates over a Unix socket and supports control, query, and event subscription. | A compact X11 example of an external WM-control boundary. It lacks Wayland/Luna-path relevance. | **X11-only reference.** Do not make it the v0 base. |

Primary references: [Hyprland IPC](https://wiki.hypr.land/IPC/), [niri IPC](https://github.com/niri-wm/niri/blob/main/docs/wiki/IPC.md), [Wayfire IPC](https://wayfire.org/2023/10/07/Wayfire-0-8.html), [i3 IPC](https://i3wm.org/docs/ipc.html), and [bspc manual](https://manpages.debian.org/experimental/bspwm/bspc.1.en.html).

## Decision tree

```text
Need an agent-native v0 workspace engine?
    └─ Yes → unmodified Sway + existing IPC (no Wyoh adapter or fork by default)

Does required product semantics or safe consumer authority exceed direct Sway IPC?
    └─ Yes → add the smallest capability mediator/Wyoh adapter

Does target evidence expose an irreducible Sway limitation?
    ├─ Yes → evaluate a Sway extension/downstream fork or another candidate
    └─ No → retain unmodified Sway

What does Luna actually ship?
    └─ Inventory its distribution, compositor, and stock recovery path before replacement or adoption

```

## Proposed ranking

1. **Sway + existing IPC** — proposed v0 engine; validate first, with no fork.
2. **Thin Wyoh adapter** — introduce only to mediate capability or add a demonstrated Luna semantic.
3. **Cagebreak** — preferred future direct fork, due to its existing Unix-socket model.
4. **dwl** — alternative when minimal owned code is more valuable than runtime control primitives.
5. **Cage** — kiosk/recovery reference.
6. **labwc** — complete but misaligned.
7. **river** — attractive architecture, excluded by upstream policy.

## Evidence and current upstream references

- [Sway repository](https://github.com/swaywm/sway) and [IPC manual](https://github.com/swaywm/sway/blob/master/sway-ipc.7.scd) — proposed v0 engine and protocol reference; pin an exact version only in a green-lit validation step.
- [Qtile repository](https://github.com/qtile/qtile) — Python configuration, X11/Wayland, remote command shell, MIT licence.
- [Qtile command graph](https://docs.qtile.org/en/stable/manual/commands/api/backend.html) — introspectable commands and Wayland window-tree operations.
- [Cagebreak repository](https://github.com/project-repo/cagebreak) — wlroots, TTY/nested operation, keyboard-first behaviour, socket control, MIT licence.
- [dwl README](https://github.com/djpohly/dwl/blob/main/README.md) — compact C goal, wlroots, TTY/nested operation, status output, compile-time configuration. Upstream says it migrated to Codeberg; verify the canonical URL before pinning.
- [Cage repository](https://github.com/cage-kiosk/cage) and [configuration documentation](https://github.com/cage-kiosk/cage/wiki/Configuration) — kiosk model and nested/TTY operation.
- [labwc repository](https://github.com/labwc/labwc) and [manual](https://labwc.github.io/labwc.1.html) — stacking scope and reconfiguration.
- [river repository](https://github.com/riverwm/river) — split design and explicit no-LLM contribution policy.

All claims were checked on 2026-09-25. Package availability and graphics compatibility still need target-device validation.
