#!/usr/bin/env python3
"""Render the two mock-ups of Mike's new look (Wyoh 6.13), on the desk.

    uv run python src/wyoh/apps/mike/mockups.py OUTPUT_DIR

A: "terminal skin" (foot, VT323, Mike's portrait as a sixel image, box-drawing
frame); B: "RPG dialogue" (an SDL window: big portrait, the question above, a
dialogue box where the answer streams). Both at 720x720 with the real answer
Mike gave on Luna on 2026-10-31 (results/wyoh/luna-mike-window/20261031T115702Z).
The portrait is cropped from Hazel's key art (worklines/hazel/.../wallpaper.png).
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[4]
HAZEL = ROOT / "worklines/hazel/video/story2-ask-the-desktop/src"
VT323 = str(HAZEL / "fonts/vt323_VT323-Regular.ttf")
PS2P = str(HAZEL / "fonts/pressstart2p_PressStart2P-Regular.ttf")
NAVY, VIOLET, DEEP = (11, 16, 38), (75, 42, 122), (26, 18, 52)
AMBER, CYAN, TEXT, DIM = (242, 169, 59), (79, 216, 232), (232, 238, 246), (120, 132, 160)
QUESTION = "Et la Lune, tu la connais ?"
ANSWER = "Oui, je sais la Lune. Elle est une partie fascinante de notre système solaire."
SHOWN = 52  # characters of the answer already streamed, to show the effect


def portrait(size: int) -> Image.Image:
    """Mike's head from the key art, reduced to pixel blocks."""
    art = Image.open(HAZEL / "art/wallpaper.png").convert("RGB")
    head = art.crop((612, 446, 972, 806)).resize((size // 4, size // 4), Image.LANCZOS)
    return head.resize((size, size), Image.NEAREST)


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, width: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= width:
            line = trial
        else:
            lines.append(line)
            line = word
    return lines + [line] if line else lines


def terminal_skin(out: Path) -> None:
    img = Image.new("RGB", (720, 720), NAVY)
    d = ImageDraw.Draw(img)
    big, small = ImageFont.truetype(VT323, 34), ImageFont.truetype(VT323, 26)
    d.rectangle((0, 0, 719, 26), fill=(30, 30, 40))  # swaybar
    d.text((8, 2), "Mike — ready", font=small, fill=TEXT)
    d.rectangle((12, 40, 707, 707), outline=AMBER, width=3)
    img.paste(portrait(128), (28, 56))
    d.rectangle((26, 54, 157, 185), outline=CYAN, width=2)
    d.text((176, 60), "MIKE", font=ImageFont.truetype(VT323, 48), fill=AMBER)
    d.text((176, 108), "LFM2.5-350M · local · prêt", font=small, fill=DIM)
    d.text((176, 140), "L2 parler  FN+B envoyer  /new  /quit", font=small, fill=DIM)
    y = 210
    d.line((28, y - 10, 692, y - 10), fill=VIOLET, width=2)
    for who, text, colour in (("toi>", "Bonjour Mike, qui es-tu ?", CYAN),
                              ("mike", "Bonjour ! Je suis Mike, ton petit assistant. Et toi, tu es là pour les tâches quotidiennes ?", TEXT),
                              ("toi>", QUESTION, CYAN), ("mike", ANSWER[:SHOWN] + "█", TEXT)):
        d.text((28, y), who, font=big, fill=AMBER if who == "mike" else CYAN)
        for line in wrap(d, text, big, 560):
            d.text((120, y), line, font=big, fill=colour)
            y += 36
        y += 14
    img.save(out)


def rpg_dialogue(out: Path) -> None:
    img = Image.new("RGB", (720, 720), NAVY)
    d = ImageDraw.Draw(img)
    for row in range(720):  # navy to violet, like the series' sky
        t = row / 719
        d.line((0, row, 719, row), fill=tuple(int(NAVY[i] + (DEEP[i] - NAVY[i]) * t) for i in range(3)))
    for x, y in ((40, 60), (650, 90), (560, 30), (120, 250), (690, 300), (300, 40), (480, 210)):
        d.rectangle((x, y, x + 3, y + 3), fill=TEXT)
    label, body = ImageFont.truetype(PS2P, 16), ImageFont.truetype(VT323, 40)
    d.rectangle((0, 0, 719, 26), fill=(30, 30, 40))
    d.text((8, 2), "Mike — ready", font=ImageFont.truetype(VT323, 26), fill=TEXT)
    # the question, above, as the player's line
    d.rectangle((24, 44, 696, 112), fill=(18, 26, 58), outline=CYAN, width=3)
    d.text((40, 54), "TOI", font=label, fill=CYAN)
    d.text((40, 76), QUESTION, font=ImageFont.truetype(VT323, 32), fill=TEXT)
    # Mike's portrait, centre
    img.paste(portrait(224), (248, 132))
    d.rectangle((244, 128, 476, 360), outline=AMBER, width=4)
    # the dialogue box, classic RPG: double border, name tag, streamed text, cursor
    d.rectangle((16, 392, 703, 668), fill=NAVY, outline=TEXT, width=4)
    d.rectangle((26, 402, 693, 658), outline=VIOLET, width=3)
    d.rectangle((40, 376, 160, 408), fill=VIOLET, outline=TEXT, width=3)
    d.text((54, 384), "MIKE", font=label, fill=AMBER)
    y = 428
    for line in wrap(d, ANSWER[:SHOWN], body, 620):
        d.text((48, y), line, font=body, fill=TEXT)
        y += 44
    d.polygon(((660, 632), (680, 632), (670, 646)), fill=AMBER)  # "more" cursor
    d.text((24, 682), "L2 parler · FN+B envoyer · B passer", font=ImageFont.truetype(VT323, 28), fill=DIM)
    img.save(out)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    terminal_skin(out / "0613_01_mockup-a-terminal-skin.png")
    rpg_dialogue(out / "0613_01_mockup-b-rpg-dialogue.png")
    print(f"rendered into {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
