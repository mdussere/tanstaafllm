// T10 Character select. Does not run alone.
// Parameters: CARDS [{name, role, lines[3], cost 0-4, pic}], SEL (cursor times), banner time and lines.
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.

// ---- from worklines/hazel/video/trailer/src/index.html, lines 399-452
// Scene 5 (24-34 s): select your intelligence, cheapest first.
const CARDS = [
  { name: 'BUTTONS', role: "Wyoh's gamepad daemon", lines: ['No model at all', '17.5 MiB, no CPU at rest', 'Live on Luna'], cost: 0, pic: 'pad' },
  { name: 'MYCROFT', role: 'The voice', lines: ['Speech to text, offline', 'You fix the text first', 'Kroko ≈ 160 MiB (luna-pi)'], cost: 1, pic: 'mic' },
  { name: 'MIKE', role: 'The local brain', lines: ['LFM2.5-350M, no network', 'One request, one action', 'You accept or refuse'], cost: 2, pic: 'mike' },
  { name: 'MANNIE', role: 'The frontier brain', lines: ['Claude Code, via the Tunnel', 'Builds, repairs, operates', 'Cost shown first'], cost: 4, pic: 'mannie' }
];
const SEL = [24.5, 26.0, 27.5, 29.0];
function scene5(t) {
  sky(C.navy, '#160c3c'); stars(t, 30, 0.7);
  txt('SELECT YOUR INTELLIGENCE', W / 2, 150, 56, C.chrome, { align: 'center', alpha: seg(t, 24.0, 24.1) });
  txt('CHEAPEST FIRST', W / 2, 215, 28, C.amber, { align: 'center', alpha: seg(t, 24.15, 24.25) });
  let sel = -1; SEL.forEach((s, i) => { if (t >= s) sel = i; });
  const banner = t >= 31.0;
  const cw = 380, gap = 40, x0 = (W - (4 * cw + 3 * gap)) / 2, y0 = 270, ch = 650;
  CARDS.forEach((c, i) => {
    const p = easeBack(seg(t, 24.0 + i * 0.1, 24.4 + i * 0.1));
    const x = x0 + i * (cw + gap), y = lerp(H + 50, y0, p);
    const on = i === sel && !banner;
    const dimmed = banner ? 0.35 : (sel >= 0 && !on ? 0.55 : 1);
    ctx.save(); ctx.globalAlpha = dimmed;
    box(x, y, cw, ch, { fill: on ? '#1b1460' : C.navy, edge: on ? C.amber : C.dim, inner: on ? C.amber2 : C.violet2, alpha: 0.95 });
    // portrait
    const px = x + 40, py = y + 40, ps = cw - 80;
    rect(px, py, ps, ps * 0.78, '#0a0d2a');
    ctx.save(); ctx.beginPath(); ctx.rect(px, py, ps, ps * 0.78); ctx.clip();
    if (c.pic === 'mike') face('mike', px, py - 20, ps, dimmed);
    else if (c.pic === 'mannie') face('mannie', px, py - 10, ps, dimmed);
    else if (c.pic === 'mic') { mic(px + ps / 2 - 96, py + 20, 12, t); }
    else if (c.pic === 'pad') { device(px + ps / 2 - 80, py + 8, 2, t, 'term'); }
    ctx.restore();
    txt(c.name, x + cw / 2, y + 340, 36, on ? C.amber : C.chrome, { align: 'center', maxW: cw - 40 });
    txt(c.role, x + cw / 2, y + 390, 38, C.cyan, { font: 'V', align: 'center', maxW: cw - 40, shadow: 2 });
    c.lines.forEach((l, j) => txt(l, x + cw / 2, y + 450 + j * 44, 36, C.chrome, { font: 'V', align: 'center', maxW: cw - 50, shadow: 2 }));
    // price pips
    txt('PRICE', x + 40, y + ch - 50, 20, C.dim);
    for (let k = 0; k < 4; k++) rect(x + 170 + k * 46, y + ch - 72, 34, 26, k < c.cost ? (c.cost >= 4 ? C.red : C.amber) : '#262c5a');
    ctx.restore();
    if (on) { // blinking cursor arrow above the card
      if (Math.floor(TA * 6) % 2 === 0) { const g = pgrid(x + cw / 2 - 24, y - 54, 6); g.r(0, 0, 8, 2, C.amber); g.r(1, 2, 6, 2, C.amber); g.r(2, 4, 4, 2, C.amber); g.r(3, 6, 2, 1, C.amber); }
    }
  });
  if (banner) {
    const p = easeOut(seg(t, 31.0, 31.2));
    rect(0, 440, W, 300 * p, '#05060f', 0.97); if (p >= 1) { rect(0, 440, W, 6, C.amber); rect(0, 734, W, 6, C.amber); }
    if (p >= 1) {
      runs([['THE ', C.chrome], ['LEAST SUFFICIENT', C.amber], [' INTELLIGENCE WINS.', C.chrome]], W / 2, 545, 48, { align: 'center', scale: 1 });
      txt('A rule beats a model. A small model beats a big one.', W / 2, 620, 48, C.cyan, { font: 'V', align: 'center', alpha: seg(t, 31.8, 32.0), shadow: 3 });
      txt('The frontier is called when it is worth its price.', W / 2, 680, 48, C.chrome, { font: 'V', align: 'center', alpha: seg(t, 32.6, 32.8), shadow: 3 });
    }
  }
  flash(t, 24.0, 0, 0.15, C.ink);
  dissolve(seg(t, 33.8, 34.0), C.ink, 21);
}
