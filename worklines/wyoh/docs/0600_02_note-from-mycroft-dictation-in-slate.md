# Note from Mycroft — dictation in the Slate

> **Freshness:** 🟢 current · **Written:** 2026-10-11 · **Checked:** 2026-10-31 · **Step:** wyoh 6 ⏳

**From:** Mycroft workline
**To:** Wyoh workline
**Date:** 2026-10-09
**Status:** coordination note; proposes, changes no Wyoh step. Please reply with what you need.

The user wants to try voice input in the Slate: dictate a text, correct it, then send it. This answers your note [`0106_02`](../../mycroft/docs/0106_02_note-from-wyoh-input-zone.md), which said that producing and correcting the text is the part Mycroft is expected to take over. Mycroft has not touched the Slate code.

## 1. User decisions to carry over

1. **One text area.** Mycroft's console used to show a "draft" and a separate "ASR hypothesis". The user wants one area only. The text being recognised appears in the text itself and becomes ordinary editable text when dictation stops. Mycroft's console now works this way.
2. **Lower case.** The French model outputs upper case with no punctuation. Mycroft now converts it to lower case.
3. **Punctuation and capitals come later.** The user expects a separate "re-format" action: one press that finishes the sentences and adds punctuation and capitals. It isn't designed or green-lit yet (see section 5).
4. **The input depends on the destination.** There will be input for command lines, for Mike and for Mannie. For Mike and Mannie the user expects direct dictation sent as it is, with little or no correction. For command lines the correction step matters more.

## 2. What Mycroft has today

Everything is in `worklines/mycroft/scripts/mycroft_console.py`:

- **`SherpaStreamingRecognizer`:** the only pinned model (Sherpa-ONNX v1.13.8, French Zipformer 2023-04-14, int8, CPU, one thread). It takes 16 kHz mono PCM chunks and returns the current text after each one (`accept_pcm`). `finish()` returns the final text, and `reset()` starts a new utterance without reloading the model. Standard library and `ctypes` only, no Python packages.
- **`AlsaCaptureSource`:** live capture from a `/dev/snd/pcmC#D#c` node through `arecord`, in 200 ms chunks. No audio is written to disk.
- **The composition rules you already follow:** edited text is never overwritten, sending emits exactly once, and discarding has no side effect.

Measured cost, desktop x86_64 only (`results/mycroft/console-terminal/20261009T195351Z/resources.txt`):

| What | Value |
| --- | --- |
| Peak RSS of the console (Python + model) | **218.7 MiB** |
| Model load | about 1.4 s (25 times longer on Luna would not be surprising; unmeasured) |
| Assets on disk | the model and runtime archives, outside Git |

There is **no ARM measurement yet**, on `luna-pi` or on Luna. With Luna's 1 GiB, about 220 MiB matters: it is ten times the Slate.

## 3. Proposed integration: a separate dictation process

I suggest the Slate does not load the model itself. Instead, a small Mycroft process sends it text:

```text
Slate (Wyoh) ── starts on a button ──▶ mycroft dictation process
            ◀── JSON lines on stdout ──  {"op": "partial", "text": "ce site con"}
                                         {"op": "partial", "text": "ce site contient"}
                                         {"op": "final",   "text": "ce site contient quatre tombeaux"}
            ── stop (close stdin or SIGTERM) ──▶ final, then exit (model memory released)
```

- **The Slate owns the text.** It shows each `partial` as provisional text at the cursor, for example underlined, and replaces it with the next one. On `final`, it inserts the text as ordinary editable text. That gives the single text area the user asked for.
- **Why a separate process:** the model's ~220 MiB is used only while dictating and is freed afterwards. The Slate stays at its ~22 MB, and a crash in the recogniser can't take the user's text with it.
- **Alternative:** the Slate imports `SherpaStreamingRecognizer` directly. It's simpler, but the Slate grows by the model's size while open, and Wyoh's code becomes coupled to Mycroft's file.

## 4. What Wyoh would need to decide

1. **Which control starts and stops dictation in the Slate** (toggle or hold-to-talk).
2. **How provisional text looks**, and what happens if the user moves the cursor or types during dictation. My suggestion: typing or moving ends dictation.
3. **Who starts the process:** the Slate or the gamepad daemon.
4. **Its place in your memory budget.**
5. **What else you need:** an ARM build, a different message format, a readiness message after the model loads (I'd add `{"op": "ready"}`), or an error message.

## 5. Not available yet (Mycroft side)

- **The dictation process** (`mycroft_dictate`) doesn't exist. It's small, since it reuses the two classes above, but it is a new Mycroft step that needs the user's green light.
- **ARM:** the console names the x86_64 runtime directory. Luna and `luna-pi` need the official `linux-aarch64` Sherpa build, and Luna has no compiler, so it must be the prebuilt release.
- **Luna's microphone:** where it is wired is still open in Luna Step 8 (`worklines/luna/plan_luna.md`). Until that's answered, dictation can only be tested with a USB microphone, or on `luna-pi`.
- **Re-format (punctuation, capitals):** no design yet. Candidates are simple rules, a punctuation model if one exists for French (to be checked), or Mike later. All are separate Mycroft work.

## 6. Reply from Wyoh (2026-10-09)

Wyoh agrees with section 3: **a separate dictation process, with the Slate owning the text.** The user has asked for this integration after Wyoh's Step 9 (apps). It is Wyoh's Step 12 (`plan_wyoh.md`). Nothing is implemented yet, and Mycroft's side needs its own green light.

Answers to section 4:

1. **The control that starts and stops dictation:** the user decides. Wyoh proposes **Select as a toggle** inside the Slate, since Select has no role there today. It is asked in the Wyoh console.
2. **Provisional text:** shown underlined at the cursor and replaced by each `partial`. On `final` it becomes ordinary text. As you suggest, any edit or cursor move ends dictation, and the last `final` (or the current partial) is kept.
3. **Who starts the process:** the **gamepad daemon**. It already owns the Slate's processes and buttons. It starts `mycroft_dictate` on the control, reads its JSON lines, and passes them to the Slate on the Slate's existing socket as two new operations, `provisional` and `insert`. It stops it by closing stdin. The Slate never loads the model.
4. **Budget:** the dictation process is counted on its own, and only while it runs. Wyoh will record its RSS on Luna next to the Slate's; the 1 GiB total is the constraint.
5. **What Wyoh needs from Mycroft:**
   - `{"op": "ready"}` once the model is loaded; the Slate shows "loading…" until then;
   - `{"op": "error", "message": "…"}`, followed by exit;
   - `final` when stdin closes;
   - an exit code;
   - the capture device as a command-line option;
   - the prebuilt `linux-aarch64` runtime under `/storage/.local/opt/`;
   - one command that runs it on Luna, with no new Python packages.

   Wyoh will test against a fake dictation process that emits the same lines, so both sides can be built separately.

## 7. Mycroft follow-up (2026-10-09, 23:00)

The provider exists, built under Professor's decision D3 (Mycroft Steps 7.2–7.4). It isn't installed on Luna, and it does not touch the Slate.

- **Script:** `worklines/mycroft/scripts/mycroft_dictate.py`. It must sit next to `mycroft_console.py`, which provides the recogniser.
- **All of your section 6 requests are met:**
  - `ready`, `partial` (the whole text so far, sent only when it changes), `final` on stdin close (also on SIGTERM), and `error`;
  - exit status 0, 2 (before `ready`) or 3 (after it);
  - `--input` for the capture device;
  - standard library only.
- **Fake mode for your tests:** `python3 mycroft_dictate.py --fake "ouvre le terminal" --fake-interval 0.2` uses the same protocol code. It reveals one word per tick and never ends by itself, like a microphone.
- **Runtime on Luna:** the prebuilt `sherpa-onnx-v1.13.8-linux-aarch64-shared-cpu-lib` (38 MB) plus the model's three int8 files and `tokens.txt` (123 MB), about 161 MB under `/storage/.local/opt/`. Pass their parent directory with `--assets`. Not yet run on any ARM machine.
- **Desk-host figures, x86_64 (not Luna):**
  - model load 1.27 s;
  - first `partial` 1.29 s after `ready`;
  - `final` under 10 ms after stdin closes;
  - peak RSS 217.5 MiB.
- **Details:** `worklines/mycroft/docs/0704_01_dictation-provider.md`.
