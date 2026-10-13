"""Mannie Step 2: Claude Code on luna-pi (`luna_pi_claude.feature`).

Live only: needs MANNIE_LUNA_PI_LIVE=1. luna-pi is reserved for Mannie (user,
2026-10-11). Writes only under michael's home there; never uses sudo; never
reads the credential file. Intent: worklines/mannie/docs/0101_01.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import tempfile
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import pytest


LIVE = os.environ.get("MANNIE_LUNA_PI_LIVE") == "1"
pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(not LIVE, reason="set MANNIE_LUNA_PI_LIVE=1 to run on luna-pi"),
]

REPO = Path(__file__).parents[2]
HOST = "luna-pi"
SSH_MUX = ["-o", "ControlMaster=auto", "-o", f"ControlPath={Path.home()}/.ssh/cm/%r@%h:%p", "-o", "ControlPersist=15m"]
VERSION = "2.1.287"
PLATFORM = "linux-arm64"
RELEASES = "https://downloads.claude.ai/claude-code-releases"
SIGNING_KEY = "https://downloads.claude.ai/keys/claude-code.asc"
FINGERPRINT = "31DDDE24DDFAB679F42D7BD2BAA929FF1A7ECACE"
CACHE = Path.home() / ".cache/tanstfaafllm/mannie"
REMOTE_CACHE = ".cache/tanstfaafllm-mannie"
REMOTE_PROBE = ".local/share/tanstfaafllm/mannie/claude_probe.py"
REMOTE_SCRATCH = "mannie-scratch"
CLAUDE = "$HOME/.local/bin/claude"
PROBE = f"python3 $HOME/{REMOTE_PROBE}"
EVIDENCE = REPO / "results/mannie/luna-pi-claude" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
# Anything that looks like a credential must never reach results/.
SECRET = re.compile(r"sk-ant-[A-Za-z0-9_-]{8,}|\"(accessToken|refreshToken)\"\s*:|CLAUDE_CODE_OAUTH_TOKEN=\S")


def _ssh(command: str, stdin: bytes | None = None, timeout: float = 120) -> subprocess.CompletedProcess[bytes]:
    (Path.home() / ".ssh/cm").mkdir(mode=0o700, exist_ok=True)
    return subprocess.run(["ssh", *SSH_MUX, HOST, command], input=stdin, capture_output=True, timeout=timeout)


def _save(name: str, text: str) -> str:
    if SECRET.search(text):
        pytest.fail(f"{name}: output contains a credential-like string; nothing was saved")
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    (EVIDENCE / name).write_text(text, encoding="utf-8")
    return text


def _save_run(name: str, result: subprocess.CompletedProcess[bytes]) -> str:
    text = result.stdout.decode("utf-8", "replace")
    _save(name, f"exit status: {result.returncode}\n--- stdout\n{text}--- stderr\n{result.stderr.decode('utf-8', 'replace')}")
    return text


def _probe(name: str, args: str, timeout: float = 300) -> dict:
    result = _ssh(f"cd $HOME/{REMOTE_SCRATCH} && {PROBE} {args}", timeout=timeout)
    _save_run(name, result)
    assert result.returncode == 0, result.stderr.decode("utf-8", "replace")
    return json.loads(result.stdout)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _fetch(url: str, target: Path) -> Path:
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        partial = target.with_suffix(target.suffix + ".part")
        with urllib.request.urlopen(url, timeout=120) as response, partial.open("wb") as handle:
            while block := response.read(1 << 20):
                handle.write(block)
        partial.rename(target)
    return target


def _verified_manifest() -> dict:
    """The release manifest, checked against Anthropic's signing key."""
    manifest = _fetch(f"{RELEASES}/{VERSION}/manifest.json", CACHE / VERSION / "manifest.json")
    signature = _fetch(f"{RELEASES}/{VERSION}/manifest.json.sig", CACHE / VERSION / "manifest.json.sig")
    key = _fetch(SIGNING_KEY, CACHE / "claude-code.asc")
    with tempfile.TemporaryDirectory() as home:
        env = {**os.environ, "GNUPGHOME": home}
        subprocess.run(["gpg", "--batch", "--import", str(key)], env=env, capture_output=True, check=True)
        listing = subprocess.run(["gpg", "--batch", "--with-colons", "--fingerprint"], env=env, capture_output=True, text=True, check=True)
        assert f"fpr:::::::::{FINGERPRINT}:" in listing.stdout, "the signing key's fingerprint is not the published one"
        verify = subprocess.run(["gpg", "--batch", "--verify", str(signature), str(manifest)], env=env, capture_output=True, text=True)
    _save("manifest-verify.txt", verify.stderr)
    assert verify.returncode == 0 and "Good signature" in verify.stderr
    return json.loads(manifest.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def remote_ready() -> None:
    probe = (Path(__file__).with_name("claude_probe.py")).read_bytes()
    result = _ssh(
        f"mkdir -p $HOME/{Path(REMOTE_PROBE).parent} $HOME/{REMOTE_SCRATCH} && cat > $HOME/{REMOTE_PROBE}", stdin=probe
    )
    assert result.returncode == 0, result.stderr


@pytest.mark.timeout(120)
def test_preflight() -> None:
    result = _ssh(
        "uname -a; echo; . /etc/os-release; echo \"$PRETTY_NAME\"; ldd --version 2>&1 | head -1; echo; "
        "grep -E 'MemTotal|MemAvailable|SwapTotal' /proc/meminfo; echo; df -k $HOME | tail -1; echo; nproc; cat /proc/loadavg; echo; "
        f"ls -la {CLAUDE} $HOME/.local/share/claude/versions 2>&1; ls -la $HOME/.claude 2>&1 | head -20; command -v python3"
    )
    text = _save_run("preflight.txt", result)
    assert result.returncode in (0, 2)  # ls of a missing install exits 2
    assert "aarch64" in text
    glibc = re.search(r"GLIBC[^\n]*?(\d+)\.(\d+)\s*$", text, re.MULTILINE)
    assert glibc and (int(glibc.group(1)), int(glibc.group(2))) >= (2, 26)
    free_kib = int([line for line in text.splitlines() if line.startswith("/dev/")][-1].split()[3])
    assert free_kib > 512 * 1024


@pytest.mark.timeout(900)
def test_install(remote_ready: None) -> None:
    manifest = _verified_manifest()
    expected = manifest["platforms"][PLATFORM]["checksum"]
    binary = _fetch(f"{RELEASES}/{VERSION}/{PLATFORM}/claude", CACHE / VERSION / f"claude-{PLATFORM}")
    assert _sha256(binary) == expected, "downloaded binary does not match the signed manifest"

    remote_binary = f"{REMOTE_CACHE}/claude-{VERSION}-{PLATFORM}"
    assert _ssh(f"mkdir -p $HOME/{REMOTE_CACHE}").returncode == 0
    copy = subprocess.run(["scp", "-q", *SSH_MUX, str(binary), f"{HOST}:{remote_binary}"], capture_output=True, timeout=600)
    assert copy.returncode == 0, copy.stderr
    remote_sum = _ssh(f"chmod +x $HOME/{remote_binary} && sha256sum $HOME/{remote_binary}").stdout.decode().split()[0]
    assert remote_sum == expected, "binary changed on its way to luna-pi"

    # Pin the measured version: background updates off, merged into any existing settings.
    settings = (
        "import json,pathlib; p=pathlib.Path.home()/'.claude/settings.json'; p.parent.mkdir(exist_ok=True); "
        "s=json.loads(p.read_text()) if p.exists() else {}; s.setdefault('env',{})['DISABLE_AUTOUPDATER']='1'; "
        "p.write_text(json.dumps(s,indent=2)+'\\n'); print(p.read_text())"
    )
    _save_run("settings.txt", _ssh(f'python3 -c "{settings}"'))

    install = _probe("install.json", f"time $HOME/{remote_binary} install {VERSION}", timeout=600)
    assert install["exit_status"] == 0, install["stderr"]
    _ssh(f"rm -f $HOME/{remote_binary}")

    after = _ssh(
        f"{CLAUDE} --version; readlink -f {CLAUDE}; sha256sum $HOME/.local/share/claude/versions/{VERSION}; "
        "du -sk $HOME/.local/share/claude $HOME/.claude; ls -la $HOME/.local/share/claude/versions"
    )
    text = _save_run("installed.txt", after)
    assert after.returncode == 0
    assert text.startswith(f"{VERSION} (Claude Code)")
    assert expected in text


@pytest.mark.timeout(300)
def test_cli_start(remote_ready: None) -> None:
    runs = {}
    for flag in ("--version", "--help"):
        runs[flag] = [_probe(f"start{flag}-{n}.json", f"time {CLAUDE} {flag}") for n in (1, 2, 3)]
        assert all(run["exit_status"] == 0 for run in runs[flag])
    summary = {
        flag: {key: [run[key] for run in result] for key in ("wall_s", "user_s", "sys_s", "max_rss_kib")}
        for flag, result in runs.items()
    }
    _save("start-summary.json", json.dumps(summary, indent=2) + "\n")
    _save_run("doctor.txt", _ssh(f"cd $HOME/{REMOTE_SCRATCH} && timeout 60 {CLAUDE} doctor < /dev/null", timeout=90))


def _logged_in() -> bool:
    mode = _ssh("stat -c %a $HOME/.claude/.credentials.json 2>/dev/null").stdout.decode().strip()
    if mode:
        assert mode == "600", f"credential file mode is {mode}, expected 600"
    return bool(mode)


@pytest.mark.timeout(180)
def test_interactive_start(remote_ready: None) -> None:
    logged_in = _logged_in()
    result = _probe(f"interactive-{'logged-in' if logged_in else 'no-login'}.json", f"pty 20 {CLAUDE}", timeout=120)
    result["logged_in"] = logged_in
    _save("interactive-summary.json", json.dumps({k: v for k, v in result.items() if k != "samples"}, indent=2) + "\n")
    assert result["first_output_s"] is not None, "Claude Code printed nothing in 20 s"


@pytest.mark.timeout(240)
def test_one_request(remote_ready: None) -> None:
    if not _logged_in():
        pytest.skip("the user has not run /login on luna-pi yet")
    prompt = "Reply with the single word: pong"
    run = _probe("request.json", f"time {CLAUDE} -p '{prompt}' --output-format json", timeout=180)
    assert run["exit_status"] == 0, run["stderr"]
    reply = json.loads(run["stdout"])
    assert "pong" in reply.get("result", "").lower()
    _save(
        "request-summary.json",
        json.dumps(
            {key: run[key] for key in ("wall_s", "user_s", "sys_s", "max_rss_kib")}
            | {key: reply.get(key) for key in ("duration_ms", "duration_api_ms", "num_turns", "usage", "modelUsage", "total_cost_usd")},
            indent=2,
        )
        + "\n",
    )
