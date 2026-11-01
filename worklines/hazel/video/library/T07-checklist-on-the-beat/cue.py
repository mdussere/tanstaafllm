# T07 cue: rising check blips, ding.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/story1-hello-luna/src/score.py, lines 337-354
def stage1():
    # 12 - 20: secure the original card. The size lands, the copy runs up, checks, then CLEAR.
    stage_start(12.0)
    groove(12.0, [('Am', 2), ('F', 2), ('C', 2), ('G', 2)], arp_v=4)
    blip(P2, 13.1, 81, 4, 10, 2); nz(13.1, [10, 7, 4], 2); hit(13.1, '48.8 GiB')
    for i in range(8):                   # the extraction bar fills
        blip(P1, 13.5 + i * 0.175, 69 + (0, 2, 3, 5, 7, 8, 10, 12)[i], 3, 8, 1); hit(13.5 + i * 0.175, 'copy')
    ding(15.0); hit(15.0, 'SAFE ON DISK')
    for i in range(2):
        blip(P1, 15.6 + i * 0.3, 76 + (0, 4)[i], 4, 10, 2); hit(15.6 + i * 0.3, 'check')
    ding(16.2, 88)
    for i in range(3):
        blip(P2, 16.5 + i * 0.15, 84 + (0, 3, 7)[i], 3, 7, 1); hit(16.5 + i * 0.15, 'partition')
    melody(17.0, [(0, 76, 1), (1, 74, 1), (2, 72, 1), (3, 71, 0.8)], 9)
    clear(18.5)
    roll(19.5, 19.98, 4, 11)


