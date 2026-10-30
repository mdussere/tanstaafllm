"""Mike 9.2: PreStaC's store and stack, with a fake engine (deterministic, no model)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "src" / "mike"))
import prestac  # noqa: E402
from prestac import Layer, PreStaC, Store  # noqa: E402


class FakeEngine:
    """A slot that holds token ids; reading costs one unit per token not already held."""

    def __init__(self, root: Path):
        self.root, self.slot, self.read, self.calls = root, [], 0, []

    def _cached(self, tokens):
        n = len(self.slot)
        return n if n <= len(tokens) and tokens[:n] == self.slot else 0

    def restore(self, filename):
        self.calls.append(("restore", filename))
        self.slot = json.loads((self.root / filename).read_text())

    def save(self, filename):
        self.calls.append(("save", filename))
        (self.root / filename).write_text(json.dumps(self.slot))

    def extend(self, tokens):
        cached = self._cached(tokens)
        self.read += len(tokens) - cached
        self.calls.append(("extend", len(tokens) - cached))
        self.slot = list(tokens)
        return {"prompt_n": len(tokens) - cached, "cache_n": cached}

    def answer(self, tokens, body):
        cached = self._cached(tokens)
        self.read += len(tokens) - cached
        self.calls.append(("answer", len(tokens) - cached))
        self.slot = list(tokens) + [-1]  # the generated tokens
        return {"content": "ok", "timings": {"prompt_n": len(tokens) - cached, "cache_n": cached}}


def layer(name, start, n):
    return Layer(name, tuple(range(start, start + n)))


L0, DESK_A, DESK_B, TERM = layer("L0", 0, 100), layer("A", 1000, 10), layer("B", 2000, 10), layer("T", 3000, 20)
Q = layer("Q", 9000, 5)


def make(tmp_path, chunk=64):
    store = Store(tmp_path / "frames")
    engine = FakeEngine(store.root)
    return PreStaC(engine, store, "test-ns", chunk=chunk), engine


def drain(cache):
    while cache.step():
        pass


def test_keys_depend_on_every_token_below():
    a = prestac.frame_keys("ns", [L0, DESK_A])
    b = prestac.frame_keys("ns", [L0, DESK_B])
    assert a[0] == b[0] and a[1] != b[1]
    assert prestac.frame_keys("other", [L0])[0] != a[0]


def test_prefetch_then_ask_reads_only_the_question(tmp_path):
    cache, engine = make(tmp_path)
    cache.set_stack([L0, DESK_A])
    drain(cache)
    assert cache.ready() == 2
    engine.read = 0
    result = cache.ask(Q, {})
    assert result.restored_tokens == 110 and engine.read == 5 and result.frame_depth == 2


def test_pop_costs_nothing_and_restores_the_frame_below(tmp_path):
    cache, engine = make(tmp_path)
    cache.set_stack([L0, DESK_A, TERM])
    drain(cache)
    cache.pop()
    assert cache.step() is False  # the frame below is already on disk
    engine.read = 0
    result = cache.ask(Q, {})
    assert ("restore", cache.store.bin(cache.keys()[-1]).name) in engine.calls
    assert result.restored_tokens == 110 and engine.read == 5


def test_switching_back_reuses_the_older_frame(tmp_path):
    cache, engine = make(tmp_path)
    cache.set_stack([L0, DESK_A]); drain(cache)
    cache.set_stack([L0, DESK_B]); drain(cache)
    read_before = engine.read
    cache.set_stack([L0, DESK_A]); drain(cache)
    assert engine.read == read_before  # nothing recomputed
    assert cache.stats.frames_computed == 3  # L0, A, B


def test_question_before_prefetch_reads_what_is_missing(tmp_path):
    cache, engine = make(tmp_path)
    cache.set_stack([L0]); drain(cache)
    cache.push(TERM)  # not prefetched yet
    engine.read = 0
    result = cache.ask(Q, {})
    assert result.frame_depth == 1 and result.restored_tokens == 100 and engine.read == 25


def test_reads_are_chunked_and_a_stale_frame_is_abandoned(tmp_path):
    cache, engine = make(tmp_path, chunk=16)
    cache.set_stack([L0])
    assert cache.step() and engine.calls[-1] == ("extend", 16)
    cache.set_stack([layer("L0b", 50000, 30)])  # navigation moved on before L0 was done
    drain(cache)
    assert not cache.store.lookup(prestac.frame_keys("test-ns", [L0])[0])
    assert cache.ready() == 1


def test_pause_holds_the_prefetch(tmp_path):
    cache, _ = make(tmp_path)
    cache.pause()
    cache.set_stack([L0])
    assert cache.step() is False and cache.ready() == 0
    cache.resume()
    drain(cache)
    assert cache.ready() == 1


def test_eviction_keeps_pinned_frames(tmp_path):
    store = Store(tmp_path / "s", budget_bytes=1)
    for key in ("a", "b"):
        (store.root / store.tmp_name(key)).write_text("x" * 10)
        store.commit(key, {})
    dropped = store.evict(pinned={"b"})
    assert dropped == ["a"] and store.lookup("b") and not store.lookup("a")


def test_background_thread(tmp_path):
    cache, engine = make(tmp_path)
    cache.start()
    try:
        cache.set_stack([L0, DESK_A, TERM])
        assert cache.wait_ready(5)
        engine.read = 0
        assert cache.ask(Q, {}).restored_tokens == 130 and engine.read == 5
    finally:
        cache.stop()
