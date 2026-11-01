# T13 cue: one rising blip per tile.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/story2-ask-the-desktop/src/score.py, lines 369-385
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


