# Mycroft v0 requirements and test protocol

**Status:** approved by the `go §1, §2, §3, §4` work order; frozen for this comparison on 2026-09-25.

## The thing being measured

Mycroft v0 is a deliberately narrow offline French ASR baseline:

```text
recorded WAV file -> one on-demand local process -> UTF-8 French text
```

It is speech-to-text, not text-to-speech. It has no prompt, hotword list, project vocabulary, intent extraction, command execution, network call, or resident process. Those omissions are test controls, not missing features accidentally hidden in a dependency.

## Input and output contract

| Aspect | v0 rule |
| --- | --- |
| Accepted input | A regular file containing a RIFF/WAVE, PCM signed 16-bit, mono stream. |
| Sample rate | 16 kHz fixtures are canonical. A backend may resample another rate only when it states that it did so; the harness does not silently convert inputs. |
| Stereo / other codecs | Reject clearly before inference. Conversion is an explicit caller responsibility for v0. |
| Language | French is fixed for the primary test. English or mixed technical words are test content, not automatic language selection. |
| Output | One UTF-8, plain-text transcript per input. No timestamps or confidence value are promised. Backend diagnostic output stays on stderr. |
| Normalisation for scoring | Lowercase; Unicode accents retained; punctuation and whitespace ignored. Raw text is retained beside the normalised score. |
| Failure | A missing asset, unreadable file, invalid WAV, unsupported format, or decoder error must yield non-zero status and a concise stderr explanation. It must not fabricate a transcript. |
| Retention | Fixtures are public/consented test inputs only. The harness writes results, not audio copies. Personal recordings are never required or retained by default. |

## TANSTAAFL resource ledger

The desktop is an instrument, not Luna. Every desktop result must identify its host and is **not** proof of target fit. The provisional Luna constraint remains four Cortex-A35 cores and 1 GiB shared LPDDR3, pending hardware inspection.

| Ledger entry | Measurement | v0 gate |
| --- | --- | --- |
| Network dependency | Observe a second run after assets are present, with networking unavailable where practical. | Must make no inference network request. |
| Runtime form | Inspect the actual executable / shared-library path. | Native Linux CPU path must exist; no target Python service or VM. |
| Model asset + runtime disk | `du -sk` for the exact installed artifact tree. | Recorded; no unexplained companion model. Selection favours the smaller total. |
| Peak RSS | Sample `/proc/<pid>/status` while the process runs. | Recorded per fixture; a desktop value is only a screening signal. |
| Cold start / elapsed time | Wall clock from process start to exit; audio duration gives real-time factor (RTF). | Recorded; no claim of target latency from desktop RTF. |
| CPU / acceleration | Record CPU-only command and any backend notices. | CPU is the baseline. GPU/Vulkan is neither tested nor required. |
| Target headroom | Measure later on delivered hardware: Linux baseline, display/WM, shared graphics allocation, and future Mike/Wyoh reserve. | No pre-hardware candidate is declared target-fit. A later selected deployment must leave measured headroom for the OS and other components. |
| Process lifetime | Observe invocation lifecycle. | Load for a file, transcribe, exit. No daemon. |

An otherwise accurate candidate fails v0 selection if it needs remote inference, requires an unbounded dependency chain, has no evidenced native Linux ARM path, or cannot state its resource cost. Disk size is not RAM, and model parameter count is not a memory measurement.

## Corpus and scoring protocol

The final device corpus will be five short (3–12 s) French recordings, versioned by manifest rather than stored in the repository: clean speech, ordinary-room noise, French technical vocabulary, a short command-like phrase, and a second speaker. Each needs the speaker's consent and a reference transcript. It will be recorded only after hardware/usage validation is green-lit.

Pre-hardware comparison uses the three public French WAVs packaged with the Sherpa model, with their upstream reference transcripts. They include ordinary declarative language plus historical and geographic terms, but not a controlled noisy-room or command set. This is consciously inadequate to claim French accuracy or generalisation. It can prove only: common input handling, offline decoding, an output shape, resource measurement, and a candidate-to-candidate comparison on the same files. The result document must preserve that limitation.

For every candidate × fixture:

1. Validate the audio contract without rewriting it.
2. Run a cold process once; capture raw transcript, stderr, exit code, elapsed seconds, peak RSS, and fixture duration.
3. Compute WER against the normalised reference when one exists; otherwise mark the quality score unavailable.
4. Repeat only when diagnosing an error; report repeats rather than silently choosing the best run.
5. Record runtime and model versions, checksums, artifact sizes, command template, and host architecture.

The quality gate at this phase is modest: it must produce a recognisably correct transcript for the upstream fixture without contextual help. The actual selection gate is comparative: choose the smallest candidate that clears that functional bar and does not create a target-path or ledger failure. Re-open quality only with the later five-clip corpus.

## Reproducibility boundaries

Downloaded weights, built executables, caches, recordings, and benchmark logs live outside this repository. A result record names their source URLs, versions, SHA-256 checksums, host architecture, and collection date. The committed harness never downloads a model implicitly.
