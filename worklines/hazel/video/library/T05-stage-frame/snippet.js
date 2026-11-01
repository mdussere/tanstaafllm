// T05 Stage frame: background, HUD (STAGE n + title + pips), CLEAR! stamp. Does not run alone.
// Parameters: STAGES [start, n, title], NSTAGES, BOSS (index of the boss stage: red title, no pips).
// A stage is:
//   function sN(t) { stageBg(t, N); hud(t, N, T0, TITLE); /* content */ clearStamp(t, T0 + len - 1.5); flash(t, T0, 0, 0.3); }
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 254-261
// Times are seconds of the cut, from 0 (no holds needed: timing.py audits them).
const BASE = 90;
const STAGES = [   // [start, number, title]
  [14, 1, 'THE SCREENSHOT TRAP'], [20, 2, 'ONE SCENE IS NOT A DESKTOP'], [28, 3, 'ASK THE ONE THAT EXISTS'],
  [36, 4, 'HAND IT TO AGENTS'], [44, 5, 'BOSS: THE BLACK PANEL'], [52, 6, '17 BUTTONS, NO KEYBOARD'],
  [62, 7, 'SEVEN LAYERS']
];
const NSTAGES = 7, BOSS = 5;

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 374-392
function stageBg(t, n) { sky(C.navy, n === BOSS ? '#2a0f3a' : '#1a0f45'); stars(t, 25, 0.8); }
function hud(t, n, t0, title) {
  const p = easeOut(seg(t, t0, t0 + 0.3));
  txt('STAGE ' + n, M + (1 - p) * -300, 110, 28, C.amber, { alpha: p });
  txt(title, M + (1 - p) * -500, 175, 44, n === BOSS ? C.red : C.chrome, { alpha: p, maxW: 1260 });
  if (n === BOSS) return;
  for (let i = 1; i <= NSTAGES; i++) {   // the stage pips, top right
    const x = W - M - (NSTAGES + 1 - i) * 46, cur = i === n;
    const c = i < n ? C.green : (cur ? (Math.floor(TA * 4) % 2 ? C.amber : '#a35d00') : C.navy2);
    rect(x, 84, 34, 34, C.shadow); rect(x, 80, 34, 34, c);
    if (i === BOSS) rect(x + 10, 90, 14, 14, i < n ? '#1d4a2c' : C.red);
  }
}
function clearStamp(t, tc, x = W - M - 220, y = 980) {
  const q = seg(t, tc, tc + 0.15);
  if (q <= 0) return;
  const shake = t < tc + 0.35 ? Math.sin(t * 90) * 8 * (1 - seg(t, tc, tc + 0.35)) : 0;
  txt('CLEAR!', x + shake, y, 72, C.green, { align: 'center', rot: -0.08, scale: lerp(2.2, 1, easeOut(q)), alpha: q * 3 });
}
