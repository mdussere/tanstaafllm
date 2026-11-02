"""Script -> scenes: every template decides the layout (named slots, positions, sizes, colours), the entry choreography
(spread on the beat over the scene length) and the cue marks; the script only carries what a writer decides.

  resolve(ep, scenes) turns each script scene {template: <name>, key, secondary, glance, ...} into the scene the page,
  the score and the audit use: internal template id (T01 ... T23), `content` (items for the stage frame, drawn by
  templates.js KINDS), `marks` (where the music lands: cues.py), `slots` (what is readable when: audit.py) and `texts`.

Optional low-level overrides, for the rare scene that needs them: `at: {name: seconds}` moves a named element (the names
are the `b.at('name', default)` calls below), `content: [...]` appends raw stage items, `events: [...]` appends raw score events.

Phone rule: `key` is the one key message (VT323 90, or Press Start 2P 56 with `key_font: P`; at most 2 lines),
`secondary` is Press Start 2P 40 or VT323 64, `glance` labels are small (28) and never carry the story.
"""
import math

BEAT = 0.5
INTERNAL = {'title_card': 'T01', 'player_card': 'T04', 'tree': 'T21', 'result': 'T22', 'end_card': 'T23'}


def _l(v):
    return [] if v is None else ([v] if isinstance(v, str) else list(v))


def _dy(font, size):
    return size if font == 'V' else round(size * 1.35)


def _ceil(x):
    return math.ceil(x / BEAT - 1e-9) * BEAT


def _snap(x):
    return round(x / BEAT) * BEAT


def _opts(kw):
    return {('from' if k == 'since' else k): v for k, v in kw.items()}


class Build:
    """Collects the content items, the cue marks and the audit slots of one scene."""

    def __init__(self, sc):
        self.sc = sc
        self.len = round(sc['t1'] - sc['t0'], 6)
        self.z = self.len - 1.5             # stage scenes: the CLEAR! stamp lands here
        self.content, self.marks, self.slots = [], [], []
        self.texts = {'key': [], 'secondary': [], 'glance': []}

    def at(self, name, default):
        return self.sc.get('at', {}).get(name, default)

    def mark(self, k, at, **kw):
        self.marks.append(dict(k=k, at=round(at, 4), **kw))

    def add(self, kind, **kw):
        self.content.append(dict(kind=kind, **_opts(kw)))

    def slot(self, at, text, font):
        self.slots.append((round(at, 4), text, font))

    def _note(self, role, lines, at, font):
        self.texts[role].append(' '.join(lines))
        if role != 'glance':
            self.slot(at, ' '.join(lines), font)

    # ---- text elements: key / secondary / glance ----------------------------------------------------------------
    def text(self, lines, x, y, at, size=28, color='chrome', font='P', dy=None, fade=0.2, role=None, **kw):
        lines = _l(lines)
        read_at = kw.pop('read_at', at + fade)
        it = dict(kind='text', lines=lines, x=x, y=y, at=at, size=size, color=color, fade=fade)
        if font == 'V':
            it['font'] = 'V'
        if len(lines) > 1:
            it['dy'] = dy or _dy(font, size)
        it.update(_opts(kw))
        self.content.append(it)
        if role:
            self._note(role, lines, read_at, font)

    def stamp(self, lines, x, y, at, size, color, role=None, dy=None, **kw):
        lines = _l(lines)
        it = dict(kind='stamp', lines=lines, x=x, y=y, at=at, size=size, color=color)
        if len(lines) > 1:
            it['dy'] = dy or _dy('P', size)
        it.update(_opts(kw))
        self.content.append(it)
        if role:
            self._note(role, lines, at + 0.15, 'P')

    def key(self, lines, at, x, y, color='chrome', font=None, size=None, stamp=True, **kw):
        """The key message: VT323 90 (faded in) or Press Start 2P 56 (stamped, or faded with stamp=False)."""
        font = font or self.sc.get('key_font', 'V')
        if font == 'V':
            self.text(lines, x, y, at, 90, color, 'V', role='key', **kw)
        elif stamp:
            self.stamp(lines, x, y, at, size or 56, color, role='key', **kw)
        else:
            self.text(lines, x, y, at, size or 56, color, 'P', role='key', **kw)
        self.mark('key', at)

    def second(self, lines, at, x, y, color='cyan', font='P', fade=0.15, **kw):
        """A secondary message: Press Start 2P 40 or VT323 64."""
        self.text(lines, x, y, at, 40 if font == 'P' else 64, color, font, fade=fade, role='secondary', **kw)
        self.mark('second', at)

    def glance(self, lines, at, x, y, color='dim', fade=0.1, **kw):
        """A small label (28 px): nothing the story depends on."""
        self.text(lines, x, y, at, 28, color, 'P', fade=fade, role='glance', **kw)

    def finish(self, tpl, **fields):
        sc = dict(self.sc)
        sc.update(fields)
        sc['template'] = tpl
        sc['content'] = self.content + list(sc.get('content', []))
        sc['marks'] = sorted(self.marks, key=lambda m: m['at'])
        sc['slots'] = sorted(self.slots)
        sc['texts'] = self.texts
        return sc


# ====================================================================== stage templates (the stage frame: HUD, CLEAR!)
def t_guess(b):
    """An agent guesses from a blurry screenshot: `guesses` chips, each costing a coin; `key` and `secondary` below."""
    sc, v = b.sc, b.at('visual', 0.5)
    gs = _l(sc['guesses'])
    b.add('pixel_grid_guess', at=v, agent_at=v + 0.5, guesses=[[v + 1.0 + BEAT * i, g] for i, g in enumerate(gs)])
    b.mark('enter', v, i=0)
    for i in range(len(gs)):
        b.mark('coin', v + 1.0 + BEAT * i)
    b.key(sc['key'], b.at('key', 1.0), 120, 740)
    b.second(sc['secondary'], b.at('secondary', b.z - 1.5), 120, 945)
    return {}


def t_two_boxes(b):
    """A first idea that failed (`fail: {label, glance: [2 lines], stamp}`), then what was kept (`works` label, `key`)."""
    sc, f = b.sc, b.sc['fail']
    works = b.at('works', b.z - 3.0)
    fail_t, spill, first = works - 1.0, works - 2.0, b.at('first', 0.5)
    g = _l(f.get('glance'))
    b.add('scene_spill', label=f['label'], at=first, gone_at=fail_t, spill_at=spill, spill_step=0.15)
    b.mark('enter', first, i=0)
    for i in range(5):
        b.mark('enter', spill + 0.15 * i, i=i + 1)
    b.glance(g[0], first + 0.1, 980, 330)
    b.stamp(f['stamp'], 980, 500, fail_t, 48, 'red', rot=-0.05)
    b.slot(fail_t + 0.15, f['stamp'], 'P')
    b.texts['secondary'].append(f['stamp'])
    b.mark('fail', fail_t)
    b.glance(g[1], fail_t + 0.3, 980, 380)
    b.add('box', x=140, y=650, w=1640, h=230, edge='green', alpha=0.95, at=works - 0.3, fade=0.2)
    b.glance(sc['works'], works - 0.3, 190, 705, 'amber')
    b.mark('turn', works)
    b.key(sc['key'], works, 960, 785, 'green', font='P', align='center', dy=70, **{'from': 1.4})
    return {}


def t_metrics(b):
    """A subject (`subject: {label, tags, link}`) and its measured figures `tiles` [{label, value, machine}]; `glance` caption."""
    sc, s = b.sc, b.sc['subject']
    tags = _l(s.get('tags'))
    b.key(sc['key'], b.at('key', 0.5), 120, 300, 'cyan')
    sub = b.at('subject', 1.0)
    b.add('box', x=120, y=430, w=560, h=440, edge='green', since=sub)
    b.add('minidesk', x=150, y=460, w=500, h=240, focus='cycle', since=sub)
    b.mark('enter', sub, i=0)
    b.text(s['label'], 150, 760, sub, 32, 'chrome', fade=0, role='glance')
    for i, tg in enumerate(tags):
        b.glance(tg, sub + BEAT * (i + 1), 150, 805 + 40 * i, ['green', 'amber', 'cyan'][i % 3])
        b.mark('enter', sub + BEAT * (i + 1), i=i + 1)
    link = sub + BEAT * (len(tags) + 1)
    if s.get('link'):
        b.add('rects', since=link, rects=[[680, 570, 60, 24, '#8e97cc'], [740, 560, 20, 44, '#cfd6ff']])
        b.text(s['link'], 690, 650, link, 28, 'cyan', fade=0, role='glance')
        b.mark('enter', link, i=len(tags) + 1)
    if sc.get('glance'):
        b.glance(sc['glance'], link, 800, 460)
    tiles = [t if isinstance(t, dict) else dict(zip(('label', 'value', 'machine'), t)) for t in sc['tiles']]
    t0, rows = b.at('tiles', b.z - 3.5), []
    for i, t in enumerate(tiles):
        ti = t0 + BEAT * i
        rows.append([ti, t['label'], t['value'], t.get('machine', sc.get('machine', ''))])
        b.add('packet', at=ti - 0.3, dur=0.3, x0=760, x1=780, y=582, color='cyan')
        b.mark('reveal', ti, i=i)
    b.add('tiles', x=800, y=485, tiles=rows)
    for r in rows:                                  # every figure is read: each tile is an audit slot
        b.slot(r[0] + 0.1, f'{r[1]} {r[2]}', 'P')
    b.texts['secondary'] += [f'{r[1]} {r[2]}' for r in rows]
    return {}


def t_flow(b):
    """An agent talks to a `target` through a pipe (`via` labels): packets go out and come back; `key` left, `secondary` right."""
    sc, z = b.sc, b.z
    via = _l(sc['via'])
    pipe, pk = b.at('pipe', 0.5), b.at('packets', 1.5)
    times = [pk, pk + 0.5, pk + 1.0, pk + 2.0]
    act = times[2] + 0.4
    b.add('agent', x=140, y=280, s=9, mode='ask')
    b.mark('enter', 0, i=0)
    b.add('pipe', x0=350, x1=1380, y=400, since=pipe, labels=[
        dict(s=v, dy=(-40, 70)[i % 2], color=('cyan', 'amber')[i % 2], at=pipe + BEAT * i) for i, v in enumerate(via)])
    b.texts['glance'] += via
    b.mark('enter', pipe, i=1)
    b.add('box', x=1400, y=250, w=400, h=300, edge='green')
    b.add('minidesk', x=1424, y=274, w=352, h=220, focus=[[0, 0], [act, 2]])
    b.text(sc['target'], 1600, 535, 0, 28, 'chrome', fade=0, align='center', role='glance')
    for i, ti in enumerate(times):
        out = i % 2 == 0
        b.add('packet', at=ti, dur=0.4, x0=350 if out else 1380, x1=1380 if out else 350, y=400,
              color=('cyan', 'green', 'amber', 'green')[i])
        b.mark('packet', ti, dir=1 if out else -1)
    b.mark('press', act)
    b.key(sc['key'], b.at('key', 1.0), 120, 700)
    sec = b.at('secondary', z - 2.5)
    b.stamp(sc['secondary'], 1560, 700, sec, 48, 'amber', align='center', rot=-0.04, role='secondary')
    b.mark('second', sec)
    if sc.get('glance'):
        b.glance(sc['glance'], sec + 0.3, 1560, 765, 'cyan', align='center')
    return {}


def t_boss(b):
    """A boss with two `phases` [{key, secondary, glance?}] and a `panel` caption: the handheld's panel is black, then lit."""
    sc = b.sc
    p1, p2 = sc['phases']
    v = b.at('victory', b.z - 2.0)
    hit = b.at('hit', v - 2.0)
    b.add('boss_hud', hit1=hit, fix=v, labels=_l(sc.get('states')) or ['BLACK', 'LIT'])
    b.add('handheld', x=170, y=250, s=5.5, bob=True, focus='cycle', states=[[0, 'black'], [v, 'flash'], [v + 0.1, 'desk']])
    b.glance(sc['panel'], 0.5, 760, 300, 'cyan')
    b.key(p1['key'], 1.0, 760, 440, 'red', font='P', size=64, rot=-0.04, until=v)
    b.mark('hit', hit)
    b.second(p1['secondary'], 2.0, 760, 560, 'chrome', font='V', fade=0.2, until=v, maxW=1040)
    if p1.get('glance'):
        b.glance(p1['glance'], 3.0, 760, 740, until=v)
    b.key(p2['key'], v, 760, 440, 'green', font='P', stamp=False, fade=0, read_at=v + 0.1)
    b.mark('victory', v)
    b.add('box', x=760, y=600, w=460, h=130, edge='green', fill='#05060f', alpha=0.95, since=v + 0.3)
    b.second(p2['secondary'], v + 0.3, 760 + 40, 690, 'green', font='V', fade=0, shadow=0)
    return dict(screens=[dict(name='boss: ' + ' '.join(_l(p1['key'])), cut=v), dict(name='boss: ' + ' '.join(_l(p2['key'])))],
                flashes=[[v, 0, 0.25], [0, 0, 0.4, 'red']])


def t_handheld(b):
    """The handheld with two `parts`. A: {key, chips [[button label, action, device button]], glance [2], secondary, screen}.
    B: {key, glance, combo {label, keys, face}, secondary, screen, agent}. Part B starts at a cut on a beat (about 55 %)."""
    pa, pb = b.sc['parts']
    cut = b.at('cut', _snap(b.len * 0.55))
    chips = pa['chips']
    ct = [b.at('chips', 1.5) + 0.25 * i for i in range(len(chips))]
    glance_a = ct[-1] + 0.25
    sec_a = b.at('secondary', glance_a + 0.5)
    kb, cb = cut + 0.5, cut + 1.0
    sec_b = cut + 1.5
    presses = [{'from': t, 'to': t + 0.2, 'btns': ['FN', c[2]]} for t, c in zip(ct, chips)]
    presses += [{'from': sec_a - 0.2, 'to': sec_a, 'btns': ['L1']}, {'from': cb, 'to': cb + 0.3, 'btns': pb['combo']['keys']}]
    b.add('handheld', x=170, y=250, s=5.5, bob=True, focus=[[0, 0], [ct[0], 1]], ws=[[0, 0], [ct[-1], 1], [cut - 0.5, 0]],
          states=[[0, 'desk'], [sec_a, pa.get('screen', 'slate')], [cb + 0.4, pb.get('screen', 'mike')]],
          answer_at=cb + 0.6, presses=presses)
    b.key(pa['key'], 0.5, 760, 330, until=cut, maxW=1040)
    b.add('actions', x=760, y=380, until=cut, actions=[[t] + c[:2] for t, c in zip(ct, chips)])
    for t in ct:
        b.mark('press', t)
    b.glance(pa['glance'][0], glance_a, 760, 580, until=cut)
    b.second(pa['secondary'], sec_a, 760, 700, 'amber', until=cut)
    b.mark('press', sec_a - 0.2)
    b.glance(pa['glance'][1], sec_a + 0.5, 760, 830, until=cut)
    b.add('flash', at=cut, up=0, down=0.25, since=cut)
    b.mark('cut', cut)
    b.key(pb['key'], kb, 680, 330, since=cut)
    if pb.get('agent', True):
        b.add('agent', x=1660, y=365, s=5, mode='ask', since=cut)
    b.glance(pb['glance'], cb, 680, 490, since=cut)
    cm = pb['combo']
    b.add('key_combo', x=680, y=545, at=cb, result_at=cb + 0.3, label=cm['label'], keys=cm['keys'], face=cm.get('face', 'mike'), since=cut)
    b.texts['glance'].append(cm['label'])
    b.mark('press', cb)
    b.mark('press', cb + 0.1)
    b.second(pb['secondary'], sec_b, 680, 790, 'green', since=cut)
    return dict(screens=[dict(name='buttons: ' + ' '.join(_l(pa['key'])), cut=cut), dict(name='agent: ' + ' '.join(_l(pb['key'])))])


def t_checklist(b):
    """`items` ticked in turn. `claim` (1-based item) is declared done, `fail` (item) shows it was not; `secondary` is
    [claim text, fail text], `glance` the 2-line setting upper left, `key` the lesson, stamped when the last item ticks."""
    sc = b.sc
    items = _l(sc['items'])
    c, f = sc['claim'], sc['fail']
    claim_t = b.at('claim', 2.5)
    fail_t = claim_t + 0.5
    resume = b.at('resume', fail_t + 2.0)
    ok = [1.5 + 0.25 * i if i < c else resume + BEAT * (i - c) for i in range(len(items))]
    gl, sec = _l(sc['glance']), _l(sc['secondary'])
    b.glance(gl[0], 0.5, 120, 290, fade=0.2)
    b.glance(gl[1], 0.5, 120, 335, 'chrome', fade=0.2)
    b.second(sec[0], claim_t, 120, 470, 'amber')
    b.second(sec[1], fail_t, 120, 535, 'red', dy=54)
    b.add('layers', since=0.9, x=1000, y=230, w=800, names=items, ok=ok, fail=dict(layer=f - 1, at=fail_t),
          highlight={'layer': c - 1, 'from': claim_t, 'until': resume}, unknown_from=dict(layer=c, at=claim_t))
    for i, t in enumerate(ok):
        b.mark('ok', t, i=i)
    b.mark('fail', fail_t)
    b.mark('turn', resume)
    b.key(sc['key'], ok[-1] + 0.5, 120, 840, font='P', dy=75, **{'from': 1.4})
    return {}


def t_compare_table(b):
    """A two-column comparison built row by row on the beat: `columns` [left, right] (header pair), `rows` [[left, right]];
    `key` above the table (2 lines)."""
    sc = b.sc
    cols, rows = _l(sc['columns']), sc['rows']
    b.key(sc['key'], b.at('key', 0.5), 120, 300, 'cyan')
    t0 = b.at('rows', 1.5)
    items = [[t0 + BEAT * i, r[0], r[1]] for i, r in enumerate([cols] + [list(r) for r in rows])]
    b.add('table', x=120, y=450, w=1680, rh=75, rows=items)
    for i, r in enumerate(items):
        b.mark('enter', r[0], i=i)
        b.texts['glance'].append(f'{r[1]} {r[2]}')
    return {}


STAGE_FN = {'guess': t_guess, 'two_boxes': t_two_boxes, 'metrics': t_metrics, 'flow': t_flow, 'boss': t_boss,
            'handheld': t_handheld, 'checklist': t_checklist, 'compare_table': t_compare_table}


# ====================================================================== frame templates (their own full-screen layouts)
def f_title_card(b):
    """`series` line (glance), the stamped `key` title, a 2-line `secondary` subtitle, PRESS START."""
    sc = b.sc
    ka, sa = b.at('key', 1.0), b.at('secondary', 1.5)
    b.texts['glance'] += [sc['series'], 'PRESS START']
    b.texts['key'].append(sc['key'])
    b.texts['secondary'].append(' '.join(sc['secondary']))
    b.slot(0.5, sc['series'].replace('·', ' '), 'P')
    b.slot(ka + 0.15, sc['key'], 'P')
    b.slot(sa + 0.2, ' '.join(sc['secondary']), 'V')
    return dict(key_at=ka, secondary_at=sa, glance_at=0.5, press_at=sa + 1.5)


def f_player_card(b):
    """A character box (`face`), `glance` [label, quest label], `name` + `secondary` role lines, the quest `key`."""
    sc = b.sc
    ra, ka = b.at('secondary', 1.0), b.at('key', 2.5)
    gl, role, key = _l(sc['glance']), _l(sc['secondary']), _l(sc['key'])
    b.texts['glance'] += gl
    b.texts['secondary'].append(' '.join([sc['name']] + role))
    b.texts['key'].append(' '.join(key))
    b.slot(0.45, f"{gl[0]} {sc['name']}", 'P')
    b.slot(ra - 0.05, ' '.join(role), 'P')
    b.slot(ka + 0.15, f"{gl[1]} {' '.join(key)}", 'V')
    return dict(glance=gl, key=key, secondary=role, key_at=ka, secondary_at=ra)


def f_tree(b):
    """The agent calls a tool (`glance` [call]); a tree of `nodes` [[depth, label]] comes back; `key` stamped, `secondary` aside."""
    sc = b.sc
    na = b.at('nodes', 1.0)
    ka = b.at('key', _ceil(na + 0.12 * len(sc['nodes'])))
    sa = b.at('secondary', ka + 1.0)
    b.texts['glance'] += _l(sc['glance'])
    b.texts['key'].append(sc['key'])
    b.texts['secondary'].append(sc['secondary'])
    b.slot(ka + 0.15, sc['key'], 'P')
    b.slot(sa + 0.2, sc['secondary'], 'V')
    return dict(glance=_l(sc['glance']), call_at=0.5, nodes_at=na, key_at=ka, secondary_at=sa)


def f_result(b):
    """A heading (`title`), one pip per stage, the lesson (`key`, 2 lines), the closing line (`secondary`, 2 lines)."""
    sc = b.sc
    ka, sa = b.at('key', 1.0), b.at('secondary', 2.5)
    key, sec = ' '.join(_l(sc['key'])), ' '.join(_l(sc['secondary']))
    b.texts['key'].append(key)
    b.texts['secondary'].append(sec)
    b.slot(0.15, sc['title'], 'P')
    b.slot(ka + 0.15, key, 'P')
    b.slot(sa + 0.2, sec, 'V')
    return dict(key=_l(sc['key']), secondary=_l(sc['secondary']), key_at=ka, secondary_at=sa)


def f_end_card(b):
    """The logo, the motto (`key`, 2 lines), `glance` [address, credit], PRESS START."""
    sc = b.sc
    ka = b.at('key', 0.5)
    key = ' '.join(_l(sc['key']))
    b.texts['key'].append(key)
    b.texts['glance'] += _l(sc.get('glance'))
    b.slot(ka, key, 'V')
    return dict(key=_l(sc['key']), glance=_l(sc.get('glance')), key_at=ka, glance_at=ka + 0.5)


FRAME_FN = {'title_card': f_title_card, 'player_card': f_player_card, 'tree': f_tree, 'result': f_result, 'end_card': f_end_card}


def check_times(sc, end):
    """Every cue mark and audit slot of a resolved scene must fall in 0..end (a stage: its CLEAR! stamp; a frame: its
    length). A template spreads its elements from the scene length; a scene too short for them would place some before
    its start or after its stamp, where they are never drawn or never read."""
    eps = 1e-6
    bad = [f"{m['k']} at {m['at']:g}" for m in sc['marks'] if not -eps <= m['at'] <= end + eps]
    bad += [f"{text[:32]!r} at {at:g}" for at, text, _ in sc['slots'] if not -eps <= at <= end + eps]
    if bad:
        raise ValueError(f"scene {sc['id']} ({sc['bars']} bars): elements outside 0..{end:g} s: {', '.join(bad)}; "
                         "lengthen the scene or move them with `at:`")


def resolve(ep, scenes):
    out, n = [], 0
    for sc in scenes:
        tpl = sc['template']
        b = Build(sc)
        try:
            if tpl in STAGE_FN:
                n += 1
                fields = STAGE_FN[tpl](b)
            elif tpl in FRAME_FN:
                fields = FRAME_FN[tpl](b)
            else:
                raise ValueError(f'unknown template {tpl!r} in scene {sc["id"]}')
        except (KeyError, IndexError, TypeError) as e:     # a missing or malformed slot in the script
            raise ValueError(f"scene {sc['id']}: template {tpl!r} cannot read its slots ({type(e).__name__}: {e}); "
                             "see the slot table in common/README.md") from e
        if tpl in STAGE_FN:
            r = b.finish('T05', stage=n, clear=b.z, clear_text=sc.get('clear_text', 'CLEAR!'),
                         clear_color=sc.get('clear_color', 'green'), **fields)
            check_times(r, r['clear'])
        else:
            r = b.finish(INTERNAL[tpl], **fields)
            check_times(r, b.len)
        out.append(r)
    return out
