# 11 · Mycroft, voice to text

> In the novel, MYCROFT is the secret phone number that lets the revolutionaries reach Mike from anywhere. Here, Mycroft is how your voice reaches Luna.

## In one sentence

Mycroft turns French speech into editable text, locally and with no network, and writes it into Wyoh's Slate, where you correct it before sending.

![Mycroft, from voice to the Slate](img/mycroft-dictation.svg)

## Where it lives

| Piece | Code | Runs on |
|---|---|---|
| Dictation provider `mycroft_dictate.py` | `worklines/mycroft/scripts/` | Luna (scripts in `/storage/.local/share/tanstfaafllm/mycroft/`, model in `/storage/.local/opt/mycroft/`) |
| Text console `mycroft_console.py` | same | desk host: speak, see the draft, edit it, accept it |
| Benchmarks and model tools | `benchmark_asr.py`, `preoptimise_model.py`; tests in `test/mycroft/` | desk host, `luna-pi`, Luna |

## How it talks to the others

- **Wyoh starts it, once.** When Luna's session starts, Wyoh's gamepad daemon launches the provider in **resident** mode, in the background. It loads Kroko once and waits with the microphone closed.
- **L2 dictates.** In the Slate, L2 starts and stops dictation; on the desktop, L2 opens the Slate straight into dictation. The provider answers `start` with `listening` in 0.002 s.
- **Lines on its output:** `ready` once loaded, then for each dictation `listening`, `partial` drafts while you speak, and a `final` text; or an `error`. These are JSON lines on standard output.
- **The Slate owns the text.** Drafts are underlined, and the final text, with capitals and punctuation, is inserted at the cursor. Nothing is sent until you press FN+A. The contract is in [`worklines/mycroft/docs/0704_01`](../worklines/mycroft/docs/0704_01_dictation-provider.md), and resident mode in [`0903_03`](../worklines/mycroft/docs/0903_03_note-from-wyoh-kroko-resident-in-slate.md).
- **Known words** (names such as Wyoh, Luna or Michael) worked on the old model, on a synthetic voice. They are not set up for Kroko yet: that is proposed step 9.10.

## What it costs

On Luna, Kroko prepared once for ARM, 2 threads, resident:

| Measure | Value |
|---|---|
| Load, once per session, in the background | 24.4 s (47.7 s with the files as published) |
| Memory | 152 MiB at rest, 172 MiB while dictating |
| Speed | RTF 0.78: it keeps up with speech |
| From L2 to listening | 0.002 s |
| From the end of speech to the final text | ≈ 1.2 s, of which 1.0 s is silence fed so that Kroko keeps the last word |
| Memory left with the desktop running | ≈ 520 MiB available of 983 MiB |

![Every model and how far it got](img/mycroft-model-journey.svg)

## Why it is like this

- **Kroko, after eight others.** Nine models were considered; the full comparison is in [06 · The speech-to-text story](06_speech-to-text-story.md). Kroko has about 18 M parameters, a quarter of the first model (Sherpa's French Zipformer). It made fewer errors on the user's reading (9 % against 13 %), uses about half the CPU and 70 MiB less, and writes capitals and punctuation. It is the only model measured that keeps up with speech on Luna.
- **Resident, because loading is long.** Kroko takes 24 s to load on Luna. The user ruled out any wait after pressing the button, so it loads once per session and stays in memory.
- **Prepared once for ARM.** Saving the model once with ONNX Runtime's "extended" optimisation, on aarch64, halves the load (47.7 s to 24.4 s) with identical text.
- **Two threads, not four.** On Luna's Cortex-A35 cores, four threads decode more slowly than one. Two is the best setting.
- **Python stays.** Sherpa's own C++ binary saved only about 15 MiB and was no faster. The heavy work is compiled code in both cases.
- **GPU later.** Luna's Mali exposes OpenCL. It is parked while the CPU is enough.

## Status and limits

- **Done:**
  - Kroko is resident on Luna and wired into the Slate (Wyoh step 12.4). The user's voice tests with the USB-C headset worked.
  - The memory check on Luna's Arch Linux ARM root passed; the user's verdict: "it will hold".
- **Open:**
  - Kroko's licence: Banafo states CC-BY-SA, but no licence text ships with the weights. Fine for private use; to settle before Kroko goes into a Luna image others download.
  - Making Kroko the code's default (step 8.7, waiting for a go).
  - Proposed: draft text for Mike while you speak (9.9), and known words for Kroko (9.10).
  - The "re-format" action (punctuation on demand) is not designed yet.

**Sources:** `worklines/mycroft/plan_mycroft.md`, Steps 4, 7, 8 and 9; results `0104_04`, `0703_01`, `0802_01`, `0808_01`, `0901_01`, `0903_01`, `0903_02` and `0908_01`; contract `0704_01`.
