# Lighter models: Kroko, Parakeet Redux, Phonon-2 (plan steps 9.3 and 9.6, desk host)

**Date:** 2026-10-11
**Green light:** the user, 2026-10-11: no more tuning of the current model; look for a substantially lighter one (Kroko, plus Parakeet Redux from the user and Phonon-2 from Charlie). The user would accept speaking English for a small, efficient model.
**Scope:** desk host (`termidor`, x86_64, i5-4590), 2 threads. The Luna measurement of Kroko is prepared (`test_luna_9_3_kroko`) and waits for a slot.

## Parakeet Redux and Phonon-2: not runnable on Luna

Both are compressed derivatives of NVIDIA's Parakeet TDT 0.6B v3. The plan had already excluded the original from Luna: NVIDIA states 2 GB of RAM (`0201_03`).

| | Parakeet Redux (Moondream) | Phonon-2 (Fermion Research) |
| --- | --- | --- |
| Languages | 25, French included (FLEURS French WER 7.71 per its card) | **English only** |
| Download | 178 MB (ternary weights −1/0/+1) | 164 MB (encoder at ~2.1 bits per weight) |
| Licence | CC-BY-4.0 | CC-BY-4.0 (code Apache-2.0) |
| Linux CPU runtime | Moondream's Photon engine, via `pip install moondream` | the `fermion-research` package: **PyTorch + Transformers** |
| Checked on 2026-10-11 | `uv pip compile` for aarch64 Linux **fails**: its kernels (`kestrel-kernels` 0.7.x) publish no aarch64 Linux wheel. On x86 it pulls PyTorch 2.14 and the full CUDA stack. | The dependency chain is PyTorch, Transformers and SciPy. Phonon's card says download size is not runtime memory, because engines expand the weights at load. |
| Verdict for Luna | **Cannot be installed** (no ARM64 Linux build of its engine). | **Cannot fit**: ~600 M parameters expanded by PyTorch exceed Luna's 1 GiB. That is also ~30× Kroko's compute on the A35. |

Their small downloads come from storage compression. The network behind them is still Parakeet's ~600 million parameters, which must be computed for every audio frame. The size that matters on Luna is the number of parameters, and that is where Kroko (~18 M) is far ahead. Community GGUF conversions of Phonon-2 for CrispASR (402–1,255 MB) were not tried.

## Kroko French against the current model

`test/mycroft/test_candidates.py` (marker `integration`) decodes the same files with Sherpa's own binary, one fresh process per file, at 2 threads. Evidence: `results/mycroft/candidates/20261011T203234Z/report.json` (ignored by Git; it contains the private reading's transcripts).

- **Kroko:** `sherpa-onnx-streaming-zipformer-fr-kroko-2025-08-06`, archive SHA-256 `e6ffd3dc43725cd6c8137b05c739f15607d0df946b9b90eb141e10059efca024`, fp32 files as published.
- **Current model:** the int8 Zipformer from 2023-04-14.

### The user's consented reading (130 s, script `0105_01`, the same file as `0104_06`)

| | Current model | Kroko |
| --- | --- | --- |
| Word error rate (WER) | 0.134 | **0.091** |
| Real-time factor | 0.065 | **0.035** |
| CPU time for 130 s of audio | 30.6 s | **16.2 s** |
| Peak RSS | 215.9 MiB | **160.5 MiB** |
| Load (recogniser created) | **1.09 s** | 2.89 s |
| Output style | upper case, no punctuation | **sentences with capitals and full stops** |

Opening of each transcript:
- Current: `DANS LE TERMINAL L'ANSE GUIDE STATUS PUIS RÉSUME LES FICHIERS MODIFIÉS SANS RIEN ÉCRIRE APICHERIE DE MIMORGOME PUIS CHERCHE…`
- Kroko: `Dans le terminal lance guide Status. Puis je résume les fichiers modifiés sans rien écrire. Affiche Redmy.com puis cherche…`

### Public Common Voice clips (references in the current model's `trans.txt`)

| Clip | Current WER | Kroko WER |
| --- | --- | --- |
| `common_voice_fr_19738183` | 0.182 | 0.273 |
| `common_voice_fr_27024649` | 0.000 | 0.083 |
| `common_voice_fr_19364697` | 0.154 | 0.231 |

The current model was trained on Common Voice, so these three clips favour it. On the user's own voice and vocabulary, Kroko is better.

## Reading

- **Kroko is the first candidate with a substantial gain.** It needs about half the CPU of the current model, 55 MiB less memory, is more accurate on the user's voice, and adds punctuation and capitals, which the user wanted for the re-format idea.
- **Its load is longer:** 2.9 s against 1.1 s on the desk host. If Luna keeps its ratio of ~15× seen in 8.1, that would be ~40 s. This is the first thing to measure on Luna (`test_luna_9_3_kroko`).
- **Projection for Luna (to verify):** the current model decodes at RTF 1.32 with 2 threads. With half the CPU work, Kroko could fall below 1, which is what live dictation needs.
- **Still open for Kroko:**
  - the licence: its README says CC-BY-SA, but the published `LICENSE` file is empty;
  - hotwords: its tokens are lower case with punctuation, and no `bpe.vocab` is published;
  - an int8 version, which would reduce memory further;
  - adapting Mycroft's adapter to its file names.

## Provenance and licence of the Kroko file (checked 2026-10-11, at the user's question)

- **Where the file comes from:** Sherpa-ONNX's model release `asr-models` on GitHub (`k2-fsa/sherpa-onnx`), file `sherpa-onnx-streaming-zipformer-fr-kroko-2025-08-06.tar.bz2`, 57.2 MB, SHA-256 `e6ffd3dc…efca024`. Its only README line is "See license at https://huggingface.co/Banafo/Kroko-ASR". So it is the k2-fsa team's ONNX packaging of a Banafo/Kroko community model. Which Banafo variant (`Kroko-FR-Community-64-L` or `-128-L`) is not stated.
- **Banafo's Hugging Face repository** (`Banafo/Kroko-ASR`): the README says the community models are "CC-BY-SA licensed", with commercial models separate. The repo metadata says "license: other / test", and the `LICENSE` file is empty.
- **Banafo's engine** (`github.com/kroko-ai/kroko-onnx`): Apache-2.0 per GitHub, active (last push 2026-05-28). It has a "free" build (no licence code) for community models, and a "pro" build with a licence key for paid models. Its README repeats "CC-BY-SA licensed community models".
- **`kroko.ai`** is the commercial site, which is why it shows no open-source download.
- **Verdict:** the community model is stated as CC-BY-SA in two Banafo READMEs, but no licence text ships with the weights. That is fine for this personal evaluation. Before redistributing the model (for example in a Luna image), ask Banafo for, or find, the exact licence version. CC-BY-SA requires attribution, and share-alike applies to modified weights such as the aarch64-prepared files.
