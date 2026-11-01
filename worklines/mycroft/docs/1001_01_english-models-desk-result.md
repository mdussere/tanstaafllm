# English speech-to-text for Mike in English (plan steps 10.1 and 10.2, desk host)

> **Freshness:** 🟢 current · **Written:** 2026-11-01 · **Checked:** 2026-11-01 · **Step:** mycroft 10.2–10.6

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

## 10.3 The scripted reading (2026-11-01)

The user read the 14 sentences of `1003_01` on their phone (94 s, M4A, private). Evidence: `results/mycroft/english-candidates/20261101T115520Z/` (ignored by Git; it holds the transcripts). The user also read the sentence numbers aloud, so the harness's WER (0.215 and 0.407) counts them as insertions; the table removes them first.

| | Kroko English | Zipformer 20M |
| --- | --- | --- |
| WER, spoken numbers removed (134 words) | **0.119** | ≈ 0.35 (some numbers merged into words, so slightly overstated) |
| RTF on the desk host | 0.047 | 0.039 |
| Peak RSS | 159 MiB | 105 MiB |

For comparison, Kroko French made 0.091 on the user's French reading (`0903_01`).

**What Kroko English got wrong**, sentence by sentence:

- **Ordinary words, sound-alikes:** "Luna guide" → "lunar guide", "dino" → "dyno", "git status" → "git statues", "files changed" → "file changed", "delete" → "delight", "free lunch" → "freelanch", "that was quick" → "but what was quick".
- **Project names, the real gap:** Mycroft → "Minecraft", Wyoh → "you", Mannie → "Many". Wolfenstein, NetSurf (once "NetSuff" through Mycroft's adapter), Mike, Luna and Professor came out right.
- **Everything else** (calculator, terminal, commander window, music folder, memory, battery, log file, small talk) was right, and punctuated.

The Zipformer 20M lost much more: "terminal full screen" → "DAMNOL FOO STREAM", "run git status" → "RANDHIST STATUES", "battery charging" → "BETTERY SHOUTING", "files" → "FIRES". It is ruled out for this use.

**Reading:** Kroko English understands the user's French-accented English about as well as Kroko French understands their French. Its weak point is the project's own names, which is what known words (proposed 9.10) are for: a per-dictation list with Mycroft, Wyoh and Mannie, mapped from how the user pronounces them. Meanwhile Mike could also tolerate "Minecraft" or "Many" in its own lookup.

## 10.5 Known words on Kroko English (2026-11-01, the user's go)

Kroko ships no `bpe.vocab`, which Sherpa needs to split a known word into tokens. `scripts/vocab_from_tokens.py` rebuilds one from Kroko's own `tokens.txt` (646 pieces). A first version scored pieces by rank alone, so Sherpa split "Mannie" into single letters that the model never emits, and the list did little. Scored so that the split with the fewest pieces wins, as the model's own BPE merges do, the list works. The adapter now writes known words in their own case for Kroko (the 2023 French model needed upper case).

`test/mycroft/test_hotwords.py::test_kroko_english_known_words_on_the_users_reading` (integration, private reading). Evidence: `results/mycroft/hotwords-en/20261101T120553Z/` (ignored by Git). List: Mycroft, Wyoh, Mannie, Luna, NetSurf, Wolfenstein.

| Setting | WER (numbers removed) | Known words right (of Mycroft, Wyoh, Mannie, Luna ×2, NetSurf, Wolfenstein) |
| --- | --- | --- |
| Greedy (today's default) | 0.111 | 2 of 7 |
| Beam search, no list | 0.119 | 2 of 7 |
| **Beam search + list, boost 3.0** | **0.089** | **5 of 7** |
| Same, Wyoh and Mannie boosted to 10 | 0.104 | 5 of 7, and new errors ("Myc Mycroft", "My") |

- **Fixed by the list:** "Minecraft" → Mycroft, "net surf" → NetSurf, "lunar guide" → Luna guide.
- **Not fixed: Wyoh ("you") and Mannie ("Many").** As the user says them, they sound like ordinary English words, and a stronger boost only damages the neighbouring words. Two options remain: a small replacement table after recognition, limited to the dictation's context (for example "Many and the professor" → "Mannie and the Professor"), or Mike tolerating "you"/"Many" in its own lookup.
- **With the list, Kroko English reaches 8.9 %**, as good as Kroko French on the French reading (9.1 %).

Not yet measured: beam search's extra CPU on Luna (here the four settings decode in a few seconds each on the desk host).

## 10.6 On Luna (2026-11-01)

Professor's go, Mannie stopped, no reboot. Kroko English, prepared at ONNX Runtime's "extended" level, was installed under `/storage/.local` beside Kroko French and measured resident through Mycroft's adapter at 2 threads (`test_luna_footprint.py::test_luna_10_6_resident_kroko_english`). Evidence: `results/mycroft/luna-footprint/20261101T171148Z/`.

| | Kroko English on Luna |
| --- | --- |
| Ready (recogniser loaded) | 22.5 s |
| Resident memory, idle / peak | 162 MiB / 188 MiB |
| Final text after the end of the audio | 0.7–0.8 s |

It costs what Kroko French costs on Luna. **The Slate still runs French:** Wyoh's `dictate_command` names `--model kroko-fr-2025`, and Wyoh is paused, so the switch waits. Beam search with known words (10.5) is not yet measured on Luna.
