#!/usr/bin/env python3
"""Make pre-optimised variants of Mycroft's pinned model (plan step 8.3, experiment).

Run on the desk host with ONNX Runtime's Python package, which Luna doesn't
need:

    uv run --no-project --with onnxruntime==1.28.0 --with onnx \\
        python worklines/mycroft/scripts/preoptimise_model.py --assets DIR --out DIR

For each variant it writes an asset root with the same layout as the
original: the model directory (the three int8 files replaced, tokens.txt
copied) and a symlink to each runtime directory. Pass that root as --assets to
the provider; no Mycroft code changes. Variants:

  onnx-extended  graph optimised once at the "extended" level and saved as
                 ONNX. It stays portable: the "all" level adds x86 layouts.
  ort-arm        ONNX Runtime's own ORT format, optimised for an ARM target,
                 stored under the original .onnx file names because Sherpa
                 opens fixed names. ONNX Runtime recognises the format from
                 the bytes, if this build accepts ORT format at all, which is
                 what the experiment checks.

The pinned runtime bundles ONNX Runtime 1.28.2; the 1.28.0 Python package is
the closest published release.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import onnxruntime as ort

MODEL_DIRNAME = "sherpa-onnx-streaming-zipformer-fr-2023-04-14"
PARTS = [f"{part}-epoch-29-avg-9-with-averaged-model.int8.onnx" for part in ("encoder", "decoder", "joiner")]


def _variant_root(out: Path, name: str, assets: Path) -> Path:
    root = out / name
    model = root / MODEL_DIRNAME
    model.mkdir(parents=True, exist_ok=True)
    shutil.copy2(assets / MODEL_DIRNAME / "tokens.txt", model / "tokens.txt")
    for runtime in assets.glob("sherpa-onnx-v*"):
        if runtime.is_dir() and not (root / runtime.name).exists():
            (root / runtime.name).symlink_to(runtime.resolve())
    return model


def onnx_extended(assets: Path, out: Path) -> None:
    model = _variant_root(out, "onnx-extended", assets)
    for part in PARTS:
        options = ort.SessionOptions()
        options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_EXTENDED
        options.optimized_model_filepath = str(model / part)
        ort.InferenceSession(str(assets / MODEL_DIRNAME / part), options, providers=["CPUExecutionProvider"])
        print(f"onnx-extended: {part} {(model / part).stat().st_size} bytes")


def ort_arm(assets: Path, out: Path) -> None:
    model = _variant_root(out, "ort-arm", assets)
    with tempfile.TemporaryDirectory() as scratch:
        work = Path(scratch)
        for part in PARTS:
            shutil.copy2(assets / MODEL_DIRNAME / part, work / part)
        subprocess.run(
            [sys.executable, "-m", "onnxruntime.tools.convert_onnx_models_to_ort", str(work),
             "--optimization_style", "Fixed", "--target_platform", "arm"],
            check=True,
        )
        for part in PARTS:
            converted = work / part.replace(".onnx", ".ort")
            shutil.copy2(converted, model / part)
            print(f"ort-arm: {part} {converted.stat().st_size} bytes")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    print(f"onnxruntime {ort.__version__}")
    onnx_extended(args.assets, args.out)
    ort_arm(args.assets, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
