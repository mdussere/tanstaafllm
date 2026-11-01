"""Draw the music map: the picture's sequences and the soundtrack wanted for them.

One SVG, time left to right over the whole cut (holds included):
  - the picture: sequences, holds (hatched) and hits (stamps, slams, cuts);
  - the music wanted: movements with their mood and colour, the intensity curve,
    the target loudness, and which layers play.

Usage: python music_map.py OUT.svg
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
HOLDS = sorted(json.loads((HERE / "holds.json").read_text())["holds"])
DUR = 60 + sum(d for _, d in HOLDS)


def out(t):
    return t + sum(d for s, d in HOLDS if s < t)


def hold_spans():
    a, spans = 0.0, []
    for s, d in HOLDS:
        spans.append((s + a, s + a + d))
        a += d
    return spans


# Picture sequences (source start, label)
SEQ = [(0, "Insert coin"), (4, "Key art"), (8, "Player 1: Luna"), (16, "Price list"), (20, "pong"),
       (24, "Select your intelligence"), (34, "Boss"), (35.5, "Pressure: 983 MiB"), (40, "The cell"),
       (48, "Speedrun"), (54, "Doctrine"), (57, "End card")]
# Hits on the picture (source time, label, strength 1-3)
HITS = [(2.95, "LLM", 3), (4, "cut", 2), (8, "cut", 1), (16, "slam", 3), (17, "slam", 3), (18, "slam", 3),
        (20, "cut", 1), (22.6, "NO FREE LLM", 3), (24, "cut", 1), (24.5, "", 1), (26, "", 1), (27.5, "", 1),
        (29, "", 1), (31, "banner", 2), (34, "boss", 2), (35.5, "cut", 2), (36, "", 1), (37, "fits", 1),
        (38, "", 1), (38.4, "LIMIT", 3), (40, "cut", 1), (43, "rule", 2), (44, "rule", 2), (45, "rule", 2),
        (46, "rule", 2), (47, "rule", 2)] + [(48 + i, "", 2) for i in range(6)] + [
        (54, "stab", 3), (54.75, "stab", 3), (55.5, "stab", 3), (57, "END", 3), (58.4, "start", 1)]

# Movements wanted (output start, end, title, mood, colour, layers)
LAYERS = ["Drone / pad", "Arpeggio", "Bass", "Drums", "Theme / lead", "Hits / FX"]
MOV = [
    (0, 7, "I. Attract mode", "arcade at rest, mysterious; blips, typing ticks; the stamp hits; the hold is a suspended chord swelling into a riser", "#3b2f8f", {0, 1, 5}),
    (7, 12, "II. Lift-off", "the drop: full theme, wide and epic, gold", "#ffb43c", {0, 1, 2, 3, 4, 5}),
    (12, 22, "III. Player 1", "playful groove; a blip per stat; half-time under the mission text; the hold breathes on a bass pedal, then a fill", "#2fc6d8", {1, 2, 3, 4, 5}),
    (22, 27.5, "IV. Every price", "stop-time slams; the hold is a ringing low drone, drums out: tension", "#b0309c", {0, 2, 5}),
    (27.5, 32, "V. One word", "near silence, terminal ticks, counter accelerando-ritardando, ding; the stamp brings the groove back", "#3ad86b", {1, 5}),
    (32, 44, "VI. Select", "menu theme; each card adds a layer, cheap to expensive; banner impact; the hold resolves the theme", "#4f7cff", {1, 2, 3, 4, 5}),
    (44, 57.5, "VII. Boss fight", "dark minor, alarm, double-time feel; pitch rises as the bar fills; peak at the limit; the hold decays to a heartbeat", "#ff3d4f", {0, 1, 2, 3, 4, 5}),
    (57.5, 73, "VIII. The cell", "steady, confident march; tiles as a rising arpeggio; one stamp per rule; holds as sustained chords", "#7a4fd8", {0, 1, 2, 3, 5}),
    (73, 86.5, "IX. Speedrun", "fast and bright; a jump and a clear jingle per stage; holds carry the fanfare's tail", "#57ff8f", {1, 2, 3, 4, 5}),
    (86.5, 90, "X. Doctrine", "three stabs, a roll and a riser to the top", "#ffd84a", {0, 2, 3, 5}),
    (90, 94, "XI. Press start", "theme cadence, A-minor chord ringing, blips, fade", "#dfe6ff", {0, 4, 5}),
]
# Intensity wanted (output time, 0-1) and target short-term loudness (output time, LUFS)
INTENSITY = [(0, .12), (2.9, .3), (2.95, .75), (3.6, .3), (6.75, .6), (7, .95), (10.75, .85), (11.75, .7),
             (12, .6), (16, .5), (19.8, .4), (21.8, .55), (22, .9), (25, .7), (25.9, .5), (27.4, .45),
             (27.5, .2), (30, .3), (30.1, .8), (31.8, .55), (32, .5), (39, .85), (41.8, .7), (43.8, .6),
             (44, .85), (45.5, .7), (48, .75), (53.9, 1.0), (55.3, .8), (57.3, .4), (57.5, .55), (62.5, .65),
             (71.8, .7), (73, .85), (86.5, .9), (89.5, 1.0), (90, 1.0), (92.5, .6), (94, 0)]
LOUD = [(0, -26), (2.95, -16), (3.6, -24), (6.75, -18), (7, -13), (12, -15), (22, -13), (27.5, -22),
        (30.1, -15), (32, -15), (44, -13), (57.5, -15), (73, -14), (86.5, -13), (92.5, -16), (94, -40)]

W, X0, X1 = 2000, 150, 1960
PX = (X1 - X0) / DUR
x = lambda T: X0 + T * PX
esc = lambda s: s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    o = []
    H = 1060
    o.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" font-family="DejaVu Sans, sans-serif">')
    o.append('<defs><pattern id="hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
             '<rect width="8" height="8" fill="#ffffff" fill-opacity="0.04"/><line x1="0" y1="0" x2="0" y2="8" stroke="#ffffff" stroke-opacity="0.35" stroke-width="3"/></pattern>')
    # intensity gradient: colours of the movements along time
    o.append('<linearGradient id="mood" x1="0" x2="1" y1="0" y2="0">')
    for a, b, _, _, c, _ in MOV:
        o.append(f'<stop offset="{(a + b) / 2 / DUR:.4f}" stop-color="{c}"/>')
    o.append('</linearGradient></defs>')
    o.append(f'<rect width="{W}" height="{H}" fill="#070b24"/>')
    o.append(f'<text x="{X0}" y="40" font-size="26" fill="#eef3ff" font-weight="bold">TANSTAAFLLM video: picture and the music wanted ({DUR:.0f} s)</text>')
    o.append(f'<text x="{X0}" y="66" font-size="15" fill="#8e97cc">Hatched: reading holds, where the picture rests. Colour = mood of each movement. Times in seconds of the final cut.</text>')

    def label(y, s):
        o.append(f'<text x="{X0 - 12}" y="{y}" font-size="14" fill="#8e97cc" text-anchor="end">{s}</text>')

    # time ruler
    y = 100
    for T in range(0, int(DUR) + 1, 2):
        major = T % 10 == 0
        o.append(f'<line x1="{x(T):.1f}" y1="{y}" x2="{x(T):.1f}" y2="{y + (12 if major else 6)}" stroke="#8e97cc"/>')
        if major:
            o.append(f'<text x="{x(T):.1f}" y="{y - 6}" font-size="13" fill="#8e97cc" text-anchor="middle">{T}</text>')
    label(y + 10, "seconds")
    # picture sequences
    y = 130
    label(y + 30, "Picture")
    starts = [out(s) for s, _ in SEQ] + [DUR]
    for i, (s, name) in enumerate(SEQ):
        a, b = starts[i], starts[i + 1]
        o.append(f'<rect x="{x(a):.1f}" y="{y}" width="{(b - a) * PX:.1f}" height="50" fill="{"#141a4a" if i % 2 else "#1d2460"}" stroke="#3a4390"/>')
        o.append(f'<text x="{x(a) + 5:.1f}" y="{y + 30}" font-size="13" fill="#eef3ff">{esc(name)}</text>')
    for a, b in hold_spans():
        o.append(f'<rect x="{x(a):.1f}" y="{y}" width="{(b - a) * PX:.1f}" height="50" fill="url(#hatch)"/>')
    # hits
    y = 200
    label(y + 22, "Hits")
    last_label = -1e9
    for s, name, k in HITS:
        T = out(s)
        if name and x(T) - last_label < 34:   # neighbours too close: one label for the group
            name = ""
        elif name:
            last_label = x(T)
        r = 4 + 3 * k
        col = ["", "#8e97cc", "#ffb43c", "#ff4d5e"][k]
        o.append(f'<path d="M{x(T):.1f},{y + 30} l{-r},{-2 * r} h{2 * r} z" fill="{col}"/>')
        if name:
            o.append(f'<text x="{x(T):.1f}" y="{y + 46}" font-size="11" fill="{col}" text-anchor="middle">{esc(name)}</text>')
    # movements
    y = 270
    label(y + 30, "Movements")
    for i, (a, b, title, mood, c, _) in enumerate(MOV):
        o.append(f'<rect x="{x(a):.1f}" y="{y}" width="{(b - a) * PX:.1f}" height="56" fill="{c}" fill-opacity="0.85" rx="4"/>')
        o.append(f'<text x="{x(a) + 6:.1f}" y="{y + 22}" font-size="14" font-weight="bold" fill="#05060f" textLength="{min((b - a) * PX - 12, len(title) * 8.6):.0f}" lengthAdjust="spacingAndGlyphs">{esc(title)}</text>')
    # mood texts, staggered on two rows
    y = 340
    label(y + 20, "Mood")
    for i, (a, b, title, mood, c, _) in enumerate(MOV):
        yy = y + (i % 2) * 70
        o.append(f'<line x1="{x(a) + 2:.1f}" y1="{yy}" x2="{x(a) + 2:.1f}" y2="{yy + 60}" stroke="{c}" stroke-width="3"/>')
        words, lines, cur = mood.split(), [], ""
        nxt = x(MOV[i + 2][0]) if i + 2 < len(MOV) else X1   # next text on the same row
        width = min(max(170, (b - a) * PX * 1.9), nxt - x(a) - 12)
        for w_ in words:
            if len(cur) + len(w_) + 1 > width / 7.2:
                lines.append(cur); cur = w_
            else:
                cur = (cur + " " + w_).strip()
        lines.append(cur)
        tx = x(a) + 8
        for j, ln in enumerate(lines[:6]):
            o.append(f'<text x="{tx:.1f}" y="{yy + 14 + j * 15}" font-size="12" fill="{c}">{esc(ln)}</text>')
    # intensity curve
    y0, hh = 500, 170
    label(y0 + hh / 2, "Intensity")
    o.append(f'<rect x="{X0}" y="{y0}" width="{X1 - X0}" height="{hh}" fill="#0b1033" stroke="#262c5a"/>')
    pts = " ".join(f"{x(T):.1f},{y0 + hh - v * hh:.1f}" for T, v in INTENSITY)
    o.append(f'<polygon points="{x(0):.1f},{y0 + hh} {pts} {x(DUR):.1f},{y0 + hh}" fill="url(#mood)" fill-opacity="0.75"/>')
    o.append(f'<polyline points="{pts}" fill="none" stroke="#eef3ff" stroke-width="2"/>')
    for a, b in hold_spans():
        o.append(f'<rect x="{x(a):.1f}" y="{y0}" width="{(b - a) * PX:.1f}" height="{hh}" fill="url(#hatch)"/>')
    # loudness
    y0, hh = 700, 110
    label(y0 + hh / 2 - 8, "Loudness")
    label(y0 + hh / 2 + 10, "(LUFS, short term)")
    o.append(f'<rect x="{X0}" y="{y0}" width="{X1 - X0}" height="{hh}" fill="#0b1033" stroke="#262c5a"/>')
    ly = lambda v: y0 + (-(v) - 12) / 28 * hh
    for v in (-14, -20, -26):
        o.append(f'<line x1="{X0}" y1="{ly(v):.1f}" x2="{X1}" y2="{ly(v):.1f}" stroke="#262c5a" stroke-dasharray="4 4"/>')
        o.append(f'<text x="{X1 + 4}" y="{ly(v) + 4:.1f}" font-size="11" fill="#8e97cc">{v}</text>')
    pts = []
    for i, (T, v) in enumerate(LOUD):   # held levels, steps at changes
        if i:
            pts.append(f"{x(T):.1f},{ly(LOUD[i - 1][1]):.1f}")
        pts.append(f"{x(T):.1f},{ly(max(v, -38)):.1f}")
    o.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="#ffb43c" stroke-width="3"/>')
    # layers
    y0 = 840
    for k, name in enumerate(LAYERS):
        yy = y0 + k * 34
        label(yy + 18, name)
        o.append(f'<line x1="{X0}" y1="{yy + 13}" x2="{X1}" y2="{yy + 13}" stroke="#1d2350"/>')
        for a, b, _, _, c, lay in MOV:
            if k in lay:
                o.append(f'<rect x="{x(a) + 1:.1f}" y="{yy + 4}" width="{(b - a) * PX - 2:.1f}" height="18" fill="{c}" fill-opacity="0.7" rx="3"/>')
    o.append('</svg>')
    pathlib.Path(sys.argv[1]).write_text("\n".join(o) + "\n")


if __name__ == "__main__":
    main()
