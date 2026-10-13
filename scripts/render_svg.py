"""Render SVG diagrams to PNG with Chromium (Playwright), as browsers show them.

Usage: uv run python scripts/render_svg.py docs/img/*.svg
The PNG is written next to each SVG, at the size of its viewBox."""
import sys, pathlib, re
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    for f in sys.argv[1:]:
        f = pathlib.Path(f).resolve()
        m = re.search(r'viewBox="0 0 (\d+) (\d+)"', f.read_text())
        w, h = int(m.group(1)), int(m.group(2))
        pg.set_viewport_size({"width": w, "height": h})
        pg.goto(f.as_uri())
        pg.screenshot(path=str(f.with_suffix(".png")), clip={"x": 0, "y": 0, "width": w, "height": h})
        print("rendered", f.with_suffix(".png"))
    b.close()
