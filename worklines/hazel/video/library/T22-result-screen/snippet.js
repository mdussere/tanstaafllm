// T22 Result screen. Does not run alone.
// Parameters: 'STORY n CLEAR', NSTAGES (pips), LESSON (PS2P 64, two lines), SECONDARY (VT323 64).
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.
// Also needs V.

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 698-714
// ---- RESULT (78 - 84): story clear, and the lesson
function sResult(t) {
  rect(0, 0, W, H, C.ink); stars(t, 18, 0.8);
  moon(W / 2, 1080 + 300, 1100, 0.3);
  const q = seg(t, 78.0, 78.15);
  if (q > 0) txt('STORY 2 CLEAR', W / 2, 230, 72, C.amber, { align: 'center', scale: lerp(1.8, 1, easeOut(q)), alpha: q * 3 });
  for (let i = 0; i < NSTAGES; i++) {
    const t0 = 78.6 + i * 0.08; if (t < t0) continue;
    const x = W / 2 - NSTAGES * 46 / 2 + i * 46;
    rect(x, 289, 34, 34, C.shadow); rect(x, 285, 34, 34, C.green);
  }
  txt("DON'T LOOK AT THE DESKTOP,", W / 2, 470, 64, C.chrome, { align: 'center', alpha: seg(t, 79.2, 79.35) });
  txt('ASK IT.', W / 2, 560, 64, C.chrome, { align: 'center', alpha: seg(t, 79.2, 79.35) });
  V('The compositor already knows', W / 2, 700, 64, C.cyan, seg(t, 80.4, 80.6), { align: 'center' });
  V('what a screenshot can only guess.', W / 2, 775, 64, C.cyan, seg(t, 80.4, 80.6), { align: 'center' });
  flash(t, 78.0, 0, 0.3);
}
