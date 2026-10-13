#!/usr/bin/env python3
"""Wyoh calculator window (Step 9.5): a flat Windows 3.1-style calculator.

The logic is `calc_core.py`; this file only draws it and reads input, with
SDL2 and SDL2_ttf through ctypes (both are on Luna's ArchR image; there is no
pygame there). Standard library only. It waits for events, so it uses no CPU
at rest.

Input, through Wyoh's gamepad daemon in its normal ("keys") mapping:
D-pad = arrows move the selection, A = Return presses the selected key,
Y = Backspace, X = Delete clears, B = Escape clears. A keyboard types digits
and operators directly; the pointer (right stick, R3) clicks keys. FN+B closes
the window like any other.
"""

from __future__ import annotations

import ctypes
import ctypes.util
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import calc_core  # noqa: E402

# --- SDL2 through ctypes --------------------------------------------------------

def _lib(*names: str) -> ctypes.CDLL:
    for name in names:
        path = ctypes.util.find_library(name) or name
        try:
            return ctypes.CDLL(path)
        except OSError:
            continue
    raise OSError(f"cannot load any of {names}")


SDL = _lib("SDL2", "libSDL2-2.0.so.0")
TTF = _lib("SDL2_ttf", "libSDL2_ttf-2.0.so.0")

SDL_INIT_VIDEO = 0x20
SDL_WINDOW_RESIZABLE = 0x20
SDL_QUIT, SDL_WINDOWEVENT, SDL_KEYDOWN, SDL_TEXTINPUT, SDL_MOUSEBUTTONDOWN = 0x100, 0x200, 0x300, 0x303, 0x401
SDLK = {"return": 13, "escape": 27, "backspace": 8, "delete": 127, "kp_enter": 0x40000058,
        "right": 0x4000004F, "left": 0x40000050, "down": 0x40000051, "up": 0x40000052}


class SDL_Rect(ctypes.Structure):
    _fields_ = [("x", ctypes.c_int), ("y", ctypes.c_int), ("w", ctypes.c_int), ("h", ctypes.c_int)]


class SDL_Color(ctypes.Structure):
    _fields_ = [("r", ctypes.c_uint8), ("g", ctypes.c_uint8), ("b", ctypes.c_uint8), ("a", ctypes.c_uint8)]


class SDL_Event(ctypes.Union):
    _fields_ = [("type", ctypes.c_uint32), ("padding", ctypes.c_uint8 * 56)]

    def key_sym(self) -> int:  # SDL_KeyboardEvent.keysym.sym at offset 20
        return int.from_bytes(bytes(self.padding[20:24]), "little", signed=True)

    def text(self) -> str:  # SDL_TextInputEvent.text at offset 12
        raw = bytes(self.padding[12:44])
        return raw.split(b"\0", 1)[0].decode("utf-8", "replace")

    def mouse(self) -> tuple[int, int, int]:  # SDL_MouseButtonEvent: button at 16, x at 20, y at 24
        button = self.padding[16]
        x = int.from_bytes(bytes(self.padding[20:24]), "little", signed=True)
        y = int.from_bytes(bytes(self.padding[24:28]), "little", signed=True)
        return button, x, y


P = ctypes.c_void_p
for name, args, res in [
    ("SDL_Init", [ctypes.c_uint32], ctypes.c_int),
    ("SDL_CreateWindow", [ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint32], P),
    ("SDL_CreateRenderer", [P, ctypes.c_int, ctypes.c_uint32], P),
    ("SDL_SetRenderDrawColor", [P, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8], ctypes.c_int),
    ("SDL_RenderClear", [P], ctypes.c_int),
    ("SDL_RenderFillRect", [P, ctypes.POINTER(SDL_Rect)], ctypes.c_int),
    ("SDL_RenderDrawRect", [P, ctypes.POINTER(SDL_Rect)], ctypes.c_int),
    ("SDL_RenderCopy", [P, P, P, ctypes.POINTER(SDL_Rect)], ctypes.c_int),
    ("SDL_RenderPresent", [P], None),
    ("SDL_GetRendererOutputSize", [P, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)], ctypes.c_int),
    ("SDL_CreateTextureFromSurface", [P, P], P),
    ("SDL_DestroyTexture", [P], None),
    ("SDL_FreeSurface", [P], None),
    ("SDL_WaitEvent", [ctypes.POINTER(SDL_Event)], ctypes.c_int),
    ("SDL_StartTextInput", [], None),
    ("SDL_GetError", [], ctypes.c_char_p),
    ("SDL_Quit", [], None),
]:
    function = getattr(SDL, name)
    function.argtypes, function.restype = args, res
for name, args, res in [
    ("TTF_Init", [], ctypes.c_int),
    ("TTF_OpenFont", [ctypes.c_char_p, ctypes.c_int], P),
    ("TTF_CloseFont", [P], None),
    ("TTF_RenderUTF8_Blended", [P, ctypes.c_char_p, SDL_Color], P),
]:
    function = getattr(TTF, name)
    function.argtypes, function.restype = args, res

# --- look (Windows 3.1) ------------------------------------------------------------

SILVER, WHITE, GREY, BLACK = (192, 192, 192), (255, 255, 255), (128, 128, 128), (0, 0, 0)
NAVY, BLUE, RED = (0, 0, 128), (0, 0, 168), (168, 0, 0)
FONTS = ["/usr/share/fonts/liberation/LiberationSans-Bold.ttf",
         "/usr/share/fonts/TTF/LiberationSans-Bold.ttf",
         "/usr/share/fonts/liberation-fonts/LiberationSans-Bold.ttf",
         "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
         "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"]
TEXT_KEYS = {"*": "×", "x": "×", "X": "×", "/": "÷", "-": "−", ",": ".", "\r": "="}
LABELS = {"⌫": "←"}  # Liberation Sans has no U+232B; the arrow reads the same


def _font_path() -> str:
    for path in FONTS:
        if os.path.exists(path):
            return path
    for root in ("/usr/share/fonts", "/usr/local/share/fonts"):
        for path in Path(root).rglob("*.ttf"):
            return str(path)
    raise FileNotFoundError("no TrueType font found")


class Window:
    def __init__(self) -> None:
        if SDL.SDL_Init(SDL_INIT_VIDEO) != 0 or TTF.TTF_Init() != 0:
            raise RuntimeError(SDL.SDL_GetError().decode())
        self.window = SDL.SDL_CreateWindow(b"Calculator", 0x2FFF0000, 0x2FFF0000, 360, 480, SDL_WINDOW_RESIZABLE)
        if not self.window:
            raise RuntimeError(SDL.SDL_GetError().decode())
        self.renderer = SDL.SDL_CreateRenderer(self.window, -1, 0)
        if not self.renderer:  # e.g. no usable EGL under Wayland (Wyoh 9.1b)
            raise RuntimeError(f"no renderer: {SDL.SDL_GetError().decode()}")
        self.font_path = _font_path().encode()
        self.fonts: dict[int, int] = {}
        self.calc = calc_core.Calculator()
        self.selected = (3, 3)  # "="
        self.rects: dict[tuple[int, int], SDL_Rect] = {}
        SDL.SDL_StartTextInput()

    def font(self, size: int) -> int:
        if size not in self.fonts:
            self.fonts[size] = TTF.TTF_OpenFont(self.font_path, size)
        return self.fonts[size]

    # drawing
    def fill(self, rect: SDL_Rect, colour: tuple[int, int, int]) -> None:
        SDL.SDL_SetRenderDrawColor(self.renderer, *colour, 255)
        SDL.SDL_RenderFillRect(self.renderer, ctypes.byref(rect))

    def bevel(self, rect: SDL_Rect, sunken: bool = False) -> None:
        """A Windows 3.1 button edge: light top-left, dark bottom-right, black frame."""
        x, y, w, h = rect.x, rect.y, rect.w, rect.h
        self.fill(SDL_Rect(x, y, w, h), BLACK)
        self.fill(SDL_Rect(x + 1, y + 1, w - 2, h - 2), GREY if sunken else WHITE)
        self.fill(SDL_Rect(x + 3, y + 3, w - 4, h - 4), WHITE if sunken else GREY)
        self.fill(SDL_Rect(x + 3, y + 3, w - 6, h - 6), SILVER)

    def text(self, text: str, size: int, colour: tuple[int, int, int], box: SDL_Rect, align: str = "center") -> None:
        surface = TTF.TTF_RenderUTF8_Blended(self.font(size), text.encode(), SDL_Color(*colour, 255))
        if not surface:
            return
        w = ctypes.c_int.from_address(surface + 16).value
        h = ctypes.c_int.from_address(surface + 20).value
        texture = SDL.SDL_CreateTextureFromSurface(self.renderer, surface)
        SDL.SDL_FreeSurface(surface)
        x = box.x + (box.w - w) // 2 if align == "center" else box.x + box.w - w
        dest = SDL_Rect(x, box.y + (box.h - h) // 2, w, h)
        SDL.SDL_RenderCopy(self.renderer, texture, None, ctypes.byref(dest))
        SDL.SDL_DestroyTexture(texture)

    def draw(self) -> None:
        width, height = ctypes.c_int(), ctypes.c_int()
        SDL.SDL_GetRendererOutputSize(self.renderer, ctypes.byref(width), ctypes.byref(height))
        W, H = width.value, height.value
        self.fill(SDL_Rect(0, 0, W, H), SILVER)
        margin = max(W // 24, 8)
        display = SDL_Rect(margin, margin, W - 2 * margin, max(H // 7, 40))
        self.fill(display, BLACK)
        self.fill(SDL_Rect(display.x + 2, display.y + 2, display.w - 3, display.h - 3), WHITE)
        self.text(self.calc.display, display.h * 5 // 9, BLACK,
                  SDL_Rect(display.x + 8, display.y, display.w - 18, display.h), align="right")
        top = display.y + display.h + margin
        rows, cols = len(calc_core.KEYPAD), len(calc_core.KEYPAD[0])
        gap = max(margin // 2, 4)
        cell_w = (W - 2 * margin - (cols - 1) * gap) // cols
        cell_h = (H - top - margin - (rows - 1) * gap) // rows
        self.rects.clear()
        done: set[str] = set()
        for r, row in enumerate(calc_core.KEYPAD):
            for c, key in enumerate(row):
                if key in done:
                    continue
                done.add(key)
                span_c = sum(1 for k in row if k == key)
                span_r = sum(1 for other in calc_core.KEYPAD if other[c] == key)
                rect = SDL_Rect(margin + c * (cell_w + gap), top + r * (cell_h + gap),
                                span_c * cell_w + (span_c - 1) * gap, span_r * cell_h + (span_r - 1) * gap)
                self.rects[(r, c)] = rect
                selected = (r, c) == self.selected
                self.bevel(rect, sunken=False)
                if selected:  # a thick navy focus frame, readable on the handheld
                    for i in range(3):
                        SDL.SDL_SetRenderDrawColor(self.renderer, *NAVY, 255)
                        frame = SDL_Rect(rect.x + 5 + i, rect.y + 5 + i, rect.w - 10 - 2 * i, rect.h - 10 - 2 * i)
                        SDL.SDL_RenderDrawRect(self.renderer, ctypes.byref(frame))
                colour = BLUE if key.isdigit() or key == "." else RED
                self.text(LABELS.get(key, key), min(cell_h, cell_w) * 4 // 9, colour, rect)
        SDL.SDL_RenderPresent(self.renderer)

    # input
    def press(self, key: str) -> None:
        self.calc.press(key)

    def handle(self, event: SDL_Event) -> bool:
        kind = event.type
        if kind == SDL_QUIT:
            return False
        if kind == SDL_KEYDOWN:
            sym = event.key_sym()
            direction = {SDLK["up"]: "up", SDLK["down"]: "down", SDLK["left"]: "left", SDLK["right"]: "right"}.get(sym)
            if direction:
                self.selected = calc_core.move(self.selected, direction)
            elif sym in (SDLK["return"], SDLK["kp_enter"]):
                self.press(calc_core.key_at(self.selected))
            elif sym == SDLK["backspace"]:
                self.press("⌫")
            elif sym in (SDLK["delete"], SDLK["escape"]):
                self.press("C")
        elif kind == SDL_TEXTINPUT:
            for char in event.text():
                key = TEXT_KEYS.get(char, char)
                if key in "0123456789.+−×÷=":
                    self.press(key)
        elif kind == SDL_MOUSEBUTTONDOWN:
            button, x, y = event.mouse()
            if button == 1:
                for position, rect in self.rects.items():
                    if rect.x <= x < rect.x + rect.w and rect.y <= y < rect.y + rect.h:
                        self.selected = position
                        self.press(calc_core.key_at(position))
        return True

    def run(self) -> None:
        event = SDL_Event()
        self.draw()
        while SDL.SDL_WaitEvent(ctypes.byref(event)):
            if not self.handle(event):
                break
            self.draw()
        for font in self.fonts.values():
            TTF.TTF_CloseFont(font)
        SDL.SDL_Quit()


if __name__ == "__main__":
    try:
        Window().run()
    except (RuntimeError, OSError) as error:
        print(f"wyoh-calc: {error}", file=sys.stderr)
        raise SystemExit(1)
