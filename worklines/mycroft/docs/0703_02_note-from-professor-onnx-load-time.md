# Note from Professor — prepare the ONNX model once, instead of at every start

**From:** Professor
**To:** Mycroft
**Date:** 2026-10-11
**Status:** coordination note written at the user's request, after reading `0703_01`. The user will work through it with Mycroft. Points marked *to verify* are not checked.

## 1. The user's reading

The model takes about 18 s to load on Luna and 1.3 s on the desk host. A copy from storage to memory should not be 12–15 times slower. If the time goes into processing at load time, that processing should be done **once, ahead of time**, and its result kept as a prepared file. ONNX Runtime then loads that file directly.

## 2. What `0703_01` already shows

- **I/O is small.** Run 1, with a cold cache, took 20.2 s. Runs 2 and 3, with the files cached, took 17.7 s. Reading the card costs about 2.5 s.
- **The rest is CPU work at session creation**, about 15 s. ONNX Runtime does two things there: it rewrites the graph (graph optimisation), and it rearranges the int8 weights into the layout its matrix kernels expect (pre-packing). A ratio of about 14 between a Cortex-A35 and the desk host is consistent with CPU work, not with I/O.

## 3. What ONNX Runtime offers to do this once

1. **A saved optimised model.** Set `SessionOptions.optimized_model_filepath` once: ONNX Runtime writes the graph after optimisation. Later starts load that file with graph optimisation off (`ORT_DISABLE_ALL`).
2. **The ORT format (`.ort`).** This is ONNX Runtime's own pre-optimised format, made for mobile and edge devices. It is produced offline (`python -m onnxruntime.tools.convert_onnx_models_to_ort`). It skips the optimisation work at load, and it can be loaded from bytes without extra copies (`session.use_ort_model_bytes_directly`, `session.use_ort_model_bytes_for_initializers`).
3. **Pre-packed weights.** Pre-packing is what probably costs the most for an int8 model, and it is normally redone at each start. *To verify:* whether the ONNX Runtime version bundled with Sherpa can save pre-packed weights ahead of time, or whether pre-packing can be turned off, and at what cost per inference.

**Make the prepared file on aarch64**, on Luna or `luna-pi`, not on the x86 desk host. Some optimisations depend on the processor, and a file optimised for x86 may be wrong or slower on ARM.

## 4. Does Sherpa allow it? *(to verify first)*

Sherpa-onnx creates the ONNX Runtime sessions itself. Check the following:

- whether it accepts `.ort` model files, or a pre-optimised `.onnx`;
- whether it exposes the graph optimisation level or session options;
- whether it reads the model from a file or from a memory buffer.

If it exposes none of this, there are two other routes: a small patch, or Sherpa's C API with our own session options. Both feed the Python-versus-compiled comparison already asked for.

## 5. Is it really compiled code that runs?

Yes. The heavy computation is in ONNX Runtime's C++ kernels (MLAS), which have hand-written assembly for ARM64. Python only reads the audio, passes it in blocks, and reads the text back. The comparison with Sherpa's own C++ binary will measure what Python actually costs: memory, CPU and start time.

Another point for the test plan: the Cortex-A35 is an ARMv8.0 core and lacks the dot-product instructions (`SDOT`/`UDOT`) that speed up int8 on newer cores. On Luna, int8 may therefore gain less than expected. Measuring fp32 against int8 once would settle it, if the fp32 model fits in memory.

## 6. Suggested order

1. Read Sherpa's code for points 4 and 3.3 (offline).
2. On Luna, using a slot from Professor (`worklines/luna-access.md`), measure the load time three ways: the current model, a pre-optimised file, and an `.ort` file. One thread, then 2 and 4.
3. If the load time is still too long, try a resident provider: it loads once and stays in memory. Swap would only be studied as zram, as a proposal.
4. Record each result in `0703_01` or in a new result file, and the decisions in the plan.
