"""Static safety checks for the user-run, read-only factory-card archive script."""

from pathlib import Path
import subprocess


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPOSITORY_ROOT / "worklines/luna/scripts/archive_factory_emuelec_card.sh"


def test_archive_factory_card_script_parses() -> None:
    subprocess.run(["bash", "-n", str(SCRIPT)], check=True)


def test_archive_factory_card_script_has_required_safety_gates() -> None:
    script = SCRIPT.read_text(encoding="utf-8")

    assert "EXPECTED_SIZE=52428800000" in script
    assert "b101033c-7e9b-4403-be0f-fa3cc86905e4" in script
    assert "Source must be a whole disk" in script
    assert "Source is not removable" in script
    assert "not the factory card" in script
    assert 'blockdev --setro "$device"' in script
    assert "refusing to overwrite" in script
    assert "zstd -t" in script
    assert "MISMATCH" in script


def test_archive_factory_card_script_never_writes_the_card() -> None:
    script = SCRIPT.read_text(encoding="utf-8")

    assert "of=" not in script
    assert "rm " not in script
    assert "mkfs" not in script
    assert "--setrw" not in script
