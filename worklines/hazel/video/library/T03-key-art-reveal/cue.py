# T03 cue: the drop and the full trailer theme.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/trailer/src/score.py, lines 238-263
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


