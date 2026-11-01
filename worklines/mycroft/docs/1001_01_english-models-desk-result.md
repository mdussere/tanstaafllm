# English speech-to-text for Mike in English (plan steps 10.1 and 10.2, desk host)

> **Freshness:** 🟢 current · **Written:** 2026-11-01 · **Checked:** 2026-11-01 · **Step:** mycroft 10.2

**Date:** 2026-11-01
**Why:** Mike's assessment (`worklines/mike/docs/1704_01`) finds LFM2.5-350M usable in English but not in French. The user wants to try talking to Mike in English, with their French accent (relayed by Professor, 2026-11-01).
**Scope:** desk host Termidor (x86_64, i5-4590), 2 threads, public clips only. Nothing on Luna; the deployed French path is unchanged.

## 10.1 What exists

Sherpa-ONNX's `asr-models` release (checked 2026-11-01) has two small English streaming models that run on the same runtime as today's French Kroko:

| | Kroko English | English Zipformer 20M |
| --- | --- | --- |
| File | `sherpa-onnx-streaming-zipformer-en-kroko-2025-08-06.tar.bz2`, 57.3 MB, SHA-256 `c8676e5f…6ade6834` | `sherpa-onnx-streaming-zipformer-en-20M-2023-02-17.tar.bz2`, 127.9 MB, SHA-256 `9c559283…2765d9` |
| Size | 70 MB fp32 encoder, ~18 M parameters (same shape as Kroko French) | ~20 M parameters; 43 MB int8 encoder |
| Training | Banafo community model | LibriSpeech (icefall, `desh2608/…-streaming-small`) |
| Output | capitals and punctuation | upper case, no punctuation |
| Licence | as Kroko French: Banafo states CC-BY-SA, but no licence text ships (README only points to `Banafo/Kroko-ASR`) | Apache-2.0 |
| ARM | ONNX files for Sherpa; the aarch64 runtime already on Luna loads the same kind of files | same |

Not measured, with the reason:
- **Moonshine Tiny English** (quantised, 29.9 MB): in Sherpa it is an offline model, so it would give no drafts while you speak.
- **NeMo streaming FastConformer English** (int8, ~100 MB): larger than both.
- **The larger English Zipformers** (2023-02-21, 2023-06-26): 300–500 MB archives.

## 10.2 Desk measures

`test/mycroft/test_candidates.py::test_english_candidates` (marker `integration`) decodes each clip with Sherpa's own binary, one fresh process per clip, at 2 threads, as in 9.3. Evidence: `results/mycroft/english-candidates/20261101T113300Z/report.json`.

The corpus is the two 16 kHz LibriSpeech clips shipped with the Zipformer 20M (6.6 s and 17.0 s). LibriSpeech is that model's training corpus, so these clips favour it, as Common Voice favoured the old French model.

| | Kroko English | English Zipformer 20M (int8) |
| --- | --- | --- |
| Word error rate, clip 0 / clip 1 | 0.000 / 0.083 | 0.056 / 0.042 |
| CPU time for 23.6 s of audio | 9.7 s | **4.4 s** |
| Peak RSS | 158 MiB | **93 MiB** |
| Load (recogniser created) | 4.8 s | **0.8–1.5 s** |
| Text | **"God, as a direct consequence of the sin…"** | "AS A DIRECT CONSEQUENCE OF THE SIN…" |

Reading the errors:
- **Kroko English:** its clip-1 errors are mostly spelling ("dishonored", "forever" for "for ever"), plus the last word "heaven" lost. That is the end-of-stream case fixed in Mycroft's own adapter, which feeds 1.0 s of silence (9.7); Sherpa's binary does not. Through Mycroft's adapter (`--model kroko-en-2025`), clip 1 ends "…a blessed soul in heaven.", so without the binary's end-of-stream loss its only differences are the two spellings.
- **Zipformer 20M:** "brothels" became "broffals", and it dropped the first word "God".

## What it means

- **Both are small enough for Luna** on paper. Kroko English should cost what Kroko French costs (RTF ~0.8 at 2 threads, ~170 MiB resident). The Zipformer 20M uses about half Kroko's CPU and 65 MiB less, but gives bare upper-case words.
- **Public clips say little about the user's accent.** The question is how each understands French-accented English with Luna's app names and commands. That is the reading in `1003_01`, which waits for the user.
- **Kroko English's load (4.8 s here)** is longer than its French twin's (2.9 s); preparing the files once at ONNX Runtime's "extended" level halved the French load on Luna, and would be the first thing to try before Luna.

## First try on the user's voice (2026-11-01)

The user sent a 13 s phone recording (M4A, private, outside the repository): one free sentence in French-accented English, not the script. Evidence: `results/mycroft/english-candidates/20261101T115058Z/` (ignored by Git). The harness's WER compares it with the script, so it is meaningless here; judged by hand against what was said:

- **Kroko English:** every word right, punctuated (20 words).
- **Zipformer 20M:** 4 words wrong out of 20 ("phone" became "foam", "proper" became "popoth"; "computer" misspelt; "of" inserted).

One sentence proves little, but it is the first sign that Kroko English understands the user's accent.

**Next:** the user's English reading (`1003_01`), then the same comparison on it. No Luna measure before the user decides.
