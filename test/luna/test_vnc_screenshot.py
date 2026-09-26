from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = Path(__file__).with_name("capture_vnc.py")


@pytest.mark.live
def test_luna_vnc_screenshot_is_captured() -> None:
    """Connect to the locally forwarded live VNC endpoint and preserve evidence."""
    if os.environ.get("LUNA_VNC_LIVE") != "1":
        pytest.skip("live VNC test: set LUNA_VNC_LIVE=1 after opening the SSH tunnel")
    host = os.environ.get("LUNA_VNC_HOST", "127.0.0.1")
    port = os.environ.get("LUNA_VNC_PORT", "5900")
    stamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    result_dir = ROOT / "results" / "luna" / "vnc" / stamp
    image = result_dir / "desktop.png"
    completed = subprocess.run(
        [sys.executable, str(CAPTURE), "--host", host, "--port", port, "--output", str(image)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    (result_dir / "pytest-capture.log").parent.mkdir(parents=True, exist_ok=True)
    (result_dir / "pytest-capture.log").write_text(completed.stdout, encoding="utf-8")
    assert completed.returncode == 0, completed.stdout
    assert image.is_file() and image.stat().st_size > 0
    with Image.open(image).convert("RGB") as captured:
        assert any(high > 8 for _, high in captured.getextrema()), "captured VNC desktop is all black"
        assert any(high > low for low, high in captured.getextrema()), "captured VNC desktop is a uniform blank frame"
