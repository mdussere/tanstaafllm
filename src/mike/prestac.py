"""PreStaC, the Prefetch Stack Cache (Mike Step 9; study `worklines/mike/docs/0901_01`).

The context is built during navigation, layer by layer; the question comes
last. PreStaC reads each layer in the background on top of the layer below,
keeps the model's state after each layer in a file (a *frame*), and answers a
question by restoring the deepest ready frame and reading only what is left.

Three levels, each using only the one below:

- `Store`: frame files on disk, keyed by the exact token ids they hold;
- an engine (`HttpEngine` over `llama-server`'s slot save/restore, or a fake
  in tests): restore, extend, save, answer;
- `PreStaC`: the wanted stack, the background worker, `ask`.

LFM2.5 is a hybrid model: its state cannot be cut back to an earlier token,
only extended or replaced by a restore. A stack fits that: push extends, pop
restores the frame below, which is still on disk.
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True)
class Layer:
    """One piece of prompt, already tokenised on its own (no merging across boundaries)."""

    name: str
    tokens: tuple[int, ...]


def frame_keys(namespace: str, layers: list[Layer]) -> list[str]:
    """The key of each frame L0…Lk: a hash of the namespace and every token id up to k."""
    digest = hashlib.sha256(namespace.encode())
    keys = []
    for layer in layers:
        digest.update(b"|" + ",".join(map(str, layer.tokens)).encode())
        keys.append(digest.copy().hexdigest()[:32])
    return keys


# --- store ------------------------------------------------------------------

class Store:
    """Frame files `<key>.bin` with `<key>.json` metadata, evicted least recently used first."""

    def __init__(self, root: Path, budget_bytes: int = 200 * 1024 * 1024):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.budget = budget_bytes

    def bin(self, key: str) -> Path:
        return self.root / f"{key}.bin"

    def tmp_name(self, key: str) -> str:
        return f"tmp-{key}.bin"

    def lookup(self, key: str) -> bool:
        return self.bin(key).is_file() and (self.root / f"{key}.json").is_file()

    def commit(self, key: str, meta: dict[str, Any]) -> None:
        """Make a saved state visible: rename the temporary file, then write the metadata."""
        tmp = self.root / self.tmp_name(key)
        os.replace(tmp, self.bin(key))
        meta = {**meta, "bytes": self.bin(key).stat().st_size, "created": time.time(), "last_used": time.time()}
        (self.root / f"{key}.json").write_text(json.dumps(meta))

    def touch(self, key: str) -> None:
        path = self.root / f"{key}.json"
        if path.is_file():
            meta = json.loads(path.read_text())
            meta["last_used"] = time.time()
            path.write_text(json.dumps(meta))

    def drop(self, key: str) -> None:
        for path in (self.bin(key), self.root / f"{key}.json"):
            path.unlink(missing_ok=True)

    def entries(self) -> list[dict[str, Any]]:
        out = []
        for path in self.root.glob("*.json"):
            try:
                out.append({"key": path.stem, **json.loads(path.read_text())})
            except (OSError, ValueError):
                continue
        return out

    def evict(self, pinned: set[str]) -> list[str]:
        entries = sorted(self.entries(), key=lambda e: e.get("last_used", 0))
        total = sum(e.get("bytes", 0) for e in entries)
        dropped = []
        for entry in entries:
            if total <= self.budget:
                break
            if entry["key"] in pinned:
                continue
            self.drop(entry["key"])
            total -= entry.get("bytes", 0)
            dropped.append(entry["key"])
        return dropped


# --- engine -------------------------------------------------------------------

class Engine(Protocol):
    def restore(self, filename: str) -> None: ...
    def save(self, filename: str) -> None: ...
    def extend(self, tokens: list[int]) -> dict[str, Any]: ...
    def answer(self, tokens: list[int], body: dict[str, Any]) -> dict[str, Any]: ...


class HttpEngine:
    """`llama-server` with one slot and `--slot-save-path` set to the store's directory."""

    def __init__(self, url: str, timeout: float = 600):
        self.url, self.timeout = url, timeout

    def _post(self, path: str, body: dict[str, Any]) -> Any:
        request = urllib.request.Request(self.url + path, data=json.dumps(body).encode(),
                                         headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            return json.load(response)

    def restore(self, filename: str) -> None:
        self._post("/slots/0?action=restore", {"filename": filename})

    def save(self, filename: str) -> None:
        self._post("/slots/0?action=save", {"filename": filename})

    def extend(self, tokens: list[int]) -> dict[str, Any]:
        """Read `tokens` (the whole frame so far), writing nothing; only the uncached tail is read."""
        reply = self._post("/completion", {"prompt": tokens, "n_predict": 0, "cache_prompt": True})
        return reply.get("timings", {})

    def answer(self, tokens: list[int], body: dict[str, Any]) -> dict[str, Any]:
        return self._post("/completion", {"prompt": tokens, "cache_prompt": True, **body})


# --- the stack ----------------------------------------------------------------

@dataclass
class AskResult:
    reply: dict[str, Any]
    prompt_tokens: int
    restored_tokens: int  # tokens covered by the frame restored (or already in the slot)
    read_tokens: int  # tokens the engine reports it read (`prompt_n`), when known
    waited_s: float  # time spent waiting for the worker to yield
    total_s: float
    frame_depth: int  # how many layers the frame used covers (0 = none)


@dataclass
class Stats:
    frames_computed: int = 0
    frames_reused: int = 0
    tokens_read_background: int = 0
    background_s: float = 0.0
    chunks_abandoned: int = 0
    events: list[dict[str, Any]] = field(default_factory=list)


class PreStaC:
    """The wanted stack, a background prefetch worker, and `ask`.

    The worker is one thread doing one engine call at a time. Reads are split
    into chunks of `chunk` tokens; between chunks the worker checks that the
    frame it computes is still wanted and that no question is waiting.
    Call `step()` directly (tests) or `start()` for the background thread.
    """

    def __init__(self, engine: Engine, store: Store, namespace: str, chunk: int = 64, debounce_s: float = 0.0):
        self.engine, self.store, self.namespace = engine, store, namespace
        self.chunk, self.debounce_s = chunk, debounce_s
        self.wanted: list[Layer] = []
        self.slot: tuple[str, int] | None = None  # (key of the frame held, its depth) or None if unknown
        self.slot_tokens: list[int] = []  # tokens the slot holds, when known (also mid-frame)
        self.paused = False
        self.stats = Stats()
        self._lock = threading.RLock()  # one engine call at a time
        self._changed = threading.Condition()
        self._asking = 0
        self._stop = False
        self._changed_at = 0.0
        self._thread: threading.Thread | None = None

    # navigation -----------------------------------------------------------
    def set_stack(self, layers: list[Layer]) -> None:
        with self._changed:
            self.wanted = list(layers)
            self._changed_at = time.monotonic()
            self.stats.events.append({"t": time.time(), "event": "set_stack", "layers": [l.name for l in layers]})
            self._changed.notify_all()

    def push(self, layer: Layer) -> None:
        self.set_stack(self.wanted + [layer])

    def pop(self) -> None:
        self.set_stack(self.wanted[:-1])

    def replace_top(self, layer: Layer) -> None:
        self.set_stack(self.wanted[:-1] + [layer])

    def pause(self) -> None:
        self.paused = True

    def resume(self) -> None:
        with self._changed:
            self.paused = False
            self._changed.notify_all()

    # queries --------------------------------------------------------------
    def keys(self, layers: list[Layer] | None = None) -> list[str]:
        return frame_keys(self.namespace, self.wanted if layers is None else layers)

    def ready(self, layers: list[Layer] | None = None) -> int:
        """How many frames of the stack, from the bottom, are on disk."""
        depth = 0
        for key in self.keys(layers):
            if not self.store.lookup(key):
                break
            depth += 1
        return depth

    # the worker -------------------------------------------------------------
    def step(self) -> bool:
        """Do one chunk of prefetch work. Returns False when there is nothing to do."""
        with self._changed:
            if self.paused or self._asking or not self.wanted:
                return False
            if self.debounce_s and time.monotonic() - self._changed_at < self.debounce_s:
                return False
            layers = list(self.wanted)
        keys = self.keys(layers)
        depth = self.ready(layers)
        if depth == len(layers):
            return False
        target_key = keys[depth]
        target_tokens = [t for layer in layers[:depth + 1] for t in layer.tokens]
        with self._lock:
            started = time.perf_counter()
            # Make the slot hold a prefix of the target frame.
            if not self._slot_is_prefix_of(target_tokens):
                if depth == 0:
                    self.slot_tokens = []  # nothing to restore below L0: start from an empty slot
                else:
                    self.engine.restore(self.store.bin(keys[depth - 1]).name)
                    self.store.touch(keys[depth - 1])
                    self.slot_tokens = [t for layer in layers[:depth] for t in layer.tokens]
                    self.stats.frames_reused += 1
            end = min(len(self.slot_tokens) + self.chunk, len(target_tokens))
            timings = self.engine.extend(target_tokens[:end])
            self.slot_tokens = target_tokens[:end]
            self.slot = None
            self.stats.tokens_read_background += timings.get("prompt_n") or 0
            if end == len(target_tokens):
                self.engine.save(self.store.tmp_name(target_key))
                self.store.commit(target_key, {"layers": [l.name for l in layers[:depth + 1]],
                                               "tokens": len(target_tokens), "namespace": self.namespace})
                self.slot = (target_key, depth + 1)
                self.stats.frames_computed += 1
                self.store.evict(pinned=set(keys))
            self.stats.background_s += time.perf_counter() - started
        # A stale target is simply dropped: the next step picks the new wanted stack.
        with self._changed:
            if keys[depth] not in self.keys() and end < len(target_tokens):
                self.stats.chunks_abandoned += 1
        return True

    def _slot_is_prefix_of(self, tokens: list[int]) -> bool:
        n = len(self.slot_tokens)
        return n > 0 and n <= len(tokens) and tokens[:n] == self.slot_tokens

    def start(self) -> None:
        def run() -> None:
            while not self._stop:
                if not self.step():
                    with self._changed:
                        self._changed.wait(0.05)
        self._thread = threading.Thread(target=run, daemon=True, name="prestac")
        self._thread.start()

    def stop(self) -> None:
        self._stop = True
        with self._changed:
            self._changed.notify_all()
        if self._thread:
            self._thread.join(30)

    def wait_ready(self, timeout: float) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.ready() == len(self.wanted):
                return True
            time.sleep(0.02)
        return False

    # the question -----------------------------------------------------------
    def ask(self, tail: Layer, body: dict[str, Any]) -> AskResult:
        """Restore the deepest ready frame of the wanted stack, then read the rest and answer."""
        started = time.perf_counter()
        with self._changed:
            self._asking += 1
            layers = list(self.wanted)
        try:
            with self._lock:  # waits at most for the chunk in progress
                waited = time.perf_counter() - started
                keys = self.keys(layers)
                tokens = [t for layer in layers for t in layer.tokens] + list(tail.tokens)
                depth = self.ready(layers)
                if self._slot_is_prefix_of(tokens) and len(self.slot_tokens) >= sum(
                        len(l.tokens) for l in layers[:depth]):
                    restored = len(self.slot_tokens)  # the slot already holds at least the frame
                elif depth:
                    self.engine.restore(self.store.bin(keys[depth - 1]).name)
                    self.store.touch(keys[depth - 1])
                    restored = sum(len(l.tokens) for l in layers[:depth])
                else:
                    restored = 0
                reply = self.engine.answer(tokens, body)
                self.slot_tokens, self.slot = [], None  # the slot now holds the question too
                read = (reply.get("timings") or {}).get("prompt_n") or 0
                return AskResult(reply, len(tokens), restored, read, waited,
                                 time.perf_counter() - started, depth)
        finally:
            with self._changed:
                self._asking -= 1
                self._changed.notify_all()
