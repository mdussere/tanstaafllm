"""Capture a generated episode page (index.html + fonts/ + art/) frame by frame with Playwright/Chromium.

Usage:
  python capture.py PAGEDIR video OUT.mp4 [--fps 30] [--audio music.wav] [--size 1920x1080]
      renders the whole video and pipes PNG frames straight into ffmpeg.
  python capture.py PAGEDIR stills OUTDIR t1 t2 ... [--size WxH]
      one PNG per requested time (seconds), named tNNN.NN.png.
  python capture.py PAGEDIR lint OUT.json t1 t2 ...
      the recorded text boxes of each frame (layout lint), as JSON {time: [box, ...]}.
The page draws at 1920 x 1080 whatever the size: a smaller size (the preview) is the same picture scaled down.
"""
import argparse
import functools
import http.server
import json
import pathlib
import subprocess
import sys
import threading

from playwright.sync_api import sync_playwright


def serve(root):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(root)))
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}/index.html"


def open_page(p, url, w, h):
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.goto(url)
    page.evaluate("() => window.ready")
    return browser, page, errors, page.evaluate("() => window.DURATION")


def shot(page, t, w, h):
    page.evaluate("t => window.renderFrame(t)", t)
    return page.screenshot(type="png", clip={"x": 0, "y": 0, "width": w, "height": h})


def render_video(root, out, fps=30, audio=None, size=(1920, 1080), preset="slow", crf=16):
    w, h = size
    httpd, url = serve(root)
    with sync_playwright() as p:
        browser, page, errors, duration = open_page(p, url, w, h)
        n = int(round(duration * fps))
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(fps), "-c:v", "png", "-i", "-"]
        if audio:
            cmd += ["-i", str(audio), "-c:a", "aac", "-b:a", "320k", "-ar", "48000"]
        cmd += ["-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-tune", "animation",
                "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2",
                "-r", str(fps), "-g", str(fps), "-bf", "2", "-movflags", "+faststart", "-t", f"{duration:.3f}", str(out)]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for i in range(n):
            ff.stdin.write(shot(page, i / fps, w, h))
            if i % 300 == 0:
                print(f"frame {i}/{n}", file=sys.stderr, flush=True)
        ff.stdin.close()
        if ff.wait() != 0:
            sys.exit("ffmpeg failed")
        browser.close()
    httpd.shutdown()
    return errors


def render_stills(root, outdir, times, size=(1920, 1080)):
    w, h = size
    outdir = pathlib.Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    httpd, url = serve(root)
    paths = []
    with sync_playwright() as p:
        browser, page, errors, _ = open_page(p, url, w, h)
        for t in times:
            f = outdir / f"t{t:06.2f}.png"
            f.write_bytes(shot(page, t, w, h))
            paths.append(f)
        browser.close()
    httpd.shutdown()
    return paths, errors


def lint_frames(root, times):
    httpd, url = serve(root)
    with sync_playwright() as p:
        browser, page, errors, _ = open_page(p, url, 1920, 1080)
        res = {t: page.evaluate("t => window.lintFrame(t)", t) for t in times}
        browser.close()
    httpd.shutdown()
    return res, errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("mode", choices=["video", "stills", "lint"])
    ap.add_argument("out")
    ap.add_argument("times", nargs="*", type=float)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--audio")
    ap.add_argument("--size", default="1920x1080")
    a = ap.parse_args()
    size = tuple(int(v) for v in a.size.split("x"))
    if a.mode == "video":
        errors = render_video(a.page, a.out, a.fps, a.audio, size)
    elif a.mode == "stills":
        _, errors = render_stills(a.page, a.out, a.times, size)
    else:
        res, errors = lint_frames(a.page, a.times)
        pathlib.Path(a.out).write_text(json.dumps(res))
    if errors:
        print("PAGE ERRORS:", *errors, sep="\n", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
