"""Mike 4.6: the model's base speed without any harness (`raw_speed.feature`).

`llama-completion` alone reads a fixed ~1,050-token French Cluedo scene
(`cluedo_prompt.txt`; its final newline is written `\\n` and read with `-e`) and answers in a few tokens, greedy, 4 threads, with
weight repacking off (Mike's lean setting) and on (llama.cpp's default).

    uv run pytest test/mike/test_raw_speed.py -m integration -s        # desk host
    uv run pytest test/mike/test_raw_speed.py -m live -s               # Luna, under the brain lock
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

import mike_eval as ev
import mike_luna as ml
import mike_server as ms

PROMPT = Path(__file__).with_name("cluedo_prompt.txt")
SETTINGS = {
    "lean": ["--no-repack", "-b", "16", "-ub", "16"],
    "repack": [],
}
COMMON = ["-e", "-c", "2048", "-t", "4", "-n", "24", "--temp", "0", "-no-cnv", "--no-display-prompt", "--no-warmup"]
RUN_DIR = ev.REPO / "results/mike/raw-speed" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
TIMING = re.compile(r"(prompt eval|eval) time =\s+([\d.]+) ms /\s+(\d+) (tokens|runs)")
LOAD = re.compile(r"load time =\s+([\d.]+) ms")


def parse(output: str) -> dict:
    out = {}
    for kind, ms_, n, _ in TIMING.findall(output):
        key = "prompt" if kind == "prompt eval" else "gen"
        out[key] = {"ms": float(ms_), "tokens": int(n), "tokens_per_s": round(int(n) / float(ms_) * 1000, 2)}
    if m := LOAD.search(output):
        out["load_ms"] = float(m.group(1))
    return out


def _record(host: str, setting: str, output: str, answer: str, extra: dict) -> dict:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    (RUN_DIR / f"{host}.{setting}.log").write_text(output)
    row = {"host": host, "setting": setting, "answer": answer.strip(), **parse(output), **extra}
    with (RUN_DIR / "summary.jsonl").open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps(row, ensure_ascii=False))
    return row


@pytest.mark.integration
@pytest.mark.parametrize("setting", SETTINGS)
def test_raw_speed_desk(setting):
    binary = ms.TOOLS_ROOT / "llama/llama-b11429/llama-completion"
    model = Path("/data/michael/tanstaafllm/mike-assets") / ml.MODEL
    if not binary.is_file() or not model.is_file():
        pytest.skip("desk binary or model missing")
    done = subprocess.run([str(binary), "-m", str(model), "-f", str(PROMPT), *COMMON, *SETTINGS[setting]],
                          capture_output=True, text=True, timeout=600, cwd=binary.parent,
                          env={"LC_ALL": "C", "PATH": "/usr/bin:/bin"})
    row = _record("desk", setting, done.stdout + "\n" + done.stderr, done.stdout, {})
    assert "prompt" in row, done.stderr[-2000:]


@pytest.mark.live
@pytest.mark.timeout(1800)
@pytest.mark.parametrize("setting", SETTINGS)
def test_raw_speed_luna(setting):
    remote_prompt = f"{ml.REMOTE_DIR}/cluedo_prompt.txt"
    subprocess.run(["scp", *ml.SSH_MUX, "-q", str(PROMPT), f"{ml.USER}@{ml.HOST}:{remote_prompt}"], check=True,
                   timeout=60)
    before = ml.mem_available_kib()
    argv = [f"{ml.REMOTE_DIR}/llama-b11429/llama-completion", "-m", f"{ml.REMOTE_DIR}/{ml.MODEL}",
            "-f", remote_prompt, *COMMON, *SETTINGS[setting]]
    # The brain lock is held by the shell that then becomes the program (`exec`), and removed after.
    script = (f"set -C; echo \"mike $$\" > {ml.LOCK} || {{ echo LOCK-HELD; cat {ml.LOCK}; exit 3; }}; set +C; "
              f"cd {ml.REMOTE_DIR}/llama-b11429 && LC_ALL=C {' '.join(argv)} > {ml.REMOTE_DIR}/raw.out 2> {ml.REMOTE_DIR}/raw.err; "
              f"rc=$?; rm -f {ml.LOCK}; echo rc=$rc")
    done = ml.ssh(f"sh -c '{script}'", timeout=1500, check=False)
    assert "LOCK-HELD" not in done, done
    output = ml.ssh(f"cat {ml.REMOTE_DIR}/raw.out; echo; cat {ml.REMOTE_DIR}/raw.err", check=False)
    answer = ml.ssh(f"cat {ml.REMOTE_DIR}/raw.out", check=False)
    after = ml.mem_available_kib()
    row = _record("luna", setting, output, answer,
                  {"mem_available_mib": {"before": before // 1024, "after": after // 1024}, "rc": done.strip()})
    assert ml.ssh(f"cat {ml.LOCK} 2>/dev/null", check=False).strip() == "", "brain lock left behind"
    assert "prompt" in row, output[-2000:]
