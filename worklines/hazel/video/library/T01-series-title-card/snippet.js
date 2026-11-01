// T01 Series title card. Does not run alone.
// Parameters: SERIES_LINE ('TANSTAAFLLM · STORY n'), TITLE (stamp, PS2P 100-112),
// SUBTITLE (VT323 90, two lines), stamp time 1.0 s, scene length 5-6 s (cut on a bar).
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.
// Also needs stampTxt (Story 2) and V (VT323 shortcut).

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 365-371
// A stamp: scale-in with shake.
function stampTxt(s, x, y, size, color, t, t0, o = {}) {
  const q = seg(t, t0, t0 + 0.15);
  if (q <= 0) return;
  const sh = t < t0 + 0.35 ? Math.sin(t * 90) * 8 * (1 - seg(t, t0, t0 + 0.35)) : 0;
  txt(s, x + sh, y, size, color, Object.assign({ scale: lerp(o.from || 2, 1, easeOut(q)), alpha: q * 3 }, o));
}

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 395-395
const V = (s, x, y, size, color, a, o = {}) => txt(s, x, y, size, color, Object.assign({ font: 'V', alpha: a, shadow: 3 }, o));

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 403-414
// ---- TITLE (0 - 6): the episode card
function sTitle(t) {
  rect(0, 0, W, H, C.ink); stars(t, 20, seg(t, 0, 1) * 0.9);
  moon(W / 2, 1080 + 260, 1100, 0.35 * seg(t, 0, 1.5));
  txt('TANSTAAFLLM · STORY 2', W / 2, 330, 36, C.amber, { align: 'center', alpha: seg(t, 0.3, 0.5) });
  stampTxt('ASK THE DESKTOP', W / 2, 520, 100, C.chrome, t, 1.0, { align: 'center', from: 2.0 });
  V('How an agent learned to work', W / 2, 635, 90, C.cyan, seg(t, 1.4, 1.6), { align: 'center' });   // large enough to read on a phone (user, 2026-11-01)
  V('a desktop without looking at it.', W / 2, 725, 90, C.cyan, seg(t, 1.4, 1.6), { align: 'center' });
  if (t > 2.4 && Math.floor(TA * 2.5) % 2 === 0) txt('PRESS START', W / 2, 885, 40, C.amber, { align: 'center' });
  flash(t, 1.0, 0, 0.25);
  flash(t, 6.0, 0.2, 0);
}
