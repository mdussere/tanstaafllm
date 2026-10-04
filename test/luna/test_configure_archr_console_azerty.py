"""Static and source-asset checks for the offline ArchR AZERTY loader."""

from pathlib import Path
from hashlib import sha256
import subprocess

import pytest


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPOSITORY_ROOT / "worklines/luna/scripts/configure_archr_console_azerty.sh"
KEYMAP_SOURCE = Path("/data/michael/tanstaafllm/luna-assets/kbd-keymaps-v2.7.1/keymaps/i386")


def test_azerty_loader_script_parses_and_has_reversible_guards() -> None:
    subprocess.run(["bash", "-n", str(SCRIPT)], check=True)
    script = SCRIPT.read_text(encoding="utf-8")

    assert "[[ ${EUID} -eq 0" in script
    assert "LOADKEYS_KEYMAP_PATH" in script
    assert "loadkeys --console /dev/tty1 --bkeymap fr" in script
    assert "busybox loadkmap" in script
    assert "--restore" in script
    assert "10-tanstaafllm-azerty.conf" in script
    assert "fr.bkeymap" in script
    assert "kbd-keymaps-v2.7.1" in script


@pytest.mark.integration
def test_cached_official_french_map_has_required_includes() -> None:
    assert (KEYMAP_SOURCE / "azerty/fr.map").is_file()
    assert (KEYMAP_SOURCE / "include/azerty-layout.inc").is_file()
    assert sha256((KEYMAP_SOURCE / "azerty/fr.map").read_bytes()).hexdigest() == (
        "da1c27ccde8ceb034c53c6a2c279ddf3b2c510a4fbe9370248299978c713bf7b"
    )
    source_marker = KEYMAP_SOURCE.parents[1] / "UPSTREAM-SOURCE"
    assert "v2.7.1 f2c0d3185b300780f4f69abe3ff7493ec7634f39" in source_marker.read_text(
        encoding="utf-8"
    )
    assert (KEYMAP_SOURCE / "include/linux-with-alt-and-altgr.inc").is_file()
