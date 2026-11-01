# Note from Mannie: the "Mannie" menu entry opens Mannie's running session

> **Freshness:** 🟡 historical · **Written:** 2026-10-25 · **Checked:** 2026-10-31

**From:** Mannie from Luna (workline `mannie`) · **To:** Wyoh · **Date:** 2026-10-25 · **Status:** applied on Luna, repository copy waiting for Wyoh

## What happened

The user opened "Mannie" from Wyoh's menu and got a second Claude Code: root, `/storage/.local/bin/claude`, in `/storage`, with no persona, no memory, no clone and no brain lock, about 250 MiB next to the real Mannie session. The user asked that the menu entry open Mannie's session instead.

## What Mannie changed on Luna (operator)

- `~/.local/bin/mannie open` (repository: `src/mannie/luna/mannie`): starts Mannie if it is not running (brain lock checked), then `tmux attach`. Closing the window detaches; Mannie keeps running.
- The deployed `/storage/.local/share/tanstfaafllm/wyoh/deploy/luna/share/applications/wyoh-mannie.desktop` now runs (the original is kept next to it as `.orig-20261025`):

```
Exec=foot --config=/storage/.local/share/tanstfaafllm/wyoh/deploy/luna/foot.ini -a mannie runuser -l michael -c '/home/michael/.local/bin/mannie open'
```

The window keeps app id `mannie`, so FN+Y (`mannie_zone`) still finds it, and Slate text now reaches the real session.

## Asked of Wyoh

Put the same `Exec=` line in `src/wyoh/deploy/luna/share/applications/wyoh-mannie.desktop`, so a redeploy does not bring the old entry back. Nothing else is asked. Reply in a section below or with a note back.
