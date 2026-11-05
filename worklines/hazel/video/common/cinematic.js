// Story 3 V3b bitmap compositor. Every scene uses committed PNG frames: no SVG, runtime rotation, or smoothing.
'use strict';

const BITMAP_SPRITES = {
  hazel_idle: 'sprites/hazel_idle.png', hazel_work: 'sprites/hazel_work.png',
  hazel_reel: 'sprites/hazel_reel.png', hazel_point: 'sprites/hazel_point.png',
  hazel_excited: 'sprites/hazel_excited.png', hazel_walk: 'sprites/hazel_walk.png',
  projector: 'sprites/projector.png', reel: 'sprites/reel.png', coin: 'sprites/coin.png',
  purse: 'sprites/purse.png', terminal: 'sprites/terminal.png', cartridge: 'sprites/cartridge.png',
  yaml: 'sprites/yaml.png', phone: 'sprites/phone.png', paper_stack: 'sprites/paper_stack.png',
  magnifier: 'sprites/magnifier.png', workbench: 'sprites/workbench.png', beam: 'sprites/beam.png'
};
const BITMAP_BACKDROPS = ['workshop', 'screening', 'factory', 'arcade'];
const BITMAP_ANIMATIONS = {
  reel_spin: { n: 8, fps: 8, loop: true }, coin_insert: { n: 6, fps: 10, loop: false },
  hazel_reaction: { n: 4, fps: 3, loop: true }, hazel_working: { n: 4, fps: 4, loop: true },
  hazel_walking: { n: 4, fps: 5, loop: true }
};
// Kept while the V2 script is converted scene by scene. Each old semantic name resolves to a real V3 PNG.
const BITMAP_ALIASES = {
  'hazel-idle': 'hazel_idle', 'hazel-work': 'hazel_work', 'hazel-hold': 'hazel_reel',
  'hazel-point': 'hazel_point', paper: 'paper_stack', desk: 'workbench', filmstrip: 'paper_stack'
};
const BITMAP_ART = {};
function bitmapLoad(key, path) {
  const im = new Image(); BITMAP_ART[key] = im;
  return new Promise((resolve, reject) => { im.onload = resolve; im.onerror = () => reject(new Error('Bitmap asset not loaded: ' + path)); im.src = 'art/sprites-v3/' + path; });
}
const BITMAP_LOADS = [];
Object.entries(BITMAP_SPRITES).forEach(([name, path]) => BITMAP_LOADS.push(bitmapLoad(name, path)));
BITMAP_BACKDROPS.forEach(name => BITMAP_LOADS.push(bitmapLoad('bg_' + name, 'backgrounds/' + name + '.png')));
Object.entries(BITMAP_ANIMATIONS).forEach(([name, spec]) => {
  for (let i = 0; i < spec.n; i++) BITMAP_LOADS.push(bitmapLoad(name + '_' + i, 'animations/' + name + '/' + String(i).padStart(2, '0') + '.png'));
});
window.CINE_READY = Promise.all(BITMAP_LOADS);

function bitmapName(name) { return BITMAP_ALIASES[name] || name; }
function bitmapImage(name, local, animation) {
  if (animation && BITMAP_ANIMATIONS[animation]) {
    const a = BITMAP_ANIMATIONS[animation], raw = Math.max(0, Math.floor(local * a.fps));
    const n = a.loop ? raw % a.n : Math.min(a.n - 1, raw);
    return BITMAP_ART[animation + '_' + n];
  }
  return BITMAP_ART[bitmapName(name)];
}
function drawBitmap(name, x, y, maxW, maxH, alpha, local, o = {}) {
  const im = bitmapImage(name, local, o.animation);
  if (!im || !im.complete || !im.naturalWidth) return;
  const scale = Math.min(maxW / im.naturalWidth, maxH / im.naturalHeight);
  const w = Math.max(1, Math.round(im.naturalWidth * scale)), h = Math.max(1, Math.round(im.naturalHeight * scale));
  if (o.anchor === 'bottom-center') { x -= w / 2; y -= h; }
  else if (o.anchor === 'center') { x -= w / 2; y -= h / 2; }
  ctx.save(); ctx.globalAlpha = Math.max(0, Math.min(1, alpha)); ctx.imageSmoothingEnabled = false;
  if (o.flip) { ctx.translate(Math.round(x + w / 2), 0); ctx.scale(-1, 1); ctx.translate(-Math.round(x + w / 2), 0); }
  ctx.drawImage(im, Math.round(x), Math.round(y), w, h); ctx.restore();
}

function shotBox(p) {
  const shot = p.shot || 'vignette';
  if (shot === 'wide') return { x: 70, y: 78, w: 1780, h: 560 };
  if (shot === 'prop') return { x: 930, y: 92, w: 840, h: 510 };
  if (shot === 'close') return { x: 120, y: 74, w: 820, h: 560 };
  if (shot === 'reveal') return { x: 500, y: 65, w: 920, h: 590 };
  return { x: 85, y: 95, w: 880, h: 520 };
}
function panel(t, p, b) {
  const a = Math.min(1, Math.max(0, (t - p.t0) * 3));
  ctx.save(); ctx.globalAlpha = 0.94 * a; ctx.fillStyle = '#070b20'; ctx.fillRect(b.x - 18, b.y - 18, b.w + 36, b.h + 36);
  ctx.strokeStyle = C.violet2; ctx.lineWidth = 8; ctx.strokeRect(b.x - 18, b.y - 18, b.w + 36, b.h + 36); ctx.restore();
}
function layerBox(layer, b) {
  return { x: b.x + (layer.x / 1920) * b.w, y: b.y + (layer.y / 674) * b.h,
    w: Math.max(12, (layer.w / 1920) * b.w), h: Math.max(12, (layer.h / 674) * b.h) };
}
function cinemaLayer(t, p, layer, b) {
  const local = t - p.t0, at = layer.at || 0;
  if (local < at || (layer.until !== undefined && local >= layer.until)) return;
  const fade = layer.fade === undefined ? 0.35 : layer.fade;
  const u = fade ? Math.min(1, (local - at) / fade) : 1, ease = 1 - Math.pow(1 - u, 3);
  const q = layerBox(layer, b), m = layer.motion || 'still'; let { x, y, w, h } = q;
  if (m === 'slide') x -= (1 - ease) * Math.min(180, b.w * .25);
  if (m === 'slide-right') x += (1 - ease) * Math.min(180, b.w * .25);
  if (m === 'drop') y -= (1 - ease) * Math.min(210, b.h * .4);
  if (m === 'float' || m === 'spin') y += Math.round(Math.sin(local * 3 + (layer.phase || 0)) * 8);
  if (m === 'wobble') x += Math.round(Math.sin(local * 12) * 7);
  if (m === 'pop') { x += w * (1 - ease) / 2; y += h * (1 - ease) / 2; w *= ease; h *= ease; }
  const name = bitmapName(layer.asset);
  const animation = layer.animation || (m === 'spin' && name === 'reel' ? 'reel_spin' : (m === 'drop' && name === 'coin' ? 'coin_insert' : null));
  const hazel = name.startsWith('hazel_');
  drawBitmap(name, hazel ? x + w / 2 : x, hazel ? y + h : y, w, h, u * (layer.opacity === undefined ? 1 : layer.opacity), local - at,
             { anchor: hazel ? 'bottom-center' : undefined, animation, flip: !!layer.flip });
}
function cinemaEffect(t, p, b) {
  const local = t - p.t0, effect = p.effect || '';
  if (effect === 'clockwork') for (let i = 0; i < 4; i++) drawBitmap(i % 2 ? 'reel' : 'yaml', b.x + 80 + i * b.w / 4, b.y + b.h * .35, 120, 150, .9, local + i, { anchor: 'center', animation: i % 2 ? 'reel_spin' : null });
  if (effect === 'copy-storm') for (let i = 0; i < Math.min(8, Math.floor(local * 2)); i++) drawBitmap('paper_stack', b.x + 40 + (i * 121) % (b.w - 160), b.y + 70 + (i * 83) % (b.h - 190), 120, 150, .78, local + i, { anchor: 'center' });
  if (effect === 'library') for (let i = 0; i < Math.min(12, Math.floor(local * 2)); i++) drawBitmap('cartridge', b.x + 85 + (i % 4) * (b.w - 170) / 3, b.y + 80 + Math.floor(i / 4) * 125, 135, 105, .92, local, { anchor: 'center' });
  if (effect === 'inspection') drawBitmap('magnifier', b.x + b.w * .64 + Math.sin(local * 2) * 24, b.y + b.h * .44, 180, 180, .95, local, { anchor: 'center' });
  if (effect === 'assembly') { drawBitmap('yaml', b.x + b.w * .36, b.y + b.h * .5, 180, 210, 1, local, { anchor: 'center' }); drawBitmap('reel', b.x + b.w * .67, b.y + b.h * .5, 180, 180, 1, local, { anchor: 'center', animation: 'reel_spin' }); }
  if (effect === 'recursion') for (let i = 0; i < 3; i++) { const s = 1 - i * .19; ctx.strokeStyle = C.cyan; ctx.lineWidth = 7; ctx.strokeRect(b.x + 55 + i * 70, b.y + 45 + i * 48, (b.w - 110) * s, (b.h - 90) * s); }
  if (effect === 'coin-return') drawBitmap('coin', b.x + b.w / 2, b.y + 80 + Math.min(270, local * 80), 150, 150, 1, local, { anchor: 'center', animation: 'coin_insert' });
}
function cinematicText(t, p) {
  const local = t - p.t0, title = (p.shot || '') === 'title';
  ctx.fillStyle = 'rgba(5,6,17,.92)'; ctx.fillRect(0, 690, W, 390); ctx.fillStyle = C.amber; ctx.fillRect(105, 720, 8, 60);
  if (p.caption) tag(p.caption, 135, 736, C.amber, Math.min(1, local * 3));
  const ka = p.key_at === undefined ? 1 : p.key_at;
  if (local >= ka) {
    const lines = Array.isArray(p.key) ? p.key : [p.key], a = Math.min(1, (local - ka) / .2), y = lines.length > 1 ? 820 : 875;
    lines.forEach((s, i) => {
      if (title) stampTxt(s, W / 2, y + i * 92, 90, C.chrome, t, p.t0 + ka, { align: 'center', maxW: 1640, from: 1.6 });
      else V(s, W / 2, y + i * 92, 90, C.chrome, a, { align: 'center', maxW: 1640 });
    });
  }
  if (p.secondary && local >= p.secondary_at) V(Array.isArray(p.secondary) ? p.secondary.join(' ') : p.secondary, W / 2, 996, 62, C.cyan, Math.min(1, (local - p.secondary_at) / .2), { align: 'center', maxW: 1650 });
}
function cinemaFrame(t, p) {
  const bg = BITMAP_ART['bg_' + (p.backdrop || 'workshop')];
  ctx.fillStyle = '#080a1f'; ctx.fillRect(0, 0, W, H);
  if (bg && bg.complete) { ctx.save(); ctx.imageSmoothingEnabled = false; ctx.drawImage(bg, 0, 0, W, H); ctx.restore(); }
  const b = shotBox(p); panel(t, p, b); ctx.save(); ctx.beginPath(); ctx.rect(b.x, b.y, b.w, b.h); ctx.clip();
  (p.layers || []).slice().sort((a, z) => (a.z || 0) - (z.z || 0)).forEach(layer => cinemaLayer(t, p, layer, b)); cinemaEffect(t, p, b); ctx.restore();
  cinematicText(t, p); flash(t, p.t0, 0, .22, '#fff'); if (t > p.t1 - .18) flash(t, p.t1, .18, 0, '#fff');
}
