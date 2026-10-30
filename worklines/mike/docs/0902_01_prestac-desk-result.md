# Step 9.2 — PreStaC on the desk host: result

**Question answered:** does the Prefetch Stack Cache work, how much of the prompt does it restore, and what does it change in time and answers?<br>
**Date:** 2026-10-29<br>
**Status:** measured on the desk host Termidor only (green light: the user, 2026-10-29). Nothing ran on Luna.
- **Setup:** LFM2.5-350M Q4_0, `llama-server` b11429, lean (`--no-repack -b 16 -ub 16`), context 2,048, one slot, `--slot-save-path`.
- **Evidence:** `results/mike/prestac-desk/20261029T073748Z/`: `navigation.json` holds every question; `same_answers.json`; the server log.
- **Code:** `src/mike/prestac.py` (store, engine, stack; study `docs/0901_01` § 5) and `test/mike/prestac_layers.py`.
- **Tests:** `test/mike/test_prestac.py` (9 deterministic tests, fake engine) and `test/mike/test_prestac_desk.py` (`integration`, `prestac_desk.feature`).

## Summary

- **PreStaC restores 98.3 % of all prompt tokens** along a navigation path of 117 questions, and at least 97.1 % for any single question. The target was 95 %.
- **Per question, it reads a median of 18 tokens** and at most 32, instead of 682 (the Luna run of 4.5) or 1,081 (no cache). The question itself and the turn around it are about 16 of those tokens.
- **The cache does not change the answers:** 28 of 28 sampled requests gave the same text through PreStaC and with no cache at all.
- **On the desk host, question to answer** takes a median of 0.32 s (at most 0.70 s), against 3.3–5.6 s per request in 3b.1.
- **Background work for the whole path:** 11 frames computed (L0, five desktops, and terminal layers), 1,246 tokens read in 7.9 s. Frames reused by restores: 9.
- **The state file grows with the context:** about 12.4 KB per token, so **13.0 MB for L0 (1,053 tokens)** and up to 13.5 MB per frame here. It is not a fixed size.
- **But the new layer order lowers the scores.** Moving the desktop after the tool JSON, which L0 requires, gives 45/81 main and 15/31 held-out with the adapter, against 55/81 and 16/31 with prompt v4's order (3b.1, same model and setting). That is a layer-design question, for 9.4.

## The path

- **Route:** the 112 evaluation requests, grouped by their five desktops. Each desktop is visited once, then the first one again with 5 questions.
- **Terminal layer:** on each desktop, from the fourth question on, the user "opens the terminal", which pushes a layer ("The terminal's working directory is ~/git/tanstfaafllm; its last command was `ls`."). At the sixth question, the layer is popped.
- **Early questions:** on every other desktop, the first question is asked at once, without waiting for the prefetch. The cache starts cold, with no frames on disk.

| Measure | Value |
| --- | --- |
| Questions | 117 |
| Prompt tokens, all questions | 127,358 |
| Restored from frames | 125,207 (**98.3 %**) |
| Read at question time | 2,151 (median 18, maximum 32 per question) |
| Question → answer | median 0.32 s, maximum 0.70 s |
| Frames computed in the background | 11; 1,246 tokens; 7.9 s |
| Restores of an existing frame by the prefetcher | 9 |
| Chunks abandoned (a stale frame) | 0 on this path |

**Early questions** (asked before the desktop frame was ready): L0 was ready, so they restored 1,053–1,068 tokens and read 17–32, in 0.29–0.47 s. A question asked during prefetch waits for at most one chunk of 64 tokens.

**With the terminal layer** (10 questions): 1,090–1,094 tokens restored, 16–20 read, 0.27–0.43 s.

## Answers and scores

| Order of the prompt | Main, model / adapter | Held-out, model / adapter |
| --- | --- | --- |
| Prompt v4 (desktop before the tool JSON), 3b.1, no cache | 44 / 55 | 12 / 16 |
| PreStaC L0 + desktop after the tool JSON (this run) | 35 / 45 | 10 / 15 |

- **The cache itself is neutral:** with the same token ids, the restored frames and a fresh read give the same answers.
- **The loss comes from moving the desktop after the 657-token tool JSON.** The model sees the open windows far from its instructions and its examples.
- **Options for 9.4** (to measure):
  1. Put the desktop in the user turn, as prompt v3 did. It would cost about 13 more tokens read per question, but L0 stays the same.
  2. Drop or shorten the tool JSON. The grammar already forces the call's shape, which would bring the desktop back next to the instructions.
  3. Repeat the verb table after the tool JSON.

## What this settles from the study's open questions (`0901_01` § 11)

| # | Question | Answer |
| --- | --- | --- |
| 1 | Does `extend` (`n_predict: 0`) leave exactly the frame's state? | **Yes:** frames restored later match their token count, and the answers equal a fresh read (28/28) |
| 2 | Does closing the HTTP request cancel a read? | Not tested. Reads are chunked (64 tokens), so a stale prefetch stops between chunks; on Luna a chunk is about 10 s (estimate) |
| 4 | State size against tokens | **About 12.4 KB per token**, close to linear: 4.8 MB at 400 tokens (3b), 13.0 MB at 1,053 |
| 3, 5 | Restore time and the reading speed of a short question after a long restored context, on Luna | for 9.3 |
| 6 | What Wyoh can tell Mike | not tested here (simulated layers) |
| 7 | Write time and wear of the SD card | for 9.3 |

## What it means for Luna (estimate, to measure in 9.3)

**Per question, from 4.5's speeds:**
- 18 tokens read ≈ 2.7 s;
- about 11 tokens written ≈ 3.3 s;
- plus restoring a 13 MB file from the SD card (not measured);
- so **about 6–7 s**, against about 105 s in 4.5.

**Building L0** (1,053 tokens) takes about 2.5 minutes once per model and runtime, then lives on disk. A new desktop frame is about 15 tokens, about 2 s.

**Disk:** a 200 MB budget holds about 15 frames of this size.

## Next

- **9.3:** the same path on Luna, through Professor and Mannie, to measure restore time, per-question time and SD-card writes.
- **9.4:** the layer order and the tool JSON, measured on the 112 requests, to get back at least the scores of prompt v4.
