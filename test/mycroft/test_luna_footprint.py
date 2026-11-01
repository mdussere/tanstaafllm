"""Mycroft on Luna: Step 8 measurements (`luna_footprint.feature`).

Live only: needs MYCROFT_LUNA_LIVE=1, MYCROFT_ASSET_ROOT, and a slot arranged
through Professor (`worklines/luna-access.md`). MYCROFT_TARGET selects the
machine: "luna" (default; files under /storage/.local) or "luna-pi" (the
Raspberry Pi 4 reference, files under the user's ~/.local). No package is
installed. MYCROFT_LUNA_REBOOT=1 reboots the target before and after a
measurement, as the user asked for Luna (it avoids SSH stalls); it is not used
on luna-pi, where the user keeps an interactive session.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import tarfile
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest


LIVE = os.environ.get("MYCROFT_LUNA_LIVE") == "1"
pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(not LIVE, reason="set MYCROFT_LUNA_LIVE=1 once Professor has given a Luna slot"),
]

REPO = Path(__file__).parents[2]
TARGET = os.environ.get("MYCROFT_TARGET", "luna")
HOST = TARGET
BASE = {"luna": "/storage", "luna-pi": "/home/michael"}[TARGET]
# Luna's OpenSSH penalises bursts of new connections: reuse one (as Wyoh's tests do).
SSH_MUX = ["-o", "ControlMaster=auto", "-o", f"ControlPath={Path.home()}/.ssh/cm/%r@%h:%p", "-o", "ControlPersist=15m"]
REMOTE_OPT = f"{BASE}/.local/opt/mycroft"
REMOTE_SHARE = f"{BASE}/.local/share/tanstfaafllm/mycroft"
RUNTIME = "sherpa-onnx-v1.13.8-linux-aarch64-shared-cpu-lib"
MODEL = "sherpa-onnx-streaming-zipformer-fr-2023-04-14"
INT8 = "epoch-29-avg-9-with-averaged-model.int8.onnx"
WAV = "common_voice_fr_19364697.wav"
WAV_SECONDS = 7.128
EVIDENCE = REPO / f"results/mycroft/{TARGET}-footprint" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _bundle() -> dict[str, Path]:
    """Remote absolute path → local file."""
    root = Path(os.environ["MYCROFT_ASSET_ROOT"])
    files = {
        f"{REMOTE_OPT}/{RUNTIME}/lib/{name}": root / RUNTIME / "lib" / name
        for name in ("libsherpa-onnx-c-api.so", "libonnxruntime.so")
    }
    for part in ("encoder", "decoder", "joiner"):
        files[f"{REMOTE_OPT}/{MODEL}/{part}-{INT8}"] = root / MODEL / f"{part}-{INT8}"
    files[f"{REMOTE_OPT}/{MODEL}/tokens.txt"] = root / MODEL / "tokens.txt"
    files[f"{REMOTE_OPT}/{MODEL}/test_wavs/{WAV}"] = root / MODEL / "test_wavs" / WAV
    scripts = REPO / "worklines/mycroft/scripts"
    files[f"{REMOTE_SHARE}/mycroft_console.py"] = scripts / "mycroft_console.py"
    files[f"{REMOTE_SHARE}/mycroft_dictate.py"] = scripts / "mycroft_dictate.py"
    files[f"{REMOTE_SHARE}/luna_footprint_probe.py"] = Path(__file__).with_name("luna_footprint_probe.py")
    return files


def _ssh(command: str, stdin: bytes | None = None, timeout: float = 120) -> subprocess.CompletedProcess[bytes]:
    (Path.home() / ".ssh/cm").mkdir(mode=0o700, exist_ok=True)
    return subprocess.run(["ssh", *SSH_MUX, HOST, command], input=stdin, capture_output=True, timeout=timeout)


def _save(name: str, result: subprocess.CompletedProcess[bytes]) -> str:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    text = result.stdout.decode("utf-8", "replace")
    (EVIDENCE / name).write_text(
        f"exit status: {result.returncode}\n--- stdout\n{text}--- stderr\n{result.stderr.decode('utf-8', 'replace')}",
        encoding="utf-8",
    )
    return text


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _reboot_and_settle() -> None:
    _ssh("reboot", timeout=30)  # the connection may drop before a status returns
    subprocess.run(["ssh", *SSH_MUX, "-O", "exit", HOST], capture_output=True)
    time.sleep(20)  # let the old sshd go away before the first probe
    deadline = time.monotonic() + 300
    while time.monotonic() < deadline:
        try:
            if _ssh("true", timeout=15).returncode == 0:
                break
        except subprocess.TimeoutExpired:  # Luna still booting: the TCP connect hangs
            subprocess.run(["ssh", *SSH_MUX, "-O", "exit", HOST], capture_output=True)
        time.sleep(5)
    else:
        pytest.fail("Luna did not answer SSH within 300 s of the reboot")
    while time.monotonic() < deadline:  # wait for boot-time work to finish
        load = float(_ssh("cut -d' ' -f1 /proc/loadavg").stdout.split()[0])
        if load < 0.5:
            return
        time.sleep(10)
    pytest.fail("Luna's load did not settle below 0.5 after the reboot")


@pytest.mark.timeout(120)
def test_luna_preflight() -> None:
    result = _ssh(
        "uname -a; echo; command -v python3 && python3 --version; echo; "
        "(ldd --version 2>&1 | head -1); echo; "
        "for f in /usr/lib/libstdc++.so.6 /lib/libstdc++.so.6 /usr/lib64/libstdc++.so.6; do "
        "  [ -e $f ] && echo $f && grep -ao 'GLIBCXX_3\\.4\\.[0-9]*' $f | sort -uV | tail -1; done; echo; "
        "grep -E 'MemTotal|MemAvailable' /proc/meminfo; echo; df -k /storage; echo; nproc; cat /proc/loadavg"
    )
    text = _save("preflight.txt", result)
    assert result.returncode == 0
    assert "aarch64" in text
    assert "Python 3" in text
    storage_line = [line for line in text.splitlines() if line.rstrip().endswith("/storage")][-1]
    free_kib = int(storage_line.split()[3])  # df -k: filesystem, size, used, available, …
    assert free_kib > 300 * 1024, "/storage needs room for the ~165 MB bundle"


def _install(files: dict[str, Path], name: str) -> list[str]:
    """Stream files whose SHA-256 differs on Luna, then verify them all."""
    manifest = {remote: _sha256(local) for remote, local in files.items()}
    check = "".join(f"{digest}  {remote}\n" for remote, digest in manifest.items())
    current = _ssh("sha256sum -c - 2>/dev/null; true", stdin=check.encode())
    matching = {line.rsplit(":", 1)[0] for line in current.stdout.decode().splitlines() if line.endswith(": OK")}
    missing = [remote for remote in files if remote not in matching]

    if missing:
        payload = io.BytesIO()
        with tarfile.open(fileobj=payload, mode="w") as archive:
            for remote in missing:
                archive.add(files[remote], arcname=remote.lstrip("/"))
        upload = _ssh("tar -xf - -C /", stdin=payload.getvalue(), timeout=3500)
        _save(f"{name}-upload.txt", upload)
        assert upload.returncode == 0

    verified = _ssh("sha256sum -c -", stdin=check.encode())
    _save(f"{name}-verify.txt", verified)
    (EVIDENCE / f"{name}.json").write_text(
        json.dumps({"uploaded": missing, "sha256": manifest, "bytes": {r: files[r].stat().st_size for r in files}}, indent=2) + "\n",
        encoding="utf-8",
    )
    assert verified.returncode == 0
    return missing


@pytest.mark.timeout(3600)
def test_luna_install_bundle() -> None:
    _install(_bundle(), "install")


@pytest.mark.timeout(1800)
def test_luna_footprint_replay() -> None:
    reboot = os.environ.get("MYCROFT_LUNA_REBOOT") == "1"
    if reboot:
        _reboot_and_settle()
    before = _save("before.txt", _ssh("uptime; grep -E 'MemTotal|MemAvailable' /proc/meminfo; ps -eo rss,comm --sort=-rss | head -15"))
    assert "MemAvailable" in before
    probe = _ssh(
        f"cd {REMOTE_SHARE} && python3 luna_footprint_probe.py --runs 3 --audio-seconds {WAV_SECONDS} -- "
        f"python3 mycroft_dictate.py --assets {REMOTE_OPT} --input {REMOTE_OPT}/{MODEL}/test_wavs/{WAV}",
        timeout=1500,
    )
    report_text = _save("probe.txt", probe)
    try:
        report = json.loads(report_text)
        (EVIDENCE / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    finally:
        if reboot:
            _reboot_and_settle()  # hand Luna back in a clean state
    assert probe.returncode == 0, report_text
    for run in report["runs"]:
        assert run["exit_status"] == 0
        assert run["final_text"].strip()


# --- Steps 8.2-8.4 and 8.6: threads, load time, compiled binary, resident provider ---

VARIANT_ROOT = f"{BASE}/.local/opt/mycroft-onnx-extended"
FULL_RUNTIME = "sherpa-onnx-v1.13.8-linux-aarch64-shared-cpu"  # same libraries, plus Sherpa's binaries
CPP_BINARY = f"{REMOTE_OPT}/{RUNTIME}/bin/sherpa-onnx"  # its RPATH finds ../lib
REMOTE_WAV = f"{REMOTE_OPT}/{MODEL}/test_wavs/{WAV}"


def _bundle_series2() -> dict[str, Path]:
    root = Path(os.environ["MYCROFT_ASSET_ROOT"])
    variants = Path(os.environ.get("MYCROFT_VARIANTS_ROOT", "/data/michael/tanstaafllm/mycroft-variants"))
    files = {CPP_BINARY: root / FULL_RUNTIME / "bin" / "sherpa-onnx"}
    for part in ("encoder", "decoder", "joiner"):
        files[f"{VARIANT_ROOT}/{MODEL}/{part}-{INT8}"] = variants / "onnx-extended" / MODEL / f"{part}-{INT8}"
    files[f"{VARIANT_ROOT}/{MODEL}/tokens.txt"] = root / MODEL / "tokens.txt"
    scripts = REPO / "worklines/mycroft/scripts"
    for name in ("mycroft_console.py", "mycroft_dictate.py"):
        files[f"{REMOTE_SHARE}/{name}"] = scripts / name
    for name in ("luna_footprint_probe.py", "sherpa_load_profile.py", "resident_probe.py"):
        files[f"{REMOTE_SHARE}/{name}"] = Path(__file__).with_name(name)
    return files


def _json_lines(name: str, command: str, timeout: float = 900) -> object:
    result = _ssh(command, timeout=timeout)
    text = _save(f"{name}.txt", result)
    assert result.returncode == 0, text[-2000:]
    return json.loads(text)


@pytest.mark.timeout(3600)
def test_luna_install_for_8_2_to_8_6() -> None:
    _install(_bundle_series2(), "install-series2")
    link = _ssh(f"ln -sfn {REMOTE_OPT}/{RUNTIME} {VARIANT_ROOT}/{RUNTIME} && ls -l {VARIANT_ROOT}")
    _save("install-series2-link.txt", link)
    assert link.returncode == 0


@pytest.mark.timeout(3600)
def test_luna_8_2_to_8_4_threads_load_compiled() -> None:
    """Steps 8.2-8.4: threads 1/2/4, load breakdown and pre-optimised model, C++ binary."""
    reboot = os.environ.get("MYCROFT_LUNA_REBOOT") == "1"
    if reboot:
        _reboot_and_settle()
    profile = f"cd {REMOTE_SHARE} && python3 sherpa_load_profile.py --scripts {REMOTE_SHARE} --wav {REMOTE_WAV}"
    cpp = (f"cd {REMOTE_SHARE} && python3 luna_footprint_probe.py --raw --runs 2 -- {CPP_BINARY} "
           f"--tokens={REMOTE_OPT}/{MODEL}/tokens.txt --encoder={REMOTE_OPT}/{MODEL}/encoder-{INT8} "
           f"--decoder={REMOTE_OPT}/{MODEL}/decoder-{INT8} --joiner={REMOTE_OPT}/{MODEL}/joiner-{INT8} --provider=cpu")
    results: dict[str, object] = {}
    try:
        # The page cache is dropped once (a runtime action, not a configuration change) to time a cold read.
        results["python_cold_t1"] = _json_lines(
            "python-cold-t1", f"sync && echo 3 > /proc/sys/vm/drop_caches && {profile} --assets {REMOTE_OPT} --threads 1")
        for threads in (1, 2, 4):
            for run in (1, 2):
                results[f"python_t{threads}_run{run}"] = _json_lines(
                    f"python-t{threads}-run{run}", f"{profile} --assets {REMOTE_OPT} --threads {threads}")
        for threads in (1, 2, 4):
            results[f"cpp_t{threads}"] = _json_lines(f"cpp-t{threads}", f"{cpp} --num-threads={threads} {REMOTE_WAV}")
        for threads in (2, 4):
            results[f"dictate_paced_t{threads}"] = _json_lines(
                f"dictate-paced-t{threads}",
                f"cd {REMOTE_SHARE} && python3 luna_footprint_probe.py --runs 2 --audio-seconds {WAV_SECONDS} -- "
                f"python3 mycroft_dictate.py --assets {REMOTE_OPT} --threads {threads} --input {REMOTE_WAV}")
        for run in (1, 2):
            results[f"extended_t1_run{run}"] = _json_lines(
                f"extended-t1-run{run}", f"{profile} --assets {VARIANT_ROOT} --threads 1")
    finally:
        (EVIDENCE / "steps-8-2-to-8-4.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if reboot:
            _reboot_and_settle()


@pytest.mark.timeout(1800)
def test_luna_8_6_resident_and_swap() -> None:
    """Step 8.6: resident provider under memory pressure; swap/zram support, read-only."""
    reboot = os.environ.get("MYCROFT_LUNA_REBOOT") == "1"
    if reboot:
        _reboot_and_settle()
    try:
        swap = _ssh(
            "cat /proc/swaps; echo; ls /sys/block; echo; "
            "(zcat /proc/config.gz 2>/dev/null | grep -E 'CONFIG_(ZRAM|ZSWAP|SWAP|ZSMALLOC|CRYPTO_LZ4|CRYPTO_ZSTD)[_=]') ; echo; "
            "find /lib/modules/$(uname -r) -name 'zram*' 2>/dev/null; echo; "
            "cat /sys/module/zswap/parameters/enabled 2>/dev/null; command -v zramctl mkswap swapon"
        )
        _save("swap-zram-readonly.txt", swap)
        threads = int(os.environ.get("MYCROFT_RESIDENT_THREADS", "2"))
        report = _json_lines(
            "resident-pressure",
            f"cd {REMOTE_SHARE} && python3 resident_probe.py --scripts {REMOTE_SHARE} --assets {REMOTE_OPT} "
            f"--wav {REMOTE_WAV} --threads {threads} --floor-mib 150 --step-mib 32",
        )
        (EVIDENCE / "resident.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        assert report["decode_after_pressure"]["text"].strip()
    finally:
        if reboot:
            _reboot_and_settle()


# --- Step 9.3: the Kroko French model on Luna (C++ binary, public clips only) ---

KROKO = "sherpa-onnx-streaming-zipformer-fr-kroko-2025-08-06"
REMOTE_KROKO = f"{REMOTE_OPT}/{KROKO}"


def _bundle_kroko() -> dict[str, Path]:
    root = Path(os.environ["MYCROFT_ASSET_ROOT"]) / KROKO
    files = {f"{REMOTE_KROKO}/{name}": root / name for name in ("encoder.onnx", "decoder.onnx", "joiner.onnx", "tokens.txt")}
    files[f"{REMOTE_KROKO}/test_wavs/0.wav"] = root / "test_wavs" / "0.wav"
    return files


@pytest.mark.timeout(3600)
def test_luna_9_3_kroko() -> None:
    """Step 9.3: Kroko against the current model, same binary, clips and threads."""
    _install(_bundle_kroko(), "install-kroko")
    reboot = os.environ.get("MYCROFT_LUNA_REBOOT") == "1"
    if reboot:
        _reboot_and_settle()
    models = {
        "kroko": f"--tokens={REMOTE_KROKO}/tokens.txt --encoder={REMOTE_KROKO}/encoder.onnx "
                 f"--decoder={REMOTE_KROKO}/decoder.onnx --joiner={REMOTE_KROKO}/joiner.onnx",
        "current": f"--tokens={REMOTE_OPT}/{MODEL}/tokens.txt --encoder={REMOTE_OPT}/{MODEL}/encoder-{INT8} "
                   f"--decoder={REMOTE_OPT}/{MODEL}/decoder-{INT8} --joiner={REMOTE_OPT}/{MODEL}/joiner-{INT8}",
    }
    clips = {"cv": REMOTE_WAV, "kroko0": f"{REMOTE_KROKO}/test_wavs/0.wav"}
    results: dict[str, object] = {}
    try:
        for model, args in models.items():
            for threads in (1, 2):
                for clip, wav in clips.items():
                    if model == "current" and threads == 1 and TARGET == "luna":
                        continue  # measured on Luna in 8.1-8.4
                    results[f"{model}_t{threads}_{clip}"] = _json_lines(
                        f"kroko-{model}-t{threads}-{clip}",
                        f"cd {REMOTE_SHARE} && python3 luna_footprint_probe.py --raw --runs 2 -- {CPP_BINARY} {args} "
                        f"--provider=cpu --num-threads={threads} {wav}")
    finally:
        (EVIDENCE / "step-9-3-kroko.json").write_text(json.dumps(results, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if reboot:
            _reboot_and_settle()
    for run_set in results.values():
        assert all(run["exit_status"] == 0 for run in run_set["runs"])


# --- Step 9.8: the resident provider with the prepared Kroko, for the Slate ---

KROKO_PREPARED = "sherpa-onnx-streaming-zipformer-fr-kroko-2025-08-06-ort-extended"


def _bundle_resident_kroko() -> dict[str, Path]:
    root = Path(os.environ["MYCROFT_ASSET_ROOT"]) / KROKO_PREPARED
    files = {f"{REMOTE_OPT}/{KROKO_PREPARED}/{name}": root / name
             for name in ("encoder.onnx", "decoder.onnx", "joiner.onnx", "tokens.txt", "README.md")}
    scripts = REPO / "worklines/mycroft/scripts"
    for name in ("mycroft_console.py", "mycroft_dictate.py"):
        files[f"{REMOTE_SHARE}/{name}"] = scripts / name
    files[f"{REMOTE_SHARE}/luna_footprint_probe.py"] = Path(__file__).with_name("luna_footprint_probe.py")
    return files


@pytest.mark.timeout(3600)
def test_luna_9_8_resident_kroko() -> None:
    """Step 9.8: one load, three start/final cycles, prepared Kroko at 2 threads."""
    _install(_bundle_resident_kroko(), "install-resident-kroko")
    reboot = os.environ.get("MYCROFT_LUNA_REBOOT") == "1"
    if reboot:
        _reboot_and_settle()
    try:
        report = _json_lines(
            "resident-kroko",
            f"cd {REMOTE_SHARE} && python3 luna_footprint_probe.py --runs 1 --resident 3 --audio-seconds {WAV_SECONDS} -- "
            f"python3 mycroft_dictate.py --resident --model kroko-fr-2025 --threads 2 --assets {REMOTE_OPT} --input {REMOTE_WAV}",
            timeout=1200,
        )
        (EVIDENCE / "step-9-8-resident-kroko.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    finally:
        if reboot:
            _reboot_and_settle()
    run = report["runs"][0]
    assert run["exit_status"] == 0 and "error" not in run
    assert all(utterance["final_text"].strip() for utterance in run["utterances"])


@pytest.mark.timeout(1800)
def test_luna_8_8_slate_session() -> None:
    """Step 8.8: memory of the real Slate session (Wyoh's daemon and its resident
    Kroko) while the user dictates; no second model is loaded."""
    _install({f"{REMOTE_SHARE}/slate_session_probe.py": Path(__file__).with_name("slate_session_probe.py")},
             "install-slate-session-probe")
    reboot = os.environ.get("MYCROFT_LUNA_REBOOT") == "1"
    window = float(os.environ.get("MYCROFT_DICTATION_WINDOW", "180"))
    if reboot:
        _reboot_and_settle()
    try:
        print(f"\n>>> Luna: dictate in the Slate now (L2 to start and stop), for {window:.0f} s <<<", flush=True)
        result = _ssh(f"python3 {REMOTE_SHARE}/slate_session_probe.py --window {window}", timeout=window + 400)
        _save("slate-session.txt", result)
        report = json.loads(result.stdout.decode().strip().splitlines()[-1])
        (EVIDENCE / "step-8-8-slate-session.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    finally:
        if reboot:
            _reboot_and_settle()
    assert "error" not in report, report.get("error")
    assert report["provider_alive_at_end"]
    assert report["listening_samples"] > 0, "no dictation seen during the window"
