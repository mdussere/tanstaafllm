"""Mannie Step 7: the Arch Linux ARM root for Luna (`alarm_root.feature`).

The account and resolver checks run by default. The image check is an integration
test: it reads a built image with debugfs (read-only) and needs
MANNIE_ALARM_IMAGE=<path to luna-alarm-root.ext4>.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).parents[2]
ALARM = REPO / "src/mannie/alarm"
sys.path.insert(0, str(ALARM))
import fetch_packages  # noqa: E402

IMAGE = os.environ.get("MANNIE_ALARM_IMAGE")


def test_accounts_replace_alarm_with_michael(tmp_path: Path) -> None:
    etc = tmp_path / "etc"
    etc.mkdir()
    (etc / "passwd").write_text("root:x:0:0::/root:/usr/bin/bash\nalarm:x:1000:1000::/home/alarm:/bin/bash\n")
    (etc / "shadow").write_text("root:$6$x:19000::::::\nalarm:$6$y:19000::::::\n")
    (etc / "group").write_text("wheel:x:998:alarm\naudio:x:995:\nalarm:x:1000:\nusers:x:984:\n")
    (etc / "gshadow").write_text("wheel:!*::alarm\naudio:!*::\nalarm:!::\n")
    subprocess.run([sys.executable, str(ALARM / "accounts.py"), str(etc)], check=True)
    passwd, shadow, group = ((etc / n).read_text() for n in ("passwd", "shadow", "group"))
    assert "alarm" not in passwd + shadow + group + (etc / "gshadow").read_text()
    assert "michael:x:1000:1000:Michael:/home/michael:/bin/bash" in passwd
    assert shadow.startswith("root:!*:19000")
    assert "wheel:x:998:michael\n" in group and "audio:x:995:michael\n" in group and "users:x:984:\n" in group


def test_resolver_skips_what_the_base_has() -> None:
    sync = {
        "git": {"DEPENDS": ["perl", "zlib-ng", "glibc"]},
        "perl": {"DEPENDS": ["glibc"]},
        "zlib-ng": {"DEPENDS": []},
        "sudo": {"DEPENDS": ["libpam.so=0-64"]},
        "pam": {"PROVIDES": ["libpam.so=0-64"]},
    }
    local = {"glibc": {}, "pam": {"PROVIDES": ["libpam.so=0-64"]}}
    assert fetch_packages.resolve(["sudo", "git"], sync, local) == ["sudo", "git", "perl", "zlib-ng"]


def _debugfs(command: str) -> str:
    return subprocess.run(["debugfs", "-R", command, IMAGE], capture_output=True, text=True).stdout


@pytest.mark.integration
@pytest.mark.skipif(not IMAGE or not shutil.which("debugfs"), reason="set MANNIE_ALARM_IMAGE to a built image")
def test_built_image() -> None:
    label = subprocess.run(["e2label", IMAGE], capture_output=True, text=True).stdout.strip()
    assert label == "ARCHR_ROOT"

    def stat(path: str) -> str:
        return _debugfs(f"stat {path}")

    for path, mode in {
        "/etc/sudoers.d/10-michael": "0440",
        "/root/.ssh/authorized_keys": "0600",
        "/etc/shadow": "0600",
        "/flash": "0755",
        "/storage": "0755",
        "/usr/local/sbin/luna-firstboot": "0755",
        "/usr/bin/passwd": "04755",
    }.items():
        assert f"Mode:  {mode}" in stat(path), path
        assert "User:     0   Group:     0" in stat(path), path
    assert 'Fast link dest: "../../../../modules/6.12.94"' in stat("/usr/lib/kernel-overlays/base/lib/modules/6.12.94")
    assert "Type: regular" in stat("/usr/lib/modules/6.12.94/rk915/rk915.ko")
    assert "Type: regular" in stat("/usr/lib/firmware/rk915_fw.bin")

    passwd, shadow = _debugfs("cat /etc/passwd"), _debugfs("cat /etc/shadow")
    assert "michael:x:1000:1000:" in passwd and "alarm:" not in passwd
    assert "\nroot:!*:" in "\n" + shadow
    assert "IgnorePkg   = linux-aarch64" in _debugfs("cat /etc/pacman.conf")
    assert "HostKey /storage/.cache/ssh/ssh_host_ed25519_key" in _debugfs("cat /etc/ssh/sshd_config.d/10-luna.conf")
    assert "LABEL=LUNA_HOME" in _debugfs("cat /etc/fstab")
    wants = _debugfs("ls /etc/systemd/system/multi-user.target.wants")
    assert "luna-firstboot.service" in wants and "sshd.service" in wants
    assert "systemd-networkd-wait-online" not in _debugfs("ls /etc/systemd/system/network-online.target.wants")
    cached = _debugfs("ls /var/cache/luna-firstboot")
    for line in _debugfs("cat /var/cache/luna-firstboot/luna-firstboot-packages.txt").split():
        assert line in cached and f"{line}.sig" in cached
