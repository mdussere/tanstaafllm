"""Runs ON Luna, detached (systemd-run), for test_luna_wifi.py (Step 7.4).

Joins a second network with wyoh_wifi's own profile writing and iwd calls,
records the result, and always returns to the network it started on, because
the desk loses SSH while Luna is away. The test network's profile is forgotten
at the end, so iwd keeps preferring home.

Candidate passwords come in a mode-600 file on /run (tmpfs), one per line;
it is deleted as soon as it is read. No password is written to the log.
"""

from __future__ import annotations

import json
import socket
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, "/storage/.local/share/tanstfaafllm/wyoh")
import wyoh_wifi as w  # noqa: E402


def address() -> str:
    out = subprocess.run(["ip", "-4", "addr", "show", "wlan0"], capture_output=True, text=True).stdout
    return next((part.split()[1] for part in out.splitlines() if "inet " in part), "")


def main() -> int:
    ssid, secrets, log_path = sys.argv[1], Path(sys.argv[2]), Path(sys.argv[3])
    candidates = [line for line in secrets.read_text(encoding="utf-8").splitlines() if line]
    secrets.unlink()
    log: dict = {"ssid": ssid, "attempts": [], "start": time.time()}

    def save() -> None:
        log_path.write_text(json.dumps(log, indent=2), encoding="utf-8")

    iwd = w.Iwd()
    station, found, _ = w.current(iwd)
    home = next(n for n in found if n.connected)
    log["home"], log["home_address"] = home.ssid, address()
    iwd.scan(station)
    station, found, _ = w.current(iwd)
    target = next((n for n in found if n.ssid == ssid), None)
    if target is None:
        log["result"] = "not in range"
        save()
        return 1
    profile = None
    try:
        for number, passphrase in enumerate(candidates):
            profile = w.write_profile(w.PROFILE_DIR, ssid, target.kind, passphrase)
            deadline = time.monotonic() + w.PROFILE_WAIT_S
            while "KnownNetwork" not in iwd.objects().get(target.path, {}).get(f"{w.IWD}.Network", {}):
                if time.monotonic() > deadline:
                    break
                time.sleep(0.25)
            began = time.monotonic()
            try:
                iwd.call(target.path, "Network", "Connect", timeout=60)
            except w.IwdError as error:
                log["attempts"].append({"candidate": number, "ok": False, "seconds": round(time.monotonic() - began, 1),
                                        "message": w.failure_message(str(error))})
                w.forget_new(iwd, target.path, profile)
                profile = None
                save()
                continue
            time.sleep(3)
            log["attempts"].append({"candidate": number, "ok": True, "seconds": round(time.monotonic() - began, 1),
                                    "address": address(), "bar": w.bar_text(iwd)})
            save()
            break
    finally:
        if profile is not None:  # forget the test network so iwd prefers home
            w.forget_new(iwd, target.path, profile)
        for _ in range(3):
            try:
                iwd.call(home.path, "Network", "Connect", timeout=60)
                break
            except w.IwdError as error:
                log["home_retry"] = w.failure_message(str(error))
                time.sleep(5)
        time.sleep(3)
        log["back_home"], log["back_address"] = w.bar_text(iwd), address()
        log["profiles_left"] = sorted(p.name for p in w.PROFILE_DIR.iterdir() if p.name.startswith(ssid))
        log["host"] = socket.gethostname()
        save()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
