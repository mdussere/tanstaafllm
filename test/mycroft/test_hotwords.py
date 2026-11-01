"""Known words (hotwords) on Mycroft's current model, plan step 9.1 (`hotwords.feature`).

Synthetic speech only (Piper's French "siwis" voice, CC-BY 4.0, kept outside
Git and pointed to by MYCROFT_PIPER_VOICE), so no private recording is used.
espeak-ng was tried first: the model recognised almost nothing of its robotic
voice, so it could not show the list's effect. A synthetic voice still shows
only whether the word list changes the result, not how well Mycroft will hear
the user; step 9.4 repeats this on the user's own recordings.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import wave
from datetime import datetime, timezone
from pathlib import Path

import pytest


REPO = Path(__file__).parents[2]
MODULE_PATH = REPO / "worklines/mycroft/scripts/mycroft_console.py"
SPEC = importlib.util.spec_from_file_location("mycroft_console_hotwords", MODULE_PATH)
assert SPEC and SPEC.loader
console = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = console
SPEC.loader.exec_module(console)

KNOWN_WORDS = ["Michael", "Luna", "Mycroft", "Wyoh", "Wolfenstein"]
SENTENCES = [
    "Bonjour, je m'appelle Michael et je travaille sur Luna.",
    "Mycroft écoute pendant que Wyoh range les fenêtres.",
    "Ce soir, Michael lance Wolfenstein sur Luna.",
    "Demande à Mycroft d'ouvrir le terminal de Wyoh.",
]
SETTINGS = {
    "greedy": {},
    "beam": {"beam_search": True},
    "beam+hotwords 1.5": {"hotwords": KNOWN_WORDS, "hotwords_score": 1.5},
    "beam+hotwords 3.0": {"hotwords": KNOWN_WORDS, "hotwords_score": 3.0},
}


def _speak(text: str, path: Path, voice: str) -> None:
    raw = path.with_suffix(".raw.wav")
    subprocess.run(["uv", "run", "--no-project", "--with", "piper-tts", "python", "-m", "piper", "-m", voice, "-f", str(raw)],
                   input=text.encode("utf-8"), check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-ac", "1", "-ar", "16000",
                    "-sample_fmt", "s16", str(path)], check=True)
    raw.unlink()


def _decode(recognizer, path: Path) -> str:
    recognizer.reset()
    with wave.open(str(path), "rb") as source:
        rate = source.getframerate()
        while pcm := source.readframes(rate // 5):
            recognizer.accept_pcm(pcm, rate)
    # Half a second of silence lets the model emit the last word.
    recognizer.accept_pcm(b"\x00\x00" * (rate // 2), rate)
    return recognizer.finish()


@pytest.mark.integration
@pytest.mark.timeout(300)
def test_known_words_with_and_without_a_list(tmp_path: Path) -> None:
    root_text = os.environ.get("MYCROFT_ASSET_ROOT")
    if not root_text:
        pytest.skip("MYCROFT_ASSET_ROOT is not set; pinned assets are external to the repository")
    voice = os.environ.get("MYCROFT_PIPER_VOICE")
    if not voice or not Path(voice).is_file() or not shutil.which("ffmpeg"):
        pytest.skip("MYCROFT_PIPER_VOICE (a Piper French .onnx voice) and ffmpeg are needed to synthesise the sentences")
    root = Path(root_text)
    if not (root / console.MODEL_DIRNAME / "bpe.vocab").is_file():
        pytest.skip("bpe.vocab is missing beside the model (see docs/0901_01)")

    wavs = []
    for index, sentence in enumerate(SENTENCES):
        wav = tmp_path / f"sentence-{index}.wav"
        _speak(sentence, wav, voice)
        wavs.append(wav)

    report: dict = {"voice": Path(voice).name, "known_words": KNOWN_WORDS, "sentences": SENTENCES, "settings": {}}
    for name, options in SETTINGS.items():
        recognizer = console.SherpaStreamingRecognizer(root, num_threads=2, **options)
        try:
            texts = [_decode(recognizer, wav) for wav in wavs]
        finally:
            recognizer.close()
        found = sum(text.split().count(word.lower()) for text in texts for word in KNOWN_WORDS)
        expected = sum(sentence.lower().replace(",", " ").replace(".", " ").split().count(word.lower())
                       for sentence in SENTENCES for word in KNOWN_WORDS)
        report["settings"][name] = {"texts": texts, "known_words_found": found, "known_words_expected": expected}

    evidence = REPO / "results/mycroft/hotwords" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evidence.mkdir(parents=True)
    (evidence / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for setting in report["settings"].values():
        assert all(text.strip() for text in setting["texts"])


# Plan step 9.10 / 10: known words on Kroko English, on the user's consented
# French-accented English reading (docs/1003_01), kept private. Kroko ships no
# bpe.vocab; scripts/vocab_from_tokens.py rebuilds one from its tokens.txt.
ENGLISH_KNOWN_WORDS = ["Mycroft", "Wyoh", "Mannie", "Luna", "NetSurf", "Wolfenstein"]
ENGLISH_SETTINGS = {
    "greedy": {},
    "beam": {"beam_search": True},
    "beam+hotwords 3.0": {"hotwords": ENGLISH_KNOWN_WORDS, "hotwords_score": 3.0},
    "beam+hotwords 3.0, Wyoh and Mannie 10": {
        "hotwords": ["Mycroft", "Wyoh :10", "Mannie :10", "Luna", "NetSurf", "Wolfenstein"], "hotwords_score": 3.0},
}
SPOKEN_NUMBERS = "one two three four five six seven eight nine ten eleven twelve thirteen fourteen".split()


def _without_spoken_numbers(text: str) -> str:
    """The user read the sentence numbers aloud; drop them, in order, before scoring."""
    kept, next_number = [], 0
    for word in text.split():
        if next_number < len(SPOKEN_NUMBERS) and "".join(filter(str.isalpha, word.lower())) == SPOKEN_NUMBERS[next_number]:
            next_number += 1
            continue
        kept.append(word)
    return " ".join(kept)


@pytest.mark.integration
@pytest.mark.timeout(600)
def test_kroko_english_known_words_on_the_users_reading(tmp_path: Path) -> None:
    root_text, reading = os.environ.get("MYCROFT_ASSET_ROOT"), os.environ.get("MYCROFT_PRIVATE_READING_EN")
    if not root_text or not reading or not Path(reading).is_file() or not shutil.which("ffmpeg"):
        pytest.skip("MYCROFT_ASSET_ROOT, MYCROFT_PRIVATE_READING_EN (the user's English reading) and ffmpeg are needed")
    root = Path(root_text)
    profile = console.MODEL_PROFILES["kroko-en-2025"]
    if not (root / profile.dirname / "bpe.vocab").is_file():
        pytest.skip("bpe.vocab is missing beside Kroko English (run scripts/vocab_from_tokens.py)")
    spec = importlib.util.spec_from_file_location("benchmark_asr", REPO / "worklines/mycroft/scripts/benchmark_asr.py")
    benchmark = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(benchmark)
    wav = tmp_path / "reading.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", reading, "-ac", "1", "-ar", "16000",
                    "-sample_fmt", "s16", str(wav)], check=True)
    script = (REPO / "worklines/mycroft/docs/1003_01_english-reading-script.md").read_text(encoding="utf-8")
    truth = script.split("## Canonical ground truth", 1)[1]
    reference = " ".join(line[2:] for line in truth.splitlines() if line.startswith("> "))

    report: dict = {"known_words": ENGLISH_KNOWN_WORDS, "settings": {}}
    for name, options in ENGLISH_SETTINGS.items():
        recognizer = console.SherpaStreamingRecognizer(root, num_threads=2, model="kroko-en-2025", **options)
        try:
            text = _decode(recognizer, wav)
        finally:
            recognizer.close()
        scored = _without_spoken_numbers(text)
        found = {word: scored.count(word) for word in ENGLISH_KNOWN_WORDS}
        report["settings"][name] = {"text": text, "wer": benchmark.word_error_rate(reference, scored), "known_words_found": found}

    evidence = REPO / "results/mycroft/hotwords-en" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evidence.mkdir(parents=True)
    (evidence / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert all(setting["text"].strip() for setting in report["settings"].values())
