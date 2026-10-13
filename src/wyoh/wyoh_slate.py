#!/usr/bin/env python3
"""Wyoh Slate: the multi-line text surface where Luna prepares input.

Proposal and user decisions: worklines/wyoh/docs/0600_01_slate-and-keyboard-proposal.md
(Wyoh Step 6).

The Slate runs inside a floating `foot` window that the gamepad daemon opens
on L1. L1 hides and shows it (the text stays), FN+X clears it, FN+A sends it.
Text arrives as terminal input: the daemon's virtual keyboard
(arrows, Return, Backspace, Delete, Shift, Ctrl+arrows), the on-screen
keyboard (wvkbd), or a USB keyboard. Commands with no key of their own
(select the word or the line, send, discard) arrive on a Unix socket from the
daemon, which also receives the text on send and delivers it.

Standard library only, and no curses: ArchR ships no terminfo database. The
module has a pure core (`Slate`, `Decoder`, `render`) and a thin terminal
adapter (`main`). The text is never written to disk or logged.
"""

from __future__ import annotations

import argparse
import codecs
import json
import os
import select
import signal
import socket
import sys
import termios
import tty
import unicodedata
from dataclasses import dataclass

Pos = tuple[int, int]  # (line, column) in logical lines


def _is_word(char: str) -> bool:
    return char.isalnum() or char == "_"


# --- Editor core -------------------------------------------------------------


class Slate:
    """Logical lines, a cursor, and an optional selection anchor."""

    def __init__(self, text: str = "") -> None:
        self.lines = text.split("\n")
        self.cursor: Pos = (len(self.lines) - 1, len(self.lines[-1]))
        self.anchor: Pos | None = None
        self.goal: int | None = None  # column kept while moving up and down

    # queries
    def text(self) -> str:
        return "\n".join(self.lines)

    def selection(self) -> tuple[Pos, Pos] | None:
        if self.anchor is None or self.anchor == self.cursor:
            return None
        return min(self.anchor, self.cursor), max(self.anchor, self.cursor)

    def selected_text(self) -> str:
        span = self.selection()
        if span is None:
            return ""
        (l0, c0), (l1, c1) = span
        if l0 == l1:
            return self.lines[l0][c0:c1]
        return "\n".join([self.lines[l0][c0:], *self.lines[l0 + 1:l1], self.lines[l1][:c1]])

    # editing
    def _delete_selection(self) -> bool:
        span = self.selection()
        self.anchor = None
        if span is None:
            return False
        (l0, c0), (l1, c1) = span
        self.lines[l0:l1 + 1] = [self.lines[l0][:c0] + self.lines[l1][c1:]]
        self.cursor = (l0, c0)
        return True

    def insert(self, text: str) -> None:
        """Insert text at the cursor, replacing any selection."""
        self._delete_selection()
        self.goal = None
        line, col = self.cursor
        head, tail = self.lines[line][:col], self.lines[line][col:]
        parts = text.split("\n")
        if len(parts) == 1:
            self.lines[line] = head + text + tail
            self.cursor = (line, col + len(text))
            return
        new = [head + parts[0], *parts[1:-1], parts[-1] + tail]
        self.lines[line:line + 1] = new
        self.cursor = (line + len(parts) - 1, len(parts[-1]))

    def newline(self) -> None:
        self.insert("\n")

    def insert_dictated(self, text: str) -> None:
        """Mycroft's final text (Step 12) at the cursor, spaced from the words around it."""
        text = text.strip()
        if not text:
            return
        line, col = self.cursor
        before = self.lines[line][:col]
        if self.selection() is None and before and not before[-1].isspace():
            text = " " + text
        self.insert(text)

    def backspace(self) -> None:
        self.goal = None
        if self._delete_selection():
            return
        line, col = self.cursor
        if col > 0:
            self.lines[line] = self.lines[line][:col - 1] + self.lines[line][col:]
            self.cursor = (line, col - 1)
        elif line > 0:
            previous = len(self.lines[line - 1])
            self.lines[line - 1:line + 1] = [self.lines[line - 1] + self.lines[line]]
            self.cursor = (line - 1, previous)

    def delete(self) -> None:
        self.goal = None
        if self._delete_selection():
            return
        line, col = self.cursor
        if col < len(self.lines[line]):
            self.lines[line] = self.lines[line][:col] + self.lines[line][col + 1:]
        elif line + 1 < len(self.lines):
            self.lines[line:line + 2] = [self.lines[line] + self.lines[line + 1]]

    # movement
    def _start_or_clear(self, select: bool) -> None:
        if select:
            if self.anchor is None:
                self.anchor = self.cursor
        else:
            self.anchor = None

    def move(self, direction: str, select: bool = False) -> None:
        """Arrow keys. Without Shift, a horizontal move first collapses a
        selection to its edge, as desktop editors do."""
        span = self.selection()
        if not select and span is not None and direction in ("left", "right"):
            self.cursor = span[0] if direction == "left" else span[1]
            self.anchor = None
            self.goal = None
            return
        self._start_or_clear(select)
        line, col = self.cursor
        if direction == "left":
            self.cursor = (line, col - 1) if col > 0 else ((line - 1, len(self.lines[line - 1])) if line > 0 else (0, 0))
            self.goal = None
        elif direction == "right":
            if col < len(self.lines[line]):
                self.cursor = (line, col + 1)
            elif line + 1 < len(self.lines):
                self.cursor = (line + 1, 0)
            self.goal = None
        elif direction in ("up", "down"):
            goal = col if self.goal is None else self.goal
            target = line - 1 if direction == "up" else line + 1
            if 0 <= target < len(self.lines):
                self.cursor = (target, min(goal, len(self.lines[target])))
            else:
                self.cursor = (line, 0) if direction == "up" else (line, len(self.lines[line]))
            self.goal = goal
        elif direction == "home":
            self.cursor = (line, 0)
            self.goal = None
        elif direction == "end":
            self.cursor = (line, len(self.lines[line]))
            self.goal = None

    def word(self, direction: str, select: bool = False) -> None:
        """Next/previous word (R1/R2, sent as Ctrl+Right/Left)."""
        self._start_or_clear(select)
        self.goal = None
        line, col = self.cursor
        text = self.lines[line]
        if direction == "right":
            if col >= len(text):
                if line + 1 < len(self.lines):
                    self.cursor = (line + 1, 0)
                return
            while col < len(text) and not _is_word(text[col]):
                col += 1
            while col < len(text) and _is_word(text[col]):
                col += 1
        else:
            if col == 0:
                if line > 0:
                    self.cursor = (line - 1, len(self.lines[line - 1]))
                return
            while col > 0 and not _is_word(text[col - 1]):
                col -= 1
            while col > 0 and _is_word(text[col - 1]):
                col -= 1
        self.cursor = (line, col)

    def _word_at_cursor(self) -> tuple[int, int] | None:
        line, col = self.cursor
        text = self.lines[line]
        if col < len(text) and _is_word(text[col]):
            start = col
        elif col > 0 and _is_word(text[col - 1]):
            start = col - 1
        else:
            return None
        end = start
        while start > 0 and _is_word(text[start - 1]):
            start -= 1
        while end < len(text) and _is_word(text[end]):
            end += 1
        return start, end

    def toggle_word(self) -> None:
        """Cross pressed as a whole: deselect if something is selected, else
        select the word under (or just before) the cursor."""
        self.goal = None
        if self.selection() is not None:
            self.anchor = None
            return
        found = self._word_at_cursor()
        if found is None:
            self.anchor = None
            return
        line = self.cursor[0]
        self.anchor, self.cursor = (line, found[0]), (line, found[1])

    def select_line(self) -> None:
        """Cross pressed twice: select the whole logical line."""
        self.goal = None
        line = self.cursor[0]
        self.anchor, self.cursor = (line, 0), (line, len(self.lines[line]))


# --- Terminal input decoding -------------------------------------------------


@dataclass(frozen=True)
class Event:
    kind: str  # "text" | "key"
    value: str
    shift: bool = False
    ctrl: bool = False


_CSI_FINAL = {"A": "up", "B": "down", "C": "right", "D": "left", "H": "home", "F": "end"}
_TILDE = {"3": "delete", "1": "home", "7": "home", "4": "end", "8": "end"}


class Decoder:
    """Turn the bytes `foot` sends into editing events (xterm conventions)."""

    def __init__(self) -> None:
        self.utf8 = codecs.getincrementaldecoder("utf-8")(errors="replace")
        self.pending = ""

    def feed(self, data: bytes) -> list[Event]:
        self.pending += self.utf8.decode(data)
        events: list[Event] = []
        while self.pending:
            consumed, event = self._one(self.pending)
            if consumed == 0:
                break  # an incomplete escape sequence; wait for more bytes
            self.pending = self.pending[consumed:]
            if event is not None:
                events.append(event)
        return events

    def flush(self) -> list[Event]:
        """A lone Escape that nothing followed: ignored (B is Backspace here)."""
        self.pending = ""
        return []

    @staticmethod
    def _modifiers(param: str) -> tuple[bool, bool]:
        try:
            bits = int(param) - 1
        except ValueError:
            return False, False
        return bool(bits & 1), bool(bits & 4)

    def _one(self, s: str) -> tuple[int, Event | None]:
        char = s[0]
        if char == "\x1b":
            if len(s) == 1:
                return 0, None
            if s[1] == "O":  # SS3 (application cursor mode)
                if len(s) < 3:
                    return 0, None
                name = _CSI_FINAL.get(s[2])
                return 3, Event("key", name) if name else None
            if s[1] != "[":
                return 2, None  # Alt+key: ignored
            end = 2
            while end < len(s) and not ("\x40" <= s[end] <= "\x7e"):
                end += 1
            if end >= len(s):
                return 0, None
            params, final = s[2:end].split(";"), s[end]
            shift, ctrl = self._modifiers(params[1]) if len(params) > 1 else (False, False)
            if final in _CSI_FINAL:
                return end + 1, Event("key", _CSI_FINAL[final], shift, ctrl)
            if final == "~" and params[0] in _TILDE:
                return end + 1, Event("key", _TILDE[params[0]], shift, ctrl)
            return end + 1, None
        if char in ("\r", "\n"):
            return 1, Event("key", "enter")
        if char in ("\x7f", "\x08"):
            return 1, Event("key", "backspace")
        if char == "\t":
            return 1, Event("text", "    ")
        if unicodedata.category(char) == "Cc":
            return 1, None
        return 1, Event("text", char)


def apply(slate: Slate, event: Event) -> None:
    if event.kind == "text":
        slate.insert(event.value)
    elif event.value == "enter":
        slate.newline()
    elif event.value == "backspace":
        slate.backspace()
    elif event.value == "delete":
        slate.delete()
    elif event.value in ("left", "right") and event.ctrl:
        slate.word(event.value, select=event.shift)
    elif event.value in ("left", "right", "up", "down", "home", "end"):
        slate.move(event.value, select=event.shift)


# --- Rendering ---------------------------------------------------------------


PROVISIONAL = "provisional"  # run style of Mycroft's text still being recognised


@dataclass(frozen=True)
class Frame:
    rows: list[list[tuple[str, bool | str]]]  # per screen row: runs of (text, False | True (selected) | PROVISIONAL)
    cursor: tuple[int, int]  # screen (row, column), 0-based
    hint: str


def _wrap(text: str, width: int) -> list[tuple[int, str]]:
    """Split a logical line into (start column, segment) rows of `width`."""
    if not text:
        return [(0, "")]
    return [(i, text[i:i + width]) for i in range(0, len(text), width)]


DICTATION_HINTS = {"loading": "dictation: loading… (L2 stops)", "listening": "dictation: listening (L2 stops)"}


def render(slate: Slate, width: int, height: int, hint: str = "FN+A send · FN+X clear · L1 hide",
           provisional: str = "", dictation: str = "") -> Frame:
    """Lay the text out in a `width` × `height` cell grid, last row for the hint.
    The view scrolls to keep the cursor visible. `provisional` (Mycroft's text
    being recognised) is shown underlined at the cursor without being part of
    the text; `dictation` is the dictation state shown in the hint."""
    if dictation:
        hint = DICTATION_HINTS.get(dictation, f"dictation: {dictation}")
    status_lines = len(slate.lines)
    if provisional:
        line, col = slate.cursor
        gap = "" if col == 0 or slate.lines[line][col - 1].isspace() else " "
        shown = Slate(slate.text())
        shown.cursor = slate.cursor
        shown.insert(gap + provisional)
        start, end = (line, col + len(gap)), shown.cursor
        return _layout(shown, width, height, hint, status_lines,
                       lambda pos: PROVISIONAL if start <= pos < end else False)
    span = slate.selection()
    return _layout(slate, width, height, hint, status_lines,
                   lambda pos: span is not None and span[0] <= pos < span[1])


def _layout(slate: Slate, width: int, height: int, hint: str, status_lines: int, style) -> Frame:
    width, text_rows = max(width, 1), max(height - 1, 1)
    visual: list[tuple[int, int, str]] = []  # (logical line, start column, segment)
    cursor_row = cursor_col = 0
    for number, line in enumerate(slate.lines):
        segments = _wrap(line, width)
        for index, (start, segment) in enumerate(segments):
            last = index == len(segments) - 1
            if number == slate.cursor[0] and start <= slate.cursor[1] and (slate.cursor[1] < start + width or last):
                cursor_row, cursor_col = len(visual), slate.cursor[1] - start
            visual.append((number, start, segment))
    if cursor_col >= width:  # cursor after a full last segment: show it on the next row
        cursor_row, cursor_col = cursor_row + 1, 0
        visual.insert(cursor_row, (slate.cursor[0], slate.cursor[1], ""))
    top = max(0, cursor_row - text_rows + 1)
    rows: list[list[tuple[str, bool | str]]] = []
    for number, start, segment in visual[top:top + text_rows]:
        runs: list[tuple[str, bool | str]] = []
        for offset, char in enumerate(segment):
            char_style = style((number, start + offset))
            if runs and runs[-1][1] == char_style:
                runs[-1] = (runs[-1][0] + char, char_style)
            else:
                runs.append((char, char_style))
        rows.append(runs)
    status = f"{status_lines} line{'s' if status_lines != 1 else ''}"
    return Frame(rows, (cursor_row - top, cursor_col), f"{hint} · {status}"[:width])


def to_ansi(frame: Frame) -> str:
    """Black background, white text; the selection in reverse video, Mycroft's
    provisional text underlined."""
    out = ["\x1b[?25l\x1b[H\x1b[2J"]
    for row, runs in enumerate(frame.rows):
        out.append(f"\x1b[{row + 1};1H")
        for text, style in runs:
            if style == PROVISIONAL:
                out.append(f"\x1b[4m{text}\x1b[24m")
            else:
                out.append(f"\x1b[7m{text}\x1b[27m" if style else text)
    out.append(f"\x1b[999;1H\x1b[2m{frame.hint}\x1b[22m")
    out.append(f"\x1b[{frame.cursor[0] + 1};{frame.cursor[1] + 1}H\x1b[?25h")
    return "".join(out)


# --- Terminal adapter --------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--socket", required=True, help="the daemon's Slate socket")
    args = parser.parse_args()

    link = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    link.connect(args.socket)
    link.sendall(json.dumps({"op": "hello", "pid": os.getpid()}).encode() + b"\n")

    slate, decoder = Slate(), Decoder()
    tty_fd = sys.stdin.fileno()
    saved = termios.tcgetattr(tty_fd)
    tty.setraw(tty_fd)
    resized = [True]
    signal.signal(signal.SIGWINCH, lambda *_: resized.__setitem__(0, True))
    inbox = b""
    result = 1
    dictation = {"state": "", "provisional": "", "stop_sent": False}

    def draw() -> None:
        size = os.get_terminal_size(sys.stdout.fileno())
        sys.stdout.write(to_ansi(render(slate, size.columns, size.lines,
                                        provisional=dictation["provisional"], dictation=dictation["state"])))
        sys.stdout.flush()

    try:
        draw()
        while True:
            try:
                readable, _, _ = select.select([tty_fd, link], [], [], 0.05 if decoder.pending else None)
            except InterruptedError:
                readable = []
            changed = resized[0]
            resized[0] = False
            if not readable and decoder.pending:
                decoder.flush()
            if tty_fd in readable:
                for event in decoder.feed(os.read(tty_fd, 4096)):
                    apply(slate, event)
                    changed = True
                    if dictation["state"] and not dictation["stop_sent"]:  # editing ends dictation
                        link.sendall(json.dumps({"op": "stop-dictation"}).encode() + b"\n")
                        dictation["stop_sent"] = True
            if link in readable:
                data = link.recv(4096)
                if not data:
                    break  # the daemon went away: discard
                inbox += data
                while b"\n" in inbox:
                    line, inbox = inbox.split(b"\n", 1)
                    message = json.loads(line)
                    op = message.get("op")
                    if op == "dictation":  # Mycroft's state: loading, listening, error: …, or "" (off)
                        dictation["state"] = str(message.get("state", ""))
                        if not dictation["state"]:
                            dictation["provisional"], dictation["stop_sent"] = "", False
                    elif op == "provisional":
                        dictation["provisional"] = str(message.get("text", ""))
                    elif op == "insert":
                        slate.insert_dictated(str(message.get("text", "")))
                        dictation["provisional"] = ""
                    elif op == "select-word":
                        slate.toggle_word()
                    elif op == "select-line":
                        slate.select_line()
                    elif op == "clear":
                        slate = Slate()
                    elif op == "send":
                        link.sendall(json.dumps({"op": "text", "text": slate.text()}).encode() + b"\n")
                        return 0
                    elif op == "discard":
                        return 0
                    changed = True
            if changed:
                draw()
    finally:
        termios.tcsetattr(tty_fd, termios.TCSADRAIN, saved)
        link.close()
    return result


if __name__ == "__main__":
    raise SystemExit(main())
