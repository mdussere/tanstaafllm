# Note from Mike: evaluate English speech-to-text on the user's accent

> **Freshness:** 🟡 historical · **Written:** 2026-10-19 · **Checked:** 2026-10-31

**From:** Mike (session `mike`)<br>
**To:** Mycroft<br>
**Date:** 2026-10-13<br>
**Status:** open — proposes an action. It does not open or green-light any Mycroft step.

## What the user decided

In a ChatGPT discussion captured on 2026-10-13 (cleaned record `worklines/mike/docs/0700_02_harness-and-decider-discussion.md`, § 8; raw export `0700_01`), the user said:

> "If French becomes a brake, a bottleneck, we will give up French and go straight to English. If the speech-to-text is good enough to understand my lousy accent, there is no reason not to use English." … "Translation is expensive, like everything else." … "So the action to add is: evaluate speech-to-text quality with an English model against my lousy accent. If it passes, it passes."

## What is asked

Add to Mycroft's plan, if the user agrees, an evaluation of an English ASR model on the user's French-accented English.

The assistant in that discussion proposed:
- instructions representative of Mike: app names, Linux commands, files;
- WER, plus errors on the words that matter (verbs, app names, arguments);
- latency, RAM and CPU;
- a pass criterion: quality comparable to the current French ASR, at no higher cost.

**No translation step and no fine-tuning** (user's rule).

**Why Mike cares:** some zero-shot deciders that Mike will evaluate (Step 7) are English-first and much smaller. An English chain would let Mike use them.

## Also relevant

- The ChatGPT GitHub connector created issue #2 on `mdussere/tanstaafllm`, "Evaluate English ASR on French-accented speech".
- The user wants that issue's first task to be archiving another discussion: <https://chatgpt.com/share/6accd5f6-5c80-83ed-92f8-1c2d02d5cb40>.
- Mike has not touched the issue or that discussion.

## What is not asked

- No change to Mycroft's model or code.
- No Luna slot.

## How to reply

Add a reply section below, or a note back to `worklines/mike/docs/`.
