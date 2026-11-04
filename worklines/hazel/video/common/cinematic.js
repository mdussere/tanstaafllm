// Story 3 modular cinematic compositor. Assets are separate SVG files (RGBA at render time).
// Scene scripts specify independent layers and animation presets; shot renderer never hardcodes an episode scene id.
'use strict';
const CINEMA_FILES = [
  'workshop','screening','factory','arcade',
  'hazel-idle','hazel-work','hazel-hold','hazel-point',
  'projector','reel','coin','purse','filmstrip','cartridge','yaml','phone',
  'paper','magnifier','desk','beam'
];
const CINEMA_ART = {};
window.CINE_READY = Promise.all(CINEMA_FILES.map(name => new Promise((resolve, reject) => {
  const im = new Image();
  CINEMA_ART[name] = im;
  im.onload = resolve;
  im.onerror = () => reject(new Error('Cinema SVG asset not loaded: ' + name));
  im.src = 'art/cinema/' + name + '.svg';
})));
function cinemaSprite(name, x, y, w, h, alpha=1, angle=0, flip=false) {
  const im = CINEMA_ART[name]; if (!im || !im.complete || !im.naturalWidth) return;
  ctx.save(); ctx.globalAlpha = Math.max(0, Math.min(1, alpha));
  ctx.translate(x + w / 2, y + h / 2); ctx.rotate(angle);
  if (flip) ctx.scale(-1, 1);
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(im, -w / 2, -h / 2, w, h);
  ctx.restore();
}
function cinemaLayer(t, p, layer) {
  const local = t - p.t0, at = layer.at || 0;
  if (local < at || (layer.until !== undefined && local >= layer.until)) return;
  const fade = layer.fade === undefined ? 0.45 : layer.fade;
  const u = fade ? Math.min(1, (local-at)/fade) : 1, ease=1-Math.pow(1-u,3);
  const m=layer.motion||'still';
  let x=layer.x,y=layer.y,w=layer.w,h=layer.h,rot=(layer.rotate||0)*Math.PI/180;
  if(m==='drop') y -= (1-ease)*(layer.distance||480);
  if(m==='slide') x -= (1-ease)*(layer.distance||340);
  if(m==='slide-right') x += (1-ease)*(layer.distance||340);
  if(m==='float') y+=Math.sin(local*2.5+(layer.phase||0))*8;
  if(m==='travel') x+=(local-at)*(layer.speed||30);
  if(m==='spin') rot+=(local-at)*(layer.speed||2.8);
  if(m==='wobble') rot+=Math.sin(local*3)*0.06;
  if(m==='pop'){const s=0.65+0.35*ease;x+=(w-w*s)/2;y+=(h-h*s)/2;w*=s;h*=s;}
  if(m==='pulse'){const s=1+0.05*Math.sin(local*6); x+=(w-w*s)/2;y+=(h-h*s)/2;w*=s;h*=s;}
  cinemaSprite(layer.asset,x,y,w,h,u*(layer.opacity===undefined?1:layer.opacity),rot,!!layer.flip);
}
function cinemaStageEffect(t,p) {
  const local=t-p.t0, effect=p.effect||'';
  if(effect==='film-track') {
    const x0=90+(local*70)%240;
    for(let i=0;i<4;i++) cinemaSprite('filmstrip',x0+(i-1)*670,365,720,155,0.65);
    ctx.fillStyle='#3ee8ff'; ctx.fillRect(120+((local*215)%1600),530,15,105);
  }
  if(effect==='copy-storm') {
    for(let i=0;i<Math.min(12,Math.floor(local*2.3));i++){
      const x=70+(i*139)%1710,y=270+((i*71)%245);
      cinemaSprite('paper',x,y,115,145,0.86,(i%2?0.1:-0.08));
    }
  }
  if(effect==='library') {
    const n=Math.min(23,Math.max(0,Math.floor((local-0.45)*4)));
    for(let i=0;i<n;i++) {
      const x=180+(i%8)*199, y=145+Math.floor(i/8)*142;
      cinemaSprite('cartridge',x,y,150,110,0.94);
    }
    if(local>5.6){
      cinemaSprite('cartridge',830,400,230,178,Math.min(1,(local-5.6)*2));
      ctx.save();ctx.globalAlpha=Math.min(1,(local-5.6)*2);ctx.fillStyle='#ffb43c';
      ctx.fillRect(874,453,143,12);ctx.restore();
    }
  }
  if(effect==='inspection'){
    for(let i=0;i<3;i++){
      const x=480+i*300;
      ctx.fillStyle=i<Math.floor(local*0.6)?'#57ff8f':'#ff4d5e';
      ctx.fillRect(x,555,54,54);
    }
    cinemaSprite('magnifier',350+local*115,320+Math.sin(local*3)*36,175,175,0.88);
  }
  if(effect==='assembly') {
    for(let i=0;i<5;i++){
      const x=240+i*305-((local*130)%305);
      cinemaSprite(i%2?'cartridge':'yaml',x,368,i%2?170:115,i%2?130:149,0.85,0);
    }
  }
  if(effect==='recursion') {
    // A screen within the film within the screen; no recursive readback or infinite canvas dependency.
    for(let i=0;i<4;i++){
      const scale=Math.pow(.65,i),x=530+250*(1-scale),y=190+160*(1-scale);
      ctx.fillStyle=['#2b1660','#24466d','#324875','#26365a'][i];
      ctx.fillRect(x,y,790*scale,465*scale);
      ctx.strokeStyle='#3ee8ff';ctx.lineWidth=10*scale;ctx.strokeRect(x,y,790*scale,465*scale);
      cinemaSprite('projector',x+30*scale,y+55*scale,320*scale,230*scale,0.9);
      cinemaSprite('reel',x+72*scale,y+25*scale,90*scale,90*scale,0.9,local*(1+i*.13));
    }
    if(local>5.5) {
      ctx.fillStyle='#100e2b';ctx.fillRect(655,435,625,103);
      tag('STORY 3',884,499,C.amber,1,{align:'center'});
    }
  }
  if(effect==='receipts') {
    if(local>1){cinemaSprite('paper',400,230,260,320);}
    if(local>2){cinemaSprite('paper',1110,230,260,320);}
    if(local>2.8){
      tag('FULL EPISODE',420,291,C.amber);
      tag('~290K',455,390,C.chrome);
      tag('REVISION',1134,291,C.cyan);
      tag('~54K',1160,390,C.chrome);
    }
  }
  if(effect==='clockwork'){
    for(let i=0;i<5;i++){
      const x=190+i*315,y=377+Math.sin(local*4+i)*12;
      cinemaSprite(i%2?'reel':'cartridge',x,y,140,140,0.85,local*(i%2?-0.4:1));
    }
  }
  if(effect==='coin-return') {
    cinemaSprite('coin',780,330+Math.min(local*85,240),168,168,1,local*2);
  }
}
function cinemaFrame(t,p) {
  const local=t-p.t0;
  ctx.save();
  ctx.fillStyle='#080a1f';ctx.fillRect(0,0,W,H);
  cinemaSprite(p.backdrop||'workshop',0,0,W,H,1);
  // Camera pans only the prop stack, never the font/UI safe area.
  ctx.save();
  const pan=(p.pan||0)*Math.sin(local*.4),zoom=1+(p.zoom||0)*Math.min(1,local/Math.max(3,p.t1-p.t0));
  ctx.translate(W/2,420);ctx.scale(zoom,zoom);ctx.translate(-W/2+pan,-420);
  (p.layers||[]).slice().sort((a,b)=>(a.z||0)-(b.z||0)).forEach(l=>cinemaLayer(t,p,l));
  cinemaStageEffect(t,p);
  ctx.restore();

  // Diegetic subtitle treatment in the shared phone-safe 16:9 layout.
  // Graphic layer and typography remain independent; all story text is authored by the renderer.
  ctx.fillStyle='rgba(5,6,17,0.88)';ctx.fillRect(0,674,W,406);
  ctx.fillStyle='#ffb43c';ctx.fillRect(110,704,8,58);
  if(p.caption) tag(p.caption,138,719,C.amber,Math.min(1,local*3));
  const keyAt=p.key_at===undefined?1.0:p.key_at;
  if(local>=keyAt){
    const lines=Array.isArray(p.key)?p.key:[p.key];
    const al=Math.min(1,(local-keyAt)/.25);
    const sy=lines.length>1?806:851;
    lines.forEach((s,i)=>V(s,W/2,sy+i*92,90,C.chrome,al,{align:'center',maxW:1640}));
  }
  if(p.secondary && local>=p.secondary_at){
    const ss=Array.isArray(p.secondary)?p.secondary.join(' '):p.secondary;
    V(ss,W/2,984,64,C.cyan,Math.min(1,(local-p.secondary_at)/.2),{align:'center',maxW:1650});
  }
  ctx.restore();
}
