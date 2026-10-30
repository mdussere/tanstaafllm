"""Mike Step 4.5: first supervised run on Luna (`luna_first_run.feature`).

Needs Luna free for Mike (Professor's go, Mannie on Luna stopped), SSH as
`michael`, and the release and model under MIKE_TOOLS_ROOT / MIKE_ASSET_ROOT.

    MIKE_ASSET_ROOT=/data/michael/tanstaafllm/mike-assets \
        uv run pytest test/mike/test_luna_first_run.py -m live -s

`MIKE_LUNA_THREADS` sets the thread count (default 4).
"""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

import mike_eval as ev
import mike_luna as ml
import mike_server as ms

# One request per tool from the held-out set: launch, focus, close, move, type, none.
PICK = {"holdout": [int(i) for i in os.environ.get("MIKE_LUNA_PICK", "0,8,13,17,22,28").split(",")]}
SETS = {"main": ev.EVAL_SET, "holdout": ev.HOLDOUT_SET}
THREADS = int(os.environ.get("MIKE_LUNA_THREADS", "4"))
RUN_DIR = ev.REPO / "results/mike/luna-first-run" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


@pytest.mark.live
@pytest.mark.timeout(3600)
def test_luna_first_run():
    root = os.environ.get("MIKE_ASSET_ROOT")
    model = Path(root or "") / ml.MODEL
    release = ms.TOOLS_ROOT / "dl-arm64" / ml.RELEASE
    if not model.is_file() or not release.is_file():
        pytest.skip("model or arm64 release missing")
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    with (RUN_DIR / "run.log").open("w") as log:
        log.write(ml.ssh("id; uname -a; nproc; free -m; cat /etc/os-release | head -3; "
                         "ls /tmp/luna-brain.lock 2>&1; ps -eo pid,rss,comm --sort=-rss | head -8"))
        installed = ml.install(release, model, log)
    timings: list[dict] = []
    servers: list[ml.LunaServer] = []

    def factory(extra, log_path):
        servers.append(ml.LunaServer(extra, log_path, threads=THREADS))
        return servers[-1]

    def on_request(case, answer):
        server = servers[-1]
        now = time.time()
        row = {"request": case.request, "end": now, "timings": answer.get("timings", {})}
        row["peak"] = ml.peak_between(server.samples, now - (answer.get("timings", {}).get("prompt_ms", 0)
                                                               + answer.get("timings", {}).get("predicted_ms", 0)) / 1000, now)
        timings.append(row)
        print(json.dumps({"request": case.request, "content": answer.get("content"), **row["timings"],
                          **row["peak"]}, ensure_ascii=False), flush=True)
        assert not server.stopped_for_memory, "MemAvailable fell below the floor"

    report = ms.run_server_eval(str(model), "lean-slot", SETS, RUN_DIR, server_factory=factory,
                                slot_dir=f"{ml.REMOTE_DIR}/slots", pick=PICK, on_request=on_request)
    server = servers[-1]
    report.update({"luna": {"threads": THREADS, "install": installed, "samples": server.samples,
                            "requests": timings, "stopped_for_memory": server.stopped_for_memory,
                            "lock_after": server.samples[-1].get("lock")}})
    ml.write_json(RUN_DIR / "report.json", report)
    mem = [s["mem_available_kib"] for s in server.samples if "mem_available_kib" in s]
    summary = {"threads": THREADS, "ready_s": report["ready_s"], "prefix": report["prefix"],
               "peak_rss_mib": round(report["status_end_kib"].get("VmHWM", 0) / 1024, 1),
               "rss_anon_mib": round(report["status_end_kib"].get("RssAnon", 0) / 1024, 1),
               "rss_file_mib": round(report["status_end_kib"].get("RssFile", 0) / 1024, 1),
               "mem_available_mib": {"before": round(mem[0] / 1024), "min": round(min(mem) / 1024),
                                     "after": round(mem[-1] / 1024)},
               "holdout": report["sets"]["holdout"]["summary"],  # only the picked cases
               "rows": [(r["request"], r["got"], r["adapter"], r.get("prompt_n"), r.get("prompt_ms"),
                         r.get("predicted_ms")) for r in report["sets"]["holdout"]["rows"]]}
    ml.write_json(RUN_DIR / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    assert server.samples[-1].get("lock") == "", "brain lock left behind"
