# T01 cue: the series opener. Needs the episode helpers of score.py (stamp, groove, roll) and nes.py.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/story2-ask-the-desktop/src/score.py, lines 310-330
THEME = [(1.25, 76, 0.75), (2.0, 69, 0.25), (2.25, 72, 0.5), (2.75, 76, 0.5),   # the trailer theme (score A)
         (3.25, 77, 0.5), (3.75, 76, 0.25), (4.0, 76, 0.25), (4.25, 72, 0.25), (4.5, 74, 0.45)]


def title():
    # 0 - 6: the series opener. A coin, the stamp, then the trailer theme over Am F G, and E into the player.
    blip(P2, 0.3, 88, 3, 7, 1); blip(P2, 0.35, 93, 4, 7, 1); hit(0.3, 'series line')
    note(P1, 0.62, 0.36, 86, 3, 1, env=E_sus, slide=-10, release=0)
    stamp(1.0, 57, 64, 33); hit(1.0, 'STAMP ASK THE DESKTOP')
    groove(1.0, [('Am', 2), ('F', 1), ('G', 1), ('E', 1)], drums='light', arp_v=5)
    for t, m, d in THEME + [(5.0, 71, 0.5), (5.5, 68, 0.45)]:
        note(P1, t, d - 0.02, m, 12, 2, vib=0.2 if d >= 0.5 else 0.0)
    roll(5.5, 5.98, 5, 12, gap0=3, gap1=2)


# The "Wyoh" motif: E A B C rising, then it settles (A minor, over Am F C G).
WYOH_THEME = [(0, 76, 1), (1, 81, 0.5), (1.5, 83, 0.5), (2, 84, 1.5), (3.5, 83, 0.5), (4, 81, 1), (5, 77, 1),
              (6, 79, 1), (7, 79, 0.5), (7.5, 76, 0.5), (8, 72, 1.5), (9.5, 74, 0.5), (10, 76, 2), (12, 74, 1), (13, 71, 1)]
WYOH_HEAD = WYOH_THEME[:4]


