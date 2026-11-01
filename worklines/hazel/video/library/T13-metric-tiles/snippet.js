// T13 Metric tiles / gauge. Does not run alone.
// Parameters: TILES [time, label, value] (one per beat), each tagged with its machine;
// or a segmented bar: total, segments [value, colour, time], the limit marker.
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.
// Also needs tag (Story 2).

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 503-503
const TILES = [[31.0, 'SOCKET READY', '42 ms'], [31.5, 'FOCUS EVENT', '0.6 ms'], [32.0, 'SWAY MEMORY', '~20 MiB'], [32.5, 'KILLED, BACK IN', '7.5 ms']];

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 522-529
  TILES.forEach(([t0, k, v], i) => {               // the secondary message: four figures, each on luna-pi
    if (t < t0) return;
    const x = X + (i % 2) * 510, y = 485 + Math.floor(i / 2) * 200, a = seg(t, t0, t0 + 0.1);
    box(x, y, 490, 185, { edge: C.cyan, alpha: 0.92 * a });
    tag(k, x + 30, y + 58, C.dim, a, { maxW: 430 });
    txt(v, x + 30, y + 120, 40, C.chrome, { alpha: a, scale: lerp(1.5, 1, easeOut(seg(t, t0, t0 + 0.15))) });
    tag('luna-pi', x + 460, y + 160, C.cyan, a, { align: 'right' });
  });

// ---- from worklines/hazel/video/trailer/src/index.html, lines 469-500
  txt('PRESSURE: WHERE 983 MiB GO', W / 2, 180, 40, C.chrome, { align: 'center' });
  const bx = 160, bw = 1600, by = 470, bh = 110, px = bw / 983;
  // bar frame
  rect(bx - 12, by - 12, bw + 24, bh + 24, C.chrome); rect(bx - 6, by - 6, bw + 12, bh + 12, C.ink);
  const used = 983 - 547;
  const pU = easeOut(seg(t, 36.0, 36.4)), pC = easeOut(seg(t, 37.0, 37.3)), pM = easeOut(seg(t, 38.0, 38.3));
  // free blocks (segmented)
  for (let x = 0; x < bw; x += 20) rect(bx + x, by, 16, bh, '#123a4a');
  const seg1 = used * px * pU, seg2 = 244 * px * pC, seg3 = 306 * px * pM;
  const over = t >= 38.3;
  const blink = over && Math.floor(TA * 8) % 2 === 0;
  function blocks(x0, w, col) { for (let x = 0; x < w; x += 20) rect(bx + x0 + x, by, Math.min(16, w - x), bh, col); }
  blocks(0, seg1, C.violet2);
  blocks(used * px, seg2, C.amber);
  blocks((used + 244) * px, Math.min(seg3, bw - (used + 244) * px), blink ? C.red : C.cyan);
  if (over) { const ox = bx + bw; rect(ox + 6, by - 6, 16, bh + 12, C.red); }
  // labels
  if (t < 36.0) txt('983 MiB OF RAM, ALL OF IT', W / 2, 700, 32, C.cyan, { align: 'center' });
  if (pU > 0) {
    txt('SYSTEM + DESKTOP + RESIDENT DICTATION', bx, 650, 24, C.dim, { alpha: pU, maxW: 700 });
    txt('547 MiB LEFT', bx + used * px + 10, 650, 32, C.green, { alpha: seg(t, 36.4, 36.5) * (t < 37.0 ? 1 : 0.8) });
    txt('Luna, Arch Linux ARM', bx + used * px + 10, 700, 36, C.dim, { font: 'V', alpha: seg(t, 36.4, 36.5), shadow: 2 });
  }
  if (pC > 0) {
    txt('CLAUDE CODE PEAK: 244 MiB', bx + used * px, 430, 24, C.amber, { alpha: pC });
    txt('luna-pi', bx + used * px + 615, 430, 36, C.dim, { font: 'V', alpha: pC, shadow: 2 });
    if (t > 37.3 && t < 38.0) { check(bx + used * px + 760, 380, 48, C.green); txt('FITS', bx + used * px + 830, 425, 32, C.green); }
  }
  if (pM > 0) {
    txt('+ MIKE ≈ 306 MiB', bx + bw, 760, 32, C.cyan, { align: 'right', alpha: pM });
    txt('lean, desk host', bx + bw, 805, 36, C.dim, { font: 'V', align: 'right', alpha: pM, shadow: 2 });
  }
