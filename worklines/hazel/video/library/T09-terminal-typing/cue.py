# T09 cue: stop-time, typing ticks, error buzz, Dsus4 wait; then the trailer's pong counter.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/story1-hello-luna/src/score.py, lines 455-470
def router():
    # 60 - 68: the router. Stop-time: an error, a suspended wait, the stamp "11", then the groove.
    stage_start(60.0)
    typing(60.4, 32, 'AP is in CSA process, reject auth', lambda t: tick(t, 4))
    buzz(61.4, 0.5, 41, 13); hit(61.4, 'CSA error')
    chord_arp(P2, 61.9, 63.9, 62, (0, 5, 7, 12), 4, 0, env=E_swell(2, 5), rate=3)   # the wait: Dsus4
    note(P1, 62.0, 1.9, 74, 6, 0, env=E_swell(3, 7), vib=0.15, vib_delay=20, release=0)
    tri(63.0, 0.9, 26)
    nz(64.0, [9, 6, 4, 2], 1); hit(64.0, 'strike AUTO')
    stamp(64.4, 76, 81, 33, 15); hit(64.4, 'STAMP 11')
    groove(65.0, [('C', 1), ('G', 1), ('Am', 1), ('G', 1)])
    melody(65.0, [(0, 76, 1), (1, 79, 1), (2, 81, 2), (4, 79, 1), (5, 74, 1)], 10)
    hit(65.0, 'CONNECTED')
    clear(66.5)



# ---- from worklines/hazel/video/trailer/src/score.py, lines 323-351
def pong():
    # V. One word (27.5 - 32.0): near silence, terminal clicks, the counter; the stamp brings the groove back.
    tri_drop(27.5, 40, 24, 4, then='halt'); nz(27.5, [6, 3, 1], 13); hit(27.5, 'CUT pong')
    note(P1, 27.5, 0.75, 45, 2, 0, env=E_sus, release=0)
    typing(27.7, 16, '> pong', lambda t: key(t, 8))
    key(28.2, 10)                                         # enter
    f0, f1 = F(28.25), F(29.4)
    for k in range(f1 - f0):                              # the counter: a rising glide that slows down
        p = k / (f1 - f0)
        cp = 1 - (1 - p) ** 3
        A.pulse(P1, f0 + k, 60 + 24 * cp, 3, 0)
    last = -1
    for v in range(590, 17701, 590):                      # ticks at each 590 tokens
        p = 1 - (1 - v / 17700) ** (1 / 3)
        f = F(28.25 + 1.15 * p)
        if f != last:
            A.pulse(P2, f, 72 + 24 * v / 17700, 6, 1)
            last = f
    note(P1, 29.4, 0.65, 81, 12, 1, env=E_exp(14), release=0); hit(29.4, 'counter lands')
    note(P2, 29.5, 0.55, 81, 5, 1, env=E_exp(12), release=0)          # its echo
    hit_all(30.1, 57, 60, 33, 15, tau=12, dur=0.4, cym='boom', tri_hold=0.35); hit(30.1, 'STAMP NO FREE LLM')
    bass8(30.5, 32.0, 33)
    chord_arp(P2, 30.5, 32.0, 57, IVS['Am'], 5, 1)
    hats(30.5, 32.0, 0.25, 4, 2)
    for t in (30.5, 31.0, 31.5):
        kick(t, 12)
    snare(31.0, 10); snare(31.75, 8, 4); snare(31.875, 11, 5)


