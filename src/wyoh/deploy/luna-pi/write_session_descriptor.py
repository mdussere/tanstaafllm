#!/usr/bin/env python3
"""Publish the socket of the Sway service that owns the Wyoh VNC session."""

from __future__ import annotations

import json
import os
from pathlib import Path


def main() -> int:
    socket_path = os.environ.get("SWAYSOCK")
    wayland_display = os.environ.get("WAYLAND_DISPLAY")
    runtime_dir = os.environ.get("XDG_RUNTIME_DIR")
    if not socket_path or not wayland_display or not runtime_dir:
        raise SystemExit("Sway did not provide a complete session environment")
    descriptor = Path.home() / ".local/state/tanstfaafllm/wyoh/sway-vnc-session.json"
    descriptor.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    temporary = descriptor.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(
            {"sway_socket": socket_path, "wayland_display": wayland_display},
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    temporary.chmod(0o600)
    temporary.replace(descriptor)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
