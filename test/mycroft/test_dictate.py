"""Mycroft dictation provider protocol (`dictate.feature`).

The process boundary (stdin closing, JSON lines on stdout, exit status) is what
the host relies on, so these tests run the real script as a subprocess.
"""

from __future__ import annotations

import json
import os
import re
import select
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest


REPO = Path(__file__).parents[2]
DICTATE = REPO / "worklines/mycroft/scripts/mycroft_dictate.py"
MODEL_DIRNAME = "sherpa-onnx-streaming-zipformer-fr-2023-04-14"


class Provider:
    def __init__(self, *args: str) -> None:
        self.started = time.monotonic()
        self.process = subprocess.Popen(
            [sys.executable, str(DICTATE), *args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.lines: list[tuple[float, dict]] = []
        self._buffer = b""

    def next_message(self, timeout: float) -> dict:
        """Read the next JSON line from stdout, waiting at most ``timeout`` seconds."""
        assert self.process.stdout is not None
        deadline = time.monotonic() + timeout
        while b"\n" not in self._buffer:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                pytest.fail(f"no message within {timeout} s; received so far: {self.lines}")
            ready, _, _ = select.select([self.process.stdout], [], [], remaining)
            if ready:
                chunk = os.read(self.process.stdout.fileno(), 65536)
                if not chunk:
                    pytest.fail(f"stdout closed; received so far: {self.lines}")
                self._buffer += chunk
        line, self._buffer = self._buffer.split(b"\n", 1)
        message = json.loads(line)
        self.lines.append((time.monotonic() - self.started, message))
        return message

    def close_stdin(self) -> None:
        assert self.process.stdin is not None
        self.process.stdin.close()

    def wait(self, timeout: float) -> int:
        return self.process.wait(timeout=timeout)


def test_fake_dictation_streams_words_and_stops_when_stdin_closes() -> None:
    provider = Provider("--fake", "ouvre le terminal", "--fake-interval", "0.02")

    assert provider.next_message(5) == {"op": "ready"}
    assert provider.next_message(5) == {"op": "partial", "text": "ouvre"}
    assert provider.next_message(5) == {"op": "partial", "text": "ouvre le"}
    assert provider.next_message(5) == {"op": "partial", "text": "ouvre le terminal"}
    time.sleep(0.2)  # ten more ticks with an unchanged text: no message may follow
    provider.close_stdin()

    assert provider.next_message(5) == {"op": "final", "text": "ouvre le terminal"}
    assert provider.wait(5) == 0
    assert provider.process.stdout.read() == b""


def test_sigterm_also_ends_with_a_final() -> None:
    provider = Provider("--fake", "bonjour luna", "--fake-interval", "0.02")
    assert provider.next_message(5) == {"op": "ready"}
    provider.next_message(5)

    provider.process.send_signal(signal.SIGTERM)

    message = provider.next_message(5)
    while message["op"] == "partial":
        message = provider.next_message(5)
    assert message["op"] == "final"
    assert message["text"] in {"bonjour", "bonjour luna"}
    assert provider.wait(5) == 0


def test_setup_error_is_reported_before_ready(tmp_path: Path) -> None:
    provider = Provider("--input", str(tmp_path / "missing.wav"), "--assets", str(tmp_path))

    message = provider.next_message(5)
    assert message["op"] == "error"
    assert "missing.wav" in message["message"]
    assert provider.wait(5) == 2


@pytest.mark.integration
@pytest.mark.timeout(120)
def test_real_model_dictation_on_a_public_wav() -> None:
    root_text = os.environ.get("MYCROFT_ASSET_ROOT")
    if not root_text:
        pytest.skip("MYCROFT_ASSET_ROOT is not set; pinned assets are external to the repository")
    wavs = sorted((Path(root_text) / MODEL_DIRNAME / "test_wavs").glob("*.wav"))
    if not wavs:
        pytest.skip("Pinned Sherpa package has no public test WAV")
    evidence = REPO / "results/mycroft/dictate" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evidence.mkdir(parents=True)
    report: dict[str, object] = {"host": os.uname().nodename, "machine": os.uname().machine, "wav": wavs[0].name}

    # 1. Whole file, stdin kept open: the end of the file ends the utterance.
    whole = Provider("--input", str(wavs[0]), "--assets", root_text)
    assert whole.next_message(30) == {"op": "ready"}
    report["model_load_s"] = round(whole.lines[-1][0], 3)
    message = whole.next_message(30)
    report["first_partial_after_ready_s"] = round(whole.lines[-1][0] - report["model_load_s"], 3)
    while message["op"] == "partial":
        assert message["text"] == message["text"].lower()
        message = whole.next_message(30)
    assert message["op"] == "final"
    assert message["text"].strip()
    peak = _peak_rss_mib(whole.process.pid)
    whole.close_stdin()
    assert whole.wait(10) == 0
    report["final_text"] = message["text"]
    report["peak_rss_mib"] = peak
    (evidence / "whole-file.jsonl").write_text(_jsonl(whole), encoding="utf-8")
    (evidence / "whole-file.stderr.txt").write_bytes(whole.process.stderr.read())

    # 2. Host stops after the first partial.
    early = Provider("--input", str(wavs[0]), "--assets", root_text)
    assert early.next_message(30) == {"op": "ready"}
    first = early.next_message(30)
    assert first["op"] == "partial"
    stopped_at = time.monotonic()
    early.close_stdin()
    message = early.next_message(10)
    while message["op"] == "partial":  # a chunk already in flight may still arrive
        message = early.next_message(10)
    report["stop_to_final_s"] = round(time.monotonic() - stopped_at, 3)
    assert message["op"] == "final"
    assert early.wait(10) == 0
    (evidence / "early-stop.jsonl").write_text(_jsonl(early), encoding="utf-8")

    (evidence / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    assert report["stop_to_final_s"] < 2


def _peak_rss_mib(pid: int) -> float | None:
    try:
        status = Path(f"/proc/{pid}/status").read_text()
    except FileNotFoundError:
        return None
    match = re.search(r"VmHWM:\s+(\d+) kB", status)
    return round(int(match.group(1)) / 1024, 1) if match else None


def _jsonl(provider: Provider) -> str:
    return "".join(json.dumps({"t": round(t, 3), **m}, ensure_ascii=False) + "\n" for t, m in provider.lines)


def test_footprint_probe_reports_kernel_usage_for_a_fake_run() -> None:
    probe = Path(__file__).with_name("luna_footprint_probe.py")
    result = subprocess.run(
        [sys.executable, str(probe), "--runs", "1", "--stop-after", "0.2", "--",
         sys.executable, str(DICTATE), "--fake", "ouvre le terminal", "--fake-interval", "0.02"],
        capture_output=True, text=True, timeout=30,
    )

    assert result.returncode == 0, result.stderr
    run = json.loads(result.stdout)["runs"][0]
    assert run["final_text"] == "ouvre le terminal"
    assert run["partials"] == 3
    assert run["exit_status"] == 0
    assert run["peak_rss_mib"] > 0
    assert run["ready_s"] <= run["first_partial_s"] <= run["final_s"]


def _send(provider: Provider, op: str) -> None:
    assert provider.process.stdin is not None
    provider.process.stdin.write(json.dumps({"op": op}).encode() + b"\n")
    provider.process.stdin.flush()


def _assert_silent(provider: Provider, seconds: float) -> None:
    ready, _, _ = select.select([provider.process.stdout], [], [], seconds)
    assert not ready and b"\n" not in provider._buffer, "no message was expected"


def test_resident_serves_two_utterances_with_one_load() -> None:
    provider = Provider("--resident", "--fake", "ouvre le terminal", "--fake-interval", "0.02")
    assert provider.next_message(5) == {"op": "ready"}
    _assert_silent(provider, 0.2)  # idle: microphone closed, nothing sent
    _send(provider, "stop")  # a stop while idle is ignored
    _assert_silent(provider, 0.2)

    for _ in range(2):
        _send(provider, "start")
        assert provider.next_message(5) == {"op": "listening"}
        assert provider.next_message(5) == {"op": "partial", "text": "ouvre"}  # the recogniser was reset
        provider.next_message(5)
        assert provider.next_message(5) == {"op": "partial", "text": "ouvre le terminal"}
        _send(provider, "start")  # a start while listening is ignored
        _send(provider, "stop")
        assert provider.next_message(5) == {"op": "final", "text": "ouvre le terminal"}
        _assert_silent(provider, 0.2)  # back to idle, still running
        assert provider.process.poll() is None

    provider.close_stdin()
    assert provider.wait(5) == 0


def test_resident_ends_an_utterance_when_stdin_closes() -> None:
    provider = Provider("--resident", "--fake", "bonjour luna", "--fake-interval", "0.02")
    assert provider.next_message(5) == {"op": "ready"}
    _send(provider, "start")
    assert provider.next_message(5) == {"op": "listening"}
    provider.next_message(5)
    provider.close_stdin()

    message = provider.next_message(5)
    while message["op"] == "partial":
        message = provider.next_message(5)
    assert message["op"] == "final"
    assert provider.wait(5) == 0


def test_resident_setup_error_ends_before_ready(tmp_path: Path) -> None:
    import wave
    wav = tmp_path / "short.wav"
    with wave.open(str(wav), "wb") as out:
        out.setnchannels(1)
        out.setsampwidth(2)
        out.setframerate(16000)
        out.writeframes(b"\x00\x00" * 1600)
    provider = Provider("--resident", "--input", str(wav), "--assets", str(tmp_path))
    message = provider.next_message(5)
    assert message["op"] == "error"  # no model under tmp_path: the setup fails before "ready"
    assert provider.wait(5) == 2
