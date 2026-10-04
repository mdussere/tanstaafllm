"""Deterministic checks for the ArchR textmode boot-entry transformer."""

from pathlib import Path
import subprocess


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPOSITORY_ROOT / "worklines/luna/scripts/enable_archr_textmode_boot.sh"
ORIGINAL_CONFIG = """LABEL ArchR\n  LINUX /KERNEL\n  FDTOVERLAYS /overlays/mipi-panel.dtbo\n  APPEND quiet console=tty0\n"""


def make_boot_mount(tmp_path: Path) -> tuple[Path, Path]:
    boot = tmp_path / "ARCHR"
    config = boot / "extlinux" / "extlinux.conf"
    config.parent.mkdir(parents=True)
    config.write_text(ORIGINAL_CONFIG, encoding="utf-8")
    return boot, config


def test_textmode_script_parses() -> None:
    subprocess.run(["bash", "-n", str(SCRIPT)], check=True)


def test_enable_then_restore_changes_only_the_boot_argument(tmp_path: Path) -> None:
    boot, config = make_boot_mount(tmp_path)

    enabled = subprocess.run([str(SCRIPT), str(boot)], check=True, text=True, capture_output=True)
    backup = config.with_name("extlinux.conf.tanstaafllm-before-textmode")

    assert "Configured one-card ArchR textmode boot." in enabled.stdout
    assert backup.read_text(encoding="utf-8") == ORIGINAL_CONFIG
    assert config.read_text(encoding="utf-8") == ORIGINAL_CONFIG.replace(
        "APPEND quiet console=tty0", "APPEND quiet console=tty0 systemd.unit=textmode.target"
    )

    repeated = subprocess.run([str(SCRIPT), str(boot)], text=True, capture_output=True)
    assert repeated.returncode == 65
    assert "Backup already exists" in repeated.stderr

    restored = subprocess.run(
        [str(SCRIPT), "--restore", str(boot)], check=True, text=True, capture_output=True
    )
    assert "Restored graphical ArchR boot configuration" in restored.stdout
    assert config.read_text(encoding="utf-8") == ORIGINAL_CONFIG


def test_refuses_an_existing_systemd_unit_override(tmp_path: Path) -> None:
    boot, config = make_boot_mount(tmp_path)
    config.write_text(ORIGINAL_CONFIG + "  APPEND systemd.unit=rescue.target\n", encoding="utf-8")

    result = subprocess.run([str(SCRIPT), str(boot)], text=True, capture_output=True)

    assert result.returncode == 65
    assert "systemd.unit override already exists" in result.stderr
