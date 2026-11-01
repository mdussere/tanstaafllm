"""Static safety checks for the user-run dArkOS Wi-Fi/SSH configuration script."""

from pathlib import Path
import subprocess


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPOSITORY_ROOT / "worklines/luna/scripts/configure_darkos_ssh.sh"


def test_darkos_configuration_script_parses() -> None:
    subprocess.run(["bash", "-n", str(SCRIPT)], check=True)


def test_darkos_configuration_script_does_not_embed_a_wifi_secret() -> None:
    script = SCRIPT.read_text(encoding="utf-8")

    assert "Home network" not in script
    assert "psk=" not in script
    assert "/run/NetworkManager/system-connections" in script
    assert "interface-name=/d" in script
    assert "Physical panel timing is selected by BOOT DTBs" in script
    assert "r36_config.ini" not in script
