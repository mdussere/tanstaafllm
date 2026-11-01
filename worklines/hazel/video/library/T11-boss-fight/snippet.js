// T11 Boss fight: red title, HP bar, phase change on a flash, victory. Does not run alone.
// Parameters: BOSS stage number, hit times, phase-b time (flash), the hero sprite state per phase.
// First part: Story 2 (two phases, phone sizes). Second part: Story 1's boss icon and HP pips.
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.
// Also needs stageBg, hud, clearStamp, stampTxt, tag, V, termBox, luna, chip (Story 1).

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 561-588
// ---- STAGE 5, the boss (44 - 52): the black panel on Luna; phase b from the flash at 48.5
function s5(t) {
  stageBg(t, BOSS); hud(t, BOSS, 44, STAGES[4][2]);
  const fixed = t >= 48.5;
  const hits = (t >= 46.5 ? 1 : 0) + (fixed ? 1 : 0);
  for (let i = 0; i < 2; i++) { const on = i >= hits; rect(W - M - 2 * 60 + i * 60, 88, 50, 26, C.shadow); rect(W - M - 2 * 60 + i * 60, 84, 50, 26, on ? C.red : C.navy2); }
  tag(fixed ? 'LIT' : 'BLACK', W - M - 140, 110, fixed ? C.green : C.red, 1, { align: 'right' });
  const scr = t < 48.5 ? 'black' : (t < 48.6 ? 'flash' : 'desk');
  luna(170, 250 + Math.round(Math.sin(t * Math.PI) * 2) * 4, 5.5, t, scr, { focus: Math.floor(t * 2) % 3 });
  const X = 760;
  tag("LUNA'S REAL 720 × 720 PANEL", X, 300, C.cyan, seg(t, 44.3, 44.4));
  if (!fixed) {
    stampTxt('BLACK.', X, 440, 64, C.red, t, 45.0, { rot: -0.04 });
    V("Sway's own screenshots", X, 560, 64, C.chrome, seg(t, 45.6, 45.8), { maxW: 1040 });
    V('looked right.', X, 625, 64, C.chrome, seg(t, 45.6, 45.8), { maxW: 1040 });
    if (t > 46.5) runs([['MALI GPU DRIVER: ', C.dim], ['NOT LOADED', C.red]], X, 740, 32, { alpha: seg(t, 46.5, 46.6) });
  } else {
    txt('GPU DRIVER', X, 440, 56, C.chrome);
    txt('LOADED.', X, 520, 56, C.green);
    if (t > 48.8) {
      termBox(X, 600, 460, 130, C.green);
      V('1 passed', X + 40, 690, 64, C.green, 1, { shadow: 0 });
    }
  }
  clearStamp(t, 50.5);
  flash(t, 48.5, 0, 0.25);
  flash(t, 44.0, 0, 0.4, C.red);
}

// ---- from worklines/hazel/video/story1-hello-luna/src/index.html, lines 569-575
  // the boss and its hit points, top right
  const hits = PATCHES.filter(p => t >= p[0]).length;
  const vis = 0.12 + 0.88 * hits / 3 + (hits < 3 ? 0.08 * Math.sin(TA * 9) : 0);
  const shake = PATCHES.reduce((s, p) => s + (t > p[0] && t < p[0] + 0.3 ? Math.sin(t * 80) * 10 * (1 - seg(t, p[0], p[0] + 0.3)) : 0), 0);
  chip(W - M - 150 + shake, 60, 6, vis);
  txt(hits < 3 ? 'HIDDEN' : 'FOUND', W - M - 190, 70, 18, hits < 3 ? C.dim : C.green, { align: 'right' });
  for (let i = 0; i < 3; i++) { const on = i >= hits; rect(W - M - 190 - (3 - i) * 50, 88, 42, 22, C.shadow); rect(W - M - 190 - (3 - i) * 50, 84, 42, 22, on ? C.red : C.navy2); }
