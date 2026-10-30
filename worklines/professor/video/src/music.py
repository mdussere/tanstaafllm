"""Synthesise the chiptune soundtrack and sound effects (numpy only).

120 BPM, A minor, 2 s per bar. Every effect is placed on the same timeline as
index.html, so cuts, stamps and blips land on the picture.

Times below are written in source seconds (the original 60 s cut). holds.json
(written by timing.py) freezes the picture at some source times so that text can
be read; out() maps a source time to the output time, and the groove keeps
playing on the current chord during a hold. Holds are whole beats, so the cuts
stay on the beat.

Usage: python music.py OUT.wav
"""
import json
import pathlib
import sys
import wave

import numpy as np

SR = 48000
HOLDS = sorted(json.loads((pathlib.Path(__file__).resolve().parent / "holds.json").read_text())["holds"])
DUR = 60.0 + sum(d for _, d in HOLDS)
N = int(SR * DUR)


def out(t):
    """Output time of source time t: an event at a hold point plays before the hold."""
    return t + sum(d for s, d in HOLDS if s < t)


def source(T):
    """Source time shown at output time T (frozen during a hold), as in index.html."""
    acc = 0.0
    for s, d in HOLDS:
        if T < s + acc:
            break
        if T < s + acc + d:
            return s
        acc += d
    return T - acc


def lead_in(t_end, dur):
    """Start of an effect of length dur that must end on source time t_end (risers, rolls)."""
    return out(t_end) - dur
BEAT = 0.5
rng = np.random.default_rng(1969)

L = np.zeros(N)
R = np.zeros(N)


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def env(n, a=0.005, d=0.08, s=0.6, r=0.05, hold=None):
    """ADSR envelope of n samples; the release takes the last r seconds."""
    t = np.arange(n) / SR
    total = n / SR
    e = np.ones(n) * s
    ai = t < a
    e[ai] = t[ai] / a
    di = (t >= a) & (t < a + d)
    e[di] = 1 - (1 - s) * (t[di] - a) / d
    ri = t > total - r
    e[ri] *= np.clip((total - t[ri]) / r, 0, 1)
    return e


def osc(kind, f, n, duty=0.5, vib=0.0, slide=None):
    t = np.arange(n) / SR
    if slide is not None:  # exponential pitch slide from f to slide
        freq = f * (slide / f) ** (t / (n / SR))
    else:
        freq = np.full(n, f)
    if vib:
        freq = freq * (1 + vib * np.sin(2 * np.pi * 5.5 * t) * np.clip(t / 0.15, 0, 1))
    ph = np.cumsum(freq) / SR % 1.0
    if kind == "sq":
        return np.where(ph < duty, 1.0, -1.0)
    if kind == "tri":
        return 4 * np.abs(ph - 0.5) - 1
    if kind == "saw":
        return 2 * ph - 1
    if kind == "sin":
        return np.sin(2 * np.pi * ph)
    raise ValueError(kind)


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):  # short buffers only
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def add(t0, sig, vol=1.0, pan=0.0):
    i = int(round(t0 * SR))
    if i >= N or i + len(sig) <= 0:
        return
    if i < 0:
        sig = sig[-i:]
        i = 0
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * vol * (1 - max(0, pan))
    R[i:i + len(sig)] += sig * vol * (1 + min(0, pan))


# ---------------- instruments ----------------
def kick(t0, vol=1.0):
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t * 28)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
    s[:200] += np.linspace(0.6, 0, 200) * rng.uniform(-1, 1, 200)
    add(t0, s, vol)


def snare(t0, vol=0.55):
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    nz = rng.uniform(-1, 1, n)
    nz = nz - np.concatenate([[0], nz[:-1]]) * 0.6
    s = nz * np.exp(-t * 18) + 0.5 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25)
    add(t0, s, vol)


def hat(t0, vol=0.16, open_=False):
    n = int((0.18 if open_ else 0.05) * SR)
    t = np.arange(n) / SR
    nz = rng.uniform(-1, 1, n)
    nz = np.diff(np.concatenate([[0], nz]))  # crude high-pass
    add(t0, nz * np.exp(-t * (14 if open_ else 70)), vol, pan=0.15)


def crash(t0, vol=0.35, length=1.6):
    n = int(length * SR)
    t = np.arange(n) / SR
    nz = np.diff(np.concatenate([[0], rng.uniform(-1, 1, n)]))
    add(t0, nz * np.exp(-t * 3.0 / length * 2), vol * 0.8, pan=-0.2)
    add(t0, nz[::-1][: n] * 0 + nz * np.exp(-t * 3.2 / length * 2), vol * 0.8, pan=0.2)


def note(t0, m, dur, kind="sq", vol=0.2, duty=0.5, pan=0.0, a=0.004, d=0.08, s=0.55, r=0.04, vib=0.0):
    n = int(dur * SR)
    if n <= 0:
        return
    add(t0, osc(kind, midi(m), n, duty, vib) * env(n, a, d, s, r), vol, pan)


def blip(t0, m=84, dur=0.035, vol=0.10, pan=0.0):
    note(t0, m, dur, "sq", vol, 0.25, pan, a=0.001, d=0.02, s=0.4, r=0.01)


def slide(t0, f0, f1, dur, kind="sq", vol=0.15, duty=0.5, pan=0.0):
    n = int(dur * SR)
    add(t0, osc(kind, f0, n, duty, slide=f1) * env(n, 0.003, 0.05, 0.7, dur * 0.3), vol, pan)


def noise_sweep(t0, dur, up=True, vol=0.25):
    n = int(dur * SR)
    t = np.arange(n) / SR
    nz = rng.uniform(-1, 1, n)
    cut = np.linspace(400, 9000, n) if up else np.linspace(9000, 300, n)
    out = np.empty(n)
    acc = 0.0
    for i in range(n):
        a = np.exp(-2 * np.pi * cut[i] / SR)
        acc = (1 - a) * nz[i] + a * acc
        out[i] = acc
    g = (t / dur) ** 2 if up else (1 - t / dur) ** 2
    add(t0, out * g * 2.5, vol)


def impact(t0, vol=1.0):
    kick(t0, 1.1 * vol)
    crash(t0, 0.28 * vol, 1.2)
    slide(t0, 220, 55, 0.4, "sq", 0.18 * vol, 0.5)


# ---------------- harmony ----------------
# chord = (root midi in octave 2/3, quality); bar k covers [2k, 2k+2)
AM, F, C_, G, DM, BB, E = (45, "m"), (41, "M"), (48, "M"), (43, "M"), (50, "m"), (46, "M"), (40, "M")
BARS = [AM, AM, AM, F, C_, G, AM, F, C_, G, AM, F, AM, F, C_, G, AM, DM, BB, E,
        AM, F, C_, G, AM, F, C_, G, F, AM]


def chord_at(t):
    if t >= 57.0:
        return AM
    if t >= 56.0:
        return G
    return BARS[min(int(t // 2), len(BARS) - 1)]


def tones(ch):
    root, q = ch
    return [root, root + (3 if q == "m" else 4), root + 7]


def section(t):
    if t < 4:
        return "intro"
    if t < 16:
        return "groove"
    if t < 20:
        return "slam"
    if t < 24:
        return "pong"
    if t < 34:
        return "select"
    if t < 40:
        return "boss"
    if t < 48:
        return "cell"
    if t < 54:
        return "run"
    if t < 57:
        return "doctrine"
    return "end"


# ---------------- arrangement ----------------
sixteenth = BEAT / 4
for k in range(int(out(57.0) / sixteenth)):
    T = k * sixteenth                     # notes go on the output grid,
    t = source(T)                         # sections and chords follow the source time
    sec = section(t)
    ch = chord_at(t)
    tn = tones(ch)
    pos16 = k % 16                      # position inside the 2-beat group... (16 per bar = 2 s)
    beat_i = k // 4
    # arpeggio (16ths), quiet in the intro
    if sec in ("intro", "groove", "select", "boss", "cell", "run", "doctrine", "slam") or (sec == "pong" and t >= 22):
        pat = [0, 1, 2, 3, 2, 1, 0, 2]
        m = tn[pat[k % 8] % 3] + 24 + (12 if pat[k % 8] == 3 else 0)
        v = 0.045 if sec == "intro" else 0.06
        note(T, m, sixteenth * 0.9, "sq", v * (0.4 + 0.6 * min(1, t / 3.5)) if sec == "intro" else v, 0.25, pan=-0.35, s=0.3, d=0.05)
    # drums
    if k % 4 == 0:
        on_beat = beat_i % 2
        if sec in ("groove", "select", "cell", "run") or (sec == "boss" and t >= 35.5) or (sec == "pong" and t >= 22):
            kick(T)
            if on_beat == 1:
                snare(T)
        if sec == "intro" and t >= 3.0:
            pass
    if sec in ("groove", "select", "cell", "boss") and k % 2 == 0 and not (sec == "boss" and t < 35.5):
        hat(T, 0.13 if k % 4 else 0.08)
    if sec == "run":
        hat(T, 0.12 if k % 2 else 0.07)
    if sec == "pong" and t < 22 and k % 2 == 0:
        hat(T, 0.08)
    # bass: 8ths, octave jumps
    if k % 2 == 0 and sec != "intro" and sec != "end":
        root = ch[0] - 12 if ch[0] >= 45 else ch[0]
        if sec == "slam":
            if k % 8 == 0:
                note(T, root, BEAT * 1.9, "tri", 0.35, s=0.8)
                note(T, root, BEAT * 1.9, "sq", 0.06, 0.5, s=0.6)
        elif sec == "pong" and t < 22:
            if k % 4 == 0:
                note(T, root, sixteenth * 1.5, "tri", 0.3)
        else:
            m = root + (12 if (k // 2) % 2 else 0)
            step = 1 if sec != "run" else 2
            for j in range(step):
                tt = T + j * sixteenth
                note(tt, m, sixteenth * (1.8 / step), "tri", 0.34, s=0.7)
                note(tt, m + 12, sixteenth * (1.6 / step), "sq", 0.045, 0.5, s=0.5)
    # pads in the intro
    if sec == "intro" and k % 16 == 0:
        for m in tn:
            note(T, m + 12, 2.0, "saw", 0.025, a=0.6, d=0.2, s=0.8, r=0.5)

# lead melody, 4-bar phrase (beat offset, length in beats, midi)
PHRASE = [
    (0, 1, 76), (1, 1, 81), (2, .5, 79), (2.5, .5, 76), (3, 1, 74),
    (4, 1.5, 72), (5.5, .5, 69), (6, 1, 72), (7, 1, 77),
    (8, 1, 76), (9, 1, 79), (10, 1, 84), (11, .5, 83), (11.5, .5, 79),
    (12, 1, 74), (13, 1, 71), (14, 1.5, 74), (15.5, .5, 79),
]
BOSS = [(0, 1, 74), (1, 1, 77), (2, 1, 81), (3, 1, 77), (4, 1, 74), (5, 1, 77), (6, 2, 82),
        (8, 1, 80), (9, 1, 76), (10, 1, 80), (11, 1, 83)]


def lead(start, phrase, transpose=0, vol=0.11, until=None):
    for b, ln, m in phrase:
        t = start + b * BEAT
        if until is not None and t >= until:
            continue
        t = out(t)
        note(t, m + transpose, ln * BEAT * 0.92, "sq", vol, 0.25, pan=0.25, a=0.005, d=0.1, s=0.6, r=0.06, vib=0.006)
        # echo (dotted eighth)
        note(t + 0.375, m + transpose, ln * BEAT * 0.8, "sq", vol * 0.35, 0.25, pan=-0.3, s=0.5, r=0.05)


lead(8.0, PHRASE)
lead(24.0, PHRASE)
lead(32.0, PHRASE, until=34.0)
lead(34.0, BOSS, -12 + 12)
lead(40.0, PHRASE, 12, vol=0.08)
lead(48.0, PHRASE, 0, vol=0.09)

# ---------------- sound effects on the picture's timeline ----------------
# Times are source seconds, placed with out(); risers and rolls that lead into a cut
# end on it with lead_in().
# scene 1
for i, tt in enumerate(np.arange(0.0, 1.0, 0.25)):
    blip(out(tt), 88 if i % 2 == 0 else 84, 0.05, 0.05)
note(out(1.0), 83, 0.07, "sq", 0.16, 0.5)    # coin: B5 then E6
note(out(1.07), 88, 0.35, "sq", 0.16, 0.5, s=0.6, r=0.2)
text = "THERE AIN'T NO SUCH THING" + "AS A FREE LUNCH."
for i, c in enumerate(text):
    if c != " ":
        blip(out(1.15 + i / 30), 96 + (i % 3), 0.02, 0.05, pan=0.2)
noise_sweep(out(2.55), 0.2, up=False, vol=0.18)   # strike-through
impact(out(2.95), 0.9)                       # LLM stamp
noise_sweep(lead_in(4.0, 1.0), 1.0, up=True, vol=0.22)   # riser into the cut
for i in range(8):
    snare(lead_in(4.0, 0.5) + i * 0.0625, 0.15 + 0.04 * i)
crash(out(4.0), 0.45, 2.0)
kick(out(4.0), 1.2)
# scene 3
for i in range(6):
    blip(out(8.5 + i * 0.5), 79 + 2 * i, 0.06, 0.09, pan=0.3)
slide(out(8.0), 200, 900, 0.3, "sq", 0.07, 0.25)   # device flies in
for i in range(28):
    blip(out(12.2 + i / 40), 91, 0.02, 0.04, pan=0.2)
# scene 4
for tt in (16.0, 17.0, 18.0):
    impact(out(tt), 1.0)
blip(out(19.0), 88, 0.12, 0.08)
crash(out(19.0), 0.2, 1.0)
for i in range(6):
    blip(out(20.2 + i / 16), 93, 0.025, 0.06)
tt = 20.75
while tt < 21.9:                             # counter ticks, slowing down
    blip(out(tt), 100, 0.012, 0.05, pan=-0.2)
    tt += 0.03 + 0.09 * ((tt - 20.75) / 1.15) ** 2
note(out(21.9), 84, 0.08, "sq", 0.15, 0.5)   # "ding"
note(out(21.98), 96, 0.5, "sq", 0.12, 0.5, s=0.5, r=0.3)
impact(out(22.6), 1.0)
# scene 5
noise_sweep(lead_in(24.0, 0.4), 0.4, up=True, vol=0.15)
for tt in (24.5, 26.0, 27.5, 29.0):
    blip(out(tt), 84, 0.05, 0.12)
    blip(out(tt + 0.06), 91, 0.08, 0.12)
impact(out(31.0), 0.9)
# scene 6
for i in range(6):                           # boss alarm
    slide(out(34.0 + i * 0.25), 880 if i % 2 == 0 else 660, 660 if i % 2 == 0 else 880, 0.24, "sq", 0.06, 0.5)
impact(out(34.0), 0.8)
impact(out(35.5), 0.7)
slide(out(36.0), 150, 600, 0.4, "sq", 0.08, 0.25)
slide(out(37.0), 200, 900, 0.3, "sq", 0.08, 0.25)
note(out(37.3), 84, 0.08, "sq", 0.1); note(out(37.38), 88, 0.08, "sq", 0.1); note(out(37.46), 91, 0.2, "sq", 0.1)
slide(out(38.0), 300, 1200, 0.3, "sq", 0.08, 0.25)
for i in range(7):                           # limit alarm, until the hold before the cut ends
    note(out(38.3) + i * 0.25, 93 if i % 2 == 0 else 89, 0.12, "sq", 0.07, 0.5)
# scene 7
for i in range(6):
    blip(out(40.0 + i * 0.5), 72 + 3 * i, 0.07, 0.1, pan=0.2 * (i % 3 - 1))
for i in range(5):
    impact(out(43.0 + i), 0.55)
# scene 8: a jump and a stage-clear arpeggio each stage
for i in range(6):
    t0 = 48.0 + i
    slide(out(t0), 300, 900, 0.18, "sq", 0.07, 0.25, pan=0.2)
    for j, m in enumerate((84, 88, 91, 96)):
        blip(out(t0 + 0.42) + j * 0.05, m + (2 if i % 2 else 0), 0.05, 0.08, pan=-0.2)
# scene 9: doctrine stabs, roll, final chord
for tt in (54.0, 54.75, 55.5):
    impact(out(tt), 1.0)
    for m in tones(AM):
        note(out(tt), m + 24, 0.5, "saw", 0.05, s=0.5, r=0.2)
for i in range(16):
    snare(lead_in(57.0, 1.0) + i * 0.0625, 0.12 + 0.03 * i)
noise_sweep(lead_in(57.0, 1.0), 1.0, up=True, vol=0.25)
impact(out(57.0), 1.2)
END = DUR - out(57.0)                        # the end card, its hold included
crash(out(57.0), 0.5, END)
for m in (45, 57, 60, 64, 69, 72, 76):       # big A minor chord, ringing out
    note(out(57.0), m, END - 0.1, "saw" if m > 50 else "tri", 0.05 if m > 50 else 0.3, a=0.01, d=0.4, s=0.6, r=1.6, vib=0.004)
    note(out(57.0), m + 12, END - 0.4, "sq", 0.02, 0.25, a=0.01, d=0.4, s=0.5, r=1.4)
# a last "game over" blip pattern under PRESS START
for i, m in enumerate((81, 84, 88, 93)):
    blip(out(58.4) + i * 0.08, m, 0.05, 0.05)

# ---------------- master ----------------
mix = np.stack([L, R], axis=1)
fade = np.ones(N)
fi = int((DUR - 0.7) * SR)              # fade with the picture's fade to black
fade[fi:] = np.linspace(1, 0, N - fi) ** 2
mix *= fade[:, None]
mix /= np.max(np.abs(mix)) + 1e-9
mix = np.tanh(mix * 2.2) / np.tanh(2.2)       # gentle saturation / limiting
mix *= 10 ** (-1.0 / 20)                      # peak at -1 dBFS
pcm = (mix * 32767).astype(np.int16)
with wave.open(sys.argv[1], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("wrote", sys.argv[1])
