/* Game shell: the full-screen layer around every game (top bar, start, pause, game over, best score, auto-pause).
   The game module draws in a canvas; everything else here is plain HTML so it stays accessible and testable.

   Game module contract (js/games/<slug>.js):
     export const meta = {background: '#rrggbb', help: ['line', ...], intro?: 'line', tips?: {reason: 'line'}, frame?: true}
       intro: shown at the top of the start screen. tips: shown on the game-over screen for that reason.
       frame: load css/games/<slug>.css, the game's decorative frame (styles .game-<slug>, .gframe, .gc corners, .gpanel).
     export default function start(k, {seed, canvas, reducedMotion, onScore, onGameOver})
       -> {update(dt), draw(), destroy(), state?()}
   The shell owns the loop: it calls update(dt) only while playing (dt in seconds, small steps), draw() every frame.
   onScore(n) reports the running score, onGameOver(score, reason) ends the run. */
import kaplay,{_k} from '../vendor/kaplay.mjs';

const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
/* Test hook (set by the test suite before the page loads): {seed, speed}. Never set in normal use. */
const TEST=(typeof window!=='undefined'&&window.__novaGameTest)||null;

export async function open(g,opts){
  const mod=await import('./'+g.slug+'.js');
  const meta=mod.meta||{};
  const root=document.createElement('div');
  root.id='gameRoot';root.className='game game-'+g.slug;
  root.setAttribute('role','dialog');root.setAttribute('aria-modal','true');root.setAttribute('aria-label',g.title);
  root.innerHTML=`<div class="gbar">
      <button type="button" class="gbtn" data-g="back">← Book</button>
      <div class="gtitle">${esc(g.title)}</div>
      <div class="gscore" aria-live="off"><span>Spice <b id="gScore">0</b></span><span>Best <b id="gBest">${opts.best}</b></span></div>
      <button type="button" class="gbtn" data-g="pause" aria-label="Pause">❚❚</button>
    </div>
    <div class="gframe"><div class="gstage"><canvas id="gCanvas" tabindex="0" aria-label="${esc(g.title)} play area"></canvas><div class="gpanel" id="gPanel"></div></div>
      <i class="gc tl" aria-hidden="true"></i><i class="gc tr" aria-hidden="true"></i><i class="gc bl" aria-hidden="true"></i><i class="gc br" aria-hidden="true"></i></div>`;
  let css=null;
  if(meta.frame){   // wait (briefly) for the frame stylesheet so the game does not flash unstyled
    css=document.createElement('link');css.rel='stylesheet';css.href='css/games/'+g.slug+'.css';css.dataset.gameCss=g.slug;
    await new Promise(res=>{css.onload=css.onerror=res;setTimeout(res,1500);document.head.appendChild(css)});
  }
  document.body.appendChild(root);
  document.documentElement.classList.add('game-open');
  const $=s=>root.querySelector(s);
  const canvas=$('#gCanvas'),panel=$('#gPanel');
  const k=kaplay({canvas,root:root.querySelector('.gstage'),global:false,debug:false,loadingScreen:false,burp:false,backgroundAudio:false,touchToMouse:false,
    maxFPS:60,pixelDensity:Math.min(2,window.devicePixelRatio||1),background:meta.background||'#000000',focus:false});
  const reducedMotion=matchMedia('(prefers-reduced-motion: reduce)').matches;
  let game=null,phase='start',score=0,bestNow=opts.best,closed=false,seedN=0;
  const seed=()=>TEST&&TEST.seed!=null?TEST.seed:(Math.random()*2**31)|0;

  function newGame(){
    if(game)game.destroy();
    score=0;$('#gScore').textContent='0';
    seedN=seed();
    game=mod.default(k,{seed:seedN,canvas,reducedMotion,
      onScore:n=>{score=n;$('#gScore').textContent=n},
      onGameOver:(n,reason)=>{score=n;over(reason)}});
  }
  function setPhase(p){
    phase=p;root.dataset.phase=p;root.dataset.score=score;
    $('[data-g=pause]').hidden=p!=='play';
    panel.hidden=p==='play';
    if(p==='play')canvas.focus({preventScroll:true});
    else{const f=panel.querySelector('button');if(f)f.focus({preventScroll:true})}
  }
  const backBtn='<button type="button" class="gbtn ghost" data-g="back">Back to book</button>';
  function showStart(){
    panel.innerHTML=`<h2>${esc(g.title)}</h2>${meta.intro?`<p class="gintro">${esc(meta.intro)}</p>`:''}${(meta.help||[]).map(l=>`<p>${esc(l)}</p>`).join('')}
      <div class="gacts"><button type="button" class="gbtn big" data-g="go">Start</button>${backBtn}</div>`;
    setPhase('start');
  }
  function play(){setPhase('play')}
  function pause(){
    if(phase!=='play')return;
    panel.innerHTML=`<h2>Paused</h2><div class="gacts"><button type="button" class="gbtn big" data-g="resume">Resume</button><button type="button" class="gbtn" data-g="restart">Restart</button>${backBtn}</div>`;
    setPhase('paused');
  }
  function over(reason){
    const isNew=opts.saveBest(score);
    if(isNew){bestNow=score;$('#gBest').textContent=score}
    panel.innerHTML=`<h2>${esc(reason||'Game over')}</h2><p class="gbig">Spice: <b id="gFinal">${score}</b></p>
      <p>${isNew?'New best score!':'Best: '+bestNow}</p>${meta.tips&&meta.tips[reason]?`<p class="gtip">${esc(meta.tips[reason])}</p>`:''}
      <div class="gacts"><button type="button" class="gbtn big" data-g="again">Play again</button>${backBtn}</div>`;
    setPhase('over');
  }

  root.addEventListener('click',e=>{
    const b=e.target.closest('[data-g]');if(!b)return;
    const a=b.dataset.g;
    if(a==='back'){opts.back();return}
    if(a==='go'||a==='resume')play();
    else if(a==='pause')pause();
    else if(a==='restart'||a==='again'){newGame();play()}
  });
  const onKey=e=>{
    if(e.key==='Escape'||e.key==='p'||e.key==='P'){if(phase==='play'){pause();e.preventDefault()}else if(phase==='paused'&&e.key!=='Escape'){play()}}
  };
  const onHide=()=>{if(document.hidden)pause()};
  const onBlur=()=>pause();
  document.addEventListener('keydown',onKey);
  document.addEventListener('visibilitychange',onHide);
  window.addEventListener('blur',onBlur);

  k.onUpdate(()=>{
    if(phase!=='play'||!game)return;
    let t=Math.min(k.dt(),0.1)*(TEST&&TEST.speed||1);
    while(t>1e-6&&phase==='play'){const s=Math.min(t,1/30);game.update(s);t-=s}
    root.dataset.score=score;
  });
  k.onDraw(()=>{if(game)game.draw()});
  if(TEST)window.__novaGameState=()=>game&&game.state?game.state():null;

  newGame();showStart();

  return {close(){
    if(closed)return;closed=true;
    document.removeEventListener('keydown',onKey);
    document.removeEventListener('visibilitychange',onHide);
    window.removeEventListener('blur',onBlur);
    try{if(game)game.destroy()}catch(e){}
    try{k.quit()}catch(e){}
    _k.k=null;   // KAPLAY keeps its last instance in module state; clear it so the next Play starts clean (no re-init warning)
    root.remove();
    if(css)css.remove();
    document.documentElement.classList.remove('game-open');
    if(TEST)delete window.__novaGameState;
    const p=document.getElementById('playBtn');if(p)p.focus({preventScroll:true});
  }};
}
