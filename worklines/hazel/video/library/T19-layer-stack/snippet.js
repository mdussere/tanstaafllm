// T19 Layer stack. Does not run alone.
// Parameters: LAYERS (names, cause to effect), LAYER_OK (tick times), the failing row and its time, lesson stamp.
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.
// Also needs stageBg, hud, clearStamp, stampTxt, tag, cross.

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 641-669
// ---- STAGE 7 (62 - 72): seven layers, from the pad to the game
const LAYERS = ['REAL PAD', 'WYOH DAEMON', 'APP PROFILE', 'VIRTUAL PAD', 'SDL', 'GAME BINDINGS', 'THE GAME MOVES'];
const LAYER_OK = [63.5, 63.75, 64.0, 64.25, 67.0, 67.5, 68.0];
function s7(t) {
  stageBg(t, 7); hud(t, 7, 62, STAGES[6][2]);
  tag('LUNA, 2026-10-30:', M, 290, C.dim, seg(t, 62.4, 62.6));
  tag("A GAME'S BUTTONS DIED.", M, 335, C.chrome, seg(t, 62.4, 62.6));
  txt('FIX "VERIFIED".', M, 470, 40, C.amber, { alpha: seg(t, 64.5, 64.65) });
  txt('THE GAME DID', M, 550, 40, C.red, { alpha: seg(t, 65.0, 65.15) });
  txt('NOT MOVE.', M, 610, 40, C.red, { alpha: seg(t, 65.0, 65.15) });
  if (t > 62.9) {
    const LX = 1000, LW = 800;
    LAYERS.forEach((s, i) => {
      const y = 230 + i * 74, ok = t >= LAYER_OK[i], fail = i === 6 && t >= 65.0 && !ok;
      const ver = i === 3 && t >= 64.5 && t < 67.0;
      rect(LX, y, LW, 60, ver ? '#3a2a10' : (i % 2 ? C.navy2 : C.violet), 0.85);
      rect(LX, y, 60, 60, ok ? C.green : (fail ? C.red : '#3b4178'));
      txt(String(i + 1), LX + 30, y + 45, 28, C.ink, { align: 'center', shadow: 0 });
      tag(s, LX + 88, y + 45, i === 6 ? C.chrome : C.dim);
      if (ok) check(LX + LW - 64, y + 11, 38, C.green);
      else if (fail) cross(LX + LW - 62, y + 13, 34, C.red);
      else if (i >= 4 && t > 64.5) txt('?', LX + LW - 45, y + 45, 28, C.dim, { align: 'center' });
    });
  }
  stampTxt('ONLY THE LAST LAYER', M, 840, 56, C.chrome, t, 68.5, { from: 1.4 });
  stampTxt('PROVES THE FIX.', M, 915, 56, C.chrome, t, 68.5, { from: 1.4 });
  clearStamp(t, 70.5);
  flash(t, 62.0, 0, 0.3);
}
