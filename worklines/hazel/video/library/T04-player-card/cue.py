# T04 cue: stamp, groove, the hero's motif, one blip per stat row.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/story2-ask-the-desktop/src/score.py, lines 325-341
# The "Wyoh" motif: E A B C rising, then it settles (A minor, over Am F C G).
WYOH_THEME = [(0, 76, 1), (1, 81, 0.5), (1.5, 83, 0.5), (2, 84, 1.5), (3.5, 83, 0.5), (4, 81, 1), (5, 77, 1),
              (6, 79, 1), (7, 79, 0.5), (7.5, 76, 0.5), (8, 72, 1.5), (9.5, 74, 0.5), (10, 76, 2), (12, 74, 1), (13, 71, 1)]
WYOH_HEAD = WYOH_THEME[:4]


def player():
    # 6 - 14: player 2, Wyoh. The groove starts and the Wyoh motif plays.
    stamp(6.0, 69, 76, 33); hit(6.0, 'flash, PLAYER 2')
    groove(6.0, [('Am', 2), ('F', 2), ('C', 2), ('G', 2)])
    melody(6.5, WYOH_THEME, 10)
    for i in range(2):
        blip(P2, 7.4 + i * 0.4, 81 + i * 2, 3, 8, 1); hit(7.4 + i * 0.4, 'stat row')
    nz(8.2, [10, 7, 4], 2); hit(8.2, 'QUEST')
    noise_sweep(13.0, 13.98, 12, 3, 2, 8)


