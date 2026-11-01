"""Mike Step 14.1: cut Luna's guide into short knowledge blocks (about 100 words), by heading.

Each block is a paragraph group under one heading, at most MAX_WORDS words, cited as
`<file>#<heading>#<n>`. Tables, images and code fences are skipped: only prose is kept.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).parents[2]
GUIDE = ["docs/10_wyoh.md", "docs/11_mycroft.md", "docs/12_mike.md", "docs/13_mannie.md", "docs/14_luna.md",
         "docs/15_the-cell.md", "docs/howto/01_fix-a-game-gamepad-mapping.md"]
MAX_WORDS = 120


def _clean(text: str) -> str:
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    return re.sub(r"[*_`>]", "", text).strip()


def blocks(files=GUIDE) -> list[dict]:
    out = []
    for name in files:
        heading, paras, fence = "top", [], False
        lines = (REPO / name).read_text(encoding="utf-8").splitlines() + ["## end"]
        for line in lines:
            if line.startswith("```"):
                fence = not fence
                continue
            if fence or line.startswith("|") or line.startswith("> **Freshness"):
                continue
            if line.startswith("#"):
                out += _group(name, heading, paras)
                heading, paras = line.lstrip("#").strip(), []
            elif line.strip() and line.strip() != "---":
                paras.append(_clean(line))
    return out


def _group(name: str, heading: str, paras: list[str]) -> list[dict]:
    groups, cur = [], []
    for p in paras:
        if cur and len(" ".join(cur + [p]).split()) > MAX_WORDS:
            groups.append(cur)
            cur = []
        cur.append(p)
    if cur:
        groups.append(cur)
    return [{"id": f"{name}#{heading}#{i}", "text": " ".join(g)} for i, g in enumerate(groups)
            if len(" ".join(g).split()) >= 15]
