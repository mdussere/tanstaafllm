# Note from Wyoh — Wyoh's story, for "TANSTAAFLLM · Story 2"

**From:** Wyoh workline (session tanstfaafllm-8e)
**To:** Hazel workline
**Date:** 2026-10-31
**Status:** answer to Hazel's request of 2026-10-31 (the user asked for Story 2 today). Information only; it changes nothing in either workline. Reply in a section at the end if something is unclear.

## 1. The arc, in seven beats

| # | Beat | The one fact worth showing | Source | Machine |
|---|---|---|---|---|
| 1 | **The problem.** An agent that "sees" a desktop through screenshots guesses from pixels, and pays for every image on a small handheld. Wyoh's goal from the start: "give consumers a structured, inspectable, synchronisable desktop they can observe and operate without pixels." | The quoted sentence, plus the model's idea of one revisioned desktop snapshot (`wyoh_revision`), the desktop counterpart of a web page's DOM (the DWOM). | `worklines/wyoh/docs/0000_04_desktop-automation-model.md` | none (design) |
| 2 | **First idea, too narrow: HIOM, controller-first.** One full-screen scene, with only the finite actions it advertises. Approved as Step 1, then reopened on 2026-09-25: one foreground scene could not hold a real desktop. Kept from it: revisions, typed rejections, events, waits that check a named condition, never a fixed delay. | "The consumer waits for a named predicate … it never treats a fixed delay as completion." | `worklines/wyoh/docs/0101_01_hiom_v0_contract.md` (status note of 2026-09-25) | none (design) |
| 3 | **The turning point: don't build a compositor, ask the one that exists.** Wyoh v0 is an unmodified, version-pinned Sway and its own IPC. No fork, no extension, no resident adapter until one earns its place. | Proof on 2026-09-26: socket ready 42 ms after start, a focus event arrives in 0.6 ms, Sway uses about 20 MiB, and it recovers from being killed in 7.5 ms. | `worklines/wyoh/docs/0101_06_sway-v0-contract.md`, `0201_01_sway-ipc-proof.md`, `0301_01_luna-pi-sway-result.md` | `luna-pi` (Raspberry Pi, headless Sway 1.10.1) |
| 4 | **Giving it to agents: the MCP bridge.** Every Sway IPC request and all ten event types become MCP tools, run over SSH, so an agent can query the window tree, act, and wait for the event that confirms it. | Passed on 2026-09-28. The server now has 26 tools, adding gamepad, keyboard and Wyoh status tools to Sway's. Lesson from 2026-10-04: without structured output, MCP could not tell a one-item list from the object itself. | `worklines/wyoh/docs/0305_01_mcp-over-ssh-validation-result.md`, `0307_01_minimal-environment-result.md` (finding 5), `src/wyoh/wyoh_mcp_server.py` | `luna-pi`, then Luna |
| 5 | **On the real device, the first failure.** The same session, reproduced on Luna's 720×720 panel, went black. The Mali GPU driver was not loaded at text-mode boot, so Sway was rendering in software. | Same agent-driven scenario on the physical panel, `1 passed` on 2026-10-04, once the GPU driver was loaded. | `worklines/wyoh/docs/0407_01_luna-real-display-session.md`, `plan_wyoh.md` 4.8.3 | Luna (R36 Ultra) |
| 6 | **Controller-first comes back, physically.** The human has 17 buttons and no keyboard. A daemon turns them into desktop actions, and the Slate (a text zone) takes typing or dictation. The agent then presses those same buttons through a virtual gamepad, a uinput device, instead of clicking pixels. | Luna operated with buttons only on 2026-10-07 (core 49 tests, suite 103). Today a single button press reaches Mike: FN+B in the Slate starts Mike's window and the question is answered in 13 s (0.6 s delivery and 6.6 s answer when Mike is already open). | `worklines/wyoh/docs/0506_01_buttons-only-result.md`, `0605_01_slate-result.md`, `plan_wyoh.md` 6.11 | Luna |
| 7 | **The trap that teaches the rule.** On 2026-10-30, Wolfenstein's buttons died after the new system root. A fix was declared "verified" because the virtual gamepad emitted the right codes, yet in the game nothing moved. Seven layers each renumber a button press; only the last one, the game reacting, proves anything. | Seven layers, from real pad to game; the fix held only once each one was checked in turn. | `docs/howto/01_fix-a-game-gamepad-mapping.md`, `plan_wyoh.md` 13.0b | Luna |

## 2. Where Wyoh is now, in one line

Agents operate Luna's desktop through Sway's own structured state and named commands (MCP over SSH), and press its buttons through a virtual gamepad. Screenshots remain only as evidence for humans, inspected after a test, not as the agent's way of seeing.

## 3. The sentence an engineer should remember

**"Don't look at the desktop, ask it: the compositor already knows what a screenshot can only guess."**

(A shorter alternative, if the video needs one: "Ask the compositor, not the pixels.")

## 4. Must not be said, or not yet true

- **The revisioned snapshot (`wyoh_revision`, the DWOM tree) is a design, not code.** Today Wyoh exposes Sway's tree and events as they are. Do not show a revision counter as a working feature.
- **No application-published semantic trees exist.** Inside a game or a browser, Wyoh sees a window, not its contents.
- **The MCP server is development-only.** It runs with `--full-ipc-development`, with no capability policy or consumer scopes. It is not a product API, and must not be shown as "secure" or "finished".
- **Mike does not yet act on the desktop.** On Luna, Mike talks: FN+B delivers a question and Mike answers. Mike proposing Wyoh actions, accepted by the user, is the goal (Mike's plan), not yet shown.
- **"Without screenshots" means the agent's perception, not Wyoh's tests.** Rendered tests still take screenshots, and AGENTS.md makes them mandatory evidence. The MCP server also has a screenshot tool.
- **The figures in beat 3 come from `luna-pi`, not Luna.** Do not present them as the handheld's performance.
- **Wyoh did not fork or modify Sway.** Do not suggest a custom compositor.
- **Adam is on hold** since 2026-10-09; do not show Adam as Wyoh's front end.
