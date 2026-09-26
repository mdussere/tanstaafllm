from __future__ import annotations

import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path

import pytest


REMOTE_INVENTORY = r'''
set -eu
printf '%s\n' '## identity'
id
uname -a
sed -n '1,80p' /etc/os-release
printf '%s\n' '## boot-and-storage'
sed -n '1p' /proc/cmdline
mount
 df -h
printf '%s\n' '## memory'
sed -n '1,24p' /proc/meminfo
printf '%s\n' '## graphics'
printf '%s\\n' '## hardware'
sed -n '1,160p' /proc/cpuinfo
sed -n '1,80p' /proc/fb 2>/dev/null || true
find /sys/class/graphics -maxdepth 2 -printf '%p\n' 2>/dev/null | sort || true
find /sys/class/drm -maxdepth 2 -printf '%p\n' 2>/dev/null | sort || true
find /dev/dri -maxdepth 1 -printf '%f\n' 2>/dev/null | sort || true
find /sys/class/drm -maxdepth 2 -name status -exec sh -c 'printf "%s=" "$1"; sed -n "1p" "$1"' sh {} \; 2>/dev/null || true
printf '%s\n' '## input'
find /dev/input -maxdepth 1 -name 'event*' -printf '%f\n' 2>/dev/null | sort || true
printf '%s\n' '## session-processes'
for proc in /proc/[0-9]*; do
  name=$(sed -n '1p' "$proc/comm" 2>/dev/null || true)
  case "$name" in
    *mulation*|weston|sway|kodi|retroarch|xorg|Xorg)
      rss=$(sed -n 's/^VmRSS:[[:space:]]*\([0-9]*\).*/\1/p' "$proc/status" 2>/dev/null || true)
      printf '%s pid=%s rss_kib=%s\n' "$name" "${proc##*/}" "${rss:-0}"
      ;;
  esac
done
printf '%s\\n' '## top-memory-processes'
for proc in /proc/[0-9]*; do
  rss=$(sed -n 's/^VmRSS:[[:space:]]*\\([0-9]*\\).*/\\1/p' "$proc/status" 2>/dev/null || true)
  name=$(sed -n '1p' "$proc/comm" 2>/dev/null || true)
  test -n "$rss" && printf '%s %s %s\n' "$rss" "${proc##*/}" "$name"
done | sort -nr | head -n 12
printf '%s\n' '## ssh'
ps w | grep -E '[s]shd|[d]ropbear' || true
'''


@pytest.mark.live
def test_luna_stock_inventory_is_read_only() -> None:
    if os.environ.get("LUNA_STOCK_LIVE") != "1":
        pytest.skip("set LUNA_STOCK_LIVE=1 to inventory the preserved Luna card")
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    result_dir = Path("results/wyoh/luna-stock-inventory") / timestamp
    result_dir.mkdir(parents=True, exist_ok=False)
    completed = subprocess.run(
        ["ssh", "luna", "sh", "-s"],
        input=REMOTE_INVENTORY.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=45,
        check=False,
    )
    (result_dir / "ssh.stdout.log").write_bytes(completed.stdout)
    (result_dir / "ssh.stderr.log").write_bytes(completed.stderr)
    assert completed.returncode == 0, completed.stderr.decode(errors="replace")
    output = completed.stdout.decode(errors="replace")
    assert "## identity" in output
    assert 'ID="emuelec"' in output
    assert "## boot-and-storage" in output
    assert "## graphics" in output
    assert "## input" in output
    assert "## session-processes" in output
    assert "## ssh" in output
