// T12 Handheld with screen states. Does not run alone.
// Parameters: scr = 'moon' | 'black' | 'q' | 'flash' | 'prompt' (Story 1) or 'desk' | 'slate' | 'mike' (Story 2),
// o.focus / o.ws / o.answerAt for the miniature desktop. Bob it: oy + round(sin(t*PI)*2)*4.
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.
// Story 2's version also needs miniDesk.

// ---- from worklines/hazel/video/story1-hello-luna/src/index.html, lines 266-280
// ---- extra sprites
function luna(ox, oy, s, t, scr) {     // the handheld with an overridden screen
  device(ox, oy, s, t, scr === 'moon' ? 'moon' : 'none');
  const x = ox + 13 * s, y = oy + 10 * s, w = 54 * s;
  if (scr === 'black' || scr === 'q') {
    rect(x, y, w, w, '#000');
    if (scr === 'q' && Math.floor(TA * 2) % 2 === 0) txt('?', x + w / 2, y + w / 2 + 30, 72, C.red, { align: 'center' });
  } else if (scr === 'prompt') {
    rect(x, y, w, w, '#02040c');
    txt('#', x + 24, y + 70, 40, C.green, { shadow: 0 });
    if (Math.floor(TA * 2) % 2 === 0) rect(x + 70, y + 36, 30, 36, C.green);
  } else if (scr === 'flash') {
    rect(x, y, w, w, '#fff');
  }
}

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 312-332
// The handheld (the shared device sprite) with Wyoh's screens drawn on it.
function luna(ox, oy, s, t, scr, o = {}) {
  device(ox, oy, s, t, scr === 'moon' ? 'moon' : 'none');
  const x = ox + 13 * s, y = oy + 10 * s, w = 54 * s;
  if (scr === 'black') rect(x, y, w, w, '#000');
  else if (scr === 'flash') rect(x, y, w, w, '#fff');
  else if (scr === 'desk' || scr === 'slate' || scr === 'mike') {
    const wins = miniDesk(x, y, w, w, { focus: o.focus || 0, ws: o.ws || 0, n: scr === 'mike' ? 2 : 3 });
    if (scr === 'slate') {                      // the Slate: a floating text zone
      const sx = x + w * 0.06, sy = y + w * 0.1, sw = w * 0.88, sh = w * 0.3;   // at the top of the panel
      rect(sx - 4, sy - 4, sw + 8, sh + 8, C.amber); rect(sx, sy, sw, sh, '#05060f');
      rect(sx + 14, sy + 18, sw * 0.55, 8, C.chrome); rect(sx + 14, sy + 40, sw * 0.35, 8, C.chrome);
      if (Math.floor(TA * 3) % 2 === 0) rect(sx + 14 + sw * 0.35 + 6, sy + 36, 6, 16, C.green);
    }
    if (scr === 'mike') {                       // Mike's window: a face and an answer
      const [mx, my, mw] = wins[1];
      face('mike', mx + 10, my + 16, Math.min(mw - 20, 90));
      for (let k = 0; k < 4; k++) if (t > (o.answerAt || 0) + k * 0.2) rect(mx + 10, my + 120 + k * 16, (mw - 30) * (k === 3 ? 0.5 : 0.9), 8, C.green);
    }
  }
}
