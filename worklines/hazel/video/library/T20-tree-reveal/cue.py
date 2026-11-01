# T20/T21 cue: the query slide, one blip per node, the theme on the stamp.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/story2-ask-the-desktop/src/score.py, lines 470-482
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


