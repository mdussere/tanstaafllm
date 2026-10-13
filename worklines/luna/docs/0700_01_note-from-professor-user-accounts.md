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
