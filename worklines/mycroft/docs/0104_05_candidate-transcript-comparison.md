# Candidate transcript comparison: the actual Step 4 evidence

**Question answered:** Which voice samples were compared, what did each candidate actually say, and how was ground truth scored?

**Status:** transparency supplement to Step 4, 2026-09-25. It adds no new model run and does not turn the three-fixture smoke test into a French accuracy claim.

## Corpus actually used

The comparison used the three public French Common Voice WAV files distributed in the Sherpa French Zipformer archive. They were read from the archive's test_wavs directory outside the repository. The committed fixture manifest preserves their IDs and upstream reference transcripts; it does not retain audio.

| Fixture ID | Duration | Audio format | Ground truth |
| --- | ---: | --- | --- |
| common-voice-fr-19364697 | 7.128 s | mono, 16 kHz, signed 16-bit PCM WAV | CE SITE CONTIENT QUATRE TOMBEAUX DE LA DYNASTIE ACHÉMÉNIDE ET SEPT DES SASSANIDES |
| common-voice-fr-19738183 | 3.816 s | mono, 16 kHz, signed 16-bit PCM WAV | CE DERNIER A ÉVOLUÉ TOUT AU LONG DE L'HISTOIRE ROMAINE |
| common-voice-fr-27024649 | 6.336 s | mono, 16 kHz, signed 16-bit PCM WAV | SON ACTIONNAIRE MAJORITAIRE EST LE CONSEIL TERRITORIAL DE SAINT PIERRE ET MIQUELON |

These are upstream sample files, not a newly curated or held-out benchmark. They are useful to prove equal input handling and expose obvious failure modes, but they are too few and too closely associated with one candidate's model package to establish independent French WER or generalisation.

The later personal microphone captures were not part of this decision: the speaker improvised rather than reading the supplied reference, so a WER against that script would be invalid. They remain temporary, private qualitative diagnostics outside the repository.

## Equal conditions

- Host: four-core Intel i5-4590, Linux x86_64.
- One new local CPU process per candidate and fixture; two decoder threads; no GPU, network, prompt, hotword list, language-model injection, or context biasing.
- Sherpa-ONNX v1.13.8 with the French int8 streaming Zipformer. Whisper.cpp v1.9.4 with ggml-tiny-q5_1.bin and its language fixed to French.
- The harness validated the same input file before each run, retained raw stdout and stderr, then extracted the candidate's explicit transcript. Sherpa's structured transcript is emitted to stderr; Whisper's is emitted to stdout.

## Raw transcript comparison

| Fixture | Sherpa-ONNX French Zipformer | WER | Whisper.cpp Tiny q5_1 | WER |
| --- | --- | ---: | --- | ---: |
| 19364697 | CE SITE CONTIENT QUATRE TOMBEAUX DE LA DYNASTIE ASHÉMÉNIDE ET SEPT DES SASSANDIDES | 0.154 | Ce site contient quatre tombeaux de la dynastie à Cheménide et sept et s'assemblée. | 0.385 |
| 19738183 | CE DERNIER ÉVOLUE TOUT AU LONG DE L'HISTOIRE ROMAINE | 0.182 | Ce dernier voulait tout au long de l'histoire romaine. | 0.182 |
| 27024649 | SON ACTIONNAIRE MAJORITAIRE EST LE CONSEIL TERRITORIAL DE SAINT PIERRE ET MIQUELON | 0.000 | Son action est arme, j'ai été allé au conseiller de Saint-Pierre et Miccolon. | 0.833 |

The third clip is the decisive qualitative failure in this smoke test: Whisper Tiny q5_1 loses several content words and changes the sentence structure, whereas the French Zipformer is exact after normalisation. The same three rows also show why the result is provisional: short, clean clips can make a tiny sample look more decisive than it is.

## Ground-truth scoring

The committed runner uses ordinary word error rate (WER), computed as the minimum word-level edit distance divided by the number of reference words:

```text
WER = (substitutions + deletions + insertions) / reference word count
```

Before scoring, reference and hypothesis are normalised identically:

1. Unicode NFC normalisation.
2. Lowercasing.
3. Tokenisation into words; punctuation and whitespace are ignored.
4. Accented letters are retained. Therefore ÉVOLUÉ and ÉVOLUE are different words, while case and a final full stop are not errors.

The harness performs the Levenshtein dynamic-programming calculation in the standard library. It records the raw text beside the normalised score rather than hiding decoding artefacts. A missing reference or missing parsed transcript produces no quality score instead of an invented one.

Across these 36 reference words, Sherpa made 4 minimum-edit errors (micro-WER 0.111) and Whisper made 17 (micro-WER 0.472). These aggregates are descriptive only; the documented decision did not claim them as population accuracy.

## Reproduce and inspect

- Fixture manifest: worklines/mycroft/scripts/fixtures/public-french-smoke.json
- Scorer: worklines/mycroft/scripts/benchmark_asr.py, functions normalise and word_error_rate
- Full result JSON Lines: retained only under /tmp/tanstfaafllm-mycroft/ on the benchmark host, with raw commands, stdout, stderr, timing, and sampled RSS. They are deliberately not committed because they contain machine-local paths and are generated evidence.

## A useful external benchmark, with a TANSTAAFL warning

[Hugging Face Open ASR Leaderboard](https://huggingface.co/spaces/hf-audio/open_asr_leaderboard) is relevant external evidence. Its multilingual section publishes French results and its public benchmark uses FLEURS, Common Voice, and MLS. Its code, normaliser, evaluation configurations, and result locations are public in the [Open ASR Leaderboard repository](https://github.com/huggingface/open_asr_leaderboard).

Use it to screen candidates and to borrow a transparent evaluation protocol. Do not use its rank as a Luna deployment decision: its reproducible hosted evaluations run on an Nvidia H200 with 256 GB RAM and require a Hugging Face account, token, storage bucket, and paid Jobs. It measures model accuracy and throughput on that host, not ARM CPU memory, cold-start cost, or the 1 GiB Luna ledger.

At this review, a directly comparable public Gemma 3n/4 French row was not verified. A future attempt to submit or run a new model would be a new benchmark scope and needs an explicit plan revision and green light.
