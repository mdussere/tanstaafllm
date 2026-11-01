// T18 Pixel-grid guess. Does not run alone.
// Parameters: the region to pixelate, block size (35 px), GUESS [time, text] (one coin each), key line.
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.
// Also needs stageBg, hud, clearStamp, tag, V, agent, miniDesk.

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 304-311
// Blur a screen region into big blocks (what a model gets from a small, cheap screenshot).
const PIX = document.createElement('canvas');
function pixelate(x, y, w, h, block) {
  PIX.width = Math.ceil(w / block); PIX.height = Math.ceil(h / block);
  const g = PIX.getContext('2d'); g.imageSmoothingEnabled = true;
  g.drawImage(cv, x, y, w, h, 0, 0, PIX.width, PIX.height);
  ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(PIX, 0, 0, PIX.width, PIX.height, x, y, w, h); ctx.restore();
}

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 436-460
// ---- STAGE 1 (14 - 20): the screenshot trap
const GUESS = [[15.0, 'A BUTTON?'], [15.5, 'A WINDOW?'], [16.0, 'WHICH ONE?']];
function s1(t) {
  stageBg(t, 1); hud(t, 1, 14, STAGES[0][2]);
  if (t > 14.4) {                                   // the desktop, as a blurry screenshot
    box(M, 230, 760, 400);
    miniDesk(M + 30, 260, 700, 340, { focus: 1, bright: true });
    pixelate(M + 30, 260, 700, 340, 35);
    for (let y = 260; y < 600; y += 35) rect(M + 30, y, 700, 2, C.ink, 0.35);
    for (let x = M + 30; x < M + 730; x += 35) rect(x, 260, 2, 340, C.ink, 0.35);
  }
  if (t > 14.6) agent(960, 300 + Math.round(Math.sin(t * 6)) * 4, 10, t, 'squint');
  GUESS.forEach(([t0, s], i) => {                  // each guess costs a coin (glance text)
    if (t < t0) return;
    const y = 290 + i * 100, a = seg(t, t0, t0 + 0.1);
    rect(1250, y - 46, measure(s, 28) + 40, 62, C.navy2, a); rect(1250, y - 46, 6, 62, C.amber, a);
    tag(s, 1270, y, C.amber, a);
    if (t < t0 + 0.6) coin(1230, y - 15 - 140 * seg(t, t0, t0 + 0.6), 3, t);
  });
  V('An agent guesses from pixels', M, 740, 90, C.chrome, seg(t, 14.9, 15.1));
  V('and pays for every image.', M, 830, 90, C.chrome, seg(t, 14.9, 15.1));
  txt('ON PAPER: A DESKTOP DOM.', M, 945, 40, C.cyan, { alpha: seg(t, 17.0, 17.15) });
  clearStamp(t, 18.5);
  flash(t, 14.0, 0, 0.3);
}
