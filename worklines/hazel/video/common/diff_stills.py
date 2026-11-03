"""Regression check: render the same times from two pages (generated page vs a reference page, e.g. a hand-written
index.html) at 1920x1080 and print the mean absolute pixel difference (0..255) per still.
Usage: diff_stills.py PAGE_A PAGE_B OUTDIR t1 t2 ...   (pages are directories holding index.html)"""
import pathlib
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import capture as CAP  # noqa: E402


def main():
    a, b, out = sys.argv[1:4]
    times = [float(x) for x in sys.argv[4:]]
    pa, ea = CAP.render_stills(a, pathlib.Path(out) / 'a', times)
    pb, eb = CAP.render_stills(b, pathlib.Path(out) / 'b', times)
    tot = []
    for t, fa, fb in zip(times, pa, pb):
        d = np.abs(np.asarray(Image.open(fa).convert('RGB'), int) - np.asarray(Image.open(fb).convert('RGB'), int))
        tot.append(d.mean())
        print(f't={t:6.2f}  mean abs diff {d.mean():.4f}  max {d.max()}  differing pixels {(d.sum(2) > 0).sum()}')
    print(f'mean over {len(times)} stills: {np.mean(tot):.5f}', *(ea + eb))


if __name__ == '__main__':
    main()
