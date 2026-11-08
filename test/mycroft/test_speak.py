"""Mycroft's speech provider (plan step 12): protocol, sentence pipeline, stop.

The default tests use a fake voice and a fake player; the integration test loads
Piper Lessac (MYCROFT_ASSET_ROOT with the voice and Sherpa's full runtime).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
import wave
from pathlib import Path

import pytest

REPO = Path(__file__).parents[2]
SPEAK = REPO / "worklines/mycroft/scripts/mycroft_speak.py"
sys.path.insert(0, str(SPEAK.parent))
import mycroft_speak as speak  # noqa: E402


class RecordingPlayer:
    def __init__(self, seconds: float = 0.0) -> None:
        self.played: list[int] = []
        self.seconds = seconds
        self._stop = threading.Event()

    def play(self, pcm: bytes, sample_rate: int) -> None:
        self.played.append(len(pcm))
        self._stop.clear()
        self._stop.wait(self.seconds)

    def stop(self) -> None:
        self._stop.set()


def _serve(lines, voice=None, player=None) -> list[dict]:
    events: list[dict] = []
    lock = threading.Lock()

    def emit(op: str, **fields: object) -> None:
        with lock:
            events.append({"op": op, **fields})

    assert speak.serve(voice or speak.FakeVoice(), player or RecordingPlayer(), emit, lines) == 0
    return events


def test_sentences_split_on_end_punctuation() -> None:
    assert speak.split_sentences(" Hello there.  How are you? Fine; thanks! ") == ["Hello there.", "How are you?", "Fine;", "thanks!"]
    assert speak.split_sentences("   ") == []
    assert speak.split_sentences("No full stop") == ["No full stop"]


def test_a_reply_is_spoken_sentence_by_sentence_then_marked_spoken() -> None:
    events = _serve(['{"op": "say", "text": "One. Two. Three."}'])
    assert [e["op"] for e in events] == ["speaking", "speaking", "speaking", "spoken"]
    assert [e["text"] for e in events[:3]] == ["One.", "Two.", "Three."]
    assert events[-1] == {"op": "spoken", "id": 1}


def test_two_replies_are_queued_in_order() -> None:
    events = _serve(['{"op": "say", "text": "First."}', '{"op": "say", "text": "Second."}', "not json", '{"op": "say", "text": ""}'])
    assert [(e["op"], e["id"]) for e in events] == [("speaking", 1), ("spoken", 1), ("speaking", 2), ("spoken", 2)]


def test_the_next_sentence_is_synthesised_while_one_plays() -> None:
    """With synthesis and playback both 0.2 s, three sentences take ~0.8 s, not 1.2 s."""
    started = time.monotonic()
    _serve(['{"op": "say", "text": "One. Two. Three."}'], speak.FakeVoice(0.2), RecordingPlayer(0.2))
    assert time.monotonic() - started < 1.05


def test_stop_cuts_the_reply_and_drops_the_rest() -> None:
    read_fd, write_fd = os.pipe()
    reader = os.fdopen(read_fd, "r")
    player = RecordingPlayer(5.0)  # each sentence "plays" for 5 s unless stopped
    events: list[dict] = []
    done = threading.Event()

    def emit(op: str, **fields: object) -> None:
        events.append({"op": op, **fields})

    def run() -> None:
        speak.serve(speak.FakeVoice(), player, emit, reader)
        done.set()

    threading.Thread(target=run, daemon=True).start()
    os.write(write_fd, b'{"op": "say", "text": "One. Two. Three."}\n')
    time.sleep(0.3)
    os.write(write_fd, b'{"op": "stop"}\n')
    os.close(write_fd)
    assert done.wait(3.0), "stop should end playback at once"
    ops = [e["op"] for e in events]
    assert "stopped" in ops and "spoken" not in ops
    assert len(player.played) == 1


def test_the_process_speaks_with_a_fake_voice(tmp_path: Path) -> None:
    result = subprocess.run([sys.executable, str(SPEAK), "--fake", "--wav-dir", str(tmp_path)],
                            input=b'{"op": "say", "text": "Hello. Bye."}\n', capture_output=True, timeout=20)
    lines = [json.loads(line) for line in result.stdout.decode().splitlines()]
    assert result.returncode == 0
    assert lines[0] == {"op": "ready", "sample_rate": 16000} and lines[-1] == {"op": "spoken", "id": 1}
    assert sorted(p.name for p in tmp_path.iterdir()) == ["000.wav", "001.wav"]


def test_missing_assets_are_a_setup_error(tmp_path: Path) -> None:
    result = subprocess.run([sys.executable, str(SPEAK), "--assets", str(tmp_path)], input=b"", capture_output=True, timeout=20)
    assert result.returncode == speak.EXIT_SETUP_ERROR
    assert json.loads(result.stdout)["op"] == "error"


@pytest.mark.integration
def test_piper_lessac_speaks_a_reply(tmp_path: Path) -> None:
    root = os.environ.get("MYCROFT_ASSET_ROOT")
    if not root:
        pytest.skip("set MYCROFT_ASSET_ROOT to the Piper voice and Sherpa's full runtime")
    started = time.monotonic()
    process = subprocess.Popen([sys.executable, str(SPEAK), "--assets", root, "--wav-dir", str(tmp_path)],
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    assert process.stdin and process.stdout
    ready = json.loads(process.stdout.readline())
    loaded = time.monotonic()
    process.stdin.write(b'{"op": "say", "text": "Good morning. The battery is at eighty percent."}\n')
    process.stdin.flush()
    first = json.loads(process.stdout.readline())
    first_sound = time.monotonic()
    process.stdin.close()
    rest = [json.loads(line) for line in process.stdout]
    assert process.wait(60) == 0
    assert ready["op"] == "ready" and first["op"] == "speaking" and rest[-1] == {"op": "spoken", "id": 1}
    with wave.open(str(tmp_path / "001.wav")) as audio:
        assert audio.getframerate() == ready["sample_rate"] and audio.getnframes() > ready["sample_rate"]
    print(f"load {loaded - started:.1f} s, first sound {first_sound - loaded:.2f} s after the text")
