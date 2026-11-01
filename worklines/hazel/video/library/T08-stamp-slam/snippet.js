// T08 Stamp slam. Does not run alone.
// Parameters: WORDS (1-3 lines), hit times (on beats), size (PS2P 56-112), colour, from-scale (1.4-2.4), rot.
// stampTxt (Story 2) is the reusable form; the trailer's price list shows three slams, one per beat.
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 365-371
// A stamp: scale-in with shake.
function stampTxt(s, x, y, size, color, t, t0, o = {}) {
  const q = seg(t, t0, t0 + 0.15);
  if (q <= 0) return;
  const sh = t < t0 + 0.35 ? Math.sin(t * 90) * 8 * (1 - seg(t, t0, t0 + 0.35)) : 0;
  txt(s, x + sh, y, size, color, Object.assign({ scale: lerp(o.from || 2, 1, easeOut(q)), alpha: q * 3 }, o));
}

// ---- from worklines/hazel/video/trailer/src/index.html, lines 354-374
function scene4(t) {
  if (t < 20) {
    sky('#12062e', '#2d0b3e'); stars(t, 60, 0.6); grid(t, 780, '#6a2a9c', 0.6);
    const lines = [
      [['EVERY TOKEN COSTS ', C.chrome], ['TIME AND MONEY.', C.amber]],
      [['EVERY MODEL COSTS ', C.chrome], ['MEMORY.', C.amber]],
      [['EVERY DAEMON COSTS ', C.chrome], ['BATTERY.', C.amber]]
    ];
    lines.forEach((ln, i) => {
      const t0 = 16.0 + i, p = seg(t, t0, t0 + 0.15);
      if (p <= 0) return;
      const sc = lerp(1.6, 1, easeOut(p));
      ctx.save(); ctx.translate(W / 2, 330 + i * 130); ctx.scale(sc, sc);
      runs(ln, 0, 0, 48, { align: 'center', alpha: p * 2 });
      ctx.restore();
    });
    txt('ON LUNA, NOTHING HIDES THOSE PRICES.', W / 2, 760, 32, C.cyan, { align: 'center', alpha: seg(t, 19.0, 19.15) });
    flash(t, 16.0, 0, 0.3);
    flash(t, 20.0, 0.12, 0, C.ink);
    return;
  }
