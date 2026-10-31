"""Tile PNG frames 2 x 2 into contact sheets (for inspection): contact.py OUTPREFIX frame1.png ..."""
import sys
from PIL import Image
out, files = sys.argv[1], sys.argv[2:]
for k in range(0, len(files), 4):
    sheet = Image.new("RGB", (1920, 1080), "white")
    for j, f in enumerate(files[k:k + 4]):
        im = Image.open(f).convert("RGB").resize((956, 536))
        sheet.paste(im, ((j % 2) * 964, (j // 2) * 544))
    sheet.save(f"{out}_{k // 4:02d}.png")
