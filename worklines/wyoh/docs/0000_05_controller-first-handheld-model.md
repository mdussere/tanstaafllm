# Wyoh — controller-first handheld interaction model

## Question answered

What must Wyoh describe and operate when Luna is a controller-operated retro handheld rather than a conventional desktop?

## What likely ships

The reported 720×720, 8-GB-eMMC, RK3326, 1-GB-LPDDR3 profile matches the R36 Ultra family, not the earlier R36S assumption. Community evidence indicates an **EmuELEC 4.7 clone** and an **EmulationStation** frontend. This is provisional until the delivered device is read without changing its firmware.

There is therefore likely **no conventional default window manager**. EmuELEC is the firmware/platform and EmulationStation is the controller-driven frontend/session shell; an emulator or port takes the foreground and returns to that shell. A compositor, X11 WM, or Wayland WM should not be inferred from that user experience.

## Evidence quality

- A model-specific [R36 Ultra manual](https://manuals.plus/ae/1005009230045763) lists RK3326, 8-GB eMMC, and a 720×720 display. An [R36 Ultra retailer listing](https://www.retrowarrior.cz/retro-handheld-prenosna-konzole-r36-ultra/) lists EmuELEC 4.7.
- Community reports describe EmuELEC 4.7 on eMMC or supplied storage; they corroborate but do not authoritatively document the firmware: [example](https://www.reddit.com/r/R36S/comments/1q2c3ff/temu_r36_ultra/) and [example](https://www.reddit.com/r/R36S/comments/1obs5yl/portmaster_on_r36_ultra/).
- [EmulationStation](https://www.emulationstation.org/faq.html) documents itself as a configurable frontend; it does not prove the exact shipped image.

The device itself remains the authority: record its actual boot target, processes, display stack, and controller mapping before changing anything.

## Core decision

Wyoh is a **controller-first handheld session controller**, not a conventional window manager. Its object model is one foreground surface plus an ordered, bounded stack of system overlays. It exposes the current selection and finite actions available from that state; it does not invent a mouse, keyboard desktop, arbitrary coordinates, or a free-floating window stack.

```text
session
├── mode: launcher | app | system-overlay | suspended | recovery
├── foreground: one surface/application
├── overlays: ordered bounded stack (menu, confirm, picker, notification)
├── focus: one selectable node
├── navigation graph: explicit up/down/left/right neighbours
└── action catalogue: actions valid now, with risk and confirmation rules
```

## Handheld Interaction Object Model (HIOM)

`snapshot()` returns a revisioned description of the active scene, not a list of arbitrary windows. A selectable node has a stable ID for its lifetime, role, label, enabled/visible state, directional neighbours, and declared actions. The snapshot is enough for Mike—or a JEV-like finite-action router—to choose a valid next interaction without inspecting pixels.

```json
{
  "schema": "wyoh.hiom.v1",
  "wyoh_revision": 417,
  "mode": "launcher",
  "foreground": {"id": "emulationstation", "kind": "frontend"},
  "overlays": [],
  "focus": "system:ports",
  "nodes": [{"id": "system:ports", "role": "entry", "label": "Ports", "nav": {"left": "system:arcade", "right": "system:settings"}}],
  "actions": [{"id": "navigate.right", "risk": "none"}, {"id": "activate", "target": "system:ports", "risk": "none"}, {"id": "open.system-menu", "risk": "none"}]
}
```

The action catalogue is finite, state-dependent, and authoritative. A model may request only an advertised action; Wyoh rejects unavailable, stale, ambiguous, or unauthorised actions with no side effect.

## Allowed interaction vocabulary

The v0 vocabulary is controller-shaped: `navigate.up|down|left|right`, `activate`, `back`, `open.system-menu`, `page.previous|next`, named shoulder/trigger actions when advertised, and `confirm|cancel` for an existing overlay. Press/repeat/hold semantics are declared per action. There is no default `pointer.move`, `pointer.click`, arbitrary `input.text`, free coordinate, focus-window, or raise-window primitive.

Text entry is not silently emulated. If a later, approved surface provides an on-screen keyboard or receives Mycroft text, it exposes a dedicated bounded semantic action with its own validation and confirmation policy.

## Relation to Mike and JEV-like routing

Wyoh does not choose intent. It makes the choice cheap: Mike receives the current action catalogue and state labels, then selects one finite action or asks the user for clarification. This fits an embeddings/classifier/JEV-like route for routine commands; a generative local model is neither required nor given a generic input device.

## Product paths after device inventory

1. **Stock-front-end bridge:** observe and operate the delivered EmuELEC/EmulationStation session only where it exposes stable, safe state and gamepad semantics.
2. **Native full-screen shell:** a minimal controller-first TANSTAAFLLM application owns HIOM; a kiosk compositor such as Cage is only display/session plumbing.
3. **Custom compositor:** consider Cagebreak or dwl only if the first two paths demonstrably cannot supply required state, recovery, or action semantics. Qtile/labwc-style desktop policy is not a default path.

## First-hardware evidence

Before installing, flashing, or launching a replacement session: identify the stock OS/frontend/version, boot path, process/display stack, controller device mapping, system overlays, application launch/return flow, SSH status, recovery route, and memory cost. This evidence decides whether Wyoh bridges the stock frontend or replaces it with a single full-screen shell.
