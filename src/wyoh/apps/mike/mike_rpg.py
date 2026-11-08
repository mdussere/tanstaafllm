#!/usr/bin/env python3
"""Mike's RPG dialogue window (Wyoh 6.13, look B).

A pygame window with Wayland app_id "mike" that runs Mike's own client
(mike.py) unchanged in a pseudo-terminal and stages what it prints: the
question above, Mike's portrait in the middle, the answer typed letter by
letter in a dialogue box. The window mirrors the client's titles ("Mike —
ready", "Mike — asks: stop Mannie?" ...), so FN+B and the Mike <-> Mannie
switch keep working. Keys: typed text and Return send a question (FN+B types
them); on Mike's question, Return = yes, Escape = no.

    python3 mike_rpg.py [-- command ...]     # default: python3 $MIKE_HOME/mike.py
"""

from __future__ import annotations

import json
import math
import os
import pty
import re
import select
import shlex
import signal
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
OSC = re.compile(r"\x1b\]2;(.*?)\x07")
# every other OSC sequence (e.g. runuser's OSC 3008 session context), ended by BEL or ST
OTHER_OSC = re.compile(r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)")
CSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


@dataclass
class Transcript:
    """What the client said, parsed from its terminal output. Pure: tested without a display."""
    title: str = "Mike — starting"
    notices: list[str] = field(default_factory=list)   # lines that are neither questions nor answers
    question: str = ""
    answer: str = ""
    mode: str = "notice"          # notice | echo | answer
    history: list[tuple[str, str]] = field(default_factory=list)  # finished (question, answer) pairs
    _pending: str = ""
    _raw: str = ""

    def sent(self, question: str) -> None:
        self.question, self.answer, self.mode = question, "", "echo"

    def feed(self, data: str) -> None:
        for title in OSC.findall(self._raw + data):
            self.title = title
        text = CSI.sub("", OTHER_OSC.sub("", OSC.sub("", self._raw + data))).replace("\r", "")
        self._raw = ""
        cut = text.find("\x1b")  # an unfinished sequence (split across reads): keep it for the next one
        if cut >= 0:
            self._raw, text = text[cut:], text[:cut]
        self._pending += text
        while self._pending:
            if self.mode == "echo":  # the terminal echoes the question: skip that line
                if "\n" not in self._pending:
                    return
                self._pending = self._pending.split("\n", 1)[1]
                self.mode = "answer"
            elif self.mode == "answer":
                end = self._pending.find("\n> ")
                if end < 0:
                    keep = 2 if self._pending.endswith(("\n", "\n>")) else 0  # a prompt may be arriving
                    self.answer += self._pending[: len(self._pending) - keep]
                    self._pending = self._pending[len(self._pending) - keep:]
                    return
                self.answer += self._pending[:end]
                self._pending, self.mode = self._pending[end + 3:], "notice"
                if not self.question.startswith("/"):
                    self.history.append((self.question, self.answer.strip()))
            else:  # notice lines; a lone "> " is the prompt
                if "\n" not in self._pending:
                    if self._pending in ("> ", ">"):
                        self._pending = ""
                    return
                line, self._pending = self._pending.split("\n", 1)
                line = line.removeprefix("> ").strip()
                if line:
                    self.notices = (self.notices + [line])[-3:]

    @property
    def phase(self) -> str:
        return self.title.removeprefix("Mike — ").split(":")[0].split(" ")[0] if self.title.startswith("Mike — ") else "starting"


class Client:
    """mike.py in a pseudo-terminal: raw keys (the Mannie question) keep working."""

    def __init__(self, command: list[str]) -> None:
        self.pid, self.fd = pty.fork()
        if self.pid == 0:
            os.execvp(command[0], command)
        self.transcript = Transcript()

    def pump(self) -> bool:
        changed = False
        while select.select([self.fd], [], [], 0)[0]:
            try:
                data = os.read(self.fd, 4096)
            except OSError:
                return changed
            if not data:
                return changed
            self.transcript.feed(data.decode("utf-8", "replace"))
            changed = True
        return changed

    def send(self, question: str) -> None:
        self.transcript.sent(question)
        os.write(self.fd, question.encode() + b"\r")

    def key(self, raw: bytes) -> None:
        os.write(self.fd, raw)

    def alive(self) -> bool:
        return os.waitpid(self.pid, os.WNOHANG) == (0, 0)

    def stop(self) -> None:
        try:
            os.kill(self.pid, signal.SIGHUP)  # mike.py stops its server on SIGHUP
        except ProcessLookupError:
            pass


class Dictation:
    """Mycroft's resident dictation provider (worklines/mycroft/scripts/mycroft_dictate.py,
    protocol in its docstring): loaded once; start/stop per utterance; the final text is sent to Mike.
    Adam, 2026-11-03: L1 or L2 (keyboard F1 or F2) starts dictating; the same again sends."""

    def __init__(self, command: list[str]) -> None:
        import subprocess
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                        text=True, bufsize=1)
        self.state, self.text, self._buffer = "loading", "", ""   # loading idle listening finishing error

    def _send(self, op: str) -> None:
        try:
            self.process.stdin.write(json.dumps({"op": op}) + "\n")
            self.process.stdin.flush()
        except OSError:
            self.state = "error"

    def toggle(self) -> None:
        if self.state == "idle":
            self.text, self.state = "", "listening"
            self._send("start")
        elif self.state == "listening":
            self.state = "finishing"
            self._send("stop")

    def pump(self) -> str | None:
        """Read the provider's lines; returns the final text once an utterance ends."""
        final = None
        fd = self.process.stdout.fileno()
        while select.select([fd], [], [], 0)[0]:
            chunk = os.read(fd, 4096).decode("utf-8", "replace")
            if not chunk:
                self.state = "error"
                break
            self._buffer += chunk
            while "\n" in self._buffer:
                line, self._buffer = self._buffer.split("\n", 1)
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                op = event.get("op")
                if op == "ready":
                    self.state = "idle"
                elif op == "partial":
                    self.text = event.get("text", "")
                elif op == "final":
                    self.text, self.state, final = "", "idle", event.get("text", "")
                elif op == "error":
                    self.state = "idle" if self.state != "loading" else "error"
        return final

    def stop(self) -> None:
        try:
            self.process.stdin.close()
            self.process.wait(timeout=3)
        except Exception:
            self.process.kill()


# --- drawing -----------------------------------------------------------------

NAVY, DEEP, PANEL = (11, 16, 38), (42, 22, 80), (16, 22, 52)
BORDER, AMBER, WHITE = (107, 95, 168), (242, 169, 59), (232, 238, 246)
CYAN, DIM, VIOLET = (79, 216, 232), (128, 140, 176), (75, 42, 122)
CPS = 40  # letters per second in the dialogue box


class View:
    def __init__(self, pygame) -> None:
        self.pg = pygame
        fonts = HERE
        self.title_font = lambda size: pygame.font.Font(str(fonts / "pressstart2p_PressStart2P-Regular.ttf"), size)
        self.body_font = lambda size: pygame.font.Font(str(fonts / "vt323_VT323-Regular.ttf"), size)
        self.label, self.body, self.small = self.title_font(16), self.body_font(36), self.body_font(28)
        self.portrait = pygame.transform.smoothscale(pygame.image.load(str(HERE / "mike-portrait.png")), (208, 208))
        self.sky = pygame.Surface((720, 720))
        for y in range(720):
            k = y / 719
            self.sky.fill(tuple(int(NAVY[i] + (DEEP[i] - NAVY[i]) * k) for i in range(3)), (0, y, 720, 1))
        import random
        rng = random.Random(7)
        for _ in range(110):
            colour = AMBER if rng.random() < 0.25 else WHITE
            self.sky.fill(tuple(int(c * rng.uniform(0.35, 0.9)) for c in colour), (rng.randrange(720), rng.randrange(720), 2, 2))
        self.shown, self.last = 0.0, time.monotonic()
        self.scroll = {"top": 0, "bottom": 0}  # lines scrolled back from the end; 0 follows the text
        self.back = 0  # history: 0 is the live exchange, n the n-th finished one before it

    def browse(self, step: int, t: Transcript) -> None:
        """Stick left (+1) goes back in the history, right (-1) comes forward."""
        self.back = max(0, min(len(t.history), self.back + step))
        self.scroll = {"top": 0, "bottom": 0}
        if self.back == 0:
            self.shown = float(len(t.answer))  # back to the live exchange: no retyping

    def scrolled(self, zone: str, step: int) -> None:
        self.scroll[zone] = max(0, self.scroll[zone] + step)

    def window(self, lines: list[str], zone: str, size: int) -> tuple[list[str], int, int]:
        """The visible slice of `lines`, with the offset clamped; returns (slice, first, total)."""
        total = len(lines)
        self.scroll[zone] = min(self.scroll[zone], max(0, total - size))
        end = total - self.scroll[zone]
        first = max(0, end - size)
        return lines[first:end], first, total

    def scrollbar(self, surf, x: int, top: int, height: int, first: int, size: int, total: int) -> None:
        if total <= size:
            return
        self.pg.draw.rect(surf, BORDER, (x, top, 6, height))
        thumb = max(14, height * size // total)
        y = top + (height - thumb) * first // max(1, total - size)
        self.pg.draw.rect(surf, AMBER, (x, y, 6, thumb))

    def wrap(self, text: str, font, width: int) -> list[str]:
        lines = []
        for paragraph in text.split("\n"):
            line = ""
            for word in paragraph.split():
                trial = f"{line} {word}".strip()
                if font.size(trial)[0] <= width:
                    line = trial
                else:
                    lines.append(line)
                    line = word
            lines.append(line)
        return lines

    def box(self, surf, rect, edge, fill=NAVY, double=False) -> None:
        pg = self.pg
        pg.draw.rect(surf, fill, rect)
        pg.draw.rect(surf, edge, rect, width=3)
        if double:
            pg.draw.rect(surf, BORDER, rect.inflate(-14, -14), width=2)

    def tag(self, surf, x, y, word, colour) -> None:
        w = self.label.size(word)[0] + 28
        rect = self.pg.Rect(x, y, w, 34)
        self.box(surf, rect, WHITE, VIOLET)
        surf.blit(self.label.render(word, True, colour), (x + 14, y + 9))

    stats: list[str] = []

    def draw(self, surf, t: Transcript, typing: str, now: float, dictation: str = "", heard: str = "") -> None:
        pg = self.pg
        t_history = t.history
        dt, self.last = now - self.last, now
        if t.mode == "echo" or (t.answer and self.shown > len(t.answer)):
            self.shown = 0.0
            self.scroll["bottom"] = 0  # a new answer: follow it
        self.shown = min(len(t.answer), self.shown + dt * CPS * (3 if len(t.answer) - self.shown > 120 else 1))
        surf.blit(self.sky, (0, 0))
        # the question (or what FN+B is typing)
        listening = dictation in ("listening", "finishing")
        if t.mode == "echo":
            self.back = 0  # a new question: back to the live exchange
        if self.back and not listening:  # browsing the history: a finished exchange, shown whole
            past_q, past_a = t.history[-self.back]
            t = Transcript(title=t.title, question=past_q, answer=past_a)
            self.shown = len(past_a)
        q = heard if listening else (typing or t.question)
        top = pg.Rect(24, 24, 672, 130)
        self.box(surf, top, AMBER if listening else CYAN, PANEL)
        label = ("LISTENING" if dictation == "listening" else "...") if listening else ("YOU" if q else "MIKE")
        if self.back and not listening:
            label = f"YOU  {len(t_history) - self.back + 1}/{len(t_history)}"
        surf.blit(self.label.render(label, True, AMBER if listening else CYAN), (44, 38))
        if listening and int(now * 2) % 2 == 0:
            pg.draw.circle(surf, (232, 96, 90), (660, 46), 9)
        if q:
            rows, first, total = self.window(self.wrap(q, self.small, 610) or [""], "top", 2)
            self.scrollbar(surf, 676, 64, 80, first, 2, total)
        else:
            rows = [("Space, L1/L2 or F1/F2: dictate, again to send" if dictation else "L1: dictate, L1 again to send")]
        for i, row in enumerate(rows):
            cursor = "_" if typing and i == len(rows) - 1 and int(now * 2) % 2 == 0 else ""
            surf.blit(self.small.render(row + cursor, True, WHITE if q else DIM), (44, 70 + i * 32))
        # Mike's portrait, with a small life of its own
        phase = t.phase
        bob = int(3 * math.sin(now * 2.2))
        frame = pg.Rect(252, 184 + bob, 216, 216)
        self.box(surf, frame.inflate(8, 8), AMBER, PANEL)
        surf.blit(self.portrait, frame.move(4, 4))
        if phase == "thinking" and not t.answer:  # thinking: three dots pulse under the portrait
            for i in range(3):
                on = int(now * 3) % 3 == i
                pg.draw.rect(surf, AMBER if on else BORDER, (330 + i * 24, 412 + bob, 14, 14))
        status = {"ready": "READY", "thinking": "THINKING", "speaking": "SPEAKING", "starting": "STARTING", "asks": "ASKS YOU",
                  "waiting": "WAITING FOR MANNIE", "busy": "BUSY"}.get(phase, phase.upper())
        # the dialogue box: the answer, typed; or Mike's notices
        box = pg.Rect(16, 444, 688, 228)
        self.box(surf, box, WHITE, NAVY, double=True)
        self.tag(surf, 40, 428, "MIKE", AMBER)
        if t.answer or t.mode == "answer":
            text, colour = t.answer[: int(self.shown)], WHITE
        else:
            text, colour = "\n".join(t.notices[-2:]), CYAN
        lines, first, total = self.window(self.wrap(text, self.body, 620), "bottom", 5)
        self.scrollbar(surf, 686, 466, 190, first, 5, total)
        for i, row in enumerate(lines):
            surf.blit(self.body.render(row, True, colour), (44, 474 + i * 38))
        if t.answer and int(self.shown) >= len(t.answer) and phase == "ready" and int(now * 2) % 2 == 0:
            pg.draw.polygon(surf, AMBER, ((662, 650), (682, 650), (672, 662)))
        hint = ("A yes · B no" if phase == "asks" else "Space, L1/L2 or F1/F2 again: send" if listening
                else "Space/L1: dictate · X: new" if dictation == "idle" else "dictation loading..." if dictation == "loading"
                else "dictation unavailable: type and Return" if dictation == "error" else "L1 dictate · X new")
        surf.blit(self.small.render(hint, True, DIM), (24, 684))
        line = ""
        if self.stats:
            line = self.stats[-self.back] if self.back and self.back <= len(self.stats) else self.stats[-1]
        if line:
            counter = self.small.render(line, True, AMBER if self.back else DIM)
            surf.blit(counter, counter.get_rect(topright=(696, 684)))


def token_stats(path: Path) -> list[str]:
    """The token counter (Adam, 2026-11-03), one line per answered turn of this session, in order:
    input and output tokens since the conversation began (or since /new), and the context's size
    after that answer, from the turns mike.py logs. The last line is the live one; browsing the
    history shows the line of the exchange shown, so question, answer and counts stay together."""
    try:
        with open(path, "rb") as log:
            log.seek(0, os.SEEK_END)
            log.seek(max(0, log.tell() - 65536))
            lines = log.read().decode("utf-8", "replace").splitlines()[1:]
    except OSError:
        return []
    records = []
    for line in lines:
        try:
            records.append(json.loads(line))
        except ValueError:
            continue
    if not records:
        return []
    session = records[-1].get("session")
    read = wrote = context = 0
    lines_out = []
    for record in records:
        if record.get("session") != session:
            continue
        if record.get("event") == "new":
            read = wrote = context = 0
        elif "predicted_n" in record:
            read += record.get("prompt_n") or 0
            wrote += record.get("predicted_n") or 0
            context = (record.get("prompt_tokens") or 0) + (record.get("predicted_n") or 0)
            lines_out.append(f"in {read} · out {wrote} · ctx {context}")
    return lines_out


_wyoh_seen = [0.0, "", ""]  # last read, state, live text


def wyoh_dictation(path: str = "/run/wyoh/gamepad.json") -> str:
    """Wyoh's direct dictation state ("listening", "stopping", "loading" or ""), read at most 4 times a second."""
    now = time.monotonic()
    if now - _wyoh_seen[0] >= 0.25:
        _wyoh_seen[0] = now
        try:
            with open(path, encoding="utf-8") as status:
                data = json.load(status)
            value = data.get("direct", "")
            _wyoh_seen[1] = {"loading": "finishing", "stopping": "finishing"}.get(value, value)
            _wyoh_seen[2] = data.get("direct_text", "") if value else ""
        except (OSError, ValueError):
            _wyoh_seen[1], _wyoh_seen[2] = "", ""
    return _wyoh_seen[1]


def main(argv: list[str]) -> int:
    command = argv[argv.index("--") + 1:] if "--" in argv else [sys.executable, str(Path(os.environ.get("MIKE_HOME", "~/.local/opt/mike")).expanduser() / "mike.py")]
    os.environ.setdefault("SDL_VIDEO_WAYLAND_WMCLASS", "mike")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    import pygame
    pygame.display.init()
    pygame.font.init()
    screen = pygame.display.set_mode((720, 720))
    client, view = Client(command), View(pygame)
    typing, caption = "", ""
    dictate = os.environ.get("MIKE_RPG_DICTATE", "")
    dictation = Dictation(shlex.split(dictate)) if dictate else None
    pygame.joystick.init()
    pads = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]  # a pad on the desk; on Luna Wyoh owns it
    pygame.key.start_text_input()
    skip_space = False
    stats_path = Path(os.environ.get("MIKE_RPG_STATS", Path.home() / ".local/state/mike/chat.jsonl"))
    stats_read = 0.0
    SCROLL_KEYS = {pygame.K_F5: ("top", 1), pygame.K_F6: ("top", -1), pygame.K_F7: ("bottom", 1), pygame.K_F8: ("bottom", -1),
                   pygame.K_PAGEUP: ("bottom", 3), pygame.K_PAGEDOWN: ("bottom", -3)}
    try:
        while True:
            client.pump()
            t = client.transcript
            if t.title != caption:
                caption = t.title
                pygame.display.set_caption(caption)  # Sway reads it: FN+B waits for "Mike — ready"
            if dictation is not None:
                heard = dictation.pump()
                if heard and heard.strip() and t.phase in ("ready", "thinking"):
                    client.send(heard.strip())
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return 0
                listening = dictation is not None and dictation.state in ("listening", "finishing")
                # Space dictates only when nothing is being typed (Adam, 2026-11-03), so it still types spaces
                space = event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and (not typing or listening)
                dictate_key = (space or (event.type == pygame.KEYDOWN and event.key in (pygame.K_F1, pygame.K_F2))
                               or (event.type == pygame.JOYBUTTONDOWN and event.button in (4, 6)))  # L1, L2 on common pads
                if dictate_key:
                    if t.phase == "speaking":  # 6.16: cut Mike's voice (Ctrl+C cuts answer and voice), then listen
                        client.key(b"\x03")
                    if dictation is not None:
                        dictation.toggle()
                    skip_space = space
                    continue
                if event.type == pygame.KEYDOWN and event.key in SCROLL_KEYS:
                    view.scrolled(*SCROLL_KEYS[event.key])  # sticks on Luna (Wyoh sends F5-F8), keys on the desk
                    continue
                if event.type == pygame.KEYDOWN and event.key == pygame.K_c and event.mod & pygame.KMOD_CTRL:
                    client.key(b"\x03")  # Ctrl+C: Mike stops its answer and its voice (Wyoh's L1 sends it on Luna)
                    continue
                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11 and t.phase == "ready":
                    client.send("/new")  # X on Luna: a new conversation
                    view.back, view.scroll = 0, {"top": 0, "bottom": 0}
                    continue
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_F9, pygame.K_F10):
                    view.browse(1 if event.key == pygame.K_F9 else -1, t)  # stick left: back; right: forward
                    continue
                if event.type == pygame.TEXTINPUT and skip_space and event.text == " ":
                    skip_space = False  # the space that started or stopped dictation is not text
                    continue
                if event.type == pygame.TEXTINPUT and t.phase != "asks":
                    typing += event.text
                elif event.type == pygame.KEYDOWN:
                    if t.phase == "asks" and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        client.key(b"\r")
                    elif t.phase == "asks" and event.key == pygame.K_ESCAPE:
                        client.key(b"\x1b")
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and typing.strip():
                        client.send(typing.strip())
                        typing = ""
                    elif event.key == pygame.K_BACKSPACE:
                        typing = typing[:-1]
            if not client.alive():
                return 0
            if time.monotonic() - stats_read > 2:
                stats_read, view.stats = time.monotonic(), token_stats(stats_path)
            if dictation is not None:
                state, heard = dictation.state, dictation.text
            else:  # on Luna, L1 is Wyoh's direct dictation (6.14): show its state, which the daemon publishes
                state = wyoh_dictation()
                heard = _wyoh_seen[2]
            view.draw(screen, t, typing, time.monotonic(), state, heard)
            pygame.display.flip()
            pygame.time.wait(33)
    finally:
        client.stop()
        if dictation is not None:
            dictation.stop()
        del pads
        pygame.quit()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
