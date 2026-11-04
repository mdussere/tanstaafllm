"""Music for the script-to-video pipeline: the series' 2A03 (NES chip) helpers, one cue per template, moods.

The helpers (envelopes, note writers, drums, sound effects, groove) are Story 2's score.py unchanged, so the
same calls give the same samples. Each template has a cue function (CUES[template_id]) that places its sound
at the scene's event times; stage scenes (T05) also take an ordered `events:` list from the script, whose
`fx` names are the FX table below. Times in a script are seconds from the scene start.

Run via build.py. Chip: nes.py (four voices, mono, 60 Hz frames, 48 kHz out).
"""
import json
import wave

import numpy as np

from nes import APU, SR

P1, P2 = 0, 1
A = APU(1.0)
HITS = []


def start(duration):
    """Begin a new score of `duration` seconds."""
    global A, HITS
    A = APU(duration)
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
ROOT = {'A': 33, 'Am': 33, 'F': 29, 'C': 36, 'G': 31, 'E': 28, 'Dm': 38, 'B': 35, 'D': 38}
IVS = {'A': (0, 4, 7), 'D': (0, 4, 7), 'Am': (0, 3, 7), 'F': (0, 4, 7), 'C': (0, 4, 7), 'G': (0, 4, 7), 'E': (0, 4, 7), 'Dm': (0, 3, 7),
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




# ============================================================= moods, themes, the FX table
# A mood is a chord progression [(chord, seconds), ...] for the groove (bass, arpeggio, drums).
MOODS = {
    'opener': [('Am', 2), ('F', 1), ('G', 1), ('E', 1)],
    'driving': [('Am', 2), ('F', 2), ('C', 2), ('G', 2)],
    'uneasy': [('Am', 2), ('Dm', 2), ('E', 2)],
    'wary': [('F', 2), ('G', 2)],
    'resolve': [('Am', 2), ('E', 1), ('Am', 1)],
    'bright': [('C', 2), ('G', 2), ('Am', 2), ('F', 2)],
    'climb': [('Am', 2), ('F', 2), ('G', 1.5)],
    'agent': [('C', 1.5), ('G', 1), ('Am', 2)],
    'layers': [('Am', 2), ('F', 1)],
    'stoptime': [('Dm', 1), ('E', 1)],
    'lift': [('F', 1), ('G', 1), ('Am', 1)],
    'theme': [('Am', 2), ('F', 1), ('G', 1)],
    'calm': [('F', 2), ('G', 2), ('Am', 1)],
    'tense': [('Am', 2), ('Dm', 2), ('E', 2)],
    'victory': [('A', 2), ('E', 1), ('A', 1)],
    'boss': [('Am', 2), ('F', 2)],
}
# What a mood adds to its chord progression for the stage cues: `scale` is the pitches of the entry blips (element i plays
# scale[i % len]), `stamp` = (m1, m2, root) of the hit on the key message, `after` is the mood after a turn (a failure
# resolved, a boss beaten), `drums` the groove's drums. Moods not listed here use DEFAULT.
DEFAULT = dict(scale=(72, 74, 76, 79, 81, 84), stamp=(69, 76, 33), after='resolve', drums='full')
STYLE = {
    'calm': dict(scale=(72, 74, 76, 79, 81, 84), drums='light', after='calm'),
    'bright': dict(scale=(72, 76, 79, 84, 88, 91), stamp=(72, 79, 36), after='bright'),
    'tense': dict(scale=(64, 67, 69, 71, 72, 76), stamp=(57, 64, 33)),
    'driving': dict(scale=(69, 72, 76, 79, 81, 84), after='driving'),
    'climb': dict(scale=(69, 72, 74, 76, 79, 81), after='agent'),
    'resolve': dict(after='resolve'),
    'boss': dict(scale=(64, 65, 67, 69, 71, 76), stamp=(53, 64, 29), after='victory', boss=True),
    'victory': dict(scale=(69, 73, 76, 81, 85, 88), stamp=(69, 76, 33), after='victory'),
}


def style(mood):
    return dict(DEFAULT, **STYLE.get(mood, {}))

# The series' trailer theme (score A), as [seconds from a bar line, midi, seconds]; the opener and the payoff play it.
THEME = [(1.25, 76, 0.75), (2.0, 69, 0.25), (2.25, 72, 0.5), (2.75, 76, 0.5),
         (3.25, 77, 0.5), (3.75, 76, 0.25), (4.0, 76, 0.25), (4.25, 72, 0.25), (4.5, 74, 0.45)]
CH = {'p1': P1, 'p2': P2}


def E(name, tau=6, swell=(2, 5), hold=60):
    return {'sus': E_sus, 'lead': E_lead, 'exp': E_exp(tau), 'swell': E_swell(*swell), 'fade': E_fade(hold, 0)}[name]


def _groove(t, mood=None, prog=None, drums='full', arp=5, hat=4):
    groove(t, [tuple(x) for x in (prog or MOODS[mood])], drums=drums, arp_v=arp, hat_v=hat)


# fx name -> function(t, ctx, **args). ctx carries the episode's motif and riffs for named note lists.
def _notes(ctx, n):
    if isinstance(n, str):
        if n == 'motif':
            return ctx['motif']
        if n == 'motif_head':
            return ctx['motif'][:4]
        return ctx['riffs'][n]
    return n


FX = {
    'blip': lambda t, c, ch='p1', m=60, frames=4, v=10, duty=2, slide=0.0: blip(CH[ch], t, m, frames, v, duty, slide),
    'coin': lambda t, c, ch='p1', v=12: coin(CH[ch], t, v),
    'ding': lambda t, c, m=84: ding(t, m),
    'buzz': lambda t, c, dur=0.35, m=40, v=13: buzz(t, dur, m, v),
    'tri_drop': lambda t, c, m0=40, m1=26, frames=4: tri_drop(t, m0, m1, frames),
    'stamp': lambda t, c, m1=69, m2=76, root=33, v=14: stamp(t, m1, m2, root, v),
    'hit_all': lambda t, c, m1=None, m2=None, root=33, v=15, tau=16, dur=0.8, cym='crash', tri_hold=0.6, duty=2:
        hit_all(t, m1, m2, root, v, tau, dur, cym, tri_hold, duty),
    'key': lambda t, c, v=9: key(t, v),
    'tick': lambda t, c, v=5: tick(t, v),
    'nz': lambda t, c, v=(8, 5, 3), per=2, mode=0: nz(t, v, per, mode),
    'boom': lambda t, c, v=15: boom(t, v),
    'melody': lambda t, c, notes=(), v=11, duty=2: melody(t, _notes(c, notes), v, duty),
    'groove': lambda t, c, mood=None, prog=None, drums='full', arp=5, hat=4: _groove(t, mood, prog, drums, arp, hat),
    'chord_arp': lambda t, c, dur=1.0, root=33, ivs=(0, 4, 7), v=5, duty=1, rate=1, env='sus', swell=(2, 5):
        chord_arp(P2, t, t + dur, root, ivs, v, duty, env=E(env, swell=swell), rate=rate),
    'note': lambda t, c, ch='p1', dur=0.5, m=60, v=12, duty=2, env='lead', tau=6, vib=0.0, release=2, slide=0.0:
        note(CH[ch], t, dur, m, v, duty, env=E(env, tau=tau), vib=vib, release=release, slide=slide),
    'bass8': lambda t, c, dur=1.0, root=33: bass8(t, t + dur, root),
    'hats': lambda t, c, dur=1.0, step=0.25, v_on=4, v_off=2: hats(t, t + dur, step, v_on, v_off),
    'ostinato': lambda t, c, dur=1.0, root=28: ostinato(t, t + dur, root),
    'double_time': lambda t, c, dur=1.0, v=12, snare=True: double_time(t, t + dur, v, snare),
    'roll': lambda t, c, dur=0.48, v0=4, v1=11, gap0=4, gap1=2: roll(t, t + dur, v0, v1, gap0, gap1),
    'noise_sweep': lambda t, c, dur=1.0, per0=12, per1=3, v0=2, v1=8: noise_sweep(t, t + dur, per0, per1, v0, v1),
    # composites: a few sounds that always go together
    'guess_coin': lambda t, c: (coin(P2, t, 9), blip(P1, t + 0.1, 64, 6, 9, 0, slide=5)),
    'key_blip': lambda t, c, v=11: (key(t, v), blip(P2, t, 81, 3, 7, 1)),
}


def expand(ev):
    """One script event -> [(at, args)]: `at` may be a list, or `at` + `step` + `n` (with `each` for per-step values)."""
    ev = dict(ev)
    fx = ev.pop('fx')
    ev.pop('label', None)
    at, step, n, each = ev.pop('at', 0), ev.pop('step', 0), ev.pop('n', None), ev.pop('each', {})
    if isinstance(at, (list, tuple)):
        return [(fx, a, ev) for a in at]
    if n is None:
        return [(fx, at, ev)]
    return [(fx, at + k * step, dict(ev, **{key_: vals[k] for key_, vals in each.items()})) for k in range(n)]


def run_event(ev, t0, ctx):
    for fx, at, args in expand(ev):
        FX[fx](t0 + at, ctx, **args)
        hit(t0 + at, fx)


# ============================================================= template cues
def groove_span(t0, t1, mood, drums='full', arp=5):
    """The mood's groove, repeated from t0 and cut at t1."""
    prog, t = [], t0
    while t < t1 - 1e-6:
        for ch, d in MOODS[mood]:
            if t >= t1 - 1e-6:
                break
            d = min(d, t1 - t)
            prog.append((ch, d))
            t += d
    groove(t0, prog, drums=drums, arp_v=arp)


BOSS_RIFF = [(0, 64, 0.5), (0.5, 64, 0.5), (1, 65, 0.5), (1.5, 64, 0.5), (2, 62, 0.5), (2.5, 64, 1), (3.5, 59, 0.5)]


def boss_ground(t0, t1):
    """The boss: a phrygian ostinato on the triangle, a riff on the lead, a double-time beat, a held E / F arpeggio."""
    stamp(t0, 52, 53, 28, 15)
    ostinato(t0, t1, 28)
    k = 0
    while t0 + k * 2.0 < t1 - 1e-6:
        melody(t0 + k * 2.0, BOSS_RIFF, 9 + k % 2, duty=0)
        chord_arp(P2, t0 + k * 2.0, min(t1, t0 + k * 2.0 + 2.0), 64 + k % 2, (0, 4, 7), 4, 0, rate=2)
        k += 1
    double_time(t0, t1 - 1.0, 12, False)


def cue_T05(sc, ctx):
    """Stage scene: the mood's ground (stage-start jingle and groove, or the boss ground), one cue per mark the layout
    placed at an element time, the scripted `events` (raw overrides), the CLEAR! jingle, a noise roll into the next scene."""
    t0, t1 = sc['t0'], sc['t1']
    mood = sc.get('mood', 'calm')
    st = style(mood)
    marks = sc.get('marks', [])
    z = sc['clear']
    turn = next((m['at'] for m in marks if m['k'] in ('turn', 'victory')), None)
    first = turn if turn is not None else z
    if st.get('boss'):
        boss_ground(t0, t0 + first)
    else:
        stage_start(t0)
        groove_span(t0 + 0.5, t0 + first, mood, st['drums'])
    if turn is not None:
        groove_span(t0 + turn, t0 + z, st['after'], 'full' if st.get('boss') else st['drums'])
    sc_, (m1, m2, root) = st['scale'], st['stamp']
    for m in marks:
        t, k, i = t0 + m['at'], m['k'], m.get('i', 0)
        if k == 'enter':
            blip(P2, t, sc_[i % len(sc_)], 3, 8, 1)
        elif k == 'reveal':
            blip(P1, t, sc_[i % len(sc_)], 4, 11, 2)
        elif k == 'ok':
            blip(P1, t, sc_[i % len(sc_)] - 12, 3, 10, 2)
        elif k in ('key', 'hit'):
            stamp(t, m1, m2, root, 13)
        elif k == 'second':
            ding(t, sc_[-1])
        elif k == 'coin':
            coin(P2, t, 9); blip(P1, t + 0.1, 64, 6, 9, 0, slide=5)
        elif k == 'packet':
            blip(P2, t, 72 if m['dir'] > 0 else 84, 10, 9, 1, slide=12 * m['dir'])
        elif k == 'press':
            key(t, 11); blip(P2, t, 81, 3, 7, 1)
        elif k == 'fail':
            buzz(t, 0.4, 40); tri_drop(t, 40, 24, 8)
        elif k == 'cut':
            stamp(t, m1, m2, root, 13)
        elif k == 'victory':
            if st.get('boss'):
                roll(t - 1.0, t - 0.02, 4, 14, 5, 1); noise_sweep(t - 1.0, t - 0.02, 14, 4, 2, 8)
            hit_all(t, m1 + 4, m2 + 12, 33, 12, tau=20, dur=0.9, cym='crash', tri_hold=0.8)
            for j, n in enumerate((69, 73, 76, 81, 76, 81, 85)):
                note(P1, t + 0.4 + j * 0.125, 0.11, n, 12, 2, env=E_exp(6), release=0)
            ding(t + 0.3, 88)
        hit(t, k)
    for ev in sc.get('events', []):
        run_event(ev, t0, ctx)
    if sc.get('clear_color', 'green') == 'red':      # a refusal: a failure buzz and a drop, not the CLEAR! jingle
        buzz(t0 + z, 0.45, 40, 13); tri_drop(t0 + z, 40, 28, 6); hit(t0 + z, sc.get('clear_text', 'NO GO!'))
    else:
        clear(t0 + z)
    roll(t1 - 0.5, t1 - 0.02, 4, 11)


def _theme(t0, t1, shift, v):
    """The series' trailer theme, `shift` seconds after t0; notes that would run past t1 - 0.5 are left out."""
    for t, m, d in THEME:
        if t0 + t + shift + d < t1 - 0.5:
            note(P1, t0 + t + shift, d - 0.02, m, v, 2, vib=0.2 if d >= 0.5 else 0.0)


def cue_T01(sc, ctx):
    """Title card: a coin on the series line, the stamp on the key, the theme over the mood, a roll into the next scene."""
    t0, t1, ka = sc['t0'], sc['t1'], sc['key_at']
    blip(P2, t0 + sc['glance_at'] + 0.3, 88, 3, 7, 1); blip(P2, t0 + sc['glance_at'] + 0.35, 93, 4, 7, 1)
    note(P1, t0 + ka - 0.38, 0.36, 86, 3, 1, env=E_sus, slide=-10, release=0)
    stamp(t0 + ka, 57, 64, 33); hit(t0 + ka, 'STAMP key')
    groove_span(t0 + ka, t1 - 0.5, sc.get('mood', 'opener'), 'light')
    _theme(t0, t1, ka - 1.0, 12)
    roll(t1 - 0.5, t1 - 0.02, 5, 12, gap0=3, gap1=2)


def cue_T04(sc, ctx):
    """Player card: stamp, groove, the motif, a blip per role line, a tick on the key, a noise sweep out."""
    t0, t1 = sc['t0'], sc['t1']
    stamp(t0, 69, 76, 33); hit(t0, 'flash, card')
    groove_span(t0, t1 - 1.0, sc.get('mood', 'driving'))
    if ctx['motif']:
        melody(t0 + 0.5, ctx['motif'], 10)
    for i in range(2):
        blip(P2, t0 + sc['secondary_at'] + i * 0.4, 81 + i * 2, 3, 8, 1); hit(t0 + sc['secondary_at'] + i * 0.4, 'role line')
    nz(t0 + sc['key_at'], [10, 7, 4], 2); hit(t0 + sc['key_at'], 'key')
    noise_sweep(t1 - 1.0, t1 - 0.02, 12, 3, 2, 8)


def cue_T21(sc, ctx):
    """Payoff: the call, one blip per tree node climbing the major scale, the theme at full voice on the key."""
    t0, t1, ka = sc['t0'], sc['t1'], sc['key_at']
    stamp(t0, 69, 76, 33, 12); hit(t0, 'payoff')
    blip(P2, t0 + sc['call_at'], 72, 12, 9, 1, slide=12); hit(t0 + sc['call_at'], 'tool call')
    for i in range(len(sc['nodes'])):
        t = t0 + sc['nodes_at'] + i * 0.12
        blip(P1, t, 76 + SCALE[(i * 2) % 7] + 12 * ((i * 2) // 7), 3, 10, 2); hit(t, 'tree node')
    hit_all(t0 + ka, 69, 76, 33, 15, tau=20, dur=0.8, cym='crash', tri_hold=0.3); hit(t0 + ka, 'STAMP key')
    groove_span(t0 + ka, t1 - 0.5, sc.get('mood', 'theme'))
    _theme(t0, t1, ka - 1.0, 13)
    noise_sweep(t1 - 0.75, t1 - 0.02, 10, 2, 3, 9)


SCALE = (0, 2, 4, 5, 7, 9, 11)


def cue_T22(sc, ctx):
    """Result: level-clear fanfare, one blip per stage pip, a quiet bed, the motif head on the closing line."""
    t0, t1 = sc['t0'], sc['t1']
    for i, m in enumerate((72, 76, 79, 84)):
        note(P1, t0 + i * 0.1, 0.1, m, 13, 2, env=E_sus, release=0)
    note(P1, t0 + 0.4, 0.55, 84, 13, 2, env=E_exp(20), vib=0.2, release=0)
    note(P2, t0, 0.9, 76, 9, 1, env=E_exp(25), arp=[0, 3, 7], release=0)
    tri(t0, 0.9, 36); crash(t0, 12); kick(t0, 13, drop=False); hit(t0, 'CLEAR title')
    for i in range(ctx['stages']):
        t = t0 + 0.6 + i * 0.08
        blip(P2, t, 72 + SCALE[i % 7] + 12 * (i // 7), 3, 8, 2); hit(t, 'pip')
    groove_span(t0 + 1.0, t1 - 1.0, sc.get('mood', 'calm'), 'light', 4)
    if ctx['motif']:
        melody(t0 + sc['secondary_at'] - 0.5, ctx['motif'][:6], 7)
    roll(t1 - 1.0, t1 - 0.02, 4, 12)


def cue_T23(sc, ctx):
    """End card: the trailer cadence, then the A-minor chord rings and fades in 4-bit steps."""
    t0 = sc['t0']
    for a, b, ch in ((0.0, 1.0, 'Am'), (1.0, 1.5, 'F'), (1.5, 2.0, 'G')):
        bass8(t0 + a, t0 + b, ROOT[ch])
        chord_arp(P2, t0 + a, t0 + b, ROOT[ch] + 24, IVS[ch], 6, 1)
    for t, m, d in ((0.0, 76, 0.75), (0.75, 69, 0.25), (1.0, 72, 0.5), (1.5, 71, 0.25), (1.75, 74, 0.25)):
        note(P1, t0 + t, d - 0.02, m, 14, 2, vib=0.25 if d >= 0.5 else 0.0)
    hats(t0, t0 + 2.0, 0.25, 5, 2)
    for t in (0.0, 0.5, 1.0, 1.5):
        kick(t0 + t, 13, drop=t != 0.0)
    snare(t0 + 0.5, 12); snare(t0 + 1.5, 13)
    hit_all(t0, None, None, 33, 15, cym='crash', tri_hold=0.15); hit(t0, 'END CARD')
    note(P1, t0 + 2.0, 3.4, 69, 14, 2, env=E_fade(60, 0), vib=0.2, vib_delay=20, release=0)
    note(P2, t0 + 2.0, 3.4, 72, 9, 1, env=E_fade(60, 0), arp=[0, 4], arp_rate=1, release=0)
    tri(t0 + 2.0, 1.6, 33)
    crash(t0 + 2.0, 12, 80); kick(t0 + 2.0, 14, drop=False); hit(t0 + 2.0, 'final chord')
    for j, t in enumerate((2.5, 3.1667, 3.8333, 4.5)):       # PRESS START blinks (steal P2)
        blip(P2, t0 + t, 88, 3, max(2, 9 - 2 * j), 1); blip(P2, t0 + t + 0.05, 93, 4, max(2, 9 - 2 * j), 1)



def cue_T24(sc, ctx):
    """Sprite-layer scenes use the NES sound palette, without repetitive stage clear stamps."""
    t0, t1 = sc['t0'], sc['t1']
    groove_span(t0 + 0.5, t1 - 0.5, sc.get('mood', 'calm'), 'light', 4)
    coin(P2, t0 + 0.1, 8)
    blip(P1, t0 + sc.get('key_at', 1), 76, 5, 10, 2)
    hit(t0 + sc.get('key_at', 1), 'cinema key')
    if sc.get('secondary'):
        ding(t0 + sc['secondary_at'], 88)
        hit(t0 + sc['secondary_at'], 'cinema secondary')
    if sc.get('effect') == 'recursion':
        stamp(t0 + 5.4, 69, 76, 33, 15)
    if sc.get('effect') == 'coin-return':
        note(P1, t1 - 2, 1.8, 69, 10, 2, env=E_fade(55, 0), release=0)
    roll(t1 - 0.4, t1 - 0.02, 4, 9)

CUES = {'T01': cue_T01, 'T04': cue_T04, 'T05': cue_T05, 'T21': cue_T21, 'T22': cue_T22, 'T23': cue_T23, 'T24': cue_T24}


# ============================================================= the episode score
def render(scenes, ctx, holds=()):
    """scenes: list of dicts with template, t0, t1 and the scene's script keys. Returns mono float samples at 48 kHz,
    peak-normalised to -1.1 dBFS with a 10 ms fade-out; silence is inserted at each reading hold [(cut, seconds)]."""
    dur = scenes[-1]['t1']
    start(dur)
    for sc in scenes:
        CUES[sc['template']](sc, ctx)
    x = A.render()
    n = int(round(dur * SR))
    x = np.concatenate([x, np.zeros(max(0, n - len(x)))])[:n]
    peak = np.abs(x).max()
    if peak == 0:
        raise ValueError('the score is silent: no cue wrote a sound')
    x /= peak
    x = np.tanh(0.8 * x) / np.tanh(0.8)                 # soft knee: a little more body (about +1.6 dB LUFS) at the same peak
    x *= 10 ** (-1.1 / 20)
    ramp = min(n, 480)
    x[-ramp:] *= np.linspace(1, 0, ramp)
    for cut, d in sorted(holds, reverse=True):          # a hold freezes the picture: the music waits too
        i = int(round(cut * SR))
        x = np.concatenate([x[:i], np.zeros(int(round(d * SR))), x[i:]])
    return x


def write_wav(path, x):
    y = np.clip(np.round(x * 32767), -32768, 32767).astype('<i2')
    st = np.repeat(y[:, None], 2, axis=1)
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(st.tobytes())


def hits_json():
    return json.dumps(sorted(HITS), indent=1) + '\n'
