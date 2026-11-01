# T22 cue: the level-clear fanfare and the pip blips.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/story2-ask-the-desktop/src/score.py, lines 483-496
def result():
    # 78 - 84: STORY 2 CLEAR. The level-clear fanfare, the seven pips, then a quiet bed for reading.
    for i, m in enumerate((72, 76, 79, 84)):
        note(P1, 78.0 + i * 0.1, 0.1, m, 13, 2, env=E_sus, release=0)
    note(P1, 78.4, 0.55, 84, 13, 2, env=E_exp(20), vib=0.2, release=0)
    note(P2, 78.0, 0.9, 76, 9, 1, env=E_exp(25), arp=[0, 3, 7], release=0)
    tri(78.0, 0.9, 36); crash(78.0, 12); kick(78.0, 13, drop=False); hit(78.0, 'STORY 2 CLEAR')
    for i in range(7):
        blip(P2, 78.6 + i * 0.08, 72 + (0, 2, 4, 5, 7, 9, 11)[i], 3, 8, 2); hit(78.6 + i * 0.08, 'pip')
    groove(79.0, [('F', 2), ('G', 2), ('Am', 1)], drums='light', arp_v=4, hat_v=3)
    melody(80.0, [(0, 76, 1), (1, 81, 0.5), (1.5, 83, 0.5), (2, 84, 2), (4, 81, 2)], 7)   # the Wyoh head, quietly
    roll(83.0, 83.98, 4, 12)


