# T11 cue: E phrygian ostinato, double time, boom, hits, A-major victory.
# Does not run alone: it calls score.py's helpers (note, blip, coin, stamp, hit_all, groove, melody...).

# ---- from worklines/hazel/video/story2-ask-the-desktop/src/score.py, lines 400-428
BOSS_RIFF = [(0, 64, 0.5), (0.5, 64, 0.5), (1, 65, 0.5), (1.5, 64, 0.5), (2, 62, 0.5), (2.5, 64, 1), (3.5, 59, 0.5)]


def boss():
    # 44 - 52: the boss, the black panel. E phrygian ostinato; two hits; the panel lights on A major.
    stamp(44.0, 52, 53, 28, 15); hit(44.0, 'BOSS')
    ostinato(44.0, 48.5, 28)
    melody(44.0, BOSS_RIFF, 9, duty=0); melody(46.0, BOSS_RIFF, 10, duty=0)
    for a, b, ch in chords_at(44.0, [('E', 2), ('F', 2), ('E', 0.5)]):
        chord_arp(P2, a, b, ROOT[ch] + 36, (0, 4, 7), 4, 0, rate=2)
    double_time(44.0, 47.5, 12, snare_on=False)
    boom(45.0, 15); tri_drop(45.0, 40, 21, 8); hit(45.0, 'BLACK.')
    blip(P2, 45.6, 76, 4, 9, 1); hit(45.6, 'screenshots looked right')
    stamp(46.5, 53, 64, 29, 13); hit(46.5, 'NOT LOADED (hit 1)')
    roll(47.5, 48.48, 4, 14, gap0=5, gap1=1)
    noise_sweep(47.5, 48.48, 14, 4, 2, 8)
    # the driver loads: victory, A major
    hit_all(48.5, 73, 76, 33, 12, tau=20, dur=0.9, cym='crash', tri_hold=0.8); hit(48.5, 'LOADED, the panel lights')
    for i, m in enumerate((69, 73, 76, 81, 76, 81, 85)):
        note(P1, 48.9 + i * 0.125, 0.11, m, 12, 2, env=E_exp(6), release=0)
    ding(48.8, 88); hit(48.8, '1 passed')
    for a, b, ch in ((49.5, 50.5, 'D'), (50.5, 52.0, 'E')):
        bass8(a, b, ROOT[ch] - 12 if ch == 'D' else ROOT[ch])
        chord_arp(P2, a, b, ROOT[ch] + 24 if ch == 'D' else ROOT[ch] + 36, (0, 4, 7), 5, 1, rate=2)
    hats(49.5, 51.5, 0.25, 4, 2)
    clear(50.5)
    roll(51.5, 51.98, 4, 12)


