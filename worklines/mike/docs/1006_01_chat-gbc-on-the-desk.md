# Step 10.6 — Chat-GBC reproduced on the desk host

> **Freshness:** 🟡 historical · **Written:** 2026-10-30 · **Checked:** 2026-10-31 · **Step:** mike 10.6 ✅

**Question answered:** does Chat-GBC (a transformer of 21k–138k parameters that runs on a 1989 Game Boy) do what its README says, run on Termidor without the ROM or an emulator, and what does it mean for Mike?<br>
**Date:** 2026-10-29<br>
**Status:** measured on Termidor only (user request, 2026-10-29: "look at it and try to reproduce it on Termidor, not in an emulator").
- **Source:** github.com/rudydel/Chat-GBC, commit `db83f9b` (2026-09-16), cloned under `mike-tools/chat-gbc/src`. A private venv holds PyTorch 2.15 (the CUDA build was installed, 5.2 GB, outside the repository; the CPU build would do).
- **Test:** `test/mike/test_chat_gbc.py` (`integration`, `chat_gbc.feature`). **Evidence:** `results/mike/chat-gbc/20261029T131848Z/` (every command's full output, `summary.jsonl`, `chat.jsonl`).
- **Not run:** its training (`make train`, `make finetune`), because Mike's non-goal excludes training; the ROM; the emulator.

## Summary

- **Its numbers reproduce exactly.** The project's own evaluation, run on its shipped checkpoints, gives the same figures as each model's training log, per source file, for the float model and for the bit-exact integer simulator (the arithmetic the Game Boy runs): 4 of 4 runs identical.
- **What the model is:** a specialist trained on 405 Game Boy question–answer pairs. It recites what it learned (100 % of training questions) and declines most other questions with "sorry, i only know about the game boy".
- **It generalises little:** 32 % (tiny) and 40 % (micro) of held-out phrasings of known facts are answered exactly.
- **For Mike:** it shows that a model of about 100k parameters can run on almost nothing, but only after **training on the task**. It is far below the 90 % gate on new phrasings, and training is outside Mike's scope today.

## Evaluation (`llm.evaluate`, held-out share 0.2, seed 0, as in training)

| Model | Parameters (README) | Mode | Training questions (80) | Held-out facts (103) | Held-out off-topic declined (41) | Same as its log |
| --- | --- | --- | --- | --- | --- | --- |
| tiny | 62k | float | 99 % | 32 % | 83 % | yes |
| tiny | 62k | integer (Game Boy) | 100 % | **32 %** | **73 %** | yes |
| micro | 136k | float | 100 % | 38 % | 83 % | yes |
| micro | 136k | integer (Game Boy) | 100 % | **40 %** | **80 %** | yes |

The README's figures (32 % and 73 % for tiny, 40 % and 80 % for micro) are the integer rows.

## Questions (`llm.chat -q`, greedy)

| Question | tiny and micro, float and integer |
| --- | --- |
| who designed the game boy | gunpei yokoi and nintendo r&d1 |
| what cpu does the game boy use | a sharp lr35902, an 8-bit chip similar to the z80 |
| what is the capital of france | sorry, i only know about the game boy |
| ouvre la calculatrice | sorry, i only know about the game boy |
| open the calculator | sorry, i only know about the game boy |

- **Time:** 2–3 s per question in integer mode, almost all of it Python and PyTorch start-up; the float runs took up to 28 s while Step 10's qualification series used the CPU. These are not speed measurements of the model.
- **Speed on the Game Boy (README, not measured here):** about one character per second on a DMG.

## What it means for Mike

- **Size is not the obstacle for a narrow task.** A trained specialist of this size answers its own task instantly on any CPU, Luna's included.
- **But it is a trained specialist.** Mike would need its own training data (requests → one of six tool calls) and a training run. That contradicts Mike's non-goal "no training of any kind"; only the user can lift it.
- **And it still generalises poorly:** 32–40 % on new phrasings, against the 90 % gate. Mike's held-out set is exactly that test.
- **Possible use, if the user ever allows training:** a tiny classifier trained on Mike's requests, with the "sorry" answer as the `none` case.
