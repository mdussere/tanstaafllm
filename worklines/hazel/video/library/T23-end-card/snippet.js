// T23 End card. Does not run alone.
// Parameters: start time T0, the motto, the URL, the byline, fade in the last 0.5 s.
// Frame only: copy it unchanged, shift the times.
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 716-728
// ---- END CARD (84 - 90), as in the trailer (motto and PRESS START enlarged for the phone)
function sEnd(t) {
  rect(0, 0, W, H, C.ink); stars(t, 15, 0.8);
  moon(W / 2, 1080 + 200, 1100, 0.35);
  const p = easeOut(seg(t, 84.0, 84.4));
  titleLogo(W / 2, 330, lerp(1700, 1500, p), 1);
  txt('There Ain\'t No Such Thing As A Free LLM.', W / 2, 610, 64, C.chrome, { font: 'V', align: 'center', alpha: seg(t, 84.3, 84.5), shadow: 3 });
  txt('github.com/mdussere/tanstaafllm', W / 2, 710, 36, C.cyan, { align: 'center', alpha: seg(t, 84.6, 84.8) });
  txt('A personal engineering project by Michael Dussere', W / 2, 795, 48, C.chrome, { font: 'V', align: 'center', alpha: seg(t, 84.9, 85.1), shadow: 3 });
  if (t > 85.5 && Math.floor(TA * 3) % 2 === 0) txt('PRESS START', W / 2, 935, 40, C.amber, { align: 'center' });
  flash(t, 84.0, 0, 0.5);
  if (t > 89.5) rect(0, 0, W, H, '#000', seg(t, 89.5, 90.0));
}
