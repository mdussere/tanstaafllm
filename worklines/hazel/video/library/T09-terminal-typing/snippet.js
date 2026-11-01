// T09 Terminal typing. Does not run alone.
// Parameters: TEXT, start time, chars per second (10-32), box colour (red edge on an error),
// optional rolling counter (target value, roll time). Story 1 stage 6, then the trailer's "pong" counter.
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.
// Also needs termBox, V (Story 1 staging).

// ---- from worklines/hazel/video/story1-hello-luna/src/index.html, lines 364-369
function termBox(x, y, w, h, title, edge = C.chrome) {
  box(x, y, w, h, { fill: '#05060f', edge, alpha: 0.95 });
  if (title) txt(title, x + 36, y + 62, 22, C.dim);
}
function typed(s, t, t0, cps) { return s.slice(0, clamp(Math.floor((t - t0) * cps), 0, s.length)); }
function cursor(t, x, y, h, c = C.green) { if (Math.floor(TA * 4) % 2 === 0) rect(x + 4, y - h * 0.8, h * 0.5, h * 0.9, c); }

// ---- from worklines/hazel/video/story1-hello-luna/src/index.html, lines 617-623
const CSA = 'AP is in CSA process, reject auth';
function s6(t) {
  stageBg(t, 6); hud(t, 6, 60, STAGES[5][2]);
  termBox(M, 250, W - 2 * M, 150, null, t > 61.4 && t < 64.4 ? C.red : C.chrome);
  const s = typed(CSA, t, 60.4, 32);
  V(s, M + 50, 345, 60, C.red, seg(t, 60.4, 60.5), { shadow: 0 });
  if (s.length < CSA.length && t > 60.4) cursor(t, M + 50 + measure(s, 60, 'V'), 345, 60, C.red);

// ---- from worklines/hazel/video/trailer/src/index.html, lines 375-390
  // "pong"
  rect(0, 0, W, H, C.ink); stars(t, 15, 0.5);
  txt('ONE WORD TO CLAUDE CODE:', W / 2, 200, 36, C.dim, { align: 'center' });
  box(460, 250, 1000, 200, { fill: '#05081a', edge: C.dim, inner: '#1d2350' });
  const word = '> pong';
  const n = Math.floor((t - 20.2) * 16);
  txt(word.slice(0, clamp(n, 0, word.length)), 520, 385, 96, C.green, { font: 'V', shadow: 0 });
  if (n < word.length + 6 && Math.floor(TA * 6) % 2 === 0) rect(520 + measure(word.slice(0, clamp(n, 0, 6)), 96, 'V') + 8, 318, 36, 70, C.green);
  const cp = easeOut(seg(t, 20.75, 21.9));
  if (t >= 20.75) {
    const v = Math.round(17700 * cp / 10) * 10;
    const s = (cp >= 1 ? '≈' : '') + v.toLocaleString('en-US');
    txt(s, W / 2, 680, 128, C.amber, { align: 'center', scale: 1 + 0.08 * (cp >= 1 ? 1 - seg(t, 21.9, 22.2) : 0) });
    txt('INPUT TOKENS', W / 2, 760, 36, C.chrome, { align: 'center' });
    txt("almost all of it Claude Code's own prompt and tools  (measured on luna-pi)", W / 2, 830, 40, C.dim, { font: 'V', align: 'center', alpha: seg(t, 22.0, 22.2), shadow: 2 });
  }
