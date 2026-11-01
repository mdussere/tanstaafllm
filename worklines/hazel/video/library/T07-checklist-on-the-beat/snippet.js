// T07 Checklist on the beat. Does not run alone.
// Parameters: a list of lines, a first time and a step (0.3-0.5 s = one beat or less); check() then the line.
// Story 1 stage 1 (the copy, safe on disk). For the boxed variant see T06; for numbered rows see T19.
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.
// Also needs drive (Story 1 sprite) and V.

// ---- from worklines/hazel/video/story1-hello-luna/src/index.html, lines 432-455
  const a2 = seg(t, 15.0, 15.2);
  if (a2 > 0) {                          // the copy, safe on disk
    const x = 1000;
    box(x, 260, 800, 470, { alpha: 0.9 * a2, edge: t > 16.2 ? C.green : C.chrome });
    drive(x + 50, 330, 9, t > 16.2);
    txt('SAFE ON DISK', x + 260, 360, 32, C.amber, { alpha: a2 });
    txt('42 GB, COMPRESSED', x + 260, 420, 24, C.chrome, { alpha: seg(t, 15.2, 15.3) });
    ['CARD READ-ONLY', 'VERIFY: IDENTICAL'].forEach((s, i) => {
      const t0 = 15.6 + i * 0.3, a = seg(t, t0, t0 + 0.1);
      if (a <= 0) return;
      check(x + 260, 450 + i * 64, 34, C.green);
      txt(s, x + 320, 480 + i * 64, 24, i === 1 ? C.green : C.chrome, { alpha: a });
    });
    V('byte for byte', x + 320, 600, 40, C.green, seg(t, 16.2, 16.4));
    ['EMUELEC', 'STORAGE', 'EEROMS'].forEach((s, i) => {   // what is inside, to explore
      const t0 = 16.5 + i * 0.15, a = seg(t, t0, t0 + 0.1);
      if (a <= 0) return;
      const w = measure(s, 20) + 28, xx = x + 50 + [0, 200, 400][i];
      rect(xx, 650, w, 44, C.navy2, a); txt(s, xx + 14, 683, 20, C.cyan, { alpha: a });
    });
  }
  V('The original card goes into a drawer, untouched.', W / 2, 790, 48, C.cyan, seg(t, 16.9, 17.1), { align: 'center' });
  txt('FIRST, SECURE THE ORIGINAL. THEN EXPLORE IT.', W / 2, 860, 32, C.amber, { align: 'center', alpha: seg(t, 17.3, 17.45) });
  clearStamp(t, 18.5);
