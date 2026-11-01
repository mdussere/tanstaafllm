# English reading script: French-accented English for Mike (plan step 10.3)

> **Freshness:** 🟢 current · **Written:** 2026-11-01 · **Checked:** 2026-11-01 · **Step:** mycroft 10.3

**Status:** prepared; the recording waits for the user.
**Question answered:** how well do the English models of `1001_01` understand the user's French-accented English, on the words Mike will hear?

## Recording rules

- Read only the sentence after each number and long dash, in one continuous take, at your normal pace and with your normal accent. Do not try to sound English.
- Do not read headings, comments, numbers or the ground-truth section aloud.
- Leave a short pause between sentences; do not stop the recorder.
- Quiet room; the USB-C headset if possible, since it is Luna's microphone.
- Any format is fine (the phone's M4A too); the harness converts it to mono 16 kHz.
- **Consent and privacy:** the recording is used only for Mycroft's evaluation. It stays outside the repository, as the French reading did (`worklines/mycroft/data/.gitignore`).

To run the comparison afterwards:

    MYCROFT_ASSET_ROOT=… MYCROFT_PRIVATE_READING_EN=/path/to/reading.m4a \
      uv run pytest -m integration test/mycroft/test_candidates.py::test_english_candidates

## 01 — Luna and its apps

<!-- App names as Wyoh knows them, and window actions. -->
- **01.1** — Open the calculator and add twelve and thirty.
- **01.2** — Start Wolfenstein, then close the commander window.
- **01.3** — Open NetSurf and show me the Luna guide.
- **01.4** — Move the dino game to the left and make the terminal full screen.

## 02 — Commands

<!-- Command words, file names, safe actions. -->
- **02.1** — In the terminal, run git status and tell me which files changed.
- **02.2** — List the files in the music folder, but do not delete anything.
- **02.3** — How much memory is free, and is the battery charging?
- **02.4** — Show the last ten lines of the log file.

## 03 — Project words

<!-- Names from the novel and the project; the hardest words for the model. -->
- **03.1** — Mike, ask Mycroft to listen while Wyoh arranges the windows.
- **03.2** — Mannie and the Professor are working on Luna tonight.
- **03.3** — There ain't no such thing as a free lunch.

## 04 — Small talk

<!-- Ordinary connected speech. -->
- **04.1** — Good morning, Mike. What time is it?
- **04.2** — Thank you, that was quick. Can you say it again more slowly?
- **04.3** — I am not sure; what do you suggest?

## Canonical ground truth

Do not read this section during the recording. It is the exact reference transcript, in reading order.

> Open the calculator and add twelve and thirty.
> Start Wolfenstein, then close the commander window.
> Open NetSurf and show me the Luna guide.
> Move the dino game to the left and make the terminal full screen.
> In the terminal, run git status and tell me which files changed.
> List the files in the music folder, but do not delete anything.
> How much memory is free, and is the battery charging?
> Show the last ten lines of the log file.
> Mike, ask Mycroft to listen while Wyoh arranges the windows.
> Mannie and the Professor are working on Luna tonight.
> There ain't no such thing as a free lunch.
> Good morning, Mike. What time is it?
> Thank you, that was quick. Can you say it again more slowly?
> I am not sure; what do you suggest?
