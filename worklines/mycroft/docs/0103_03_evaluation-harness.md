# Mycroft pre-hardware evaluation harness

**Status:** Step 3 complete, 2026-09-25.

## What is committed

| Artifact | Purpose |
| --- | --- |
| `scripts/benchmark_asr.py` | Standard-library runner: validates each WAV, invokes one native decoder process, samples `/proc` RSS, extracts an explicit transcript, calculates WER, and emits JSON Lines. |
| `scripts/fixtures/public-french-smoke.json` | Three upstream public French fixtures and their reference text. Audio remains external and is located through `MYCROFT_ASSET_ROOT`. |
| `scripts/candidates/*.json` | Pinned argument profiles. They invoke a native executable with no network access or ambient model discovery. |
| `scripts/README.md` | Contract and generic invocation format. |

The runner is neither a Mycroft daemon nor the Step 5 product CLI. It exists to make a disposable, same-input comparison possible before target hardware is available.

## Invocation used

```text
MYCROFT_ASSET_ROOT=/outside-repo/mycroft-assets \
timeout 120 python3 worklines/mycroft/scripts/benchmark_asr.py \
  --manifest worklines/mycroft/scripts/fixtures/public-french-smoke.json \
  --candidate worklines/mycroft/scripts/candidates/<candidate>.json \
  --results /outside-repo/results-<candidate>.jsonl
```

`MYCROFT_ASSET_ROOT` must contain assets installed beforehand. The harness deliberately does not fetch them. Logs and raw JSON Lines in this evaluation were kept under `/tmp/tanstfaafllm-mycroft/`, outside the repository.

## Machine-readable record

Each line contains:

- candidate ID and pinned version;
- host system and architecture;
- fixture ID, external path, duration, and sample rate;
- expanded native command, exit code, stdout, stderr, and parser result;
- raw transcript and reference;
- elapsed wall seconds, sampled peak RSS in KiB, RTF, and normalised WER;
- a harness error in place of a crash when one fixture cannot run.

RSS is sampled every 10 ms from Linux `/proc/<pid>/status`. It is useful screening evidence but can miss a very short allocation spike. It is not peak target RAM and must never be recast as proof that a 1-GiB Luna can host the process.

## Acceptance and limitations

The harness produced comparable resource-accounted results for both shortlisted native candidates and all three fixtures. It had one early parser-profile error (Sherpa's structured result is on stderr); that failure was retained in the temporary benchmark log, corrected by declaring the stream explicitly, and then rerun. No results were selected or silently discarded.

The test uses a four-core x86_64 Intel i5-4590 desktop, not ARM hardware. `whisper.cpp` was locally built from the pinned source for the comparison; the CMake build utility lived only under `/tmp` and is not a Mycroft runtime dependency. The Sherpa runtime was the official x64 CPU archive. Neither path validates RK3326, ARMv7, shared GPU memory, battery, thermals, or the eventual audio stack.
