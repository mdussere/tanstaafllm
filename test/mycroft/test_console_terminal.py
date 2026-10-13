"""Real-terminal evidence for the Mycroft v0 console (`console_terminal.feature`).

The console program itself is the boundary under test, so it runs as a child
process on a pseudo-terminal and `pyte` emulates the screen the user would
see. Needs the externally installed pinned assets; reads only the model's
public test WAVs.
"""

from __future__ import annotations

import fcntl
import os
import pty
import re
import select
import struct
import sys
import termios
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import pyte
import pytest


REPO = Path(__file__).parents[2]
CONSOLE = REPO / "worklines/mycroft/scripts/mycroft_console.py"
MODEL_DIRNAME = "sherpa-onnx-streaming-zipformer-fr-2023-04-14"
COLUMNS, ROWS = 80, 24
SPACE, ESC = b" ", b"\x1b"
LEAVE_ALT_SCREEN = b"\x1b[?1049l"


class PtyConsole:
    def __init__(self, wav: Path, asset_root: Path, evidence: Path) -> None:
        self.screen = pyte.Screen(COLUMNS, ROWS)
        self.stream = pyte.ByteStream(self.screen)
        self.raw = bytearray()
        self.evidence = evidence
        self.frames = 0
        self.pid, self.fd = pty.fork()
        if self.pid == 0:  # child: size the terminal, then become the console
            fcntl.ioctl(0, termios.TIOCSWINSZ, struct.pack("HHHH", ROWS, COLUMNS, 0, 0))
            os.environ.update(MYCROFT_ASSET_ROOT=str(asset_root), TERM="xterm")
            os.execv(sys.executable, [sys.executable, str(CONSOLE), "--input", str(wav)])

    def pump(self, seconds: float) -> None:
        deadline = time.monotonic() + seconds
        while (remaining := deadline - time.monotonic()) > 0:
            ready, _, _ = select.select([self.fd], [], [], min(remaining, 0.02))
            if not ready:
                continue
            try:
                data = os.read(self.fd, 65536)
            except OSError:  # child closed the terminal
                return
            self.raw.extend(data)
            self.stream.feed(data)

    def text(self) -> str:
        return "\n".join(line.rstrip() for line in self.screen.display)

    def wait_for(self, predicate: Callable[[], bool], timeout: float, what: str) -> None:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate():
                return
            self.pump(0.05)
        self.snapshot(f"timeout-{what}")
        pytest.fail(f"Timed out after {timeout} s waiting for {what}:\n{self.text()}")

    def press(self, keys: bytes) -> None:
        os.write(self.fd, keys)

    def snapshot(self, name: str) -> str:
        self.frames += 1
        text = self.text()
        (self.evidence / f"{self.frames:02d}-{name}.txt").write_text(text + "\n", encoding="utf-8")
        return text

    def wait_exit(self, timeout: float) -> int:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.pump(0.05)
            pid, status = os.waitpid(self.pid, os.WNOHANG)
            if pid:
                self.pump(0.2)
                return os.waitstatus_to_exitcode(status)
        os.kill(self.pid, 9)
        pytest.fail("Console did not exit")


@pytest.mark.integration
@pytest.mark.timeout(120)
def test_console_in_a_real_terminal() -> None:
    root_text = os.environ.get("MYCROFT_ASSET_ROOT")
    if not root_text:
        pytest.skip("MYCROFT_ASSET_ROOT is not set; pinned assets are external to the repository")
    root = Path(root_text)
    wavs = sorted((root / MODEL_DIRNAME / "test_wavs").glob("*.wav"))
    if not wavs:
        pytest.skip("Pinned Sherpa package has no public test WAV")
    evidence = REPO / "results/mycroft/console-terminal" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evidence.mkdir(parents=True)
    app = PtyConsole(wavs[0], root, evidence)
    try:
        _run_scenario(app)
    finally:
        (evidence / "terminal-output.bin").write_bytes(bytes(app.raw))


def _row(app: PtyConsole, index: int) -> str:
    return app.screen.display[index].rstrip()


def _draft(app: PtyConsole) -> str:
    rows = [line.rstrip() for line in app.screen.display]
    start = rows.index("Text:") + 1
    end = next(i for i in range(start, len(rows)) if rows[i].startswith("───"))
    return "".join(rows[start:end]).rstrip()


def _run_scenario(app: PtyConsole) -> None:
    app.wait_for(lambda: "Ready (" in app.text(), 30, "model loaded")
    app.snapshot("ready")
    assert _row(app, 0) == "Mycroft v0 — idle"
    assert _row(app, 1) == "Source: not started"

    quiet_from = len(app.raw)
    app.pump(0.5)
    assert len(app.raw) == quiet_from, "the console must not redraw an unchanged screen"

    app.press(SPACE)
    app.wait_for(lambda: _row(app, 0) == "Mycroft v0 — recording", 5, "recording")
    app.wait_for(lambda: _draft(app) != "", 15, "a partial hypothesis")
    partial = app.snapshot("partial-hypothesis")
    assert "Mycroft v0 — recording" in partial

    app.wait_for(lambda: _row(app, 0) == "Mycroft v0 — stopped-draft", 30, "replay EOF")
    automatic = _draft(app)
    app.snapshot("stopped-draft")
    assert automatic.strip()
    assert automatic == automatic.lower(), "Mycroft emits lower case"
    assert "hypothesis" not in app.text(), "one text area only"

    app.press(b" quoi")
    app.wait_for(lambda: _draft(app).endswith(" quoi"), 5, "typed draft text containing q")
    app.snapshot("edited-with-q")
    assert _row(app, 0) == "Mycroft v0 — stopped-draft"

    app.press(b"\r")
    app.wait_for(lambda: _row(app, 0) == "Mycroft v0 — accepted", 5, "accepted")
    app.snapshot("accepted")

    app.press(SPACE)
    app.wait_for(lambda: _row(app, 0) == "Mycroft v0 — recording", 5, "second recording")
    app.press(ESC)
    app.wait_for(lambda: _row(app, 0) == "Mycroft v0 — discarded", 2, "discard by a lone Esc")
    app.snapshot("discarded-by-esc")

    status = Path(f"/proc/{app.pid}/status").read_text()
    peak_kib = int(re.search(r"VmHWM:\s+(\d+) kB", status).group(1))
    (app.evidence / "resources.txt").write_text(
        f"host={os.uname().nodename} arch={os.uname().machine}\n"
        f"console peak RSS (VmHWM) after two sessions: {peak_kib / 1024:.1f} MiB\n",
        encoding="utf-8",
    )

    app.press(b"q")
    assert app.wait_exit(10) == 0
    after_view = bytes(app.raw).rsplit(LEAVE_ALT_SCREEN, 1)
    assert len(after_view) == 2, "the console must restore the normal screen"
    accepted = (automatic + " quoi").encode("utf-8")
    assert after_view[1].count(accepted) == 1, after_view[1]
    assert not re.search(rb"(?<!\r)\n", after_view[0]), "a bare line feed would start the next line mid-screen"
