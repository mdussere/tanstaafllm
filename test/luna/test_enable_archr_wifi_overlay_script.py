"""Deterministic install/restore checks for the ArchR Wi-Fi overlay script."""

from pathlib import Path
import subprocess


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPOSITORY_ROOT / "worklines/luna/scripts/enable_archr_wifi_overlay.sh"
CONFIG = """LABEL ArchR
  LINUX /KERNEL
  FDTDIR /dtbs/
  FDTOVERLAYS /overlays/mipi-panel.dtbo
  APPEND boot=${partition_boot} quiet systemd.unit=textmode.target
"""


def make_boot(tmp_path: Path, config: str = CONFIG) -> Path:
    boot = tmp_path / "ARCHR"
    (boot / "extlinux").mkdir(parents=True)
    (boot / "overlays").mkdir()
    (boot / "overlays/mipi-panel.dtbo").write_bytes(b"panel")
    (boot / "extlinux/extlinux.conf").write_text(config, encoding="utf-8")
    return boot


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["bash", str(SCRIPT), *args], capture_output=True, text=True)


def test_install_changes_only_the_overlay_line_and_restores(tmp_path: Path) -> None:
    boot = make_boot(tmp_path)
    config = boot / "extlinux/extlinux.conf"

    result = run(str(boot))
    assert result.returncode == 0, result.stderr
    assert (boot / "overlays/wifi-rk915.dtbo").read_bytes() == (
        REPOSITORY_ROOT / "worklines/luna/data/wifi-rk915.dtbo"
    ).read_bytes()
    assert config.read_text(encoding="utf-8") == CONFIG.replace(
        "mipi-panel.dtbo\n", "mipi-panel.dtbo /overlays/wifi-rk915.dtbo\n"
    )
    assert (boot / "extlinux/extlinux.conf.tanstaafllm-before-wifi-overlay").read_text(
        encoding="utf-8"
    ) == CONFIG

    (boot / "overlays/wifi-rk915.dtbo").write_bytes(b"older revision")
    installed = config.read_text(encoding="utf-8")
    result = run(str(boot))  # a second run only refreshes the overlay file
    assert result.returncode == 0, result.stderr
    assert "boot configuration unchanged" in result.stdout
    assert config.read_text(encoding="utf-8") == installed
    assert (boot / "overlays/wifi-rk915.dtbo").read_bytes() == (
        REPOSITORY_ROOT / "worklines/luna/data/wifi-rk915.dtbo"
    ).read_bytes()

    result = run("--restore", str(boot))
    assert result.returncode == 0, result.stderr
    assert config.read_text(encoding="utf-8") == CONFIG


def test_refuses_unexpected_overlay_line(tmp_path: Path) -> None:
    boot = make_boot(tmp_path, CONFIG.replace("mipi-panel.dtbo", "other.dtbo"))

    result = run(str(boot))
    assert result.returncode != 0
    assert "Unexpected FDTOVERLAYS line" in result.stderr
    assert not (boot / "overlays/wifi-rk915.dtbo").exists()


def test_refuses_non_boot_directory(tmp_path: Path) -> None:
    result = run(str(tmp_path))
    assert result.returncode != 0
    assert "Not an ArchR BOOT mount" in result.stderr


def test_refuses_update_when_backup_exists_but_line_is_not_installed(tmp_path: Path) -> None:
    boot = make_boot(tmp_path)
    (boot / "extlinux/extlinux.conf.tanstaafllm-before-wifi-overlay").write_text(CONFIG)

    result = run(str(boot))
    assert result.returncode != 0
    assert "not the installed form" in result.stderr
