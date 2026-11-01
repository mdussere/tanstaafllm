# Step 14.1–14.3 — The "flashlight embedding", measured on Termidor

> **Freshness:** 🟢 current · **Written:** 2026-11-01 · **Checked:** 2026-11-01 · **Step:** mike 14.3 ⏳

**Question answered:** which is the smallest, fastest embedding that serves both zero-shot routing of short English sentences and retrieval of short knowledge blocks from Luna's guide?<br>
**Answer, for review:** the Model2Vec static models all run in about 0.14 ms per sentence. Speed does not separate them, so the choice comes down to quality against memory:
- **POTION-4M** is the smallest that reaches the best routing score (81 %);
- it puts the right block in the top 3 for 80 % of the guide questions;
- its best score separates guide questions from outside questions with an AUC of 0.94;
- it takes 15 MB on disk and about 92 MiB for the whole Python process on the desk.

BM25 and TF-IDF are lighter, with no model at all, but route much worse (56–58 %). Nothing has run on Luna yet.

- **Go:** the user via Professor, 2026-11-01. Termidor only; nothing goes into Mike's conversation.
- **Test:** `test/mike/test_flashlight.py` (`integration`, `flashlight.feature`), with `flashlight_bench.py`, which measures each candidate in its own process.
- **Data:** `flashlight_data.json`:
  - 36 routing sentences in 6 labels: small talk, a question about the guide, a Luna action, weather, cooking, music;
  - 30 guide questions, each with its expected blocks;
  - 10 questions the guide does not answer.
- **Blocks:** `flashlight_blocks.py` cuts `docs/10`–`15` and the gamepad how-to into 65 prose blocks of 16–120 words, each cited as file, heading and part.
- **Evidence:** `results/mike/flashlight/20261101T163351Z/candidates.jsonl`.
- **Candidates:**
  - Model2Vec `minishlab/potion-base-2M`, `-4M` and `-8M`, and `potion-retrieval-32M` as a larger reference; MIT licence, weights in the Hugging Face cache, not in Git;
  - BM25 and TF-IDF, written in standard Python;
  - `model2vec` 0.10 is in the `embed` dependency group.

![Flashlight embedding candidates](../../../docs/img/mike-flashlight.png)

| Candidate | Disk | Process RSS | ms per sentence / per 100 words | Routing: description only / + 3 anchors | Retrieval top-1 / top-3 (of 30) | Guide vs outside: AUC / best threshold |
| --- | --- | --- | --- | --- | --- | --- |
| BM25 | — | 27 MiB | 0.13 / 0.58 | 31 % / 56 % | 13 / 22 | 0.87 / 85 % |
| TF-IDF | — | 27 MiB | 0.21 / 1.28 | 31 % / 58 % | 19 / 23 | 0.69 / 78 % |
| POTION-2M | 8 MB | 85 MiB | 0.14 / 0.38 | 72 % / 64 % | 16 / 21 | 0.90 / 90 % |
| **POTION-4M** | 15 MB | 92 MiB | 0.14 / 0.37 | 78 % / **81 %** | 19 / 24 | **0.94 / 95 %** |
| POTION-8M | 30 MB | 106 MiB | 0.14 / 0.36 | 78 % / 81 % | 20 / 23 | 0.95 / 95 % |
| POTION-retrieval-32M | 125 MB | 218 MiB | 0.15 / 0.39 | 86 % / 81 % | 23 / 25 | 0.96 / 93 % |

## What the numbers say

- **Speed is not the limit.**
  - Every candidate embeds a sentence in under a quarter of a millisecond on the desk, and a 100-word block in under 1.3 ms.
  - Loading POTION-4M takes 0.6 s, and indexing all 65 blocks takes 11 ms.
  - Luna's Cortex-A35 will be several times slower. That still leaves a large margin under "a few milliseconds", but it is not measured yet.
- **Memory is the cost.**
  - The figure is the whole process: Python and numpy alone take about 27 MiB, and `model2vec` with its tokenizer adds about 55 MiB before any weights.
  - A leaner runtime on Luna (numpy with the vocabulary table) should take less. To measure there.
- **Routing:**
  - The static models route far better than word overlap. Words do not tell "Do you like cats or dogs?" from a cooking question; vectors mostly do.
  - POTION-4M's 7 errors out of 36 are near-misses: "Launch the file manager" was taken for a guide question, and "How do I fix a game's buttons?" for a Luna action.
- **Retrieval:**
  - All candidates find the right block in the top 3 for 70–83 % of the guide questions.
  - The misses go to a neighbouring block on the same subject. For example, "What was gained by moving to Arch Linux ARM?" lands on "What we did" instead of "What it changed".
  - Blocks summarised offline, as the user plans, should help. This set used raw prose.
- **Out of domain:**
  - The static models' best score separates guide questions from outside ones well: AUC 0.94 for POTION-4M, with a threshold near 0.40 cosine. Its median top score is 0.57 for guide questions and 0.32 for outside ones.
  - This is a measurement only: no filter was built, as the user decided.
- **The set is small:** 36 routing sentences, 30 retrieval questions and 10 outside questions. One sentence is worth about 3 points. Differences of a few points between the POTION models are within that noise.

## Proposal (for Professor and the user)

- **Flashlight: POTION-4M.** It routes as well as 8M and 32M, separates the domains almost as well, and is half the size of 8M.
- **Next:**
  - 14.4: measure on Luna, warm and resident: milliseconds per sentence and RAM, with a numpy-only loader if `model2vec`'s dependencies are too heavy there.
  - A larger routing set, written with the user, before trusting a few points.
