from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

from sway_ipc_probe import FocusWorkspaceMediator, FocusWorkspaceRequest


class RecordingTransport:
    def __init__(self) -> None:
        self.commands: list[str] = []

    def command(self, command: str) -> None:
        self.commands.append(command)


def test_focus_mediator_rejects_without_side_effect() -> None:
    transport = RecordingTransport()
    mediator = FocusWorkspaceMediator()
    with pytest.raises(PermissionError):
        mediator.invoke(
            transport,
            FocusWorkspaceRequest(workspace="wyoh-proof", expected_revision=3, allowed=False),
            revision=3,
        )
    with pytest.raises(ValueError, match="stale"):
        mediator.invoke(
            transport,
            FocusWorkspaceRequest(workspace="wyoh-proof", expected_revision=2, allowed=True),
            revision=3,
        )
    with pytest.raises(ValueError, match="ambiguous"):
        mediator.invoke(
            transport,
            FocusWorkspaceRequest(workspace="wyoh proof", expected_revision=3, allowed=True),
            revision=3,
        )
    assert transport.commands == []


def test_focus_mediator_emits_only_a_fixed_workspace_command() -> None:
    transport = RecordingTransport()
    FocusWorkspaceMediator().invoke(
        transport,
        FocusWorkspaceRequest(workspace="wyoh-proof", expected_revision=3, allowed=True),
        revision=3,
    )
    assert transport.commands == ["workspace wyoh-proof"]


@pytest.mark.live
def test_luna_pi_headless_sway_ipc_proof() -> None:
    if os.environ.get("WYOH_LIVE") != "1":
        pytest.skip("set WYOH_LIVE=1 to run against luna-pi")
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    result_dir = Path("results/wyoh/sway-ipc") / timestamp
    result_dir.mkdir(parents=True, exist_ok=False)
    probe = Path(__file__).with_name("sway_ipc_probe.py")
    prefix = "/home/michael/.local/opt/wyoh-sway-1.10.1-test-20260926/usr"
    completed = subprocess.run(
        [
            "ssh",
            "luna-pi",
            "python3",
            "-",
            "--start-headless",
            "--sway-binary",
            f"{prefix}/bin/sway",
            "--library-path",
            f"{prefix}/lib/aarch64-linux-gnu",
        ],
        input=probe.read_bytes(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=45,
        check=False,
    )
    (result_dir / "ssh.stdout.log").write_bytes(completed.stdout)
    (result_dir / "ssh.stderr.log").write_bytes(completed.stderr)
    assert completed.returncode == 0, completed.stderr.decode("utf-8", errors="replace")
    payload = json.loads(completed.stdout)
    (result_dir / "proof.json").write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    assert payload["sway_version"] == "1.10.1"
    assert payload["proof"]["focused_workspace"] == "wyoh-proof"
    assert payload["proof"]["event"]["change"] == "focus"
    assert payload["idle_sample"]["rss_kib"] > 0
    assert payload["recovery_ms"] >= 0
