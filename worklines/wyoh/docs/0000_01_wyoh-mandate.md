> **Current status (2026-09-25):** The mandate now frames Wyoh as Luna’s agent-native graphical-session interface. The candidate v0 engine is unmodified Sway plus its IPC; a Wyoh adapter follows only when Sway cannot express a required safe semantic or operation. Mike remains limited to simple offline system actions, while Mannie retains development work; live Mycroft context remains a separate Mycroft-workline decision.
>
> This initial mandate remains source evidence. Its Qtile-first and controller-only assumptions are superseded by [the Sway follow-up record](0101_03_followup_discussion.md).

# Wyoh mandate — what the initial discussion establishes

## Question answered

What should the Wyoh workline own before hardware or compositor implementation begins?

## Established direction

Wyoh is the window-management layer that makes Luna’s graphical environment observable and controllable through a small structured interface, so the local system assistant (Mike) does not need screenshots or mouse coordinates.

```text
Mycroft: audio → text
Mike:    intent → declared action request
Wyoh:    session state + input/window/navigation action
Mannie:  desktop-side Codex development → SSH → target
```

Wyoh owns only state it controls: outputs, known applications/windows, focus, workspace or screen, geometry/layout, input mode, declared actions, and session events. Third-party Wayland clients remain opaque; Wyoh can report compositor metadata but cannot reliably know a client’s internal buttons.

TANSTAAFLLM-native applications may later publish an optional semantic tree to Wyoh. That is a separate protocol, not an assumption about all Wayland applications.

## Direction from the source discussion

- Initial development happens on the desktop and interacts with devices over SSH.
- `luna-pi` is the Raspberry Pi 4B reference/prototyping target; Luna is the future handheld.
- The target is expected to be constrained (discussion estimate: RK3326/Mali-G31 class, roughly 1 GB RAM), but hardware facts are unverified.
- The discussion favoured a fast Python prototype with Qtile, initially on X11; it also named dwl, Cage, Cagebreak, and labwc.
- A small local model must select bounded state-aware actions, not receive a general shell. Invalid output must be harmless and recoverable.

## Explicit non-decisions

- No final compositor or display protocol is selected.
- Luna OS, kernel, DRM/KMS, graphics, input mapping, RAM, screen geometry, and recovery path are unknown.
- No Wyoh runtime has been installed, benchmarked, forked, or run on `luna-pi` or Luna.
- The exact division between Wyoh, a launcher, and Mike remains to be ratified.

## Consequence

The immediate output is a contract and selection method. Cloning a WM, choosing a graphics stack, or promising resource use would be premature.

## Source

- [Complete initial discussion](../../general/docs/0001_01_initial_discussion.md), especially “Identifie les wm opensource…” and “Qqchose en python ?”.
