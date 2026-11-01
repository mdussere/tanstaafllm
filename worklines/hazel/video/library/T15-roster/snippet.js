// T15 Roster. Does not run alone.
// Parameters: CELL tiles [{n, j, j2, pic}], BUBBLES (one line each), RULES (runs), rule ticker start.
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.

// ---- from worklines/hazel/video/trailer/src/index.html, lines 510-578
// Scene 7 (40-48 s): the cell.
const CELL = [
  { n: 'PROFESSOR', j: 'Coordinates the cell,', j2: 'records the decisions', pic: 'prof' },
  { n: 'WYOH', j: 'The desktop, the buttons,', j2: 'the apps', pic: 'wyoh' },
  { n: 'MYCROFT', j: 'The voice:', j2: 'speech to text', pic: 'mic' },
  { n: 'MIKE', j: 'The local brain:', j2: 'small, accepted actions', pic: 'mike' },
  { n: 'MANNIE', j: 'Claude Code', j2: 'on the device', pic: 'mannie' },
  { n: 'LUNA', j: 'The device: cards,', j2: 'boot, Wi-Fi, audio', pic: 'luna' }
];
const RULES = [
  [['EACH AGENT OWNS ', C.chrome], ['ITS PART.', C.amber]],
  [['EVERYONE TALKS TO ', C.chrome], ['EVERYONE.', C.cyan]],
  [['PROFESSOR KEEPS ', C.chrome], ['THE DECISIONS.', C.amber]],
  [['ADAM, THE HUMAN, ', C.chrome], ['GIVES THE GO.', C.green]],
  [['EVERYTHING IS ', C.chrome], ['WRITTEN DOWN.', C.cyan]]
];
// What each agent says when it pops up: one speech bubble per tile.
const BUBBLES = ['Who takes Luna?', 'Desktop is up!', 'I heard that.', 'One action. OK?', 'On it.', '983 MiB left!'];
function bubble(x, y, s, p) {   // pixel speech bubble whose tail points down to (x, y)
  if (p <= 0) return;
  const w = measure(s, 30, 'V') + 36, h = 46, bx = x - w / 2, by = y - h - 18 - (1 - easeBack(p)) * 20;
  ctx.save(); ctx.globalAlpha = clamp(p * 3);
  rect(bx - 4, by - 4, w + 8, h + 8, C.ink); rect(bx, by, w, h, C.chrome);
  rect(x - 8, by + h, 16, 8, C.chrome); rect(x - 4, by + h + 8, 8, 8, C.chrome);
  ctx.restore();
  txt(s, x, by + 33, 30, C.ink, { font: 'V', align: 'center', shadow: 0, alpha: clamp(p * 3) });
}
function scene7(t) {
  sky(C.navy, '#120a33'); stars(t, 35, 0.6);
  txt('THE CELL', W / 2, 140, 64, C.chrome, { align: 'center', scale: 1 + 0.03 * beatPulse(t) });
  txt('Luna is built by a cell of AI coding agents: one Claude Code session per part.', W / 2, 205, 44, C.cyan, { font: 'V', align: 'center', alpha: seg(t, 40.2, 40.4), shadow: 3 });
  const tw = 500, th = 230, gx = 30, gy = 30, x0 = (W - (3 * tw + 2 * gx)) / 2, y0 = 260;
  CELL.forEach((c, i) => {
    const t0 = 40.0 + i * 0.5, p = easeBack(seg(t, t0, t0 + 0.25));
    if (p <= 0) return;
    const x = x0 + (i % 3) * (tw + gx), y = y0 + Math.floor(i / 3) * (th + gy);
    ctx.save(); ctx.translate(x + tw / 2, y + th / 2); ctx.scale(p, p); ctx.translate(-(x + tw / 2), -(y + th / 2));
    box(x, y, tw, th, { fill: '#0d1238', edge: i === 0 ? C.amber : C.dim, px: 5 });
    const ps = 170, px = x + 28, py = y + 30;
    rect(px, py, ps, ps, '#0a0d2a');
    ctx.save(); ctx.beginPath(); ctx.rect(px, py, ps, ps); ctx.clip();
    if (c.pic === 'mic') mic(px + 13, py + 13, 9, t);
    else if (c.pic === 'luna') device(px + 45, py + 3, 1.5, t, 'moon');
    else face(c.pic, px, py, ps);
    ctx.restore();
    txt(c.n, x + 225, y + 85, 30, i === 0 ? C.amber : C.chrome, { maxW: 250 });
    txt(c.j, x + 225, y + 140, 34, C.chrome, { font: 'V', maxW: 255, shadow: 2 });
    txt(c.j2, x + 225, y + 178, 34, C.chrome, { font: 'V', maxW: 255, shadow: 2 });
    ctx.restore();
  });
  // the cell chatters: one bubble per agent, after all the tiles are in
  CELL.forEach((c, i) => {
    const t0 = 41.0 + i * 0.3, x = x0 + (i % 3) * (tw + gx), y = y0 + Math.floor(i / 3) * (th + gy);
    const wob = Math.round(Math.sin(TA * 4 + i) * 2) * 2;
    bubble(x + tw - 130, y + 40 + wob, BUBBLES[i], seg(t, t0, t0 + 0.25) * (t < 43.0 ? 1 : 1 - seg(t, 43.0, 43.2)));
  });
  // rules ticker
  if (t >= 43.0) {
    const i = Math.min(4, Math.floor(t - 43.0)), t0 = 43.0 + i, p = seg(t, t0, t0 + 0.12);
    rect(0, 800, W, 190, C.ink, 0.85);
    txt('HOW THE CELL RUNS', M, 850, 24, C.dim);
    for (let k = 0; k < 5; k++) rect(W - M - (5 - k) * 34, 830, 24, 24, k <= i ? C.amber : '#262c5a');
    ctx.save(); ctx.translate(W / 2, 940); ctx.scale(lerp(1.4, 1, easeOut(p)), lerp(1.4, 1, easeOut(p)));
    runs(RULES[i], 0, 0, 44, { align: 'center', alpha: p * 2 });
    ctx.restore();
  }
  flash(t, 40.0, 0, 0.15, C.ink);
  dissolve(seg(t, 47.8, 48.0), C.ink, 17);
}
