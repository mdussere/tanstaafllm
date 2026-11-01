"""Run Camp Currie.

    python -m camp_currie                  # play (arrows, Return = A, Escape = B)
    python -m camp_currie --agent          # development protocol: actions on stdin, JSON state on stdout
    python -m camp_currie --script success,retry,...   # the simulated evaluator's outcomes

Agent protocol (development only, docs/0101_01 s.5): each stdin line is an
action (up, down, confirm, back), or "shot PATH" to save the frame, or "quit".
Each action answers one JSON line: the semantic state plus rss_kib.
"""

from __future__ import annotations

import argparse
import json
import sys

import pygame

from . import render
from .core import DEFAULT_SCRIPT, ScriptedEvaluator, State, semantic, step

KEYS = {pygame.K_UP: "up", pygame.K_DOWN: "down", pygame.K_RETURN: "confirm", pygame.K_KP_ENTER: "confirm",
        pygame.K_SPACE: "confirm", pygame.K_ESCAPE: "back", pygame.K_BACKSPACE: "back"}


def peak_rss_kib() -> int:
    try:
        with open("/proc/self/status", encoding="ascii") as status:
            return next(int(line.split()[1]) for line in status if line.startswith("VmHWM"))
    except (OSError, StopIteration):
        return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="camp_currie", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--agent", action="store_true")
    parser.add_argument("--script", default=",".join(DEFAULT_SCRIPT))
    args = parser.parse_args(argv)
    evaluator = ScriptedEvaluator(tuple(args.script.split(",")))  # type: ignore[arg-type]
    pygame.display.init()
    pygame.font.init()
    pygame.display.set_caption("Camp Currie")
    screen = pygame.display.set_mode((render.W, render.H))
    state, entered = State(), pygame.time.get_ticks()
    if args.agent:
        for raw in sys.stdin:
            line = raw.strip()
            if not line:
                continue
            if line == "quit":
                break
            if line.startswith("shot "):
                render.draw(screen, state, 10.0)
                pygame.image.save(screen, line[5:])
                print(json.dumps({"shot": line[5:]}), flush=True)
                continue
            try:
                state = step(state, line, evaluator)
                render.draw(screen, state, 10.0)  # the window shows each state too
                pygame.display.flip()
                pygame.event.pump()
                print(json.dumps({**semantic(state), "rss_kib": peak_rss_kib()}), flush=True)
            except ValueError as error:
                print(json.dumps({"error": str(error)}), flush=True)
        pygame.quit()
        return 0
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return 0
            if event.type == pygame.KEYDOWN and event.key in KEYS:
                previous = state.scene
                state = step(state, KEYS[event.key], evaluator)
                if state.scene != previous or KEYS[event.key] == "confirm":
                    entered = pygame.time.get_ticks()
        render.draw(screen, state, (pygame.time.get_ticks() - entered) / 1000)
        pygame.display.flip()
        clock.tick(30)


if __name__ == "__main__":
    raise SystemExit(main())
