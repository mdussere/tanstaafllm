"""Static safety checks for the user-run card scripts of Mannie's Step 7.

backup-luna-card.sh only reads the card; write-luna-root.sh replaces ARCHR_ROOT
only, after its own backup. Neither is run by the test suite.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BACKUP = REPO / "src/mannie/luna/backup-luna-card.sh"
WRITE = REPO / "src/mannie/alarm/write-luna-root.sh"


def test_scripts_parse() -> None:
    for script in (BACKUP, WRITE):
        subprocess.run(["bash", "-n", str(script)], check=True)


def test_backup_pins_the_card_and_verifies() -> None:
    script = BACKUP.read_text(encoding="utf-8")
    assert "EXPECTED_SIZE=62534975488" in script
    for uuid in ("2900-7A2B", "3cf95927-e0f1-4043-ad1d-fe04cae2f642", "27afae0b-7cbb-4e80-b91f-f46b9fde0a6e", "a2bafe90-b2fb-47d9-91d8-f78c3090d63d"):
        assert uuid in script
    for gate in ("Source must be a whole disk", "Source is not removable", "not Luna's card", "system-root disk", 'blockdev --setro "$device"', "refusing to overwrite", "zstd -t", "MISMATCH", "ro,noload"):
        assert gate in script


def test_backup_never_writes_the_card() -> None:
    script = BACKUP.read_text(encoding="utf-8")
    for forbidden in ("of=", "mkfs", "--setrw", "e2image", "rm -", "rm \""):
        assert forbidden not in script


def test_write_script_backs_up_first_and_asks() -> None:
    script = WRITE.read_text(encoding="utf-8")
    assert script.index('e2image -ra -p "$ROOTPART" "$BACKUP"') < script.index('e2image -ra -p "$IMAGE" "$ROOTPART"')
    assert "WRITE-LUNA-ROOT" in script and "is not removable" in script
    assert "of=" not in script and "mkfs" not in script
