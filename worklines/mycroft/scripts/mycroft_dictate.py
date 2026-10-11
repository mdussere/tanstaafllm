#!/usr/bin/env python3
"""Mycroft dictation provider: one utterance of live text for a host that owns it.

The host (on Luna, Wyoh's gamepad daemon feeding the Slate) starts this
process, reads JSON lines from its stdout, and stops it by closing its stdin.
The host owns the text; this process only recognises speech. Protocol agreed
with Wyoh in worklines/wyoh/docs/0600_02_note-from-mycroft-dictation-in-slate.md:

    {"op": "ready"}                       model loaded and capture started
    {"op": "partial", "text": "..."}      whole current text, sent only when it changes
    {"op": "final", "text": "..."}        once: stdin closed, SIGTERM, or the input ended
    {"op": "error", "message": "..."}     then exit

Exit status: 0 after "final"; 2 for an error before "ready" (setup); 3 for an
error after it. Bytes written to stdin are ignored; only its closing matters.

Text is lower case without punctuation (the pinned model's output, lowered).
No audio is written anywhere. `--fake TEXT` runs the same protocol without a
model or microphone, so a host can be developed and tested separately.
"""

from __future__ import annotations

import argparse
import json
import os
import select
import signal
import sys
import time
from pathlib import Path
from typing import Callable, Optional

from mycroft_console import ConsoleError, SherpaStreamingRecognizer, default_asset_root, make_source


EXIT_SETUP_ERROR = 2
EXIT_RUNTIME_ERROR = 3


class FakeSource:
    """A microphone that never ends: one tick per interval until the host stops."""

    sample_rate = 16000

    def __init__(self, interval: float) -> None:
        self.interval = interval
        self._next_at = 0.0

    def start(self) -> None:
        self._next_at = time.monotonic() + self.interval

    def poll(self, now: float) -> Optional[bytes]:
        if now < self._next_at:
            return None
        self._next_at += self.interval
        return b"\x00\x00"

    def close(self) -> None:
        pass


class FakeRecognizer:
    """Reveals the given text one word per tick, like a recogniser catching up."""

    def __init__(self, text: str) -> None:
        self._words = text.split()
        self._shown = 0

    def accept_pcm(self, pcm: bytes, sample_rate: int) -> str:
        self._shown = min(len(self._words), self._shown + 1)
        return " ".join(self._words[: self._shown])

    def finish(self) -> str:
        return " ".join(self._words[: self._shown])

    def close(self) -> None:
        pass


def dictate(source, recognizer, emit: Callable[..., None], stdin_fd: int, stopped: Callable[[], bool]) -> int:
    """Run one utterance after "ready" has been sent; returns the exit status."""
    text = ""
    try:
        while not stopped():
            ready, _, _ = select.select([stdin_fd], [], [], 0.02)
            if ready and not os.read(stdin_fd, 4096):
                break  # the host closed stdin: stop
            pcm = source.poll(time.monotonic())
            if pcm is None:
                continue
            if pcm == b"":
                break  # a replayed file ended
            current = recognizer.accept_pcm(pcm, source.sample_rate)
            if current != text:
                text = current
                emit("partial", text=text)
        emit("final", text=recognizer.finish())
        return 0
    except ConsoleError as exc:
        emit("error", message=str(exc))
        return EXIT_RUNTIME_ERROR
    finally:
        source.close()
        recognizer.close()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mycroft dictation provider (JSON lines on stdout; close stdin to stop)")
    parser.add_argument("--input", metavar="PATH", help="/dev/snd/pcmC#D#c capture node, or a 16-bit mono WAV to replay")
    parser.add_argument("--assets", metavar="DIR", help="parent of the pinned Sherpa runtime and model (default: $MYCROFT_ASSET_ROOT)")
    parser.add_argument("--fake", metavar="TEXT", help="no model or audio: reveal TEXT one word per tick")
    parser.add_argument("--fake-interval", type=float, default=0.2, metavar="SECONDS", help="tick length for --fake")
    args = parser.parse_args(argv)
    if (args.input is None) == (args.fake is None):
        parser.error("give exactly one of --input or --fake")
    return args


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)

    def emit(op: str, **fields: str) -> None:
        sys.stdout.write(json.dumps({"op": op, **fields}, ensure_ascii=False) + "\n")
        sys.stdout.flush()

    stop_requested = [False]
    signal.signal(signal.SIGTERM, lambda *_: stop_requested.__setitem__(0, True))
    try:
        if args.fake is not None:
            source, recognizer = FakeSource(args.fake_interval), FakeRecognizer(args.fake)
        else:
            source = make_source(Path(args.input))
            recognizer = SherpaStreamingRecognizer(Path(args.assets) if args.assets else default_asset_root())
        source.start()
    except ConsoleError as exc:
        emit("error", message=str(exc))
        return EXIT_SETUP_ERROR
    emit("ready")
    return dictate(source, recognizer, emit, sys.stdin.fileno(), lambda: stop_requested[0])


if __name__ == "__main__":
    raise SystemExit(main())
