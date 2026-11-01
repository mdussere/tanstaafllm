#!/usr/bin/env python3
"""Crop the crew portraits for Camp Currie from the series' key art (run once, on the desk).

    uv run --group wyoh python src/camp-currie/tools/make_portraits.py

Source: worklines/hazel/video/story2-ask-the-desktop/src/art/wallpaper.png (the
project's key art, 1254x1254). Output: src/camp-currie/assets/portraits/*.png, 192 px.
Mycroft has no face and Luna is the Moon: the game draws both.
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "worklines/hazel/video/story2-ask-the-desktop/src/art/wallpaper.png"
OUT = ROOT / "src/camp-currie/assets/portraits"
SIZE = 192
CROPS = {  # left, top, right, bottom in the 1254 px key art
    "mannie": (80, 440, 400, 760),
    "wyoh": (330, 560, 650, 880),
    "mike": (612, 446, 972, 806),
    "professor": (930, 600, 1250, 920),
}

if __name__ == "__main__":
    art = Image.open(ART).convert("RGB")
    OUT.mkdir(parents=True, exist_ok=True)
    for name, box in CROPS.items():
        art.crop(box).resize((SIZE, SIZE), Image.LANCZOS).save(OUT / f"{name}.png", optimize=True)
        print(name, box)
