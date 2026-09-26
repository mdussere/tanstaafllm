# Mycroft v0 text-console implementation and automated evidence

**Status:** foreground console implemented; automated replay and adapter evidence
passes. A real microphone/terminal smoke test is still required before Step 5
acceptance.

## Delivered boundary

`worklines/mycroft/scripts/mycroft_console.py` implements the approved v0
composition loop:

```text
one --input PATH → source chunks → one pinned local ASR profile
                 → visible hypothesis + editable draft → explicit stdout acceptance
```

It has no model selector, download path, context feed, command parser, IPC
sink, network client, audio retention, or resident background process. The
selected profile is Sherpa-ONNX `v1.13.8`, French streaming Zipformer
`2023-04-14`, int8 encoder/decoder/joiner, `cpu`, one thread, and
`greedy_search`. The exact selected filenames agree with the existing candidate
profile (`encoder`, `decoder`, and `joiner` at
`epoch-29-avg-9-with-averaged-model.int8.onnx`).

The model assets remain external to the repository and are located through
`MYCROFT_ASSET_ROOT`. This does **not** turn that environment variable into a
model selector: it is the installation location of the one profile.

## Source contract in code

- A regular path is accepted only as RIFF/WAVE, signed 16-bit mono PCM. Other
  codecs and stereo fail before a session starts; conversion stays an explicit
  caller cost.
- Replay reads and paces 200 ms chunks. It calls the same recogniser callback
  used by live capture, and its EOF calls the same finalisation path as `F6`.
- A live path must be `/dev/snd/pcmC#D#c`, be a readable character device, and
  is mapped to ALSA `plughw:#,#` for `arecord`. This respects the requested
  `/dev/...` user interface while using ALSA's actual device naming internally.
- `F5`, `F6`, `Enter`, `Esc`, editing keys, and `q` implement the state machine
  in the intent. Accept emits the exact edited draft once to stdout. Discard
  emits nothing. A manually edited draft cannot be overwritten by later ASR
  callbacks.

## Automated evidence

All tests and experiments for this console are pytest modules in
`test/mycroft/`:

- `test_console.py`: 15 deterministic state-machine, renderer, key-decoder,
  replay pacing/EOF, format-rejection, and capture-path-validation tests.
- `test_sherpa_adapter.py`: pinned native C API test plus the full public-WAV
  replay → hypothesis/draft → EOF/F6 → edit → accept path. Both require only
  the externally installed Sherpa package and upstream public `test_wavs`.

On 2026-09-25, with the external `sherpa-onnx-v1.13.8` x64 shared runtime and
French model package present, all then-existing checks passed: **16 passed in
3.65 s**. The first failed adapter attempt exposed a real filename mismatch;
the implementation was corrected to the `epoch-29-avg-9-with-averaged-model`
int8 files already pinned by the candidate record, then the adapter test passed
in 2.68 s. A later asset-location regression test brings the suite to 17
tests: 15 asset-free tests pass by default and two native integrations skip
cleanly until `MYCROFT_ASSET_ROOT` again points at the externally installed
package. These are desktop functional results only, not Luna latency, RAM, or
microphone compatibility evidence.

## Remaining acceptance evidence

1. Run the documented console inside a real terminal against a permitted live
   capture node. Verify permission/device error handling, F5/F6, visible
   partials, edit/supplement, Enter, Esc, and q without retaining audio.
2. Record equivalent memory/latency evidence for this foreground C-API profile
   under the existing ledger. The earlier batch-decoder RSS is useful baseline
   evidence, not proof for this process or for Luna.
3. Validate the delivered Luna audio stack only in its separately green-lit
   hardware stage. No x64 desktop `arecord` result can prove the target path.
