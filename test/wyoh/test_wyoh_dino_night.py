"""Deterministic tests for the white-on-black Dino build (Step 9.9)."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).parents[2]
sys.path.insert(0, str(ROOT / "src" / "wyoh" / "apps" / "dino"))
import make_night as m  # noqa: E402


def _png(pixels: list[tuple[int, int, int, int]]) -> bytes:
    image = Image.new("RGBA", (len(pixels), 1))
    image.putdata(pixels)
    out = io.BytesIO()
    image.save(out, format="PNG")
    return out.getvalue()


def test_chrome_grey_becomes_white_and_transparency_is_kept():
    data = m.night_sprite(_png([(0x53, 0x53, 0x53, 255), (0xF7, 0xF7, 0xF7, 255), (0, 0, 0, 0)]))
    pixels = list(Image.open(io.BytesIO(data)).convert("RGBA").getdata())
    assert pixels[0] == (255, 255, 255, 255)        # the ink: white
    assert pixels[1][3] == 255 and pixels[1][0] < 16  # near-white details: near black
    assert pixels[2][3] == 0                          # transparent stays transparent


def test_background_is_cleared_to_black():
    assert m.night_main("x\nlove.graphics.clear(1, 1, 1)\ny") == "x\nlove.graphics.clear(0, 0, 0)\ny"


def test_an_unexpected_main_lua_is_refused():
    with pytest.raises(ValueError):
        m.night_main("love.graphics.clear(0.5, 0.5, 0.5)")
