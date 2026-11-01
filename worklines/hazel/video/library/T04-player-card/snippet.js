// T04 Player card. Does not run alone.
// Parameters: PLAYER n, NAME (PS2P 80-88), portrait (face() in a box, or device()/luna() sprite),
// TAGLINE (PS2P 40), QUEST line (VT323 90 for the phone), optional STATS rows [label, value].
// First part: Story 2 (phone sizes). Second part: the trailer's stat rows and mission box.
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 416-434
// ---- PLAYER (6 - 14): Wyoh, the desktop layer of Luna
function sPlayer(t) {
  sky(C.navy, '#1a0f45'); stars(t, 25, 0.8);
  const bob = Math.round(Math.sin(t * Math.PI) * 2) * 4;
  const by = lerp(1200, 230, easeBack(seg(t, 6.0, 6.5))) + bob;
  box(M, by, 560, 560, { edge: C.cyan });
  face('wyoh', M + 24, by + 24, 512);
  const X = 780, hp = easeOut(seg(t, 6.1, 6.45));
  txt('PLAYER 2', X + (1 - hp) * 300, 250, 32, C.amber, { alpha: hp });
  txt('WYOH', X + (1 - hp) * 500, 350, 80, C.chrome, { alpha: hp });
  txt('THE DESKTOP LAYER', X, 440, 40, C.cyan, { alpha: seg(t, 6.8, 6.95) });
  txt('OF LUNA', X, 500, 40, C.cyan, { alpha: seg(t, 6.8, 6.95) });
  txt('QUEST:', X, 610, 32, C.amber, { alpha: seg(t, 8.2, 8.3) });
  const qa = seg(t, 8.25, 8.4);
  V('Observe and operate', X, 705, 90, C.chrome, qa, { maxW: 1020 });
  V('the desktop without pixels.', X, 790, 90, C.chrome, qa, { maxW: 1020 });
  flash(t, 6.0, 0, 0.3);
  dissolve(seg(t, 13.75, 14.0), C.ink, 11);
}

// ---- from worklines/hazel/video/trailer/src/index.html, lines 316-319
const STATS = [
  ['CPU', '4 × CORTEX-A35'], ['RAM', '983 MiB'], ['SCREEN', '720 × 720'],
  ['INPUT', '17 BUTTONS, 2 STICKS'], ['NETWORK', '2.4 GHz WI-FI'], ['PRICE', '≈ 30 €']
];

// ---- from worklines/hazel/video/trailer/src/index.html, lines 329-348
  STATS.forEach(([k, v], i) => {
    const t0 = 8.5 + i * 0.5, a = seg(t, t0, t0 + 0.12);
    if (a <= 0) return;
    const y = 360 + i * 72;
    rect(820, y - 44, 980, 60, i % 2 ? C.navy2 : C.violet, 0.55 * a);
    txt(k, 840, y, 24, C.dim, { alpha: a });
    const hl = (k === 'RAM' || k === 'PRICE');
    txt(v, 1080, y, 32, hl ? C.amber : C.chrome, { alpha: a, maxW: 700, scale: 1 + 0.25 * (1 - seg(t, t0, t0 + 0.2)) });
  });
  // mission dialogue
  if (t >= 12.0) {
    const op = easeOut(seg(t, 12.0, 12.2));
    box(820, 800, 980, lerp(10, 210, op), {});
    if (op >= 1) {
      const m1 = 'MISSION: MAKE IT AUTONOMOUS.';
      txt(m1.slice(0, Math.floor((t - 12.2) * 40)), 860, 868, 32, C.amber);
      txt('It listens, acts on its own desktop, maintains itself.', 860, 930, 44, C.chrome, { font: 'V', alpha: seg(t, 13.0, 13.2), maxW: 900, shadow: 3 });
      txt('A lot to ask of a 30-euro console. That is the point.', 860, 978, 44, C.cyan, { font: 'V', alpha: seg(t, 14.0, 14.2), maxW: 900, shadow: 3 });
    }
  }
