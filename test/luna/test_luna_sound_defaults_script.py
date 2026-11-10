"""Offline checks for worklines/luna/scripts/luna_sound_defaults.sh (Luna Step 9.3).

The installed jack switch runs against a fake `amixer` that reports the jack
state and records the mux it is asked to set.
"""

import os
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parents[2] / "worklines/luna/scripts/luna_sound_defaults.sh"

FAKE_AMIXER = """#!/bin/sh
case "$*" in
  *"cget iface=CARD,name=Headphones Jack"*) echo "  : values=$JACK" ;;
  *cget*) echo "amixer: Cannot find the given element" >&2; exit 1 ;;
  *cset*) echo "$*" >> "$LOG" ;;
esac
"""


@pytest.fixture
def root(tmp_path: Path) -> Path:
    (tmp_path / "var/lib/alsa").mkdir(parents=True)
    (tmp_path / "var/lib/alsa/asound.state").write_text("state before\n")
    return tmp_path


def run(root: Path, mode: str) -> subprocess.CompletedProcess:
    env = {**os.environ, "LUNA_ROOT": str(root)}
    return subprocess.run(["sh", str(SCRIPT), mode], env=env, capture_output=True, text=True)


def test_script_is_valid_posix_sh():
    subprocess.run(["sh", "-n", str(SCRIPT)], check=True)


def test_apply_installs_the_switch_and_its_unit(root: Path):
    result = run(root, "--apply")
    assert result.returncode == 0, result.stderr
    unit = (root / "etc/systemd/system/luna-jack-switch.service").read_text()
    assert "ExecStart=/usr/local/bin/luna-jack-switch" in unit
    assert "WantedBy=multi-user.target" in unit
    assert (root / "var/lib/alsa/asound.state.before-luna-sound").read_text() == "state before\n"


@pytest.mark.parametrize(("jack", "mux"), [("off", "SPK"), ("on", "HP")])
def test_switch_follows_the_jack(root: Path, tmp_path: Path, jack: str, mux: str):
    run(root, "--apply")
    bin_dir = tmp_path / "fakebin"
    bin_dir.mkdir()
    (bin_dir / "amixer").write_text(FAKE_AMIXER)
    (bin_dir / "amixer").chmod(0o755)
    log = tmp_path / "amixer.log"
    env = {**os.environ, "PATH": f"{bin_dir}:{os.environ['PATH']}", "JACK": jack, "LOG": str(log)}
    subprocess.run([str(root / "usr/local/bin/luna-jack-switch"), "--once"], env=env, check=True)
    assert log.read_text().split()[-1] == mux


def test_undo_restores_the_state_and_removes_the_files(root: Path):
    run(root, "--apply")
    (root / "var/lib/alsa/asound.state").write_text("state after\n")
    result = run(root, "--undo")
    assert result.returncode == 0, result.stderr
    assert (root / "var/lib/alsa/asound.state").read_text() == "state before\n"
    assert not (root / "usr/local/bin/luna-jack-switch").exists()
    assert not (root / "etc/systemd/system/luna-jack-switch.service").exists()
