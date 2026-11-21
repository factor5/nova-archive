/* Entry point: load data, wire up the page, start sync. */
import {$} from './util.js';
import {loadLocal} from './state.js';
import {applyTheme,themePicker,initTheme} from './theme.js';
import {authClick,connect,initOnline,setSync} from './sync.js';
import {prep} from './data.js';
import {route} from './views.js';
import {initActions} from './actions.js';
loadLocal();
initActions();
(async function(){
  try{
    const r=await fetch('data.json');if(!r.ok)throw new Error(r.status);
    prep(await r.json());
  }catch(e){
    $('#app').innerHTML='<div class="panel empty"><h3>Archive offline</h3><p>Could not load the award data. Please reload the page.</p></div>';return;
  }
  initTheme();applyTheme();$('#themeBtn').addEventListener('click',themePicker);setSync('loading');$('#authBtn').addEventListener('click',authClick);$('#sync').addEventListener('click',e=>e.currentTarget.classList.toggle('show'));route();connect();
  initOnline();
  if('serviceWorker' in navigator)navigator.serviceWorker.register('sw.js').catch(()=>{});
})();
