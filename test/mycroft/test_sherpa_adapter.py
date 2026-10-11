"""Optional evidence test for the one pinned Sherpa streaming adapter.

Run only with externally installed assets. The test fixture is upstream public
model audio; it neither downloads assets nor writes an audio copy.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import wave
from pathlib import Path

import pytest


MODULE_PATH = Path(__file__).parents[2] / "worklines/mycroft/scripts/mycroft_console.py"
SPEC = importlib.util.spec_from_file_location("mycroft_console_adapter", MODULE_PATH)
assert SPEC and SPEC.loader
console = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = console
SPEC.loader.exec_module(console)


@pytest.mark.integration
def test_pinned_sherpa_adapter_emits_a_streaming_result() -> None:
    root_text = os.environ.get("MYCROFT_ASSET_ROOT")
    if not root_text:
        pytest.skip("MYCROFT_ASSET_ROOT is not set; pinned assets are external to the repository")
    root = Path(root_text)
    wavs = sorted((root / console.MODEL_DIRNAME / "test_wavs").glob("*.wav"))
    if not wavs:
        pytest.skip("Pinned Sherpa package has no public test WAV")

    recognizer = console.SherpaStreamingRecognizer(root)
    try:
        with wave.open(str(wavs[0]), "rb") as source:
            assert source.getnchannels() == 1
            assert source.getsampwidth() == 2
            while pcm := source.readframes(3200):
                recognizer.accept_pcm(pcm, source.getframerate())
        result = recognizer.finish()
    finally:
        recognizer.close()

    assert result.strip(), "The pinned adapter must expose a non-empty final transcript."

@pytest.mark.integration
def test_replay_and_console_share_the_streaming_composition_flow() -> None:
    """Public WAV: replay EOF must have Space-stop semantics and accept only after edit."""
    root_text = os.environ.get("MYCROFT_ASSET_ROOT")
    if not root_text:
        pytest.skip("MYCROFT_ASSET_ROOT is not set; pinned assets are external to the repository")
    root = Path(root_text)
    wavs = sorted((root / console.MODEL_DIRNAME / "test_wavs").glob("*.wav"))
    if not wavs:
        pytest.skip("Pinned Sherpa package has no public test WAV")

    emitted: list[str] = []
    app = console.TerminalConsole(wavs[0], root, emitted.append)
    app._start()
    assert app.controller.state.phase is console.Phase.RECORDING
    assert isinstance(app.source, console.ReplaySource)
    app.source._next_at = 0.0  # Fast deterministic replay: no wall-clock wait in pytest.

    for _ in range(200):
        app.tick()
        if app.controller.state.phase is console.Phase.STOPPED_DRAFT:
            break
    else:
        pytest.fail("Replay did not reach its single EOF finalisation")

    automatic = app.controller.state.draft
    assert automatic.strip()
    app.action("end")
    app.action("!")
    app.action("enter")
    assert emitted == [automatic + "!"]
    assert app.controller.state.phase is console.Phase.ACCEPTED
