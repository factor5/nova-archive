/* Spice Run (Dune): top-down survival, endless score run. Game spec: docs/games/dune/README.md.
   Collect spice. Moving fast makes noise; noise draws the worm. The storm moves in from the top; spice pushes it back.
   World units: the shorter side of the play area is always 360 units, so the game feels the same on any screen. */

export const meta={
  background:'#d8b57c',
  frame:true,
  intro:'Betrayed and hunted, you have fled into the deep desert. The storm that hid you is still at your back, and something vast moves under the sand.',
  tips:{
    'Taken by the worm':'Tip: the desert people walk without rhythm. Slow, soft steps do not carry through the sand, so stay inside the inner ring when the worm is near.',
    'Lost in the storm':'Tip: every spice you gather pushes the storm back. Creeping keeps you safe from the worm, but not from the storm.'
  },
  help:[
    'Drag anywhere to move (arrow keys or WASD on a keyboard, hold Shift to run).',
    'The further you drag, the faster you go, and the more noise you make. Noise draws the worm.',
    'The storm moves in from the top. Collect spice to push it back.'
  ]
};

/* Tuning knobs, all in world units and seconds. Changed after playtests. */
const C={
  side:360, playerR:9, maxSpeed:140, quietBelow:0.35,
  noiseUp:2.5, noiseDown:0.6, hearAt:0.3,
  wormR:13, wormRoam:35, wormHunt:58, wormHuntLoud:47, wormTurn:2.2, wormLen:16,
  wormAccel:40, wormBrake:80,   // the worm speeds up gradually when it hears you (units/s per second), slows down faster
  stormSpeed:9, stormPush:28, stormStart:-20,
  spiceCount:4, spiceR:6, pickup:15, respawn:0.6,
  rampSeconds:120, maxDiff:1.8,
  // joystick, in screen pixels: full speed at joyR; nothing within joyDead; joyCurve > 1 gives more room for slow, quiet walking
  joyR:110, joyDead:8, joyCurve:1.6
};

function rng(seed){let a=seed>>>0;return ()=>{a=(a+0x6D2B79F5)>>>0;let t=a;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return ((t^t>>>14)>>>0)/4294967296}}
const clamp=(v,a,b)=>v<a?a:v>b?b:v;
const ang=a=>Math.atan2(Math.sin(a),Math.cos(a));

export default function start(k,{seed,canvas,reducedMotion,onScore,onGameOver}){
  const R=rng(seed);
  let u=1,W=C.side,H=C.side;           // pixels per unit, world size in units
  function measure(){u=Math.min(k.width(),k.height())/C.side;W=k.width()/u;H=k.height()/u}
  measure();
  const P={x:W/2,y:H*0.62,vx:0,vy:0};
  const worm={x:W*0.12,y:H-24,dir:-Math.PI/2,state:'roam',tx:W*0.5,ty:H*0.8,trail:[],speed:C.wormRoam};
  let noise=0,storm=C.stormStart,t=0,score=0,alive=true,shake=0,spawnT=[];
  const spice=[];
  const dunes=Array.from({length:14},()=>({y:R(),a:4+R()*10,f:0.006+R()*0.01,p:R()*6.28}));
  const rnd=(a,b)=>a+R()*(b-a);
  function placeSpice(){
    for(let i=0;i<20;i++){
      const s={x:rnd(20,W-20),y:rnd(Math.max(storm,0)+50,H-20)};
      if(Math.hypot(s.x-P.x,s.y-P.y)>60){spice.push(s);return}
    }
    spice.push({x:rnd(20,W-20),y:rnd(Math.max(storm,0)+50,H-20)});
  }
  for(let i=0;i<C.spiceCount;i++)placeSpice();
  for(let i=0;i<C.wormLen;i++)worm.trail.push({x:worm.x,y:worm.y});

  /* Input: one pointer (touch, mouse or pen) is a floating joystick; keyboard as a fallback. */
  const joy={id:null,ox:0,oy:0,dx:0,dy:0};
  const pos=e=>{const r=canvas.getBoundingClientRect();return [(e.clientX-r.left)*k.width()/r.width,(e.clientY-r.top)*k.height()/r.height]};
  const down=e=>{if(joy.id!==null)return;joy.id=e.pointerId;[joy.ox,joy.oy]=pos(e);joy.dx=joy.dy=0;try{canvas.setPointerCapture(e.pointerId)}catch(x){}e.preventDefault()};
  const move=e=>{
    if(e.pointerId!==joy.id)return;
    const [x,y]=pos(e);let dx=x-joy.ox,dy=y-joy.oy;const len=Math.hypot(dx,dy);
    // the base follows the thumb once it passes the edge, so changing direction is immediate
    if(len>C.joyR){const f=1-C.joyR/len;joy.ox+=dx*f;joy.oy+=dy*f;dx=x-joy.ox;dy=y-joy.oy}
    joy.dx=dx;joy.dy=dy;e.preventDefault()};
  const up=e=>{if(e.pointerId!==joy.id)return;joy.id=null;joy.dx=joy.dy=0};
  canvas.addEventListener('pointerdown',down);canvas.addEventListener('pointermove',move);
  canvas.addEventListener('pointerup',up);canvas.addEventListener('pointercancel',up);
  // the canvas is resized by KAPLAY after the window's resize event, so check its size every frame instead
  let seenW=k.width(),seenH=k.height();
  // on a resize (e.g. turning the phone) everything keeps its place relative to the screen, so the storm cannot jump onto you
  const onResize=()=>{
    seenW=k.width();seenH=k.height();
    const W0=W,H0=H;measure();const sx=W/W0,sy=H/H0;
    const fit=(o,r)=>{o.x=clamp(o.x*sx,r,W-r);o.y=clamp(o.y*sy,r,H-r)};
    fit(P,C.playerR);fit(worm,0);for(const s of spice)fit(s,20);for(const a of worm.trail){a.x*=sx;a.y*=sy}
    worm.tx*=sx;worm.ty*=sy;storm=storm>0?storm*sy:storm;
  };

  function input(){
    if(joy.id!==null){
      const len=Math.hypot(joy.dx,joy.dy);
      if(len<C.joyDead)return [0,0,0];
      const d=Math.min(1,(len-C.joyDead)/(C.joyR-C.joyDead));
      return [joy.dx/len,joy.dy/len,Math.pow(d,C.joyCurve)];   // speed as a share of maxSpeed
    }
    let x=0,y=0;
    if(k.isKeyDown('left')||k.isKeyDown('a'))x--;
    if(k.isKeyDown('right')||k.isKeyDown('d'))x++;
    if(k.isKeyDown('up')||k.isKeyDown('w'))y--;
    if(k.isKeyDown('down')||k.isKeyDown('s'))y++;
    if(!x&&!y)return [0,0,0];
    const l=Math.hypot(x,y);
    return [x/l,y/l,k.isKeyDown('shift')?1:0.34];
  }

  function end(reason){alive=false;if(!reducedMotion)shake=0.35;onGameOver(score,reason)}

  function update(dt){
    if(!alive)return;
    t+=dt;
    const diff=Math.min(C.maxDiff,1+t/C.rampSeconds);
    // player
    const [ix,iy,d]=input();
    const sp=C.maxSpeed*d;
    P.x=clamp(P.x+ix*sp*dt,C.playerR,W-C.playerR);
    P.y=clamp(P.y+iy*sp*dt,C.playerR,H-C.playerR);
    // noise follows speed; slow walking is silent
    const target=Math.pow(clamp((d-C.quietBelow)/(1-C.quietBelow),0,1),1.2);
    noise=target>noise?Math.min(target,noise+C.noiseUp*dt):Math.max(target,noise-C.noiseDown*dt);
    // worm: hears noise, hunts the last place it heard you, roams when it loses you
    if(noise>C.hearAt){worm.state='hunt';worm.tx=P.x;worm.ty=P.y}
    const toT=Math.hypot(worm.tx-worm.x,worm.ty-worm.y);
    if(toT<12){
      if(worm.state==='hunt')worm.state='roam';
      worm.tx=rnd(20,W-20);worm.ty=rnd(Math.max(storm,0)+40,H-20);
    }
    const want=Math.atan2(worm.ty-worm.y,worm.tx-worm.x);
    const turn=C.wormTurn*Math.sqrt(diff)*dt;
    worm.dir+=clamp(ang(want-worm.dir),-turn,turn);
    const wantSpeed=(worm.state==='hunt'?C.wormHunt+C.wormHuntLoud*noise:C.wormRoam)*diff;
    worm.speed=wantSpeed>worm.speed?Math.min(wantSpeed,worm.speed+C.wormAccel*diff*dt):Math.max(wantSpeed,worm.speed-C.wormBrake*dt);
    worm.x=clamp(worm.x+Math.cos(worm.dir)*worm.speed*dt,0,W);
    worm.y=clamp(worm.y+Math.sin(worm.dir)*worm.speed*dt,0,H);
    const last=worm.trail[0];
    if(Math.hypot(worm.x-last.x,worm.y-last.y)>5){worm.trail.unshift({x:worm.x,y:worm.y});worm.trail.length=C.wormLen}
    if(Math.hypot(worm.x-P.x,worm.y-P.y)<C.wormR+C.playerR){end('Taken by the worm');return}
    // storm closes in from the top
    storm+=C.stormSpeed*diff*dt;
    if(P.y-C.playerR<storm){end('Lost in the storm');return}
    // spice
    for(let i=spice.length-1;i>=0;i--){
      const s=spice[i];
      if(s.y<storm){spice.splice(i,1);spawnT.push(C.respawn);continue}
      if(Math.hypot(s.x-P.x,s.y-P.y)<C.pickup){
        spice.splice(i,1);spawnT.push(C.respawn);score++;onScore(score);
        storm=Math.max(C.stormStart,storm-C.stormPush);
      }
    }
    spawnT=spawnT.map(x=>x-dt);
    while(spawnT.length&&spawnT[0]<=0){spawnT.shift();placeSpice()}
  }

  /* Drawing. Danger is shown by shape and motion, not only colour (worm rings, striped storm, LOUD label). */
  const col={sand:k.rgb(216,181,124),dune:k.rgb(190,150,95),ink:k.rgb(43,28,16),player:k.rgb(250,244,230),
    spice:k.rgb(214,96,28),spiceHi:k.rgb(255,196,120),worm:k.rgb(92,60,34),storm:k.rgb(120,84,52),stormLine:k.rgb(236,214,176),
    meter:k.rgb(60,40,22),quiet:k.rgb(244,236,218),loud:k.rgb(40,24,12)};
  const V=(x,y)=>k.vec2(x,y);
  function draw(){
    if(k.width()!==seenW||k.height()!==seenH)onResize();
    k.pushTransform();
    if(shake>0){shake=Math.max(0,shake-k.dt());k.pushTranslate(V((R()-0.5)*8*shake/0.35,(R()-0.5)*8*shake/0.35))}
    k.pushScale(V(u,u));
    for(const d of dunes){
      const y0=d.y*H,pts=[];
      for(let x=0;x<=W+20;x+=20)pts.push(V(x,y0+Math.sin(x*d.f+d.p)*d.a));
      k.drawLines({pts,width:1.5,color:col.dune,opacity:0.7});
    }
    for(const s of spice){
      const p=1+0.15*Math.sin(t*5+s.x);
      k.drawCircle({pos:V(s.x,s.y),radius:C.spiceR*1.9*p,color:col.spiceHi,opacity:0.35});
      k.drawPolygon({pts:[V(s.x,s.y-C.spiceR*1.3),V(s.x+C.spiceR,s.y),V(s.x,s.y+C.spiceR*1.3),V(s.x-C.spiceR,s.y)],color:col.spice});
    }
    // worm: a moving ridge of sand with rings around its head; rings grow while it hunts
    for(let i=worm.trail.length-1;i>0;i--){
      const a=worm.trail[i];
      k.drawCircle({pos:V(a.x,a.y),radius:C.wormR*(1-i/worm.trail.length*0.6),color:col.worm,opacity:0.18+0.4*(1-i/worm.trail.length)});
    }
    const rings=worm.state==='hunt'?3:1;
    for(let r=0;r<rings;r++){
      const ph=((t*1.5+r/rings)%1);
      k.drawCircle({pos:V(worm.x,worm.y),radius:C.wormR+ph*26,fill:false,outline:{width:2,color:col.ink},opacity:(1-ph)*0.8});
    }
    k.drawCircle({pos:V(worm.x,worm.y),radius:C.wormR,color:col.worm,outline:{width:2,color:col.ink}});
    // player
    k.drawCircle({pos:V(P.x,P.y),radius:C.playerR+3,color:col.ink,opacity:0.25});
    k.drawCircle({pos:V(P.x,P.y),radius:C.playerR,color:col.player,outline:{width:2.5,color:col.ink}});
    k.drawCircle({pos:V(P.x,P.y),radius:2.5,color:col.ink});
    // storm band with moving stripes and a ragged front
    if(storm>0){
      k.drawRect({pos:V(0,0),width:W,height:storm,color:col.storm,opacity:0.85});
      for(let y=storm-6-((t*30)%14);y>0;y-=14)k.drawLine({p1:V(0,y),p2:V(W,y+6),width:2,color:col.stormLine,opacity:0.5});
      const pts=[];for(let x=0;x<=W+12;x+=12)pts.push(V(x,storm+Math.sin(x*0.15+t*4)*3));
      k.drawLines({pts,width:3,color:col.ink});
    }
    k.popTransform();
    // noise meter (screen space, top left)
    const mw=Math.min(160,k.width()*0.42),mx=12,my=12;
    const loud=noise>C.hearAt;
    k.drawRect({pos:V(mx,my),width:mw,height:14,color:col.quiet,opacity:0.55,radius:4,outline:{width:2,color:col.ink}});
    k.drawRect({pos:V(mx+2,my+2),width:Math.max(0,(mw-4)*noise),height:10,color:loud?col.ink:col.meter,opacity:loud?1:0.6,radius:3});
    k.drawLine({p1:V(mx+2+(mw-4)*C.hearAt,my-3),p2:V(mx+2+(mw-4)*C.hearAt,my+17),width:2,color:col.ink});
    k.drawText({text:loud?'NOISE: LOUD, the worm hears you':'noise',pos:V(mx,my+18),size:12,color:col.ink});
    // floating joystick
    if(joy.id!==null){
      k.drawCircle({pos:V(joy.ox,joy.oy),radius:C.joyR,fill:false,outline:{width:2,color:col.ink},opacity:0.5});
      // inner ring: inside it you walk silently
      k.drawCircle({pos:V(joy.ox,joy.oy),radius:C.joyDead+(C.joyR-C.joyDead)*Math.pow(C.quietBelow,1/C.joyCurve),fill:false,outline:{width:1.5,color:col.ink},opacity:0.35});
      const len=Math.hypot(joy.dx,joy.dy),m=Math.min(len,C.joyR),kx=len?joy.ox+joy.dx/len*m:joy.ox,ky=len?joy.oy+joy.dy/len*m:joy.oy;
      k.drawCircle({pos:V(kx,ky),radius:16,fill:false,outline:{width:3,color:col.ink},opacity:0.45});
    }
  }

  return {
    update,draw,
    state:()=>({x:P.x,y:P.y,noise,storm,score,alive,t,worm:{x:worm.x,y:worm.y,state:worm.state},spice:spice.map(s=>({x:s.x,y:s.y}))}),
    destroy(){
      canvas.removeEventListener('pointerdown',down);canvas.removeEventListener('pointermove',move);
      canvas.removeEventListener('pointerup',up);canvas.removeEventListener('pointercancel',up);
    }
  };
}
