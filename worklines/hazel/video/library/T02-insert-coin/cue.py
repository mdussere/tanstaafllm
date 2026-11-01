# T02 cue: attract mode, coin, typing ticks, strike, stamp, riser.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/trailer/src/score.py, lines 214-235
def attract():
    # I. Attract mode (0 - 7.0): arcade at rest, mysterious.
    notes = [57, 64, 71, 72, 76, 72, 71, 64]
    for k in range(15):                                   # slow 12.5 % arpeggio, Am9
        note(P2, k * 0.25, 0.24, notes[k % 8], 4 + (k > 3), 0, env=E_exp(9), release=0)
    for t in (0.0, 0.5):                                  # INSERT COIN blinks
        blip(P1, t, 93, 3, 4, 1)
    note(P1, 0.62, 0.36, 86, 3, 1, env=E_sus, slide=-10, release=0)      # the coin drops
    coin(P1, 1.0); hit(1.0, 'coin, CREDIT 01')
    typing(1.15, 30, "THERE AIN'T NO SUCH THING" + "AS A FREE " + "LUNCH" + ".", lambda t: tick(t, 4))
    note(P1, 2.55, 0.14, 96, 11, 1, env=E_exp(6), slide=-24, release=0)  # red strike
    nz(2.55, [10, 7, 4, 2], 2); hit(2.55, 'strike LUNCH')
    hit_all(2.95, 57, 64, 33, 15, tau=14, dur=0.75, cym='boom', tri_hold=0.7); hit(2.95, 'STAMP LLM')
    note(P2, 3.3, 0.45, 88, 6, 1, env=E_exp(10), release=0)               # the credit fades in
    # hold 3.75 - 6.75: a suspended chord swelling into a riser
    note(P1, 3.75, 1.5, 71, 7, 2, env=E_swell(1, 7), vib=0.12, vib_delay=30, release=0)
    note(P1, 5.25, 1.73, 69, 11, 2, env=E_swell(5, 11), vib=0.15, vib_delay=10, release=0)
    chord_arp(P2, 3.75, 5.25, 57, (0, 2, 7, 12), v=6, duty=0, env=E_swell(2, 6), rate=2)
    chord_arp(P2, 5.25, 6.98, 64, (0, 5, 7, 12), v=9, duty=0, env=E_swell(3, 9), rate=2)
    tri(6.0, 0.98, 28, slide=12)                         # the triangle joins only for the last climb
    noise_sweep(4.75, 6.0, 15, 6, 1, 4)
    roll(6.0, 6.98, 6, 13, gap0=4, gap1=2, per0=5, per1=2)
