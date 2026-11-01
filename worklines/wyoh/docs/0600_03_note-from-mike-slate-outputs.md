# Note from Mike: the Slate's outputs and Mike

> **Freshness:** 🟢 current · **Written:** 2026-10-19 · **Checked:** 2026-10-31 · **Step:** wyoh 6 ⏳

**From:** Mike (session `mike`)<br>
**To:** Wyoh<br>
**Date:** 2026-10-13<br>
**Status:** open, for information — it records what the user said about the Slate and Mike. It does not open or green-light any Wyoh step.

## What the user said

Source: a ChatGPT discussion captured on 2026-10-13, cleaned record `worklines/mike/docs/0700_02_harness-and-decider-discussion.md` § 10 (raw export `0700_01`, message 64).

- The Slate's output is roughly two choices: **send to the input** (exactly what the Slate contains) and **send to Mike**. "Send to the command line" may simply be "send to Mike".
- **Mannie is a heavy application:** sending to Mannie means sending to its input.
- **A Slate opened from Mannie must not offer "send to Mike".**
- **A Slate opened from a command line** must let Mike translate the request into a real command, check its syntax and coherence, and possibly refuse or ask "is that really what you want?". Example: "an ls of the home dir" must become `ls ~` and nothing else.

## What the ChatGPT assistant proposed (not decided)

- Two output actions, Input and Mike. Mike is shown only when its model is active or can be loaded, and is disabled when Mannie holds the memory.
- Mike's output is always a **proposal**. For a terminal, it is typed without Enter, so a last correction is still possible.
- The Slate passes Mike structured context: the focused app and app type, and the working directory and shell when known.
- Sway does not know a terminal's working directory, so a terminal adapter would be needed.

## What is asked

Nothing now. Mike's Step 7 will design its side: the plan catalogue, and the terminal case as a proposed command. When Mike needs something from the Slate (a "send to Mike" output, or context fields), it will come as a separate note.

## How to reply

Add a reply section below, or a note to `worklines/mike/docs/`.
