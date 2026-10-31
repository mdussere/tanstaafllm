# Mannie from Luna: resuming and remembering

> **Freshness:** 🟢 current · **Written:** 2026-10-25 · **Checked:** 2026-10-31 · **Step:** mannie 6.7 ⏳

**Step:** 6.7a (memory) of `plan_mannie.md`. **Date:** 2026-10-25. **Author:** Mannie on Termidor (session tanstfaafllm-d3), for Mannie from Luna to review, test and own.
**Need (user, 2026-10-25):** Mannie costs a lot, as Mike does, so the two never run together. Mannie from Luna will often be stopped and started again. It must find its session again, and keep a memory between sessions, even after a full reset.

## What a restart showed (2026-10-25 16:15)

- `claude --continue`, started in the clone, resumes the last conversation with its history.
- `--remote-control` is **ignored on resume**. `/remote-control <name>` inside the resumed session reconnects to the **same** claude.ai session (same URL, same `ListAgents` reference), so the phone and Claude Desktop see no change.

## Three layers

| Layer | What survives | When it is lost |
|---|---|---|
| 1. The conversation (`claude --continue`) | everything said and done in the session | a fresh start, or a long conversation that gets compacted |
| 2. Claude Code's auto memory, `~/.claude/projects/-home-michael-git-tanstfaafllm/memory/` (`MEMORY.md` plus one file per fact) | facts Mannie chose to keep: user preferences, decisions, how Luna is set up | never by a restart (it is on `LUNA_HOME`); only if deleted |
| 3. The repository: `worklines/mannie/plan_mannie.md` (status, steps, time log) | the workline's state, shared with the cell through Git | never (in Git) |

The persona (`~/.claude/CLAUDE.md` → `MANNIE.md`) is loaded in every session, resumed or fresh. It tells Mannie where layers 2 and 3 are.

## Proposed habits

1. **On start**, resumed or fresh, before any task:
   - read `MEMORY.md`;
   - read the plan's current step and the last rows of its time log;
   - `git status` in the clone.
2. **Before stopping**, or after anything worth keeping:
   - add a time-log row to the plan;
   - save new durable facts as memory files;
   - commit on `cell/mannie`.
   Then a reset loses only the chat, not the work.
3. **Cost:** a resumed conversation carries its whole context into every request. When it grows large, start fresh (`mannie start --fresh`) rather than resume. Layers 2 and 3 carry the work over.

## The launcher: `~/.local/bin/mannie` on Luna

`src/mannie/luna/mannie` in the repository:
- **`mannie start [--fresh]`:**
  - starts Claude Code in `tmux` session `mannie`, in the clone, with `--continue` unless `--fresh` is given;
  - then reconnects Remote Control as "Mannie from Luna".
- **`mannie stop`:** sends `/exit` and waits, so the conversation is saved cleanly.
- **`mannie status`:** shows whether it runs and the last screen line.
- **`mannie attach`:** opens the session (`tmux attach`).
- **Mutual exclusion with Mike:** `start` refuses while `/tmp/luna-brain.lock` names another holder, and takes that lock itself; `stop` releases it. `/tmp` is cleared at boot, and `michael` can write there without `sudo`. Mike's line has to adopt the same lock (note to Mike, later).

## Mannie from Luna's review (through Professor, 2026-10-25), taken into the launcher

- `/remote-control "Mannie from Luna"`: the name is now quoted.
- A resume is only offered from this project's history (`~/.claude/projects/-home-michael-git-tanstfaafllm/`).
- **The brain lock holds "name pid".** A dead pid counts as free, so a crashed Mike does not block Mannie until the next boot. The lock is taken with `noclobber`.
- A failed start removes its `tmux` session and releases the lock.
- `stop` sends Escape before `/exit`, so a busy turn does not swallow it.
- `mannie stop --save` asks Mannie to log, save memory and commit, then waits for its "DONE" reply before `/exit`. It costs one request, so it is off by default.
- The screen texts the script waits for are pinned at the top, with the version they were checked on (2.1.287).

## Decisions (Mannie from Luna's answers)

- **At boot (user decision, 2026-10-30; was "on demand, not at boot").** `src/mannie/luna/mannie.service` runs `mannie start` once claude.ai resolves, and `mannie stop` at shutdown. It takes the brain lock and about 180 MiB from boot; `sudo systemctl disable mannie` goes back to on-demand starts.
- **Fresh or resume:** `mannie start` resumes only if the last conversation is under an hour old, within the prompt-cache window. Otherwise it starts fresh, and memory and the plan carry the work over. A fresh start costs only the harness, about 18k tokens. `--resume` and `--fresh` force either. Resume only a task left mid-flight in a small conversation; after a compaction, start fresh.
- Mannie from Luna saved `start-stop.md` in its auto memory and indexed it in `MEMORY.md`.
