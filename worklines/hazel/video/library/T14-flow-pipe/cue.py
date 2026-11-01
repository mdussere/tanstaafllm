# T14 cue: sliding blips, up for a query, down for an answer.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/story2-ask-the-desktop/src/score.py, lines 386-402
def stage4():
    # 36 - 44: the MCP bridge. Query, answer, act, event; the 26 TOOLS stamp.
    stage_start(36.0)
    groove(36.0, [('Am', 2), ('F', 2), ('C', 2), ('G', 2)])
    for t, m, sl, lab in ((37.0, 72, 12, 'query'), (37.45, 84, -12, 'tree back'), (38.0, 76, 12, 'act'),
                          (39.0, 88, -12, 'event confirms')):
        blip(P2, t, m, 10, 9, 1, slide=sl); hit(t, lab)
    key(38.4, 10); hit(38.4, 'focus moves')
    stamp(40.0, 72, 79, 36); hit(40.0, 'STAMP 26 TOOLS')
    melody(40.5, [(0, 76, 1), (1, 77, 1), (2, 79, 1)], 8)
    clear(42.5)
    roll(43.5, 43.98, 5, 12)


BOSS_RIFF = [(0, 64, 0.5), (0.5, 64, 0.5), (1, 65, 0.5), (1.5, 64, 0.5), (2, 62, 0.5), (2.5, 64, 1), (3.5, 59, 0.5)]


