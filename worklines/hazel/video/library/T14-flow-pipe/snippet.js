// T14 Flow / pipe. Does not run alone.
// Parameters: two ends (sprite boxes), the pipe label, and packets [t0, t1, from, to, colour]:
// query out, answer back, act, event back. Story 2 stage 4.
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.
// Also needs stageBg, hud, clearStamp, stampTxt, tag, V, agent, miniDesk.

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 357-364
function packet(t, t0, t1, x0, x1, y, c) {
  if (t < t0 || t > t1 + 0.05) return;
  const p = easeOut(seg(t, t0, t1));
  for (let i = 0; i < 5; i++) rect(lerp(x0, x1, p) - (x1 > x0 ? 1 : -1) * i * 22 - 9, y - 9, 18, 18, c, 1 - i / 5);
}
function arrowHead(x, y, dir, c, s = 22) {
  ctx.save(); ctx.fillStyle = c; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - dir * s, y - s); ctx.lineTo(x - dir * s, y + s); ctx.fill(); ctx.restore();
}

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 534-559
// ---- STAGE 4 (36 - 44): the MCP bridge
function s4(t) {
  stageBg(t, 4); hud(t, 4, 36, STAGES[3][2]);
  agent(M + 20, 280, 9, t, 'ask');
  const P0 = M + 230, P1x = 1380, PY = 400;
  if (t > 36.3) {                                    // the pipe
    rect(P0, PY - 16, P1x - P0, 32, '#5c64a8'); rect(P0, PY - 10, P1x - P0, 20, '#14173a');
    for (let x = P0 + 10 + (TA * 120) % 60; x < P1x - 20; x += 60) rect(x, PY - 3, 24, 6, '#3b4178');
    tag('MCP OVER SSH', (P0 + P1x) / 2, PY - 40, C.cyan, seg(t, 36.3, 36.4), { align: 'center' });
    tag('DEVELOPMENT ONLY', (P0 + P1x) / 2, PY + 70, C.amber, seg(t, 36.6, 36.7), { align: 'center' });
  }
  box(1400, 250, 400, 300, { edge: C.green });
  const focus = t > 38.4 ? 2 : 0;
  miniDesk(1424, 274, 352, 220, { focus });
  tag('SWAY', 1600, 535, C.chrome, 1, { align: 'center' });
  packet(t, 37.0, 37.4, P0, P1x, PY, C.cyan);         // query ...
  packet(t, 37.45, 37.85, P1x, P0, PY, C.green);      // ... the tree comes back
  packet(t, 38.0, 38.4, P0, P1x, PY, C.amber);        // act
  packet(t, 39.0, 39.4, P1x, P0, PY, C.green);        // the event confirms it
  V('Query the tree, act,', M, 700, 90, C.chrome, seg(t, 37.0, 37.15));
  V('wait for the event.', M, 790, 90, C.chrome, seg(t, 39.0, 39.15));
  stampTxt('26 TOOLS', 1580, 700, 48, C.amber, t, 40.0, { align: 'center', rot: -0.04 });
  tag('luna-pi, THEN LUNA', 1580, 765, C.cyan, seg(t, 40.3, 40.4), { align: 'center' });
  clearStamp(t, 42.5);
  flash(t, 36.0, 0, 0.3);
}
