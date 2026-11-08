#!/usr/bin/env python3
"""Mycroft's speech provider: Piper Lessac kept loaded, speaking Mike's replies (plan step 12).

The counterpart of ``mycroft_dictate.py --resident``: one process, one model load,
JSON lines both ways.

Host → provider (stdin):
    {"op": "say", "text": "…"}            speak this text; queued after any text still speaking
    {"op": "stop"}                         stop speaking now and drop what is queued

Provider → host (stdout):
    {"op": "ready", "sample_rate": 22050}  model loaded; idle
    {"op": "speaking", "id": 1, "sentence": 0, "text": "…"}   a sentence starts playing
    {"op": "spoken", "id": 1}              the whole "say" number 1 has been played
    {"op": "stopped"}                      after "stop"
    {"op": "error", "message": "…"}

Closing stdin ends the process once queued speech has played. The text is split
into sentences; the next one is synthesised while the current one plays, so the
first sound comes after one sentence's synthesis, not the whole reply's.
Standard library only, plus Sherpa-ONNX's C library through ctypes, as on Luna.
"""

from __future__ import annotations

import argparse
import ctypes
import json
import platform
import queue
import re
import subprocess
import sys
import threading
import time
import wave
from pathlib import Path
from typing import Callable, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mycroft_console import ConsoleError, default_asset_root  # noqa: E402

VOICE_DIRNAME = "vits-piper-en_US-lessac-medium-int8"  # the user's choice, 2026-11-01 (step 11)
VOICE_MODEL = "en_US-lessac-medium.onnx"
EXIT_SETUP_ERROR = 2
# The speech-to-text runtime on x86_64 is Sherpa's "no-tts" build; speech needs the full one.
# On aarch64 (Luna, luna-pi) the same library serves both.
TTS_RUNTIME_DIRNAMES = {
    "x86_64": "sherpa-onnx-v1.13.8-linux-x64-shared",
    "aarch64": "sherpa-onnx-v1.13.8-linux-aarch64-shared-cpu-lib",
}
SENTENCE_END = re.compile(r"(?<=[.!?;:])\s+")


def split_sentences(text: str) -> list[str]:
    return [part.strip() for part in SENTENCE_END.split(text.strip()) if part.strip()]


# --- Sherpa-ONNX v1.13.8 C API structures (c-api.h); every field present, unused ones zero ---

class _Vits(ctypes.Structure):
    _fields_ = [("model", ctypes.c_char_p), ("lexicon", ctypes.c_char_p), ("tokens", ctypes.c_char_p),
                ("data_dir", ctypes.c_char_p), ("noise_scale", ctypes.c_float), ("noise_scale_w", ctypes.c_float),
                ("length_scale", ctypes.c_float), ("dict_dir", ctypes.c_char_p)]


class _Matcha(ctypes.Structure):
    _fields_ = [("acoustic_model", ctypes.c_char_p), ("vocoder", ctypes.c_char_p), ("lexicon", ctypes.c_char_p),
                ("tokens", ctypes.c_char_p), ("data_dir", ctypes.c_char_p), ("noise_scale", ctypes.c_float),
                ("length_scale", ctypes.c_float), ("dict_dir", ctypes.c_char_p)]


class _Kokoro(ctypes.Structure):
    _fields_ = [("model", ctypes.c_char_p), ("voices", ctypes.c_char_p), ("tokens", ctypes.c_char_p),
                ("data_dir", ctypes.c_char_p), ("length_scale", ctypes.c_float), ("dict_dir", ctypes.c_char_p),
                ("lexicon", ctypes.c_char_p), ("lang", ctypes.c_char_p)]


class _Kitten(ctypes.Structure):
    _fields_ = [("model", ctypes.c_char_p), ("voices", ctypes.c_char_p), ("tokens", ctypes.c_char_p),
                ("data_dir", ctypes.c_char_p), ("length_scale", ctypes.c_float)]


class _Zipvoice(ctypes.Structure):
    _fields_ = [("tokens", ctypes.c_char_p), ("encoder", ctypes.c_char_p), ("decoder", ctypes.c_char_p),
                ("vocoder", ctypes.c_char_p), ("data_dir", ctypes.c_char_p), ("lexicon", ctypes.c_char_p),
                ("feat_scale", ctypes.c_float), ("t_shift", ctypes.c_float), ("target_rms", ctypes.c_float),
                ("guidance_scale", ctypes.c_float)]


class _Pocket(ctypes.Structure):
    _fields_ = [("lm_flow", ctypes.c_char_p), ("lm_main", ctypes.c_char_p), ("encoder", ctypes.c_char_p),
                ("decoder", ctypes.c_char_p), ("text_conditioner", ctypes.c_char_p), ("vocab_json", ctypes.c_char_p),
                ("token_scores_json", ctypes.c_char_p), ("voice_embedding_cache_capacity", ctypes.c_int32)]


class _Supertonic(ctypes.Structure):
    _fields_ = [("duration_predictor", ctypes.c_char_p), ("text_encoder", ctypes.c_char_p),
                ("vector_estimator", ctypes.c_char_p), ("vocoder", ctypes.c_char_p), ("tts_json", ctypes.c_char_p),
                ("unicode_indexer", ctypes.c_char_p), ("voice_style", ctypes.c_char_p)]


class _ModelConfig(ctypes.Structure):
    _fields_ = [("vits", _Vits), ("num_threads", ctypes.c_int32), ("debug", ctypes.c_int32),
                ("provider", ctypes.c_char_p), ("matcha", _Matcha), ("kokoro", _Kokoro), ("kitten", _Kitten),
                ("zipvoice", _Zipvoice), ("pocket", _Pocket), ("supertonic", _Supertonic)]


class _TtsConfig(ctypes.Structure):
    _fields_ = [("model", _ModelConfig), ("rule_fsts", ctypes.c_char_p), ("max_num_sentences", ctypes.c_int32),
                ("rule_fars", ctypes.c_char_p), ("silence_scale", ctypes.c_float)]


class _Audio(ctypes.Structure):
    _fields_ = [("samples", ctypes.POINTER(ctypes.c_float)), ("n", ctypes.c_int32), ("sample_rate", ctypes.c_int32)]


class PiperVoice:
    """One loaded Piper voice; ``synthesise`` returns 16-bit mono PCM."""

    def __init__(self, asset_root: Path, voice_dir: Optional[Path] = None, num_threads: int = 2,
                 length_scale: float = 1.0) -> None:
        voice = voice_dir or next((d for d in (asset_root / VOICE_DIRNAME, asset_root / "tts" / VOICE_DIRNAME)
                                   if d.is_dir()), asset_root / VOICE_DIRNAME)
        machine = platform.machine()
        if machine not in TTS_RUNTIME_DIRNAMES:
            raise ConsoleError(f"No pinned Sherpa runtime with speech for the {machine} architecture.")
        lib_path = asset_root / TTS_RUNTIME_DIRNAMES[machine] / "lib" / "libsherpa-onnx-c-api.so"
        required = {"model": voice / VOICE_MODEL, "tokens": voice / "tokens.txt", "runtime": lib_path}
        missing = [name for name, path in required.items() if not path.is_file()]
        if not (voice / "espeak-ng-data").is_dir():
            missing.append("espeak-ng-data")
        if missing:
            raise ConsoleError("Piper assets are missing: " + ", ".join(missing) + f" (looked in {voice}).")
        try:
            self._lib = ctypes.CDLL(str(lib_path))
        except OSError as exc:
            raise ConsoleError(f"Cannot load pinned Sherpa runtime: {exc}") from exc
        lib = self._lib
        lib.SherpaOnnxCreateOfflineTts.argtypes = [ctypes.POINTER(_TtsConfig)]
        lib.SherpaOnnxCreateOfflineTts.restype = ctypes.c_void_p
        lib.SherpaOnnxDestroyOfflineTts.argtypes = [ctypes.c_void_p]
        lib.SherpaOnnxOfflineTtsSampleRate.argtypes = [ctypes.c_void_p]
        lib.SherpaOnnxOfflineTtsSampleRate.restype = ctypes.c_int32
        lib.SherpaOnnxOfflineTtsGenerate.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int32, ctypes.c_float]
        lib.SherpaOnnxOfflineTtsGenerate.restype = ctypes.POINTER(_Audio)
        lib.SherpaOnnxDestroyOfflineTtsGeneratedAudio.argtypes = [ctypes.POINTER(_Audio)]

        self._keep = [str(p).encode() for p in (voice / VOICE_MODEL, voice / "tokens.txt", voice / "espeak-ng-data")]
        config = _TtsConfig()
        config.model.vits.model, config.model.vits.tokens, config.model.vits.data_dir = self._keep
        config.model.vits.noise_scale = 0.667  # Piper's defaults, as the offline binary uses
        config.model.vits.noise_scale_w = 0.8
        config.model.vits.length_scale = length_scale
        config.model.num_threads = num_threads
        config.model.provider = b"cpu"
        config.max_num_sentences = 1
        config.silence_scale = 0.2
        self._tts = lib.SherpaOnnxCreateOfflineTts(ctypes.byref(config))
        if not self._tts:
            raise ConsoleError("Sherpa could not create the Piper voice.")
        self.sample_rate = lib.SherpaOnnxOfflineTtsSampleRate(self._tts)

    def synthesise(self, text: str) -> bytes:
        audio = self._lib.SherpaOnnxOfflineTtsGenerate(self._tts, text.encode("utf-8"), 0, 1.0)
        if not audio:
            raise ConsoleError("Sherpa returned no audio.")
        try:
            n = audio.contents.n
            samples = audio.contents.samples
            pcm = bytearray(2 * n)
            view = memoryview(pcm).cast("h")
            for i in range(n):
                value = samples[i]
                view[i] = 32767 if value >= 1.0 else -32768 if value <= -1.0 else int(value * 32767)
            return bytes(pcm)
        finally:
            self._lib.SherpaOnnxDestroyOfflineTtsGeneratedAudio(audio)

    def close(self) -> None:
        if getattr(self, "_tts", None):
            self._lib.SherpaOnnxDestroyOfflineTts(self._tts)
            self._tts = None


class FakeVoice:
    """Deterministic stand-in: 10 ms of silence per character, for protocol tests."""

    sample_rate = 16000

    def __init__(self, seconds_per_sentence: float = 0.0) -> None:
        self.seconds_per_sentence = seconds_per_sentence

    def synthesise(self, text: str) -> bytes:
        time.sleep(self.seconds_per_sentence)
        return b"\x00\x00" * (160 * len(text))

    def close(self) -> None:
        pass


class AplayPlayer:
    """Plays 16-bit mono PCM through ALSA's aplay; ``stop`` cuts the current sentence."""

    def __init__(self, device: Optional[str] = None) -> None:
        self.device = device
        self._process: Optional[subprocess.Popen[bytes]] = None
        self._lock = threading.Lock()

    def play(self, pcm: bytes, sample_rate: int) -> None:
        command = ["aplay", "-q", "-t", "raw", "-f", "S16_LE", "-c", "1", "-r", str(sample_rate)]
        if self.device:
            command += ["-D", self.device]
        with self._lock:
            self._process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL)
            process = self._process
        try:
            process.communicate(pcm)
        except (BrokenPipeError, ValueError):
            pass
        finally:
            with self._lock:
                self._process = None

    def stop(self) -> None:
        with self._lock:
            if self._process and self._process.poll() is None:
                self._process.kill()


class WavPlayer:
    """Writes each sentence to <dir>/<say id>-<sentence>.wav instead of playing it (tests, evidence)."""

    def __init__(self, directory: Path, seconds_per_sentence: float = 0.0) -> None:
        self.directory = directory
        self.seconds_per_sentence = seconds_per_sentence
        self.count = 0
        self._stop = threading.Event()

    def play(self, pcm: bytes, sample_rate: int) -> None:
        self.directory.mkdir(parents=True, exist_ok=True)
        with wave.open(str(self.directory / f"{self.count:03d}.wav"), "wb") as out:
            out.setnchannels(1)
            out.setsampwidth(2)
            out.setframerate(sample_rate)
            out.writeframes(pcm)
        self.count += 1
        self._stop.clear()
        self._stop.wait(self.seconds_per_sentence)

    def stop(self) -> None:
        self._stop.set()


def serve(voice, player, emit: Callable[..., None], lines) -> int:
    """Read commands from ``lines`` (an iterator of text lines) until it ends; returns the exit status."""
    epoch = 0  # bumped by "stop": work from an older epoch is dropped
    lock = threading.Lock()
    to_synthesise: queue.Queue = queue.Queue()
    to_play: queue.Queue = queue.Queue(maxsize=1)  # synthesise one sentence ahead, no more

    def current(item_epoch: int) -> bool:
        with lock:
            return item_epoch == epoch

    def synthesiser() -> None:
        while (job := to_synthesise.get()) is not None:
            job_epoch, say_id, sentences = job
            for index, sentence in enumerate(sentences):
                if not current(job_epoch):
                    break
                try:
                    pcm = voice.synthesise(sentence)
                except ConsoleError as exc:
                    emit("error", message=str(exc))
                    break
                to_play.put((job_epoch, say_id, index, sentence, pcm, index == len(sentences) - 1))
        to_play.put(None)

    def speaker() -> None:
        while (item := to_play.get()) is not None:
            item_epoch, say_id, index, sentence, pcm, last = item
            if not current(item_epoch):
                continue
            emit("speaking", id=say_id, sentence=index, text=sentence)
            player.play(pcm, voice.sample_rate)
            if last and current(item_epoch):
                emit("spoken", id=say_id)

    threads = [threading.Thread(target=synthesiser, daemon=True), threading.Thread(target=speaker, daemon=True)]
    for thread in threads:
        thread.start()
    say_id = 0
    for line in lines:
        try:
            message = json.loads(line)
            op = message.get("op")
        except (ValueError, AttributeError):
            continue
        if op == "say":
            sentences = split_sentences(str(message.get("text", "")))
            if sentences:
                say_id += 1
                with lock:
                    to_synthesise.put((epoch, say_id, sentences))
        elif op == "stop":
            with lock:
                epoch += 1
            player.stop()
            emit("stopped")
    to_synthesise.put(None)
    for thread in threads:
        thread.join()
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Mycroft speech provider (JSON lines; close stdin to end)")
    parser.add_argument("--assets", type=Path, help="Sherpa asset root (default: MYCROFT_ASSET_ROOT)")
    parser.add_argument("--voice-dir", type=Path, help=f"Piper voice directory (default: <assets>/{VOICE_DIRNAME})")
    parser.add_argument("--threads", type=int, default=2)
    parser.add_argument("--length-scale", type=float, default=1.0, help="> 1 speaks more slowly (the tutor's 'again, slowly')")
    parser.add_argument("--device", help="ALSA playback device for aplay (default: the system's)")
    parser.add_argument("--wav-dir", type=Path, help="write WAVs here instead of playing (tests, evidence)")
    parser.add_argument("--fake", action="store_true", help="silent deterministic voice, no model (protocol tests)")
    args = parser.parse_args(argv)

    write_lock = threading.Lock()

    def emit(op: str, **fields: object) -> None:
        with write_lock:
            sys.stdout.write(json.dumps({"op": op, **fields}, ensure_ascii=False) + "\n")
            sys.stdout.flush()

    try:
        voice = FakeVoice() if args.fake else PiperVoice(args.assets or default_asset_root(), args.voice_dir,
                                                         args.threads, args.length_scale)
    except ConsoleError as exc:
        emit("error", message=str(exc))
        return EXIT_SETUP_ERROR
    player = WavPlayer(args.wav_dir) if args.wav_dir else AplayPlayer(args.device)
    emit("ready", sample_rate=voice.sample_rate)
    try:
        return serve(voice, player, emit, sys.stdin)
    finally:
        voice.close()


if __name__ == "__main__":
    sys.exit(main())
