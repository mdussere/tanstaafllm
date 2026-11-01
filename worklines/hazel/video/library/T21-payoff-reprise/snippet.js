// T21 Payoff reprise: the title stamp on a dark band. Does not run alone.
// Parameters: band y and height, STAMP text (the episode title + '.'), stamp time (on the theme's hit), one secondary.
// First Story 2 (payoff), then Story 1 (stage 7).
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.
// Also needs stampTxt and V.

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 689-695
  const q = seg(t, 73.5, 73.65);
  if (q > 0) rect(0, 630, W, 140, C.ink, 0.7 * q);
  stampTxt('ASK THE DESKTOP.', W / 2, 745, 96, C.chrome, t, 73.5, { align: 'center', from: 2.0 });
  V('Screenshots stay, as evidence for humans.', W / 2, 860, 64, C.cyan, seg(t, 74.6, 74.8), { align: 'center' });
  flash(t, 72.0, 0, 0.3);
  flash(t, 73.5, 0, 0.3);
  dissolve(seg(t, 77.75, 78.0), C.ink, 13);

// ---- from worklines/hazel/video/story1-hello-luna/src/index.html, lines 658-664
  const q = seg(t, 72.5, 72.65);
  if (q > 0) {
    rect(0, 870, W, 210, C.ink, 0.85 * q);
    const sh = t < 72.9 ? Math.sin(t * 90) * 10 * (1 - seg(t, 72.5, 72.9)) : 0;
    txt('HELLO, LUNA.', W / 2 + sh, 1030, 104, C.chrome, { align: 'center', scale: lerp(2.0, 1, easeOut(q)), alpha: q * 3 });
  }
  flash(t, 68.0, 0, 0.3);
