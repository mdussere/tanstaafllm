# Mycroft evaluation harness

`benchmark_asr.py` is a disposable desktop measurement tool, not the Mycroft v0 product CLI. It invokes an already-installed native decoder once per WAV file and writes one JSON object per line. It makes no network calls and downloads no asset.

```text
python3 worklines/mycroft/scripts/benchmark_asr.py \
  --manifest /outside-repo/fixtures.json \
  --candidate /outside-repo/candidate.json \
  --results /outside-repo/results.jsonl
```

Manifest shape:

```json
{"fixtures": [{"id": "clip-01", "audio": "/outside-repo/clip-01.wav", "reference": "BONJOUR"}]}
```

Candidate shape:

```json
{
  "id": "native-example",
  "version": "pinned-version",
  "command": ["/outside-repo/decoder", "{audio}"],
  "transcript_regex": "(?m)^TRANSCRIPT: (?P<text>.+)$"
}
```

The fixture must be a mono, signed 16-bit PCM WAV. The transcript parser is intentionally explicit: backend output is not treated as a transcript merely because it happened to be printed. Fields include raw stdout/stderr, exit status, elapsed seconds, sampled peak RSS, audio duration, RTF, raw transcript, and normalised WER.

Peak RSS is sampled from Linux `/proc`; short-lived child allocation between samples can be missed, and a desktop value cannot prove a 1-GiB target fit. Results must record the host and separate installed runtime/model sizes separately.

## Mycroft v0 text console

`mycroft_console.py` is the foreground composition application, not the batch
benchmark. It uses one fixed local profile: Sherpa-ONNX `v1.13.8`, the French
streaming Zipformer `2023-04-14`, int8 encoder/decoder/joiner, CPU provider,
one inference thread, and greedy decoding. There is no model argument, model
download, command execution path, network client, or persistent service.

The installed runtime and model directory live outside Git. Point
`MYCROFT_ASSET_ROOT` at their common parent:

```text
MYCROFT_ASSET_ROOT=/path/to/assets \
  python3 worklines/mycroft/scripts/mycroft_console.py \
  --input /path/to/input.wav
```

Replay accepts only RIFF/WAVE, signed 16-bit mono PCM. This is deliberately the
same narrow format as the existing v0 evaluation contract: convert M4A, MP3,
or stereo files explicitly before invoking Mycroft. Replay is paced in 200 ms
chunks through the same recogniser callback path as live capture; EOF has the
same finalisation semantics as stopping with `Space`.

For live capture, pass a Linux capture-node path such as
`/dev/snd/pcmC0D0c`. The source adapter validates that exact character device
and maps it internally to ALSA's `plughw:0,0` form, because `arecord` consumes
ALSA device names rather than `/dev` paths. `arecord` (ALSA utilities) is a
host/runtime prerequisite; its availability and real microphone operation are
not yet evidence of Luna compatibility. The process reads raw PCM only and
never writes an audio file.

The console uses the terminal's alternate screen, loads the model once at
startup, and redraws only when its state changes. The interactive bindings are
`Enter` accept, `Esc` discard, `q` quit when no draft is
being edited, and `Ctrl-C` quit without emitting anything. `Space` toggles
recording (start, then stop); inside a stopped draft `Space` and `q` are
ordinary text. Function keys are not used, because editor-embedded terminals
such as VS Code's capture them; unbound escape sequences are ignored. Accepted text is emitted once to stdout as UTF-8; when
stdout is the terminal it is printed after the full-screen view closes, so it
stays visible. It is never executed or sent anywhere. After a user edit, later
hypotheses remain visible but cannot overwrite the draft.

### Tests and experiments

All Mycroft console tests and experiments are pytest modules under
`test/mycroft/`. They use public upstream WAVs or generated in-memory PCM only;
no private recording is read or copied.

```text
python3 -m pytest test/mycroft -v
MYCROFT_ASSET_ROOT=/path/to/assets \
  python3 -m pytest test/mycroft -m integration -v -s \
  --timeout=90 --timeout-method=thread
```

The second command verifies the pinned C adapter and the complete public-WAV
replay composition flow. It requires the externally installed Sherpa assets.
The integration run includes `test_console_terminal.py`, which runs the real
program on an 80×24 pseudo-terminal, emulates the screen with `pyte`, and saves
each screen under `results/mycroft/console-terminal/<timestamp>/`
(`console_terminal.feature` is its contract). A real-terminal live-microphone
smoke test remains manual and pending; do not mistake a skipped test for
device validation.

## Mycroft dictation provider

`mycroft_dictate.py` produces one utterance of live text for a host that owns
it (Wyoh's gamepad daemon, for the Slate). It writes JSON lines on stdout
(`ready`, `partial`, `final`, `error`) and stops when its stdin is closed. The
protocol is in `worklines/mycroft/docs/0704_01_dictation-provider.md`.

```text
python3 worklines/mycroft/scripts/mycroft_dictate.py --input /dev/snd/pcmC0D0c --assets /path/to/assets
python3 worklines/mycroft/scripts/mycroft_dictate.py --fake "ouvre le terminal"
```

The Sherpa runtime directory is chosen by architecture: the x64 no-TTS
release on a desktop, and the official `linux-aarch64-shared-cpu-lib` release
on Luna or `luna-pi`.

## Model choice (plan step 9.3)

`--model` selects the speech model in `mycroft_console.py` and `mycroft_dictate.py`:

- `zipformer-fr-2023` (default): the pinned 2023 French Zipformer, int8, upper case lowered by Mycroft;
- `kroko-fr-2025`: the Kroko French community model (fp32, ~18 M parameters), which writes its own case and punctuation.

`--threads` sets Sherpa's thread count (2 is best on Luna, `0802_01`). Example of a live test on the desk host:

```text
MYCROFT_ASSET_ROOT=/path/to/assets \
  uv run python worklines/mycroft/scripts/mycroft_console.py --input /dev/snd/pcmC0D0c --model kroko-fr-2025 --threads 2
```
