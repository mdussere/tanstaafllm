#!/usr/bin/env python3
"""Build Dino Love2D in white on black for Luna (Wyoh Step 9.9, user request).

The user wants the Chrome T-Rex game "white on black, not black on white",
like Chrome's own night mode. This script, run on the desk:

1. downloads Google-Dino-Love2D at a pinned commit and checks its SHA-256;
2. inverts the sprite sheet's colours, keeping transparency, then stretches
   the levels so Chrome's grey (#535353) becomes white;
3. makes the game clear its background to black instead of white;
4. packs `Dino-Love2D-night.love` and writes `PROVENANCE.txt` beside it.

The output goes to a directory outside Git (sprites are Chromium's, BSD-3;
the game is MIT). Deployment to Luna is a later sub-step.

    uv run python src/wyoh/apps/dino/make_night.py OUTPUT_DIR
"""

from __future__ import annotations

import hashlib
import io
import sys
import urllib.request
import zipfile
from datetime import UTC, datetime
from pathlib import Path

from PIL import Image

COMMIT = "b4fbaa4494e69149a0e68963e2490ec398b501f8"  # justaporter/Google-Dino-Love2D, 2026-10-04
URL = f"https://github.com/justaporter/Google-Dino-Love2D/archive/{COMMIT}.zip"
SOURCE_SHA256 = "2b502dd8724d30470d2447aad92eb0fa2f31bc300ecf634d94fd73da30bd8396"  # first download, 2026-10-09
FILES = ("main.lua", "conf.lua", "sprite.png", "hit.ogg", "jump.ogg", "reached.ogg",
         "LICENSE", "LICENSE-chromium-dino.txt")
CLEAR_DAY, CLEAR_NIGHT = "love.graphics.clear(1, 1, 1)", "love.graphics.clear(0, 0, 0)"


def night_sprite(data: bytes) -> bytes:
    """Invert RGB, keep alpha, and stretch so the darkest original ink is white."""
    image = Image.open(io.BytesIO(data)).convert("RGBA")
    pixels = image.load()
    width, height = image.size
    darkest = min((min(pixels[x, y][:3]) for x in range(width) for y in range(height) if pixels[x, y][3]),
                  default=0)
    span = max(255 - darkest, 1)
    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]
            if a:
                pixels[x, y] = tuple(min(255, round((255 - c) * 255 / span)) for c in (r, g, b)) + (a,)
    out = io.BytesIO()
    image.save(out, format="PNG", optimize=True)
    return out.getvalue()


def night_main(source: str) -> str:
    if source.count(CLEAR_DAY) != 1:
        raise ValueError("main.lua no longer clears to white in one place; review the patch")
    return source.replace(CLEAR_DAY, CLEAR_NIGHT)


def build(archive: bytes) -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    with zipfile.ZipFile(io.BytesIO(archive)) as source:
        prefix = source.namelist()[0].split("/", 1)[0] + "/"
        for name in FILES:
            files[name] = source.read(prefix + name)
    files["sprite.png"] = night_sprite(files["sprite.png"])
    files["main.lua"] = night_main(files["main.lua"].decode("utf-8")).encode("utf-8")
    return files


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    archive = urllib.request.urlopen(URL, timeout=60).read()
    digest = hashlib.sha256(archive).hexdigest()
    if digest != SOURCE_SHA256:
        print(f"source SHA-256 {digest} != pinned {SOURCE_SHA256}; refusing to build", file=sys.stderr)
        return 1
    files = build(archive)
    love = out / "Dino-Love2D-night.love"
    with zipfile.ZipFile(love, "w", zipfile.ZIP_DEFLATED) as package:  # main.lua at the root
        for name, data in files.items():  # fixed dates: the same input gives the same .love
            package.writestr(zipfile.ZipInfo(name, date_time=(2026, 10, 4, 0, 0, 0)), data, zipfile.ZIP_DEFLATED)
    (out / "sprite-night.png").write_bytes(files["sprite.png"])
    love_digest = hashlib.sha256(love.read_bytes()).hexdigest()
    (out / "PROVENANCE.txt").write_text(
        f"Dino Love2D, white on black (Wyoh Step 9.9), built {datetime.now(UTC).isoformat(timespec='seconds')}\n"
        f"source: {URL}\nsource sha256: {digest}\n"
        f"changes: sprite.png colours inverted and levels stretched (alpha kept); "
        f"main.lua `{CLEAR_DAY}` -> `{CLEAR_NIGHT}`\n"
        f"licences: game MIT (LICENSE); sprites and sounds BSD-3-Clause, The Chromium Authors "
        f"(LICENSE-chromium-dino.txt)\n"
        f"output: {love.name} sha256 {love_digest}\n"
        "runtime: Love2D 11.5 (PortMaster's love_11.5 runtime in the original port)\n",
        encoding="utf-8")
    print(love, love_digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
