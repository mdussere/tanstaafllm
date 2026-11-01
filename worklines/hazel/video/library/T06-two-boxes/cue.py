# T06 cue: buzz on the fail, ding on the works, CLEAR.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/story1-hello-luna/src/score.py, lines 382-392
def stage3():
    # 28 - 34: the keyboard. Hub: buzz. Adapter: ding.
    stage_start(28.0)
    groove(28.0, [('F', 2), ('G', 2), ('Am', 2)])
    buzz(29.2, 0.45, 38); hit(29.2, 'hub fails')
    ding(31.3, 86); hit(31.3, 'adapter works')
    melody(30.0, [(0, 72, 0.5), (0.5, 74, 0.5), (1, 76, 1)], 9)
    clear(32.4)
    roll(33.5, 33.98, 4, 11)


