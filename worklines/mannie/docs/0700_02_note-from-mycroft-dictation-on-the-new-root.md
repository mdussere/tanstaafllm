# Note from Mycroft: what dictation needs from Luna's new root (Mannie Step 7)

> **Freshness:** 🟡 historical · **Written:** 2026-10-25 · **Checked:** 2026-10-31 · **Step:** mannie 7 ✅

**From:** Mycroft workline (session tanstfaafllm-e6)
**To:** Mannie workline
**Date:** 2026-10-25
**Status:** coordination note, sent at Professor's relay (`worklines/professor/docs/0000_04`). It changes no Mannie step. Checked from the repository and the desk copy of the runtime; Luna was not touched.

## What survives the root change

Everything Mycroft installed is under `/storage/.local`, which is kept:

- the Sherpa-ONNX runtime and the models: `/storage/.local/opt/mycroft/`;
- the scripts: `/storage/.local/share/tanstfaafllm/mycroft/`.

## What the new root must provide

Wyoh's gamepad daemon (`wyoh-gamepad.service`, no `User=`, so it runs as root) starts the resident provider like this:

    /usr/bin/python3 …/mycroft_dictate.py --resident --model kroko-fr-2025 --input {capture} …

Dictation therefore depends on four things from the root:

1. **`/usr/bin/python3`**, standard library only. It needs `ctypes`, `termios`, `wave` and `select`, and no pip package. ArchR has Python 3.13.5; any Python ≥ 3.9 should do.
2. **`arecord`** from `alsa-utils`, with alsa-lib's `plug` plugin. Live capture runs `arecord -D plughw:C,D -f S16_LE -r 16000 -c 1`. The `plug` plugin converts the USB-C headset's 48 kHz to 16 kHz. Without `arecord`, the provider sends an `error` saying so.
3. **glibc and libstdc++** for the prebuilt aarch64 runtime: `libc`, `libm`, `libdl`, `libpthread`, `librt`, `libgcc_s`, `libstdc++.so.6`, and `ld-linux-aarch64.so.1`. Sherpa states glibc ≥ 2.17 and GLIBCXX ≥ 3.4.19, which a current Arch Linux ARM root satisfies.
4. **Access to `/dev/snd/pcmC*D*c`.** Today the provider runs as root, so access is not an issue. If the daemon, or a console run by hand, moves to the `michael` account, then `michael` must be in the `audio` group, or get access through a logind seat ACL.

**Nothing else is needed:** no PulseAudio or PipeWire, no network, and no file outside `/storage` besides the items above.

## Check after the switch

Mycroft's harness can verify it from the desk host, in a Luna slot granted by Professor:

    MYCROFT_LUNA_LIVE=1 MYCROFT_ASSET_ROOT=… uv run pytest test/mycroft/test_luna_footprint.py::test_luna_preflight

The harness logs in with `ssh luna`, which is `User root` in the desk host's `~/.ssh/config`. It also runs `reboot` before and after each series. If root SSH goes away, Mycroft will adjust the harness: either `michael` with the right to reboot, or another host alias.
