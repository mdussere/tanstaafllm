"""Capture index.html frame by frame with Playwright/Chromium.

Usage:
  python capture.py video OUT.mp4 [--fps 30] [--audio music.wav]
      renders the whole video (60 s plus the reading holds) and pipes PNG frames straight into ffmpeg.
  python capture.py stills OUTDIR t1 t2 ...
      writes one PNG per requested time (seconds), for inspection.
"""
import argparse
import functools
import http.server
import pathlib
import subprocess
import sys
import threading

from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
W, H = 1920, 1080


def serve():
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Quiet, directory=str(HERE))
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, f"http://127.0.0.1:{httpd.server_address[1]}/index.html"


def open_page(p, url):
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
    page.goto(url)
    page.evaluate("() => window.ready")
    return browser, page, errors, page.evaluate("() => window.DURATION")


def shot(page, t):
    page.evaluate("t => window.renderFrame(t)", t)
    return page.screenshot(type="png", clip={"x": 0, "y": 0, "width": W, "height": H})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["video", "stills"])
    ap.add_argument("out")
    ap.add_argument("times", nargs="*", type=float)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--audio")
    a = ap.parse_args()
    httpd, url = serve()
    with sync_playwright() as p:
        browser, page, errors, duration = open_page(p, url)
        if a.mode == "stills":
            out = pathlib.Path(a.out)
            out.mkdir(parents=True, exist_ok=True)
            for t in a.times:
                (out / f"t{t:06.2f}.png").write_bytes(shot(page, t))
        else:
            n = int(round(duration * a.fps))
            cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(a.fps),
                   "-c:v", "png", "-i", "-"]
            if a.audio:
                cmd += ["-i", a.audio, "-c:a", "aac", "-b:a", "320k", "-ar", "48000"]
            cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", "16", "-tune", "animation",
                    "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.2",
                    "-r", str(a.fps), "-g", str(a.fps), "-bf", "2", "-movflags", "+faststart",
                    "-t", f"{duration:.3f}", a.out]
            ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
            for i in range(n):
                ff.stdin.write(shot(page, i / a.fps))
                if i % 150 == 0:
                    print(f"frame {i}/{n}", file=sys.stderr, flush=True)
            ff.stdin.close()
            if ff.wait() != 0:
                sys.exit("ffmpeg failed")
        browser.close()
        if errors:
            print("PAGE ERRORS:", *errors, sep="\n", file=sys.stderr)
            sys.exit(1)
    httpd.shutdown()


if __name__ == "__main__":
    main()
