"""Runs ON Luna (as root, in the Wyoh session's environment): what SDL makes of
Wyoh's virtual game pad, layer 5 of docs/howto/01_fix-a-game-gamepad-mapping.md.

It creates a second pad with wyoh-game-pad's vendor and product (1209:0012),
opens it through SDL2's GameController API (on Arch Linux ARM: sdl2-compat on
SDL3), presses each pad index and pushes each axis, and prints what a game such
as ECWolf receives:

    pad 0 (0x130) -> ['button0']      game controller button 0 = A
    ABS_RX + -> ['axis2+']             game controller axis 2 = right stick X

Method from Mannie from Luna's probe (2026-10-30). Close the game first: SDL
must see only this pad, so run it with the game's filter, e.g.
    SDL_GAMECONTROLLER_IGNORE_DEVICES_EXCEPT=0x1209/0x0012 python3 luna_game_pad_probe.py
Button numbers are SDL_GameControllerButton values (A 0, B 1, X 2, Y 3, back 4,
guide 5, start 6, left stick 7, right stick 8, left shoulder 9, right shoulder 10).
A game may number its own axes differently: check turning in the game itself.
"""

from __future__ import annotations

import ctypes
import sys
import time

sys.path.insert(0, "/storage/.local/share/tanstfaafllm/wyoh")
import wyoh_gamepad as w  # noqa: E402

SDL_INIT_JOYSTICK, SDL_INIT_GAMECONTROLLER = 0x200, 0x2000
CONTROLLER_AXIS, CONTROLLER_BUTTON_DOWN = 0x650, 0x651


def main() -> int:
    sdl = ctypes.CDLL("libSDL2-2.0.so.0")
    sdl.SDL_GameControllerOpen.restype = ctypes.c_void_p
    sdl.SDL_GameControllerMapping.restype = ctypes.c_char_p
    sdl.SDL_GameControllerMapping.argtypes = [ctypes.c_void_p]
    sdl.SDL_JoystickNameForIndex.restype = ctypes.c_char_p
    pad = w.UInputPad(1800)
    time.sleep(1)
    sdl.SDL_Init(SDL_INIT_GAMECONTROLLER | SDL_INIT_JOYSTICK)
    count = sdl.SDL_NumJoysticks()
    index = count - 1
    print("joysticks:", [sdl.SDL_JoystickNameForIndex(i) for i in range(count)],
          "game controller:", bool(sdl.SDL_IsGameController(index)))
    controller = sdl.SDL_GameControllerOpen(index)
    print("mapping:", sdl.SDL_GameControllerMapping(controller))
    event = (ctypes.c_uint8 * 64)()

    def drain() -> list[str]:
        seen = set()
        while sdl.SDL_PollEvent(event):
            kind = int.from_bytes(bytes(event[0:4]), "little")
            if kind == CONTROLLER_BUTTON_DOWN:
                seen.add(f"button{event[12]}")
            elif kind == CONTROLLER_AXIS:
                value = int.from_bytes(bytes(event[16:18]), "little", signed=True)
                if abs(value) > 8000:
                    seen.add(f"axis{event[12]}{'+' if value > 0 else '-'}")
        return sorted(seen)

    try:
        drain()
        for number in range(w.PAD_BUTTONS):
            pad.emit(w.EV_KEY, 0x130 + number, 1)
            time.sleep(0.1)
            pad.emit(w.EV_KEY, 0x130 + number, 0)
            time.sleep(0.2)
            print(f"pad {number} ({hex(0x130 + number)}) ->", drain())
        for name in ("ABS_X", "ABS_Y", "ABS_RX", "ABS_RY"):
            code = getattr(w, name)
            pad.emit(w.EV_ABS, code, 1700)
            time.sleep(0.2)
            pad.emit(w.EV_ABS, code, 0)
            time.sleep(0.2)
            print(name, "+ ->", drain())
    finally:
        pad.close()
        sdl.SDL_Quit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
