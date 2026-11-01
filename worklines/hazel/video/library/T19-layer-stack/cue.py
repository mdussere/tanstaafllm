# T19 cue: checks, ding, buzz, Dsus4 stop-time, the stamp.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/story2-ask-the-desktop/src/score.py, lines 448-469
def stage7():
    # 62 - 72: seven layers. Four checks, "verified", the game does not move (stop-time), then each layer in turn.
    stage_start(62.0)
    groove(62.0, [('Am', 2), ('F', 1)])
    for i, t in enumerate((63.5, 63.75, 64.0, 64.25)):
        blip(P1, t, 72 + (0, 2, 4, 5)[i], 3, 10, 2); hit(t, f'layer {i + 1} ok')
    ding(64.5, 84); hit(64.5, 'VERIFIED')
    buzz(65.0, 0.5, 40, 13); tri_drop(65.0, 40, 21, 10); hit(65.0, 'THE GAME DID NOT MOVE')
    chord_arp(P2, 65.5, 66.5, 62, (0, 5, 7, 12), 4, 0, env=E_swell(2, 5), rate=3)    # stop-time: Dsus4
    tick(65.5, 5); tick(66.0, 5)
    groove(66.5, [('Dm', 1), ('E', 1)], drums='light')
    for i, t in enumerate((67.0, 67.5)):
        blip(P1, t, 77 + 2 * i, 4, 11, 2); hit(t, f'layer {i + 5} ok')
    roll(67.5, 67.98, 4, 12)
    ding(68.0, 88); hit(68.0, 'layer 7: the game moves')
    stamp(68.5, 69, 76, 33); hit(68.5, 'STAMP ONLY THE LAST ONE')
    groove(69.0, [('F', 1), ('G', 1), ('Am', 1)])
    melody(69.0, [(0, 72, 1), (1, 74, 1), (2, 76, 2)], 9)
    clear(70.5)
    roll(71.5, 71.98, 4, 11)


