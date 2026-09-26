#!/usr/bin/env python3
"""Capture a VNC framebuffer as persistent test evidence."""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def capture(host: str, port: int, output: Path, timeout: int = 15) -> Path:
    """Save a VNC screenshot and its command log, or raise on failure."""
    vncdo = os.environ.get("VNC_CAPTURE_BIN", "vncdo")
    binary = shutil.which(vncdo)
    if binary is None:
        candidate = Path(sys.executable).with_name(vncdo)
        if candidate.is_file():
            binary = str(candidate)
    if binary is None:
        raise RuntimeError("vncdo is required; install vncdotool in the test environment")
    output.parent.mkdir(parents=True, exist_ok=True)
    command = [binary, "--timeout", str(timeout), "--server", f"{host}::{port}", "capture", str(output)]
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
    (output.parent / "capture.log").write_text("$ " + " ".join(command) + "\n" + completed.stdout, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"VNC capture failed with exit code {completed.returncode}; see {output.parent / 'capture.log'}")
    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("VNC capture completed without a non-empty image")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=5900, type=int)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    print(capture(args.host, args.port, args.output))


if __name__ == "__main__":
    main()
