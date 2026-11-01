# T17 cue: bright C G Am F, the members hop, a rising fanfare.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/trailer/src/score.py, lines 521-546
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


