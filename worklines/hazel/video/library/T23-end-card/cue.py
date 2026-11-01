# T23 cue: the trailer cadence and the A-minor chord fading in 4-bit steps.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/story2-ask-the-desktop/src/score.py, lines 497-516
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


