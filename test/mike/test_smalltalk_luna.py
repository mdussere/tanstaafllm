"""Mike Step 12.5: the small-talk client on Luna (`smalltalk_luna.feature`).

    uv run pytest test/mike/test_smalltalk_luna.py -m live -s

Only with Mannie on Luna stopped (`mannie stop --save`) and the brain lock
free: the client itself refuses to start otherwise. Over SSH as michael, the
client (`src/mike/smalltalk.py` with `prestac.py`, copied and checked by SHA-256) is fed
Step 12.1's questions on stdin, one run per setting, sharing one state
directory so that the third run finds layer L0 saved:

1. French, lean, cold (L0 read and saved);
2. English, lean, cold;
3. French, lean, warm (L0 restored);
4. French, repacked weights (to compare the writing speed on ARM).

Kroko, Sway and the Wyoh services are left running. The client's own log
(`chat.jsonl`: start time, tokens read, time to the first word and to the
last, server memory) and each server log are copied back.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

import mike_eval as ev
import mike_luna as ml
from test_chat_baseline import CONVERSATIONS

CLIENT = ev.REPO / "src/mike/smalltalk.py"
PRESTAC = ev.REPO / "src/mike/prestac.py"
STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
RUN_DIR = ev.REPO / "results/mike/smalltalk-luna" / STAMP
STATE = f"/home/michael/.local/state/mike-run-{STAMP}"
RUNS = [("1-fr-cold", "fr", ""), ("2-en-cold", "en", ""), ("3-fr-warm", "fr", ""), ("4-fr-repack", "fr", "MIKE_REPACK=1")]


def stdin_for(lang: str) -> str:
    """The questions of one language, a /new between conversations, then /quit."""
    blocks = ["\n".join(questions) for l, questions in CONVERSATIONS if l == lang]
    return "\n/new\n".join(blocks) + "\n/quit\n"


def test_stdin_for():
    text = stdin_for("en")
    assert text.count("/new") == 2 and text.endswith("/quit\n")


@pytest.mark.live
@pytest.mark.timeout(3600)
def test_smalltalk_on_luna():
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    lock = ml.ssh(f"cat {ml.LOCK} 2>/dev/null; true").strip()
    if lock:
        pid = lock.split()[-1]
        alive = ml.ssh(f"test -d /proc/{pid} && echo alive; true").strip()
        if alive:
            pytest.skip(f"Luna's brain lock is held: {lock}")
    for local in (CLIENT, PRESTAC):  # the client imports prestac.py from its own directory
        remote = f"{ml.REMOTE_DIR}/{local.name}"
        subprocess.run(["scp", "-o", "BatchMode=yes", "-o", f"ControlPath={Path.home()}/.ssh/cm/%r@%h:%p",
                        str(local), f"{ml.USER}@{ml.HOST}:{remote}"], check=True, timeout=60)
        assert ml.ssh(f"sha256sum {remote}").split()[0] == hashlib.sha256(local.read_bytes()).hexdigest()
    env = ml.ssh("uname -a; nproc; free -m; pgrep -a python3; pgrep -a sway | head -3")
    (RUN_DIR / "luna.txt").write_text(env)
    for name, lang, extra in RUNS:
        before = ml.mem_available_kib()
        out = ml.ssh(f"cd {ml.REMOTE_DIR} && XDG_STATE_HOME={STATE} {extra} python3 smalltalk.py --lang {lang} "
                     f"<<'EOF'\n{stdin_for(lang)}EOF\n", timeout=1800)
        (RUN_DIR / f"{name}.out").write_text(out)
        (RUN_DIR / f"{name}.server.log").write_text(ml.ssh(f"cat {STATE}/mike/llama-server.log"))
        (RUN_DIR / f"{name}.mem.json").write_text(json.dumps({"mem_available_kib_before": before}))
    log = ml.ssh(f"cat {STATE}/mike/chat.jsonl")
    (RUN_DIR / "chat.jsonl").write_text(log)
    assert not ml.ssh(f"cat {ml.LOCK} 2>/dev/null; true").strip(), "the client left the brain lock behind"
    records = [json.loads(line) for line in log.splitlines() if line.strip()]
    starts = [r for r in records if r.get("event") == "start"]
    turns = [r for r in records if "question" in r]
    summary = {"starts": starts, "turns": len(turns)}
    done = 0
    for name, lang, _ in RUNS:
        n = sum(len(q) for l, q in CONVERSATIONS if l == lang)
        mine, done = turns[done:done + n], done + n
        firsts, totals = sorted(r["first_s"] for r in mine), sorted(r["total_s"] for r in mine)
        rate = [r["predicted_n"] / (r["predicted_ms"] / 1000) for r in mine if r.get("predicted_ms")]
        summary[name] = {"first_s_median": firsts[len(firsts) // 2], "first_s_max": firsts[-1],
                         "total_s_median": totals[len(totals) // 2], "total_s_max": totals[-1],
                         "write_tokens_per_s_median": round(sorted(rate)[len(rate) // 2], 2),
                         "prompt_n_max": max(r["prompt_n"] for r in mine),
                         "rss_kib_max": max(r.get("VmHWM", 0) for r in mine)}
    (RUN_DIR / "summary.json").write_text(json.dumps(summary, indent=1))
    print(json.dumps(summary))
    assert len(turns) == sum(sum(len(q) for l, q in CONVERSATIONS if l == lang) for _, lang, _ in RUNS)
