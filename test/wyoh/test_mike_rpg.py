"""Wyoh 6.13 look B: Mike's RPG dialogue window. Contract: mike_rpg.feature.

The transcript parser runs in the default suite; the rendered session needs pygame:
    uv run --group camp-currie pytest test/wyoh/test_mike_rpg.py
"""

from __future__ import annotations

import os
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "wyoh" / "apps" / "mike"))
from mike_rpg import Client, Transcript, View  # noqa: E402

FAKE = [sys.executable, str(Path(__file__).with_name("fixtures") / "fake_mike.py")]


def test_the_transcript_separates_titles_notices_question_and_answer():
    t = Transcript()
    t.feed("\x1b]2;Mike — starting\x07Mike is starting…\r\nReady (4.95 s). Ask.\r\n\x1b]2;Mike — ready\x07> ")
    assert t.phase == "ready" and t.notices == ["Mike is starting…", "Ready (4.95 s). Ask."]
    t.sent("hello")
    t.feed("hello\r\n\x1b]2;Mike — thinking\x07Hel")
    assert t.phase == "thinking" and t.answer == "Hel"
    t.feed("lo \x1b[36mthere\x1b[0m!\r\n")
    t.feed("\x1b]2;Mike — ready\x07> ")
    assert t.answer == "Hello there!" and t.mode == "notice" and t.phase == "ready"


def test_the_phase_comes_from_the_title():
    for title, phase in (("Mike — asks: stop Mannie?", "asks"), ("Mike — waiting for Mannie", "waiting"),
                         ("Mike — busy", "busy"), ("something else", "starting")):
        t = Transcript(title=title)
        assert t.phase == phase


def wait(client, check, timeout=10.0):
    deadline = time.monotonic() + timeout
    while not check(client.transcript):
        assert time.monotonic() < deadline, client.transcript
        client.pump()
        time.sleep(0.02)


def test_a_rendered_session_with_a_fake_mike(monkeypatch):
    pygame = pytest.importorskip("pygame")
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    out = ROOT / "results/wyoh/mike-rpg" / datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out.mkdir(parents=True, exist_ok=False)
    pygame.display.init(); pygame.font.init()
    screen = pygame.display.set_mode((720, 720))
    view = View(pygame)

    def shot(name, t, typing="", extra=10.0):
        view.last = time.monotonic() - extra  # let the typewriter catch up
        view.draw(screen, t, typing, time.monotonic())
        pygame.image.save(screen, str(out / f"{name}.png"))

    client = Client(FAKE)
    try:
        wait(client, lambda t: t.phase == "ready")
        shot("1-ready", client.transcript)
        shot("2-typing", client.transcript, typing="hello")
        client.send("hello")
        wait(client, lambda t: t.phase == "thinking")
        view.shown = 0.0
        view.last = time.monotonic()
        view.draw(screen, client.transcript, "", time.monotonic())
        pygame.image.save(screen, str(out / "3-thinking.png"))
        wait(client, lambda t: t.phase == "ready" and t.mode == "notice")
        assert client.transcript.answer.strip() == "Hello! I am Mike, Luna's small local brain. How can I help?"
        shot("4-answer", client.transcript)
    finally:
        client.stop()
    os.environ["FAKE_MIKE_ASK"] = "1"
    try:
        client = Client(FAKE)
        wait(client, lambda t: t.phase == "asks")
        shot("5-asks", client.transcript)
        client.key(b"\r")
        wait(client, lambda t: t.phase == "waiting")
        wait(client, lambda t: t.phase == "ready")
    finally:
        os.environ.pop("FAKE_MIKE_ASK")
        client.stop()
        pygame.quit()


def test_dictation_starts_then_stops_and_returns_the_final_text():
    from mike_rpg import Dictation
    script = ROOT / "worklines/mycroft/scripts/mycroft_dictate.py"
    d = Dictation([sys.executable, str(script), "--resident", "--fake", "hello mike", "--fake-interval", "0.05"])
    try:
        deadline = time.monotonic() + 20
        while d.state != "idle":
            assert time.monotonic() < deadline and d.state != "error", d.state
            d.pump(); time.sleep(0.02)
        d.toggle()                                   # F1 / L1: start
        assert d.state == "listening"
        while d.text != "hello mike":
            assert time.monotonic() < deadline, d.text
            d.pump(); time.sleep(0.02)
        d.toggle()                                   # again: stop and send
        final = None
        while final is None:
            assert time.monotonic() < deadline
            final = d.pump(); time.sleep(0.02)
        assert final == "hello mike" and d.state == "idle"
    finally:
        d.stop()


def test_space_dictates_and_sends_to_mike_in_the_real_window(monkeypatch):
    """The whole window (main loop), a fake Mike and Mycroft's --fake provider; Space is pressed twice."""
    pygame = pytest.importorskip("pygame")
    import mike_rpg
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    script = ROOT / "worklines/mycroft/scripts/mycroft_dictate.py"
    monkeypatch.setenv("MIKE_RPG_DICTATE", f"{sys.executable} {script} --resident --fake 'hello' --fake-interval 0.05")
    seen, real_get, start = {"sent": None}, pygame.event.get, time.monotonic()
    original_send = mike_rpg.Client.send

    def send(self, question):
        seen["sent"] = question
        original_send(self, question)
    monkeypatch.setattr(mike_rpg.Client, "send", send)
    steps = iter([(2.0, pygame.K_SPACE), (3.0, pygame.K_SPACE)])
    nxt = next(steps)

    def events():
        nonlocal nxt
        out = list(real_get())
        if nxt and time.monotonic() - start > nxt[0]:
            out.append(pygame.event.Event(pygame.KEYDOWN, key=nxt[1], mod=0, unicode=" "))
            out.append(pygame.event.Event(pygame.TEXTINPUT, text=" "))
            nxt = next(steps, None)
        if seen["sent"] or time.monotonic() - start > 15:
            out.append(pygame.event.Event(pygame.QUIT))
        return out
    monkeypatch.setattr(pygame.event, "get", events)
    mike_rpg.main(["--", *FAKE])
    assert seen["sent"] == "hello"


def test_other_osc_sequences_are_dropped_even_when_split():
    t = Transcript()
    t.feed("\x1b]3008;start=baf9;user=michael\x1b")
    t.feed("\\Mike is starting…\r\n")
    assert t.notices == ["Mike is starting…"]


def test_finished_exchanges_go_to_the_history_and_can_be_browsed():
    pygame = pytest.importorskip("pygame")
    t = Transcript()
    for q, a in (("one", "first answer"), ("two", "second answer")):
        t.sent(q)
        t.feed(f"{q}\r\n{a}\r\n> ")
    assert t.history == [("one", "first answer"), ("two", "second answer")]
    view = View.__new__(View)
    view.back, view.scroll, view.shown = 0, {"top": 0, "bottom": 0}, 0.0
    view.browse(1, t); view.browse(1, t); view.browse(1, t)   # stick left three times: stops at the oldest
    assert view.back == 2
    view.browse(-1, t)                                        # stick right: forward
    assert view.back == 1
