# Mycroft dictation provider for Wyoh's Slate (Steps 7.2–7.4)

> **Freshness:** 🟡 historical · **Written:** 2026-10-11 · **Checked:** 2026-10-31 · **Step:** mycroft 7.4 ✅

**Status:** 7.2 and 7.4 done; 7.3 done on the desk host, with the `luna-pi` measurement waiting until `luna-pi` is back on.
**Date:** 2026-10-09
**Green light:** 🟩 go 7.2–7.4, given by Professor on the user's behalf (decision D3 in `worklines/professor/docs/0503_01_delegated-coordination-log-2026-10-09.md`). No Luna install, no Slate code, no commit.

## 7.2 Interface (agreed with Wyoh)

Wyoh's answer is in `worklines/wyoh/docs/0600_02_note-from-mycroft-dictation-in-slate.md` §6. Wyoh's gamepad daemon starts the provider and passes its text to the Slate, which owns the text. The provider only recognises speech.

```text
python3 mycroft_dictate.py --input /dev/snd/pcmC#D#c [--assets DIR]
python3 mycroft_dictate.py --fake "texte de test" [--fake-interval 0.2]
```

| Direction | Message | Meaning |
| --- | --- | --- |
| stdout | `{"op": "ready"}` | model loaded, capture started; the Slate can drop "loading…" |
| stdout | `{"op": "partial", "text": "…"}` | the **whole** current text of the utterance, sent only when it changes |
| stdout | `{"op": "final", "text": "…"}` | sent once: stdin closed, SIGTERM, or the input ended |
| stdout | `{"op": "error", "message": "…"}` | then exit |
| stdin | close | stop; anything written is ignored |
| exit status | `0` / `2` / `3` | after `final` / error before `ready` / error after `ready` |

- **Text:** lower case without punctuation (the model's output, lowered); UTF-8 JSON with literal accents (`ensure_ascii=False`).
- **No audio** is written anywhere.
- **One utterance per process.** The model's memory is released on exit.
- **Assets:** `--assets DIR` (default `$MYCROFT_ASSET_ROOT`) is the parent of the model directory and the runtime directory.
- **Fake mode:** reveals the given words one per tick and never ends by itself, like a microphone. It runs the same protocol code, so Wyoh can build and test without a model or microphone.

## 7.3 Runtime by architecture

`mycroft_console.runtime_dirname()` maps the machine to the one pinned Sherpa v1.13.8 release; another architecture is an error.

| Machine | Runtime directory | Archive SHA-256 |
| --- | --- | --- |
| `x86_64` | `sherpa-onnx-v1.13.8-linux-x64-shared-no-tts` | `d0f96c8b…eec5fc` (Step 4 record) |
| `aarch64` (Luna, `luna-pi`) | `sherpa-onnx-v1.13.8-linux-aarch64-shared-cpu-lib` | `fb98b80628a383909bf83626daca2e0d0ffc93bf1f7d222eaaa4282b388f072f` (matches GitHub's published digest) |

The aarch64 `-lib` archive is the official prebuilt build, libraries only (12.6 MB compressed, 38 MB extracted). Checked on the desk host with `file`, `readelf`, and `objdump`:

- all three libraries are 64-bit ARM (aarch64) ELF objects;
- their `RPATH` is `$ORIGIN`, so they find each other without `LD_LIBRARY_PATH`;
- they need only `libc`, `libm`, `libdl`, `libpthread`, `librt`, `libstdc++`, and `libgcc_s`;
- the newest symbol versions they require are `GLIBC_2.17` and `GLIBCXX_3.4.19` (GCC 4.8 era).

No compiler is needed, which suits Luna. **Not yet shown:** that they load and run on `luna-pi` or Luna, and their memory and speed there. The `luna-pi` run waits until it is back on (Professor D3).

**Footprint on a device:** 123 MB of model files (three int8 ONNX files plus `tokens.txt`; the rest of the 405 MB model directory isn't needed) plus 38 MB of libraries, about **161 MB**, plus the two scripts.

## 7.4 Implementation and evidence

- `worklines/mycroft/scripts/mycroft_dictate.py` reuses `SherpaStreamingRecognizer`, `make_source`, and `AlsaCaptureSource` from `mycroft_console.py`. It uses the standard library and `ctypes` only, so it needs no new Python packages on Luna.
- Contract: `test/mycroft/dictate.feature`. Tests: `test/mycroft/test_dictate.py` runs the script as a subprocess, because the process boundary is what the host relies on.

| Command | Result |
| --- | --- |
| `uv run pytest test/mycroft` | 31 passed, 4 skipped (assets not set) |
| `MYCROFT_ASSET_ROOT=… uv run pytest test/mycroft -m integration` | 4 passed |
| `uv run pytest -m "not live and not integration"` | 292 passed |

Real-model run, desk host `termidor` (x86_64), public WAV `common_voice_fr_19364697.wav` (7.1 s), evidence in `results/mycroft/dictate/20261009T203427Z/`:

| Measure | Value |
| --- | --- |
| Start → `ready` (model load) | 1.27 s |
| `ready` → first `partial` | 1.29 s |
| Partials | one every 0.2–0.5 s, word by word |
| Host closes stdin → `final` | under 10 ms |
| Peak RSS | 217.5 MiB |
| Final text | `ce site contient quatre tombeaux de la dynastie ashéménide et sept des sassandides` |

These are desk-host figures. They say nothing about Luna's speed or memory. The first partial arrives about 1.3 s after `ready` even on this PC, because the streaming model needs a first audio window before it can emit text.

## Left open

- **7.3 on `luna-pi`:** load the aarch64 runtime and measure model load, first-partial latency, real-time factor, and RSS (when `luna-pi` is on).
- **On Luna:** install under `/storage/.local/opt/` as Wyoh asked. Not authorised tonight. It also waits for Luna Step 8 to locate the microphone.
- **7.5 acceptance:** dictated text in the Slate, corrected and sent. This needs Wyoh's Step 12 and the user.
