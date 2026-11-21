/* Theme switching: any theme in config.THEMES, or Auto (light/dark from the phone). */
import {THEMES,AUTO_LIGHT,AUTO_DARK} from './config.js';
import {$,esc} from './util.js';
import {S} from './state.js';
import {touch} from './sync.js';
import {openOv,closeOv} from './overlay.js';
export function themeMode(){
  let m='';try{m=S.theme||localStorage.getItem('nova-theme')||''}catch(e){m=S.theme||''}
  return THEMES.some(t=>t[0]===m)?m:'auto';
}
export function applyTheme(){
  const m=themeMode();
  const r=m==='auto'?(matchMedia('(prefers-color-scheme: light)').matches?AUTO_LIGHT:AUTO_DARK):m;
  document.documentElement.dataset.theme=r;
  const mt=document.querySelector('meta[name=theme-color]');if(mt)mt.content=THEMES.find(t=>t[0]===r)[3];
  const b=$('#themeBtn');if(b){const t=THEMES.find(x=>x[0]===m);b.textContent=t[1];b.title='Theme: '+t[2];b.setAttribute('aria-label','Theme: '+t[2]+'. Tap to change')}
}
export function setTheme(id){
  if(!THEMES.some(t=>t[0]===id))return;
  S.theme=id;try{localStorage.setItem('nova-theme',id)}catch(e){}
  applyTheme();touch();
}
export function themePicker(){
  const cur=themeMode();
  openOv(`<h3>Theme</h3><p>Your choice is saved with your account.</p>${THEMES.map(t=>`<button class="mrow ${t[0]===cur?'on':''}" data-act="settheme" data-v="${t[0]}"><span class="ck">${t[0]===cur?'✓':''}</span><span style="flex:1">${esc(t[2])}</span><i class="sw" style="background:${t[4]}"></i></button>`).join('')}
    <div style="margin-top:14px;text-align:right"><button class="btn sm ghost" data-act="ovclose2">Done</button></div>`);
}
export function initTheme(){
  const mq=matchMedia('(prefers-color-scheme: light)');
  if(mq.addEventListener)mq.addEventListener('change',()=>{if(themeMode()==='auto')applyTheme()});
}
