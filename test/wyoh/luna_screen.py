"""Screen predicates for Luna tests, against the deployed wallpaper.

Since 2026-10-08 the Luna session shows the user's TANSTAAFLLM background
instead of a plain colour. Swaybg draws the 720x720 file 1:1, so below the bar
an empty desktop is the image itself, and a drawn window is where the screen
no longer matches it.

The acceptance scenarios fetch JPEG frames (Luna's Wi-Fi moves about 160 KB/s
and a wallpaper PNG is about 1 MB), so every check tolerates JPEG artefacts:
colours match within a tolerance rather than exactly.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops

from test_minimal_env import BAR, BAR_ROW, BODY, Predicate

WALLPAPER = Path(__file__).parents[2] / "src/wyoh/deploy/luna/share/backgrounds/tanstaafllm-720.png"
_REFERENCE = Image.open(WALLPAPER).convert("RGB")
SILVER = (192, 192, 192)  # fuzzel background (menu, input zone, pop-up)
FULL = {"x": 0, "y": 0, "width": 720, "height": 720}
MENU_AREA = {"x": 120, "y": 200, "width": 480, "height": 320}


def _box(rect: dict[str, int]) -> tuple[int, int, int, int]:
    return (rect["x"], rect["y"], rect["x"] + rect["width"], rect["y"] + rect["height"])


def _near_fraction(image: Image.Image, rect: dict[str, int], color: tuple[int, int, int], tol: int = 24) -> float:
    """Share of pixels within `tol` of `color` on every channel."""
    region = image.convert("RGB").crop(_box(rect))
    pixels = region.width * region.height
    if not pixels:
        return 0.0
    target = Image.new("RGB", region.size, color)
    diff = ImageChops.difference(region, target)
    worst = ImageChops.lighter(ImageChops.lighter(*diff.split()[:2]), diff.split()[2])
    return sum(count for count, value in (worst.getcolors(pixels) or []) if value <= tol) / pixels


def _changed_fraction(image: Image.Image, rect: dict[str, int], tol: int = 40) -> float:
    """Share of pixels differing from the wallpaper by more than `tol` (grey level)."""
    box = _box(rect)
    diff = ImageChops.difference(image.convert("RGB").crop(box), _REFERENCE.crop(box)).convert("L")
    pixels = diff.width * diff.height
    unchanged = sum(count for count, value in (diff.getcolors(pixels) or []) if value <= tol)
    return 1.0 - unchanged / pixels if pixels else 0.0


def _empty_desktop(image: Image.Image) -> bool:
    """Bar present, and everything below it is the wallpaper."""
    return _changed_fraction(image, BODY) < 0.03 and _near_fraction(image, BAR_ROW, BAR) > 0.5


def _drawn(rect: dict[str, int]) -> Predicate:
    """The window rectangle no longer shows the wallpaper."""
    return lambda image: _changed_fraction(image, rect) > 0.8


def _silver_visible(image: Image.Image) -> bool:
    """A fuzzel surface (menu, input zone, or pop-up) is on screen."""
    return _near_fraction(image, FULL, SILVER, tol=10) > 0.02


def _menu_open(image: Image.Image) -> bool:
    return _near_fraction(image, MENU_AREA, SILVER, tol=10) > 0.2


def _menu_closed(image: Image.Image) -> bool:
    return _near_fraction(image, MENU_AREA, SILVER, tol=10) < 0.01
