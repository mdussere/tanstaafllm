"""Text slots for the reading audit: [(seconds from the scene start when the text is readable, text, font 'P' or 'V')].
Only key and secondary messages are listed (phone rule); glance text is left out. layout.py records the slots of every
template (`sc['slots']`); `item_slots` covers raw stage items with `read`. LEAD is how long before the scene end the
text starts to disappear (a dissolve or a closing flash): the cut.
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


def slots_of(sc, ep):
    """[(seconds from the scene start when the text is readable, text, font)]: the slots the layout recorded (key and
    secondary messages), plus any raw stage item that carries `read`. Glance text is never listed (phone rule)."""
    out = list(sc.get('slots', []))
    for it in sc.get('content', []):
        out += item_slots(it)
    if sc['template'] == 'T05' and sc.get('title'):
        out.append((0.3, f"STAGE {sc['stage']} {sc['title']}", 'P'))     # the HUD title every stage frame shows
    return sorted(out)


LEAD = {'T01': 0.2, 'T04': 0.25, 'T21': 0.25, 'T23': 0.5}      # default cut lead per template: the closing dissolve
