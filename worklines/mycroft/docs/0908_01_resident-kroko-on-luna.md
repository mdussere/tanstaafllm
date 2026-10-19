# Resident Kroko on Luna (plan step 9.8)

**Date:** 2026-10-13
**Asked by:** Wyoh's note [`0903_03`](0903_03_note-from-wyoh-kroko-resident-in-slate.md), carrying the user's decisions (Kroko for the Slate, kept loaded while the Slate is hidden).
**Luna slot:** Professor (session tanstfaafllm-96), 2026-10-13 22:41. Luna was rebooted before and after the series.
**Harness:** `test/mycroft/test_luna_footprint.py::test_luna_9_8_resident_kroko` (contract in `luna_footprint.feature`). Evidence: `results/mycroft/luna-footprint/20261013T204205Z/step-9-8-resident-kroko.json`.

## What is installed on Luna

| Path | Content |
| --- | --- |
| `/storage/.local/opt/mycroft/sherpa-onnx-streaming-zipformer-fr-kroko-2025-08-06-ort-extended/` | Kroko prepared once at ONNX Runtime's portable "extended" level (used by `--model kroko-fr-2025`) |
| `/storage/.local/opt/mycroft/sherpa-onnx-streaming-zipformer-fr-kroko-2025-08-06/` | Kroko as published. Its `encoder.onnx` is complete (70,092,599 bytes), so no partial file is left. It is kept for comparison and can be removed. |
| `/storage/.local/share/tanstfaafllm/mycroft/mycroft_dictate.py`, `mycroft_console.py` | The current scripts, with `--resident` and `--model`. SHA-256 is identical to the working tree. |

## Measurement

Command: `mycroft_dictate.py --resident --model kroko-fr-2025 --threads 2`, replaying a public 7.1 s Common Voice clip at real-time pace. The run was 3 utterances (`start`, the whole clip, `stop`) in one process, with one load.

| Measure | Luna |
| --- | --- |
| Load, process start → `ready` | **24.4 s** (published files, step 9.3: 47.7 s) |
| RSS idle after load | **151.5 MiB** |
| RSS while listening, and after the first utterance | 172.0 MiB |
| Peak RSS | **171.7 MiB** (current model at 2 threads: 236 MiB) |
| `start` → `listening` | **0.002–0.003 s** on each utterance |
| End of audio → `final` | 1.23–1.27 s, including the 1.0 s silence padding |
| Text, all 3 utterances | "Ce site contient quatre tombeaux de la dynastie, Acheménide et sept des soixante nids." (identical; last word kept) |
| Memory available before the run | 772.7 MiB |

**Reading:**
- The model now loads once per session, and each later utterance starts with no wait.
- Decoding keeps up with speech at 2 threads. Only ~0.25 s of work is left after the padding when the clip ends. Step 9.3 measured RTF 0.76–0.79 for the same files and threads.
- The first `partial` came 3.5 s after `start`, because that is when the clip's first words were decoded. That delay follows the audio, not a loading cost.
- RSS settles at ~172 MiB after the first utterance and stays there for as long as the session runs.

## Licence (unchanged)

Kroko's community models are stated CC-BY-SA by Banafo in two READMEs, but no licence text ships with the weights (the `LICENSE` file is empty). That is enough for personal evaluation. Before any redistribution, for example in a Luna image, the exact licence version must be found. Share-alike applies to the prepared files, because they are modified weights. See [`0903_01`](0903_01_lighter-candidates-desk-result.md).
