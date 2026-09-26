"""Deterministic Mycroft v0 console tests.

No test here needs a microphone, a model asset, a network connection, or a
private recording. The optional pinned-runtime adapter test is deliberately
separate so a normal checkout remains light.
"""

from __future__ import annotations

import importlib.util
import sys
import wave
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).parents[2] / "worklines/mycroft/scripts/mycroft_console.py"
SPEC = importlib.util.spec_from_file_location("mycroft_console", MODULE_PATH)
assert SPEC and SPEC.loader
console = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = console
SPEC.loader.exec_module(console)


def test_manual_edit_owns_draft_after_stop() -> None:
    controller = console.DraftController()
    controller.start("replay fixture.wav")
    controller.hypothesis("bonjour luna")
    controller.stop("bonjour luna")
    controller.edit("end")
    controller.edit("!")
    controller.hypothesis("a later recogniser update")

    assert controller.state.draft == "bonjour luna!"
    assert controller.state.hypothesis == "bonjour luna"
    assert controller.state.phase is console.Phase.STOPPED_DRAFT


def test_accept_emits_exact_draft_once() -> None:
    emitted: list[str] = []
    controller = console.DraftController(emitted.append)
    controller.start("replay fixture.wav")
    controller.stop("raw output")
    controller.edit("end")
    controller.edit("!")

    assert controller.accept() is True
    assert controller.accept() is False
    assert emitted == ["raw output!"]
    assert controller.state.phase is console.Phase.ACCEPTED


def test_discard_never_emits_and_stops_recording() -> None:
    emitted: list[str] = []
    controller = console.DraftController(emitted.append)
    controller.start("microphone /dev/snd/pcmC0D0c")
    controller.hypothesis("do not keep this")

    assert controller.discard() is True
    assert emitted == []
    assert controller.state.phase is console.Phase.DISCARDED
    assert controller.state.draft == ""
    assert controller.state.hypothesis == ""


def test_invalid_actions_do_not_change_the_state() -> None:
    controller = console.DraftController()

    assert controller.stop() is False
    assert controller.accept() is False
    assert controller.state.phase is console.Phase.IDLE
    controller.start("replay fixture.wav")
    assert controller.accept() is False
    assert controller.state.phase is console.Phase.RECORDING


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("\x1b[15~", ["f5"]),
        ("\x1b[17~", ["f6"]),
        ("\x1b[D", ["left"]),
        ("\r", ["enter"]),
        ("\x7f", ["backspace"]),
        ("x", ["x"]),
    ],
)
def test_key_decoder_maps_documented_terminal_sequences(raw: str, expected: list[str]) -> None:
    assert console.KeyDecoder().feed(raw) == expected


def test_renderer_snapshot_is_terminal_independent() -> None:
    controller = console.DraftController()
    controller.start("replay fixture.wav")
    controller.hypothesis("bonjour")

    snapshot = console.render_snapshot(controller.state)

    assert "State: recording | Source: replay fixture.wav" in snapshot
    assert "Draft:\nbonjour" in snapshot
    assert "ASR hypothesis:\nbonjour" in snapshot
    assert "\x1b" not in snapshot


def _write_mono_wav(path: Path, frames: bytes, sample_rate: int = 10) -> None:
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(frames)


def test_replay_source_delivers_time_ordered_chunks_and_single_eof(tmp_path: Path) -> None:
    path = tmp_path / "fixture.wav"
    _write_mono_wav(path, b"\x00\x00" * 5, sample_rate=10)
    source = console.ReplaySource(path, chunk_ms=200)
    source._next_at = 10.0  # deterministic clock seam; no wall-clock sleep

    assert source.poll(9.9) is None
    assert source.poll(10.0) == b"\x00\x00" * 2
    assert source.poll(10.1) is None
    assert source.poll(10.2) == b"\x00\x00" * 2
    assert source.poll(10.4) == b"\x00\x00"
    assert source.poll(10.5) == b""
    assert source.poll(10.6) is None
    source.close()


def test_replay_rejects_non_mono_pcm_before_a_session(tmp_path: Path) -> None:
    path = tmp_path / "stereo.wav"
    with wave.open(str(path), "wb") as output:
        output.setnchannels(2)
        output.setsampwidth(2)
        output.setframerate(16000)
        output.writeframes(b"\x00\x00" * 4)

    with pytest.raises(console.ConsoleError, match="16-bit mono PCM"):
        console.ReplaySource(path)


def test_capture_path_is_mapped_only_for_a_real_capture_node(tmp_path: Path) -> None:
    fake = tmp_path / "pcmC0D0c"
    fake.write_bytes(b"")

    with pytest.raises(console.ConsoleError, match="capture PCM node"):
        console.AlsaCaptureSource(fake)

def test_default_asset_root_is_the_repository_local_installation_slot(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MYCROFT_ASSET_ROOT", raising=False)
    expected = Path(__file__).parents[2] / ".mycroft-assets"
    assert console.default_asset_root() == expected
