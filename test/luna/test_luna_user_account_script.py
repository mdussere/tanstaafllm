"""Offline checks for worklines/luna/scripts/luna_user_account.sh (Luna Step 7.0).

The script runs against a fake ArchR root (LUNA_ROOT) that mimics the real
layout: /etc/shadow is a link to /storage/.cache/shadow.
"""

import os
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[2] / "worklines/luna/scripts/luna_user_account.sh"

PASSWD = "root:x:0:0:root:/storage:/bin/sh\n"
GROUP = "root:x:0:\nwheel:x:10:root\ninput:x:97:\nvideo:x:91:\naudio:x:92:\n"
SHADOW = "root:$6$hash:20000:0:99999:7:::\n"


@pytest.fixture
def root(tmp_path: Path) -> Path:
    (tmp_path / "etc").mkdir()
    (tmp_path / "bin").mkdir()
    (tmp_path / "usr/bin").mkdir(parents=True)
    (tmp_path / "home").mkdir()
    (tmp_path / "storage/.cache").mkdir(parents=True)
    (tmp_path / "storage/.ssh").mkdir()
    (tmp_path / "etc/passwd").write_text(PASSWD)
    (tmp_path / "etc/group").write_text(GROUP)
    (tmp_path / "storage/.cache/shadow").write_text(SHADOW)
    (tmp_path / "etc/shadow").symlink_to("../storage/.cache/shadow")
    (tmp_path / "usr/cache").mkdir()
    (tmp_path / "usr/cache/shadow").write_text(SHADOW)  # rebuilt into the link at boot
    (tmp_path / "storage/.ssh/authorized_keys").write_text("ssh-ed25519 AAAA test\n")
    for exe in ("bin/sh", "usr/bin/sudo"):
        (tmp_path / exe).write_text("#!/bin/sh\n")
        (tmp_path / exe).chmod(0o755)
    (tmp_path / "usr/bin/sudo").chmod(0o4755)  # a real sudo is setuid
    return tmp_path


def run(root: Path, mode: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "LUNA_ROOT": str(root)}
    return subprocess.run(["sh", str(SCRIPT), mode], env=env, capture_output=True, text=True)


def test_script_is_valid_posix_sh():
    subprocess.run(["sh", "-n", str(SCRIPT)], check=True)


def test_apply_adds_one_account_through_the_shadow_link(root: Path):
    result = run(root, "--apply")
    assert result.returncode == 0, result.stderr

    assert (root / "etc/passwd").read_text() == PASSWD + "michael:x:1000:1000:Michael:/home/michael:/bin/sh\n"
    assert (root / "etc/shadow").is_symlink()
    shadow = (root / "storage/.cache/shadow").read_text().splitlines()
    assert shadow[0] == SHADOW.strip()
    assert shadow[1].startswith("michael:*:")
    assert (root / "usr/cache/shadow").read_text().splitlines()[1].startswith("michael:*:")

    group = (root / "etc/group").read_text().splitlines()
    assert "wheel:x:10:root,michael" in group
    assert "input:x:97:michael" in group
    assert "audio:x:92:michael" in group
    assert "michael:x:1000:" in group
    assert "warning: no group render" in result.stdout

    assert (root / "home/michael/.ssh/authorized_keys").read_text() == "ssh-ed25519 AAAA test\n"
    assert oct((root / "home/michael/.ssh").stat().st_mode & 0o777) == "0o700"
    assert (root / "etc/sudoers.d/10-luna-wheel").read_text() == "%wheel ALL=(ALL:ALL) NOPASSWD: ALL\n"


def test_apply_backs_up_the_real_files_first(root: Path):
    run(root, "--apply")
    (backup,) = (root / "storage/.local/share/luna-accounts").glob("*-before-apply")
    assert (backup / "passwd").read_text() == PASSWD
    assert (backup / "group").read_text() == GROUP
    assert (backup / "shadow").read_text() == SHADOW


def test_apply_refuses_twice(root: Path):
    run(root, "--apply")
    again = run(root, "--apply")
    assert again.returncode != 0
    assert "already exists" in again.stderr


def test_apply_refuses_a_taken_id(root: Path):
    (root / "etc/passwd").write_text(PASSWD + "other:x:1000:1000::/:/bin/sh\n")
    result = run(root, "--apply")
    assert result.returncode != 0
    assert "michael" not in (root / "etc/passwd").read_text()


@pytest.mark.parametrize("sudo", ["absent", "archr-shim"])
def test_apply_without_a_setuid_sudo_skips_the_dropin(root: Path, sudo: str):
    if sudo == "absent":
        (root / "usr/bin/sudo").unlink()
    else:
        (root / "usr/bin/sudo").chmod(0o755)
    result = run(root, "--apply")
    assert result.returncode == 0, result.stderr
    assert "no setuid sudo" in result.stdout
    assert not (root / "etc/sudoers.d/10-luna-wheel").exists()


def test_undo_restores_the_files_and_keeps_the_home(root: Path):
    run(root, "--apply")
    result = run(root, "--undo")
    assert result.returncode == 0, result.stderr
    assert (root / "etc/passwd").read_text() == PASSWD
    assert (root / "etc/group").read_text() == GROUP
    assert (root / "storage/.cache/shadow").read_text() == SHADOW
    assert (root / "usr/cache/shadow").read_text() == SHADOW
    assert (root / "etc/shadow").is_symlink()
    assert not (root / "etc/sudoers.d/10-luna-wheel").exists()
    assert (root / "home/michael/.ssh/authorized_keys").exists()


def test_check_changes_nothing(root: Path):
    before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    result = run(root, "--check")
    assert result.returncode == 0, result.stderr
    assert "no michael in passwd" in result.stdout
    assert {p: p.read_bytes() for p in root.rglob("*") if p.is_file()} == before
