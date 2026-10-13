# Known words and lighter models (plan steps 9.1 and 9.2)

**Date:** 2026-10-11
**Request:** the user, 2026-10-11. Keeping the current model resident costs ~250 MiB on Luna. Can a smaller model do, fine-tuned on the user's voice or restricted to one language? And can the model be given a list of known words ("Michael", Wyoh, Luna, Mycroft, Wolfenstein…) so that it recognises them without ambiguity?
**Scope:** desk host only; code reading, public sources, and synthetic speech. No private recording, nothing on Luna.

## 9.1 Known words ("hotwords") on the current model

### What Sherpa v1.13.8 requires (read in its source code)

- **The feature exists:** "hotwords", also called contextual biasing. A list of words or phrases gets a score bonus while the decoder searches, optionally with a boost per line (`WORD :2.0`).
- **It needs modified beam search.** Mycroft used greedy search, which ignores hotwords (`online-recognizer-transducer-impl.h`).
- **It needs the tokenizer's vocabulary.** The list is written in plain words, and Sherpa cuts each word into the model's tokens with a `bpe.vocab` file (`modeling_unit = "bpe"`, `bpe_vocab`; `utils.cc`, `EncodeHotwords`). Sherpa's model package doesn't include that file. Two cautions:
  - With no splitting mode set, Sherpa ends the process (`SHERPA_ONNX_EXIT`) instead of returning an error.
  - The words must be upper case for this model, because its 500 tokens are upper case.
- **A list can be given per utterance**, not only at load time (`SherpaOnnxCreateOnlineStreamWithHotwords`, phrases separated by `/`). A later context source (for example Wyoh's window titles) could therefore pass a different list to each dictation without reloading the model.

### What was set up

- `bpe.vocab`: the original training repository (`shaojieli/icefall-asr-commonvoice-fr-pruned-transducer-stateless7-streaming-2023-04-02`, Apache-2.0) publishes the tokenizer. Its `tokens.txt` is identical to Sherpa's, and its `unigram_500.vocab` (500 lines, piece and score) was copied beside the model as `bpe.vocab`, outside Git.
- `SherpaStreamingRecognizer` gained optional `hotwords`, `hotwords_score` and `beam_search` arguments. The default is unchanged (greedy, no list).

### Test on synthetic speech

`test/mycroft/test_hotwords.py` (contract `hotwords.feature`, marker `integration`) synthesises four French sentences, decodes them at 2 threads in four ways, and counts the known words found. Evidence: `results/mycroft/hotwords/20261011T202242Z/report.json`.

The voice is Piper's French "siwis" (CC-BY 4.0, outside Git). espeak-ng was tried first, but the model recognised almost nothing of its robotic voice (`…/hotwords/` first run), so it could not show anything.

| Sentence (spoken) | Greedy (today) | Beam search alone | Beam search + list (boost 1.5 or 3.0) |
| --- | --- | --- | --- |
| Bonjour, je m'appelle Michael et je travaille sur Luna. | **michael** … **luna** | same | same |
| Mycroft écoute pendant que Wyoh range les fenêtres. | croft … wi orange | same | **mycroft** … wyange |
| Ce soir, Michael lance Wolfenstein sur Luna. | **michael** **wolfenstein** **luna** | same | same |
| Demande à Mycroft d'ouvrir le terminal de Wyoh. | amicroft … will | same | amicroft … wy |
| Known words found | 5 / 9 | 5 / 9 | 6 / 9 |

What this shows:

1. **Michael, Luna and Wolfenstein were already recognised without a list**, at least in this voice.
2. **The list helps where the spelling matches the sound.** "Mycroft" became correct once, but "à Mycroft" stays glued as "amicroft".
3. **The list cannot fix a name pronounced unlike its French reading.** "Wyoh" is spoken roughly "ouaïo", but the list holds its spelling W-Y-O-H. It only pulls the text towards "wy…". The standard remedy is to list the **pronounced form** (for example "OUAÏO") and map it back to "Wyoh" after recognition. That map would be Mycroft's own small replacement table, because Sherpa's hotword list keeps no display spelling.
4. Beam search alone changed nothing here, and boost 3.0 gave the same result as 1.5.

**Limits:** one synthetic voice and four sentences. Step 9.4 would measure the real effect on the user's recorded voice. The cost of beam search on Luna (it does more work per frame than greedy) is not measured.

## 9.2 Lighter models: fine-tuning, one language, other models

### One language

**The current model is already French only.** It was trained on Common Voice French with 500 French tokens. Restricting it to one language gains nothing: its size comes from the network, not from languages. Sherpa's multilingual French-capable models (NVIDIA NeMo Canary and FastConformer, en/de/es/fr) are larger, not smaller (int8 archives of 100–150 MB).

### A smaller French model: Kroko

Sherpa's model release has a second streaming French model, **`sherpa-onnx-streaming-zipformer-fr-kroko-2025-08-06`** (Banafo "Kroko" community model):

| | Current model (2023-04-14) | Kroko French (2025-08-06) |
| --- | --- | --- |
| Archive | 398 MB | **57 MB** |
| Encoder file | 293 MB fp32, 127 MB int8 | **70 MB fp32** (no int8 file) |
| Parameters (estimated from the fp32 size) | ~73 million | **~18 million** (about 4× fewer) |
| Output | upper case, no punctuation | tokens include lower case, digits, `.`, `,` and `’`, so probably punctuated text |
| Licence | Apache-2.0 | README: "CC-BY-SA community models". Hugging Face metadata says "other", and the published `LICENSE` file is **empty**: to confirm. |

**Expected gain (estimates, not measured):**

- memory: roughly a third of today's ~250 MiB RSS;
- load time: roughly a quarter of today's ~17 s;
- speed: decoding about four times faster, so likely below real time on Luna at 2 threads (today RTF 1.32).

Its accuracy is unknown, as is how its tokens handle hotwords. Step 9.3 measures all of this.

### Fine-tuning on the user's voice

- **Possible on the current model:** the original repository publishes the PyTorch checkpoints (`exp/pretrained.pt`, `exp/epoch-30.pt`) and the training recipe (icefall), under Apache-2.0. It would make the model more accurate on the user's voice and vocabulary, but **not smaller or faster**. It needs a GPU desk machine, an icefall installation, and probably at least an hour of transcribed recordings of the user (an estimate).
- **Making a model smaller** means training or distilling a smaller network. That is a research project in its own right, well beyond hotwords or swapping in a model that is already small.
- **Fine-tuning Kroko:** Kroko publishes ONNX files and its own `.data` format, and its site offers training guides and paid custom models. A public PyTorch checkpoint for the French community model was not found, so fine-tuning it ourselves is unverified.
- The plan lists fine-tuning and speaker adaptation as v0 non-goals. Any of it needs a scope change.

## Recommendation

1. **9.3 first:** evaluate Kroko (licence, accuracy on the existing corpus and the representative recording, speed and memory on the desk host, then on Luna). It is the only option here that cuts memory and time at once.
2. **Known words:** use a list per dictation, plus a small table mapping pronounced forms to spellings for names like Wyoh. Measure on the user's voice (9.4).
3. **Fine-tuning:** only if 9.3 and 9.4 leave a gap. It doesn't solve the size problem.
