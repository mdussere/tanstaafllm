// T17 Opening / to be continued. Does not run alone.
// Parameters: the two promise lines, the follow line, ROW (the faces hopping onto the Moon), PRESS START line.
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.

// ---- from worklines/hazel/video/trailer/src/index.html, lines 580-605
// Scene 8 (48-54 s): the opening. The cell is ready; the adventure begins.
const ROW = ['prof', 'wyoh', 'mic', 'mike', 'mannie', 'luna'];
function scene8(t) {
  rect(0, 0, W, H, C.ink); stars(t, 60, 0.8);
  moon(W / 2, lerp(H + 700, H + 260, easeOut(seg(t, 48.0, 49.5))), 1300, 0.55);
  txt('THE CELL IS READY.', W / 2, 250, 40, C.chrome, { align: 'center', alpha: seg(t, 48.2, 48.35) });
  const sp = seg(t, 49.0, 49.15);
  if (sp > 0) txt('THE ADVENTURE BEGINS.', W / 2, 400, 72, C.amber, { align: 'center', rot: -0.02, scale: lerp(2.2, 1, easeOut(sp)), alpha: sp * 2 });
  txt('Follow our missions, one story at a time.', W / 2, 500, 56, C.cyan, { font: 'V', align: 'center', alpha: seg(t, 50.2, 50.4), shadow: 3 });
  // the six members hop onto the Moon, one after the other
  const s = 150, gap = 40, x0 = (W - (6 * s + 5 * gap)) / 2, gy = 820;
  ROW.forEach((k, i) => {
    const t0 = 48.4 + i * 0.15, p = easeBack(seg(t, t0, t0 + 0.35));
    if (p <= 0) return;
    const hop = Math.abs(Math.sin((TA * 2.2 + i * 0.37) * Math.PI)) * 26;
    const x = x0 + i * (s + gap), y = gy - s - hop + (1 - p) * 300;
    rect(x - 6, y - 6, s + 12, s + 12, i === 0 ? C.amber : C.dim); rect(x, y, s, s, '#0a0d2a');
    ctx.save(); ctx.beginPath(); ctx.rect(x, y, s, s); ctx.clip();
    if (k === 'mic') mic(x + 12, y + 12, 8, t);
    else if (k === 'luna') device(x + 40, y + 4, 1.3, t, 'moon');
    else face(k, x, y, s);
    ctx.restore();
  });
  if (t > 51.0 && Math.floor(TA * 2.5) % 2 === 0) txt('PRESS START TO FOLLOW', W / 2, 990, 28, C.amber, { align: 'center' });
  flash(t, 48.0, 0, 0.2, '#ffffff');
}
