// T06 Two boxes: fails / works. Does not run alone.
// Parameters: left box (red edge + cross at T_FAIL), right box (green edge + check at T_OK), their sprites
// and two label lines each. Story 1 stage 3 (the keyboard).
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.
// Also needs stageBg, hud, clearStamp, cross, hub, adapter (Story 1 sprites).

// ---- from worklines/hazel/video/story1-hello-luna/src/index.html, lines 515-535
// ---- STAGE 3 (28 - 34): the keyboard
function s3(t) {
  stageBg(t, 3); hud(t, 3, 28, STAGES[2][2]);
  const a1 = seg(t, 28.5, 28.7);
  if (a1 > 0) {
    box(M, 280, 800, 480, { alpha: 0.9 * a1, edge: t > 29.2 ? C.red : C.chrome });
    hub(M + 90, 400, 10);
    txt('MULTI-PORT USB-C HUB', M + 400, 600, 28, C.chrome, { align: 'center', alpha: a1 });
    if (t > 29.2) { cross(M + 640, 330, 70, C.red); txt('NOT EVEN CAPS LOCK.', M + 400, 690, 28, C.red, { align: 'center', alpha: seg(t, 29.2, 29.3) }); }
  }
  const a2 = seg(t, 30.6, 30.8);
  if (a2 > 0) {
    const x = 1000;
    box(x, 280, 800, 480, { alpha: 0.9 * a2, edge: t > 31.3 ? C.green : C.chrome });
    adapter(x + 240, 410, 10);
    txt('PLAIN USB-C TO USB-A', x + 400, 600, 28, C.chrome, { align: 'center', alpha: a2 });
    if (t > 31.3) { check(x + 640, 330, 70, C.green); txt('WORKS STRAIGHT AWAY.', x + 400, 690, 28, C.green, { align: 'center', alpha: seg(t, 31.3, 31.4) }); }
  }
  clearStamp(t, 32.4);
  flash(t, 28.0, 0, 0.3);
}
