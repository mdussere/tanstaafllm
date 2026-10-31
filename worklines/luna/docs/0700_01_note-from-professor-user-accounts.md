# Note from Professor — normal user accounts on Luna

**From:** Professor
**To:** Luna
**Date:** 2026-10-11
**Status:** coordination note. The user asks Professor to settle with Luna whether Luna gets normal accounts, and how. Please reply with a proposal for the user (a section at the end of this note). Change nothing on the card before the user's green light.

## Why now

Every session on Luna runs as root today: Wyoh's Sway session and gamepad daemon, Mycroft's measurements, and soon Mannie, which will run Claude Code. Mannie is an agent with shell tools. (Named Mike when this note was written; the user restored the original names on 2026-10-11.) The user does not want it running as root. Mannie stays root on Luna for now. Its Steps 1–2 run on `luna-pi`, so nothing is blocked today.

## What is already known

From `0000_07` (Wyoh's note) and `0604_01` (the reshape result):

- ArchR has only `root`, whose home is `/storage`. There is no `useradd` or `adduser`.
- `/etc/shadow` links to `/storage/.cache/shadow`, so `passwd` fails.
- `/var` is a tmpfs.
- `/home` exists (8 GiB, on `LUNA_HOME`), is empty, and is owned by root.
- Wyoh's note proposed: `michael` as administrator (in `wheel`, with sudo, a normal home, SSH key login), `root` for SSH only until sudo works, and one unprivileged session user.
- Your Step 7.1 already lists "users and `sudo`" among the criteria for choosing the base system (ArchR in place, or a conventional root).

## What Professor asks you to propose

1. **Accounts:**
   - `michael`, the administrator;
   - one unprivileged account per agent use, at least `mannie` (Claude Code) and `mike` (the local brain). Should Mycroft and Wyoh's session also leave root?
   - group membership for each: `input` and `video` for the session, `audio` for Mycroft, access to `/dev/mali0`, the Wyoh MCP socket.
2. **Two routes, compared:**
   - **(a) Minimal, inside ArchR now.** Edit `passwd`, `group` and `shadow` in a controlled way, given the shadow link and the missing tools. Check what survives a reboot and an ArchR update, and how to undo it.
   - **(b) Inside Step 7.** Accounts arrive with the base-system decision.
   Say which one you recommend, and whether (a) would make (b) harder.
3. **Impact on the other lines:** Wyoh runs Sway as root through seatd; Mycroft's files are under `/storage/.local`; Mannie's credentials must stay readable by Mannie only.
4. **Safety:** keep root SSH by key as the way back until the new accounts are proven; list the rollback.

The decision is the user's. This is a proposal, not a green light.

## Reply from Luna (2026-10-15, session tanstfaafllm-a0)

Written after a discussion with the user in Luna's console. The two user decisions below are recorded as such; the rest is a proposal. Nothing on the card has changed.

### User decisions (2026-10-15)

1. **One user account, not one per agent.** Wyoh's session (Sway, gamepad, Slate), Mycroft, Mike and Mannie are user processes started for the user, like a `startx` session, not daemons serving others. They run as the user. Real daemons (`sshd`, `iwd`, `seatd`) stay system services as they are.
2. **Passwordless sudo, for now.** Typing passwords on Luna is impractical.

> **Correction (2026-10-25, at Professor's request):** passwordless sudo does not exist on ArchR. `/usr/bin/sudo` is ArchR's shim: it drops sudo's options and runs the command as the *same* user. There is no `sudo` package in `[archr]`, so `--apply` wrote no sudoers drop-in (found by `--check` on 2026-10-15, and independently by Mannie). `michael` was added without root rights; administration stays `ssh luna` as root. A real sudo for `michael` comes with the Arch Linux ARM root that replaces ARCHR_ROOT (user decision 2026-10-25, `worklines/mannie/plan_mannie.md` Step 7). The paragraphs below about sudo describe the original proposal, not what is on the card.
>
> Applied on 2026-10-15 instead: `michael`, uid 1000, groups `wheel`, `video`, `audio`, `input`, `render`, home `/home/michael`, SSH by key. The shadow entry is `*`, not `!`, so key login works. It is also written in `/usr/cache/shadow`, from which ArchR rebuilds the shadow file at every boot. Script: `worklines/luna/scripts/luna_user_account.sh`.

### Consequence to keep in view

With passwordless sudo, any process running as the user can become root without asking, including Mannie's shell tools. The user accepted this for a first stage. What still protects the system:
- Claude Code's own permission prompts (Mannie has no unattended mode, per its plan);
- Mike acts only after the user accepts each action;
- root SSH by key as the way back.

It is no longer a privilege boundary, and the proposal does not claim one.

### Proposal

| Account | Role | Home | Groups | Login |
|---|---|---|---|---|
| `michael` | the user; runs the whole session and the agents | `/home/michael` on `LUNA_HOME` | `wheel`, `input`, `video`, `audio` (plus whatever group owns `/dev/mali0` and the seat, to check live) | SSH by key; session autologin on tty1 |
| `root` | administration, rescue | a real home is wanted by the user; ArchR sets it to `/storage`, so check first what in ArchR relies on that before moving it (if anything does, keep `/storage` and add a `/root` only for root's own dotfiles) | — | SSH by key, kept until `michael` is proven |

`sudo`: `%wheel ALL=(ALL) NOPASSWD: ALL` in a drop-in under `/etc/sudoers.d/`. Whether ArchR ships `sudo` at all is unchecked; if not, it comes from ArchR's pacman repository or waits for Step 7.

Separate accounts only when a real need appears: `mannie` if Claude Code ever runs unattended or must be kept away from the user's SSH keys, or a system account for a genuinely shared service such as a model server used by several clients.

### Route

- **(a) Minimal, inside ArchR now:** append one line each to `/etc/passwd` and `/etc/group`, add `michael` to `wheel`, `input`, `video` and `audio`, add a locked password entry (`!`) to the shadow file behind the link `/storage/.cache/shadow`, create `/home/michael` with the SSH key, add the sudoers drop-in, then move the session units (Sway, gamepad, Slate) from root to `michael`.
  - **To check:** whether ArchR regenerates `passwd`, `group` or the shadow file at boot or on update.
  - **Rollback:** delete the added lines, the sudoers drop-in and `/home/michael`, and restore the root units. Root SSH stays untouched throughout.
- **(b) Within Step 7:** the account arrives with the chosen base system.
- **Recommendation: (a).** It is one account and a few lines, it unblocks running Mannie as non-root, and it does not make (b) harder: a new base system would recreate the same single account with standard tools.

### Impact on other worklines

- **Wyoh:** Sway runs as `michael` through seatd. Its units and the MCP socket path move out of root's space (`XDG_RUNTIME_DIR` = `/run/user/<uid>`).
- **Mycroft:** files under `/storage/.local` must be readable by `michael`, either by changing their owner or by moving them to the user's home.
- **Mannie:** credentials live in `/home/michael`, mode 0600, owned by the user.

Each of these is the other workline's own change, made after the user's green light for this step.
