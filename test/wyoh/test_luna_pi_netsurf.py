"""Step 9.10: NetSurf (nsfb on SDL) in luna-pi's headless Sway, before Luna.

Contract: `luna_pi_netsurf.feature`. The bundle comes from
`src/wyoh/apps/netsurf/fetch_netsurf.py`. Debian 13 has no libjpeg.so.8 (Arch
Linux ARM has), so luna-pi needs one beside the port's libraries, given by
WYOH_NETSURF_EXTRA_LIBS (for example Ubuntu's libjpeg-turbo8, extracted).

Run with:
    WYOH_LUNA_PI_NETSURF_LIVE=1 WYOH_NETSURF_BUNDLE=<assembled dir> \
        WYOH_NETSURF_EXTRA_LIBS=<dir with libjpeg.so.8> \
        uv run pytest -m live test/wyoh/test_luna_pi_netsurf.py
"""

from __future__ import annotations

import os
import struct
import subprocess
import zlib
from datetime import UTC, datetime
from pathlib import Path

import pytest

pytestmark = pytest.mark.live
HOST = "luna-pi"
REMOTE = ".local/opt/netsurf-test"
# luna-pi's Wyoh Sway (720x720 headless); wayland-0 is labwc's desktop.
ENV = ("XDG_RUNTIME_DIR=/run/user/1000 WAYLAND_DISPLAY=wayland-1 SDL_VIDEODRIVER=wayland "
       "SDL_VIDEO_WAYLAND_WMCLASS=netsurf HOME=$PWD LD_LIBRARY_PATH=$PWD/libs.aarch64 "
       "NETSURFRES=$PWD/resources NETSURF_DIR=$PWD/ XDG_DATA_HOME=$PWD/conf")
PAGES = [
    ("duckduckgo-lite", "https://lite.duckduckgo.com/lite/", 20),
    ("duckduckgo-search", "https://lite.duckduckgo.com/lite/?q=lune", 20),
    ("wikipedia", "https://fr.wikipedia.org/wiki/Lune", 60),
]


def _ssh(command: str, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["ssh", "-o", "BatchMode=yes", HOST, command],
                          capture_output=True, text=True, timeout=timeout, check=False)


def _png_colours(data: bytes) -> int:
    """Distinct values among a sample of the first image row's bytes."""
    width, _height = struct.unpack(">II", data[16:24])
    chunks, pos = b"", 8
    while pos < len(data):
        size, kind = struct.unpack(">I4s", data[pos:pos + 8])
        if kind == b"IDAT":
            chunks += data[pos + 8:pos + 8 + size]
        pos += size + 12
    raw = zlib.decompress(chunks)
    return len(set(raw[: len(raw) // 2 : 7]))


@pytest.fixture(scope="module")
def result_dir() -> Path:
    if os.environ.get("WYOH_LUNA_PI_NETSURF_LIVE") != "1":
        pytest.skip("set WYOH_LUNA_PI_NETSURF_LIVE=1, WYOH_NETSURF_BUNDLE and WYOH_NETSURF_EXTRA_LIBS")
    bundle = Path(os.environ["WYOH_NETSURF_BUNDLE"])
    extra = Path(os.environ["WYOH_NETSURF_EXTRA_LIBS"])
    out = Path("results/wyoh/luna-pi-netsurf") / datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    out.mkdir(parents=True, exist_ok=False)
    _ssh(f"rm -rf {REMOTE}")
    for source, target in ((bundle, REMOTE), (extra, f"{REMOTE}/libs.aarch64")):
        copied = subprocess.run(["rsync", "-aL", f"{source}/", f"{HOST}:{target}/"],
                                capture_output=True, text=True, timeout=300, check=False)
        assert copied.returncode == 0, copied.stderr
    linked = _ssh(f"cd {REMOTE} && LD_LIBRARY_PATH=$PWD/libs.aarch64 ldd ./nsfb")
    (out / "ldd.txt").write_text(linked.stdout + linked.stderr, encoding="utf-8")
    assert "not found" not in linked.stdout, linked.stdout
    return out


@pytest.mark.parametrize(("name", "url", "seconds"), PAGES, ids=[page[0] for page in PAGES])
def test_netsurf_opens_a_page_on_luna_pi(result_dir: Path, name: str, url: str, seconds: int) -> None:
    run = _ssh(f"pkill -x nsfb; sleep 1; cd {REMOTE} && export {ENV} && mkdir -p conf/Hotlist downloads && "
               f"(./nsfb -fsdl -w720 -h720 '{url}' > /tmp/nsfb-{name}.log 2>&1 &); sleep {seconds}; "
               f"grim /tmp/nsfb-{name}.png; echo running: $(ps -o rss=,time= -C nsfb); cat /tmp/nsfb-{name}.log",
               timeout=seconds + 60)
    (result_dir / f"{name}.log").write_text(f"url: {url}\nwaited: {seconds} s (running: RSS KiB, CPU time)\n{run.stdout}{run.stderr}",
                                            encoding="utf-8")
    fetched = subprocess.run(["scp", "-q", f"{HOST}:/tmp/nsfb-{name}.png", str(result_dir / f"{name}.png")],
                             capture_output=True, text=True, timeout=60, check=False)
    _ssh("pkill -x nsfb")
    assert "running: " in run.stdout and "running: \n" not in run.stdout, f"nsfb stopped: {run.stdout}{run.stderr}"
    assert fetched.returncode == 0, fetched.stderr
    assert _png_colours((result_dir / f"{name}.png").read_bytes()) > 3, "blank screenshot"
