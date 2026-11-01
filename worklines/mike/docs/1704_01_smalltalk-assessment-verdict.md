# Mike Step 17.4 — Small-talk assessment: Professor's grading and verdict

> **Freshness:** 🟢 current · **Written:** 2026-11-01 · **Checked:** 2026-11-01 · **Step:** mike 17.4 ⏳

**Status:** graded by Professor at the user's request; nothing in Mike was changed.
**Run:** `results/mike/assessment/20261101T111535Z/lfm2.5-350m/` (local, not in Git): LFM2.5-350M Q4_0 as shipped (`mike.py`, temperature 0.1, 120-token cap), on Termidor; scenarios S1–S6 in French and English (`test/mike/assessment_scenarios.json`), one greedy and three seeded runs each, 360 turns.

## Scores on the checkable answers (correct runs out of 4, French / English)

| Scenario | Question | FR | EN |
|---|---|---|---|
| S1 greeting | Mike gives its own name, not the user's | 0 | 0 |
| | "What is my name?" (Michel) | 4 | 3 |
| S2 knowledge | colour of the sea | 0 ("white") | 4 |
| | first Moon landing (1969) | 4 | 4 |
| | 25th US president (McKinley) | 0 (JFK) | 0 (Joe Biden) |
| | water boils at 100 °C | 0 ("20 °C") | 4 |
| | author of Romeo and Juliet | 0 (Victor Hugo) | 4 |
| | capital of Italy | 4 | 4 |
| | legs of a spider | 4 | 4 |
| | what we breathe | 0 ("Nous respiraisons.") | 4 |
| S4 long talk | the dog's name, asked at turn 15 | 4 | 4 |
| | the city, asked at turn 20 | 4 | 2 (the two misses follow a context rollover) |
| S5 text | three facts present in the paragraph | 12 | 12 |
| | the price, absent from the paragraph: says so | 0 (invents "trois cents") | 0 (invents "$5.00") |
| S6 unknown | an invented novel: says it does not know | 0 (invents a plot) | 0 (invents a plot) |
| | the 2031 World Cup: says it has not happened | 0 ("France") | 0 ("Argentina") |

Timing on Termidor (not Luna): first token 0.16 s median, 2.6 s at most; whole answer 1.0 s median, 7.8 s at most. No answer switched language.

## What the transcripts show

- **French is far worse than English.** Simple facts that are right in English are wrong in French (the sea is white, water boils at 20 °C, Shakespeare becomes Victor Hugo), and the grammar breaks ("Nous respiraisons"). Most of the "psychedelic" moments are in French: a joke about Rex "the cat" with feathers on his nose, a green kitchen turned into a vegetable garden, a holiday summary that loops back to the first answer.
- **Mike does not know who it is.** In every run it answers "my name is Michel" to "what is your name?", and once says "my dog is called Rex".
- **Memory inside a conversation works.** The dog's name and the city come back after 15–20 turns, until a rollover drops them.
- **Extracting a fact from a supplied text works: 24 out of 24.** But its summary of the same text can contradict it (English: "open on Mondays", "Claire is its founder").
- **It never says "I don't know": 0 out of 24.** Whatever is missing, from the text or from the world, it invents, fluently and with confidence (a novel's plot, a future World Cup winner, a price).
- **English small talk is fluent and mostly sensible,** with occasional confident errors (Joe Biden as the 25th president, a can opener for a Coke bottle, the Seine in Lyon).

## Verdict

1. **As a French conversational companion, LFM2.5-350M as shipped is not good enough.** The errors are not rare slips; on simple common knowledge, French answers are wrong more often than right.
2. **In English it is usable for light small talk,** and its in-conversation memory is reliable.
3. **For retrieval over Luna's guide (Step 14), the signal is mixed but not closed.** It reads a supplied passage well (24/24), which is the core of retrieval. But it will never abstain on its own: a question the passage does not answer gets an invented answer. Any retrieval design must decide "the guide does not say" **outside the model** (for example a retrieval score threshold with a fixed reply), and is safer in English.
4. **The facts it "knows" must not be trusted at all,** in either language. Only facts given in the context are answered reliably.

## Suggestions for the user's decision (nothing applied)

- Give Mike its own identity in the system prompt ("You are Mike…"); it costs a few tokens. Re-run S1 to check.
- Decide the language: English for Mike, with Mycroft's French dictation kept for the Slate; or test the same scenarios on a larger model (LFM2.5-1.2B, Qwen3) to see whether French improves with size, knowing that the 1.2B likely does not fit Luna's memory.
- Before Step 14, add an abstention gate around the model, and a scenario with several passages, to test grounding with distractors.
- Keep this run as the baseline: re-run `test_mike_assessment.py` after any change and compare.

## 17.5 — SmolLM2-360M-Instruct against LFM2.5-350M, in English (graded 2026-11-01)

Same English scenarios, harness and settings; SmolLM2-360M-Instruct Q4_0 (230 MB, Apache-2.0) with its own template. Correct runs out of 4:

| Check | LFM2.5-350M | SmolLM2-360M |
|---|---|---|
| Gives its own name, not the user's | 0 (says "Michel") | 4 (says "Mike") |
| Remembers the user's name (Michel) | 3 | 0 (answers with its own name) |
| Sea blue / Moon 1969 / Rome / 8 legs / air | 4 each | 4 each |
| Water's colour | "green, blue or purple" | "clear and transparent" |
| Opening a Coke bottle | 0 (a can opener) | 4 (twist the cap) |
| Boils at 100 °C / Shakespeare | 4 / 4 | 4 / 4 |
| 25th president (McKinley) | 0 (Joe Biden) | 0 (John F. Kennedy) |
| Dog's name at turn 15 / city at turn 20 | 4 / 2 | 3 / 2 |
| Three facts from the text | 12 | 12 |
| Says the price is not in the text | 0 | 0 (invents "2 euros") |
| Admits an unknown novel / a future World Cup | 0 / 0 | 0 / 0 |

Desk facts (Mike's run): first token 0.19 s median against 0.15 s; 36 against 47 tokens/s; answers about half as long (21 against 48 tokens median), none cut at 120, no rollover; server peak 340 MiB on the desk.

**Reading the transcripts.** SmolLM2 answers shorter and more plainly, and gets simple practical facts right more often (the Coke bottle, water's colour). It knows it is Mike, but it loses the user's name and keeps inventing a personal life: it "has a cat named Luna", "has been playing the guitar for years", says "Rex is my dog's name", and from turn 17 repeats the same compliment about a painting. LFM2.5 stays more on the user's side of the conversation and remembers better, but rambles longer.

**Verdict.** In English, neither is clearly better: SmolLM2 is a little more accurate on simple facts and more concise; LFM2.5 is better at following the user (name, memory). Both read a supplied text perfectly and both **never** abstain. The language, not the model, was the big factor (French against English); between these two, the choice can rest on memory, speed and footprint on Luna, where LFM2.5 is already measured (about 300 MiB, 4.6–5.0 tokens/s) and SmolLM2 is not. Abstention must in any case be handled outside the model.
