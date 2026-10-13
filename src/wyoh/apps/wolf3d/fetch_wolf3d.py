#!/usr/bin/env python3
"""Assemble Wolfenstein 3D (shareware, ECWolf) for Luna (Wyoh Step 9.8).

Downloads, from PortMaster's wolf3d port at a pinned commit, the aarch64
ECWolf engine, its data archive, the shareware episode files (*.WL1) and the
port's libjpeg, then writes an app directory from `wyoh-app.template.toml` and `run`:

    uv run python src/wyoh/apps/wolf3d/fetch_wolf3d.py OUTPUT_DIR

OUTPUT_DIR (outside Git) is then copied to /storage/.local/opt/wolf3d-ecwolf/
on Luna. Each file's SHA-256 goes into the manifest's [sha256] table, so
`wyoh_apps.py` refuses a tampered or partial copy.
"""

from __future__ import annotations

import hashlib
import shutil
import sys
import urllib.parse
import urllib.request
from pathlib import Path

COMMIT = "d36a1c2297277b7434591dd5a190751ff7424f6f"  # PortsMaster/PortMaster-New, 2026-05-14
BASE = f"https://raw.githubusercontent.com/PortsMaster/PortMaster-New/{COMMIT}/ports/wolf3d"
FILES = {
    "ecwolf": "wolf3d/engines/ecwolf",
    "data/ecwolf.pk3": "wolf3d/engines/ecwolf.pk3",
    "libs/libjpeg.so.62": "wolf3d/libs/libjpeg.so.62",
    "wolf3d.png": "cover.png",
    **{f"data/{name}.WL1": f"wolf3d/data/{name}.WL1"
       for name in ("AUDIOHED", "AUDIOT", "GAMEMAPS", "MAPHEAD", "VGADICT", "VGAGRAPH", "VGAHEAD", "VSWAP")},
}
HERE = Path(__file__).resolve().parent


def make_icon(cover: Path) -> bytes:
    """A 128 x 128 pixel-art icon: BJ Blazkowicz's portrait, cropped square from
    the status bar of the port's 400 x 300 cover and enlarged without blur."""
    import io

    from PIL import Image  # desk-side build tool; Pillow is a dev dependency

    with Image.open(cover) as image:
        face = image.convert("RGBA").crop((196, 211, 230, 245))  # 34 x 34 around the portrait
    out = io.BytesIO()
    face.resize((136, 136), Image.NEAREST).resize((128, 128), Image.LANCZOS).save(out, format="PNG")
    return out.getvalue()


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    digests: dict[str, str] = {}
    for target, source in FILES.items():
        url = f"{BASE}/{urllib.parse.quote(source)}"
        data = urllib.request.urlopen(url, timeout=120).read()
        path = out / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        digests[target] = hashlib.sha256(data).hexdigest()
        print(f"{digests[target][:12]}  {len(data):>8}  {target}")
    (out / "ecwolf").chmod(0o755)
    icon = make_icon(out / "wolf3d.png")  # BJ's face from the status bar of the port's cover
    (out / "wolf3d-icon.png").write_bytes(icon)
    digests["wolf3d-icon.png"] = hashlib.sha256(icon).hexdigest()
    shutil.copy2(HERE / "run", out / "run")
    shutil.copy2(HERE / "ecwolf.default.cfg", out / "ecwolf.default.cfg")  # copied to a mutable ecwolf.cfg at first run
    template = (HERE / "wyoh-app.template.toml").read_text(encoding="utf-8").rstrip()
    manifest = template + "\n\n[sha256]\n"  # the template ends with its tables; [sha256] is one more
    manifest += "".join(f'"{name}" = "{digest}"\n' for name, digest in sorted(digests.items()))
    (out / "wyoh-app.toml").write_text(manifest, encoding="utf-8")
    print(f"assembled {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
