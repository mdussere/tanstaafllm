"""TANSTAAFLLM story 1, "Hello, Luna": soundtrack for a 2A03 (NES) sound chip, four voices, mono.

Run:  uv run --project <repo> python score.py OUT.wav   (also writes hits.json beside OUT.wav)
Writes 94.00 s, 48 kHz, 16-bit (the mono chip output on both channels).

Same chip, same tempo and same helpers as the trailer score (series unity):
P1 = lead, P2 = harmony / fast-arpeggio chords / effects, TRI = bass and kick drops,
NOISE = drums and hits. 120 BPM (0.5 s per beat, 2 s per bar), A minor. The trailer theme
opens and closes the episode. Times are seconds of the final cut (no reading holds).
"""
import json
import pathlib
import sys
import wave

import numpy as np

from nes import APU, SR

HERE = pathlib.Path(__file__).resolve().parent
DUR = 94.0
OFF = 0.0          # added to every time: the scenes after the choice of system (2026-10-31) play 6 s later
A = APU(DUR)
P1, P2 = 0, 1
HITS = []


def F(t):
    """Frame of time t (16ths fall on 8/7-frame grooves, as in trackers)."""
    return int(np.floor((t + OFF) * 60 + 0.5 + 1e-9))


def hit(t, label):
    HITS.append((round(t + OFF, 3), label))


# ------------------------------------------------------------- envelopes (frame k of n, peak v) -> 0..15
def E_sus(k, n, v):
    return v


def E_lead(k, n, v):            # bite, then settle three steps lower
    return v - min(3, k // 4)


def E_exp(tau):
    return lambda k, n, v: v * np.exp(-k / tau)


def E_swell(v0, v1):
    return lambda k, n, v: v0 + (v1 - v0) * k / max(1, n - 1)


def E_fade(hold, v_end=0):      # hold the level, then fade in 4-bit steps to v_end
    return lambda k, n, v: v if k < hold else v + (v_end - v) * (k - hold) / max(1, n - hold)


# ------------------------------------------------------------- writers
def note(ch, t, dur, m, v=12, duty=2, env=E_lead, vib=0.0, vib_delay=14, vib_rate=6.0, slide=0.0,
         slide_frames=None, arp=None, arp_rate=1, release=2):
    f0 = F(t)
    n = max(1, F(t + dur) - f0)
    vol, mm = v, m
    for k in range(n):
        vol = env(k, n, v)
        mm = m
        if slide:
            mm += slide * min(1.0, k / (slide_frames or n))
        if vib and k >= vib_delay:
            mm += vib * np.sin(2 * np.pi * vib_rate * (k - vib_delay) / 60)
        if arp:
            mm += arp[(k // arp_rate) % len(arp)]
        A.pulse(ch, f0 + k, mm, vol, duty)
    for k in range(release):
        A.pulse(ch, f0 + n + k, mm, vol * (release - k) / (release + 1), duty, weak=True)


def chord_arp(ch, t0, t1, root, ivs, v=5, duty=1, env=E_sus, rate=1):
    note(ch, t0, t1 - t0, root, v, duty, env=env, arp=list(ivs), arp_rate=rate, release=0)


def tri(t, dur, m, gate=1.0, slide=0.0):
    f0 = F(t)
    n = max(1, F(t + dur) - f0)
    g = max(1, int(round(n * gate)))
    for k in range(n):
        if k < g:
            A.triangle(f0 + k, m + slide * k / g)
        else:
            A.tri_halt(f0 + k)


def tri_drop(t, m0, m1, frames=4, then=None):
    f0 = F(t)
    for k in range(frames):
        A.triangle(f0 + k, m0 + (m1 - m0) * k / max(1, frames - 1))
    if then == 'halt':
        A.tri_halt(f0 + frames)


def nz(t, vols, pers, mode=0, weak=False):
    f0 = F(t)
    pers = pers if isinstance(pers, (list, tuple)) else [pers] * len(vols)
    for k, v in enumerate(vols):
        A.noise(f0 + k, v, pers[min(k, len(pers) - 1)], mode, weak)


# ------------------------------------------------------------- drums (noise, plus triangle drops)
def kick(t, v=13, drop=True, root=None):
    nz(t, [v, v * 0.55, v * 0.25], [9, 11, 12])
    if drop:
        tri_drop(t, 50, 26, 4, then=None if root is None else 'halt')


def snare(t, v=12, n=9):
    nz(t, [v * 0.8 ** k for k in range(n)], [3] + [6] * (n - 1))


def hat(t, v=4, open_=False, weak=False):
    nz(t, [v * (0.82 if open_ else 0.45) ** k for k in range(10 if open_ else 3)], 0, weak=weak)


def crash(t, v=12, n=50, per=2):
    nz(t, [v * 0.95 ** k for k in range(n)], [4, 3] + [per] * (n - 2))


def boom(t, v=15, n=40):
    nz(t, [v, v] + [v * 0.92 ** k for k in range(n)], [3, 5] + [13] * n)


def clank(t, v=10, n=8):
    nz(t, [v * 0.75 ** k for k in range(n)], 7, mode=1)


def roll(t0, t1, v0, v1, gap0=4, gap1=2, per0=6, per1=3):
    f, f1 = F(t0), F(t1)
    while f < f1:
        p = (f - F(t0)) / max(1, f1 - F(t0))
        v = v0 + (v1 - v0) * p
        gap = max(1, int(round(gap0 + (gap1 - gap0) * p)))
        per = int(round(per0 + (per1 - per0) * p))
        for k in range(gap):
            if f + k < f1:
                A.noise(f + k, v * 0.6 ** k, per, 0)
        f += gap


def noise_sweep(t0, t1, per0, per1, v0, v1):
    f, f1 = F(t0), F(t1)
    for k in range(f1 - f):
        p = k / max(1, f1 - f - 1)
        A.noise(f + k, v0 + (v1 - v0) * p, int(round(per0 + (per1 - per0) * p)), 0)


def hit_all(t, m1, m2, root, v=15, tau=16, dur=0.8, cym='crash', tri_hold=0.6, duty=2):
    """Everything at once: two pulse notes, a triangle drop onto the root, a noise crash."""
    if m1 is not None:
        note(P1, t, dur, m1, v, duty, env=E_exp(tau), release=0)
    if m2 is not None:
        note(P2, t, dur, m2, v, duty, env=E_exp(tau), release=0)
    tri_drop(t, root + 24, root, 5)
    if tri_hold:
        tri(t + 5 / 60, tri_hold, root)
    if cym == 'crash':
        crash(t, v)
    elif cym == 'boom':
        boom(t, v)


# ------------------------------------------------------------- sound effects (they steal a channel)
def blip(ch, t, m, frames=4, v=10, duty=2, slide=0.0):
    note(ch, t, frames / 60, m, v, duty, env=E_exp(frames / 1.5), slide=slide, release=0)


def coin(ch, t, v=12):
    note(ch, t, 4 / 60, 83, v, 2, env=E_sus, release=0)
    note(ch, t + 4 / 60, 0.5, 88, v, 2, env=E_exp(9), release=0)


def tick(t, v=5):
    nz(t, [v, v * 0.3], 0, mode=1)


def key(t, v=9):
    nz(t, [v, v * 0.5, v * 0.2], [3, 5, 8], mode=1)


def typing(t0, cps, text, fn):
    for i, c in enumerate(text):
        if c != ' ':
            fn(t0 + (i + 1) / cps)


# ------------------------------------------------------------- harmony
ROOT = {'Am': 33, 'F': 29, 'C': 36, 'G': 31, 'E': 28, 'Dm': 38, 'B': 35, 'D': 38}
IVS = {'Am': (0, 3, 7), 'F': (0, 4, 7), 'C': (0, 4, 7), 'G': (0, 4, 7), 'E': (0, 4, 7), 'Dm': (0, 3, 7),
       'Esus4': (0, 5, 7), 'Asus2': (0, 2, 7)}


def bass8(t0, t1, root, octave=True, gate=0.65):
    k = 0
    while t0 + k * 0.25 < t1 - 1e-6:
        tri(t0 + k * 0.25, min(0.25, t1 - t0 - k * 0.25), root + (12 if octave and k % 2 else 0), gate)
        k += 1


def hats(t0, t1, step=0.25, v_on=4, v_off=2, weak=False):
    k = 0
    while t0 + k * step < t1 - 1e-6:
        hat(t0 + k * step, v_on if k % 2 else v_off, weak=weak)
        k += 1




# (from the trailer score: the boss ostinato and the double-time beat)
OST = [0, 0, 12, 0, 1, 0, 12, 0, 0, 0, 12, 0, 3, 0, 1, 0]


def ostinato(t0, t1, root):
    k = 0
    while t0 + k * 0.125 < t1 - 1e-6:
        tri(t0 + k * 0.125, 0.125, root + OST[k % 16], 0.7)
        k += 1


def double_time(t0, t1, v=12, snare_on=True):
    k = 0
    while t0 + k * 0.25 < t1 - 1e-6:
        t = t0 + k * 0.25
        hat(t + 0.125, 3)
        if k % 2 == 0:
            kick(t, v, drop=False)
        elif snare_on:
            snare(t, v - 1, 7)
        k += 1




# ============================================================= episode helpers
def chords_at(t0, prog):
    """prog: [(name, seconds), ...] from t0 -> [(start, end, name), ...]"""
    out, t = [], t0
    for name, d in prog:
        out.append((t, t + d, name))
        t += d
    return out


def groove(t0, prog, drums='full', arp_v=5, bass=True, hat_v=4):
    """Bass in eighths, P2 chord arpeggio, kick on 1 and 3, snare on 2 and 4."""
    for a, b, ch in chords_at(t0, prog):
        if bass:
            bass8(a, b, ROOT[ch])
        if arp_v:
            chord_arp(P2, a, b, ROOT[ch] + 36, IVS[ch], arp_v, 1, rate=2)
    t1 = t0 + sum(d for _, d in prog)
    if drums == 'none':
        return
    hats(t0, t1, 0.25, hat_v, 2, weak=True)
    k = 0
    while t0 + k * 0.5 < t1 - 1e-6:
        t = t0 + k * 0.5
        if k % 2 == 0:
            kick(t, 12 if drums == 'full' else 9, drop=True)
        elif drums == 'full':
            snare(t, 10, 7)
        k += 1


def melody(t0, notes, v=11, duty=2, gap=0.02):
    """notes: [(beat offset from t0, midi, beats)], one beat = 0.5 s."""
    for b, m, d in notes:
        note(P1, t0 + b * 0.5, d * 0.5 - gap, m, v, duty, vib=0.2 if d >= 1 else 0.0)


def stage_start(t):
    for i, m in enumerate((69, 72, 76, 81)):
        blip(P1, t + i * 0.06, m, 4, 11, 1)
    crash(t, 8, 30); kick(t, 13)
    hit(t, 'stage start')


def clear(t):
    """The CLEAR! jingle: a coin, then a major arpeggio up on P2."""
    coin(P1, t, 13)
    for i, m in enumerate((76, 80, 83, 88)):
        blip(P2, t + 0.08 + i * 0.07, m, 5, 11, 2)
    nz(t, [12, 9, 6, 4, 2], 3)
    hit(t, 'CLEAR!')


def buzz(t, dur=0.35, m=40, v=13):
    """The failure buzz: a low 12.5 % pulse sliding down, with a short noise rasp."""
    note(P1, t, dur, m, v, 0, env=E_exp(dur * 40), slide=-6, release=0)
    nz(t, [v, v * 0.8, v * 0.6, v * 0.4, v * 0.2], 12)


def ding(t, m=84):
    note(P2, t, 0.06, m, 12, 2, env=E_sus, release=0)
    note(P2, t + 0.06, 0.4, m + 7, 11, 2, env=E_exp(10), release=0)


def stamp(t, m1, m2, root, v=14):
    hit_all(t, m1, m2, root, v, tau=12, dur=0.6, cym='boom', tri_hold=0.4)


# ============================================================= the score
def title():
    # 0 - 5: the series opener. A coin, the stamp, then the trailer theme over Am F G.
    blip(P2, 0.3, 88, 3, 7, 1); blip(P2, 0.35, 93, 4, 7, 1); hit(0.3, 'series line')
    note(P1, 0.62, 0.36, 86, 3, 1, env=E_sus, slide=-10, release=0)
    stamp(1.0, 57, 64, 33); hit(1.0, 'STAMP HELLO, LUNA')
    groove(1.0, [('Am', 2), ('F', 1), ('G', 1)], drums='light', arp_v=5)
    for t, m, d in [(1.25, 76, 0.75), (2.0, 69, 0.25), (2.25, 72, 0.5), (2.75, 76, 0.5),
                    (3.25, 77, 0.5), (3.75, 76, 0.25), (4.0, 76, 0.25), (4.25, 72, 0.25), (4.5, 74, 0.45)]:
        note(P1, t, d - 0.02, m, 12, 2, vib=0.2 if d >= 0.5 else 0.0)
    roll(4.5, 4.98, 5, 12, gap0=3, gap1=2)


LUNA_THEME = [(0, 69, 1), (1, 72, 1), (2, 76, 1.5), (3.5, 74, 0.5), (4, 72, 1), (5, 71, 1), (6, 72, 2),
              (8, 69, 1), (9, 72, 1), (10, 77, 1.5), (11.5, 76, 0.5), (12, 74, 2)]


def player():
    # 5 - 12: player 1, the R36 Ultra. The groove starts; a new tune for Luna.
    stamp(5.0, 69, 76, 33); hit(5.0, 'flash, PLAYER 1')
    groove(5.0, [('Am', 2), ('F', 2), ('C', 2), ('G', 1)])
    melody(5.5, LUNA_THEME, 10)
    for i in range(3):
        blip(P2, 5.8 + i * 0.4, 81 + i * 2, 3, 8, 1); hit(5.8 + i * 0.4, 'stat row')
    nz(7.4, [10, 7, 4], 2); hit(7.4, 'QUEST')
    noise_sweep(11.0, 11.98, 12, 3, 2, 8)


def stage1():
    # 12 - 20: secure the original card. The size lands, the copy runs up, checks, then CLEAR.
    stage_start(12.0)
    groove(12.0, [('Am', 2), ('F', 2), ('C', 2), ('G', 2)], arp_v=4)
    blip(P2, 13.1, 81, 4, 10, 2); nz(13.1, [10, 7, 4], 2); hit(13.1, '48.8 GiB')
    for i in range(8):                   # the extraction bar fills
        blip(P1, 13.5 + i * 0.175, 69 + (0, 2, 3, 5, 7, 8, 10, 12)[i], 3, 8, 1); hit(13.5 + i * 0.175, 'copy')
    ding(15.0); hit(15.0, 'SAFE ON DISK')
    for i in range(2):
        blip(P1, 15.6 + i * 0.3, 76 + (0, 4)[i], 4, 10, 2); hit(15.6 + i * 0.3, 'check')
    ding(16.2, 88)
    for i in range(3):
        blip(P2, 16.5 + i * 0.15, 84 + (0, 3, 7)[i], 3, 7, 1); hit(16.5 + i * 0.15, 'partition')
    melody(17.0, [(0, 76, 1), (1, 74, 1), (2, 72, 1), (3, 71, 0.8)], 9)
    clear(18.5)
    roll(19.5, 19.98, 4, 11)


def choose():
    # 20 - 26: choosing a system. One loops and is set aside; ArchR is chosen.
    stage_start(20.0)
    groove(20.0, [('Am', 2), ('F', 2), ('G', 2)], arp_v=4)
    buzz(21.6, 0.25); hit(21.6, 'RESTARTS IN A LOOP')
    tri_drop(22.4, 40, 28, 6); nz(22.4, [12, 9, 6, 4, 2], 13); hit(22.4, 'SET ASIDE')
    blip(P2, 22.8, 88, 3, 9, 1); hit(22.8, 'cursor on ArchR')
    for i in range(2):
        blip(P1, 23.4 + i * 0.4, 79 + (0, 5)[i], 4, 10, 2); hit(23.4 + i * 0.4, 'check')
    stamp(24.4, 69, 76, 33); hit(24.4, 'WE CHOOSE ArchR')
    clear(25.4)
    roll(25.5, 25.98, 4, 11)


def stage2():
    # 20 - 28: a black screen. Dark Dm, then the screen lights on C.
    stage_start(20.0)
    groove(20.0, [('Dm', 2), ('Am', 2), ('E', 1)], drums='light', arp_v=4)
    tri_drop(20.6, 40, 21, 8); nz(20.6, [12, 9, 6, 4, 2], 13); hit(20.6, 'NOTHING AT ALL')
    blip(P2, 24.4, 88, 3, 8, 1); hit(24.4, 'ARCH R FLASHER')
    roll(24.0, 24.98, 4, 12)
    stamp(25.0, 72, 79, 36); hit(25.0, 'screen comes alive')
    groove(25.0, [('C', 1), ('G', 1), ('Am', 1), ('G', 1)], arp_v=5)
    melody(25.5, [(0, 79, 1), (1, 76, 1), (2, 72, 1), (3, 74, 2)], 10)
    clear(26.5)


def stage3():
    # 28 - 34: the keyboard. Hub: buzz. Adapter: ding.
    stage_start(28.0)
    groove(28.0, [('F', 2), ('G', 2), ('Am', 2)])
    buzz(29.2, 0.45, 38); hit(29.2, 'hub fails')
    ding(31.3, 86); hit(31.3, 'adapter works')
    melody(30.0, [(0, 72, 0.5), (0.5, 74, 0.5), (1, 76, 1)], 9)
    clear(32.4)
    roll(33.5, 33.98, 4, 11)


def stage4():
    # 34 - 42: find a terminal. Three keys, the screen goes black (music drops), then text mode.
    stage_start(34.0)
    for i in range(3):
        key(34.5 + i * 0.15, 12); hit(34.5 + i * 0.15, 'key')
    groove(34.0, [('Am', 1)], arp_v=4)
    tri_drop(35.0, 45, 21, 10); nz(35.0, [10, 7, 4, 2], 13); hit(35.0, 'black screen')
    for t in (35.5, 36.0, 36.5):                              # only a ticking clock
        tick(t, 5); blip(P2, t, 57, 3, 4, 0)
    roll(36.5, 36.98, 3, 10)
    stamp(37.0, 69, 76, 33); hit(37.0, 'TEXT MODE')
    groove(37.0, [('Am', 2), ('F', 2), ('G', 1)])
    blip(P1, 37.6, 93, 3, 9, 1); hit(37.6, 'prompt')
    melody(38.0, [(0, 76, 1), (1, 77, 1), (2, 79, 2)], 9)
    blip(P2, 38.6, 84, 3, 8, 1); hit(38.6, 'AZERTY')
    clear(40.6)
    roll(41.5, 41.98, 5, 12)


BOSS_RIFF = [(0, 64, 0.5), (0.5, 64, 0.5), (1, 65, 0.5), (1.5, 64, 0.5), (2, 62, 0.5), (2.5, 64, 1), (3.5, 59, 0.5)]


def boss():
    # 42 - 60: the boss. E phrygian ostinato, double time; three patch hits; a major victory.
    stamp(42.0, 52, 53, 28, 15); hit(42.0, 'BOSS')
    ostinato(42.0, 47.5, 28)
    for k in range(2):
        melody(42.0 + 2 * k, BOSS_RIFF, 9, duty=0)
    for a, b, ch in chords_at(42.0, [('E', 2), ('F', 2), ('E', 1.5)]):
        chord_arp(P2, a, b, ROOT[ch] + 36, (0, 4, 7) if ch == 'E' else (0, 4, 7), 4, 0, rate=2)
    double_time(42.0, 47.5, 12, snare_on=False)
    buzz(43.3, 0.3, 40, 11); hit(43.3, 'wi-fi none')
    nz(45.4, [11, 8, 5, 3], 3); hit(45.4, 'INVISIBLE')
    stamp(47.5, 53, 64, 29, 13); hit(47.5, 'pin 2 compare')
    ostinato(47.5, 53.0, 28)
    for a, b, ch in chords_at(47.5, [('F', 0.5), ('E', 2), ('F', 1), ('E', 2)]):
        chord_arp(P2, a, b, ROOT[ch] + 36, (0, 4, 7), 4, 0, rate=2)
    double_time(47.5, 52.0, 12)
    melody(48.0, BOSS_RIFF, 10, duty=0); melody(50.5, BOSS_RIFF[:4], 10, duty=0)
    blip(P2, 48.4, 76, 4, 9, 1); hit(48.4, 'ArchR box')
    stamp(50.2, 64, 71, 28, 14); hit(50.2, 'LISTENING')
    roll(52.0, 52.98, 4, 14, gap0=5, gap1=1)
    noise_sweep(52.0, 52.98, 14, 4, 2, 8)
    # the three patches: each one a hit and a step up the chord ladder
    for t0, (m1, m2, root, prog) in zip((53.0, 54.8, 56.6),
                                        ((69, 76, 33, 'Am'), (72, 77, 29, 'F'), (74, 79, 31, 'G'))):
        stamp(t0, m1, m2, root, 15); hit(t0, f'PATCH ({prog})')
    for a, b, ch in ((53.0, 54.8, 'Am'), (54.8, 56.6, 'F'), (56.6, 58.2, 'G')):
        ostinato(a + 0.6, b, ROOT[ch])
        chord_arp(P2, a + 0.6, b, ROOT[ch] + 36, IVS[ch], 5, 1, rate=2)
        double_time(a + 0.5, b, 12)
        note(P1, a + 0.7, b - a - 0.75, ROOT[ch] + 43, 9, 2, env=E_swell(6, 11), vib=0.2, vib_delay=12, release=0)
    roll(57.7, 58.18, 6, 14, gap0=2, gap1=1)
    # victory: A major
    hit_all(58.2, 73, 76, 33, 15, tau=20, dur=0.9, cym='crash', tri_hold=0.8)
    clear(58.25)
    for i, m in enumerate((69, 73, 76, 81, 76, 81, 85)):
        note(P1, 58.75 + i * 0.125, 0.11, m, 12, 2, env=E_exp(6), release=0)
    bass8(59.0, 59.98, 33)
    hats(59.0, 59.98, 0.25, 4, 2)


def router():
    # 60 - 68: the router. Stop-time: an error, a suspended wait, the stamp "11", then the groove.
    stage_start(60.0)
    typing(60.4, 32, 'AP is in CSA process, reject auth', lambda t: tick(t, 4))
    buzz(61.4, 0.5, 41, 13); hit(61.4, 'CSA error')
    chord_arp(P2, 61.9, 63.9, 62, (0, 5, 7, 12), 4, 0, env=E_swell(2, 5), rate=3)   # the wait: Dsus4
    note(P1, 62.0, 1.9, 74, 6, 0, env=E_swell(3, 7), vib=0.15, vib_delay=20, release=0)
    tri(63.0, 0.9, 26)
    nz(64.0, [9, 6, 4, 2], 1); hit(64.0, 'strike AUTO')
    stamp(64.4, 76, 81, 33, 15); hit(64.4, 'STAMP 11')
    groove(65.0, [('C', 1), ('G', 1), ('Am', 1), ('G', 1)])
    melody(65.0, [(0, 76, 1), (1, 79, 1), (2, 81, 2), (4, 79, 1), (5, 74, 1)], 10)
    hit(65.0, 'CONNECTED')
    clear(66.5)


def ssh():
    # 68 - 76: log in from the PC. A build, the typed command, Enter, and HELLO, LUNA.
    stage_start(68.0)
    groove(68.0, [('Am', 1), ('F', 1), ('G', 0.5)], drums='light')
    typing(70.5, 10, '$ ssh luna', lambda t: key(t, 9))
    for i in range(5):
        tri(70.5 + i * 0.2, 0.18, 33 + i * 2, 0.7)
    roll(70.5, 71.58, 3, 11, gap0=6, gap1=2)
    key(71.6, 14); hit(71.6, 'Enter')
    for i, m in enumerate((81, 84, 88, 91)):
        blip(P2, 71.65 + i * 0.12, m, 3, 9, 1)
    blip(P1, 72.0, 93, 3, 10, 1); hit(72.0, 'Luna prompt')
    # 72.5 the payoff: the trailer theme on C, at full voice
    hit_all(72.5, 72, 79, 36, 15, tau=20, dur=0.8, cym='crash', tri_hold=0.3); hit(72.5, 'STAMP HELLO, LUNA.')
    groove(73.0, [('F', 1), ('G', 1), ('Am', 0.75)])
    for t, m, d in [(73.0, 76, 0.75), (73.75, 69, 0.25), (74.0, 72, 0.5), (74.5, 76, 0.5), (75.0, 79, 0.75)]:
        note(P1, t, d - 0.02, m, 13, 2, vib=0.2 if d >= 0.5 else 0.0)
    noise_sweep(75.25, 75.98, 10, 2, 3, 9)


def result():
    # 76 - 82: STORY 1 CLEAR. The level-clear fanfare, the eight pips, then a quiet bed for reading.
    for i, m in enumerate((72, 76, 79, 84)):
        note(P1, 76.0 + i * 0.1, 0.1, m, 13, 2, env=E_sus, release=0)
    note(P1, 76.4, 0.55, 84, 13, 2, env=E_exp(20), vib=0.2, release=0)
    note(P2, 76.0, 0.9, 76, 9, 1, env=E_exp(25), arp=[0, 3, 7], release=0)
    tri(76.0, 0.9, 36); crash(76.0, 12); kick(76.0, 13, drop=False); hit(76.0, 'STORY 1 CLEAR')
    for i in range(8):
        blip(P2, 76.6 + i * 0.08, 72 + (0, 2, 4, 5, 7, 9, 11, 12)[i], 3, 8, 2); hit(76.6 + i * 0.08, 'pip')
    groove(77.0, [('F', 2), ('G', 2), ('Am', 1)], drums='light', arp_v=4, hat_v=3)
    melody(78.0, [(0, 72, 2), (2, 71, 2), (4, 69, 2)], 7)
    roll(81.0, 81.98, 4, 12)


def finale():
    # 82 - 88: the end card, as in the trailer: theme cadence, the A-minor chord rings and fades.
    for t0, t1, ch in ((82.0, 83.0, 'Am'), (83.0, 83.5, 'F'), (83.5, 84.0, 'G')):
        bass8(t0, t1, ROOT[ch])
        chord_arp(P2, t0, t1, ROOT[ch] + 24, IVS[ch], 6, 1)
    for t, m, d in ((82.0, 76, 0.75), (82.75, 69, 0.25), (83.0, 72, 0.5), (83.5, 71, 0.25), (83.75, 74, 0.25)):
        note(P1, t, d - 0.02, m, 14, 2, vib=0.25 if d >= 0.5 else 0.0)
    hats(82.0, 84.0, 0.25, 5, 2)
    for t in (82.0, 82.5, 83.0, 83.5):
        kick(t, 13, drop=t != 82.0)
    snare(82.5, 12); snare(83.5, 13)
    hit_all(82.0, None, None, 33, 15, cym='crash', tri_hold=0.15); hit(82.0, 'END CARD')
    note(P1, 84.0, 3.4, 69, 14, 2, env=E_fade(60, 0), vib=0.2, vib_delay=20, release=0)
    note(P2, 84.0, 3.4, 72, 9, 1, env=E_fade(60, 0), arp=[0, 4], arp_rate=1, release=0)
    tri(84.0, 1.6, 33)
    crash(84.0, 12, 80); kick(84.0, 14, drop=False); hit(84.0, 'final chord')
    for j, t in enumerate((84.5, 85.1667, 85.8333, 86.5)):   # PRESS START blinks (steal P2)
        blip(P2, t, 88, 3, max(2, 9 - 2 * j), 1); blip(P2, t + 0.05, 93, 4, max(2, 9 - 2 * j), 1)


def render():
    global OFF
    for f in (title, player, stage1, choose):
        f()
    OFF = 6.0                            # the rest keeps its original times, 6 s later
    for f in (stage2, stage3, stage4, boss, router, ssh, result, finale):
        f()
    x = A.render()
    n = int(round(DUR * SR))
    x = np.concatenate([x, np.zeros(max(0, n - len(x)))])[:n]
    x *= 10 ** (-1.1 / 20) / np.abs(x).max()          # plain peak normalisation, as the trailer
    ramp = min(n, 480)
    x[-ramp:] *= np.linspace(1, 0, ramp)
    return x


def write_wav(path, x):
    y = np.clip(np.round(x * 32767), -32768, 32767).astype('<i2')
    st = np.repeat(y[:, None], 2, axis=1)
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(st.tobytes())


def main():
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / 'music.wav'
    x = render()
    write_wav(out, x)
    (out.parent / 'hits.json').write_text(json.dumps(sorted(HITS), indent=1) + '\n')
    print(f'wrote {out}: {len(x) / SR:.3f} s, peak {20 * np.log10(np.abs(x).max()):.2f} dBFS')


if __name__ == '__main__':
    main()
