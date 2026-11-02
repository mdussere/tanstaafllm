// TANSTAAFLLM shared video templates: parametric scene functions on top of runtime.js.
//
// A template is TPL[id](t, p): t is the source time in seconds (absolute, holds removed), p is the scene
// object from the episode script plus p.t0 / p.t1 (scene start and end). Every event time in p is
// RELATIVE to the scene start (A(x) = p.t0 + x makes it absolute). Animations that depend on the
// phase of t (bob, blinks, shake) use the absolute t, so a scene looks the same wherever it is placed
// on a bar line that is a multiple of its animation period (all scenes start on even seconds).
//
// The stage frame (T05) is a container: it draws the stage background, the HUD and a list of content
// items (KINDS), then the CLEAR! stamp and the cut flashes. Each content kind is a function
// KINDS[kind](t, p, item). Items can be gated with from / until (relative seconds).
//
// Text draws go through txt() / runs() in runtime.js, which record their boxes for the layout lint.
// The audit side of each template (what text it shows and when it becomes readable) is in slots.py;
// the music side is in cues.py. Keep the three in step when you add a template.
'use strict';
const TPL = {}, KINDS = {};
const col = c => (C[c] !== undefined ? C[c] : c);
const dflt = (v, d) => (v === undefined ? d : v);
const pick = (o, keys) => { const r = {}; for (const k of keys) if (o[k] !== undefined) r[k] = o[k]; return r; };
// A value that changes over time: a number, 'cycle' (a focus that walks 0,1,2 twice a second), or [[from, value], ...].
function steps(t, p, v, def = 0) {
  if (v === 'cycle') return Math.floor(t * 2) % 3;
  if (Array.isArray(v)) { let r = def; for (const [f, val] of v) if (t >= p.t0 + f) r = val; return r; }
  return v === undefined ? def : v;
}

// ======================================================================= content kinds
// text: lines of one font at one place. font 'P' (Press Start 2P) or 'V' (VT323, shadow 3 like V()).
// lines: strings, or { s, at } when a line has its own time. at/fade: fade-in; fade 0 = no fade. blink: Hz.
KINDS.text = (t, p, it) => {
  const font = dflt(it.font, 'P'), fade = dflt(it.fade, 0.2);
  const o = pick(it, ['align', 'maxW', 'shadow', 'rot', 'scale']);
  if (font === 'V') { o.font = 'V'; if (o.shadow === undefined) o.shadow = 3; }
  (it.lines || [it.s]).forEach((ln, i) => {
    const s = typeof ln === 'string' ? ln : ln.s, at = p.t0 + (typeof ln === 'string' ? it.at : ln.at);
    if (t < at) return;
    if (it.blink && Math.floor(TA * it.blink) % 2 !== 0) return;
    const a = fade ? seg(t, at, at + fade) : 1;
    if (a <= 0) return;
    txt(s, it.x, it.y + i * (it.dy || 0), it.size || 28, col(it.color || 'chrome'), Object.assign({ alpha: a }, o));
  });
};
// runs: one line of coloured pieces: parts [[text, colour], ...]
KINDS.runs = (t, p, it) => {
  const at = p.t0 + it.at, fade = dflt(it.fade, 0.1);
  if (t < at) return;
  runs(it.parts.map(([s, c]) => [s, col(c)]), it.x, it.y, it.size || 28, Object.assign({ alpha: fade ? seg(t, at, at + fade) : 1 }, pick(it, ['align', 'maxW', 'font'])));
};
// stamp: lines that slam in (scale-in with shake) at `at`
KINDS.stamp = (t, p, it) => {
  const o = pick(it, ['align', 'from', 'rot', 'maxW', 'font']);
  (it.lines || [it.s]).forEach((s, i) => stampTxt(s, it.x, it.y + i * (it.dy || 0), it.size || 48, col(it.color || 'chrome'), t, p.t0 + it.at, o));
};
KINDS.box = (t, p, it) => {
  const a = it.fade ? seg(t, p.t0 + it.at, p.t0 + it.at + it.fade) : 1;
  if (a <= 0) return;
  box(it.x, it.y, it.w, it.h, { edge: col(it.edge || 'chrome'), fill: it.fill, alpha: dflt(it.alpha, 0.92) * a });
};
KINDS.rects = (t, p, it) => it.rects.forEach(([x, y, w, h, c, a]) => rect(x, y, w, h, col(c), dflt(a, 1)));
KINDS.minidesk = (t, p, it) => miniDesk(it.x, it.y, it.w, it.h, { focus: steps(t, p, it.focus), ws: steps(t, p, it.ws), n: it.n, bright: it.bright });
KINDS.agent = (t, p, it) => agent(it.x, it.y + (it.bob ? Math.round(Math.sin(t * 6)) * 4 : 0), it.s || 10, t, it.mode || 'look');
KINDS.face = (t, p, it) => face(it.name, it.x, it.y, it.s);
KINDS.flash = (t, p, it) => flash(t, p.t0 + it.at, dflt(it.up, 0), dflt(it.down, 0.3), col(it.color || '#fff'));
KINDS.packet = (t, p, it) => packet(t, p.t0 + it.at, p.t0 + it.at + it.dur, it.x0, it.x1, it.y, col(it.color));

// T18 pixel-grid guess: the screen as a blurry screenshot, a squinting agent, a guess chip + coin per guess.
KINDS.pixel_grid_guess = (t, p, it) => {
  const A = x => p.t0 + x, b = dflt(it.block, 35);
  if (t > A(it.at)) {
    box(M, 230, 760, 400);
    miniDesk(M + 30, 260, 700, 340, { focus: 1, bright: true });
    pixelate(M + 30, 260, 700, 340, b);
    for (let y = 260; y < 600; y += b) rect(M + 30, y, 700, 2, C.ink, 0.35);
    for (let x = M + 30; x < M + 730; x += b) rect(x, 260, 2, 340, C.ink, 0.35);
  }
  if (t > A(it.agent_at)) agent(960, 300 + Math.round(Math.sin(t * 6)) * 4, 10, t, it.agent || 'squint');
  it.guesses.forEach(([t0r, s], i) => {
    const t0 = A(t0r);
    if (t < t0) return;
    const y = 290 + i * 100, a = seg(t, t0, t0 + 0.1);
    rect(1250, y - 46, measure(s, 28) + 40, 62, C.navy2, a); rect(1250, y - 46, 6, 62, C.amber, a);
    tag(s, 1270, y, C.amber, a);
    if (t < t0 + 0.6) coin(1230, y - 15 - 140 * seg(t, t0, t0 + 0.6), 3, t);
  });
};

// T06 two boxes (one scene that did not fit): the scene box with its A/B/X actions, then windows spill out.
KINDS.scene_spill = (t, p, it) => {
  const A = x => p.t0 + x;
  if (t > A(it.at)) {
    const gone = t > A(it.gone_at);
    box(M, 240, 760, 400, { edge: gone ? C.dim : C.chrome });
    txt(it.label, M + 50, 310, 32, gone ? C.dim : C.chrome);
    rect(M + 50, 340, 660, 160, '#0c1440');
    rect(M + 70, 360, 620, 24, '#3b4178'); rect(M + 70, 400, 400, 14, '#5c64a8'); rect(M + 70, 430, 300, 14, '#5c64a8');
    ['A', 'B', 'X'].forEach((k, i) => {
      const cx = M + 120 + i * 200, cy = 570;
      ctx.save(); ctx.fillStyle = gone ? '#3b4178' : [C.green, C.red, C.cyan][i]; ctx.beginPath(); ctx.arc(cx, cy, 36, 0, 7); ctx.fill(); ctx.restore();
      txt(k, cx, cy + 14, 28, C.ink, { align: 'center', shadow: 0 });
    });
  }
  const SPILL = [[M + 560, 240, 240, 160], [M + 20, 480, 280, 150], [M + 480, 450, 300, 170], [M - 20, 370, 220, 140], [M + 280, 290, 240, 140]];
  SPILL.forEach(([x, y, w, h], i) => {
    const t0 = A(it.spill_at) + i * dflt(it.spill_step, 0.15);
    if (t < t0) return;
    const pp = easeBack(seg(t, t0, t0 + 0.25));
    const cx = x + w / 2, cy = y + h / 2, ww = w * pp, hh = h * pp;
    rect(cx - ww / 2 + 8, cy - hh / 2 + 8, ww, hh, C.shadow);
    rect(cx - ww / 2, cy - hh / 2, ww, hh, '#3b4178'); rect(cx - ww / 2 + 4, cy - hh / 2 + 18, ww - 8, hh - 22, '#05060f');
  });
};

// T13 metric tiles: up to four boxes, each with a caption, a figure and the machine badge. tiles: [[at, caption, figure, badge], ...]
KINDS.tiles = (t, p, it) => {
  it.tiles.forEach(([t0r, k, v, bd], i) => {
    const t0 = p.t0 + t0r;
    if (t < t0) return;
    const x = it.x + (i % 2) * 510, y = it.y + Math.floor(i / 2) * 200, a = seg(t, t0, t0 + 0.1);
    box(x, y, 490, 185, { edge: C.cyan, alpha: 0.92 * a });
    tag(k, x + 30, y + 58, C.dim, a, { maxW: 430 });
    txt(v, x + 30, y + 120, 40, C.chrome, { alpha: a, scale: lerp(1.5, 1, easeOut(seg(t, t0, t0 + 0.15))) });
    tag(bd, x + 460, y + 160, C.cyan, a, { align: 'right' });
  });
};

// compare_table: two columns, one row per beat; rows: [[at, left, right]], the first row is the header
KINDS.table = (t, p, it) => {
  const half = it.w / 2;
  it.rows.forEach(([t0r, l, r], i) => {
    const t0 = p.t0 + t0r;
    if (t < t0) return;
    const a = seg(t, t0, t0 + 0.1), y = it.y + i * it.rh, head = i === 0;
    box(it.x, y, it.w, it.rh - 8, { edge: head ? C.amber : C.cyan, alpha: 0.92 * a });
    tag(l, it.x + 30, y + 46, head ? C.amber : C.dim, a, { maxW: half - 50 });
    tag(r, it.x + half + 30, y + 46, head ? C.amber : C.chrome, a, { maxW: half - 50 });
  });
};

// T14 flow / pipe: a pipe from x0 to x1 at height y with moving dashes and centred labels [{s, dy, color, at}]
KINDS.pipe = (t, p, it) => {
  const P0 = it.x0, P1x = it.x1, PY = it.y;
  rect(P0, PY - 16, P1x - P0, 32, '#5c64a8'); rect(P0, PY - 10, P1x - P0, 20, '#14173a');
  for (let x = P0 + 10 + (TA * 120) % 60; x < P1x - 20; x += 60) rect(x, PY - 3, 24, 6, '#3b4178');
  (it.labels || []).forEach(l => tag(l.s, (P0 + P1x) / 2, PY + l.dy, col(l.color), seg(t, p.t0 + l.at, p.t0 + l.at + 0.1), { align: 'center' }));
};

// T12 handheld with screen states. states: [[from, 'black'|'flash'|'desk'|'slate'|'mike'|'moon'|'none']], focus / ws: steps or 'cycle',
// presses: [{from, to, btns: [...]}] (lights the buttons in the window)
KINDS.handheld = (t, p, it) => {
  const A = x => p.t0 + x, s = dflt(it.s, 5.5), ox = it.x, oy = it.y + (it.bob ? Math.round(Math.sin(t * Math.PI) * 2) * 4 : 0);
  let scr = 'desk';
  for (const [f, st] of it.states) if (t >= A(f)) scr = st;
  luna(ox, oy, s, t, scr, { focus: steps(t, p, it.focus), ws: steps(t, p, it.ws), answerAt: it.answer_at === undefined ? undefined : A(it.answer_at) });
  (it.presses || []).forEach(pr => { if (t >= A(pr.from) && t < A(pr.to)) pr.btns.forEach(b => press(ox, oy, s, b)); });
};

// actions chips: two rows of two, [[at, button label, action label, device button]]
KINDS.actions = (t, p, it) => {
  it.actions.forEach(([t0r, k, s2], i) => {
    if (t < p.t0 + t0r) return;
    const x = it.x + (i % 2) * 530, y = it.y + Math.floor(i / 2) * 72;
    rect(x, y, 510, 58, C.navy2); rect(x, y + 52, 510, 6, C.cyan);
    tag(k, x + 16, y + 42, C.amber); tag(s2, x + 494, y + 42, C.cyan, 1, { align: 'right' });
  });
};

// key combo: a label, two keycaps with a plus, an arrow and the answering face (after `result_at`)
KINDS.key_combo = (t, p, it) => {
  const A = x => p.t0 + x, X = it.x, Y = dflt(it.y, 545);
  if (t > A(it.at)) {
    let x = X;
    tag(it.label, X, Y, C.amber);
    x += keycap(x, Y + 25, it.keys[0], t < A(it.result_at)) + 20;
    txt('+', x + 10, Y + 97, 32, C.chrome); x += 70;
    x += keycap(x, Y + 25, it.keys[1], t < A(it.result_at)) + 40;
    if (t > A(it.result_at)) {
      rect(x, Y + 77, 120, 12, C.cyan); arrowHead(x + 140, Y + 83, 1, C.cyan);
      box(x + 170, Y + 5, 150, 150, { edge: C.green });
      face(it.face, x + 185, Y + 20, 120);
    }
  }
};

// T19 layer stack: rows with a number, a name and a mark; ok: [at per layer]; one layer can fail, one can be highlighted
KINDS.layers = (t, p, it) => {
  const A = x => p.t0 + x, LX = it.x, LW = it.w, n = it.names.length, last = n - 1;
  it.names.forEach((s, i) => {
    const y = it.y + i * 74, ok = t >= A(it.ok[i]), fail = i === it.fail.layer && t >= A(it.fail.at) && !ok;
    const ver = i === it.highlight.layer && t >= A(it.highlight.from) && t < A(it.highlight.until);
    rect(LX, y, LW, 60, ver ? '#3a2a10' : (i % 2 ? C.navy2 : C.violet), 0.85);
    rect(LX, y, 60, 60, ok ? C.green : (fail ? C.red : '#3b4178'));
    txt(String(i + 1), LX + 30, y + 45, 28, C.ink, { align: 'center', shadow: 0 });
    tag(s, LX + 88, y + 45, i === last ? C.chrome : C.dim);
    if (ok) check(LX + LW - 64, y + 11, 38, C.green);
    else if (fail) cross(LX + LW - 62, y + 13, 34, C.red);
    else if (i >= it.unknown_from.layer && t > A(it.unknown_from.at)) txt('?', LX + LW - 45, y + 45, 28, C.dim, { align: 'center' });
  });
};

// T11 boss HUD: two hit pips (top right) and the state tag. hit1: first hit, fix: second hit (the fix)
KINDS.boss_hud = (t, p, it) => {
  const fixed = t >= p.t0 + it.fix, hits = (t >= p.t0 + it.hit1 ? 1 : 0) + (fixed ? 1 : 0);
  for (let i = 0; i < 2; i++) { const on = i >= hits; rect(W - M - 2 * 60 + i * 60, 88, 50, 26, C.shadow); rect(W - M - 2 * 60 + i * 60, 84, 50, 26, on ? C.red : C.navy2); }
  tag(fixed ? it.labels[1] : it.labels[0], W - M - 140, 110, fixed ? C.green : C.red, 1, { align: 'right' });
};

function drawItems(t, p) {
  for (const it of p.content || []) {
    if (it.from !== undefined && !(t >= p.t0 + it.from)) continue;
    if (it.until !== undefined && !(t < p.t0 + it.until)) continue;
    KINDS[it.kind](t, p, it);
  }
}

// ======================================================================= frame templates
// T05 stage frame: background, HUD (STAGE n + title), content items, CLEAR! stamp, flashes.
// flashes: [[at, up, down, colour]] drawn last; default one white flash going down over 0.3 s at the start.
TPL.T05 = (t, p) => {
  stageBg(t, p.stage); hud(t, p.stage, p.t0, p.title);
  drawItems(t, p);
  if (p.clear !== undefined) clearStamp(t, p.t0 + p.clear, p.clear_text, C[p.clear_color] || C.green);
  (p.flashes || [[0, 0, 0.3]]).forEach(([at, up, down, c]) => flash(t, p.t0 + at, up, down, c ? col(c) : '#fff'));
};

// T01 title card: `series` (glance), the stamped `key` title, a two-line `secondary` subtitle, PRESS START
TPL.T01 = (t, p) => {
  const A = x => p.t0 + x;
  rect(0, 0, W, H, C.ink); stars(t, 20, seg(t, A(0), A(1)) * 0.9);
  moon(W / 2, 1080 + 260, 1100, 0.35 * seg(t, A(0), A(1.5)));
  txt(p.series, W / 2, 330, 32, C.amber, { align: 'center', alpha: seg(t, A(p.glance_at), A(p.glance_at + 0.2)) });
  stampTxt(p.key, W / 2, 520, 100, C.chrome, t, A(p.key_at), { align: 'center', from: 2.0 });
  const ua = seg(t, A(p.secondary_at), A(p.secondary_at + 0.2));
  p.secondary.forEach((s, i) => V(s, W / 2, 640 + i * 70, 64, C.cyan, ua, { align: 'center' }));
  if (t > A(p.press_at) && Math.floor(TA * 2.5) % 2 === 0) txt('PRESS START', W / 2, 900, 28, C.amber, { align: 'center' });
  flash(t, A(p.key_at), 0, 0.25);
  flash(t, p.t1, 0.2, 0);
};

// T04 player card: the character box slides up; label + name, role lines (secondary), quest label (glance) + quest (key)
TPL.T04 = (t, p) => {
  const A = x => p.t0 + x;
  sky(C.navy, '#1a0f45'); stars(t, 25, 0.8);
  const bob = Math.round(Math.sin(t * Math.PI) * 2) * 4;
  const by = lerp(1200, 230, easeBack(seg(t, A(0), A(0.5)))) + bob;
  box(M, by, 560, 560, { edge: C.cyan });
  face(p.face, M + 24, by + 24, 512);
  const X = 780, hp = easeOut(seg(t, A(0.1), A(0.45)));
  txt(p.glance[0], X + (1 - hp) * 300, 250, 32, C.amber, { alpha: hp });
  txt(p.name, X + (1 - hp) * 500, 350, 40, C.chrome, { alpha: hp });
  const ra = seg(t, A(p.secondary_at), A(p.secondary_at + 0.15));
  p.secondary.forEach((s, i) => txt(s, X, 410 + i * 56, 40, C.cyan, { alpha: ra }));
  txt(p.glance[1], X, 600, 32, C.amber, { alpha: seg(t, A(p.key_at - 0.05), A(p.key_at + 0.05)) });
  const qa = seg(t, A(p.key_at), A(p.key_at + 0.15));
  p.key.forEach((s, i) => V(s, X, 700 + i * 90, 90, C.chrome, qa, { maxW: 1020 }));
  flash(t, A(0), 0, 0.3);
  dissolve(seg(t, p.t1 - 0.25, p.t1), C.ink, dflt(p.seed, 11));
};

// T21 payoff reprise + tree reveal: the agent calls the tool (glance), the tree of `nodes` [[depth, label]] comes back
// (leaves green), the `key` is stamped over it, the `secondary` aside follows
TPL.T21 = (t, p) => {
  const A = x => p.t0 + x;
  sky(C.navy, '#1a0f45'); stars(t, 25, 0.8); grid(t, 900, C.violet2, 0.5);
  agent(M + 40, 300, 10, t, 'ask');
  const X0 = M + 280, X1 = 760, n = p.nodes.length, step = n <= 6 ? 66 : 360 / n;
  if (t > A(p.call_at)) {
    tag(p.glance[0], X0 + 10, 330, C.cyan, seg(t, A(p.call_at), A(p.call_at + 0.1)));
    packet(t, A(p.call_at), A(p.call_at + 0.5), X0, X1 + 300, 360, C.cyan);
  }
  const ys = p.nodes.map((_, i) => 280 + i * step);
  p.nodes.forEach(([d, s], i) => {
    const t0 = A(p.nodes_at) + i * 0.12;
    if (t < t0) return;
    const x = X1 + 300 + d * 80, y = ys[i], leaf = i === n - 1 || p.nodes[i + 1][0] <= d;
    if (d > 0) {
      let j = i - 1; while (j > 0 && p.nodes[j][0] >= d) j--;
      rect(x - 56, ys[j] + 16, 6, y - 6 - (ys[j] + 16), C.dim); rect(x - 56, y - 6, 40, 6, C.dim);
    }
    rect(x, y - 38, measure(s, 28) + 30, 52, leaf ? C.navy2 : C.violet);
    tag(s, x + 15, y, leaf ? C.green : C.chrome);
  });
  const q = seg(t, A(p.key_at), A(p.key_at + 0.15));
  if (q > 0) rect(0, 630, W, 140, C.ink, 0.7 * q);
  stampTxt(p.key, W / 2, 745, 96, C.chrome, t, A(p.key_at), { align: 'center', from: 2.0 });
  V(p.secondary, W / 2, 860, 64, C.cyan, seg(t, A(p.secondary_at), A(p.secondary_at + 0.2)), { align: 'center' });
  flash(t, A(0), 0, 0.3);
  flash(t, A(p.key_at), 0, 0.3);
  dissolve(seg(t, p.t1 - 0.25, p.t1), C.ink, dflt(p.seed, 13));
};

// T22 result screen: heading (`title`), one pip per stage, the lesson (`key`), the closing line (`secondary`)
TPL.T22 = (t, p) => {
  const A = x => p.t0 + x;
  rect(0, 0, W, H, C.ink); stars(t, 18, 0.8);
  moon(W / 2, 1080 + 300, 1100, 0.3);
  const q = seg(t, A(0), A(0.15));
  if (q > 0) txt(p.title, W / 2, 230, 72, C.amber, { align: 'center', scale: lerp(1.8, 1, easeOut(q)), alpha: q * 3 });
  for (let i = 0; i < NSTAGES; i++) {
    const t0 = A(0.6) + i * 0.08; if (t < t0) continue;
    const x = W / 2 - NSTAGES * 46 / 2 + i * 46;
    rect(x, 289, 34, 34, C.shadow); rect(x, 285, 34, 34, C.green);
  }
  const ka = seg(t, A(p.key_at), A(p.key_at + 0.15)), sa = seg(t, A(p.secondary_at), A(p.secondary_at + 0.2));
  p.key.forEach((s, i) => txt(s, W / 2, 480 + i * 76, 56, C.chrome, { align: 'center', alpha: ka }));
  p.secondary.forEach((s, i) => V(s, W / 2, 700 + i * 75, 64, C.cyan, sa, { align: 'center' }));
  flash(t, A(0), 0, 0.3);
};

// T23 end card: the chrome logo, the motto (`key`), `glance` [address, credit], PRESS START, fade to black
TPL.T23 = (t, p) => {
  const A = x => p.t0 + x;
  rect(0, 0, W, H, C.ink); stars(t, 15, 0.8);
  moon(W / 2, 1080 + 200, 1100, 0.35);
  const pp = easeOut(seg(t, A(0), A(0.4)));
  titleLogo(W / 2, 330, lerp(1700, 1500, pp), 1);
  const ka = seg(t, A(p.key_at - 0.2), A(p.key_at));
  p.key.forEach((s, i) => V(s, W / 2, 610 + i * 90, 90, C.chrome, ka, { align: 'center' }));
  const ga = p.glance_at;
  txt(p.glance[0], W / 2, 830, 28, C.cyan, { align: 'center', alpha: seg(t, A(ga), A(ga + 0.2)) });
  txt(p.glance[1], W / 2, 890, 32, C.chrome, { font: 'V', align: 'center', alpha: seg(t, A(ga + 0.3), A(ga + 0.5)), shadow: 3 });
  if (t > A(ga + 1.0) && Math.floor(TA * 3) % 2 === 0) txt('PRESS START', W / 2, 960, 28, C.amber, { align: 'center' });
  flash(t, A(0), 0, 0.5);
  if (t > p.t1 - 0.5) rect(0, 0, W, H, '#000', seg(t, p.t1 - 0.5, p.t1));
};
