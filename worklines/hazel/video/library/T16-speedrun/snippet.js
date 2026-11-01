// T16 Speedrun (retired: the trailer's first cut, replaced by T17 on 2026-10-31). Does not run alone.
// Parameters: STAGES [problem, fix] (one per second), the running device, the pips.
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.

// ---- from worklines/professor/video/src/index.html @ 7a76cc0, lines 563-594
// Scene 8 (48-54 s): bring-up speedrun.
const STAGES = [
  ['FIRST BACKUP: A 62-BYTE FILE', 'RETRY. VERIFIED BYTE FOR BYTE.'],
  ['ARCHR BOOTS TO A BLACK SCREEN', 'RIGHT PANEL DESCRIPTION. IT LIVES.'],
  ['THE WI-FI CHIP IS INVISIBLE', '3 HARDWARE PATCHES. wlan0 APPEARS.'],
  ['THE ROUTER REFUSES TO TALK', 'CHANNEL AUTO → 11. CONNECTED.'],
  ['TYPING ON A MATCHBOX SCREEN', '$ ssh luna'],
  ['A GAMING SYSTEM, ALL ROOT', 'NEW ROOT: ARCH LINUX ARM.']
];
function scene8(t) {
  const i = Math.min(5, Math.floor(t - 48)), t0 = 48 + i, lt = t - t0;
  sky('#060a22', '#0f2a3a'); stars(t, 220, 0.7);
  txt('SPEEDRUN: BRINGING UP THE HANDHELD', W / 2, 150, 40, C.chrome, { align: 'center' });
  txt('SEPT - OCT 2026, CARD BY CARD', W / 2, 205, 24, C.dim, { align: 'center' });
  txt(`STAGE 1-${i + 1}`, W / 2, 330, 32, C.amber, { align: 'center' });
  const [a, b] = STAGES[i];
  const pa = seg(lt, 0, 0.08), pb = seg(lt, 0.4, 0.48);
  txt(a, W / 2, 450, 48, C.chrome, { align: 'center', alpha: pa });
  if (pb > 0) txt(b, W / 2, 560, 48, i === 4 ? C.green : C.cyan, { align: 'center', alpha: pb, scale: lerp(1.3, 1, easeOut(pb)), font: 'P' });
  if (lt > 0.7) txt('CLEAR!', W / 2, 660, 32, C.green, { align: 'center' });
  // ground and running device
  const gy = 920;
  for (let x = 0; x < W; x += 40) { rect(x - ((t * 400) % 40), gy, 36, 18, '#2a3e6a'); }
  rect(0, gy + 18, W, H - gy - 18, '#0a1530');
  const prog = seg(t, 48, 54);
  const dx = lerp(M + 40, W - M - 160, prog), hop = Math.sin(clamp(lt / 0.5) * Math.PI) * 70;
  device(dx, gy - 168 - hop, 1.5, t, 'term');
  // pips
  for (let k = 0; k < 6; k++) rect(W / 2 - 3 * 60 + k * 60 + 10, 740, 40, 24, k <= i ? C.green : '#262c5a');
  flash(t, t0, 0, 0.12, '#ffffff');
}

