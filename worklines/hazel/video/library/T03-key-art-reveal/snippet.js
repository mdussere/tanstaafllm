// T03 Key-art reveal (and the doctrine variant over the key art). Does not run alone.
// Parameters: artCover(srcY, zoom, block): srcY pans the art, block = pixel size (64 -> 1 resolves it),
// the manifesto lines and their fade-in times; doctrine: three lines L, one every 0.75 s.
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.

// ---- from worklines/hazel/video/trailer/src/index.html, lines 300-313
// Scene 2 (4-8 s): the key art resolves from big pixels, with the manifesto line.
function scene2(t) {
  const p = seg(t, 4, 8);
  const block = Math.max(1, Math.round(64 * Math.pow(1 - seg(t, 4.0, 4.7), 2)));
  artCover(lerp(20, 75, easeOut(p)), lerp(1.0, 1.04, p), block);
  const g = ctx.createLinearGradient(0, 640, 0, H); g.addColorStop(0, 'rgba(5,6,15,0)'); g.addColorStop(0.45, 'rgba(5,6,15,0.88)'); g.addColorStop(1, 'rgba(5,6,15,0.96)');
  ctx.fillStyle = g; ctx.fillRect(0, 640, W, H - 640);
  const a1 = seg(t, 4.9, 5.1), a2 = seg(t, 5.5, 5.7), a3 = seg(t, 6.3, 6.6);
  txt('A CONSPIRACY TO TURN A TINY, STUBBORN COMPUTER', W / 2, 860, 32, C.chrome, { align: 'center', alpha: a1 });
  runs([['INTO A MACHINE THAT ', C.chrome], ['RUNS ITSELF.', C.amber]], W / 2, 920, 32, { align: 'center', alpha: a2 });
  txt('...without pretending that any intelligence is free.', W / 2, 990, 44, C.cyan, { font: 'V', align: 'center', alpha: a3, shadow: 3 });
  flash(t, 4.0, 0, 0.35);
  dissolve(seg(t, 7.75, 8.0), C.ink, 11);
}

// ---- from worklines/hazel/video/trailer/src/index.html, lines 607-621
// Scene 9 (54-60 s): doctrine, then the end card.
function scene9(t) {
  if (t < 57) {
    artCover(lerp(330, 290, seg(t, 54, 57)), 1.08, 1);
    rect(0, 0, W, H, C.ink, 0.62);
    const L = [['NO FREE LLMS.', C.amber], ['NO INVISIBLE MASTERS.', C.chrome], ['NO SURRENDER TO THE DESKTOP.', C.cyan]];
    L.forEach(([s, c], i) => {
      const t0 = 54.0 + i * 0.75, p = seg(t, t0, t0 + 0.12);
      if (p <= 0) return;
      txt(s, W / 2, 420 + i * 150, 64, c, { align: 'center', alpha: p * 2, scale: lerp(1.5, 1, easeOut(p)) });
    });
    flash(t, 54.0, 0, 0.3);
    return;
  }
  rect(0, 0, W, H, C.ink); stars(t, 15, 0.8);
