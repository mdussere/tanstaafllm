# T05 cue: the stage-start sting and the CLEAR! jingle.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/story2-ask-the-desktop/src/score.py, lines 278-293
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


