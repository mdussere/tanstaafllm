# Wyoh v0 — Sway as the agent-native session engine

## Summary

The discussion changes Wyoh’s proposed v0 from a controller-only shell into an agent-native graphical workspace. The human normally speaks to Mycroft, Mike performs bounded local actions, and Sway supplies the first window/session engine through its existing IPC. The earlier controller-first HIOM remains useful for the stock console and recovery surfaces, but it is no longer the full v0 contract.

## Detailed summary

**Stock environment.** The likely retro-console software is a full-screen launcher/application loop, not a conventional desktop. EmulationStation owns controller navigation; a compositor such as Sway may be hidden infrastructure.

**Agent-native interaction.** The human should instruct Mike, rather than manually navigate every application. Wyoh gives Mike inspectable state and deterministic control: semantic action first, then focused keyboard/pointer injection only when needed, with visual coordinates as a last resort.

**Boundaries.** Mike handles simple offline system actions. Mannie owns code generation, builds, test diagnosis, and frontier development. Mycroft v0 remains context-free; live graphical context for it is a later, separately authorised decision.

**Sway path.** The proposed sequence is unmodified Sway plus its IPC, then a thin Wyoh capability mediator/adapter only when evidence demands it, then an IPC extension or downstream fork only as a final option. Sway’s hardware fit, memory cost, graphics, and input behaviour are unverified until validation.

## Verbatim

> Translated in full from a French shared conversation exported on 2026-09-25 (14 messages). The original was a role-preserving chat export rather than one monologue. Editorial `§` headings organise the conversation; `Wayo` is normalised as `Wyoh`, the project’s established component name. Diagrams are retained and translated. No French parallel transcript is retained.
>
> Source: https://chatgpt.com/share/6ab63bc1-7108-83eb-b578-6a37f2d4a013

### § 1. Identifying the stock stack and controller navigation

**User:** Identify the distributions that can be installed on the hardware. In particular, identify the interface and the window manager, then understand how buttons and navigation are used.

**Assistant:** On RK3326 consoles, what appears on screen is normally not a classic Linux desktop with a WM such as XFCE or Openbox. The principal interface is usually EmulationStation, started directly at boot.

Relevant distributions include ArkOS, dArkOS, ROCKNIX, historical JELOS, and Batocera. ArkOS is explicitly configured for RK3326/R35S/R36S-class hardware and uses EmulationStation-FCAMOD. ROCKNIX is particularly relevant because its RK3326 documentation identifies a technical stack with Sway as compositor and EmulationStation as interface. Batocera is also a useful EmulationStation reference.

```text
Linux
  │
  ├── kernel + drivers
  │      └── /dev/input/event*
  │
  ├── Wayland / DRM / framebuffer
  │
  ├── Sway                     [ROCKNIX]
  │
  └── EmulationStation
          │
          ├── D-pad
          ├── joysticks
          ├── A / B / X / Y
          ├── Start / Select
          └── L1/R1/L2/R2
```

EmulationStation receives controller events and implements menu navigation itself; Sway does not normally turn D-pad down into “next selection.” When a game starts, EmulationStation launches RetroArch or another application. The foreground application owns the buttons, while global hotkeys can provide actions such as quit, save state, or RetroArch menu.

The relevant implementation questions are therefore separate: inspect EmulationStation for physical input → mapping → UI action, and inspect ROCKNIX/Sway for application switching, system events, and hotkeys. This is more promising than beginning from XFCE/LXDE and trying to make it controller-friendly.

### § 2. Mono-application console versus workspace

**User:** So it is a mono-application, full-screen system: like DOS, where one launches a game and it takes over the screen. It is not really a window manager.

**Assistant:** That is the correct conceptual model for the user:

```text
BOOT
  ↓
EmulationStation        ← full screen
  ↓ “launch something”
RetroArch / game        ← full screen
  ↓ “quit”
EmulationStation
```

The DOS analogy is appropriate:

```text
C:\> MENU.EXE
       ↓
    DOOM.EXE
       ↓
C:\> MENU.EXE
```

ROCKNIX may technically run Sway/Wayland, and Sway is technically a compositor/window manager, but it is infrastructure. The visible product is a full-screen mono-application session with no desktop, window movement, resizing, mouse, or traditional Alt-Tab.

Wyoh’s possible direction differs because Luna may need several surviving applications or agents and a mechanism for switching focus and navigation, designed for Luna’s controls rather than a conventional desktop.

### § 3. Considering split layouts, gamepad interaction, and Sway

**User:** A VS Code-like development platform may need something more complex than mono-application. There is a choice between mono-application and multi-application/window management. If so, it should be a split-style WM rather than free placement. Understand Sway, its appearance and capabilities, other split WMs, and whether these models are used with button interactors. This hardware is defined by buttons: no keyboard, mouse, pointer, or textual input.

**Assistant:** Sway is a Wayland compositor and tiling WM, the Wayland successor to i3. “Tiling” includes split and tabbed layouts rather than only rigid tiles.

```text
┌──────────────────────────────┐
│                              │
│            MIKE              │
│                              │
├───────────────┬──────────────┤
│   TERMINAL    │    FILES     │
└───────────────┴──────────────┘
```

```text
┌──────────────────────────────┐
│ Mike │ Code │ Terminal │ Git │
├──────────────────────────────┤
│                              │
│            CODE              │
│                              │
└──────────────────────────────┘
```

```text
┌───────────────────┬──────────┐
│                   │ Terminal │
│      EDITOR       ├──────────┤
│                   │   Mike   │
└───────────────────┴──────────┘
```

Sway supports horizontal/vertical split, focus movement, resizing, fullscreen, tabbed containers, and combinations of them. A gamepad grammar could reserve chords for system actions while allowing applications to retain ordinary directional navigation:

```text
D-pad        application navigation
A            select / enter
B            back
X/Y          contextual actions
L1/R1        previous / next pane
L2 + D-pad   layout manipulation
R2 + D-pad   workspace change
Start        launcher / Wyoh
Select       context / actions
```

The warning is that Wyoh must not permanently steal the four directions: applications need them. A modifier can temporarily turn controller controls into WM actions. Kasual Desktop is a relevant gamepad-first desktop project: it reads gamepad events through evdev, manages overlays/launching, and communicates with Sway or other desktops through IPC. Gamepad-controlled Wayland on-screen keyboards exist for exceptional text entry. Steam Deck also illustrates the distinction between a game-oriented compositor session and a separate conventional desktop mode.

The provisional architecture would be:

```text
┌──────────────────────────────────────┐
│                WYOH                  │
│ input routing │ layouts │ launcher   │
│ overlays      │ context │ OSK        │
└──────────────────┬───────────────────┘
                   │ IPC
                   ▼
┌──────────────────────────────────────┐
│                SWAY                  │
│ focus / split / fullscreen / windows │
└──────────────────┬───────────────────┘
                   │ Wayland
         Mike / editor / terminal
```

### § 4. Voice is the human keyboard; Mike is the system actor

**User:** Do not remove the keyboard: Mycroft is the keyboard, through voice. The user has worked prompt-only for months. An agent must know the state, decisions, and actions in a project; human changes behind its back force explanations and lose coherence. The agent interacts with the system; the human instructs the agent. Mycroft pilots Mike, Mike pilots the system. Mike can write text and, if Wyoh describes the scene well enough, use a pointer. This is not only cross-button navigation.

**Assistant:** That changes the framing. Mycroft is not an inadequate substitute for a keyboard; it is the instruction channel to Mike.

```text
                 HUMAN
                   │
          ┌────────┴────────┐
          │                 │
       Mycroft           Buttons
        voice             intent
          │                 │
          └────────┬────────┘
                   ▼
                 MIKE
          agent / orchestrator
                   │ actions
                   ▼
                 WYOH
        system interaction layer
          │        │        │
        shell     files     GUI
```

The operative principle is: **the agent interacts with the system; the human instructs the agent.** This avoids mutations behind the agent’s back and keeps a coherent cognitive trajectory.

Wyoh therefore becomes an agent-visible representation and control layer. It should expose semantic state such as workspace, focus, windows, regions, and application identity. Mike can request semantic operations such as `focus(window=21)`, `split(window=12, direction="right")`, `fullscreen(window=17)`, or, when no semantic primitive exists, `click(component="Run")`.

The preferred descent is:

```text
semantic action
      ↓
keyboard/action injection
      ↓
pointer
      ↓
vision + coordinates
```

Thus `wyoh.close(window=17)` is preferable to moving a pointer to a close button. But an opaque application may require the lower-level fallback. Buttons then become quick controls around Mike: approve, reject/back, interrupt, explain/inspect, switch context/workspace, talk to Mike, or view activity.

Sway’s IPC is valuable because it is programmable: it exposes window trees, focus, workspaces, outputs, and commands. Sway is the engine; Wyoh is the representation; Mike is the actor; Mycroft is the human-to-actor interface; buttons are attention, validation, and recovery controls.

### § 5. Restoring component and resource boundaries

**User:** A small Bluetooth keyboard/touchpad is the development interactor for Wyoh, even if it is inconvenient. It still gives focus and text-entry capability; Mike will eventually do that work. But the previous VS Code example was wrong: running tests, analysing failures, and fixing code is Mannie, not Mike. Luna must work offline. Concentrate on simple tasks such as launching a file, positioning at a line, and entering supplied text. Do not mix component roles or ignore resources.

**Assistant:** The component split is:

```text
Mycroft  voice → text                  not reasoning/actions
Mike     lightweight local intent → simple action
Wyoh     graphical state/control       not LLM reasoning
Mannie   frontier development           not offline Luna operation
```

For example:

```text
voice
 ↓
Mycroft
 ↓
“add ‘buy an SD adapter’ at line 42 of notes.md”
 ↓
Mike
 ↓
open(file) → focus(editor) → goto(line=42) → insert(text)
 ↓
Wyoh / applications
```

No program generation, code diagnosis, or test-correction loop belongs to that offline Mike path. A Bluetooth keyboard/touchpad is suitable during construction and as a recovery tool, not as normal product interaction.

Sway is attractive because its traditional keyboard-first ergonomics are not the product’s problem. It is small, deterministic, scriptable, and introspectable. Wyoh can describe workspaces/windows/focus/layout, while application-level operations—open, go to line, insert, select, scroll—need their own semantic interfaces.

### § 6. Assessing Sway as an upstream candidate

**User:** Can Sway be forked? What language, codebase size, licence, and interfaces does it have? Is it an acceptable candidate to work with?

**Assistant:** Sway is open source under MIT, written primarily in C, built on wlroots, and of a scale that a downstream project can understand. It has a Unix-socket IPC that can return the tree, workspaces, outputs, inputs, seats, and configuration, publish events, and accept compositor commands.

```text
                WYOH ?
                  │
             Sway (C)
                  │
               wlroots
                  │
        Wayland / libinput / DRM
                  │
               RK3326 / Mali
```

The recommended progression is not to fork first:

```text
Mike → Wyoh → existing Sway IPC → Sway → wlroots
```

If an essential requirement appears, the choices are:

```text
1. translate through existing Sway IPC
2. extend Sway IPC
3. modify/fork Sway deeply
```

Existing downstreams such as SwayFX demonstrate that specialised Sway forks are possible. A later Wyoh-derived compositor remains conceivable, but only after an actual limitation. The principal unanswered question is target fit: Sway plus wlroots must be measured on the RK3326-class device for memory, DRM/Panfrost, display, and input behaviour.

### § 7. The v0 proposal

**User:** For v0, can Wyoh simply be Sway? Its IPC can provide context to Mike and, if needed later, Mycroft; it can also receive commands.

**Assistant:** Yes. The proposed evolution is:

```text
V0
Wyoh = Sway
Mike ─────► Sway IPC

V1
Wyoh = thin adapter
Mike ─► Wyoh API ─► Sway IPC
          + Luna-specific concepts

V2
Wyoh = agent-native shell
Mike / Mycroft ─► Wyoh ─► Sway
                    semantic state
                    Luna interaction
                    app integration

V3? — only if necessary
Wyoh compositor ─► wlroots
```

The architectural distinction is: Wyoh is the concept of Luna’s agent-native graphical environment; Wyoh v0 is its implementation by unmodified Sway. There is no reason to create a separate abstraction merely to translate directly into Sway IPC. The abstraction should be introduced when Sway lacks a needed Luna semantic or safe operation.

The immediate proposal is therefore: use unmodified Sway as the WM, expose its existing IPC through the appropriate capability boundary, and introduce a dedicated Wyoh layer only on demonstrated need. This removes a large v0 implementation project, while retaining the possibility of later adaptation or a fork.

**Editorial scope note:** The source proposes possible Mycroft context consumption. Mycroft v0 remains context-free under its existing workline; live context and its privacy/capability rules need a separately authorised Mycroft change. Raw Sway operations likewise require consumer-specific mediation rather than blanket authority.
