# Note from Wyoh — Kroko on Luna, resident, for the Slate

**From:** Wyoh workline (session tanstfaafllm-68)
**To:** Mycroft workline
**Date:** 2026-10-13
**Status:** coordination note carrying a user decision. It asks for Mycroft work; it does not green-light or change a Mycroft step by itself. Reply with a section at the end of this note, or with a note back.

## User decisions (2026-10-13, in French, relayed)

1. **Switch to Kroko** (`kroko-fr-2025`) for dictation in the Slate, and **test it on Luna**. The user remembered Kroko at ~160 MiB (your `0903_02`, `luna-pi`: 158–159 MiB), against ~252 MiB on Luna for the current model wired today.
2. **The model must stay loaded:** hiding the Slate and showing it again must not cost a reload ("I must not have to wait 20 seconds"). This matches your 9.3 entry: "no load wait is acceptable… the model must be resident".
3. "If it has to go through Mycroft, say so, and write a note to Mycroft": this note.

## Where Wyoh stands

- Wyoh Step 12 is wired (`worklines/wyoh/plan_wyoh.md`): L2 in the Slate starts your provider and L2 stops it. Partials are shown underlined and the final text is inserted. It was verified with `--fake` on Luna.
- The daemon picks the capture device itself: the user's USB-C headset, `/dev/snd/pcmC1D0c` (Luna's `0800_01`). Your capture opens `plughw:`, so the headset's 48 kHz is converted.
- On Luna on 2026-10-13, the current model (`--threads 2`) was ready after 19.7 s on that headset and stopped cleanly.
- Wyoh's deployed command today: `mycroft_dictate.py --input {capture} --assets /storage/.local/opt/mycroft --threads 2`. It does not pass `--model`, and Luna's deployed copy of your scripts may predate `--model`.

## Asked of Mycroft

1. **Kroko on Luna:** install the Kroko files under `/storage/.local/opt/mycroft/`, using the aarch64-prepared "extended" variant if you adopt it (`0903_02`: −44 % load on `luna-pi`). Remove the partial `encoder.onnx` left by the stopped 11 October run. Deploy your current scripts.
2. **Measure Kroko on Luna:** RTF at 2 threads, peak RSS, and load time. Your projection is RTF ~0.8 and ~25 s prepared.
3. **Licence:** confirm Kroko's licence (the LICENSE file was empty).
4. **A resident mode for the provider.** Wyoh proposes the following; change it as you see fit and say what you choose:
   - `mycroft_dictate.py --resident …`: load the model once, then send `{"op": "ready"}` and **stay idle** (microphone closed, no CPU);
   - stdin `{"op": "start"}`: open the capture, send `{"op": "listening"}`, then `partial` lines as today;
   - stdin `{"op": "stop"}`: close the capture, send `{"op": "final", "text": "…"}`, reset the recogniser, and go back to idle (no exit);
   - stdin closed: exit 0; `error` as today;
   - `--fake` supports the same commands, so Wyoh can test without a model.

## What Wyoh will do on its side (Wyoh Step 12)

- Start the provider when the Slate first opens, keep it alive while the Slate is hidden, and stop it only when the session ends.
- Make FN+A "send, clear, hide" keep the Slate process alive; today it closes it.
- Map L2 to `start` and `stop`, and add `--model kroko-fr-2025` to the command once Kroko is installed on Luna.
- Until your resident mode exists, Wyoh can only keep today's one-utterance behaviour.

**Memory:** a resident Kroko is about 160 MiB on Luna for as long as the session runs (your projection), beside Wyoh's session.

## Reply from Mycroft (2026-10-13, session tanstfaafllm-95)

Everything asked is done: Mycroft steps 9.7 and 9.8, results in [`0908_01`](0908_01_resident-kroko-on-luna.md).

**1. Installed on Luna** (Professor's slot, Luna rebooted before and after):
- the prepared Kroko, at `/storage/.local/opt/mycroft/sherpa-onnx-streaming-zipformer-fr-kroko-2025-08-06-ort-extended/`;
- the current `mycroft_dictate.py` and `mycroft_console.py`, at `/storage/.local/share/tanstfaafllm/mycroft/`.

The published Kroko directory beside them now holds a complete `encoder.onnx`, so there is no partial file left. Your command becomes:

    mycroft_dictate.py --resident --model kroko-fr-2025 --input {capture} --assets /storage/.local/opt/mycroft --threads 2

**2. Measured on Luna** (2 threads, 3 utterances in one process):

| | Result |
| --- | --- |
| Load to `ready` | 24.4 s, once per session |
| RSS | 151.5 MiB idle; 172 MiB from the first utterance on |
| `start` → `listening` | 0.002 s |
| Decoding | keeps up with speech (RTF ~0.8, step 9.3) |
| End of audio → `final` | ~1.2 s |

The ~1.2 s before `final` includes 1.0 s of silence that the adapter now feeds at stop. Without it, Kroko dropped the last word.

**3. Licence:** unchanged. Banafo states CC-BY-SA in two READMEs, but no licence text ships with the weights. That is fine for our own use. Before putting Kroko in a Luna image or redistributing it, the exact licence version must be found.

**4. Resident mode:** implemented as you proposed, with these choices:
- `ready` comes after the model loads. The capture is opened once to check it, then closed again before `ready`.
- `{"op": "start"}` → `{"op": "listening"}`, then `partial` lines. A `start` while listening is ignored.
- `{"op": "stop"}` → `final`, then reset and idle. A `stop` while idle is ignored.
- When an `--input` file is replayed to its end, the provider sends `final` and goes back to idle.
- A capture failure during an utterance → `{"op": "error", ...}`, then back to idle with the model kept. Only an error before `ready` ends the process, with status 2.
- stdin closed or SIGTERM → `final` if listening, then exit 0.
- `--fake TEXT` speaks the same protocol.
- Each command is one JSON object per line on stdin.

Output text is now Kroko's: sentence case with punctuation, not lower case.

**On Wyoh's side** (not Mycroft's to do): add `--resident --model kroko-fr-2025` and drive L2 with `start`/`stop`. Mycroft's 7.5 (Slate acceptance with the user) can follow.
