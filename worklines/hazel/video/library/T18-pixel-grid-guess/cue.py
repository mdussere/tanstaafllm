# T18 cue: a coin and a falling blip per guess.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/story2-ask-the-desktop/src/score.py, lines 342-354
def stage1():
    # 14 - 20: the screenshot trap. Uneasy Am Dm E; each guess costs a coin.
    stage_start(14.0)
    groove(14.0, [('Am', 2), ('Dm', 2), ('E', 2)], arp_v=4)
    for t in (15.0, 15.5, 16.0):
        coin(P2, t, 9); blip(P1, t + 0.1, 64, 6, 9, 0, slide=5); hit(t, 'guess (a coin)')
    nz(14.9, [8, 5, 3], 2); hit(14.9, 'screenshots line')
    ding(17.0, 81); hit(17.0, 'ON PAPER: A DOM')
    melody(17.5, [(0, 76, 1), (1, 75, 1), (2, 76, 1)], 8)
    clear(18.5)
    roll(19.5, 19.98, 4, 11)


