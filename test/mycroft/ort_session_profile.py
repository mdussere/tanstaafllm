#!/usr/bin/env python3
"""Where does a model's load time go? (plan step 9.3, Kroko's slow load)

Runs on the measured machine with ONNX Runtime's Python package. For each
.onnx file given, it times creating an inference session (one thread):

  * at each graph-optimisation level (disabled, basic, extended, all);
  * then, once more, after saving the "all"-optimised graph made on this
    machine and reloading that file with optimisation disabled. This is the
    "prepare once" idea of note 0703_02, done on the target architecture.

Prints one JSON report.
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import tempfile
import time
from pathlib import Path

import onnxruntime as ort

LEVELS = {
    "disabled": ort.GraphOptimizationLevel.ORT_DISABLE_ALL,
    "basic": ort.GraphOptimizationLevel.ORT_ENABLE_BASIC,
    "extended": ort.GraphOptimizationLevel.ORT_ENABLE_EXTENDED,
    "all": ort.GraphOptimizationLevel.ORT_ENABLE_ALL,
}


def _session_seconds(model: str, level, save_to: str | None = None) -> float:
    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    options.graph_optimization_level = level
    if save_to:
        options.optimized_model_filepath = save_to
    started = time.monotonic()
    ort.InferenceSession(model, options, providers=["CPUExecutionProvider"])
    return round(time.monotonic() - started, 3)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("models", nargs="+")
    parser.add_argument("--save-extended", metavar="DIR",
                        help="also write each model, optimised here at the portable 'extended' level, into DIR")
    args = parser.parse_args()
    report: dict = {"machine": platform.machine(), "onnxruntime": ort.__version__, "models": {}}
    for model in args.models:
        times = {name: _session_seconds(model, level) for name, level in LEVELS.items()}
        with tempfile.TemporaryDirectory() as scratch:
            saved = str(Path(scratch) / "optimised.onnx")
            times["all_while_saving"] = _session_seconds(model, LEVELS["all"], saved)
            times["reload_saved_disabled"] = _session_seconds(saved, LEVELS["disabled"])
            times["saved_bytes"] = Path(saved).stat().st_size
        times["bytes"] = Path(model).stat().st_size
        report["models"][Path(model).name] = times
        if args.save_extended:
            Path(args.save_extended).mkdir(parents=True, exist_ok=True)
            times["extended_while_saving"] = _session_seconds(
                model, LEVELS["extended"], str(Path(args.save_extended) / Path(model).name))
    json.dump(report, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
