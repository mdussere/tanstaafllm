"""Camp Currie's drawing: one 720x720 software surface, pygame-ce (Steps 2-3).

The look follows the series (palette, fonts, cast) and the screens borrow game
mechanics: comm calls (Star Fox, Codec), stamps (Ace Attorney), a node map
(Mario World, FTL), a results screen with a rank (Star Fox). docs/0101_01 s.3.
`t` is the time in seconds since the scene began; screenshots pass a large t.
"""

from __future__ import annotations

import math
import random
from functools import lru_cache
from pathlib import Path

import pygame

from .core import MISSIONS, State

ASSETS = Path(__file__).resolve().parent.parent / "assets"
W = H = 720
NAVY, VIOLET_BG = (11, 16, 38), (42, 22, 80)
PANEL, PANEL_LIGHT = (16, 22, 52), (24, 32, 70)
BORDER, AMBER, WHITE = (107, 95, 168), (242, 169, 59), (232, 238, 246)
CYAN, GREEN, CORAL, DIM = (79, 216, 232), (91, 227, 125), (232, 96, 90), (128, 140, 176)
STAMP = {"success": ("CLEAR!", GREEN), "retry": ("TRY AGAIN", CORAL), "uncertain": ("NOT SURE", CYAN)}


@lru_cache(maxsize=None)
def font(kind: str, size: int) -> pygame.font.Font:
    name = {"title": "pressstart2p_PressStart2P-Regular.ttf", "body": "vt323_VT323-Regular.ttf"}[kind]
    return pygame.font.Font(str(ASSETS / "fonts" / name), size)


@lru_cache(maxsize=None)
def portrait(name: str, size: int = 192) -> pygame.Surface:
    path = ASSETS / "portraits" / f"{name.lower()}.png"
    surf = pygame.Surface((size, size))
    if path.exists():
        surf = pygame.transform.smoothscale(pygame.image.load(str(path)).convert(), (size, size))
    elif name.lower() == "mycroft":
        surf.fill((14, 20, 44))
        cx = size // 2
        for i, h in enumerate((30, 54, 80, 54, 30)):  # sound bars either side of the microphone
            for side in (-1, 1):
                pygame.draw.rect(surf, CYAN, (cx + side * (50 + i * 12) - 3, cx - h // 2, 6, h))
        microphone(surf, (cx, cx - 6), 1.0, WHITE)
    else:  # Luna: the Moon
        surf.fill((8, 10, 28))
        moon(surf, (size // 2, size // 2), size // 2 - 14)
    # comm-screen scanlines
    for y in range(0, size, 3):
        pygame.draw.line(surf, (0, 0, 0), (0, y), (size, y))
    return surf


@lru_cache(maxsize=1)
def background() -> pygame.Surface:
    surf = pygame.Surface((W, H))
    for y in range(H):
        k = y / (H - 1)
        surf.fill(tuple(int(NAVY[i] + (VIOLET_BG[i] - NAVY[i]) * k) for i in range(3)), (0, y, W, 1))
    rng = random.Random(7)
    for _ in range(140):
        x, y = rng.randrange(W), rng.randrange(H)
        colour = AMBER if rng.random() < 0.25 else WHITE
        surf.fill(tuple(int(c * rng.uniform(0.35, 0.9)) for c in colour), (x, y, 2, 2))
    return surf


def moon(surf: pygame.Surface, centre: tuple[int, int], r: int) -> None:
    """A lit Moon: grey disc, maria, craters with a rim, and a soft shadow on one side."""
    size = 2 * r + 4
    disc = pygame.Surface((size, size), pygame.SRCALPHA)
    c = (r + 2, r + 2)
    pygame.draw.circle(disc, (200, 204, 218), c, r)
    rng = random.Random(3)
    for _ in range(5):  # maria: large dark patches
        a, d = rng.uniform(0, 2 * math.pi), rng.uniform(0.1, 0.6) * r
        pygame.draw.circle(disc, (166, 172, 192), (int(c[0] + d * math.cos(a)), int(c[1] + d * math.sin(a))), int(rng.uniform(0.18, 0.3) * r))
    for _ in range(40):  # craters: dark bowl, light rim on the lit side
        a, d = rng.uniform(0, 2 * math.pi), math.sqrt(rng.random()) * 0.9 * r
        cr = max(2, int(rng.uniform(0.015, 0.07) * r))
        x, y = int(c[0] + d * math.cos(a)), int(c[1] + d * math.sin(a))
        pygame.draw.circle(disc, (226, 228, 238), (x - 1, y - 1), cr + 1)
        pygame.draw.circle(disc, (140, 146, 168), (x, y), cr)
    shade = pygame.Surface((size, size), pygame.SRCALPHA)  # shadow towards the bottom right
    for k in range(12):
        pygame.draw.circle(shade, (10, 12, 40, 14), (c[0] + int(r * (0.25 + k * 0.02)), c[1] + int(r * (0.25 + k * 0.02))), r)
    mask = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(mask, (255, 255, 255, 255), c, r)
    shade.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    disc.blit(shade, (0, 0))
    pygame.draw.circle(disc, (236, 238, 246), c, r, width=2)
    surf.blit(disc, (centre[0] - c[0], centre[1] - c[1]))


def microphone(surf: pygame.Surface, centre: tuple[int, int], scale: float, colour: tuple[int, int, int]) -> None:
    cx, cy = centre
    w, h = int(34 * scale), int(60 * scale)
    pygame.draw.rect(surf, colour, (cx - w // 2, cy - h // 2, w, h), border_radius=w // 2)
    pygame.draw.arc(surf, colour, (cx - w, cy - h // 4, 2 * w, h), math.pi, 2 * math.pi, max(3, int(5 * scale)))
    pygame.draw.line(surf, colour, (cx, cy + h // 2 + int(8 * scale)), (cx, cy + h // 2 + int(26 * scale)), max(3, int(5 * scale)))
    pygame.draw.line(surf, colour, (cx - int(18 * scale), cy + h // 2 + int(26 * scale)), (cx + int(18 * scale), cy + h // 2 + int(26 * scale)), max(3, int(5 * scale)))


def text(surf, s, kind, size, colour, pos, anchor="topleft", shadow=True) -> pygame.Rect:
    img = font(kind, size).render(s, True, colour)
    rect = img.get_rect(**{anchor: pos})
    if shadow:
        surf.blit(font(kind, size).render(s, True, (0, 0, 0)), rect.move(3, 3))
    surf.blit(img, rect)
    return rect


def wrap(s: str, kind: str, size: int, width: int) -> list[str]:
    lines, line = [], ""
    for word in s.split():
        trial = f"{line} {word}".strip()
        if font(kind, size).size(trial)[0] <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    return lines + ([line] if line else [])


def panel(surf, rect, colour=BORDER, fill=PANEL) -> None:
    pygame.draw.rect(surf, fill, rect)
    pygame.draw.rect(surf, colour, rect, width=3)


def typed(s: str, t: float, rate: float = 45.0) -> str:
    return s[: int(t * rate)]


def header(surf, label: str, title: str, state: State | None = None) -> None:
    text(surf, label, "title", 16, AMBER, (32, 30))
    text(surf, title, "title", 26, WHITE, (32, 56))
    if state is not None:  # five signal lights (Duolingo-like progress)
        for i, lit in enumerate(state.cleared):
            rect = pygame.Rect(W - 32 - (len(state.cleared) - i) * 30, 34, 22, 22)
            pygame.draw.rect(surf, GREEN if lit else (30, 38, 80), rect)
            pygame.draw.rect(surf, BORDER, rect, width=2)


def footer(surf, hint: str, t: float) -> None:
    colour = AMBER if int(t * 2) % 2 == 0 else (150, 104, 36)
    band = pygame.Surface((W, 52), pygame.SRCALPHA)
    band.fill((8, 10, 30, 200))
    surf.blit(band, (0, H - 60))
    text(surf, hint, "body", 30, colour, (W // 2, H - 26), anchor="midbottom")


def dialogue(surf, speaker: str, body: str, t: float, top: int = 440, bottom: int = 640) -> None:
    rect = pygame.Rect(24, top, W - 48, bottom - top)
    panel(surf, rect, WHITE, NAVY)
    pygame.draw.rect(surf, BORDER, rect.inflate(-14, -14), width=2)
    tag = pygame.Rect(44, top - 20, 30 + font("title", 16).size(speaker.upper())[0], 36)
    panel(surf, tag, WHITE, (75, 42, 122))
    text(surf, speaker.upper(), "title", 16, AMBER, tag.center, anchor="center", shadow=False)
    y = top + 30
    for line in wrap(typed(body, t), "body", 34, rect.width - 60):
        text(surf, line, "body", 34, WHITE, (52, y), shadow=False)
        y += 36


def comm_frame(surf, who: str, pos: tuple[int, int], t: float, label: str = "INCOMING CALL") -> None:
    x, y = pos
    frame = pygame.Rect(x - 8, y - 8, 192 + 16, 192 + 16)
    panel(surf, frame, AMBER, PANEL)
    surf.blit(portrait(who), (x, y))
    text(surf, who.upper(), "title", 22, AMBER, (x + 230, y + 8))
    if int(t * 2) % 2 == 0 or t > 1.5:
        text(surf, label, "body", 30, CYAN, (x + 230, y + 46))
    for i in range(5):  # signal bars
        h = 10 + i * 9
        pygame.draw.rect(surf, CYAN if i < 4 else (40, 60, 90), (x + 232 + i * 16, y + 130 - h, 10, h))
    text(surf, "CH 1 · LUNA RELAY", "body", 26, DIM, (x + 320, y + 112), shadow=False)


def stamp(surf, word: str, colour, centre, t: float, angle: float = -8.0) -> None:
    k = min(1.0, t / 0.25)
    size = int(52 + (1 - k) * 40)
    img = font("title", size).render(word, True, colour)
    shadow = font("title", size).render(word, True, (0, 0, 0))
    shake = int(6 * math.sin(t * 60) * max(0.0, 0.4 - t)) if t < 0.4 else 0
    for surface, off in ((shadow, 5), (img, 0)):
        rot = pygame.transform.rotate(surface, angle)
        surf.blit(rot, rot.get_rect(center=(centre[0] + off + shake, centre[1] + off)))


def draw(surf: pygame.Surface, s: State, t: float) -> None:
    surf.blit(background(), (0, 0))
    globals()[f"_{s.scene}"](surf, s, t)


def _title(surf, s, t):
    moon(surf, (W // 2, H + 210), 420)
    pygame.draw.circle(surf, (60, 120, 220), (612, 132), 30)  # Earth
    pygame.draw.circle(surf, (90, 190, 120), (604, 126), 12)
    text(surf, "CAMP", "title", 52, WHITE, (W // 2, 196), anchor="center")
    text(surf, "CURRIE", "title", 52, AMBER, (W // 2, 262), anchor="center")
    text(surf, "L-CAT", "title", 20, CYAN, (W // 2, 326), anchor="center")
    text(surf, "Lunar Communication Assessment Training", "body", 32, WHITE, (W // 2, 362), anchor="center")
    if int(t * 2) % 2 == 0:
        text(surf, "PRESS A", "title", 22, AMBER, (W // 2, 452), anchor="center")


NODES = ((150, 300), (360, 230), (570, 300))


def _missions(surf, s, t):
    header(surf, "STAGE SELECT", "MISSIONS")
    moon(surf, (W // 2, 560), 330)
    for (x1, y1), (x2, y2) in zip(NODES, NODES[1:]):  # dotted route
        for k in range(0, 20):
            if k % 2 == 0:
                pygame.draw.line(surf, DIM, (x1 + (x2 - x1) * k / 20, y1 + (y2 - y1) * k / 20),
                                 (x1 + (x2 - x1) * (k + 1) / 20, y1 + (y2 - y1) * (k + 1) / 20), 4)
    for i, ((x, y), mission) in enumerate(zip(NODES, MISSIONS)):
        locked = bool(mission.locked_reason)
        pygame.draw.circle(surf, (40, 48, 90) if locked else GREEN, (x, y), 26)
        pygame.draw.circle(surf, WHITE, (x, y), 26, width=3)
        text(surf, "?" if locked else str(i + 1), "title", 20, WHITE, (x, y + 2), anchor="center", shadow=False)
        if i == s.cursor:
            bob = int(4 * math.sin(t * 6))
            pygame.draw.circle(surf, AMBER, (x, y), 36, width=4)
            pygame.draw.polygon(surf, AMBER, ((x - 12, y - 64 + bob), (x + 12, y - 64 + bob), (x, y - 46 + bob)))
    m = MISSIONS[s.cursor]
    box = pygame.Rect(24, 430, W - 48, 210)
    panel(surf, box, AMBER if not m.locked_reason else BORDER, PANEL)
    text(surf, f"LEVEL {s.cursor + 1}", "title", 16, AMBER, (48, 452))
    text(surf, m.title.upper(), "title", 24, WHITE, (48, 480))
    text(surf, m.blurb, "body", 34, CYAN, (48, 524), shadow=False)
    if m.locked_reason:
        text(surf, "LOCKED · " + m.locked_reason, "body", 32, CORAL if s.notice else DIM, (48, 572), shadow=False)
    else:
        text(surf, "5 contacts · simulated results", "body", 32, DIM, (48, 572), shadow=False)
    footer(surf, "up/down choose · A open · B back", t)


def _briefing(surf, s, t):
    header(surf, "STAGE 1 · BRIEFING", MISSIONS[s.mission].title.upper(), s)
    comm_frame(surf, "Professor", (56, 140), t, "MISSION BRIEFING")
    dialogue(surf, "Professor", "Recruit, five crew members will call you. Answer each one by name. "
             "No microphone yet: every result is simulated.", t)
    footer(surf, "A start", t)


def _contact(surf, s, t):
    c = s.current
    header(surf, f"STAGE 1 · CONTACT {s.contact + 1}/5", MISSIONS[s.mission].title.upper(), s)
    comm_frame(surf, c.name, (56, 140), t)
    dialogue(surf, c.name, c.line, t, top=400, bottom=520)
    text(surf, c.target.upper(), "title", 44, WHITE, (W // 2, 568), anchor="center")
    text(surf, "say: " + c.hint, "body", 34, CYAN, (W // 2, 612), anchor="center")
    footer(surf, "A your turn · B missions", t)


def _turn(surf, s, t):
    c = s.current
    header(surf, f"STAGE 1 · CONTACT {s.contact + 1}/5", "YOUR TURN", s)
    centre = (W // 2, 230)
    pygame.draw.circle(surf, PANEL, centre, 92)
    pygame.draw.circle(surf, BORDER, centre, 92, width=4)
    microphone(surf, (centre[0], centre[1] - 14), 1.3, DIM)
    pygame.draw.line(surf, CORAL, (centre[0] - 64, centre[1] + 64), (centre[0] + 64, centre[1] - 64), 9)
    text(surf, "NO MICROPHONE · SIMULATED", "body", 32, CORAL, (W // 2, 346), anchor="center")
    text(surf, c.target.upper(), "title", 40, WHITE, (W // 2, 412), anchor="center")
    for i, label in enumerate(s.options()):
        rect = pygame.Rect(150, 470 + i * 82, W - 300, 64)
        selected = i == s.cursor
        panel(surf, rect, AMBER if selected else BORDER, PANEL_LIGHT if selected else PANEL)
        text(surf, ("> " if selected else "") + label.upper(), "title", 20, AMBER if selected else WHITE, rect.center, anchor="center")
    footer(surf, "up/down choose · A select · B back", t)


def _result(surf, s, t):
    c, o = s.current, s.last
    header(surf, f"STAGE 1 · CONTACT {s.contact + 1}/5", c.name.upper(), s)
    surf.blit(portrait(c.name, 144), (40, 120))
    pygame.draw.rect(surf, AMBER, (36, 116, 152, 152), width=4)
    word, colour = STAMP[o.kind]
    stamp(surf, word, colour, (450, 196), t)
    for i, line in enumerate(wrap(o.reason, "body", 32, W - 80)):
        text(surf, line, "body", 32, CYAN if o.kind != "retry" else CORAL, (W // 2, 330 + i * 34), anchor="center")
    if o.kind == "success":
        dialogue(surf, c.name, c.reply, t, top=400, bottom=600)
        footer(surf, "A next contact" if s.contact < 4 else "A debrief", t)
    else:
        dialogue(surf, "Relay", "Take a breath and try again. Retrying costs nothing." if o.kind == "retry"
                 else "The check was not sure. That says nothing about your accent.", t, top=400, bottom=600)
        footer(surf, "A try again", t)


def _debrief(surf, s, t):
    header(surf, "STAGE 1 · DEBRIEF", MISSIONS[s.mission].title.upper(), s)
    stamp(surf, "STAGE CLEAR!", GREEN, (W // 2, 168), t, angle=-5)
    box = pygame.Rect(40, 250, W - 80, 330)
    panel(surf, box, AMBER, PANEL)
    text(surf, "RANK", "title", 18, AMBER, (80, 282))
    text(surf, s.rank(), "title", 110, AMBER, (160, 440), anchor="center")
    for i, (label, value) in enumerate((("Contacts", "5/5"), ("Transmissions", str(s.attempts)),
                                        ("Retries", str(s.retries)), ("Not sure", str(s.uncertain)))):
        text(surf, label, "body", 36, WHITE, (290, 290 + i * 54), shadow=False)
        text(surf, value, "body", 36, AMBER, (630, 290 + i * 54), anchor="topright", shadow=False)
    text(surf, "Simulated results, not a pronunciation score.", "body", 30, CYAN, (W // 2, 618), anchor="center")
    footer(surf, "A missions", t)
