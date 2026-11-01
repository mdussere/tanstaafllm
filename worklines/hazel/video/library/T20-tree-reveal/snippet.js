// T20 Tree reveal. Does not run alone.
// Parameters: the query label, TREE [depth, label], first node time, step (0.12 s).
// Needs the shared renderer head (index.html lines 32-252): C, W, H, M, TA, clamp, seg, lerp, easeOut, easeBack, txt, runs, measure, rect, box, flash, dissolve, check, stars, sky, grid, moon, face, artCover, titleLogo, device, mic, coin.
// Also needs agent, packet, tag.

// ---- from worklines/hazel/video/story2-ask-the-desktop/src/index.html, lines 671-688
// ---- PAYOFF (72 - 78): the agent asks Sway, the tree comes back
const TREE = [[0, 'root'], [1, 'output DSI-1'], [2, 'workspace 1'], [3, 'window: foot'], [3, 'window: mike']];
function sPayoff(t) {
  sky(C.navy, '#1a0f45'); stars(t, 25, 0.8); grid(t, 900, C.violet2, 0.5);
  agent(M + 40, 300, 10, t, 'ask');
  const X0 = M + 280, X1 = 760;
  if (t > 72.3) {
    tag('sway_get_tree', X0 + 10, 330, C.cyan, seg(t, 72.3, 72.4));
    packet(t, 72.3, 72.8, X0, X1 + 300, 360, C.cyan);
  }
  TREE.forEach(([d, s], i) => {                       // windows, not what is inside them
    const t0 = 72.9 + i * 0.12;
    if (t < t0) return;
    const x = X1 + 300 + d * 80, y = 280 + i * 66;
    if (d > 0) { rect(x - 56, y - 50 - (i === 4 ? 66 : 0), 6, 50 + (i === 4 ? 66 : 0), C.dim); rect(x - 56, y - 6, 40, 6, C.dim); }
    rect(x, y - 38, measure(s, 28) + 30, 52, i >= 3 ? C.navy2 : C.violet);
    tag(s, x + 15, y, i >= 3 ? C.green : C.chrome);
  });
