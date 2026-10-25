"""Mannie 2.5: persona and project snapshot for Claude Code (`mannie_context.feature`).

The bundle checks run by default. The deployment and the request are live, with the
same target switch as test_luna_pi_claude.py: MANNIE_LUNA_PI_LIVE=1 (luna-pi) or
MANNIE_LUNA_LIVE=1 (Luna, held through worklines/luna-access.md).
"""

from __future__ import annotations

import io
import json
import re
import sys
import tarfile
from pathlib import Path

import pytest

from test_luna_pi_claude import CLAUDE, HOST, LIVE, SECRET, _logged_in, _probe, _save, _save_run, _ssh, remote_ready  # noqa: F401

REPO = Path(__file__).parents[2]
sys.path.insert(0, str(REPO / "src" / "mannie"))
import build_context  # noqa: E402

REMOTE_CONTEXT = ".local/share/tanstfaafllm/mannie/context"
# Loaded into every session, so it is paid for in tokens on every request.
PERSONA_MAX_BYTES = 4096
live = pytest.mark.skipif(not LIVE, reason="set MANNIE_LUNA_PI_LIVE=1 (luna-pi) or MANNIE_LUNA_LIVE=1 (Luna)")


def test_bundle_layout(tmp_path: Path) -> None:
    files = build_context.build(tmp_path / "context")
    context = tmp_path / "context"
    assert (context / "MANNIE.md").read_bytes() == build_context.PERSONA.read_bytes()
    assert re.match(r"commit: \S+\nuncommitted changes: (yes|no)\nbuilt: \d{4}-", (context / "VERSION").read_text())
    for required in ("README.md", "AGENTS.md", "docs/README.md", "docs/13_mannie.md", "worklines/mannie/plan_mannie.md"):
        assert Path(required) in files
        assert (context / "repo" / required).is_file()
    index = (context / "repo/INDEX.md").read_text()
    assert all(f"`{relative}`" in index for relative in files)
    assert not any(part.startswith(".") for relative in files for part in relative.parts)


def test_bundle_holds_no_secret(tmp_path: Path) -> None:
    build_context.build(tmp_path / "context")
    leaks = [p for p in (tmp_path / "context").rglob("*") if p.is_file() and SECRET.search(p.read_text(errors="replace"))]
    # The intent document describes the credential pattern itself; nothing else may match.
    assert [p.name for p in leaks if p.name != "0101_01_mannie-on-luna-intent.md"] == []


def test_persona_is_small_and_points_to_the_clone() -> None:
    text = build_context.PERSONA.read_text(encoding="utf-8")
    assert len(text.encode()) <= PERSONA_MAX_BYTES
    assert "~/git/tanstfaafllm" in text and "cell/mannie" in text and "plan_mannie.md" in text
    assert build_context.IMPORT_LINE == f"@~/{REMOTE_CONTEXT}/MANNIE.md"


def _tarball(source: Path) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        archive.add(source, arcname="context")
    return buffer.getvalue()


@live
@pytest.mark.live
@pytest.mark.timeout(600)
def test_deploy(tmp_path: Path) -> None:
    build_context.build(tmp_path / "context")
    staging = f"$HOME/{REMOTE_CONTEXT}.new"
    unpack = _ssh(f"rm -rf {staging} && mkdir -p {staging} && tar -xzf - -C {staging} --strip-components=1", stdin=_tarball(tmp_path / "context"), timeout=500)
    assert unpack.returncode == 0, unpack.stderr
    # Swap in the new snapshot, then make sure ~/.claude/CLAUDE.md imports the persona.
    # The user's own lines in that file are kept.
    swap = _ssh(
        f"rm -rf $HOME/{REMOTE_CONTEXT}.old; if [ -d $HOME/{REMOTE_CONTEXT} ]; then mv $HOME/{REMOTE_CONTEXT} $HOME/{REMOTE_CONTEXT}.old; fi; "
        f"mv {staging} $HOME/{REMOTE_CONTEXT} && rm -rf $HOME/{REMOTE_CONTEXT}.old && chmod -R a+rX,go-w $HOME/{REMOTE_CONTEXT} && "
        f"mkdir -p $HOME/.claude && touch $HOME/.claude/CLAUDE.md && "
        f"(grep -qxF '{build_context.IMPORT_LINE}' $HOME/.claude/CLAUDE.md || printf '%s\\n' '{build_context.IMPORT_LINE}' >> $HOME/.claude/CLAUDE.md) && "
        f"cat $HOME/.claude/CLAUDE.md; echo; cat $HOME/{REMOTE_CONTEXT}/VERSION; du -sk $HOME/{REMOTE_CONTEXT}; find $HOME/{REMOTE_CONTEXT} -type f | wc -l"
    )
    text = _save_run("context-deploy.txt", swap)
    assert swap.returncode == 0
    assert build_context.IMPORT_LINE in text.splitlines()


@live
@pytest.mark.live
@pytest.mark.timeout(300)
def test_knows_who_and_where(remote_ready: None) -> None:
    """One request: does Claude answer as Mannie (user-level CLAUDE.md, any directory), and know the snapshot?"""
    if not _logged_in():
        pytest.skip(f"the user has not logged in on {HOST} yet")
    prompt = "Who are you, in one sentence, and where is your clone of the repository? Do not use any tool."
    run = _probe("context-request.json", f"time {CLAUDE} -p '{prompt}' --output-format json", timeout=240)
    assert run["exit_status"] == 0, run["stderr"]
    reply = json.loads(run["stdout"])
    _save(
        "context-request-summary.json",
        json.dumps(
            {key: run[key] for key in ("wall_s", "user_s", "sys_s", "max_rss_kib", "min_mem_available_kib")}
            | {key: reply.get(key) for key in ("result", "duration_ms", "duration_api_ms", "num_turns", "usage", "total_cost_usd")},
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
    )
    answer = reply.get("result", "")
    assert "Mannie" in answer
    assert "git/tanstfaafllm" in answer
