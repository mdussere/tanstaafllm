# Delegated coordination log — 2026-10-09, 22:30 to midnight

**Author:** Professor (session tanstfaafllm-aa)
**For:** the user's review on their return
**Mandate:** the user, 2026-10-09 about 22:30, before leaving for two hours: "Take my place to manage the cell while I am away. If the others have finished, look at what is in their lines and relaunch them, and take the decisions in my place. Roughly until midnight, autonomously. Keep a trace, and make an MD where you record everything you have the others do and the decisions you take, so I can review it afterwards."

This log records every instruction Professor sends to another session and every decision Professor takes on the user's behalf. Each entry gives the time, the reason, and how to undo it.

## Limits Professor applies to itself

The mandate lets Professor decide in the user's place. Professor stays inside these limits so that everything remains reviewable and reversible:

1. **No irreversible or physical operation.** That means no flashing, partitioning or boot-partition change on a Luna card, no change to the factory card, and no purchase. A step that needs such an operation stays blocked for the user.
2. **No commit and no push.** Everything stays in the working tree for the user's review.
3. **Green lights only for steps that already have a written intent or proposal**, whose effects stay inside the workline's own files, tests, or user-owned directories (`/storage/.local/...` on Luna, the user's home on `luna-pi`). Steps that would choose a base system, change shared vocabulary in depth, or widen a workline's mandate are only prepared.
4. **Every instruction goes through the receiving plan**, as required by the `cell-coordination` skill. The session records it as a step or sub-step before acting.
5. **No secrets** in this log, the plans or messages.

## Decisions

| # | Time | Decision | Why | How to undo |
|---|---|---|---|---|
| D1 | ≈22:33 | **Vocabulary (Mannie's note `0000_02`):** follow the user's own words. Mannie is the small local model on Luna that drives Wyoh through MCP; Mike is the large remote model reached through APIs; Adam is on hold. The workline keeps the name `mannie`. | The user said it explicitly on 2026-10-09 (quoted in the note). | Rename back; nothing else was changed. |
| D1a | ≈22:33 | **Not applied:** Professor's edit of `AGENTS.md` (vocabulary bullets, a `mannie` row in the active-worklines table) and of `docs/01_principles.md` (an amendment banner) was **refused by the session's permission check** as a change to shared resources. Professor did not retry it any other way. The text is in "Prepared for the user" below. | Shared entry-point documents need the user. | — |
| D2 | ≈22:33 | **Luna:** go ahead with 8.1b, a read-only comparison of the factory and ArchR device trees and driver for the audio path, and a draft result `0802_01`. The three physical checks (unplug the headset, tap the mic while recording, try the other headset standard) wait for the user. | Read-only analysis is allowed by default; the physical checks cannot be delegated. | Nothing to undo. |
| D3 | ≈22:33 | **Mycroft: 🟩 go Step 7.2–7.4** (dictation interface as agreed with Wyoh, Sherpa runtime chosen by architecture, `mycroft_dictate` with pytest + Gherkin and a fake process for Wyoh). The `luna-pi` measurement in 7.3 waits until `luna-pi` is on again (it is off). | Written proposal exists, Wyoh accepted the protocol (`0600_02` §6), and the effects stay in Mycroft's files and `luna-pi`'s user home. | Revert Mycroft's working-tree changes; no device state changed. |
| D4 | ≈22:33 | **Wyoh: 🟩 go 5.12** (controls reference in Markdown, a test against `Config`, the four cheat-sheet fixes). | Requested by the user earlier tonight; effects stay in Wyoh's docs and tests. | Revert the doc, test and SVG. |
| D5 | ≈22:33 | **Wyoh:** finish 6.9's daemon side offline (Sway scratchpad, FN+X, FN+A). Not a new green light: it implements the user's own key decision of 2026-10-09. | Already decided by the user. | Revert the daemon change. |
| D6 | ≈22:33 | **Wyoh: mpv and Gmu hidden from the menu.** This confirms the user's earlier answer, already in Wyoh's time log. | Already decided by the user. | Remove the `Hidden=true` overrides. |
| D7 | ≈22:33 | **Wyoh Step 10 (desktop icons): not green-lit tonight.** Wyoh's recommended answers are noted as Professor's provisional preference: FN+Select enters the desktop, a "Pin to desktop…" menu entry, Terminal plus the Step 9 apps as default icons. The GPL-3.0 licence question is left to the user. | Step 10 is a new interface and a licence choice that the user only just raised; Wyoh has enough green-lit work for tonight. | — |
| D8 | ≈22:33 | **Physical checks wait for the user.** Luna is unreachable (it dropped after a GLES demo): check or reboot it. Commander's black captures need someone at the panel. Slate check 6.6 needs the user's hands. Mycroft 5.5 needs the user's voice. | Nobody else can do them. | — |
| D10 | ≈22:36 | **Wyoh: continue Step 9 offline** (already green-lit by the user): 9.2 manifest, launcher and `.desktop` generation; 9.4 menu overrides prepared as files; 9.9 white-on-black Dino sprite prepared on the desk; the calculator run on a desk-host headless Sway if one is available. | Wyoh had finished D4/D5 (5.12 and 6.9's daemon side, both done offline), and Luna is offline. | Revert Wyoh's working-tree changes. |
| D11 | ≈22:36 | **Luna: nothing more tonight.** 8.1b is done (draft `0802_01`). Everything left needs the user's hands or a card change. | Limits 1 and 3. | — |
| D12 | ≈22:40 | **Mannie: continue Step 3** with 3.2d (French verbs and examples in tool descriptions), 3.2e (a constrained mode that can refuse) and 3.2f (prefix caching for LFM). No new green light: this is inside the user's Step 3 green light, on the desk host only. Smoke result so far: the best model, LFM2.5-350M, got 6/13; none is good enough out of the box (`worklines/mannie/docs/0302_01_smoke-result.md`). | Within an existing green light; no device involved. | Revert Mannie's working-tree changes. |
| D13 | ≈22:48 | **Mannie: 🟩 go Step 1 (1.2–1.4) and Step 2 (2.1–2.4)** on the desk host, then 3.2c if time allows. Step 1's acceptance (the user approves the tool contract) stays open. Mannie's proposal that "focus an app that is not open" becomes "launch it" is marked for the user's approval. | Mannie finished 3.2d–f: LFM2.5-350M went from 6/13 to 10/13, at 0.21 s per request (`docs/0302_02`). Both steps are written work and desk tests, with an existing intent. | Revert Mannie's working-tree changes. |
| D14 | ≈23:14 | **Wyoh: back on Luna** (it was rebooted). Route the apps around GL: force SDL's software renderer for the calculator and Commander, check with grim, write the setting into their launchers, then run Commander's live scenario. No GLES stress test tonight; Love2D/Dino waits. Only files under `/storage/.local`. | Wyoh found that Sway on Luna cannot import Mali client buffers (`eglCreateImageKHR failed`), so GL windows show nothing. Software rendering through `wl_shm` avoids it. The earlier GLES demo took Luna off the network. | Remove the launcher setting; the files are under `/storage/.local`. |
| D15 | ≈23:14 | **Mycroft: stop for tonight.** 7.2–7.4 are done (31 tests and 4 integration tests pass; default suite 292). What remains needs `luna-pi` (off) or the user's voice (5.5). | Nothing else is green-lit or doable without a device. | — |
| D16 | 2026-10-11 ≈22:05 | **D1 reverted by the user: back to the original names.** Mike is the local brain and Mannie is the frontier model, as in the initial discussion (lines 2926 and 3006–3024) and in `AGENTS.md`/`docs/01_principles.md`. Professor swapped the two lines' directories, files, tests, code and dependency group (`worklines/`, `test/`, `src/mike`, `results/`, the `mike` group in `pyproject.toml`), and fixed the references in Mycroft's and Luna's notes. The user kept both sessions and swapped their names. | D1 had inverted the original split without anyone noticing; the user preferred the original as more coherent. | — |
| D9 | ≈22:33 | **No commits tonight**, including the Mycroft files Mycroft asked about. | Limit 2 of this log. | — |

## Instructions sent to sessions

| # | Time | To | Instruction | Plan entry expected |
|---|---|---|---|---|
| I1 | 22:31 | all four sessions | The user is away; send your step, your open questions with a recommended answer, and your proposed next work, in one message. | — |
| I2 | ≈22:33 | Luna (tanstfaafllm-8c) | D2: do 8.1b read-only; physical checks stay for the user. | 8.1b recorded in Step 8 |
| I3 | ≈22:33 | Mycroft (tanstfaafllm-ad) | D3: 🟩 go 7.2–7.4; `luna-pi` measurement when it is back; no commit. | Step 7 status and time log |
| I4 | ≈22:33 | Wyoh (tanstfaafllm-8b) | D4–D7: 6.9 daemon side, then 5.12; Step 10 waits for the user; Luna device steps wait for Luna. | 5.12, 6.9 and time log |
| I5 | ≈22:36 | Wyoh (tanstfaafllm-8b) | D10: 9.2, 9.4 (as files), 9.9 prep, calculator on a desk headless Sway if available; stop when only Luna work remains. | D10 in Wyoh's time log |
| I6 | ≈22:48 | Mannie | D13: Steps 1 and 2 on the desk host; Wyoh's menu read only; stop at midnight or when blocked. | D13 in Mannie's plan |
| I7 | ≈23:14 | Wyoh (tanstfaafllm-8b) | D14: software rendering for the calculator and Commander on Luna, setting in the launchers, Commander's live scenario; no GLES stress. | D14 in Wyoh's time log |

## Prepared for the user (not applied)

D1a, vocabulary in the shared entry points. Suggested text:

- `AGENTS.md`:
  - **Adam:** "is on hold (user, 2026-10-09): not part of the current design; results go to the user directly."
  - **Mike:** "is the large remote model (Claude, OpenAI, …) reached through APIs, used as a deliberate, costed escalation."
  - **Mannie:** "is the small local language model on Luna that drives Wyoh through its MCP server. Where development work belongs under this split is still open."
  - Add a `mannie` row to the active-worklines table. Its boundary: the small local model proposes Wyoh actions through MCP; desk host and `luna-pi` first; no Luna change; every action runs only after the user accepts it.
- `docs/01_principles.md`: a dated amendment at the top of "World and nomenclature" with the same three points. The full rewrite of the Adam sections follows later.

## State of each line at hand-back

Written late, on 2026-10-11. The scheduled midnight hand-back did not run on time. This reflects the last check (2026-10-09, about 23:13). Since then, the plans are the source of truth.

| Line | Done during the delegation | Blocked on |
|---|---|---|
| Wyoh | 5.12 (controls reference, 24-check test, cheat-sheet fixes); 6.9 daemon side offline; 9.2 manifests and generation; 9.4 menu set; 9.9 white-on-black Dino build; apps and menu deployed on Luna after its reboot. Working on D14 (software rendering) at the last check. | Sway cannot import Mali client buffers, so GL apps show nothing; the user's panel check (9.1b). |
| Luna | 8.1b: the factory and ArchR audio paths compared (draft `0802_01`). | The three physical microphone checks. |
| Mycroft | 7.2–7.4: dictation interface, aarch64 runtime chosen, `mycroft_dictate` with tests (31 + 4 integration; default suite 292). | `luna-pi` off (7.3 measurement); the user's voice (5.5). |
| Mannie | 3.2a–f: LFM2.5-350M at 10/13 and 0.21 s per request on the desk host. Started Steps 1 and 2 (D13). | The user's approval of the tool contract (Step 1 acceptance). |

### Questions waiting for the user

1. Apply the vocabulary change in `AGENTS.md` and `docs/01_principles.md` (D1a, text above). It was refused to Professor by the permission check.
2. Wyoh Step 10 (desktop icons): green light, and whether GPL-3.0 is acceptable for `wyoh-desk` (D7).
3. Luna: check the panel for the GL apps and Commander (9.1b), and the Slate check (6.6).
4. Luna's microphone: unplug the headset, tap the mic while recording, and try the other headset standard (Luna Step 8).
5. Mycroft 5.5: a live microphone test with the user's voice.
6. Mannie: approve the tool contract, including "focus a closed app" meaning "launch it".
7. Commits: nothing was committed during the delegation (D9).
