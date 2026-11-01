# T08 cue: stamp() and the trailer's three stop-time slams.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/story2-ask-the-desktop/src/score.py, lines 305-308
def stamp(t, m1, m2, root, v=14):
    hit_all(t, m1, m2, root, v, tau=12, dur=0.6, cym='boom', tri_hold=0.4)



# ---- from worklines/hazel/video/trailer/src/score.py, lines 309-322
def prices():
    # IV. Every price (22.0 - 27.5): stop-time slams; the hold is a ringing low drone.
    for t, m1, m2, r, lab in ((22.0, 69, 76, 33, 'SLAM 1'), (23.0, 65, 72, 29, 'SLAM 2'), (24.0, 67, 74, 31, 'SLAM 3')):
        hit_all(t, m1, m2, r, 15, tau=30, dur=0.97, tri_hold=0.88); hit(t, lab)
        for k in range(1, 4):                             # the price meter ticks after each slam
            hat(t + 0.25 * k, 5, weak=True)
    hit_all(25.0, 68, 71, 28, 12, tau=18, dur=0.85, cym=None, tri_hold=2.3); hit(25.0, 'ON LUNA')
    clank(25.0, 11)
    # hold 25.88 - 27.38: low drone (the triangle's E), a minor-second rub above, drums out
    note(P1, 25.85, 1.53, 76, 4, 2, env=E_swell(2, 5), vib=0.1, vib_rate=3, release=0)
    note(P2, 25.85, 1.53, 77, 4, 2, env=E_swell(1, 4), vib=0.1, vib_rate=2.5, release=0)
    noise_sweep(26.3, 27.38, 15, 12, 1, 3)


