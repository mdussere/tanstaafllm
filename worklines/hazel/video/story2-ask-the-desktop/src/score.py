"""TANSTAAFLLM story 2, "Ask the desktop" (Wyoh): soundtrack for a 2A03 (NES) sound chip, four voices, mono.

Run:  uv run --project <repo> python score.py OUT.wav   (also writes hits.json beside OUT.wav)
Writes 90.00 s, 48 kHz, 16-bit (the mono chip output on both channels).

Same chip, same tempo and same helpers as the trailer and story 1 scores (series unity):
P1 = lead, P2 = harmony / fast-arpeggio chords / effects, TRI = bass and kick drops,
NOISE = drums and hits. 120 BPM (0.5 s per beat, 2 s per bar), A minor. The trailer theme
opens the episode and returns at the payoff; a new "Wyoh" motif (E A B C, rising) plays
under the player screen. Times are seconds of the cut (no reading holds).
"""
import json
import pathlib
import sys
import wave

import numpy as np

from nes import APU, SR

HERE = pathlib.Path(__file__).resolve().parent
DUR = 90.0
A = APU(DUR)
P1, P2 = 0, 1
HITS = []


def F(t):
    """Frame of time t (16ths fall on 8/7-frame grooves, as in trackers)."""
    return int(np.floor(t * 60 + 0.5 + 1e-9))


def hit(t, label):
    HITS.append((round(t, 3), label))


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
THEME = [(1.25, 76, 0.75), (2.0, 69, 0.25), (2.25, 72, 0.5), (2.75, 76, 0.5),   # the trailer theme (score A)
         (3.25, 77, 0.5), (3.75, 76, 0.25), (4.0, 76, 0.25), (4.25, 72, 0.25), (4.5, 74, 0.45)]


def title():
    # 0 - 6: the series opener. A coin, the stamp, then the trailer theme over Am F G, and E into the player.
    blip(P2, 0.3, 88, 3, 7, 1); blip(P2, 0.35, 93, 4, 7, 1); hit(0.3, 'series line')
    note(P1, 0.62, 0.36, 86, 3, 1, env=E_sus, slide=-10, release=0)
    stamp(1.0, 57, 64, 33); hit(1.0, 'STAMP ASK THE DESKTOP')
    groove(1.0, [('Am', 2), ('F', 1), ('G', 1), ('E', 1)], drums='light', arp_v=5)
    for t, m, d in THEME + [(5.0, 71, 0.5), (5.5, 68, 0.45)]:
        note(P1, t, d - 0.02, m, 12, 2, vib=0.2 if d >= 0.5 else 0.0)
    roll(5.5, 5.98, 5, 12, gap0=3, gap1=2)


# The "Wyoh" motif: E A B C rising, then it settles (A minor, over Am F C G).
WYOH_THEME = [(0, 76, 1), (1, 81, 0.5), (1.5, 83, 0.5), (2, 84, 1.5), (3.5, 83, 0.5), (4, 81, 1), (5, 77, 1),
              (6, 79, 1), (7, 79, 0.5), (7.5, 76, 0.5), (8, 72, 1.5), (9.5, 74, 0.5), (10, 76, 2), (12, 74, 1), (13, 71, 1)]
WYOH_HEAD = WYOH_THEME[:4]


def player():
    # 6 - 14: player 2, Wyoh. The groove starts and the Wyoh motif plays.
    stamp(6.0, 69, 76, 33); hit(6.0, 'flash, PLAYER 2')
    groove(6.0, [('Am', 2), ('F', 2), ('C', 2), ('G', 2)])
    melody(6.5, WYOH_THEME, 10)
    for i in range(2):
        blip(P2, 7.4 + i * 0.4, 81 + i * 2, 3, 8, 1); hit(7.4 + i * 0.4, 'stat row')
    nz(8.2, [10, 7, 4], 2); hit(8.2, 'QUEST')
    noise_sweep(13.0, 13.98, 12, 3, 2, 8)


def stage1():
    # 14 - 20: the screenshot trap. Uneasy Am Dm E; each guess costs a coin.
    stage_start(14.0)
    groove(14.0, [('Am', 2), ('Dm', 2), ('E', 2)], arp_v=4)
    for t in (15.0, 15.5, 16.0):
        coin(P2, t, 9); blip(P1, t + 0.1, 64, 6, 9, 0, slide=5); hit(t, 'guess (a coin)')
    nz(14.9, [8, 5, 3], 2); hit(14.9, 'screenshots line')
    ding(17.0, 81); hit(17.0, 'ON PAPER: A DOM')
    melody(17.5, [(0, 76, 1), (1, 75, 1), (2, 76, 1)], 8)
    clear(18.5)
    roll(19.5, 19.98, 4, 11)


def stage2():
    # 20 - 28: HIOM. One scene, windows spill, REOPENED; the lesson kept as a stamp.
    stage_start(20.0)
    groove(20.0, [('F', 2), ('G', 2)], arp_v=4)
    for i in range(5):
        blip(P2, 21.6 + i * 0.15, 72 + (0, 3, 5, 7, 10)[i], 3, 8, 1); hit(21.6 + i * 0.15, 'window spills')
    buzz(22.5, 0.4, 40); tri_drop(22.5, 40, 26, 6); hit(22.5, 'REOPENED')
    groove(24.0, [('Am', 2), ('E', 1), ('Am', 1)])
    stamp(23.5, 69, 76, 33, 12); hit(23.5, 'STAMP WAIT FOR A NAMED CONDITION')
    melody(24.0, [(0, 76, 1), (1, 74, 0.5), (1.5, 72, 0.5), (2, 71, 1)], 9)
    clear(26.5)
    roll(27.5, 27.98, 4, 11)


def stage3():
    # 28 - 36: ask the one that exists. Bright C G Am F; four tiles, four rising blips.
    stage_start(28.0)
    groove(28.0, [('C', 2), ('G', 2), ('Am', 2), ('F', 2)])
    blip(P2, 28.9, 84, 3, 8, 1); hit(28.9, 'SWAY box')
    ding(29.3, 84); hit(29.3, 'UNMODIFIED')
    blip(P2, 29.7, 79, 3, 8, 1); hit(29.7, 'NO FORK')
    nz(30.3, [9, 6, 3], 2); hit(30.3, 'MEASURED ON luna-pi')
    melody(29.0, WYOH_HEAD, 9)
    for i, t in enumerate((31.0, 31.5, 32.0, 32.5)):
        blip(P1, t, 76 + (0, 3, 5, 8)[i], 4, 11, 2); hit(t, 'tile')
    ding(32.5, 88)
    melody(33.0, [(0, 84, 1), (1, 83, 1)], 9)
    clear(34.5)
    roll(35.5, 35.98, 4, 11)


def stage4():
    # 36 - 44: the MCP bridge. Query, answer, act, event; the 26 TOOLS stamp.
    stage_start(36.0)
    groove(36.0, [('Am', 2), ('F', 2), ('C', 2), ('G', 2)])
    for t, m, sl, lab in ((37.0, 72, 12, 'query'), (37.45, 84, -12, 'tree back'), (38.0, 76, 12, 'act'),
                          (39.0, 88, -12, 'event confirms')):
        blip(P2, t, m, 10, 9, 1, slide=sl); hit(t, lab)
    key(38.4, 10); hit(38.4, 'focus moves')
    stamp(40.0, 72, 79, 36); hit(40.0, 'STAMP 26 TOOLS')
    melody(40.5, [(0, 76, 1), (1, 77, 1), (2, 79, 1)], 8)
    clear(42.5)
    roll(43.5, 43.98, 5, 12)


BOSS_RIFF = [(0, 64, 0.5), (0.5, 64, 0.5), (1, 65, 0.5), (1.5, 64, 0.5), (2, 62, 0.5), (2.5, 64, 1), (3.5, 59, 0.5)]


def boss():
    # 44 - 52: the boss, the black panel. E phrygian ostinato; two hits; the panel lights on A major.
    stamp(44.0, 52, 53, 28, 15); hit(44.0, 'BOSS')
    ostinato(44.0, 48.5, 28)
    melody(44.0, BOSS_RIFF, 9, duty=0); melody(46.0, BOSS_RIFF, 10, duty=0)
    for a, b, ch in chords_at(44.0, [('E', 2), ('F', 2), ('E', 0.5)]):
        chord_arp(P2, a, b, ROOT[ch] + 36, (0, 4, 7), 4, 0, rate=2)
    double_time(44.0, 47.5, 12, snare_on=False)
    boom(45.0, 15); tri_drop(45.0, 40, 21, 8); hit(45.0, 'BLACK.')
    blip(P2, 45.6, 76, 4, 9, 1); hit(45.6, 'screenshots looked right')
    stamp(46.5, 53, 64, 29, 13); hit(46.5, 'NOT LOADED (hit 1)')
    roll(47.5, 48.48, 4, 14, gap0=5, gap1=1)
    noise_sweep(47.5, 48.48, 14, 4, 2, 8)
    # the driver loads: victory, A major
    hit_all(48.5, 73, 76, 33, 12, tau=20, dur=0.9, cym='crash', tri_hold=0.8); hit(48.5, 'LOADED, the panel lights')
    for i, m in enumerate((69, 73, 76, 81, 76, 81, 85)):
        note(P1, 48.9 + i * 0.125, 0.11, m, 12, 2, env=E_exp(6), release=0)
    ding(48.8, 88); hit(48.8, '1 passed')
    for a, b, ch in ((49.5, 50.5, 'D'), (50.5, 52.0, 'E')):
        bass8(a, b, ROOT[ch] - 12 if ch == 'D' else ROOT[ch])
        chord_arp(P2, a, b, ROOT[ch] + 24 if ch == 'D' else ROOT[ch] + 36, (0, 4, 7), 5, 1, rate=2)
    hats(49.5, 51.5, 0.25, 4, 2)
    clear(50.5)
    roll(51.5, 51.98, 4, 12)


def stage6():
    # 52 - 62: 17 buttons. Presses map to actions; then the agent presses FN+B and Mike answers.
    stage_start(52.0)
    groove(52.0, [('Am', 2), ('F', 2), ('G', 1.5)])
    for t in (53.5, 53.75, 54.0, 54.25):
        key(t, 11); blip(P2, t, 81, 3, 7, 1); hit(t, 'button -> action')
    key(54.6, 11); ding(54.8, 84); hit(54.8, 'SLATE')
    nz(54.5, [8, 5, 3], 2); hit(54.5, 'BUTTONS ONLY')
    stamp(57.5, 72, 79, 36, 13); hit(57.5, 'THE AGENT PRESSES')
    groove(57.5, [('C', 1.5), ('G', 1), ('Am', 2)])
    melody(58.0, WYOH_HEAD, 9)
    key(58.5, 13); key(58.6, 13); hit(58.5, 'FN+B')
    for i, m in enumerate((81, 84, 88)):
        blip(P2, 58.8 + i * 0.07, m, 3, 9, 1)
    ding(59.0, 86); hit(59.0, 'MIKE ANSWERS')
    clear(60.5)
    roll(61.5, 61.98, 4, 11)


def stage7():
    # 62 - 72: seven layers. Four checks, "verified", the game does not move (stop-time), then each layer in turn.
    stage_start(62.0)
    groove(62.0, [('Am', 2), ('F', 1)])
    for i, t in enumerate((63.5, 63.75, 64.0, 64.25)):
        blip(P1, t, 72 + (0, 2, 4, 5)[i], 3, 10, 2); hit(t, f'layer {i + 1} ok')
    ding(64.5, 84); hit(64.5, 'VERIFIED')
    buzz(65.0, 0.5, 40, 13); tri_drop(65.0, 40, 21, 10); hit(65.0, 'THE GAME DID NOT MOVE')
    chord_arp(P2, 65.5, 66.5, 62, (0, 5, 7, 12), 4, 0, env=E_swell(2, 5), rate=3)    # stop-time: Dsus4
    tick(65.5, 5); tick(66.0, 5)
    groove(66.5, [('Dm', 1), ('E', 1)], drums='light')
    for i, t in enumerate((67.0, 67.5)):
        blip(P1, t, 77 + 2 * i, 4, 11, 2); hit(t, f'layer {i + 5} ok')
    roll(67.5, 67.98, 4, 12)
    ding(68.0, 88); hit(68.0, 'layer 7: the game moves')
    stamp(68.5, 69, 76, 33); hit(68.5, 'STAMP ONLY THE LAST ONE')
    groove(69.0, [('F', 1), ('G', 1), ('Am', 1)])
    melody(69.0, [(0, 72, 1), (1, 74, 1), (2, 76, 2)], 9)
    clear(70.5)
    roll(71.5, 71.98, 4, 11)


def payoff():
    # 72 - 78: the agent asks, the tree comes back, the trailer theme at full voice on "ASK THE DESKTOP."
    stamp(72.0, 69, 76, 33, 12); hit(72.0, 'payoff')
    blip(P2, 72.3, 72, 12, 9, 1, slide=12); hit(72.3, 'sway_get_tree')
    for i in range(5):
        blip(P1, 72.9 + i * 0.12, 76 + (0, 3, 5, 7, 12)[i], 3, 10, 2); hit(72.9 + i * 0.12, 'tree node')
    hit_all(73.5, 69, 76, 33, 15, tau=20, dur=0.8, cym='crash', tri_hold=0.3); hit(73.5, 'STAMP ASK THE DESKTOP.')
    groove(73.5, [('Am', 2), ('F', 1), ('G', 1)])
    for t, m, d in THEME:
        note(P1, t + 72.5, d - 0.02, m, 13, 2, vib=0.2 if d >= 0.5 else 0.0)
    noise_sweep(77.25, 77.98, 10, 2, 3, 9)


def result():
    # 78 - 84: STORY 2 CLEAR. The level-clear fanfare, the seven pips, then a quiet bed for reading.
    for i, m in enumerate((72, 76, 79, 84)):
        note(P1, 78.0 + i * 0.1, 0.1, m, 13, 2, env=E_sus, release=0)
    note(P1, 78.4, 0.55, 84, 13, 2, env=E_exp(20), vib=0.2, release=0)
    note(P2, 78.0, 0.9, 76, 9, 1, env=E_exp(25), arp=[0, 3, 7], release=0)
    tri(78.0, 0.9, 36); crash(78.0, 12); kick(78.0, 13, drop=False); hit(78.0, 'STORY 2 CLEAR')
    for i in range(7):
        blip(P2, 78.6 + i * 0.08, 72 + (0, 2, 4, 5, 7, 9, 11)[i], 3, 8, 2); hit(78.6 + i * 0.08, 'pip')
    groove(79.0, [('F', 2), ('G', 2), ('Am', 1)], drums='light', arp_v=4, hat_v=3)
    melody(80.0, [(0, 76, 1), (1, 81, 0.5), (1.5, 83, 0.5), (2, 84, 2), (4, 81, 2)], 7)   # the Wyoh head, quietly
    roll(83.0, 83.98, 4, 12)


def finale():
    # 84 - 90: the end card, as in the trailer: theme cadence, the A-minor chord rings and fades.
    for t0, t1, ch in ((84.0, 85.0, 'Am'), (85.0, 85.5, 'F'), (85.5, 86.0, 'G')):
        bass8(t0, t1, ROOT[ch])
        chord_arp(P2, t0, t1, ROOT[ch] + 24, IVS[ch], 6, 1)
    for t, m, d in ((84.0, 76, 0.75), (84.75, 69, 0.25), (85.0, 72, 0.5), (85.5, 71, 0.25), (85.75, 74, 0.25)):
        note(P1, t, d - 0.02, m, 14, 2, vib=0.25 if d >= 0.5 else 0.0)
    hats(84.0, 86.0, 0.25, 5, 2)
    for t in (84.0, 84.5, 85.0, 85.5):
        kick(t, 13, drop=t != 84.0)
    snare(84.5, 12); snare(85.5, 13)
    hit_all(84.0, None, None, 33, 15, cym='crash', tri_hold=0.15); hit(84.0, 'END CARD')
    note(P1, 86.0, 3.4, 69, 14, 2, env=E_fade(60, 0), vib=0.2, vib_delay=20, release=0)
    note(P2, 86.0, 3.4, 72, 9, 1, env=E_fade(60, 0), arp=[0, 4], arp_rate=1, release=0)
    tri(86.0, 1.6, 33)
    crash(86.0, 12, 80); kick(86.0, 14, drop=False); hit(86.0, 'final chord')
    for j, t in enumerate((86.5, 87.1667, 87.8333, 88.5)):   # PRESS START blinks (steal P2)
        blip(P2, t, 88, 3, max(2, 9 - 2 * j), 1); blip(P2, t + 0.05, 93, 4, max(2, 9 - 2 * j), 1)


def render():
    for f in (title, player, stage1, stage2, stage3, stage4, boss, stage6, stage7, payoff, result, finale):
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
