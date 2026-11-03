"""One small contact sheet: N thumbnails in a grid, 960 px wide in total.
Usage: contact.py OUT.png frame1.png frame2.png ...   (4 columns; 12 frames give 960 x 405)"""
import sys

from PIL import Image


def sheet(out, files, cols=4, width=960):
    tw = width // cols
    th = round(tw * 9 / 16)
    rows = -(-len(files) // cols)
    im = Image.new("RGB", (tw * cols, th * rows), "black")
    for i, f in enumerate(files):
        im.paste(Image.open(f).convert("RGB").resize((tw, th), Image.LANCZOS), ((i % cols) * tw, (i // cols) * th))
    im.save(out)


if __name__ == "__main__":
    sheet(sys.argv[1], sys.argv[2:])
