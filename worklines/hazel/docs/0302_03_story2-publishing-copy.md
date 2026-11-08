# Story 2 "Ask the desktop": YouTube and LinkedIn copy

> **Freshness:** 🟢 current · **Written:** 2026-11-08 · **Checked:** 2026-11-08 · **Step:** hazel 3.2d

**Files to upload** (in `~/Videos/TANSTAAFLLM/`):

- `tanstaafllm-story2-ask-the-desktop.mp4`: 90 s, 1920 × 1080, render `results/hazel/story2-ask-the-desktop/20261102T021609-full/`;
- `tanstaafllm-story2-ask-the-desktop-thumbnail.jpg`: 1280 × 720, the episode's title card, rendered by its own code.

Every claim below comes from the episode's fact table (`results/…/NOTES.md`) and Wyoh's note `0302_02`. These limits are kept: the MCP bridge is for development only, Mike answers but does not act on the desktop, and the IPC figures were measured on `luna-pi`.

## YouTube

**Title:**

```
TANSTAAFLLM · Story 2: Ask the desktop 🪟
```

**Description:**

```
How do you let an AI agent work a desktop without looking at it?

Wyoh is the desktop layer of Luna, a ~30-euro game handheld turned into a small Linux computer. Screenshots make an agent guess from pixels, and every image costs. Playwright lets an LLM drive a browser by reading the page's DOM. Wyoh does the same for a desktop: it asks the compositor.

00:00 Ask the desktop
00:06 Player 2: Wyoh
00:14 The screenshot trap: NO GO
00:20 Like Playwright, for a desktop: LET'S DO IT
00:30 One scene is not a desktop
00:38 Ask the one that exists: Sway, unmodified
00:46 Hand it to agents: MCP over SSH (development only)
00:54 Boss: the black panel
01:02 17 buttons, no keyboard
01:12 Ask the desktop
01:18 Story 2 clear

Don't look at the desktop, ask it: the compositor already knows what a screenshot can only guess.

Figures on screen carry the machine they were measured on. Screenshots stay, as evidence for humans.
Pixel-art video and NES-chip soundtrack, generated from a script and rendered on a CPU.

TANSTAAFLLM: There Ain't No Such Thing As A Free LLM.
https://github.com/mdussere/tanstaafllm
A personal engineering project by Michael Dussere.

#AI #LLM #Linux #Playwright #Wayland #PixelArt
```

## LinkedIn

```
🪟 Story 2: Ask the desktop

How do you let an AI agent work a desktop without looking at it?

Screenshots make an agent guess from pixels, and every image costs tokens. On a ~30-euro handheld, that is a bad deal.

The idea came from the browser: Playwright lets an LLM drive a page by reading its DOM. On our handheld, Luna, Wyoh does the same for the desktop. It doesn't render anything for the agent; it asks the compositor (Sway, unmodified), which already knows every window, the focus and the events. A development agent reads that window tree, acts through named actions or the same buttons a human presses, and waits for the event that confirms it.

Don't look at the desktop, ask it: the compositor already knows what a screenshot can only guess.

The video itself follows the same rule. It is generated from a 144-line script and rendered on a CPU, with an emulated NES chip for the music. Spend CPU, not tokens.

90 seconds, pixel art: https://youtu.be/<link once uploaded>
Code and notes: https://github.com/mdussere/tanstaafllm

#AI #LLM #AgenticAI #Linux #OpenSource
```
