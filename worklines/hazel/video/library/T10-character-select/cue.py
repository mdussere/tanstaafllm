# T10 cue: the menu theme, one layer per card, a coin on the expensive one, the banner hit.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/trailer/src/score.py, lines 352-401
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


