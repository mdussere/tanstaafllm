#!/usr/bin/env python3
"""Mycroft v0: one foreground, offline, text-only streaming ASR console.

The program deliberately has one source option and one model profile.  It is
not a command runner, daemon, audio recorder, or model picker.  Private audio
is read from its supplied path and is never copied or written by this program.
"""

from __future__ import annotations

import argparse
import array
import ctypes
import os
import re
import select
import subprocess
import sys
import termios
import time
import tty
import wave
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable, Iterator, Optional


MODEL_DIRNAME = "sherpa-onnx-streaming-zipformer-fr-2023-04-14"
RUNTIME_DIRNAME = "sherpa-onnx-v1.13.8-linux-x64-shared-no-tts"
MODEL_ID = "sherpa-onnx-fr-zipformer-int8 / 2023-04-14"
CHUNK_MS = 200
PCM_CAPTURE_PATH = re.compile(r"^/dev/snd/pcmC(?P<card>\d+)D(?P<device>\d+)c$")


class ConsoleError(RuntimeError):
    """An honest, user-facing setup or input error."""


class Phase(str, Enum):
    IDLE = "idle"
    RECORDING = "recording"
    STOPPED_DRAFT = "stopped-draft"
    ACCEPTED = "accepted"
    DISCARDED = "discarded"
    ERROR = "error"


@dataclass
class ConsoleState:
    phase: Phase = Phase.IDLE
    source_label: str = "not started"
    hypothesis: str = ""
    draft: str = ""
    edited: bool = False
    cursor: int = 0
    status: str = "F5 starts a session. No audio is retained."
    accepted_text: Optional[str] = None


class DraftController:
    """Pure state machine.  It has no terminal, model, or audio dependency."""

    def __init__(self, accept_sink: Callable[[str], None] | None = None) -> None:
        self.state = ConsoleState()
        self._accept_sink = accept_sink or (lambda text: print(text, flush=True))

    def start(self, source_label: str) -> bool:
        if self.state.phase == Phase.RECORDING:
            self.state.status = "Already recording; F6 stops or Esc discards."
            return False
        self.state = ConsoleState(
            phase=Phase.RECORDING,
            source_label=source_label,
            status="Recording: hypotheses are visible below the draft.",
        )
        return True

    def hypothesis(self, text: str) -> None:
        if self.state.phase != Phase.RECORDING:
            return
        self.state.hypothesis = text
        if not self.state.edited:
            self.state.draft = text
            self.state.cursor = len(text)

    def stop(self, final_text: str = "") -> bool:
        if self.state.phase != Phase.RECORDING:
            self.state.status = "F6 is available only while recording."
            return False
        if final_text:
            self.hypothesis(final_text)
        self.state.phase = Phase.STOPPED_DRAFT
        self.state.status = "Stopped: edit the draft, Enter accepts, Esc discards."
        return True

    def audio_failed(self, message: str) -> None:
        if self.state.phase == Phase.RECORDING:
            self.state.phase = Phase.STOPPED_DRAFT
        self.state.status = "Audio/ASR error: " + message

    def edit(self, key: str) -> bool:
        if self.state.phase != Phase.STOPPED_DRAFT:
            self.state.status = "Draft editing is available after F6 (or replay EOF)."
            return False
        text = self.state.draft
        cursor = self.state.cursor
        if key == "left":
            self.state.cursor = max(0, cursor - 1)
        elif key == "right":
            self.state.cursor = min(len(text), cursor + 1)
        elif key == "home":
            self.state.cursor = 0
        elif key == "end":
            self.state.cursor = len(text)
        elif key == "backspace":
            if cursor:
                self.state.draft = text[: cursor - 1] + text[cursor:]
                self.state.cursor = cursor - 1
        elif key == "delete":
            self.state.draft = text[:cursor] + text[cursor + 1 :]
        elif len(key) == 1 and key.isprintable():
            self.state.draft = text[:cursor] + key + text[cursor:]
            self.state.cursor = cursor + 1
        else:
            return False
        self.state.edited = True
        self.state.status = "Draft edited. Enter accepts exactly this text."
        return True

    def accept(self) -> bool:
        if self.state.phase != Phase.STOPPED_DRAFT:
            self.state.status = "Enter accepts only a stopped draft."
            return False
        text = self.state.draft
        self._accept_sink(text)
        self.state.phase = Phase.ACCEPTED
        self.state.accepted_text = text
        self.state.status = "Accepted once. F5 starts a fresh session; q quits."
        return True

    def discard(self) -> bool:
        if self.state.phase == Phase.IDLE:
            self.state.status = "There is no draft to discard."
            return False
        was_recording = self.state.phase == Phase.RECORDING
        self.state.phase = Phase.DISCARDED
        self.state.hypothesis = ""
        self.state.draft = ""
        self.state.cursor = 0
        self.state.edited = False
        self.state.accepted_text = None
        self.state.status = "Discarded; no text was emitted." if not was_recording else "Discarded and recording stopped; no text was emitted."
        return True

    def can_quit(self) -> bool:
        if self.state.phase == Phase.RECORDING:
            self.state.status = "Use F6 to stop or Esc to discard before quitting."
            return False
        return True


def render_snapshot(state: ConsoleState) -> str:
    """Return a deterministic renderer snapshot; the terminal adds ANSI around it."""
    cursor_marker = " " * state.cursor + "^" if state.phase == Phase.STOPPED_DRAFT else ""
    return "\n".join(
        (
            "Mycroft v0 — offline text composition",
            f"State: {state.phase.value} | Source: {state.source_label}",
            f"Model: {MODEL_ID}",
            f"Status: {state.status}",
            "",
            "Draft:",
            state.draft or "(empty)",
            cursor_marker,
            "",
            "ASR hypothesis:",
            state.hypothesis or "(waiting)",
            "",
            "F5 start  F6 stop  Enter accept  Esc discard  q quit",
        )
    )


class ReplaySource:
    """PCM WAV replay. Chunks are paced by the foreground loop, never batched."""

    kind = "replay"

    def __init__(self, path: Path, chunk_ms: int = CHUNK_MS) -> None:
        self.path = path
        try:
            self._wave = wave.open(str(path), "rb")
        except (wave.Error, OSError) as exc:
            raise ConsoleError(f"Cannot open replay WAV {path}: {exc}") from exc
        if self._wave.getnchannels() != 1 or self._wave.getsampwidth() != 2:
            self._wave.close()
            raise ConsoleError("Replay requires RIFF/WAVE signed 16-bit mono PCM; convert explicitly before v0.")
        self.sample_rate = self._wave.getframerate()
        self.chunk_frames = max(1, self.sample_rate * chunk_ms // 1000)
        self.label = f"replay {path} ({self.sample_rate} Hz mono PCM)"
        self._next_at = 0.0
        self._finished = False

    def start(self) -> None:
        self._next_at = time.monotonic()

    def poll(self, now: float) -> Optional[bytes]:
        if self._finished or now < self._next_at:
            return None
        data = self._wave.readframes(self.chunk_frames)
        if not data:
            self._finished = True
            return b""
        self._next_at += len(data) / 2 / self.sample_rate
        return data

    def close(self) -> None:
        self._wave.close()


class AlsaCaptureSource:
    """A /dev/snd capture-node adapter backed by the system ALSA capture tool."""

    kind = "microphone"

    def __init__(self, path: Path) -> None:
        match = PCM_CAPTURE_PATH.match(str(path))
        if not match:
            raise ConsoleError("Live input must be a capture PCM node such as /dev/snd/pcmC0D0c.")
        if not path.is_char_device():
            raise ConsoleError(f"Live input is not a character device: {path}")
        if not os.access(path, os.R_OK):
            raise ConsoleError(f"Cannot read {path}; check the audio-device permission.")
        self.alsa_device = f"plughw:{match.group('card')},{match.group('device')}"
        self.label = f"microphone {path} via ALSA {self.alsa_device}"
        self.sample_rate = 16000
        self._process: subprocess.Popen[bytes] | None = None

    def start(self) -> None:
        try:
            self._process = subprocess.Popen(
                ["arecord", "-q", "-D", self.alsa_device, "-f", "S16_LE", "-r", "16000", "-c", "1", "-t", "raw"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError as exc:
            raise ConsoleError("Live capture needs the system 'arecord' command (ALSA utilities).") from exc
        if self._process.stdout is None:
            raise ConsoleError("Could not open the live-capture stream.")
        os.set_blocking(self._process.stdout.fileno(), False)

    def poll(self, now: float) -> Optional[bytes]:
        if self._process is None or self._process.stdout is None:
            return None
        try:
            data = os.read(self._process.stdout.fileno(), 6400)
        except BlockingIOError:
            data = None
        if data:
            return data
        if self._process.poll() is not None:
            diagnostic = b""
            if self._process.stderr:
                diagnostic = self._process.stderr.read()
            message = diagnostic.decode("utf-8", "replace").strip() or f"arecord exited with {self._process.returncode}"
            raise ConsoleError(message)
        return None

    def close(self) -> None:
        if self._process and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait()


# ctypes layouts mirror the pinned Sherpa C API; they are intentionally local
# so the v0 runtime needs no Python wheel and no runtime model selection.
class _FeatureConfig(ctypes.Structure):
    _fields_ = [("sample_rate", ctypes.c_int32), ("feature_dim", ctypes.c_int32)]


class _TransducerConfig(ctypes.Structure):
    _fields_ = [("encoder", ctypes.c_char_p), ("decoder", ctypes.c_char_p), ("joiner", ctypes.c_char_p)]


class _ParaformerConfig(ctypes.Structure):
    _fields_ = [("encoder", ctypes.c_char_p), ("decoder", ctypes.c_char_p)]


class _OneModelConfig(ctypes.Structure):
    _fields_ = [("model", ctypes.c_char_p)]


class _OnlineModelConfig(ctypes.Structure):
    _fields_ = [
        ("transducer", _TransducerConfig), ("paraformer", _ParaformerConfig),
        ("zipformer2_ctc", _OneModelConfig), ("tokens", ctypes.c_char_p),
        ("num_threads", ctypes.c_int32), ("provider", ctypes.c_char_p),
        ("debug", ctypes.c_int32), ("model_type", ctypes.c_char_p),
        ("modeling_unit", ctypes.c_char_p), ("bpe_vocab", ctypes.c_char_p),
        ("tokens_buf", ctypes.c_char_p), ("tokens_buf_size", ctypes.c_int32),
        ("nemo_ctc", _OneModelConfig), ("t_one_ctc", _OneModelConfig),
    ]


class _CtcFstConfig(ctypes.Structure):
    _fields_ = [("graph", ctypes.c_char_p), ("max_active", ctypes.c_int32)]


class _HomophoneConfig(ctypes.Structure):
    _fields_ = [("dict_dir", ctypes.c_char_p), ("lexicon", ctypes.c_char_p), ("rule_fsts", ctypes.c_char_p)]


class _RecognizerConfig(ctypes.Structure):
    _fields_ = [
        ("feat_config", _FeatureConfig), ("model_config", _OnlineModelConfig),
        ("decoding_method", ctypes.c_char_p), ("max_active_paths", ctypes.c_int32),
        ("enable_endpoint", ctypes.c_int32), ("rule1_min_trailing_silence", ctypes.c_float),
        ("rule2_min_trailing_silence", ctypes.c_float), ("rule3_min_utterance_length", ctypes.c_float),
        ("hotwords_file", ctypes.c_char_p), ("hotwords_score", ctypes.c_float),
        ("ctc_fst_decoder_config", _CtcFstConfig), ("rule_fsts", ctypes.c_char_p),
        ("rule_fars", ctypes.c_char_p), ("blank_penalty", ctypes.c_float),
        ("hotwords_buf", ctypes.c_char_p), ("hotwords_buf_size", ctypes.c_int32), ("hr", _HomophoneConfig),
    ]


class _RecognizerResult(ctypes.Structure):
    _fields_ = [
        ("text", ctypes.c_char_p), ("tokens", ctypes.c_char_p), ("tokens_arr", ctypes.POINTER(ctypes.c_char_p)),
        ("timestamps", ctypes.POINTER(ctypes.c_float)), ("count", ctypes.c_int32), ("json", ctypes.c_char_p),
    ]


class SherpaStreamingRecognizer:
    """Pinned Sherpa C API adapter; accepts PCM chunks and emits text snapshots."""

    def __init__(self, asset_root: Path) -> None:
        model_dir = asset_root / MODEL_DIRNAME
        runtime_dir = asset_root / RUNTIME_DIRNAME
        lib_path = runtime_dir / "lib" / "libsherpa-onnx-c-api.so"
        required = {
            "encoder": model_dir / "encoder-epoch-29-avg-9-with-averaged-model.int8.onnx",
            "decoder": model_dir / "decoder-epoch-29-avg-9-with-averaged-model.int8.onnx",
            "joiner": model_dir / "joiner-epoch-29-avg-9-with-averaged-model.int8.onnx",
            "tokens": model_dir / "tokens.txt",
            "runtime": lib_path,
        }
        missing = [name for name, path in required.items() if not path.is_file()]
        if missing:
            raise ConsoleError("Pinned Sherpa assets are missing: " + ", ".join(missing) + ". Set MYCROFT_ASSET_ROOT to their parent directory.")
        try:
            self._lib = ctypes.CDLL(str(lib_path))
        except OSError as exc:
            raise ConsoleError(f"Cannot load pinned Sherpa runtime: {exc}") from exc
        self._lib.SherpaOnnxCreateOnlineRecognizer.argtypes = [ctypes.POINTER(_RecognizerConfig)]
        self._lib.SherpaOnnxCreateOnlineRecognizer.restype = ctypes.c_void_p
        self._lib.SherpaOnnxDestroyOnlineRecognizer.argtypes = [ctypes.c_void_p]
        self._lib.SherpaOnnxCreateOnlineStream.argtypes = [ctypes.c_void_p]
        self._lib.SherpaOnnxCreateOnlineStream.restype = ctypes.c_void_p
        self._lib.SherpaOnnxDestroyOnlineStream.argtypes = [ctypes.c_void_p]
        self._lib.SherpaOnnxOnlineStreamAcceptWaveform.argtypes = [ctypes.c_void_p, ctypes.c_int32, ctypes.POINTER(ctypes.c_float), ctypes.c_int32]
        self._lib.SherpaOnnxIsOnlineStreamReady.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self._lib.SherpaOnnxIsOnlineStreamReady.restype = ctypes.c_int32
        self._lib.SherpaOnnxDecodeOnlineStream.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self._lib.SherpaOnnxGetOnlineStreamResult.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
        self._lib.SherpaOnnxGetOnlineStreamResult.restype = ctypes.POINTER(_RecognizerResult)
        self._lib.SherpaOnnxDestroyOnlineRecognizerResult.argtypes = [ctypes.POINTER(_RecognizerResult)]
        self._lib.SherpaOnnxOnlineStreamInputFinished.argtypes = [ctypes.c_void_p]

        encode = lambda path: str(path).encode("utf-8")
        self._config = _RecognizerConfig()
        self._config.feat_config.sample_rate = 16000
        self._config.feat_config.feature_dim = 80
        self._config.model_config.transducer.encoder = encode(required["encoder"])
        self._config.model_config.transducer.decoder = encode(required["decoder"])
        self._config.model_config.transducer.joiner = encode(required["joiner"])
        self._config.model_config.tokens = encode(required["tokens"])
        self._config.model_config.num_threads = 1
        self._config.model_config.provider = b"cpu"
        self._config.decoding_method = b"greedy_search"
        self._recognizer = self._lib.SherpaOnnxCreateOnlineRecognizer(ctypes.byref(self._config))
        if not self._recognizer:
            raise ConsoleError("Pinned Sherpa rejected its recognizer configuration.")
        self._stream = self._lib.SherpaOnnxCreateOnlineStream(self._recognizer)
        if not self._stream:
            self.close()
            raise ConsoleError("Pinned Sherpa could not create a streaming session.")
        self._finished = False

    @staticmethod
    def _float_samples(pcm: bytes) -> ctypes.Array[ctypes.c_float]:
        samples = array.array("h")
        samples.frombytes(pcm[: len(pcm) - (len(pcm) % 2)])
        if sys.byteorder != "little":
            samples.byteswap()
        return (ctypes.c_float * len(samples))(*(sample / 32768.0 for sample in samples))

    def _result(self) -> str:
        result = self._lib.SherpaOnnxGetOnlineStreamResult(self._recognizer, self._stream)
        if not result:
            return ""
        try:
            return (result.contents.text or b"").decode("utf-8", "replace")
        finally:
            self._lib.SherpaOnnxDestroyOnlineRecognizerResult(result)

    def accept_pcm(self, pcm: bytes, sample_rate: int) -> str:
        if self._finished:
            raise ConsoleError("ASR stream is already finalised.")
        samples = self._float_samples(pcm)
        if not samples:
            return self._result()
        self._lib.SherpaOnnxOnlineStreamAcceptWaveform(self._stream, sample_rate, samples, len(samples))
        while self._lib.SherpaOnnxIsOnlineStreamReady(self._recognizer, self._stream):
            self._lib.SherpaOnnxDecodeOnlineStream(self._recognizer, self._stream)
        return self._result()

    def finish(self) -> str:
        if not self._finished:
            self._lib.SherpaOnnxOnlineStreamInputFinished(self._stream)
            while self._lib.SherpaOnnxIsOnlineStreamReady(self._recognizer, self._stream):
                self._lib.SherpaOnnxDecodeOnlineStream(self._recognizer, self._stream)
            self._finished = True
        return self._result()

    def close(self) -> None:
        if getattr(self, "_stream", None):
            self._lib.SherpaOnnxDestroyOnlineStream(self._stream)
            self._stream = None
        if getattr(self, "_recognizer", None):
            self._lib.SherpaOnnxDestroyOnlineRecognizer(self._recognizer)
            self._recognizer = None


def default_asset_root() -> Path:
    supplied = os.environ.get("MYCROFT_ASSET_ROOT")
    if supplied:
        return Path(supplied)
    return Path(__file__).resolve().parents[3] / ".mycroft-assets"


def make_source(path: Path) -> ReplaySource | AlsaCaptureSource:
    if path.is_file():
        return ReplaySource(path)
    if path.exists() and path.is_char_device():
        return AlsaCaptureSource(path)
    raise ConsoleError(f"Input does not exist as a regular WAV file or character device: {path}")


class KeyDecoder:
    """Decode the documented function keys and standard single-line editing keys."""

    _ESCAPES = {"\x1b[15~": "f5", "\x1b[17~": "f6", "\x1b[D": "left", "\x1b[C": "right", "\x1b[H": "home", "\x1b[F": "end", "\x1b[3~": "delete"}

    def __init__(self) -> None:
        self._buffer = ""

    def feed(self, text: str) -> list[str]:
        self._buffer += text
        events: list[str] = []
        while self._buffer:
            if self._buffer[0] != "\x1b":
                char, self._buffer = self._buffer[0], self._buffer[1:]
                events.append({"\r": "enter", "\n": "enter", "\x7f": "backspace", "\x08": "backspace"}.get(char, char))
                continue
            complete = next((seq for seq in self._ESCAPES if self._buffer.startswith(seq)), None)
            if complete:
                events.append(self._ESCAPES[complete])
                self._buffer = self._buffer[len(complete):]
            elif any(seq.startswith(self._buffer) for seq in self._ESCAPES):
                break
            else:
                self._buffer = self._buffer[1:]
                events.append("escape")
        return events


class TerminalConsole:
    def __init__(self, input_path: Path, asset_root: Path, output: Callable[[str], None]) -> None:
        self.input_path = input_path
        self.asset_root = asset_root
        self.controller = DraftController(output)
        self.source: ReplaySource | AlsaCaptureSource | None = None
        self.recognizer: SherpaStreamingRecognizer | None = None
        self.running = True

    def redraw(self) -> None:
        sys.stderr.write("\x1b[2J\x1b[H" + render_snapshot(self.controller.state) + "\n")
        sys.stderr.flush()

    def _start(self) -> None:
        try:
            source = make_source(self.input_path)
            recognizer = SherpaStreamingRecognizer(self.asset_root)
            source.start()
        except ConsoleError as exc:
            self.controller.state.status = str(exc)
            return
        self.source, self.recognizer = source, recognizer
        self.controller.start(source.label)

    def _stop(self) -> None:
        if not self.source or not self.recognizer:
            self.controller.stop()
            return
        try:
            final = self.recognizer.finish()
            self.controller.stop(final)
        except ConsoleError as exc:
            self.controller.audio_failed(str(exc))
        finally:
            self.source.close()
            self.recognizer.close()
            self.source = self.recognizer = None

    def action(self, event: str) -> None:
        if event == "f5":
            self._start()
        elif event == "f6":
            self._stop()
        elif event == "escape":
            if self.controller.state.phase == Phase.RECORDING:
                if self.source:
                    self.source.close()
                if self.recognizer:
                    self.recognizer.close()
                self.source = self.recognizer = None
            self.controller.discard()
        elif event == "enter":
            self.controller.accept()
        elif event == "q" and self.controller.can_quit():
            self.running = False
        else:
            self.controller.edit(event)

    def tick(self) -> None:
        if not self.source or not self.recognizer or self.controller.state.phase != Phase.RECORDING:
            return
        try:
            pcm = self.source.poll(time.monotonic())
            if pcm is None:
                return
            if pcm == b"":
                self._stop()  # replay EOF has exactly the F6 finalisation semantics
                return
            self.controller.hypothesis(self.recognizer.accept_pcm(pcm, self.source.sample_rate))
        except ConsoleError as exc:
            self.controller.audio_failed(str(exc))
            if self.source:
                self.source.close()
            if self.recognizer:
                self.recognizer.close()
            self.source = self.recognizer = None

    def run(self) -> int:
        if not sys.stdin.isatty() or not sys.stderr.isatty():
            raise ConsoleError("Mycroft v0 needs an interactive terminal for its editable foreground console.")
        old_settings = termios.tcgetattr(sys.stdin.fileno())
        decoder = KeyDecoder()
        try:
            tty.setraw(sys.stdin.fileno())
            self.redraw()
            while self.running:
                ready, _, _ = select.select([sys.stdin], [], [], 0.05)
                if ready:
                    data = os.read(sys.stdin.fileno(), 64).decode("utf-8", "replace")
                    for event in decoder.feed(data):
                        self.action(event)
                self.tick()
                self.redraw()
        finally:
            if self.source:
                self.source.close()
            if self.recognizer:
                self.recognizer.close()
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
            sys.stderr.write("\x1b[2J\x1b[H")
            sys.stderr.flush()
        return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mycroft v0 offline streaming text console")
    parser.add_argument("--input", required=True, metavar="PATH", help="RIFF/WAVE replay file or /dev/snd/pcmC#D#c capture node")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        console = TerminalConsole(Path(args.input), default_asset_root(), lambda text: print(text, flush=True))
        return console.run()
    except ConsoleError as exc:
        print(f"mycroft-console: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
