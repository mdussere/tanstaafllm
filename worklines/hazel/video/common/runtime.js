// TANSTAAFLLM shared video runtime (extracted unchanged from Story 2's index.html head, plus the lint hooks).
'use strict';
const W = 1920, H = 1080, M = 120;          // canvas size and safe margin
const BPM = 120, BEAT = 60 / BPM;           // 0.5 s per beat, 2 s per bar
const cv = document.getElementById('c');
const ctx = cv.getContext('2d');
ctx.imageSmoothingEnabled = false;

const C = {
  ink: '#05060f', navy: '#070b24', navy2: '#0f1645', violet: '#2b1660', violet2: '#4a2a8c',
  amber: '#ffb43c', amber2: '#ff8a1e', cyan: '#3ee8ff', chrome: '#eef3ff', dim: '#8e97cc',
  red: '#ff4d5e', green: '#57ff8f', moon: '#a9b3d8', shadow: '#0a0420'
};

// ---------- tiny utilities ----------
const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
const seg = (t, a, b) => clamp((t - a) / (b - a));
const easeOut = p => 1 - Math.pow(1 - p, 3);
const easeIn = p => p * p * p;
const easeBack = p => { const s = 1.7; p -= 1; return p * p * ((s + 1) * p + s) + 1; };
const lerp = (a, b, p) => a + (b - a) * p;
function rng(seed) { return function () { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const beatPulse = t => Math.pow(1 - ((t / BEAT) % 1), 4);   // 1 on each beat, decays


// Reading holds (the generator writes them into the timeline): at each [source time, seconds], the
// choreography freezes so the last text stays on screen long enough to be read.
// TA is the ambient (output) time: stars, grid and blinks keep moving during a hold.
let HOLDS = [], TA = 0, DURATION = 60;
let NSTAGES = 7, BOSS = 5;                  // set from the episode (stages, boss_stage)
function sourceTime(T) {
  let acc = 0;
  for (const [s, d] of HOLDS) {
    if (T < s + acc) break;
    if (T < s + acc + d) return s;
    acc += d;
  }
  return T - acc;
}

const NOLIG = '0.1px';
// Text with a hard pixel drop shadow. font: 'P' (Press Start 2P) or 'V' (VT323).
function txt(s, x, y, size, color, o = {}) {
  const fam = (o.font || 'P') === 'P' ? 'PS2P' : 'VT';
  ctx.save();
  ctx.font = `${size}px ${fam}`;
  ctx.letterSpacing = NOLIG;            // non-zero spacing switches off the fonts' fi/fl ligatures
  ctx.textAlign = o.align || 'left';
  ctx.textBaseline = o.base || 'alphabetic';
  let sc = 1;
  const maxW = o.maxW || (W - 2 * M);
  const w = ctx.measureText(s).width;
  if (w > maxW) sc = maxW / w;
  ctx.globalAlpha = o.alpha === undefined ? 1 : clamp(o.alpha);
  ctx.translate(x, y);
  if (o.rot) ctx.rotate(o.rot);
  if (o.scale) ctx.scale(o.scale, o.scale);
  ctx.scale(sc, 1);
  const sh = o.shadow === undefined ? Math.max(2, Math.round(size / 8)) : o.shadow;
  if (sh) { ctx.fillStyle = o.shadowColor || C.shadow; ctx.fillText(s, sh, sh); }
  ctx.fillStyle = color;
  ctx.fillText(s, 0, 0);
  if (LINT.on && !o.noLint) lintRecord(s, x, y, size, o, w * sc, ctx.globalAlpha, sc);
  ctx.restore();
  return w * sc;
}
// ---------- layout lint (text only): every txt() call records its bounding box when LINT.on ----------
// squeeze: the horizontal scale txt() applied to fit maxW (1 = natural width). o.group: texts of one message laid out
// side by side (the metric tiles), counted as one message by the lint.
const LINT = { on: false, rec: [] };
function lintRecord(s, x, y, size, o, w, alpha, squeeze = 1) {
  const fam = (o.font || 'P') === 'P' ? 'PS2P' : 'VT';
  ctx.save(); ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.font = `${size}px ${fam}`; ctx.letterSpacing = NOLIG;
  const m = ctx.measureText(s), cap = ctx.measureText('H');
  ctx.restore();
  const k = o.scale || 1, asc = m.actualBoundingBoxAscent * k, desc = m.actualBoundingBoxDescent * k;
  const al = o.align || 'left';
  const x0 = al === 'center' ? -w * k / 2 : (al === 'right' ? -w * k : 0);
  const pts = [[x0, -asc], [x0 + w * k, -asc], [x0 + w * k, desc], [x0, desc]];
  const c = Math.cos(o.rot || 0), sn = Math.sin(o.rot || 0);
  const xs = pts.map(([px, py]) => x + px * c - py * sn), ys = pts.map(([px, py]) => y + px * sn + py * c);
  LINT.rec.push({ s, font: fam, size, scale: k, alpha, glyph: cap.actualBoundingBoxAscent * k, squeeze, group: o.group || null,
    x0: Math.min(...xs), x1: Math.max(...xs), y0: Math.min(...ys), y1: Math.max(...ys) });
}
function measure(s, size, font = 'P') { ctx.save(); ctx.font = `${size}px ${font === 'P' ? 'PS2P' : 'VT'}`; ctx.letterSpacing = NOLIG; const w = ctx.measureText(s).width; ctx.restore(); return w; }
// A line made of coloured runs: [[text, color], ...], centred or left-aligned.
function runs(parts, x, y, size, o = {}) {
  const full = parts.map(p => p[0]).join('');
  let w = measure(full, size, o.font || 'P');
  let sz = size;
  const maxW = o.maxW || (W - 2 * M);
  if (w > maxW) { sz = Math.floor(size * maxW / w); w = measure(full, sz, o.font || 'P'); }
  let cx = o.align === 'center' ? x - w / 2 : x;
  if (LINT.on) lintRecord(full, x, y, sz, Object.assign({}, o, { scale: 1, rot: 0 }), w, o.alpha === undefined ? 1 : clamp(o.alpha));
  for (const [s, col] of parts) { txt(s, cx, y, sz, col, Object.assign({}, o, { align: 'left', maxW: 99999, noLint: true })); cx += measure(s, sz, o.font || 'P'); }
  return w;
}
function rect(x, y, w, h, c, a = 1) { ctx.globalAlpha = a; ctx.fillStyle = c; ctx.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h)); ctx.globalAlpha = 1; }
// Pixel-art frame (box with double border, RPG style).
function box(x, y, w, h, o = {}) {
  const b = o.px || 6;
  rect(x, y, w, h, o.fill || C.navy, o.alpha === undefined ? 0.92 : o.alpha);
  rect(x, y, w, b, o.edge || C.chrome); rect(x, y + h - b, w, b, o.edge || C.chrome);
  rect(x, y, b, h, o.edge || C.chrome); rect(x + w - b, y, b, h, o.edge || C.chrome);
  rect(x + 2 * b, y + 2 * b, w - 4 * b, b / 2, o.inner || C.violet2);
  rect(x + 2 * b, y + h - 2.5 * b, w - 4 * b, b / 2, o.inner || C.violet2);
}
function flash(t, t0, up, down, color = '#fff') {
  let a = 0;
  if (t >= t0 - up && t < t0) a = seg(t, t0 - up, t0);
  else if (t >= t0 && t < t0 + down) a = 1 - seg(t, t0, t0 + down);
  if (a > 0) rect(0, 0, W, H, color, a);
}
// Blocky dissolve: squares of 60 px switch to colour in a pseudo-random order.
function dissolve(p, color = '#000', seed = 7) {
  if (p <= 0) return;
  const r = rng(seed), s = 60;
  ctx.fillStyle = color;
  for (let y = 0; y < H; y += s) for (let x = 0; x < W; x += s) if (r() < p) ctx.fillRect(x, y, s, s);
}
// Hand-drawn check mark and cross (the pixel fonts have no such glyphs).
function check(x, y, s, c) { ctx.save(); ctx.strokeStyle = c; ctx.lineWidth = s / 5; ctx.lineCap = 'square'; ctx.beginPath(); ctx.moveTo(x, y + s * .55); ctx.lineTo(x + s * .38, y + s * .9); ctx.lineTo(x + s, y + s * .1); ctx.stroke(); ctx.restore(); }

// ---------- backgrounds ----------
const STARS = (() => { const r = rng(42), a = []; for (let i = 0; i < 260; i++) a.push({ x: r() * W, y: r() * H, z: 0.2 + r() * 0.8, p: r() * 6.28 }); return a; })();
function stars(t, speed = 30, alpha = 1) {
  for (const s of STARS) {
    const x = ((s.x - TA * speed * s.z) % W + W) % W;   // ambient time: keeps moving during holds
    const tw = 0.55 + 0.45 * Math.sin(TA * 3 + s.p);
    const sz = s.z > 0.85 ? 6 : (s.z > 0.5 ? 4 : 3);
    rect(x, s.y, sz, sz, s.z > 0.9 ? C.amber : C.chrome, alpha * tw * (0.35 + 0.65 * s.z));
  }
}
function sky(top = C.navy, bottom = C.violet) {
  const g = ctx.createLinearGradient(0, 0, 0, H); g.addColorStop(0, top); g.addColorStop(1, bottom);
  ctx.fillStyle = g; ctx.fillRect(0, 0, W, H);
}
// Synthwave-ish pixel grid floor.
function grid(t, y0 = 760, color = C.violet2, alpha = 0.8) {
  ctx.save(); ctx.globalAlpha = alpha; ctx.strokeStyle = color; ctx.lineWidth = 3;
  const hy = y0, vx = W / 2;
  for (let i = -14; i <= 14; i++) { ctx.beginPath(); ctx.moveTo(vx + i * 30, hy); ctx.lineTo(vx + i * 260, H); ctx.stroke(); }
  const off = (TA * 1.2) % 1;
  for (let k = 0; k < 12; k++) { const p = Math.pow((k + off) / 12, 2.2); const y = hy + p * (H - hy); ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
  ctx.restore();
}
// Pixel moon, drawn once at low resolution and scaled with nearest-neighbour.
const MOON = (() => {
  const n = 96, c = document.createElement('canvas'); c.width = c.height = n; const g = c.getContext('2d');
  const r = rng(9), crat = []; for (let i = 0; i < 16; i++) crat.push([r() * n, r() * n, 2 + r() * 8]);
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) {
    const dx = x + .5 - n / 2, dy = y + .5 - n / 2, d = Math.hypot(dx, dy);
    if (d > n / 2 - 1) continue;
    let l = 0.95 - (dx + dy) / (n * 1.6);
    for (const [cx, cy, cr] of crat) { const e = Math.hypot(x - cx, y - cy); if (e < cr) l -= 0.18; if (e > cr - 1.2 && e < cr && x < cx) l += 0.1; }
    const dither = ((x + y) % 2) * 0.04;
    l = clamp(l + dither, 0.15, 1);
    const k = Math.round(l * 5) / 5;
    g.fillStyle = `rgb(${Math.round(60 + 120 * k)},${Math.round(70 + 125 * k)},${Math.round(120 + 110 * k)})`;
    g.fillRect(x, y, 1, 1);
  }
  return c;
})();
function moon(x, y, size, alpha = 1) { ctx.save(); ctx.globalAlpha = alpha; ctx.imageSmoothingEnabled = false; ctx.drawImage(MOON, x - size / 2, y - size / 2, size, size); ctx.restore(); }

// ---------- key art ----------
const ART = new Image(); ART.src = 'art/wallpaper.png';
const FACE = {               // crops in the 1254 x 1254 key art
  mannie: [70, 420, 300, 300], wyoh: [330, 540, 320, 320], mike: [620, 450, 330, 330], prof: [900, 610, 320, 320]
};
function face(name, x, y, s, alpha = 1, gray = 0) {
  const [sx, sy, sw, sh] = FACE[name];
  ctx.save(); ctx.globalAlpha = alpha; ctx.imageSmoothingEnabled = true;
  if (gray) ctx.filter = `grayscale(${gray}) brightness(${1 - gray * 0.5})`;
  ctx.drawImage(ART, sx, sy, sw, sh, x, y, s, s); ctx.restore();
}
// Draw the key art covering the frame, with an optional mosaic (block size in px).
const MOS = document.createElement('canvas');
function artCover(srcY, zoom, block = 1, alpha = 1) {
  const sc = (W / 1254) * zoom, sw = W / sc, sh = H / sc, sx = (1254 - sw) / 2;
  ctx.save(); ctx.globalAlpha = alpha;
  if (block > 1) {
    MOS.width = Math.ceil(W / block); MOS.height = Math.ceil(H / block);
    const g = MOS.getContext('2d'); g.imageSmoothingEnabled = true;
    g.drawImage(ART, sx, srcY, sw, sh, 0, 0, MOS.width, MOS.height);
    ctx.imageSmoothingEnabled = false; ctx.drawImage(MOS, 0, 0, W, H);
  } else { ctx.imageSmoothingEnabled = true; ctx.drawImage(ART, sx, srcY, sw, sh, 0, 0, W, H); }
  ctx.restore();
}
const LOGO = document.createElement('canvas');
function titleLogo(cx, cy, w, alpha = 1) {   // the chrome title from the key art
  const sx = 40, sy = 118, sw = 1190, sh = 290, h = w * sh / sw;
  LOGO.width = Math.ceil(w); LOGO.height = Math.ceil(h);
  const g = LOGO.getContext('2d'); g.globalCompositeOperation = 'source-over'; g.imageSmoothingEnabled = true;
  g.drawImage(ART, sx, sy, sw, sh, 0, 0, w, h);
  g.globalCompositeOperation = 'destination-in';
  const gh = g.createLinearGradient(0, 0, w, 0); gh.addColorStop(0, 'rgba(0,0,0,0)'); gh.addColorStop(0.05, '#000'); gh.addColorStop(0.95, '#000'); gh.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = gh; g.fillRect(0, 0, w, h);
  const gv = g.createLinearGradient(0, 0, 0, h); gv.addColorStop(0, 'rgba(0,0,0,0)'); gv.addColorStop(0.12, '#000'); gv.addColorStop(0.85, '#000'); gv.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = gv; g.fillRect(0, 0, w, h);
  ctx.save(); ctx.globalAlpha = alpha; ctx.drawImage(LOGO, cx - w / 2, cy - h / 2); ctx.restore();
  return h;
}

// ---------- pixel sprites ----------
function pgrid(ox, oy, s) {   // returns helpers drawing on an s-pixel grid
  return {
    r(x, y, w, h, c, a = 1) { rect(ox + x * s, oy + y * s, w * s, h * s, c, a); },
    circ(cx, cy, rad, c) { for (let y = Math.floor(cy - rad); y <= cy + rad; y++) for (let x = Math.floor(cx - rad); x <= cx + rad; x++) if ((x + .5 - cx) ** 2 + (y + .5 - cy) ** 2 <= rad * rad) rect(ox + x * s, oy + y * s, s, s, c); }
  };
}
// Luna, the R36 Ultra-style handheld: 80 x 112 cells. Screen content is animated.
function device(ox, oy, s, t, screen = 'moon') {
  const g = pgrid(ox, oy, s);
  g.r(5, -3, 16, 4, '#2a2e55'); g.r(59, -3, 16, 4, '#2a2e55');
  g.r(2, 0, 76, 112, '#14173a'); g.r(0, 2, 80, 108, '#14173a');
  g.r(3, 1, 74, 110, '#3b4178'); g.r(1, 3, 78, 106, '#3b4178');
  g.r(3, 2, 72, 2, '#5c64a8'); g.r(2, 4, 2, 100, '#5c64a8');
  g.r(9, 6, 62, 62, '#0b0d22');                                  // bezel
  const sx = 13, sy = 10, sw = 54, sh = 54;                      // square screen
  g.r(sx, sy, sw, sh, '#0c1440');
  // screen content
  if (screen === 'moon') {
    const r = rng(3); for (let i = 0; i < 18; i++) { const x = Math.floor(r() * sw), y = Math.floor(r() * sh); if ((Math.floor(TA * 4) + i) % 5) g.r(sx + x, sy + y, 1, 1, i % 4 ? '#c8d0ff' : C.amber); }
    ctx.save(); ctx.beginPath(); ctx.rect(ox + sx * s, oy + sy * s, sw * s, sh * s); ctx.clip();
    moon(ox + (sx + 27) * s, oy + (sy + 27) * s, 34 * s, 1);
    ctx.restore();
    if (Math.floor(TA * 2) % 2 === 0) g.r(sx + 4, sy + sh - 7, 3, 4, C.green);
  } else if (screen === 'term') {
    g.r(sx + 3, sy + 4, 18, 2, C.green); g.r(sx + 3, sy + 9, 30, 2, '#9aa3d8'); g.r(sx + 3, sy + 14, 24, 2, '#9aa3d8');
    if (Math.floor(TA * 2) % 2 === 0) g.r(sx + 3, sy + 19, 3, 3, C.green);
  }
  g.r(30, 70, 20, 2, '#5c64a8');                                 // brand strip
  // d-pad
  g.r(11, 78, 6, 18, '#111329'); g.r(5, 84, 18, 6, '#111329'); g.r(12, 79, 4, 16, '#272b52'); g.r(6, 85, 16, 4, '#272b52');
  // ABXY
  g.circ(64, 80, 3.5, '#ffd34d'); g.circ(64, 94, 3.5, '#57ff8f'); g.circ(57, 87, 3.5, '#3ee8ff'); g.circ(71, 87, 3.5, '#ff4d5e');
  // select / start / fn
  g.r(31, 76, 6, 2, '#111329'); g.r(43, 76, 6, 2, '#111329'); g.r(37, 81, 6, 2, '#111329');
  // sticks
  g.circ(30, 100, 6, '#111329'); g.circ(30, 100, 4, '#2a2e55'); g.circ(50, 100, 6, '#111329'); g.circ(50, 100, 4, '#2a2e55');
}
// Microphone icon on a 16 x 16 grid (Mycroft).
function mic(ox, oy, s, t) {
  const g = pgrid(ox, oy, s);
  g.r(6, 1, 4, 1, '#cfd6ff'); g.r(5, 2, 6, 7, '#cfd6ff'); g.r(6, 2, 2, 7, '#ffffff');
  g.r(3, 6, 1, 4, C.dim); g.r(12, 6, 1, 4, C.dim); g.r(4, 10, 8, 1, C.dim); g.r(7, 11, 2, 2, C.dim); g.r(5, 13, 6, 1, C.dim);
  for (let i = 0; i < 3; i++) { const a = 0.4 + 0.6 * Math.abs(Math.sin(t * 6 + i)); g.r(14 + i * 1.6, 5 - i, 0.8, 4 + 2 * i, C.cyan, a); g.r(1.2 - i * 1.6, 5 - i, 0.8, 4 + 2 * i, C.cyan, a); }
}
function coin(cx, cy, s, t) {   // spinning pixel coin
  const w = Math.max(0.15, Math.abs(Math.cos(t * 9)));
  ctx.save(); ctx.translate(cx, cy); ctx.scale(w, 1);
  const g = pgrid(-8 * s, -8 * s, s);
  g.circ(8, 8, 8, '#a35d00'); g.circ(8, 8, 7, C.amber); g.circ(8, 8, 5, '#ffd27a'); g.r(7, 4, 2, 8, '#a35d00');
  ctx.restore();
}


// ---------- shared staging and sprites (Story 2) ----------
// ---- extra sprites (all drawn here: icons, not pictures of real screens)
// A generic agent: a little robot, 20 x 24 cells. mode: 'look', 'squint', 'ask'.
function agent(ox, oy, s, t, mode = 'look') {
  const g = pgrid(ox, oy, s);
  g.r(9, 0, 2, 3, C.dim); g.r(8, -1, 4, 2, mode === 'ask' ? C.cyan : C.amber);
  g.r(1, 3, 18, 12, '#14173a'); g.r(2, 4, 16, 10, '#5c64a8'); g.r(2, 4, 16, 1, '#8e97cc');
  g.r(4, 6, 12, 6, '#111329');                                       // visor
  const blink = Math.floor(TA * 1.3) % 5 === 0 && (TA * 1.3) % 1 < 0.15;
  if (mode === 'squint') { g.r(5, 9, 4, 1, C.amber); g.r(11, 9, 4, 1, C.amber); g.r(5, 7, 4, 1, '#3b4178'); g.r(11, 7, 4, 1, '#3b4178'); }
  else if (blink) { g.r(5, 9, 4, 1, C.cyan); g.r(11, 9, 4, 1, C.cyan); }
  else { g.r(5, 7, 4, 3, C.cyan); g.r(11, 7, 4, 3, C.cyan); g.r(6, 7, 1, 1, '#ffffff'); g.r(12, 7, 1, 1, '#ffffff'); }
  g.r(7, 15, 6, 2, '#14173a');                                       // neck
  g.r(2, 17, 16, 8, '#14173a'); g.r(3, 18, 14, 6, '#3b4178');        // body
  g.r(8, 20, 4, 2, mode === 'ask' ? C.green : C.cyan);
  g.r(0, 18, 2, 5, '#3b4178'); g.r(18, 18, 2, 5, '#3b4178');         // arms
}
// A tiled desktop in miniature: a bar and up to three windows. o.focus: which window is focused.
function miniDesk(x, y, w, h, o = {}) {
  rect(x, y, w, h, '#0c1440');
  const bh = Math.max(8, Math.round(h * 0.07));
  rect(x, y, w, bh, '#14173a');
  for (let i = 0; i < 3; i++) rect(x + 6 + i * bh * 1.3, y + 2, bh - 4, bh - 4, i === (o.ws || 0) ? C.amber : '#3b4178');
  const n = o.n === undefined ? 3 : o.n, pad = Math.max(4, Math.round(w * 0.012)), top = y + bh + pad, H2 = h - bh - 2 * pad;
  const wins = n === 1 ? [[x + pad, top, w - 2 * pad, H2]]
    : n === 2 ? [[x + pad, top, (w - 3 * pad) / 2, H2], [x + 2 * pad + (w - 3 * pad) / 2, top, (w - 3 * pad) / 2, H2]]
    : [[x + pad, top, (w - 3 * pad) / 2, H2], [x + 2 * pad + (w - 3 * pad) / 2, top, (w - 3 * pad) / 2, (H2 - pad) / 2],
       [x + 2 * pad + (w - 3 * pad) / 2, top + (H2 + pad) / 2, (w - 3 * pad) / 2, (H2 - pad) / 2]];
  wins.forEach(([wx, wy, ww, wh], i) => {
    const f = i === (o.focus || 0);
    rect(wx, wy, ww, wh, f ? C.cyan : '#3b4178');
    const th = Math.max(5, Math.round(h * 0.045));
    rect(wx + 3, wy + th, ww - 6, wh - th - 3, o.bright ? ['#1d2a6a', '#2b1660', '#0f3a4a'][i] : '#05060f');
    if (o.bright) { rect(wx + ww * 0.2, wy + wh * 0.35, ww * 0.3, wh * 0.3, [C.amber, C.green, C.red][i]); rect(wx + ww * 0.6, wy + wh * 0.6, ww * 0.25, wh * 0.2, C.chrome); }
    for (let k = 0; k < 6; k++) {
      const ly = wy + th + 8 + k * Math.max(7, h * 0.05);
      if (ly > wy + wh - 10) break;
      rect(wx + 10, ly, (ww - 24) * (0.35 + 0.5 * ((i * 7 + k * 3) % 5) / 5), Math.max(2, h * 0.012), '#5c64a8');
    }
  });
  return wins;
}
// Blur a screen region into big blocks (what a model gets from a small, cheap screenshot).
const PIX = document.createElement('canvas');
function pixelate(x, y, w, h, block) {
  PIX.width = Math.ceil(w / block); PIX.height = Math.ceil(h / block);
  const g = PIX.getContext('2d'); g.imageSmoothingEnabled = true;
  g.drawImage(cv, x, y, w, h, 0, 0, PIX.width, PIX.height);
  ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(PIX, 0, 0, PIX.width, PIX.height, x, y, w, h); ctx.restore();
}
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
// Light a button on the device: 'B', 'FN', 'A', 'X', 'Y', 'UP', 'DOWN', 'LEFT', 'RIGHT', 'L1'.
function press(ox, oy, s, b) {
  const g = pgrid(ox, oy, s), c = '#ffffff';
  if (b === 'B') g.circ(64, 94, 3.5, c);
  else if (b === 'A') g.circ(71, 87, 3.5, c);
  else if (b === 'X') g.circ(64, 80, 3.5, c);
  else if (b === 'Y') g.circ(57, 87, 3.5, c);
  else if (b === 'FN') g.r(37, 81, 6, 2, c);
  else if (b === 'UP') g.r(12, 79, 4, 6, c);
  else if (b === 'DOWN') g.r(12, 89, 4, 6, c);
  else if (b === 'LEFT') g.r(6, 85, 6, 4, c);
  else if (b === 'RIGHT') g.r(16, 85, 6, 4, c);
  else if (b === 'L1') g.r(5, -3, 16, 4, c);
  else if (b === 'R1') g.r(59, -3, 16, 4, c);
}
function cross(x, y, s, c) { ctx.save(); ctx.strokeStyle = c; ctx.lineWidth = s / 5; ctx.lineCap = 'square'; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x + s, y + s); ctx.moveTo(x + s, y); ctx.lineTo(x, y + s); ctx.stroke(); ctx.restore(); }
function keycap(x, y, label, down) {
  const w = Math.max(120, measure(label, 32) + 50), h = 100, d = down ? 10 : 0;
  rect(x, y + 14, w, h, '#111329');
  rect(x, y + d, w, h, down ? C.amber : '#5c64a8'); rect(x + 8, y + d + 8, w - 16, h - 30, down ? '#ffd27a' : '#8e97cc');
  txt(label, x + w / 2, y + d + 62, 32, C.ink, { align: 'center', shadow: 0 });
  return w;
}
// A packet travelling along a line (from x0 to x1 at height y), with a short trail.
function packet(t, t0, t1, x0, x1, y, c) {
  if (t < t0 || t > t1 + 0.05) return;
  const p = easeOut(seg(t, t0, t1));
  for (let i = 0; i < 5; i++) rect(lerp(x0, x1, p) - (x1 > x0 ? 1 : -1) * i * 22 - 9, y - 9, 18, 18, c, 1 - i / 5);
}
function arrowHead(x, y, dir, c, s = 22) {
  ctx.save(); ctx.fillStyle = c; ctx.beginPath(); ctx.moveTo(x, y); ctx.lineTo(x - dir * s, y - s); ctx.lineTo(x - dir * s, y + s); ctx.fill(); ctx.restore();
}
// A stamp: scale-in with shake.
function stampTxt(s, x, y, size, color, t, t0, o = {}) {
  const q = seg(t, t0, t0 + 0.15);
  if (q <= 0) return;
  const sh = t < t0 + 0.35 ? Math.sin(t * 90) * 8 * (1 - seg(t, t0, t0 + 0.35)) : 0;
  txt(s, x + sh, y, size, color, Object.assign({ scale: lerp(o.from || 2, 1, easeOut(q)), alpha: q * 3 }, o));
}

// ---- shared staging
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
function clearStamp(t, tc, label = 'CLEAR!', color = C.green, x = W - M - 220, y = 980) {   // label: the stage's end stamp (default CLEAR!)
  const q = seg(t, tc, tc + 0.15);
  if (q <= 0) return;
  x = Math.min(x, W - M - measure(label, 72) * 0.55);   // a longer label moves left to stay inside the frame
  const shake = t < tc + 0.35 ? Math.sin(t * 90) * 8 * (1 - seg(t, tc, tc + 0.35)) : 0;
  txt(label, x + shake, y, 72, color, { align: 'center', rot: -0.08, scale: lerp(2.2, 1, easeOut(q)), alpha: q * 3 });
}
function termBox(x, y, w, h, edge = C.chrome) { box(x, y, w, h, { fill: '#05060f', edge, alpha: 0.95 }); }
function cursor(t, x, y, h, c = C.green) { if (Math.floor(TA * 4) % 2 === 0) rect(x + 4, y - h * 0.8, h * 0.5, h * 0.9, c); }
const V = (s, x, y, size, color, a, o = {}) => txt(s, x, y, size, color, Object.assign({ font: 'V', alpha: a, shadow: 3 }, o));
const tag = (s, x, y, color, a = 1, o = {}) => txt(s, x, y, 28, color, Object.assign({ alpha: a }, o));

// ---------- post: scanlines + vignette ----------
const POST = (() => {
  const c = document.createElement('canvas'); c.width = W; c.height = H; const g = c.getContext('2d');
  g.fillStyle = 'rgba(0,0,0,0.10)'; for (let y = 0; y < H; y += 4) g.fillRect(0, y + 2, W, 2);
  const v = g.createRadialGradient(W / 2, H / 2, H * 0.45, W / 2, H / 2, H * 1.05);
  v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(0,0,0,0.55)'); g.fillStyle = v; g.fillRect(0, 0, W, H);
  return c;
})();

// ---------- the player: the generated page defines EPISODE = {scenes, holds, base, stages, boss_stage} ----------
function renderFrame(T) {
  TA = T;
  const t = sourceTime(T);
  ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.filter = 'none';
  const S = EPISODE.scenes;
  const sc = S.find(s => t < s.t1) || S[S.length - 1];
  TPL[sc.template](t, sc.p);
  ctx.globalAlpha = 1; ctx.drawImage(POST, 0, 0);
}
window.renderFrame = renderFrame;
// Layout lint: render one frame with the text recorder on and return the recorded boxes.
window.lintFrame = T => { LINT.on = true; LINT.rec = []; renderFrame(T); LINT.on = false; return LINT.rec; };
NSTAGES = EPISODE.stages; BOSS = EPISODE.boss_stage;
HOLDS = EPISODE.holds.slice().sort((a, b) => a[0] - b[0]);
DURATION = EPISODE.base + HOLDS.reduce((a, h) => a + h[1], 0);
window.ready = Promise.all([
  document.fonts.load('32px PS2P'), document.fonts.load('32px VT'),
  new Promise(r => { if (ART.complete) r(); else ART.onload = r; })
]).then(() => document.fonts.ready).then(() => { window.DURATION = DURATION; });

window.ready.then(() => {
  const q = new URLSearchParams(location.search);
  if (q.has('play')) { const t0 = performance.now(); const loop = () => { renderFrame(((performance.now() - t0) / 1000) % DURATION); requestAnimationFrame(loop); }; loop(); }
  else renderFrame(parseFloat(q.get('t') || '0'));
});
