# Luna access

Only one session uses Luna (the R36 Ultra, `ssh luna`) at a time. Luna has about 1 GiB of RAM: a speech model and a graphical test running together would distort each other's measurements, or exhaust the memory. Professor decides who holds Luna. A session that wants Luna asks Professor, and does not contact the session that holds it.

**Since 2026-10-25, Mannie runs on Luna as its operator** (user). No session uses SSH on Luna without first telling Mannie on Luna what it will run and getting its agreement, and nobody reboots or resets Luna while Mannie is running there. A reboot waits until Mannie has saved its state and stopped (`skills/cell-coordination`).

**Rules for the holder:**
- Reboot Luna after each test series (`ssh luna reboot`, then wait for SSH), as the user asked, but only once Mannie on Luna has stopped.
- Install only under `/storage/.local/`. Make no change to the boot partition, the card layout, or ArchR's own files.
- To release Luna: finish the current series, reboot Luna, record the state in your plan, then tell Professor "Luna released".

## Current holder

| Since | Holder | Purpose | Release condition |
|---|---|---|---|
| 2026-10-26 | Mannie on Luna (operator) | Mannie lives on Luna (user, 2026-10-25) | — |

## Queue

| Order | Session | Purpose | Granted by |
|---|---|---|---|

## History

| Time | Event |
|---|---|
| 2026-10-11 12:35 | Professor created this file on the user's instruction: Wyoh finishes first, then Luna passes to Mycroft. |
| 2026-10-11 12:37 | Wyoh released Luna: series finished, Luna rebooted, state in `plan_wyoh.md` 9.11. |
| 2026-10-11 12:38 | Professor gave Luna to Mycroft. |
| 2026-10-11 12:42 | Mycroft released Luna: 7.3b done (`worklines/mycroft/docs/0703_01_luna-footprint-result.md`), Luna rebooted. |
| 2026-10-11 12:43 | Professor gave Luna back to Wyoh. |
| 2026-10-11 | The user allowed 2–4 threads for Mycroft and asked for the load time and the cost of Python to be examined. Mycroft queued after Wyoh's current series. |
| 2026-10-11 13:15 | Professor ran one read-only listing on Luna (GPU libraries) during Wyoh's slot, at the user's request; nothing was run on the GPU. |
| 2026-10-11 13:25 | Mycroft reports that the user gave it Luna directly for its steps 8.2–8.4 (about 25 min). Professor paused Wyoh. |
| 2026-10-11 13:42 | Mycroft released Luna (8.2–8.4 done, Luna rebooted). Professor gave Luna back to Wyoh. |
| 2026-10-11 22:34 | Wyoh idle. Professor gave Luna to Mycroft for step 9.3 (about 20 min). |
| 2026-10-11 22:40 | User decision: Mycroft works on `luna-pi` instead of Luna, so the 22:34 slot was withdrawn. Wyoh holds Luna. |
| 2026-10-13 | No session running, so the 2026-10-11 23:39 Mycroft entry is stale. The user asked the Luna session (tanstfaafllm-a0) directly to rerun the microphone tests with a USB-C headset; Luna holds Luna for 8.2e. |
| 2026-10-13 | Luna released Luna: 8.2e done (USB-C headset microphone works), Luna rebooted, SSH answering. |
| 2026-10-15 | No Professor session running. The user told Luna (tanstfaafllm-03) to take Luna over, interrupting Wyoh's Step 7 slot, for Luna Step 7.0 (user account), and allowed the changes to ArchR's account files. Wyoh gets Luna back after the release. |

## luna-pi

`luna-pi` (Raspberry Pi 4) is shared too, under the same rules: one session at a time, and ask Professor for it.

| Since | Holder | Purpose |
|---|---|---|
| — | (free) | Mycroft released it after 9.3 (results `worklines/mycroft/docs/0903_02`); not rebooted because the user's own SSH session is open on it |

Waiting for `luna-pi`: Mannie (Claude Code, the 600 MiB rehearsal if green-lit).
| 2026-10-11 22:35 | Mycroft confirmed: 9.3 stopped early, Luna rebooted and answering; only a partial Kroko `encoder.onnx` remains under `/storage/.local/opt/mycroft` (no measurement run). |
| 2026-10-11 22:46 | Wyoh released Luna (rebooted). Professor gave it to the Luna session for 8.2b. |
| 2026-10-11 22:48 | Luna session released Luna (8.2b done, rebooted). Professor gave it back to Wyoh. |
| 2026-10-11 22:56 | Wyoh released Luna (rebooted after deploying the USB-microphone choice). Professor gave Luna exclusively to the Luna session for 8.2c (user green light). |
| 2026-10-11 23:02 | Luna session released Luna: 8.2c negative (no jack-mic signal even with factory register values); registers restored, rebooted. Professor gave Luna back to Wyoh. |
| 2026-10-11 23:02 | Wyoh idle, had not resumed. Professor gave Luna to the Luna session for 8.2d. |
| 2026-10-11 23:07 | Luna session released Luna: 8.2d, the USB-C/jack adapter shows only a GenesysLogic hub (no USB audio). Rebooted. Professor gave Luna back to Wyoh. |
| 2026-10-11 23:39 | Wyoh idle. Professor gave Luna to Mycroft for 9.3 (Kroko on Luna, user request). |
| 2026-10-13 | Wyoh took the free Luna for its 12.3 at the user's request; no Professor session was running to arbitrate. |
| 2026-10-13 | Wyoh released Luna (rebooted after its 12.3 checks). Next Luna use for dictation is Mycroft's Kroko install and measurement (note `worklines/mycroft/docs/0903_03`). |
| 2026-10-13 | Wyoh took the free Luna for 9.8b (Wolfenstein controls) at the user's request. |
| 2026-10-13 | Wyoh released Luna after 9.8b (rebooted). |
| 2026-10-13 22:41 | Professor (new session tanstfaafllm-96) gave the free Luna to Mycroft for 9.8. |
| 2026-10-13 | Mycroft released Luna: 9.8 done (`worklines/mycroft/docs/0908_01`), Luna rebooted and answering. Prepared Kroko and current scripts installed under `/storage/.local`. |
| 2026-10-13 22:53 | Professor gave Luna to Wyoh (queue position 1) for Step 9 and 12.4. |
| 2026-10-13 22:55 | Mannie (session tanstfaafllm-7f) reported that the user gave it Luna directly at 22:53 for 2.4. As on 2026-10-11 13:25, the user's direct grant wins: Professor gave Luna to Mannie and put Wyoh back first in the queue. |
| 2026-10-13 | The user gave Luna directly to Wyoh ("luna est à toi") for the Mannie menu entry and larger fonts. |
| 2026-10-15 | Wyoh released Luna: Wyoh 9.12 done, Luna rebooted. |
| 2026-10-15 | Wyoh took the free Luna for Step 7 (Wi-Fi) at the user's request; no Professor session reachable. |
| 2026-10-15 | Luna released Luna: `michael` account added and checked after two reboots (key login, shadow line kept), Luna rebooted, SSH answering. Wyoh can take it back. |
| 2026-10-25 00:28 | The user gave Mannie the go for 6.1–6.5; Mannie took the free Luna. |
| 2026-10-25 09:00 | The user put Luna's card in Termidor for Mannie's Step 7 (study and preparation of an Arch Linux ARM root). Mannie remounted its four partitions read-only. |
| 2026-10-25 14:27 | The card is back in Luna; Luna boots the Arch Linux ARM root (Mannie Step 7.3). |
| 2026-10-25 17:40 | Mannie from Luna saved its state (3348544, pushed) and gave its go; Professor ran `mannie stop` over SSH as michael. Lock free, MemAvailable 654 MiB. Luna given to Mike for its first run, supervised by Professor. |
| 2026-10-25 | Mike released Luna: 4.5 done (`worklines/mike/docs/0405_01`), stopped after 3 requests at the user's word. Professor checked: no llama-server, lock free, Mannie stopped, MemAvailable 651 MiB; Mike's files kept in `~/.local/opt/mike/` (259 MB). No reboot. |
| 2026-10-25 22:20 | Mike: 4.6 run at the user's direct request (raw llama-completion, no harness: about 165 s for a 1,056-token prompt; the model is the cost). User decision: LFM2.5-350M is not usable on Luna as it is; Luna is left to Mannie, and Mike goes back to desk studies (Mike Step 8). Luna rebooted at 22:11, not by Mike. No Mike process, no lock. Luna free; Mannie's restart is the user's call. |
| 2026-10-26 | User: restart Mannie. Professor ran `mannie start` over SSH: fresh start, Remote Control "Mannie from Luna" (ref aca8f5), brain lock "mannie 13735", MemAvailable 369 MiB. |
| 2026-10-28 | Mycroft: 8.8 slot with Mannie stopped (user go). Luna was rebooted twice by the harness; no reboot after the last window, at the user's choice. Nothing was installed except `slate_session_probe.py` under `/storage/.local/share/tanstfaafllm/mycroft/`. Mannie can be restarted. |
| 2026-10-31 12:20 | Mike took Luna for 12.5 (small-talk run, about 20 min, as michael): Mannie on Luna stopped itself on the user's order, relayed by Professor; lock free, MemAvailable 550 MiB. Kroko, Sway and Wyoh services untouched, no reboot. |
| 2026-10-31 12:27 | Mike released Luna: 12.5 done (`results/mike/smalltalk-luna/20261031T112056Z/`, 6 min 22 s). No lock, no llama-server, MemAvailable 558 MiB; no reboot. Mannie's restart left to Professor. |
| 2026-10-31 12:34 | Wyoh booked Luna for 6.11 (Mike's window and FN+B: deploy, regenerate apps, one wyoh-gamepad restart, live check with screenshots; about 15 min, no reboot), agreed by Professor; waiting for Mannie to stop. |
| 2026-10-31 12:58 | Wyoh released Luna: 6.11 live check passed (`results/wyoh/luna-mike-window/20261031T115702Z/`). Deployed `wyoh_gamepad.py` (backup `.bak-20261031`) and `/storage/.local/opt/wyoh-mike/`, regenerated app entries (Calculator restored after a first run without its manifest glob), Sway reloaded, wyoh-gamepad restarted twice. Mike closed: no llama-server, no brain lock, MemAvailable 567 MiB. No reboot; Mannie can be restarted. |
| 2026-10-31 19:50 | Mike installed its Step 13 client on Luna on the user's go (Mannie on Luna offline): `mike.py` and `prestac.py` copied to `/home/michael/.local/opt/mike/` (SHA-256 checked), `smalltalk.py` now a link to `mike.py`, the old one kept as `smalltalk.py.step12`. Copy only: the user's open Mike window and its server were not touched, no service restarted, no reboot. |
| 2026-10-31 20:15 | Mike copied the 13.8/13.9 `mike.py` (journal, switch prompt) to `/home/michael/.local/opt/mike/` on the user's install go (Mannie on Luna offline; SHA-256 checked). The user's Mike window (lock `mike 2189 2207`) was left running; the new client applies at the next start. No service touched, no reboot. |
