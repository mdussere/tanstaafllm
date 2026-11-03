"""Reading audit, computed from the template text slots (rules of Story 2's timing.py).

ORIENT 0.4 s to notice a new screen, then 0.25 s per word in VT323 mixed case and 0.30 s in Press Start 2P
capitals; the last text needs at least MIN_HOLD. The shortfall becomes a hold rounded up to whole beats
(SNAP 0.5 s); a shortfall under TOLERANCE is dropped. A screen is a scene, or a part of it (`screens:` in the script).
"""
import math

import slots as S

ORIENT, MIN_HOLD = 0.4, 1.0
PER_WORD = {'P': 0.30, 'V': 0.25}
SNAP, TOLERANCE = 0.5, 0.1


def words(s):
    return len([w for w in s.replace('/', ' ').split() if any(c.isalnum() for c in w)])


def screens(scenes, ep):
    """[(name, cut_abs, [(readable_abs, text, font)])]"""
    out = []
    for i, sc in enumerate(scenes):
        sl = [(sc['t0'] + r, s, f) for r, s, f in S.slots_of(sc, ep)]
        end = sc['t1'] - sc.get('cut_lead', S.LEAD.get(sc['template'], 0.0))
        parts = sc.get('screens') or [{'name': f"{i} {sc['id']}"}]
        cuts = [sc['t0'] + p['cut'] for p in parts[:-1]] + [end]
        lo = sc['t0']
        for p, cut in zip(parts, cuts):
            out.append((p['name'], cut, [e for e in sl if lo <= e[0] <= cut + 1e-9]))
            lo = cut
    return out


def audit(scenes, ep):
    rows = []
    for name, cut, elems in screens(scenes, ep):
        if not elems:
            continue
        first = min(e[0] for e in elems)
        last_t, last_s, last_f = max(elems, key=lambda e: e[0])
        need_last = max(MIN_HOLD, ORIENT + words(last_s) * PER_WORD[last_f])
        have_last = cut - last_t
        need_total = ORIENT + sum(words(s) * PER_WORD[f] for _, s, f in elems)
        hold = max(0.0, need_last - have_last)
        hold = SNAP * math.ceil((hold - TOLERANCE) / SNAP) if hold > TOLERANCE else 0.0
        rows.append(dict(screen=name, cut=round(cut, 3), last=last_s, words=words(last_s), have_last=round(have_last, 2),
                         need_last=round(need_last, 2), have_total=round(cut - first, 2), need_total=round(need_total, 2),
                         hold=round(hold, 1)))
    return rows


def table(rows):
    lines = ['| Screen | Last text before the cut | Words | Last on screen | Needed | Whole screen | Needed | Hold added |',
             '|---|---|---|---|---|---|---|---|']
    for r in rows:
        h = '+' + format(r['hold'], '.1f') + ' s' if r['hold'] else '-'
        lines.append(f"| {r['screen']} | {r['last'][:48]} | {r['words']} | {r['have_last']:.2f} s | {r['need_last']:.2f} s "
                     f"| {r['have_total']:.2f} s | {r['need_total']:.2f} s | {h} |")
    extra = sum(r['hold'] for r in rows)
    lines.append(f"\nHolds: +{extra:.1f} s.")
    return '\n'.join(lines), extra
