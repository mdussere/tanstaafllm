"""Static safety checks for the reversible dArkOS R36 Ultra display fallback."""

from pathlib import Path
import subprocess


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    REPOSITORY_ROOT
    / "worklines/luna/scripts/select_darkos_ultra_display_fallback.sh"
)


def test_darkos_ultra_fallback_script_parses() -> None:
    subprocess.run(["bash", "-n", str(SCRIPT)], check=True)


def test_darkos_ultra_fallback_is_explicit_and_reversible() -> None:
    script = SCRIPT.read_text(encoding="utf-8")

    assert "GR36-MB V1.1-20250422" in script
    assert "tanstaafllm-before-ultra-display" in script
    assert '[[ ! -e $backup_dir ]]' in script
    assert "Refusing to overwrite existing rollback directory" in script
    assert "logo-720x720.bmp" in script
    assert "rm " not in script
