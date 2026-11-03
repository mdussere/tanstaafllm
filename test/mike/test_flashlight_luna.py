"""Mike Step 14.4: the flashlight on Luna, warm (`flashlight_luna.feature`).

    uv run pytest test/mike/test_flashlight_luna.py -m live -s

Only in a slot agreed with Mannie on Luna (Professor arranges it). Over SSH as michael:

1. a venv under ~/.local/opt/mike-embed with `model2vec` (the desk's version) and
   its dependencies from PyPI; nothing system-wide;
2. the bench, the guide pages it cuts into blocks, the data, and POTION-4M's
   files from the desk's Hugging Face cache, copied under
   ~/.local/share/tanstfaafllm/mike/flashlight/ (no download on Luna);
3. `flashlight_bench.py` for BM25, POTION-4M and their fusion, each in its own
   process, exactly as on the desk.

Evidence in results/mike/flashlight-luna/<timestamp>/: each candidate's JSON line,
`pip freeze`, Python and memory before and after.
"""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pytest

import flashlight_blocks as fb
import mike_eval as ev
import mike_luna as ml

STAMP = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
RUN_DIR = ev.REPO / "results/mike/flashlight-luna" / STAMP
VENV = "/home/michael/.local/opt/mike-embed"
BASE = "/home/michael/.local/share/tanstfaafllm/mike/flashlight"
MODEL2VEC = "model2vec==0.10.0"  # as in uv.lock
CANDIDATES = ["bm25", "minishlab/potion-base-4M", "rrf"]
FILES = ["test/mike/flashlight_bench.py", "test/mike/flashlight_blocks.py", "test/mike/flashlight_data.json",
         *fb.GUIDE]
HF_CACHE = Path.home() / ".cache/huggingface/hub/models--minishlab--potion-base-4M"


def push_tar(local_root: Path, names: list[str], remote_root: str) -> None:
    """Copy files with their relative paths, through tar over SSH."""
    ml.ssh(f"mkdir -p {remote_root}")
    tar = subprocess.Popen(["tar", "-C", str(local_root), "-cf", "-", *names], stdout=subprocess.PIPE)
    done = subprocess.run(["ssh", *ml.SSH_MUX, "-l", ml.USER, ml.HOST, f"tar -C {remote_root} -xf -"],
                          stdin=tar.stdout, capture_output=True, timeout=300)
    tar.wait()
    assert tar.returncode == 0 and done.returncode == 0, done.stderr


@pytest.mark.live
@pytest.mark.timeout(3600)
def test_flashlight_on_luna():
    assert HF_CACHE.is_dir(), "run the desk study first: POTION-4M must be in the desk's Hugging Face cache"
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    before = ml.ssh("python3 --version; uname -m; nproc; free -m; cat /tmp/luna-brain.lock 2>/dev/null; true")
    (RUN_DIR / "luna-before.txt").write_text(before)
    ml.ssh(f"test -x {VENV}/bin/python || python3 -m venv {VENV}", timeout=300)
    pip = ml.ssh(f"{VENV}/bin/python -m pip install --disable-pip-version-check -q '{MODEL2VEC}' 2>&1; "
                 f"{VENV}/bin/python -m pip freeze", timeout=1800)
    (RUN_DIR / "pip.txt").write_text(pip)
    push_tar(ev.REPO, FILES, BASE)
    push_tar(HF_CACHE.parent, [HF_CACHE.name], f"{BASE}/hf/hub")
    rows = []
    for name in CANDIDATES:
        out = ml.ssh(f"cd {BASE} && HF_HOME={BASE}/hf HF_HUB_OFFLINE=1 HF_HUB_DISABLE_PROGRESS_BARS=1 "
                     f"{VENV}/bin/python test/mike/flashlight_bench.py {name} 2>{BASE}/{name.replace('/', '_')}.err",
                     timeout=900)
        rows.append(json.loads(out.splitlines()[-1]) | {"host": "luna"})
    (RUN_DIR / "candidates.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    (RUN_DIR / "luna-after.txt").write_text(ml.ssh("free -m; cat /tmp/luna-brain.lock 2>/dev/null; true"))
    print(RUN_DIR)
    for r in rows:
        print(r["candidate"], r["rss_loaded_mib"], r["load_s"], r["ms_short_sentence"], r["ms_100_words"],
              r["retrieval"]["top3"], r["routing_with_anchors"]["accuracy"])
    assert len(rows) == len(CANDIDATES)
