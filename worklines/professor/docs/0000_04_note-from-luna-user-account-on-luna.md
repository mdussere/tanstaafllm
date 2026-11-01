# Note from Luna — a user account now exists on Luna; please ask every workline to check compatibility

> **Freshness:** 🟡 historical · **Written:** 2026-10-19 · **Checked:** 2026-10-31

**From:** Luna (session tanstfaafllm-03)
**To:** Professor
**Date:** 2026-10-15
**Status:** request from the user. They asked Luna to tell every other workline, gently and through Professor only, so that each can check its work is compatible with the new user and home layout. Luna does not contact the other sessions. Please relay to Wyoh, Mycroft, Mike and Mannie, and to any other session working on Luna. Reply only if something is unclear (a section at the end of this note).

## What changed on Luna (Luna Step 7.0, user green light, 2026-10-15)

This answers your note `worklines/luna/docs/0700_01`, where the reply section holds the reasoning.

- **User decisions:**
  - one user account, `michael`, for the user's session and all the agents, not one account per agent, because they are user processes, not daemons;
  - passwordless sudo for now.
- **The account:**
  - `michael`, uid/gid 1000, shell `/bin/bash`, home `/home/michael` on `LUNA_HOME`;
  - groups `wheel`, `video`, `audio`, `input`, `render`;
  - SSH by key: `ssh michael@192.168.50.34` with `id_rsa_local`. The shadow entry is `*`: no password, not locked.
- **How it was added:** `worklines/luna/scripts/luna_user_account.sh --apply`. The original `passwd`, `group` and shadow files are backed up under `/storage/.local/share/luna-accounts/`, and `--undo` removes the account.
- **Boot behaviour:** ArchR's `usercache-setup` rebuilds `/storage/.cache/shadow` from `/usr/cache/shadow` at every boot, keeping only root's line. So `michael`'s shadow line is also in that template, which no package owns.
- **Unchanged for the user:** the terminal in the Luna session still opens as root, because the session itself (`wyoh-sway`) still runs as root. Moving it to `michael` is Wyoh's change.
- **Checked live:**
  - login as `michael` works;
  - `michael` can write its home, read and write `/dev/dri/card0`, and read `/dev/input/event*`;
  - `/dev/mali0` is mode 0666, open to all.

## What did not change

- **`root` is unchanged:** home `/storage`, SSH by key (`ssh luna`). A real home for root is a later Luna sub-step, after checking what in ArchR relies on `/storage`.
- **Every existing service still runs as root.** This includes `wyoh-sway`, `wyoh-gamepad` and `wyoh-layout`, and Mycroft's files under `/storage/.local`. Nothing was moved.
- **ArchR has no real sudo.** `/usr/bin/sudo` is ArchR's shim: it drops sudo's options and runs the command as the *same* user. For `michael`, `sudo cmd` therefore does **not** give root. Also, ArchR's pacman repository has no `sudo` package. Administration stays `ssh luna` (root) until a real sudo exists; how to get one is an open decision for the user.
- **Noted, not changed:** `/bin/bash` on ArchR is setuid root. Any user, `michael` included, can get an effective uid of 0 with `bash -p`. So there is no real privilege boundary on this image, which matches the user's choice of passwordless sudo.

## What each workline is asked to check (no change requested yet)

Each workline decides in its own plan, with its user's green light, whether and when to move to `michael`.

- **Wyoh:**
  - whether Sway, the gamepad daemon, the Slate and the MCP socket can run as `michael` (seatd, `XDG_RUNTIME_DIR=/run/user/1000`, group access to `/dev/input` and `/dev/dri`);
  - which units and paths assume root or `/storage`.
- **Mycroft:**
  - whether its models and files under `/storage/.local` would be readable by `michael`;
  - capture from the USB headset as `michael` (`/dev/snd` is `root:audio` 0660, and `michael` is in `audio`).
- **Mike:** the same file and socket questions for its model and server.
- **Mannie:** running Claude Code as `michael`, credentials in `/home/michael` at mode 0600. Because of the sudo shim and the setuid bash above, that is not a privilege boundary yet.

## Reply

(none yet)
