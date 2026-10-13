"""Record Luna's capture device under controlled jack conditions (see audio_jack_record.feature).

Run one condition at a time from Termidor, with output visible:
    uv run pytest -m live -s "test/luna/test_audio_jack_record.py::test_record_condition[none-silent]"
"""

from __future__ import annotations

import array
import io
import json
import math
import os
import subprocess
import wave
from datetime import datetime
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DEVICE = "hw:0,0"
RATE = 48000
CHANNELS = 2
SECONDS = 5

CONDITIONS = {
    "none-silent": "Unplug everything and stay quiet.",
    "none-speak": "Unplug everything and speak normally about 20 cm from the handheld.",
    "headset-silent": "Plug a 4-pole headset with a microphone and stay quiet.",
    "headset-speak": "Plug a 4-pole headset with a microphone and speak into its microphone.",
    "headphones-speak": "Plug 3-pole headphones (no microphone) and speak at the handheld.",
    "usb-silent": "USB-C headset plugged into Luna; stay quiet.",
    "usb-speak": "USB-C headset plugged into Luna; speak into its microphone.",
}
USB_DEVICE = "hw:1,0"  # Step 8.2e: first USB sound card; override with LUNA_AUDIO_DEVICE


def device_for(condition: str) -> str:
    return os.environ.get("LUNA_AUDIO_DEVICE") or (USB_DEVICE if condition.startswith("usb-") else DEVICE)


def channel_stats(frames: bytes, channels: int) -> list[dict[str, float]]:
    """RMS, peak and DC offset per channel of 16-bit little-endian PCM, in dBFS where relevant."""
    samples = array.array("h")
    samples.frombytes(frames)
    stats = []
    for channel in range(channels):
        values = samples[channel::channels]
        count = max(len(values), 1)
        mean = sum(values) / count
        rms = math.sqrt(sum((v - mean) ** 2 for v in values) / count)
        peak = max((abs(v) for v in values), default=0)
        stats.append({
            "rms": round(rms, 2),
            "rms_dbfs": round(20 * math.log10(rms / 32768), 1) if rms else -math.inf,
            "peak": peak,
            "peak_dbfs": round(20 * math.log10(peak / 32768), 1) if peak else -math.inf,
            "dc_offset": round(mean, 2),
        })
    return stats


def test_channel_stats_on_a_known_signal() -> None:
    left = [1000, -1000] * 50
    right = [0] * 100
    frames = array.array("h", [s for pair in zip(left, right) for s in pair]).tobytes()
    stats = channel_stats(frames, 2)
    assert stats[0]["rms"] == 1000 and stats[0]["peak"] == 1000 and stats[0]["dc_offset"] == 0
    assert stats[1]["rms"] == 0 and stats[1]["rms_dbfs"] == -math.inf


def ssh(command: str, *, binary: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "luna", command],
                          capture_output=True, text=not binary, check=False, timeout=60)


@pytest.mark.live
@pytest.mark.parametrize("condition", list(CONDITIONS))
def test_record_condition(condition: str) -> None:
    result_dir = ROOT / "results/luna/audio-jack" / f"{datetime.now():%Y%m%dT%H%M%S}_{condition}"
    result_dir.mkdir(parents=True)

    before = ssh("amixer -c0 cget name='Headphones Jack'; amixer -c0 contents; cat /proc/asound/cards; "
                 "amixer -c1 contents 2>/dev/null")
    (result_dir / "mixer-before.txt").write_text(before.stdout + before.stderr, encoding="utf-8")
    assert before.returncode == 0, before.stderr

    device = device_for(condition)
    print(f"\n{CONDITIONS[condition]}\nRECORDING {SECONDS} s on {device} — go now ...", flush=True)
    recorded = ssh(f"arecord -D {device} -f S16_LE -r {RATE} -c {CHANNELS} -d {SECONDS} -t wav -",
                   binary=True)
    print("done.", flush=True)
    (result_dir / "arecord.log").write_bytes(recorded.stderr)
    assert recorded.returncode == 0, recorded.stderr.decode(errors="replace")
    (result_dir / "recording.wav").write_bytes(recorded.stdout)

    after = ssh("amixer -c0 cget name='Headphones Jack'")
    (result_dir / "jack-after.txt").write_text(after.stdout + after.stderr, encoding="utf-8")

    # arecord writes a streaming header with an unknown length; read the PCM after the header.
    with wave.open(io.BytesIO(recorded.stdout)) as wav:
        assert (wav.getnchannels(), wav.getsampwidth(), wav.getframerate()) == (CHANNELS, 2, RATE)
        header = len(recorded.stdout) - wav.getnframes() * CHANNELS * 2
    frames = recorded.stdout[max(header, 44):]
    seconds = len(frames) / (RATE * CHANNELS * 2)
    jack_on = "values=on" in before.stdout.split("numid=", 2)[1] if "numid=" in before.stdout else None

    stats = {"condition": condition, "instruction": CONDITIONS[condition], "device": device,
             "seconds": round(seconds, 2), "headphones_jack_on": jack_on,
             "channels": channel_stats(frames, CHANNELS)}
    (result_dir / "stats.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(stats, indent=2))
    assert seconds >= SECONDS - 0.5, f"only {seconds:.2f} s captured"


SNAPSHOT = (
    "echo '## jack'; amixer -c0 cget numid=1 | tail -1; "
    "grep -i 'Headphone detection' /sys/kernel/debug/gpio; "
    "echo '## saradc (raw, scale mV)'; I=/sys/bus/iio/devices/iio:device0; cat $I/in_voltage_scale; "
    "for c in 0 1 2 3 4 5; do echo \"ch$c $(cat $I/in_voltage${c}_raw) $(cat $I/in_voltage${c}_raw)\"; done; "
    "echo '## rk817 codec registers 0x12-0x4f'; "
    "grep -E '^(1[2-9a-f]|[2-4][0-9a-f]):' /sys/kernel/debug/regmap/0-0020/registers; "
    "echo '## dapm'; D=/sys/kernel/debug/asoc/rk817_ext/rk817-codec.5.auto/dapm; "
    "for w in 'MIC Power On' MICL MICR 'ADC L' 'ADC R'; do head -1 \"$D/$w\"; done"
)


@pytest.mark.live
def test_codec_and_mic_line_snapshot() -> None:
    """Step 8.2b: read-only snapshot of jack detect, SARADC and codec registers, at rest and during capture."""
    result_dir = ROOT / "results/luna/audio-jack" / f"{datetime.now():%Y%m%dT%H%M%S}_snapshot"
    result_dir.mkdir(parents=True)
    rest = ssh(SNAPSHOT)
    (result_dir / "rest.txt").write_text(rest.stdout + rest.stderr, encoding="utf-8")
    capture = ssh(f"arecord -D {DEVICE} -f S16_LE -r {RATE} -c {CHANNELS} -d 4 -t raw /dev/null 2>/dev/null & "
                  f"sleep 2; {SNAPSHOT}; wait")
    (result_dir / "capture.txt").write_text(capture.stdout + capture.stderr, encoding="utf-8")
    print(f"\n==== REST ====\n{rest.stdout}\n==== DURING CAPTURE ====\n{capture.stdout}")
    assert rest.returncode == 0 and capture.returncode == 0, rest.stderr + capture.stderr
    assert "MIC Power On: On" in capture.stdout


# Step 8.2c: runtime register trial (green-lit by the user on 2026-10-11). It writes only the
# RK817 codec's live registers over I2C; a reboot restores them, and the test restores them too.
TRIAL_PHASES = [
    ("as-is", "ArchR state: differential, AMIC_CFG1 untouched"),
    ("cfg1", "AMIC_CFG1 (0x28) = 0x30, as the factory driver writes"),
    ("cfg1+single", "AMIC_CFG1 = 0x30 and single-ended input (0x27 bit 7 cleared)"),
    ("single", "single-ended input only, AMIC_CFG1 back to 0x00"),
]
PHASE_SECONDS = 2.5
TRIAL_SCRIPT = r"""
set -u
get() { i2cget -f -y 0 0x20 $1; }
up() { cut -d' ' -f1 /proc/uptime; }
arecord -D hw:0,0 -f S16_LE -r 48000 -c 2 -d 10 -t wav /tmp/luna-8.2c.wav 2>/tmp/luna-8.2c.log &
echo "start $(up)"
sleep 1
r27=$(get 0x27); r28=$(get 0x28)
echo "phase as-is $(up) 0x27=$r27 0x28=$r28"
sleep 1.5
i2cset -f -y 0 0x20 0x28 0x30
echo "phase cfg1 $(up) 0x27=$(get 0x27) 0x28=$(get 0x28)"
sleep 2.5
i2cset -f -y 0 0x20 0x27 $(( r27 & 0x7f ))
echo "phase cfg1+single $(up) 0x27=$(get 0x27) 0x28=$(get 0x28)"
sleep 2.5
i2cset -f -y 0 0x20 0x28 0x00
echo "phase single $(up) 0x27=$(get 0x27) 0x28=$(get 0x28)"
wait
v=$(get 0x27); i2cset -f -y 0 0x20 0x27 $(( v | 0x80 )); i2cset -f -y 0 0x20 0x28 $r28
echo "restored $(up) 0x27=$(get 0x27) 0x28=$(get 0x28)"
cat /tmp/luna-8.2c.log
"""


def window_rms(frames: bytes, channels: int, rate: int, seconds: float) -> list[list[float]]:
    """RMS in dBFS per channel for consecutive windows, DC removed per window."""
    step = int(rate * seconds) * channels * 2
    return [[s["rms_dbfs"] for s in channel_stats(frames[i:i + step], channels)]
            for i in range(0, len(frames) - step + 1, step)]


@pytest.mark.live
def test_register_trial() -> None:
    """Step 8.2c: does writing AMIC_CFG1 and/or single-ended input bring the headset microphone to life?"""
    if os.environ.get("LUNA_AUDIO_WRITE") != "1":
        pytest.skip("writes codec registers: set LUNA_AUDIO_WRITE=1 (Step 8.2c, user-approved)")
    result_dir = ROOT / "results/luna/audio-jack" / f"{datetime.now():%Y%m%dT%H%M%S}_trial-8.2c"
    result_dir.mkdir(parents=True)
    print("\nKeep tapping or scratching the headset microphone for 10 s ... RECORDING", flush=True)
    run = ssh(TRIAL_SCRIPT)
    print("done.", flush=True)
    (result_dir / "trial.log").write_text(run.stdout + run.stderr, encoding="utf-8")
    assert run.returncode == 0, run.stdout + run.stderr
    wav_bytes = ssh("cat /tmp/luna-8.2c.wav && rm -f /tmp/luna-8.2c.wav /tmp/luna-8.2c.log", binary=True).stdout
    (result_dir / "recording.wav").write_bytes(wav_bytes)
    with wave.open(io.BytesIO(wav_bytes)) as wav:
        frames = wav.readframes(wav.getnframes())

    log = run.stdout.splitlines()
    start = float(next(l for l in log if l.startswith("start")).split()[1])
    phases = {l.split()[1]: float(l.split()[2]) - start for l in log if l.startswith("phase")}
    bounds = [phases[name] for name, _ in TRIAL_PHASES] + [len(frames) / (RATE * CHANNELS * 2)]
    summary = []
    for (name, meaning), begin, end in zip(TRIAL_PHASES, bounds, bounds[1:]):
        a, b = (int((t + 0.2) * RATE) * CHANNELS * 2 for t in (begin, end - 0.2))
        summary.append({"phase": name, "meaning": meaning, "from_s": round(begin, 2), "to_s": round(end, 2),
                        "channels": channel_stats(frames[a:b], CHANNELS)})
    stats = {"phases": summary, "windows_0.5s_dbfs": window_rms(frames, CHANNELS, RATE, 0.5)}
    (result_dir / "stats.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    for p in summary:
        print(f"{p['phase']:12} {p['from_s']:5.2f}-{p['to_s']:5.2f} s  "
              + "  ".join(f"{c['rms_dbfs']:6.1f} dBFS" for c in p["channels"]))
    assert "restored" in run.stdout


# Step 8.2c, second trial: the exact register values the factory BSP driver writes for capture.
# The first trial left AMIC_CFG0's low bits as ArchR set them (bit 2), whereas the BSP sets bit 1.
FACTORY_PHASES = [
    ("as-is", {}),
    ("factory", {"0x27": "0x0a", "0x28": "0x30", "0x29": "0xaa"}),
    ("factory+bit2", {"0x27": "0x0e", "0x28": "0x30", "0x29": "0xaa"}),
    ("bit1-only", {"0x27": "0x02", "0x28": "0x30", "0x29": "0xaa"}),
]


def factory_trial_script() -> str:
    lines = ["set -u", "get() { i2cget -f -y 0 0x20 $1; }", "up() { cut -d' ' -f1 /proc/uptime; }",
             "rest27=$(get 0x27); rest28=$(get 0x28); rest29=$(get 0x29)",
             "arecord -D hw:0,0 -f S16_LE -r 48000 -c 2 -d 10 -t wav /tmp/luna-8.2c.wav 2>/tmp/luna-8.2c.log &",
             'echo "start $(up)"', "sleep 1",
             "r27=$(get 0x27); r28=$(get 0x28); r29=$(get 0x29)"]
    for index, (name, writes) in enumerate(FACTORY_PHASES):
        if index:
            lines.append("sleep 2.3")
        lines += [f"i2cset -f -y 0 0x20 {reg} {value}" for reg, value in writes.items()]
        lines.append(f'echo "phase {name} $(up) 0x27=$(get 0x27) 0x28=$(get 0x28) 0x29=$(get 0x29)"')
    lines += ["wait",
              "i2cset -f -y 0 0x20 0x27 $rest27; i2cset -f -y 0 0x20 0x28 $rest28",
              "i2cset -f -y 0 0x20 0x29 $rest29",
              'echo "restored $(up) 0x27=$(get 0x27) 0x28=$(get 0x28) 0x29=$(get 0x29)"',
              "cat /tmp/luna-8.2c.log"]
    return "\n".join(lines) + "\n"


@pytest.mark.live
def test_register_trial_factory_values() -> None:
    """Step 8.2c: the factory driver's exact capture register values, including AMIC_CFG0 bit 1."""
    if os.environ.get("LUNA_AUDIO_WRITE") != "1":
        pytest.skip("writes codec registers: set LUNA_AUDIO_WRITE=1 (Step 8.2c, user-approved)")
    result_dir = ROOT / "results/luna/audio-jack" / f"{datetime.now():%Y%m%dT%H%M%S}_trial-8.2c-factory"
    result_dir.mkdir(parents=True)
    script = factory_trial_script()
    (result_dir / "script.sh").write_text(script, encoding="utf-8")
    run = ssh(script)
    (result_dir / "trial.log").write_text(run.stdout + run.stderr, encoding="utf-8")
    assert run.returncode == 0, run.stdout + run.stderr
    wav_bytes = ssh("cat /tmp/luna-8.2c.wav && rm -f /tmp/luna-8.2c.wav /tmp/luna-8.2c.log", binary=True).stdout
    (result_dir / "recording.wav").write_bytes(wav_bytes)
    with wave.open(io.BytesIO(wav_bytes)) as wav:
        frames = wav.readframes(wav.getnframes())
    log = run.stdout.splitlines()
    start = float(next(l for l in log if l.startswith("start")).split()[1])
    marks = [(l.split()[1], float(l.split()[2]) - start) for l in log if l.startswith("phase")]
    bounds = [t for _, t in marks] + [len(frames) / (RATE * CHANNELS * 2)]
    summary = []
    for (name, _), begin, end in zip(marks, bounds, bounds[1:]):
        a, b = (int((t + 0.2) * RATE) * CHANNELS * 2 for t in (begin, end - 0.2))
        summary.append({"phase": name, "from_s": round(begin, 2), "to_s": round(end, 2),
                        "channels": channel_stats(frames[a:b], CHANNELS)})
    stats = {"phases": summary, "windows_0.5s_dbfs": window_rms(frames, CHANNELS, RATE, 0.5)}
    (result_dir / "stats.json").write_text(json.dumps(stats, indent=2) + "\n", encoding="utf-8")
    for p in summary:
        print(f"{p['phase']:13} {p['from_s']:5.2f}-{p['to_s']:5.2f} s  "
              + "  ".join(f"{c['rms_dbfs']:6.1f} dBFS" for c in p["channels"]))
    assert "restored" in run.stdout


@pytest.mark.live
def test_usb_audio_snapshot() -> None:
    """Step 8.2d: what Luna enumerates on USB, and which capture devices exist, with an adapter plugged."""
    result_dir = ROOT / "results/luna/audio-jack" / f"{datetime.now():%Y%m%dT%H%M%S}_usb-audio"
    result_dir.mkdir(parents=True)
    run = ssh("echo '## lsusb'; lsusb; echo '## usb devices'; ls /sys/bus/usb/devices/; "
              "echo '## sound cards'; cat /proc/asound/cards; arecord -l; ls /dev/snd; "
              "echo '## kernel usb/sound messages'; dmesg | grep -i -E 'usb|snd|audio' | grep -v -E 'mali|wyoh'")
    (result_dir / "snapshot.txt").write_text(run.stdout + run.stderr, encoding="utf-8")
    print(run.stdout)
    assert run.returncode == 0, run.stderr
