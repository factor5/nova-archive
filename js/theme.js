/* Theme switching: Dark (Nova), Paper (light) or Auto. */
import {THEMES} from './config.js';
import {$,toast} from './util.js';
import {S} from './state.js';
import {touch} from './sync.js';
export function themeMode(){try{return S.theme||localStorage.getItem('nova-theme')||'auto'}catch(e){return S.theme||'auto'}}
export function applyTheme(){
  const m=themeMode();const r=m==='auto'?(matchMedia('(prefers-color-scheme: light)').matches?'paper':'dark'):m;
  document.documentElement.dataset.theme=r;
  const mt=document.querySelector('meta[name=theme-color]');if(mt)mt.content=r==='paper'?'#f3eee1':'#04060d';
  const b=$('#themeBtn');if(b){const t=THEMES.find(x=>x[0]===m);b.textContent=t[1];b.title='Theme: '+t[2];b.setAttribute('aria-label','Theme: '+t[2]+'. Tap to change')}
}
export function cycleTheme(){
  const i=THEMES.findIndex(x=>x[0]===themeMode());const n=THEMES[(i+1)%THEMES.length];
  S.theme=n[0];try{localStorage.setItem('nova-theme',n[0])}catch(e){}
  applyTheme();touch();toast('Theme: '+n[2]);
}
export function initTheme(){
  const mq=matchMedia('(prefers-color-scheme: light)');
  if(mq.addEventListener)mq.addEventListener('change',()=>{if(themeMode()==='auto')applyTheme()});
}
