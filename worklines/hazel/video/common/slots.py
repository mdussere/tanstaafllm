"""Text slots of each template, for the reading audit: [(seconds from the scene start when the text is readable,
text, font 'P' or 'V')]. Only key and secondary messages are listed (phone rule); glance text is left out.

Register a new template by adding a function to SLOTS (and, for T05 content kinds, a branch in item_slots).
`lead` is how long before the scene end the text starts to disappear (a dissolve or a closing flash): the cut.
"""


def _join(lines):
    return ' '.join(l if isinstance(l, str) else l['s'] for l in lines)


def item_slots(it):
    """Slots of one T05 content item that carries `read` (true, or the text to count)."""
    r = it.get('read')
    if not r:
        return []
    font = 'V' if it.get('font') == 'V' else 'P'
    kind = it['kind']
    text = r if isinstance(r, str) else None
    if kind == 'text':
        fade = it.get('fade', 0.2)
        lines = it.get('lines', [])
        if any(not isinstance(l, str) for l in lines):                 # lines with their own times
            return [(l['at'] + fade, l['s'], font) for l in lines]
        return [(it.get('read_at', it['at'] + fade), text or _join(lines), font)]
    if kind == 'stamp':
        return [(it.get('read_at', it['at'] + 0.15), text or _join(it['lines']), font)]
    if kind == 'runs':
        return [(it.get('read_at', it['at'] + it.get('fade', 0.1)), text or ''.join(p[0] for p in it['parts']), font)]
    if kind == 'tiles':
        t, k, v = it['tiles'][-1]
        return [(t + 0.1, f'{k} {v}', 'P')]
    if kind == 'pipe':
        return [(max(l['at'] for l in it['labels']) + 0.1, text or _join([l['s'] for l in it['labels']]), 'P')]
    raise ValueError(f'item kind {kind} has no audit slot')


def t05(sc, ep):
    out = [(0.3, f"STAGE {sc['stage']} {sc['title']}", 'P')]
    for it in sc.get('content', []):
        out += item_slots(it)
    return out


def t01(sc, ep):
    return [(0.5, sc['series'].replace('·', ' '), 'P'), (sc['title_at'] + 0.15, sc['title'], 'P'),
            (sc.get('sub_at', 1.4) + 0.2, ' '.join(sc['sub']), 'V')]


def t04(sc, ep):
    return [(0.45, f"{sc['label']} {sc['name']}", 'P'), (0.95, ' '.join(sc['role']), 'P'),
            (2.4, f"{sc['quest_label']} {' '.join(sc['quest'])}", 'V')]


def t21(sc, ep):
    sa = sc.get('stamp_at', 1.5)
    return [(sa + 0.15, sc['stamp'], 'P'), (sc.get('aside_at', 2.6) + 0.2, sc['aside'], 'V')]


def t22(sc, ep):
    return [(0.15, sc['headline'], 'P'), (sc.get('lesson_at', 1.2) + 0.15, ' '.join(sc['lesson']), 'P'),
            (sc.get('sub_at', 2.4) + 0.2, ' '.join(sc['sub']), 'V')]


def t23(sc, ep):
    return [(0.5, sc['motto'], 'V'), (0.8, sc['url'], 'P'), (1.1, sc['credit'], 'V')]


SLOTS = {'T01': t01, 'T04': t04, 'T05': t05, 'T21': t21, 'T22': t22, 'T23': t23}
LEAD = {'T01': 0.2, 'T04': 0.25, 'T21': 0.25, 'T23': 0.5}      # default cut lead per template
