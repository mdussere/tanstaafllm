"""TANSTAAFLLM soundtrack for a 2A03 (NES) sound chip: four voices, mono, 60 Hz frames.

Run:  uv run --project <repo> python score.py OUT.wav   (also writes hits.json beside OUT.wav)
Writes music.wav (86.50 s, 48 kHz, 16-bit; the mono chip output on both channels) and hits.json.

Channels:  P1 = lead (pulse), P2 = harmony, fast-arpeggio chords and echo (pulse),
           TRI = bass, kick and tom drops (triangle), NOISE = drums and hits (LFSR noise).
Sound effects steal a channel: the music on it drops out while the effect plays.
120 BPM (the picture's beat: 30 frames), A minor. Times are output seconds of the final cut.
"""
import json
import pathlib
import sys
import wave

import numpy as np

from nes import APU, SR

HERE = pathlib.Path(__file__).resolve().parent
DUR = 86.5
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


# ============================================================= the score
def attract():
    # I. Attract mode (0 - 7.0): arcade at rest, mysterious.
    notes = [57, 64, 71, 72, 76, 72, 71, 64]
    for k in range(15):                                   # slow 12.5 % arpeggio, Am9
        note(P2, k * 0.25, 0.24, notes[k % 8], 4 + (k > 3), 0, env=E_exp(9), release=0)
    for t in (0.0, 0.5):                                  # INSERT COIN blinks
        blip(P1, t, 93, 3, 4, 1)
    note(P1, 0.62, 0.36, 86, 3, 1, env=E_sus, slide=-10, release=0)      # the coin drops
    coin(P1, 1.0); hit(1.0, 'coin, CREDIT 01')
    typing(1.15, 30, "THERE AIN'T NO SUCH THING" + "AS A FREE " + "LUNCH" + ".", lambda t: tick(t, 4))
    note(P1, 2.55, 0.14, 96, 11, 1, env=E_exp(6), slide=-24, release=0)  # red strike
    nz(2.55, [10, 7, 4, 2], 2); hit(2.55, 'strike LUNCH')
    hit_all(2.95, 57, 64, 33, 15, tau=14, dur=0.75, cym='boom', tri_hold=0.7); hit(2.95, 'STAMP LLM')
    note(P2, 3.3, 0.45, 88, 6, 1, env=E_exp(10), release=0)               # the credit fades in
    # hold 3.75 - 6.75: a suspended chord swelling into a riser
    note(P1, 3.75, 1.5, 71, 7, 2, env=E_swell(1, 7), vib=0.12, vib_delay=30, release=0)
    note(P1, 5.25, 1.73, 69, 11, 2, env=E_swell(5, 11), vib=0.15, vib_delay=10, release=0)
    chord_arp(P2, 3.75, 5.25, 57, (0, 2, 7, 12), v=6, duty=0, env=E_swell(2, 6), rate=2)
    chord_arp(P2, 5.25, 6.98, 64, (0, 5, 7, 12), v=9, duty=0, env=E_swell(3, 9), rate=2)
    tri(6.0, 0.98, 28, slide=12)                         # the triangle joins only for the last climb
    noise_sweep(4.75, 6.0, 15, 6, 1, 4)
    roll(6.0, 6.98, 6, 13, gap0=4, gap1=2, per0=5, per1=2)


THEME = [(7.0, 76, 0.75), (7.75, 69, 0.25), (8.0, 72, 0.5), (8.5, 76, 0.5),
         (9.0, 77, 0.75), (9.75, 76, 0.25), (10.0, 76, 0.25), (10.25, 72, 0.25), (10.5, 74, 1.25)]


def liftoff():
    # II. Lift-off (7.0 - 12.0): the drop, the full theme.
    for t, m, d in THEME:
        note(P1, t, d - 0.02, m, 14, 2, vib=0.25 if d >= 0.5 else 0.0)
    chord_arp(P2, 7.0, 9.0, 57, IVS['Am'], 6, 1)
    chord_arp(P2, 9.0, 10.5, 53, IVS['F'], 6, 1)
    chord_arp(P2, 10.5, 11.75, 55, IVS['G'] + (12,), 6, 1, env=E_fade(20, 3))
    bass8(7.0, 9.0, 33); bass8(9.0, 10.5, 29); tri(10.5, 1.25, 31)
    hats(7.0, 10.75, 0.25, 5, 2)
    for b in range(8):
        t = 7.0 + 0.5 * b
        kick(t, 14 if b == 0 else 12)
        if b % 2:
            snare(t, 13)
    crash(7.0, 15); hit(7.0, 'CUT key art')
    hats(10.75, 11.75, 0.125, 3, 2)                       # hold: the hats keep time, the theme note rings
    kick(11.0, 8, drop=False)
    for k, t in enumerate((11.75, 11.8333, 11.9167)):
        snare(t, 9 + 2 * k, 5)
    tri_drop(11.75, 52, 40, 5); tri_drop(11.875, 47, 35, 5, then='halt')


def player1():
    # III. Player 1 (12.0 - 22.0): playful groove; a blip per stat; half time under the mission.
    for bar, ch in ((12.0, 'C'), (14.0, 'G')):
        r = ROOT[ch]
        for e, off in ((0, 0), (2, 12), (3, 0), (4, 0), (6, 12), (7, 7)):
            tri(bar + e * 0.25, 0.25, r + off, 0.6)
        for e in (1, 3, 5, 7):                            # offbeat chord "pah"s
            chord_arp(P2, bar + e * 0.25, bar + e * 0.25 + 0.12, r + 24, IVS[ch], 5, 0)
        hats(bar, bar + 2.0, 0.25, 4, 2)
        for e in (0, 3, 4):
            kick(bar + e * 0.25, 12)
        for e in (2, 6):
            snare(bar + e * 0.25, 11)
    for bar, shift in ((12.0, 0), (14.0, -5)):
        for e, m in ((0, 79), (1, 76), (3, 79), (4, 81), (5, 79), (6, 76)):
            note(P1, bar + e * 0.25, 0.17, m + shift, 10, 1, env=E_exp(7), release=0)
    crash(12.0, 9); hit(12.0, 'CUT player 1')
    for i, m in enumerate((84, 86, 88, 91, 93, 96)):     # six stats, six blips (they steal P2)
        blip(P2, 12.5 + 0.5 * i, m, 6, 11 if i in (1, 5) else 9, 2, slide=2)
    # half time under the mission text
    for bar, ch in ((16.0, 'Am'), (18.0, 'F')):
        r = ROOT[ch]
        tri(bar, 0.7, r, 0.9); tri(bar + 0.75, 0.25, r, 0.6); tri(bar + 1.0, 0.5, r + 12, 0.85)
        tri(bar + 1.5, 0.3 if bar == 18.0 else 0.5, r + 7, 0.8)
        chord_arp(P2, bar, min(bar + 2.0, 19.75), r + 24, IVS[ch], 4, 1, env=E_fade(10, 2))
        hats(bar, min(bar + 2.0, 19.8), 0.25, 3, 1)
        kick(bar, 12); kick(bar + 0.75, 8, drop=False); snare(bar + 1.0, 12)
    for t, m, d in ((16.0, 76, 0.9), (17.0, 72, 0.45), (17.5, 74, 0.45), (18.0, 72, 0.9), (19.0, 69, 0.75)):
        note(P1, t, d, m, 11, 2, vib=0.2)
    blip(P2, 16.0, 76, 9, 9, 1, slide=12)                 # the dialogue box opens
    typing(16.2, 40, 'MISSION: MAKE IT AUTONOMOUS.', lambda t: blip(P2, t, 96, 1, 5, 0))
    note(P2, 17.0, 0.3, 88, 6, 1, env=E_exp(6), release=0)
    note(P2, 18.0, 0.3, 91, 6, 1, env=E_exp(6), release=0)
    # hold 19.8 - 21.8: breathe on a bass pedal, then a fill
    for k in range(8):
        tri(20.0 + 0.25 * k, 0.25, 28 if k % 4 else 40, 0.45 + 0.07 * (k % 4))
    note(P2, 19.8, 1.2, 64, 6, 0, env=lambda k, n, v: 2 + 4 * np.sin(np.pi * k / n), arp=[0, 5, 7, 12],
         arp_rate=3, release=0)
    hats(20.0, 21.0, 0.5, 2, 2)
    note(P1, 21.0, 0.97, 64, 7, 1, env=lambda k, n, v: 6 + 6 * k / n, slide=12, release=0)  # pickup climbs
    roll(21.0, 21.97, 3, 13, gap0=8, gap1=3, per0=7, per1=4)
    for k, t in enumerate((21.5, 21.625, 21.75, 21.875)):
        tri_drop(t, 55 - 3 * k, 43 - 3 * k, 6, then='halt' if k == 3 else None)


def prices():
    # IV. Every price (22.0 - 27.5): stop-time slams; the hold is a ringing low drone.
    for t, m1, m2, r, lab in ((22.0, 69, 76, 33, 'SLAM 1'), (23.0, 65, 72, 29, 'SLAM 2'), (24.0, 67, 74, 31, 'SLAM 3')):
        hit_all(t, m1, m2, r, 15, tau=30, dur=0.97, tri_hold=0.88); hit(t, lab)
        for k in range(1, 4):                             # the price meter ticks after each slam
            hat(t + 0.25 * k, 5, weak=True)
    hit_all(25.0, 68, 71, 28, 12, tau=18, dur=0.85, cym=None, tri_hold=2.3); hit(25.0, 'ON LUNA')
    clank(25.0, 11)
    # hold 25.88 - 27.38: low drone (the triangle's E), a minor-second rub above, drums out
    note(P1, 25.85, 1.53, 76, 4, 2, env=E_swell(2, 5), vib=0.1, vib_rate=3, release=0)
    note(P2, 25.85, 1.53, 77, 4, 2, env=E_swell(1, 4), vib=0.1, vib_rate=2.5, release=0)
    noise_sweep(26.3, 27.38, 15, 12, 1, 3)


def pong():
    # V. One word (27.5 - 32.0): near silence, terminal clicks, the counter; the stamp brings the groove back.
    tri_drop(27.5, 40, 24, 4, then='halt'); nz(27.5, [6, 3, 1], 13); hit(27.5, 'CUT pong')
    note(P1, 27.5, 0.75, 45, 2, 0, env=E_sus, release=0)
    typing(27.7, 16, '> pong', lambda t: key(t, 8))
    key(28.2, 10)                                         # enter
    f0, f1 = F(28.25), F(29.4)
    for k in range(f1 - f0):                              # the counter: a rising glide that slows down
        p = k / (f1 - f0)
        cp = 1 - (1 - p) ** 3
        A.pulse(P1, f0 + k, 60 + 24 * cp, 3, 0)
    last = -1
    for v in range(590, 17701, 590):                      # ticks at each 590 tokens
        p = 1 - (1 - v / 17700) ** (1 / 3)
        f = F(28.25 + 1.15 * p)
        if f != last:
            A.pulse(P2, f, 72 + 24 * v / 17700, 6, 1)
            last = f
    note(P1, 29.4, 0.65, 81, 12, 1, env=E_exp(14), release=0); hit(29.4, 'counter lands')
    note(P2, 29.5, 0.55, 81, 5, 1, env=E_exp(12), release=0)          # its echo
    hit_all(30.1, 57, 60, 33, 15, tau=12, dur=0.4, cym='boom', tri_hold=0.35); hit(30.1, 'STAMP NO FREE LLM')
    bass8(30.5, 32.0, 33)
    chord_arp(P2, 30.5, 32.0, 57, IVS['Am'], 5, 1)
    hats(30.5, 32.0, 0.25, 4, 2)
    for t in (30.5, 31.0, 31.5):
        kick(t, 12)
    snare(31.0, 10); snare(31.75, 8, 4); snare(31.875, 11, 5)


def select():
    # VI. Select (32.0 - 44.0): menu theme; each card adds a layer, cheap to expensive.
    crash(32.0, 7); hit(32.0, 'CUT select')
    note(P1, 32.0, 0.4, 48, 6, 1, env=E_sus, slide=24, release=0)   # the cards rise
    chords = [(32.0, 34.0, 'Am'), (34.0, 36.0, 'F'), (36.0, 38.0, 'G'), (38.0, 40.0, 'Am'), (40.0, 41.0, 'F'),
              (41.0, 42.0, 'G')]
    for t0, t1, ch in chords:
        r = ROOT[ch]
        if t1 > 32.5:                                     # Buttons: triangle bass and kick
            bass8(max(t0, 32.5), t1, r, octave=t0 >= 35.5)
        if t1 > 34.0:                                     # Mycroft: the arpeggio
            pat = [0, 1, 2, 3, 2, 1]
            notes = [r + 24 + i for i in IVS[ch]] + [r + 36]
            t, k = max(t0, 34.0), 0
            while t < t1 - 1e-6:
                note(P2, t, 0.12, notes[pat[k % 6]], 7 if t0 < 37 else 8, 0 if t0 < 37 else 1, env=E_exp(5),
                     release=0)
                k += 1
                t = max(t0, 34.0) + 0.125 * k
    t = 32.5
    while t < 41.99:
        kick(t, 12)
        t += 0.5
    hats(35.5, 42.0, 0.125, 4, 2, weak=True)              # Mike: hats and snare
    for k in range(13):
        t = 35.5 + 0.5 * k
        if (t - 32.0) % 1.0 > 0.4 and t < 42.0:
            snare(t, 12)
    for t, (a, b), lab in ((32.5, (79, 86), 'BUTTONS'), (34.0, (81, 88), 'MYCROFT'), (35.5, (83, 90), 'MIKE')):
        blip(P1, t, a, 3, 10); blip(P1, t + 0.05, b, 5, 10); hit(t, 'select ' + lab)
    coin(P2, 37.0, 12); hit(37.0, 'select MANNIE')       # Mannie: the expensive one, and the theme
    mel = [(37.0, 64, 0.25), (37.25, 69, 0.25), (37.5, 71, 0.25), (37.75, 72, 0.25),
           (38.0, 76, 0.75), (38.75, 69, 0.25), (39.0, 72, 0.5), (39.5, 76, 0.5),
           (40.0, 77, 0.75), (40.75, 76, 0.25), (41.0, 74, 0.5), (41.5, 71, 0.5)]
    for t, m, d in mel:
        note(P1, t, d - 0.02, m, 15 if t == 39.0 else 13, 2, vib=0.25 if d >= 0.5 else 0.0)
    hit_all(39.0, None, 81, 33, 14, tau=14, dur=0.5, tri_hold=0.0); hit(39.0, 'BANNER')
    blip(P2, 39.8, 88, 4, 7, 1); blip(P2, 40.6, 84, 4, 7, 1)
    # hold 41.8 - 43.8: the theme resolves on A minor
    note(P1, 42.0, 1.75, 69, 13, 2, env=E_fade(30, 5), vib=0.25)
    chord_arp(P2, 42.0, 43.8, 57, IVS['Am'] + (12,), 6, 1, env=E_fade(20, 1))
    tri(42.0, 1.75, 33)
    kick(42.0, 13); crash(42.0, 9, 30)
    hats(42.5, 43.0, 0.25, 3, 2)
    noise_sweep(43.0, 43.98, 15, 7, 2, 9)


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


def boss():
    # VII. Boss fight (44.0 - 57.5): dark minor, alarm, double time; the pitch rises as the bar fills.
    ostinato(44.0, 48.0, 33)
    double_time(44.0, 45.5, 13)
    double_time(45.5, 47.0, 10, snare_on=False)
    roll(47.0, 47.98, 5, 14, gap0=8, gap1=2, per0=7, per1=3)
    for j in range(12):                                   # alarm on the blinking BOSS FIGHT (steals P2)
        t = 44.0 + j / 3 + 1 / 6
        v = 9 if t < 45.5 else max(1, 9 - 3 * (t - 45.5))
        note(P2, t, 10 / 60, 81 if j % 2 else 87, v, 2, env=E_sus, release=0)
    hit_all(44.0, 57, 58, 33, 15, tau=16, dur=0.55, cym='boom', tri_hold=0.0); hit(44.0, 'BOSS FIGHT')
    hit_all(44.6, 58, None, 34, 13, tau=10, dur=0.35, cym='crash', tri_hold=0.0); hit(44.6, 'VS')
    for t, m, d in ((45.5, 64, 0.75), (46.25, 65, 0.25), (46.5, 64, 0.5), (47.0, 62, 0.5), (47.5, 63, 0.45)):
        note(P1, t, d - 0.02, m, 11, 2, vib=0.2)
    # pressure: where 983 MiB go
    steps = [(48.0, 50.0, 33), (50.0, 51.0, 35), (51.0, 53.5, 36), (53.5, 53.9, 38), (53.9, 55.3, 40)]
    for i, (t0, t1, r) in enumerate(steps):
        ostinato(t0, t1, r)
        double_time(t0, t1, 12 + min(i, 3))
        chord_arp(P2, t0, t1, r + 24, (0, 3, 7), 4 + i, 1)
        note(P1, t0, t1 - t0 - 0.02, r + 36, 9 + 1.5 * i, 2, env=E_sus, vib=0.2, release=0)
    hit_all(48.0, None, 69, 33, 14, tau=10, dur=0.3, tri_hold=0.0); hit(48.0, 'CUT pressure')
    hit(50.0, 'system fills'); hit(51.0, 'Claude Code fits'); hit(53.5, 'Mike fills')
    crash(51.0, 10, 25); kick(51.0, 13)
    crash(50.0, 8, 20); crash(53.5, 11, 15)
    for t0, t1, nb, m0 in ((50.0, 50.4, 18, 72), (51.0, 51.3, 10, 76), (53.5, 53.8, 12, 82)):   # bar segments
        last = -1
        for j in range(1, nb + 1):
            p = 1 - (1 - j / nb) ** (1 / 3)
            f = F(t0 + (t1 - t0) * p)
            if f != last:
                A.pulse(P2, f, m0 + 10 * j / nb, 8, 0)
                last = f
    for k, m in enumerate((84, 88, 91)):                  # FITS
        blip(P2, 51.3 + 0.05 * k, m, 3 if k < 2 else 8, 11, 1)
    hit_all(53.9, 76, 77, 28, 15, tau=24, dur=0.9, cym='crash', tri_hold=0.0); hit(53.9, 'RIGHT AT THE LIMIT')
    note(P1, 54.8, 0.48, 76, 12, 2, vib=0.3, release=0)
    blip(P2, 53.8, 93, 4, 10, 2)
    for j in range(14):                                   # the red blink: alarm at 8 Hz
        t = 54.0 + 0.25 * j
        v = 9 if t < 55.3 else max(0, 9 - 7 * (t - 55.3))
        if v >= 1:
            note(P2, t, 6 / 60, 88 if j % 2 else 89, v, 2, env=E_sus, release=0)
    # hold 55.3 - 57.3: decays to a heartbeat
    note(P1, 55.3, 1.9, 64, 7, 2, env=E_fade(10, 0), vib=0.1, vib_rate=3, release=0)
    for t in (55.75, 56.75):
        tri_drop(t, 40, 26, 5, then='halt'); tri_drop(t + 0.2, 36, 24, 4, then='halt')
        nz(t, [4, 2], 13); nz(t + 0.2, [3, 1], 13)
    noise_sweep(57.25, 57.48, 10, 2, 2, 8)


def cell():
    # VIII. The cell (57.5 - 73.0): steady march; tiles as a rising arpeggio; one stamp per rule.
    PAH = {'Am': (72, 76), 'F': (72, 77), 'C': (76, 79), 'G': (74, 79)}
    march = [(57.5, 59.5, 'Am'), (59.5, 60.5, 'F'), (62.5, 63.5, 'G'), (64.5, 65.5, 'Am'), (66.5, 67.5, 'C'),
             (68.5, 69.5, 'Am'), (71.0, 71.8, 'F')]
    holds = [(60.5, 62.5, 'C'), (63.5, 64.5, 'G'), (65.5, 66.5, 'F'), (67.5, 68.5, 'G'), (69.5, 71.0, 'F'),
             (71.8, 73.0, 'G')]
    for t0, t1, ch in march:
        b = 0
        while t0 + b * 0.5 < t1 - 1e-6:
            t = t0 + b * 0.5
            beat = int(round((t - 57.5) / 0.5)) % 4
            if beat in (0, 2):
                tri(t, 0.5, ROOT[ch] + (0 if beat == 0 else 7), 0.75)
                kick(t, 12, drop=False)
            else:
                tri(t, 0.5, ROOT[ch] + 12, 0.35)
                snare(t - 0.0625, 4, 3); snare(t, 12, 7); snare(t + 0.25, 5, 3)
                hi, lo = PAH[ch]
                note(P1, t, 0.2, lo, 8, 1, env=E_exp(6), release=0)
                note(P2, t, 0.2, hi, 8, 1, env=E_exp(6), release=0)
            b += 1
    for t0, t1, ch in holds:                              # holds as sustained chords
        hi, lo = PAH[ch]
        note(P1, t0, t1 - t0, lo, 8, 2, env=E_fade(int((t1 - t0) * 40), 5), vib=0.12, vib_delay=20, release=0)
        note(P2, t0, t1 - t0, hi, 7, 1, env=E_fade(int((t1 - t0) * 40), 4), vib=0.12, vib_delay=26, release=0)
        tri(t0, t1 - t0, ROOT[ch], 0.97)
        k = 0
        while t0 + k * 1.0 < t1 - 0.3:
            nz(t0 + k * 1.0, [5, 3, 2, 1], 12)            # a soft pulse keeps the march alive
            k += 1
    for i, m in enumerate((69, 72, 76, 79, 81, 84)):     # six tiles pop in (P1), with an echo on P2
        t = 57.5 + 0.5 * i
        note(P1, t, 0.3, m, 12, 1, env=E_exp(8), release=0)
        note(P2, t + 0.15, 0.25, m, 5, 1, env=E_exp(6), release=0)
    kick(57.5, 13); crash(57.5, 9, 30); hit(57.5, 'CUT the cell')
    for i in range(6):                                    # the speech bubbles pop: a two-note chirp each (P2)
        t = 58.5 + 0.3 * i
        blip(P2, t, 84 + 2 * (i % 3), 3, 9, 1); blip(P2, t + 0.06, 91 + 2 * (i % 3), 4, 9, 1)
        hit(t, f'bubble {i + 1}')
    for i, (t, ch) in enumerate(((62.5, 'G'), (64.5, 'Am'), (66.5, 'C'), (68.5, 'Am'), (71.0, 'F'))):
        hi, lo = PAH[ch]
        hit_all(t, lo, hi, ROOT[ch], 14, tau=10, dur=0.45, cym='crash' if i % 2 == 0 else None, tri_hold=0.4)
        snare(t, 15, 4)
        hit(t, f'RULE {i + 1}')
    for k, t in enumerate((72.75, 72.8125, 72.875, 72.9375)):
        snare(t, 7 + 2 * k, 4)


def opening():
    # IX. The opening (73.0 - 79.0): the cell is ready, the adventure begins; bright, major, short.
    crash(73.0, 12, 18); kick(73.0, 13); hit(73.0, 'CUT opening')
    for i, m in enumerate((72, 76, 79, 84, 88, 91)):     # six members hop onto the Moon (P1)
        t = 73.4 + 0.15 * i
        note(P1, t, 0.12, m, 11, 1, env=E_exp(6), slide=12, release=0)
    hit_all(74.0, 72, 79, 36, 15, tau=14, dur=0.6, cym='crash', tri_hold=0.5); hit(74.0, 'THE ADVENTURE BEGINS')
    prog = ((74.5, 75.5, 'C'), (75.5, 76.5, 'G'), (76.5, 77.5, 'Am'), (77.5, 78.5, 'F'))
    for t0, t1, ch in prog:
        bass8(t0, t1, ROOT[ch], gate=0.6)
        chord_arp(P2, t0, t1, ROOT[ch] + 24 if ROOT[ch] + 24 < 64 else ROOT[ch] + 12, IVS[ch], 5, 0)
        b = 0
        while t0 + b * 0.5 < t1 - 1e-6:
            kick(t0 + b * 0.5, 12, drop=False)
            if b % 2:
                snare(t0 + b * 0.5, 11, 6)
            b += 1
    hats(74.5, 78.5, 0.25, 4, 2)
    for t, m, d in ((74.5, 76, 0.5), (75.0, 79, 0.5), (75.5, 83, 0.75), (76.25, 81, 0.25), (76.5, 81, 0.5),
                    (77.0, 76, 0.5), (77.5, 77, 0.5), (78.0, 79, 0.5)):   # a rising fanfare (P1)
        note(P1, t, d - 0.02, m, 13, 2, vib=0.2 if d >= 0.5 else 0.0)
    roll(78.5, 78.98, 6, 14, gap0=4, gap1=2, per0=6, per1=3)
    tri_drop(78.5, 52, 40, 6); tri_drop(78.625, 49, 37, 6); tri_drop(78.75, 45, 33, 6)
    tri_drop(78.875, 43, 31, 6, then='halt')


def finale():
    # X. Doctrine (79 - 82.5): three stabs, then a roll and a riser to the top.
    for t, m1, m2, r, lab in ((79, 69, 76, 33, 'STAB 1'), (79.75, 65, 72, 29, 'STAB 2'), (80.5, 67, 74, 31, 'STAB 3')):
        hit_all(t, m1, m2, r, 15, tau=16, dur=0.7, cym='crash' if t != 79.75 else 'boom', tri_hold=0.6)
        hit(t, lab)
    bass8(81.25, 82, 31, octave=False, gate=0.5)
    note(P1, 81.2, 1.29, 67, 13, 2, env=E_swell(6, 13), slide=12, release=0)       # the riser climbs
    chord_arp(P2, 81.2, 82.49, 55, (0, 4, 7, 12), 9, 1, env=E_swell(4, 11))
    roll(81.2, 82.49, 4, 14, gap0=6, gap1=2, per0=7, per1=2)
    for k in range(4):
        tri_drop(82 + 0.125 * k, 50 + 3 * k, 38 + 3 * k, 6, then='halt' if k == 3 else None)
    # XI. Press start (82.5 - 86.5): theme cadence, the A-minor chord rings, blips.
    for t0, t1, ch in ((82.5, 83.5, 'Am'), (83.5, 84, 'F'), (84, 84.5, 'G')):
        bass8(t0, t1, ROOT[ch])
        chord_arp(P2, t0, t1, ROOT[ch] + 24, IVS[ch], 6, 1)
    for t, m, d in ((82.5, 76, 0.75), (83.25, 69, 0.25), (83.5, 72, 0.5), (84, 71, 0.25), (84.25, 74, 0.25)):
        note(P1, t, d - 0.02, m, 14, 2, vib=0.25 if d >= 0.5 else 0.0)
    hats(82.5, 84.5, 0.25, 5, 2)
    for t in (82.5, 83, 83.5, 84):
        kick(t, 13, drop=t != 82.5)
    snare(83, 12); snare(84, 13)
    hit_all(82.5, None, None, 33, 15, cym='crash', tri_hold=0.15); hit(82.5, 'END CARD')
    # the final A-minor chord: A on the triangle, A4 on P1, C5/E5 arpeggiated on P2; 4-bit fade to silence
    note(P1, 84.5, 1.9, 69, 14, 2, env=E_fade(30, 0), vib=0.2, vib_delay=20, release=0)
    note(P2, 84.5, 1.9, 72, 9, 1, env=E_fade(30, 0), arp=[0, 4], arp_rate=1, release=0)
    tri(84.5, 1.3, 33)
    crash(84.5, 12, 70); kick(84.5, 14, drop=False); hit(84.5, 'final chord')
    for j, t in enumerate((83.9, 84.5, 85.1667, 85.8333)):   # PRESS START blinks (steal P2)
        blip(P2, t, 88, 3, max(2, 9 - 2 * j), 1); blip(P2, t + 0.05, 93, 4, max(2, 9 - 2 * j), 1)
    hit(83.9, 'PRESS START')


def render():
    for f in (attract, liftoff, player1, prices, pong, select, boss, cell, opening, finale):
        f()
    x = A.render()
    n = int(round(DUR * SR))
    x = np.concatenate([x, np.zeros(max(0, n - len(x)))])[:n]
    peak_db = -1.1
    x *= 10 ** (peak_db / 20) / np.abs(x).max()          # plain peak normalisation
    ramp = min(n, 480)
    x[-ramp:] *= np.linspace(1, 0, ramp)                  # last 10 ms: land on zero
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
