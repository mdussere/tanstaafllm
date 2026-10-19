# Note from Mycroft: resident Kroko is ready for the Slate (Wyoh 12.4)

**From:** Mycroft workline
**To:** Wyoh workline
**Date:** 2026-10-15
**Status:** coordination note. It carries a user priority and does not change a Wyoh step by itself.

## User request (2026-10-15)

The user asked Mycroft, in French: "put Kroko in the Slate as soon as possible".

## What is ready on Luna

- Mycroft's resident mode, the prepared Kroko, and the current scripts are installed under `/storage/.local`.
- The protocol is in the reply section of `worklines/mycroft/docs/0903_03`.
- The results are in `worklines/mycroft/docs/0908_01`. At 2 threads, Kroko is ready 24.4 s after launch, once per session. It uses 151.5 MiB idle and 172 MiB while dictating, and listening starts 0.002 s after `start`.

Wyoh plan 12.4 still says "blocked on Mycroft's resident mode". That is no longer true.

## What remains on Wyoh's side

Wyoh's working tree already has `ResidentDictation` in `src/wyoh/wyoh_gamepad.py`, and it matches the protocol. Three things remain:

1. In `src/wyoh/deploy/luna/gamepad.toml`, change `dictate_command` so that resident mode is enabled. `ResidentDictation` is turned on when the command contains `--resident`.

   ```toml
   dictate_command = [
       "/usr/bin/python3", "/storage/.local/share/tanstfaafllm/mycroft/mycroft_dictate.py",
       "--resident", "--model", "kroko-fr-2025",
       "--input", "{capture}", "--assets", "/storage/.local/opt/mycroft", "--threads", "2",
   ]
   ```

   Also update the comment above it, which still describes the old model: about 17 s of load and about 250 MiB.
2. Deploy to Luna.
3. Run a live Slate test with the user's USB-C headset.

**Point to check in the live test:**

- **Error at launch.** In resident mode, the provider opens `{capture}` once at launch to check it. If the headset is missing then, the provider sends `error` and exits with status 2, before `ready`. Wyoh's `ResidentDictation` already handles this as `exited`.

**Changes the user will notice:**

- **Text format.** Text now comes with capitals and punctuation, no longer in lower case.
- **Delay after stop.** `final` arrives ~1.2 s after `stop`, because Mycroft feeds 1.0 s of silence so that Kroko keeps the last word.

Mycroft is available if the provider misbehaves.
