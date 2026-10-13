# Note from Professor — OpenCL on Luna's GPU (parked)

**From:** Professor
**To:** Mycroft
**Date:** 2026-10-11
**Status:** parked by the user. Do not start this until Mycroft has usable CPU dictation on Luna. Recorded in the plan under "Recorded for later".

## User decision

First get usable dictation on Luna, with low lag on the CPU. Use all four cores if needed, and optimise the model load (sub-steps 7.3c–e and note `0703_02`). OpenCL comes afterwards: "even if the gain is not magnificent, it could be fun to drive OpenCL on the micro GPU."

## What Luna has (read-only listing, 2026-10-11)

- ArchR loads ARM's own driver, `libmali-bifrost-g31-g24p0-wayland-gbm` (`/usr/lib/libmali.so.1.9.0`, 56 MB). The device node is `/dev/mali0`.
- **OpenCL: present.** The library exports `clGetPlatformIDs` and registers itself in `/etc/OpenCL/vendors/mali.icd`.
- **Vulkan: absent.** The library has no `vkCreateInstance`, and no Vulkan ICD file exists. Paths that need Vulkan (llama.cpp Vulkan, ncnn, whisper.cpp Vulkan) are closed with this driver.
- OpenGL ES 3.1 compute shaders are a second possible way in.
- Nothing has run on the GPU yet. Whether OpenCL works, and how fast it is, is unknown.

## Candidate engines (not verified)

| Engine | GPU path | Remarks |
|---|---|---|
| ONNX Runtime with the Arm NN or ACL execution provider | OpenCL (Arm Compute Library targets Mali) | Closest to Sherpa's ONNX models. ONNX Runtime would have to be rebuilt for aarch64. |
| MNN | OpenCL | Used on Mali. Converts from ONNX. |
| TensorFlow Lite GPU delegate | OpenCL or GLES 3.1 | Needs a model conversion. |
| llama.cpp OpenCL | OpenCL | Aimed at Adreno; Mali support is weak. More relevant to Mike (the local brain) than to Mycroft. |

## Cautions

- The G31 MP2 is a very small GPU. It shares Luna's 1 GiB and its memory bandwidth with the CPU.
- Streaming ASR works in small chunks, so the overhead of each GPU dispatch may cancel the gain.
- The GPU is also used by the compositor, so a compute job could disturb the display.

## When it is unparked

1. Check that the OpenCL platform answers (`clinfo`), and measure raw GPU throughput against the 4 CPU cores (for example with `clpeak`), all under `/storage`.
2. Try one engine on the same model and WAV as the CPU measurements, and compare lag, load time and RSS.
