# WayVNC, Sway, and the headless Wyoh session

## Summary

This discussion distinguishes WayVNC from the traditional Xvnc/TigerVNC model and places it beside, rather than above, the Sway session that Wyoh observes through IPC. It proposes a headless Sway output exported through WayVNC when remote development access is needed, while retaining Sway as the owner of graphical state and input routing.

## Detailed summary

**Architecture proposed in the discussion**

- Sway is described as the session owner: a Wayland compositor, tiling window manager, input router, and output manager.
- WayVNC is described as a secondary RFB/VNC endpoint attached to that Sway session; Wyoh MCP reaches Sway through Sway IPC.
- The discussion additionally proposes that a future Wyoh service might observe WayVNC's control IPC for remote-access state, without making VNC the owner of the desktop.

**Difference from the traditional VNC model**

- Xvnc/TigerVNC conventionally supplies an X server, virtual framebuffer, and VNC server together.
- In the proposed Wayland arrangement, Sway creates the headless output and WayVNC exports it. The VNC viewer therefore sees the same Sway session that Wyoh observes.
- The source discussion notes that modern TigerVNC also has `w0vncserver` for sharing an existing Wayland session; this is retained as a nuance, not a selection claim.

**Headless use and resource direction**

- A physical display is not required if Sway has a headless output for WayVNC to export.
- The discussion suggests making WayVNC optional on the eventual handheld, so it is available for development/support rather than a permanent resource cost.

**Open verification work**

- The claims in the assistant side of this conversation are source discussion, not an installed-system inventory.
- The precise service launch chain, environment variables, output dimensions, WayVNC control interface, and input behaviour require version-pinned evidence from the actual deployment.

## Verbatim

> Cleaned and translated from a French ChatGPT shared conversation exported with the repository Playwright scraper on 2026-09-30. Speaker roles are retained. Editorial section headings were added for readability; no substantive exchange or diagram was omitted. The source UI showed unlinked `GitHub +1` attribution markers after several assistant claims; because it supplied no target URLs, those markers are recorded as source attributions rather than citations.

### § 1. The Sway IPC and WayVNC question

**User**

With Wyoh, we are working on the MCP that exposes Sway's IPC. The idea is that we can connect to the Sway started by the VNC server. It uses WayVNC, which is a server I do not know. Did it appear recently? What differentiates it from TigerVNC, for example?

**Assistant**

Yes. Above all, WayVNC is much more natural than TigerVNC in our Wyoh/Sway architecture.

WayVNC is a VNC server specifically designed for wlroots-based Wayland compositors, including Sway. It does not create the desktop itself: it attaches to an existing Wayland session, captures its framebuffer, creates virtual input devices, and exposes the result through the VNC/RFB protocol. It can also work with a headless session/output without a physical screen. *(The source displayed `GitHub +1` here.)*

#### The fundamental difference from TigerVNC

Historically, the classic TigerVNC model is more like this:

```text
TigerVNC / Xvnc
      │
      ├── X server
      ├── virtual framebuffer
      └── RFB/VNC server
             │
          viewer
```

Xvnc is literally both an X server and a VNC server. It creates its own virtual screen, then X applications display inside it. *(The source displayed `TigerVNC +1` here.)*

WayVNC works more like this:

```text
             Sway
        (Wayland compositor)
             │
       wlroots protocols
             │
           WayVNC
             │
          RFB/VNC
             │
        VNC viewer
```

In other words, Sway remains the master of the graphical session. WayVNC is almost a Sway peripheral: output capture plus keyboard/mouse injection. *(The source displayed `GitHub` here.)*

That is precisely what we want for Wyoh.

#### For the MCP → Sway IPC question

We should therefore invert your phrase slightly: “the Sway started by the VNC server.” With WayVNC, conceptually, WayVNC should not own Sway. We want:

```text
systemd / Wyoh launcher
          │
          ▼
        Sway
          │
     ┌────┴──────────────┐
     │                   │
     ▼                   ▼
 sway IPC              WayVNC
 swaymsg                 │
     │                   │ RFB
     ▼                   ▼
 Wyoh MCP             dev machine
     │
     ▼
Mike / Mannie / Codex
```

This gives us an interesting ownership property: VNC becomes entirely secondary.

On the final Luna, we could even have:

```text
                    Sway
                     │
             ┌───────┼────────┐
             │       │        │
             ▼       ▼        ▼
           screen  Wyoh MCP  WayVNC
          720x720              │
                               │
                         only when
                         needed
```

So WayVNC would not need to run permanently, which fits our aim of saving R36 resources.

#### Is WayVNC recent?

Relatively, yes: it clearly belongs to the Wayland/wlroots generation, unlike VNC/TigerVNC, which comes from the X11 world. The project is still actively developed; the discussion states that the repository has more than 800 commits and that recent releases add detached mode, headless-output resizing, and work around virtual seats. *(The source displayed `GitHub +1` here.)*

There is one especially interesting detail for Wyoh that I had not considered: WayVNC has its own Unix JSON IPC. It typically creates:

```text
$XDG_RUNTIME_DIR/wayvncctl
```

and `wayvncctl` communicates with it through JSON messages. We can query/control the WayVNC instance while it is running. *(The source displayed `GitHub` here.)*

We therefore get:

```text
                    WYOH MCP
                       │
          ┌────────────┴────────────┐
          │                         │
          ▼                         ▼
   Sway IPC socket           WayVNC IPC socket
          │                         │
          ▼                         ▼
        Sway                     WayVNC
          │                         │
          └──────────┬──────────────┘
                     │
                  Wayland
```

Architecturally, this begins to look very clean: Wyoh could expose both the desktop's logical state through Sway IPC and, eventually, the state/control of visual access through WayVNC IPC.

There is an interesting nuance: TigerVNC itself now also has `w0vncserver` for sharing an existing Wayland session, so the modern comparison is no longer simply “TigerVNC equals X11.” Nevertheless, traditional Xvnc remains fundamentally a virtual X server.

For Luna/Wyoh, I would therefore keep Sway + WayVNC: their conceptual proximity around wlroots is exactly what we are seeking, and it avoids introducing a second graphical-session model merely to have remote desktop access.

### § 2. Is a compositor a window manager?

**User**

Is a compositor a window manager?

**Assistant**

For Sway, practically speaking, yes—but the terms are not exact synonyms.

Under X11, we traditionally separated:

```text
X server
   │
   ├── Window Manager     ← placement, focus, windows
   │      e.g. i3
   │
   └── Compositor         ← final rendering, transparency, effects...
          e.g. picom
```

Under Wayland, the architecture changes. The Wayland compositor takes over much of the role formerly shared between the graphical server, window manager, and compositor:

```text
Applications
     │
     │ Wayland
     ▼
┌─────────────────────┐
│        Sway         │
│                     │
│ Window management   │
│ Input               │
│ Composition         │
│ Outputs / screens   │
└──────────┬──────────┘
           ▼
       DRM / KMS
           ▼
          GPU
```

So Sway is both a Wayland compositor and a tiling window manager. We can roughly see it as “i3 reimplemented for Wayland, plus the graphical layer that Wayland requires of the compositor.”

This matters for Wyoh: when we say “Wyoh equals Sway v0,” Sway is not just the component that organises windows. It is the central component of the graphical session.

That is why WayVNC attaches to Sway rather than to a hypothetical separate “Wayland server”: under Wayland, Sway is that server/compositor.

### § 3. Operating without a physical display

**User**

We typically used Xvnc or TigerVNC when there was no physical display, which is the case with luna-pi. Can WayVNC handle that?

**Assistant**

Yes. WayVNC can operate without a physical screen, but there is an important conceptual difference from Xvnc.

With Xvnc, Xvnc itself created the virtual display:

```text
Xvnc :1
  ├── X server
  ├── virtual framebuffer 1920×1080
  └── VNC server
```

With Sway + WayVNC, Sway must have a virtual/headless output. WayVNC then exports that output:

```text
          Sway
            │
     HEADLESS output
       720 × 720
            │
      ┌─────┴─────┐
      │           │
   Sway IPC     WayVNC
                  │
                  │ RFB
                  ▼
             VNC viewer
```

So on luna-pi without a screen, this is perfectly suited to what we want.

Sway/wlroots can create headless outputs. For example, depending on version/configuration, we can use Sway/wlroots virtual-output mechanisms and then tell WayVNC which output to export.

For our Wyoh test, this is architecturally better than Xvnc: the desktop WayVNC sees is the real Sway session whose IPC socket our MCP interrogates. We do not have a graphical session created artificially by VNC alongside it.

The point to check on the current luna-pi, however, is how the Sway session was started. If the current VNC script/service starts Sway in a particular way, we need to inspect the exact command and environment variables: `WAYLAND_DISPLAY`, `SWAYSOCK`, `XDG_RUNTIME_DIR`, and possibly the wlroots backend.

If you provide the `systemctl status` of the VNC/Sway service or the script that launches it, I can reconstruct the full chain: boot → headless Sway → `SWAYSOCK` → WayVNC → Wyoh MCP.

If you want, I can:

- explain how to configure Sway with a headless output on luna-pi;
- describe precisely the VNC/Sway service-start chain on luna-pi; or
- explain how Wyoh MCP could use the Sway and WayVNC IPC interfaces at the same time.
