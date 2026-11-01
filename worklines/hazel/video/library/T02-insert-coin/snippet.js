// T02 Insert coin. Does not run alone.
// Parameters: L1 / L2a / L2b / L2c (the sentence split around the struck word), TYPE0 (typing start),
// TYPE_CPS (30 chars/s), strike time 2.55, stamp time 2.95, STAMP word ('LLM'), credit line.
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.

// ---- from worklines/hazel/video/trailer/src/index.html, lines 254-298
// Scene 1 (0-4 s): insert coin, then the free-lunch line gets corrected.
const L1 = "THERE AIN'T NO SUCH THING", L2a = "AS A FREE ", L2b = "LUNCH", L2c = ".";
const TYPE0 = 1.15, TYPE_CPS = 30;
function scene1(t) {
  rect(0, 0, W, H, C.ink);
  stars(t, 20, seg(t, 0, 1.2) * 0.9);
  if (t < 1.0) {
    if (Math.floor(TA * 4) % 2 === 0) txt('INSERT COIN', W / 2, 560, 64, C.amber, { align: 'center' });
    coin(W / 2, 380 - (1 - easeIn(seg(t, 0.2, 1.0))) * 40 + easeIn(seg(t, 0.6, 1.0)) * 140, 8, t);
    return;
  }
  txt('CREDIT 01', W - M, H - 90, 24, C.amber, { align: 'right', alpha: seg(t, 1.0, 1.05) });
  const n = Math.floor((t - TYPE0) * TYPE_CPS);
  const full = L1.length + L2a.length + L2b.length + L2c.length;
  const sz = 56;
  const s1 = L1.slice(0, clamp(n, 0, L1.length));
  txt(s1, W / 2 - measure(L1, sz) / 2, 440, sz, C.chrome);
  let k = n - L1.length;
  const line2 = L2a + L2b + L2c, x2 = W / 2 - measure(line2, sz) / 2;
  if (k > 0) {
    const shown = line2.slice(0, k);
    txt(shown, x2, 560, sz, C.chrome);
    if (k > L2a.length + L2b.length) {
      // strike LUNCH
      const lx = x2 + measure(L2a, sz), lw = measure(L2b, sz);
      const p = easeOut(seg(t, 2.55, 2.75));
      if (p > 0) rect(lx - 8, 560 - sz * 0.45, (lw + 16) * p, 10, C.red);
      // stamp LLM
      const q = seg(t, 2.95, 3.12);
      if (q > 0) {
        const sc = lerp(2.4, 1, easeOut(q));
        const shake = t < 3.35 ? Math.sin(t * 90) * 10 * (1 - seg(t, 3.0, 3.35)) : 0;
        txt('LLM', lx + lw / 2 + shake, 730, 120, C.cyan, { align: 'center', rot: -0.06, scale: sc, alpha: q * 3 });
      }
    }
  }
  if (n < full && Math.floor(TA * 8) % 2 === 0) {
    // blinking block cursor while typing
    const done = n <= L1.length;
    const cx = done ? W / 2 - measure(L1, sz) / 2 + measure(s1, sz) : x2 + measure(line2.slice(0, Math.max(0, k)), sz);
    rect(cx + 6, (done ? 440 : 560) - sz, sz * 0.8, sz, C.amber);
  }
  txt('after Robert A. Heinlein, The Moon Is a Harsh Mistress', W / 2, 880, 40, C.dim, { font: 'V', align: 'center', alpha: seg(t, 3.25, 3.5), shadow: 2 });
  flash(t, 4.0, 0.25, 0);
}
