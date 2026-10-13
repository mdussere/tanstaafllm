"""Wyoh calculator core (Step 9.5): the logic of a Windows 3.1-style calculator.

User request via Professor (2026-10-09): "very flat, very simple, like the old
Windows calculator": 18 keys (digits, + - x /, C, backspace, decimal point,
=), no memory, no scientific mode. See
worklines/wyoh/docs/0900_01_note-from-professor-graphical-apps.md.

Pure and standard library only: `Calculator` (what the keys do) and `KEYPAD`
with `move()` (where the gamepad selection goes). The window is separate.
Arithmetic uses Decimal, so 0.1 + 0.2 shows 0.3.
"""

from __future__ import annotations

from decimal import Decimal, DivisionByZero, InvalidOperation, Overflow, getcontext

DIGITS = 12  # shown on the display, as on the original
getcontext().prec = 28

OPS = {"+": lambda a, b: a + b, "−": lambda a, b: a - b, "×": lambda a, b: a * b, "÷": lambda a, b: a / b}
ERROR = "Error"


def _format(value: Decimal) -> str:
    """At most DIGITS significant digits, no exponent, no trailing zeros."""
    if value.is_zero():
        return "0"
    if abs(value) >= Decimal(10) ** DIGITS:
        raise Overflow
    whole = len(str(abs(value).to_integral_value(rounding="ROUND_DOWN")).lstrip("0"))  # 0 below 1
    rounded = round(value, max(DIGITS - whole, 0))
    text = f"{rounded:f}"
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if text in ("-0", "") else text


class Calculator:
    def __init__(self) -> None:
        self.clear()

    def clear(self) -> None:
        self.display = "0"
        self.accumulator: Decimal | None = None
        self.pending: str | None = None
        self.entering = False  # True while digits are being typed
        self.repeat: tuple[str, Decimal] | None = None  # for "=" pressed again

    @property
    def error(self) -> bool:
        return self.display == ERROR

    def press(self, key: str) -> str:
        """Apply one key ("0"-"9", ".", "+", "−", "×", "÷", "=", "C", "⌫"); return the display."""
        if key == "C" or (self.error and key != "⌫"):
            self.clear()
            if key == "C":
                return self.display
        if self.error:
            return self.display
        if key.isdigit() and len(key) == 1:
            self._digit(key)
        elif key == ".":
            if not self.entering:
                self.display, self.entering = "0.", True
            elif "." not in self.display:
                self.display += "."
        elif key == "⌫":
            if self.entering:
                self.display = self.display[:-1] or "0"
                if self.display in ("-", "-0"):
                    self.display = "0"
        elif key in OPS:
            if self.pending and self.entering:
                self._compute()
            elif self.accumulator is None or self.entering:
                self.accumulator = Decimal(self.display)
            if not self.error:
                self.pending, self.entering, self.repeat = key, False, None
        elif key == "=":
            if self.pending:
                operand = Decimal(self.display)
                self.repeat = (self.pending, operand)
                self._compute()
                self.pending = None
            elif self.repeat:
                op, operand = self.repeat
                self._apply(Decimal(self.display), op, operand)
            self.entering = False
        else:
            raise ValueError(f"unknown key: {key!r}")
        return self.display

    def _digit(self, digit: str) -> None:
        if not self.entering:
            self.display, self.entering = digit, True
            return
        if sum(c.isdigit() for c in self.display) >= DIGITS:
            return
        self.display = digit if self.display == "0" else self.display + digit

    def _compute(self) -> None:
        assert self.pending is not None and self.accumulator is not None
        self._apply(self.accumulator, self.pending, Decimal(self.display))

    def _apply(self, left: Decimal, op: str, right: Decimal) -> None:
        try:
            result = OPS[op](left, right)
            self.display = _format(result)
            self.accumulator = Decimal(self.display)
        except (DivisionByZero, InvalidOperation, Overflow, ZeroDivisionError):
            self.display, self.accumulator, self.pending = ERROR, None, None
        self.entering = False


# The keypad: 4 columns x 5 rows; "=" spans two rows, "0" two columns.
KEYPAD: list[list[str]] = [
    ["C", "⌫", "÷", "×"],
    ["7", "8", "9", "−"],
    ["4", "5", "6", "+"],
    ["1", "2", "3", "="],
    ["0", "0", ".", "="],
]


def move(position: tuple[int, int], direction: str) -> tuple[int, int]:
    """Move the selection (row, column) one key in a direction, skipping the
    other half of a wide key; it stops at the edges."""
    row, col = position
    key = KEYPAD[row][col]
    dr, dc = {"up": (-1, 0), "down": (1, 0), "left": (0, -1), "right": (0, 1)}[direction]
    r, c = row + dr, col + dc
    while 0 <= r < len(KEYPAD) and 0 <= c < len(KEYPAD[0]) and KEYPAD[r][c] == key:
        r, c = r + dr, c + dc
    if not (0 <= r < len(KEYPAD) and 0 <= c < len(KEYPAD[0])):
        return position
    return _anchor((r, c))


def _anchor(position: tuple[int, int]) -> tuple[int, int]:
    """The top-left cell of the key at `position` (wide and tall keys have one)."""
    row, col = position
    key = KEYPAD[row][col]
    while row > 0 and KEYPAD[row - 1][col] == key:
        row -= 1
    while col > 0 and KEYPAD[row][col - 1] == key:
        col -= 1
    return row, col


def key_at(position: tuple[int, int]) -> str:
    return KEYPAD[position[0]][position[1]]
