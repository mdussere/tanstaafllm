---
name: commit-prep
description: Prepare small, reviewable TANSTAAFLLM Git commit scripts with explicit file manifests. Use when the user asks to prepare, review, or execute project commits.
---

# Commit Prep

Prepare commits as explicit, reviewable changesets.

## Green-light rule

Never run a commit script or any `git commit` command until the user explicitly authorises that commit. Preparing and showing scripts is allowed; executing one is not implied by preparation.

**Standing routine (user, 2026-10-31): finished work is committed, pushed and linked.** The user often follows the work from a phone and cannot see local files. So when a session finishes a piece of its own work, that standing instruction is the go: commit the session's own files with an explicit manifest, `git fetch` and rebase or merge if needed, push to `origin main`, and give the user direct GitHub links (`https://github.com/mdussere/tanstfaafllm/blob/main/<path>` for files, `https://github.com/mdussere/tanstfaafllm/commit/<sha>` for commits). It does not cover other sessions' files, work in progress, force-pushes, or anything excluded below (secrets, private records such as `worklines/professor/docs/0505_01`). A user who says "don't commit yet" overrides it.

## Workflow

1. Inspect the full worktree with `git status --porcelain=v1 --untracked-files=all` and preserve unrelated changes.
2. Group files by one coherent intent. Keep raw source archives, workline plans, and unrelated tools or skills in separate commits unless the user asks otherwise.
3. Write every commit manifest as an explicit file list. Never use a directory, glob, `git add .`, or `git add -A`.
4. Put each review-only commit script in the ignored root `tmp/` directory. Before every commit block, abort if the index already contains staged changes. Stage each manifest with one literal `git add -- <file>` command per file, validate it with `git diff --cached --check`, and show the staged name-status and stat. Preserve raw source archives byte-for-byte; if one contains pre-existing whitespace, validate the remaining staged paths explicitly and state the exception in the script.
5. Write a concise 5–10-line commit message: a short first line, a blank line, and 3–8 lines that explain the intent. One light lunar/revolutionary emoji is welcome; the message must still describe the change.
6. Before execution, let the user inspect the script and the proposed manifest. After an explicit green light, run only the named script and report its result.

## Readable script pattern

Use literal commands and a literal heredoc for each message. Avoid helper functions: repetition makes the exact staging operation easy to read and leaves room for non-`git add` operations when needed.

```bash
# 03 — Mycroft channel
git diff --cached --quiet || {
  echo "Abort: index already contains staged changes." >&2
  exit 1
}
git add -- "worklines/mycroft/docs/0000_01_mycroft_v0_handoff.md"
git add -- "worklines/mycroft/plan_mycroft.md"
git diff --cached --check
git diff --cached --stat
git diff --cached --name-status
git commit -F - <<'MESSAGE'
🎙️ open the Mycroft channel

Define the pre-hardware French ASR v0 boundary.
Record candidate models, evaluation gates, and handoff.
Keep context, commands, and output speech deferred.
MESSAGE
```

Keep the complete set of proposed commits together in one temporary script when that makes review easier.

## Project conventions

- Plans, documentation, workline artifacts, reusable scripts, and skills are normally versioned. Temporary commit-review scripts under root `tmp/` are intentionally not versioned.
- Do not include secrets, `.env` files, virtual environments, caches, generated builds, downloaded model weights, or private recordings.
- If a commit materially changes a workline plan, include the corresponding `docs/LOGBOOK.md` update or make the separation explicit.
- Follow `AGENTS.md`; `workplan` remains the only repository-mandatory skill.

## Message style

Use 5–10-line messages. The following are examples of opening lines; follow each with a short body that explains the change.

- `📜 seed Luna's charter`
- `📡 archive first transmissions`
- `🎙️ open Mycroft's channel`
- `🪟 map Wyoh's horizon`
- `🔒 seal the commit protocol`
