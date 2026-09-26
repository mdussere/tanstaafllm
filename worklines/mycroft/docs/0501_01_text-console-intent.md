# Mycroft v0 text-console intent

**Question answered:** What exact user-visible application is built before any Mycroft v0 implementation starts?<br>
**Status:** implementation green-lit; automated replay/recogniser evidence complete, real-microphone smoke test pending.<br>
**Model policy:** one pinned model/runtime in v0; future model configurability is a separate compatibility requirement, not a v0 selector.

## Purpose

Mycroft v0 is a foreground, text-only application. It accepts either live microphone audio or a replayed audio file, displays incremental ASR hypotheses in a visible draft, and lets the user edit or supplement that draft. Nothing is sent to a command, Mike, Wyoh, or another destination until the user explicitly accepts it. Discarding removes the draft from the application view; it must not execute or retain it.

The application proves the interaction shape, not a graphical window manager, target microphone stack, contextual ASR, or command interpreter.

## Invocation and parameters

```text
mycroft-console --input /dev/snd/pcmC0D0c
mycroft-console --input ./representative-reading.wav
```

| Parameter | v0 behaviour |
| --- | --- |
| `--input PATH` | The only source parameter. A regular audio file is replayed as a time-ordered pseudo stream. A character-device path, normally under `/dev/snd/`, is opened as live capture. The application reports which source kind it selected. |
| regular-file input | Invalid, unreadable, unsupported, or non-normalisable audio fails before a recording session begins. Replay uses the same incremental ASR and UI path as live capture; it is not a separate batch-result screen. |
| character-device input | The foreground capture adapter accepts only a readable capture PCM node shaped `/dev/snd/pcmC#D#c`; it maps that node internally to ALSA `plughw:#,#` for `arecord`. Permission, format, missing-ALSA-tool, or device failures leave the console idle with an actionable error. A path under `/dev` is not assumed to be a microphone merely because it exists. |
| selected model | Exactly one installed, pinned ASR model/runtime is used in v0: the current Sherpa reference unless a reopened evidence step changes that decision. There is no runtime model picker. |

Model identity, version, asset checksum, and recogniser settings appear in a non-editable status view. A later profile/configuration mechanism may choose among compatible installed models, but must preserve these input, draft, acceptance, replay, and test contracts.

## Visible console and controls

The terminal shows a status line, the current mode/source, a single-line editable draft, an incremental-hypothesis area, and a concise key legend. The editable draft is authoritative once the user changes it; subsequent ASR partials appear separately and must not overwrite manual edits.

| Key | Action | Allowed states | Behaviour |
| --- | --- | --- | --- |
| `F5` | Start recording | idle, stopped draft, discarded, accepted | Starts a fresh capture session and clears only the unaccepted draft after confirmation in the status area. |
| `F6` | Stop recording | recording | Stops audio capture, finalises outstanding ASR audio, and leaves the resulting draft editable. |
| `Enter` | Accept text | stopped draft | Emits the exact current draft as the sole UTF-8 result, marks it accepted, and performs no destination action. |
| `Esc` | Discard text | recording, stopped draft, accepted | Stops capture if necessary, clears the local draft/hypothesis view, and reports discard. |
| ordinary printable keys, arrows, backspace/delete | Edit or supplement draft | stopped draft | Normal single-line terminal editing. `Enter` is reserved for accept, so v0 does not create multiline input. |
| `q` | Quit | non-recording | Exits without retaining an unaccepted draft. During recording it explains that `F6` or `Esc` is required first. |

The binding names are part of the v0 intent and must be configurable only if the test harness can still address their semantic actions. They are keyboard bindings for the pre-hardware console, not a claim about final handheld button mapping.

## State and scenario contract

```text
idle --F5--> recording --F6--> stopped-draft --Enter--> accepted
                   |                 |                    |
                   +------Esc--------+---------Esc--------+--> discarded
```

| Scenario | Required result |
| --- | --- |
| Start microphone capture | Status changes to recording; partial ASR updates remain visible; no accepted output yet exists. |
| Start replay | The audio file produces timed pseudo-stream chunks and the same partial/final UI events as microphone capture. End of file behaves as `F6`. |
| Stop | Capture stops once; the last recogniser final result is merged only into untouched draft text; manual edits survive. |
| Edit/supplement | User text can correct, delete, or add to the stopped draft before acceptance. No ASR update may erase an edit. |
| Accept | Only permitted from stopped draft. stdout/result sink receives the exact edited text once; the application does not parse it as a command. |
| Discard | Any unaccepted text is cleared. No stdout accepted-result event, command, network request, or retained recording results. |
| Invalid action | Start while recording, stop while idle, or accept while recording leaves the state unchanged and explains why. |
| ASR or audio failure | Capture stops safely, the last visible draft remains editable/discardable, and the error is surfaced. It never fabricates an accepted result. |

## Implementation approach

One foreground process owns the terminal state machine. It has four replaceable adapters: terminal input/rendering, audio source (`mic` or deterministic `replay`), the pinned streaming ASR recogniser, and an accepted-text sink. The only v0 sink is UTF-8 stdout or an in-process result object; no shell, IPC action, or network destination is connected.

The replay adapter paces fixed-duration PCM chunks through the same recogniser callback path as the microphone adapter. The recogniser returns partial and final hypotheses; a draft controller owns the distinction between automatic text and user-edited text. Rendering consumes state snapshots rather than recogniser callbacks directly, making terminal tests deterministic. The process constructs the single model only when the user starts a session, releases it on stop/discard/quit, and never becomes a daemon.

## Testing policy and harness

The test harness must test semantics independently of real audio and models, then use replay for controlled integration evidence.

1. **State-machine tests:** inject key actions and fake source/recogniser events. Assert transitions, prohibited actions, draft preservation, accept-once behaviour, and discard-with-no-result.
2. **Renderer tests:** compare normalised text-console snapshots for idle, recording, stopped draft, error, accepted, and discarded states. No terminal escape-sequence timing assumption is allowed.
3. **Replay-contract tests:** use a small public or consented WAV fixture and a deterministic chunk clock. Assert that replay follows the microphone event contract and that end-of-file finalises exactly once.
4. **Recognizer-adapter tests:** run the pinned model only on retained/public fixtures. Record model identity, elapsed time, peak RSS where measurable, transcript events, and failures using the existing resource ledger.
5. **Manual smoke test:** verify microphone permission/device failure, start/stop, visible partials, edit/supplement, accept, discard, and quit in a real terminal. Do not retain personal audio by default.

Tests must never require a target device, cloud inference, a resident service, a second model, or command execution. Private recordings, model weights, caches, and raw run logs remain outside Git.

## Acceptance for implementation

Mycroft v0 is acceptable only when the same console can use microphone and replay sources, presents incremental text, preserves edits, accepts exactly the edited draft, discards safely, reports failures honestly, and passes the state/replay/renderer tests with its one pinned local model inside the recorded resource ledger.
