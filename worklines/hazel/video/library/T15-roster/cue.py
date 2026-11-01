# T15 cue: steady march, tiles as a rising arpeggio, one hit per rule.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/trailer/src/score.py, lines 472-520
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


