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

Resident mode (`--resident`, plan step 9.7, asked by Wyoh in note 0903_03):
the model is loaded once and kept, so showing the Slate again costs no reload.

    {"op": "ready"}                       model loaded; idle, microphone closed
    stdin {"op": "start"}                 open the capture, then
    {"op": "listening"}                   … and "partial" lines as above
    stdin {"op": "stop"}                  "final", reset, back to idle (no exit)
    stdin closed or SIGTERM               "final" if listening, then exit 0

A replayed file that ends also gives "final" and returns to idle. A "start"
while listening and a "stop" while idle are ignored. A capture failure during
an utterance sends "error" and returns to idle, keeping the model loaded; only
a failure before "ready" ends the process (status 2).
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

from mycroft_console import DEFAULT_MODEL, DEFAULT_THREADS, MODEL_PROFILES, ConsoleError, SherpaStreamingRecognizer, default_asset_root, make_source


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

    def reset(self) -> None:
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


def resident(make_source_: Callable[[], object], recognizer, emit: Callable[..., None], stdin_fd: int,
             stopped: Callable[[], bool]) -> int:
    """Serve utterances on start/stop commands with one loaded model; returns the exit status."""
    source = None
    text = ""
    pending = b""

    def end_utterance() -> None:
        nonlocal source, text
        try:
            emit("final", text=recognizer.finish())
        finally:
            source.close()
            source, text = None, ""
            recognizer.reset()

    try:
        while not stopped():
            # Idle: wake twice a second at most; listening: poll the audio often.
            ready, _, _ = select.select([stdin_fd], [], [], 0.02 if source else 0.5)
            if ready:
                chunk = os.read(stdin_fd, 4096)
                if not chunk:
                    break  # the host closed stdin: exit
                pending += chunk
                while b"\n" in pending:
                    line, pending = pending.split(b"\n", 1)
                    try:
                        op = json.loads(line).get("op")
                    except (ValueError, AttributeError):
                        continue
                    if op == "start" and source is None:
                        try:
                            source = make_source_()
                            source.start()
                        except ConsoleError as exc:
                            source = None
                            emit("error", message=str(exc))
                            continue
                        emit("listening")
                    elif op == "stop" and source is not None:
                        end_utterance()
            if source is None:
                continue
            try:
                pcm = source.poll(time.monotonic())
            except ConsoleError as exc:  # capture failed: keep the model, go back to idle
                emit("error", message=str(exc))
                source.close()
                source, text = None, ""
                recognizer.reset()
                continue
            if pcm is None:
                continue
            if pcm == b"":
                end_utterance()  # a replayed file ended
                continue
            current = recognizer.accept_pcm(pcm, source.sample_rate)
            if current != text:
                text = current
                emit("partial", text=text)
        if source is not None:
            end_utterance()
        return 0
    except ConsoleError as exc:
        emit("error", message=str(exc))
        return EXIT_RUNTIME_ERROR
    finally:
        if source is not None:
            source.close()
        recognizer.close()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mycroft dictation provider (JSON lines on stdout; close stdin to stop)")
    parser.add_argument("--input", metavar="PATH", help="/dev/snd/pcmC#D#c capture node, or a 16-bit mono WAV to replay")
    parser.add_argument("--assets", metavar="DIR", help="parent of the pinned Sherpa runtime and model (default: $MYCROFT_ASSET_ROOT)")
    parser.add_argument("--threads", type=int, default=DEFAULT_THREADS, help=f"Sherpa inference threads (default {DEFAULT_THREADS})")
    parser.add_argument("--model", choices=sorted(MODEL_PROFILES), default=DEFAULT_MODEL, help=f"speech model (default {DEFAULT_MODEL})")
    parser.add_argument("--resident", action="store_true", help="load once, then serve start/stop commands from stdin")
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
    if args.fake is not None:
        new_source = lambda: FakeSource(args.fake_interval)  # noqa: E731
    else:
        new_source = lambda: make_source(Path(args.input))  # noqa: E731
    try:
        source = new_source()  # validates the input before any model load
        if args.fake is not None:
            recognizer = FakeRecognizer(args.fake)
        else:
            recognizer = SherpaStreamingRecognizer(Path(args.assets) if args.assets else default_asset_root(), args.threads, model=args.model)
        if not args.resident:
            source.start()
    except ConsoleError as exc:
        emit("error", message=str(exc))
        return EXIT_SETUP_ERROR
    emit("ready")
    if args.resident:
        source.close()  # idle with the capture closed
        return resident(new_source, recognizer, emit, sys.stdin.fileno(), lambda: stop_requested[0])
    return dictate(source, recognizer, emit, sys.stdin.fileno(), lambda: stop_requested[0])


if __name__ == "__main__":
    raise SystemExit(main())
