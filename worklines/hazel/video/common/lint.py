"""Layout lint as text. The page records every text box (font, size, glyph height, bounding box) per frame;
build.py samples frames and this module reports, per scene:
  overflow   a text box outside the 1920 x 1080 frame
  margin     a text box in the outer 5 % of the frame (but inside it)
  overlap    two visible texts whose boxes intersect (by more than 2 px each way)
  clear      a text inside the CLEAR! stamp's zone (a stage scene with `clear:`), whether or not the stamp is out yet
  phone      glyph heights against the phone rule: key >= 50 px (VT323 >= 90, Press Start 2P >= 56), secondary >= 35 px;
             a scene without any 50 px text, and frames with more than one secondary (HUD excluded), are reported;
             smaller texts are listed as glance text (the story must not depend on them)
Texts that are still fading in (alpha < 0.5) or sliding in (scale > 1.02) are ignored for the geometric checks.
"""
from collections import defaultdict

W, H, M = 1920, 1080, 120
KEY_PX, SECOND_PX = 50, 35
CLEAR_ZONE = (W - M - 220 - 6 * 72 / 2 - 8, 910, W - M - 220 + 6 * 72 / 2 + 8, 998)   # x0, y0, x1, y1 of "CLEAR!" at 72 px


def source_time(T, holds):
    acc = 0.0
    for s, d in sorted(holds):
        if T < s + acc:
            break
        if T < s + acc + d:
            return s
        acc += d
    return T - acc


def hit(a, b):
    return min(a['x1'], b['x1']) - max(a['x0'], b['x0']) > 2 and min(a['y1'], b['y1']) - max(a['y0'], b['y0']) > 2


def box_s(r):
    return f"x {r['x0']:.0f}..{r['x1']:.0f}, y {r['y0']:.0f}..{r['y1']:.0f}"


def messages(rs):
    """Group text boxes (sorted by y) into messages: lines of one message have the same font and size, the same left edge
    or centre, and are stacked closely."""
    groups = []
    for r in rs:
        for g in groups:
            q = g[-1]
            if q['font'] == r['font'] and q['size'] == r['size'] and r['y0'] - q['y1'] < r['size'] and \
                    (abs(q['x0'] - r['x0']) < 3 or abs((q['x0'] + q['x1']) - (r['x0'] + r['x1'])) < 6):
                g.append(r)
                break
        else:
            groups.append([r])
    return groups


def analyse(rec, scenes, holds):
    found = defaultdict(list)        # (kind, scene, text, detail) -> [times]
    glyphs = defaultdict(dict)       # scene -> text -> (glyph px, font, size)
    nsec = defaultdict(list)         # scene -> [(T, [texts])]
    nkey = defaultdict(int)          # scene -> most key messages on screen at once
    frames = 0
    for T, boxes in sorted(rec.items(), key=lambda kv: float(kv[0])):
        T = float(T)
        t = source_time(T, holds)
        sc = next((s for s in scenes if t < s['t1']), scenes[-1])
        frames += 1
        vis = [r for r in boxes if r['alpha'] >= 0.5 and r['scale'] <= 1.02]
        for r in vis:
            if r['x0'] < -1 or r['x1'] > W + 1 or r['y0'] < -1 or r['y1'] > H + 1:
                found[('overflow', sc['id'], r['s'], box_s(r))].append(T)
            elif r['x0'] < 0.05 * W or r['x1'] > 0.95 * W or r['y0'] < 0.05 * H or r['y1'] > 0.95 * H:
                found[('margin', sc['id'], r['s'], box_s(r))].append(T)
            if r['alpha'] >= 0.9:
                g = glyphs[sc['id']].get(r['s'], (0, '', 0))
                if r['glyph'] > g[0]:
                    glyphs[sc['id']][r['s']] = (r['glyph'], r['font'], r['size'])
            if sc.get('clear') is not None and r['s'] != sc.get('clear_text', 'CLEAR!'):
                z = dict(x0=CLEAR_ZONE[0], y0=CLEAR_ZONE[1], x1=CLEAR_ZONE[2], y1=CLEAR_ZONE[3])
                if hit(r, z):
                    found[('clear', sc['id'], r['s'], box_s(r))].append(T)
        for i, a in enumerate(vis):
            for b in vis[i + 1:]:
                if hit(a, b):
                    found[('overlap', sc['id'], f"{a['s']!r} x {b['s']!r}", box_s(a))].append(T)
        sec = sorted((r for r in vis if r['alpha'] >= 0.9 and SECOND_PX <= r['glyph'] < KEY_PX
                      and not (r['s'].startswith('STAGE ') or r['s'] == sc.get('title'))), key=lambda r: r['y0'])
        groups = messages(sec)
        keys = messages(sorted((r for r in vis if r['alpha'] >= 0.9 and r['glyph'] >= KEY_PX
                                and not (r['s'].startswith('STAGE ') or r['s'] == sc.get('clear_text', 'CLEAR!') or r['s'] == sc.get('title'))), key=lambda r: r['y0']))
        nkey[sc['id']] = max(nkey[sc['id']], len(keys))
        if len(groups) > 1:
            nsec[sc['id']].append((T, [' / '.join(r['s'] for r in g) for g in groups]))

    lines = [f'LAYOUT LINT: {frames} frames sampled', '']
    counts = {}
    for kind, label in (('overflow', 'text outside the frame'), ('margin', 'text in the outer 5 %'),
                        ('overlap', 'texts overlapping'), ('clear', 'text in the CLEAR! zone')):
        items = sorted((k for k in found if k[0] == kind), key=lambda k: (found[k][0], k))
        counts[kind] = len(items)
        lines.append(f'== {kind}: {label} ({len(items)}) ==')
        for k in items:
            ts = found[k]
            lines.append(f'  {k[1]:8s} {k[2]!r:48.48s} {k[3]}  t={ts[0]:g}..{ts[-1]:g} ({len(ts)} samples)')
        lines.append('')
    lines.append('== phone: glyph height by scene (key >= 50 px, secondary >= 35 px, glance below) ==')
    nokey, multi, glance_total = [], [], 0
    for s in scenes:
        g = glyphs.get(s['id'], {})
        hud_t = {s.get('title', '')}
        body = {k: v for k, v in g.items() if not (k.startswith('STAGE ') or k == s.get('clear_text', 'CLEAR!') or k in hud_t)}
        key = sorted(k for k, v in body.items() if v[0] >= KEY_PX)
        sec = sorted(k for k, v in body.items() if SECOND_PX <= v[0] < KEY_PX)
        gl = sorted(k for k, v in body.items() if v[0] < SECOND_PX)
        glance_total += len(gl)
        if not key:
            nokey.append(s['id'])
        elif nkey[s['id']] > 1:
            multi.append(s['id'])
        lines.append(f"  {s['id']:8s} key {len(key)} texts / {nkey[s['id']]} at once, secondary {len(sec)}, glance {len(gl)}"
                     + (f"  [glance: {', '.join(repr(x) for x in gl)}]" if gl else '')
                     + ('' if key else '  ** NO KEY MESSAGE >= 50 px **'))
    lines.append('')
    n2 = sum(len(v) for v in nsec.values())
    lines.append(f'== phone: frames with more than one secondary message (stacked lines count as one), HUD excluded ({n2}) ==')
    for sid, lst in nsec.items():
        lines.append(f"  {sid:8s} t={lst[0][0]:g}..{lst[-1][0]:g} ({len(lst)} samples): {lst[0][1]}")
    summary = (f"lint: overflow {counts['overflow']}, margin {counts['margin']}, overlap {counts['overlap']}, "
               f"clear-zone {counts['clear']}, scenes without a 50 px key {len(nokey)} {nokey}, scenes with 2+ keys at once {len(multi)} {multi}, "
               f"frames with 2+ secondaries {n2}, glance texts {glance_total}")
    lines += ['', summary]
    return '\n'.join(lines) + '\n', summary
