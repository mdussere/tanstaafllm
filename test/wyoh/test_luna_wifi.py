"""Step 7.4: Wyoh's Wi-Fi panel on Luna.

Contract: `luna_wifi.feature`. Switching networks cuts the desk's SSH, so the
join is run on Luna by `luna_wifi_switch.py`, detached, which always returns
to the starting network; the test waits for Luna to come back and reads its log.

Run with:
    WYOH_LUNA_LIVE=1 WYOH_WIFI_TEST_SSID=<ssid> WYOH_WIFI_TEST_PASSPHRASES=<one per line> \
        uv run pytest -m live test/wyoh/test_luna_wifi.py
The passphrases travel over SSH's stdin to a mode-600 file on Luna's /run,
deleted on reading; they are never written to results/.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

import pytest

from test_luna_minimal_env import HOST, SSH_MUX, _ssh

pytestmark = pytest.mark.live
SCRIPT = Path(__file__).with_name("luna_wifi_switch.py")
REMOTE_SCRIPT = "/run/wyoh/luna_wifi_switch.py"
REMOTE_LOG = "/run/wyoh/wifi-switch.json"


def test_luna_joins_a_second_network_and_comes_home() -> None:
    if os.environ.get("WYOH_LUNA_LIVE") != "1":
        pytest.skip("set WYOH_LUNA_LIVE=1, WYOH_WIFI_TEST_SSID and WYOH_WIFI_TEST_PASSPHRASES")
    ssid = os.environ["WYOH_WIFI_TEST_SSID"]
    secrets = os.environ["WYOH_WIFI_TEST_PASSPHRASES"].replace("\\n", "\n")
    result_dir = Path("results/wyoh/luna-wifi") / datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    result_dir.mkdir(parents=True, exist_ok=False)

    copied = subprocess.run(["scp", *SSH_MUX, "-q", str(SCRIPT), f"{HOST}:{REMOTE_SCRIPT}"],
                            capture_output=True, text=True, timeout=60, check=False)
    assert copied.returncode == 0, copied.stderr
    secret_file = f"/run/wyoh/wifi-test-{os.getpid()}"
    stored = subprocess.run(["ssh", *SSH_MUX, HOST, f"umask 077; rm -f {REMOTE_LOG}; cat > {secret_file}"],
                            input=secrets + "\n", capture_output=True, text=True, timeout=30, check=False)
    assert stored.returncode == 0, stored.stderr
    started = _ssh(f"systemd-run --unit=wyoh-wifi-switch-{os.getpid()} --collect "
                   f"/usr/bin/python3 {REMOTE_SCRIPT} '{ssid}' {secret_file} {REMOTE_LOG}")
    assert started.returncode == 0, started.stderr

    time.sleep(10)
    log = None
    deadline = time.monotonic() + 300
    while time.monotonic() < deadline:
        try:
            read = subprocess.run(["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes", HOST, f"cat {REMOTE_LOG}"],
                                  capture_output=True, text=True, timeout=15, check=False)
        except subprocess.TimeoutExpired:
            read = None
        if read is not None and read.returncode == 0 and read.stdout.strip():
            candidate = json.loads(read.stdout)
            if "back_home" in candidate:
                log = candidate
                break
        time.sleep(5)
    assert log is not None, "Luna did not come back within 5 minutes (check it from the console)"
    (result_dir / "wifi-switch.json").write_text(json.dumps(log, indent=2), encoding="utf-8")
    assert secrets.split("\n")[0] not in json.dumps(log)

    assert any(attempt["ok"] for attempt in log["attempts"]), log["attempts"]
    joined = next(attempt for attempt in log["attempts"] if attempt["ok"])
    assert joined["address"] and joined["bar"].startswith(ssid)
    assert log["back_home"].startswith(log["home"]) and log["back_address"] == log["home_address"]
    assert log["profiles_left"] == []
