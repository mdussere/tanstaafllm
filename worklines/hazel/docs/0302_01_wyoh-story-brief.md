# Story 2 brief — "Ask the desktop" (Wyoh)

**Workline:** hazel · **Step:** 3.2b · **Date:** 2026-10-31 · **Status:** brief for the first version

This brief is for whoever composes the episode, a sub-agent or Hazel. It needs nothing from the cell's conversations.

## The user's idea

From the start, Wyoh wanted to interact with the desktop **natively**, without screenshots. That means taking hold of the desktop directly, acting on it, and getting feedback (user, 2026-10-31). The episode tells how Wyoh got there.

## Read first

1. `worklines/hazel/docs/0302_02_note-from-wyoh-story.md`: Wyoh's own story in seven beats, with a fact and a source for each beat, and a list of things that must not be said. **This is the authority.**
2. `docs/10_wyoh.md`: Wyoh's public page (the pieces, the costs, the status).
3. `worklines/hazel/docs/0103_01_series-template.md`: the series rules (frame, look, sound, reading, phone).
4. `worklines/hazel/video/story1-hello-luna/`: Story 1, the model to build on (`NOTES.md`, `src/`).
5. The source documents named in the note, for any detail you show.

## The episode

- **Title card:** "TANSTAAFLLM · STORY 2", stamp **"ASK THE DESKTOP"**, and a cyan subtitle in this spirit: "How an agent learned to work a desktop without looking at it."
- **Player:** WYOH, the desktop layer of Luna. Quest: let agents and humans **observe and operate the desktop without pixels**. Use the goal sentence from beat 1.
- **Stages:** one per beat of the note, so seven stages, kept short. The note's own fact goes on screen, with its machine (`luna-pi` or Luna). Suggested staging, which the composer may change:
  1. **The screenshot trap.** An agent squints at a pixel grid and guesses. Do not show any cost figure: the note gives none.
  2. **One scene is not a desktop (HIOM).** Too narrow, and reopened. Keep its lesson as a stamp: "WAIT FOR A NAMED CONDITION, NEVER A FIXED DELAY."
  3. **Ask the one that exists.** Sway, unmodified, answers over its IPC. The figures are 42 ms, 0.6 ms, ≈ 20 MiB and 7.5 ms, all labelled **luna-pi**.
  4. **Hand it to agents: the MCP bridge.** Query the window tree, then act, then wait for the event that confirms the action; show 26 tools. The structured-output lesson is a short aside.
  5. **Boss: the black panel.** On Luna's 720 × 720 panel, the session went black, because the Mali GPU driver was not loaded and Sway was rendering in software. Once the driver loads: `1 passed`.
  6. **17 buttons, no keyboard.** The daemon turns buttons into desktop actions, and the Slate takes the text. The agent presses the same buttons through a virtual gamepad. The payoff: FN+B reaches Mike, and he answers in 13 s (6.6 s when Mike is already open).
  7. **Seven layers.** A fix was "verified" because the codes were right, yet the game did not move. Count the layers from the pad to the game; only the last one, the game reacting, proves the fix.
- **Payoff:** the title stamp "ASK THE DESKTOP" comes back when the agent asks Sway and gets the tree back.
- **"STORY 2 CLEAR":** **"DON'T LOOK AT THE DESKTOP, ASK IT."**, then in VT323: "The compositor already knows what a screenshot can only guess."
- **End card:** the trailer's, unchanged.
- **Length:** at most 90 s, and the reading audit should need no holds.
- **Sound:** the same chip and helpers as Story 1. Add a short new "Wyoh" motif. The trailer theme opens the episode and returns at the payoff.

## Must not be said (from Wyoh's note)

- Do not show the revisioned snapshot (`wyoh_revision`, the DWOM tree) as working: it is a design, not code.
- Wyoh sees windows, not what is inside them: no app contents as a tree.
- Do not present the MCP server as secure, finished or a product API: it is for development only.
- Mike talks; he does not act on the desktop yet.
- "Without screenshots" means the way the agent perceives the desktop. Tests still take screenshots as evidence for humans, and the episode may say so.
- The figures in stage 3 come from `luna-pi`, not from Luna.
- Wyoh did not fork or modify Sway.
- Do not show Adam as Wyoh's front end.
- There are no screenshots or photos of real screens: everything is drawn (the user's rule). A drawn window tree, a drawn panel and a drawn pad are fine.
