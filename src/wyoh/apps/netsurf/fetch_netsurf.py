#!/usr/bin/env python3
"""Assemble NetSurf (framebuffer front end, SDL surface) for Luna (Wyoh Step 9.10).

Downloads, from PortMaster's netsurf port at a pinned commit, the aarch64
`nsfb` binary, its private libraries (libs.aarch64: SDL 1.2 compatibility,
libwebp, libffi, libwayland-client) and its resources. It then writes Wyoh's
Choices over the port's (user, 2026-10-09: "minimalist, almost no images";
2026-10-15: "a very, very simple browser"): images, backgrounds, animations
and JavaScript off; DuckDuckGo Lite as home page and search, since Google
Search needs JavaScript. The port's cookie file is not taken.

    uv run python src/wyoh/apps/netsurf/fetch_netsurf.py OUTPUT_DIR

OUTPUT_DIR (outside Git) is then copied to /storage/.local/opt/netsurf/ on
Luna. Each file's SHA-256 goes into the manifest's [sha256] table.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
import urllib.parse
import urllib.request
from pathlib import Path

COMMIT = "d36a1c2297277b7434591dd5a190751ff7424f6f"  # PortsMaster/PortMaster-New, as for wolf3d
PORT = "ports/netsurf/netsurf"
RAW = f"https://raw.githubusercontent.com/PortsMaster/PortMaster-New/{COMMIT}/{PORT}"
TREE = f"https://api.github.com/repos/PortsMaster/PortMaster-New/git/trees/{COMMIT}:{PORT}?recursive=1"
TAKE = ("nsfb", "libs.aarch64/", "resources/", "COPYING.txt")
HERE = Path(__file__).resolve().parent

# Wyoh's changes to the port's resources/Choices (NetSurf option names).
CHOICES = {
    "foreground_images": "0",
    "background_images": "0",
    "animate_images": "0",
    "enable_javascript": "0",
    "homepage_url": "https://lite.duckduckgo.com/lite/",
    "search_web_provider": "DuckDuckGo",
    "cookie_file": "./conf/Cookies",
    "cookie_jar": "./conf/Cookies",
    "disc_cache_size": "16777216",   # 16 MiB on the card, not the port's 1 GiB
    "prefer_dark_mode": "0",
}


def choices(original: str) -> str:
    lines, seen = [], set()
    for line in original.splitlines():
        key = line.split(":", 1)[0]
        if key in CHOICES:
            line, _ = f"{key}:{CHOICES[key]}", seen.add(key)
        lines.append(line)
    lines += [f"{key}:{value}" for key, value in CHOICES.items() if key not in seen]
    return "\n".join(lines) + "\n"


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    tree = json.load(urllib.request.urlopen(TREE, timeout=60))["tree"]
    names = [item["path"] for item in tree if item["type"] == "blob" and item["path"].startswith(TAKE)]
    digests: dict[str, str] = {}
    for name in names:
        data = urllib.request.urlopen(f"{RAW}/{urllib.parse.quote(name)}", timeout=120).read()
        if name == "resources/Choices":
            data = choices(data.decode("utf-8")).encode("utf-8")
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        digests[name] = hashlib.sha256(data).hexdigest()
        print(f"{digests[name][:12]}  {len(data):>8}  {name}")
    (out / "nsfb").chmod(0o755)
    shutil.copy2(HERE / "run", out / "run")
    template = (HERE / "wyoh-app.template.toml").read_text(encoding="utf-8").rstrip()
    manifest = template + "\n\n[sha256]\n"
    manifest += "".join(f'"{name}" = "{digest}"\n' for name, digest in sorted(digests.items()))
    (out / "wyoh-app.toml").write_text(manifest, encoding="utf-8")
    print(f"assembled {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
