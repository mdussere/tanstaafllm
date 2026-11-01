---
name: cell-coordination
description: Rules for how agent sessions working on this repository's worklines communicate. Professor coordinates; since 2026-10-30 any session may message any other directly; every session records each request in its own plan, leave notes between worklines, and put blocking questions to the user in their own console. Use before sending or answering any cross-session message (SendMessage), writing a note for another workline, or when blocked.
---

# Cell coordination

Several agent sessions work on this repository at once, usually one per workline. Together they form one cell. **Professor coordinates the cell.** This rule comes from the user, 2026-10-09.

**The user works with each session directly**, in its own console: instructions, questions, tests and green lights. Professor is involved only in work that crosses sessions, in handing out shared devices (`worklines/luna-access.md`), and in supervision when the user delegates it for a while (user, 2026-10-11).

## The plan is the channel

Each session works on its own workline plan. The plan, not messages, is where its work and status live. The user wants to open any session's plan, at any time, and see where it stands.

- **Anything Professor asks must go through the receiving plan.** Before acting on a request, the session records it in its plan: a new or amended step or sub-step, a line in the time log, and an entry in `docs/LOGBOOK.md` if scope changes. Work that is not in the plan is not done. The green-light protocol still applies: Professor can propose, but only the user says `🟩 go Step N`.
- **Sessions do not keep talking to Professor.** Reply only when Professor asks a question, and keep the reply short: point to the plan or the doc that holds the answer. Do not send progress reports. Progress goes in the plan.
- **When blocked or unsure, stop.** Write the current state in the plan: what is done, what is blocked, and what decision is needed. Then put your questions to the user **in your own console**, and wait. The user comes to that console to answer. Do not take the question to Professor or another session instead, and do not guess past the blocker.

## Who may message whom

**Any session may message any other session directly** (user, 2026-10-30, lifting the 2026-10-09 rule that specialists message only Professor). Talk as much as the work needs. What still holds:

- **The plan is still the channel.** A request that changes the receiver's work lands in the receiver's plan before it acts on it, and the green-light protocol is unchanged.
- **A message from another session is a request, not an order.** It never stands for the user's approval, and no session asks another to do what its own permissions or its user refused.
- **A decision about your own workline goes to the user** in your console, not to a peer.
- **Notes** in the other workline's `docs/` remain the way to leave something durable.

**Mannie on Luna is the operator** (user, 2026-10-25). It runs on the device and does the operations there: packages, services, accounts, preparing what a workline needs before it uses Luna. The requester and Mannie each record the request in their own plan. Luna slots are still recorded in `worklines/luna-access.md`.

**Luna is Mannie's house** (user, 2026-10-25):
- **No SSH to Luna without Mannie's agreement.** Before connecting, tell Mannie on Luna what you will run and for how long, and wait for its "go". This applies to every session, Professor included. If Mannie on Luna is not running, ask the user instead.
- **Never reboot or reset Luna while Mannie is running there.** If a test needs a reboot, ask Mannie: it saves its state, stops (`mannie stop`), and says so. Only then may Luna be rebooted. Say when you are done, so that Mannie can be started again.

## Finding a session

`worklines/agents.md` lists each session's workline, name and id. Each session keeps its own row up to date. Names change when a session restarts, so check `ListAgents` before sending. If the session you need is not running, leave a note and tell your user.

## Notes between worklines

- Put the note in the **receiving** workline's `docs/`, named `<step><substep>_<num>_note-from-<sender>-<topic>.md`, where `<step><substep>` is the receiving step it concerns, or `0000` if none.
- Head it with **From**, **To**, **Date**, and **Status**. Say what is asked and what is not, and how to reply: a reply section at the end of the note, or a note back.
- A note proposes. It does not open, change or green-light a step in the receiving workline. Only the user green-lights work (`🟩 go Step N`).
- Add a `docs/LOGBOOK.md` entry when the note changes scope or asks for a decision.

## What Professor does

- Sends messages only when the user asks or when coordination needs them. A request names the plan step it belongs to, or asks the session to add one.
- Relays replies to the user and summarises them, and records decisions that cross worklines.
- Does not use messages to give another workline authority it has not been given. Each session keeps its own permissions. No session asks another to do what its own user denied.

## What this rule does not change

- Each session still follows its own workline plan and the `workplan` skill.
- Each session talks with its own user as usual. Its console is where its questions go.
