"""Static safety checks for the destructive, user-run ArchR transition script."""

from pathlib import Path
import subprocess


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPOSITORY_ROOT / "worklines/luna/scripts/archive_darkos_and_flash_archr.sh"


def test_archive_and_flash_archr_script_parses() -> None:
    subprocess.run(["bash", "-n", str(SCRIPT)], check=True)


def test_archive_and_flash_archr_script_has_required_safety_gates() -> None:
    script = SCRIPT.read_text(encoding="utf-8")

    assert "EXPECTED_SERIAL=000000002964" in script
    assert "Target must be a whole disk" in script
    assert "Target is not removable" in script
    assert "Unexpected serial" in script
    assert "ERASE-TEST-CARD" in script
    assert "zstd -t" in script
    assert 'sha256sum -c "$snapshot.sha256"' in script
    assert 'sha256sum -c "$ARCHR_SUM"' in script
    assert 'dd of="$target"' in script
    assert "must subsequently install the specific" in script
    assert "Do not boot Luna yet" in script
    assert "r36-ultra.dtb" in script
    assert "rm " not in script
