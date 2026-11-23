/* User actions: click and keyboard handlers, list and reading operations. */
import {setTheme,themePicker} from './theme.js';
import {openAddBook,pickResult,saveNew} from './addbook.js';
import {runImport} from './importlists.js';
import {PAGE} from './config.js';
import {$,esc,toast,uid} from './util.js';
import {S,rating,setMeta,ui} from './state.js';
import {touch} from './sync.js';
import {BYID,visible} from './data.js';
import {card,stars} from './cards.js';
import {bookOv,closeOv,listPicker,openOv,reviewOv} from './overlay.js';
import {renderAll,renderLists,renderResults,route} from './views.js';
let pickIds=[];
export function toggleRead(id){if(S.read.has(id))S.read.delete(id);else{S.read.add(id);delete S.reading[id]}touch()}
export function newList(name,ids){
  name=name.trim();if(!name)return null;
  const l={id:uid(),name,created:Date.now(),books:[...new Set(ids||[])]};S.lists.push(l);touch();return l;
}
document.addEventListener('click',ev=>{
  const aw=ev.target.closest('[data-aw]');
  if(aw){const k=aw.dataset.aw;ui.awards.has(k)?ui.awards.delete(k):ui.awards.add(k);ui.limit=PAGE;renderResults();return}
  const t=ev.target.closest('[data-act]');if(!t)return;
  const act=t.dataset.act,v=t.dataset.v;
  const host=t.closest('[data-id]');const id=host&&host.dataset.id;
  const cur=S.lists.find(l=>l.id===ui.listId);
  if(act==='ovclose'){if(ev.target===t)closeOv();return}
  if(act==='gobook'){ev.preventDefault();closeOv();location.hash='#book/'+encodeURIComponent(v||id);return}
  if(act==='back'){ev.preventDefault();if(history.length>1)history.back();else location.hash='#library';return}
  if(act==='gotolist'){ui.listId=v;location.hash='#lists';return}
  if(act==='addbook'){openAddBook();return}
  if(act==='importlists'){runImport();return}
  if(act==='abpick'){pickResult(v);return}
  if(act==='absave'){saveNew();return}
  if(act==='settheme'){setTheme(v);themePicker();return}
  if(act==='ovclose2'){closeOv();renderAll();return}
  if(act==='openbook'){bookOv(id);return}
  if(act==='read'){toggleRead(id);renderAll();return}
  if(act==='start'){if(S.read.has(id))S.read.delete(id);S.reading[id]=Date.now();touch();renderAll();toast('Started reading');return}
  if(act==='stop'){delete S.reading[id];touch();renderAll();return}
  if(act==='finish'){delete S.reading[id];S.read.add(id);setMeta(id,'f',Date.now());touch();closeOv();renderAll();reviewOv(id);return}
  if(act==='star'){const n=+v;setMeta(id,'r',rating(id)===n?0:n);touch();
    if(t.closest('.modal')){const w=t.closest('.rate');w.outerHTML=stars(id,true);const f=$('.modal .rate .st');}
    renderAll();return}
  if(act==='note'){reviewOv(id);return}
  if(act==='notesave'){const tx=$('#noteTxt');if(tx){setMeta(id,'n',tx.value.trim());touch()}closeOv();renderAll();toast('Saved');return}
  if(act==='author'){closeOv();ui.author=v;ui.limit=PAGE;if(ui.tab!=='library'){location.hash='#library'}else renderResults();window.scrollTo({top:0,behavior:'smooth'});return}
  if(act==='clearauthor'){ui.author='';renderResults();return}
  if(act==='more'){ui.limit+=PAGE;renderResults();return}
  if(act==='reset'){Object.assign(ui,{q:'',result:'all',read:'all',decade:'',source:'all',sort:'best',group:'none',limit:PAGE,author:''});ui.awards.clear();$('#app').innerHTML='';renderAll();return}
  if(act==='addlist'){pickIds=[id];const b=BYID.get(id);listPicker(pickIds,'Add to reading list',b.title+' — '+b.author);return}
  if(act==='addall'){const ids=visible().map(b=>b.id);if(!ids.length){toast('No books to add');return}pickIds=ids;listPicker(ids,'Add all results to a list',ids.length+' books currently shown by your filters');return}
  if(act==='toggle'){const l=S.lists.find(x=>x.id===v);const i=l.books.indexOf(pickIds[0]);i<0?l.books.push(pickIds[0]):l.books.splice(i,1);touch();listPicker(pickIds,'Add to reading list',BYID.get(pickIds[0]).title+' — '+BYID.get(pickIds[0]).author);return}
  if(act==='bulk'){const l=S.lists.find(x=>x.id===v);let n=0;for(const x of pickIds)if(!l.books.includes(x)){l.books.push(x);n++}touch();toast(n+' added to “'+l.name+'”');closeOv();renderAll();return}
  if(act==='ovnew'){const l=newList($('#ovNew').value,pickIds.length>1?pickIds:[]);if(!l){$('#ovNew').focus();return}
    if(pickIds.length===1){l.books.push(pickIds[0]);touch()}toast('Added to “'+l.name+'”');closeOv();renderAll();return}
  if(act==='surprise'){const pool=visible().filter(b=>!S.read.has(b.id));if(!pool.length){toast('Nothing unread matches — widen your filters');return}
    const b=pool[Math.floor(Math.random()*pool.length)];
    openOv(`<h3>Your next transmission</h3><p>A random unread pick from your current filters.</p><div class="grid" style="grid-template-columns:1fr">${card(b)}</div><div style="margin-top:14px;display:flex;gap:8px;justify-content:flex-end"><button class="btn sm" data-act="surprise">Another</button><button class="btn sm ghost" data-act="ovclose2">Close</button></div>`);return}
  if(act==='pick'){ui.listId=v;renderLists();return}
  if(act==='newlist'){const el=$('#newListName');const l=newList(el.value,[]);if(!l){el.focus();return}ui.listId=l.id;renderAll();return}
  if(act==='dellist'){if(t.dataset.sure){S.lists=S.lists.filter(l=>l.id!==ui.listId);touch();renderAll();toast('List deleted')}else{t.dataset.sure='1';t.textContent='Click again to confirm';setTimeout(()=>{if(t.isConnected){delete t.dataset.sure;t.textContent='Delete list'}},3000)}return}
  if(act==='copylist'&&cur){const txt=cur.name+'\n'+cur.books.map(i=>BYID.get(i)).filter(Boolean).map((b,i)=>(i+1)+'. '+b.title+' — '+b.author+(S.read.has(b.id)?' [read]':'')).join('\n');
    (navigator.clipboard?navigator.clipboard.writeText(txt):Promise.reject()).then(()=>toast('List copied'),()=>{openOv('<h3>Copy list</h3><p>Select and copy the text below.</p><textarea readonly style="width:100%;height:220px;background:var(--field);color:var(--text);border:1px solid var(--line);border-radius:8px;padding:10px;font:inherit">'+esc(txt)+'</textarea><div style="margin-top:12px;text-align:right"><button class="btn sm" data-act="ovclose2">Close</button></div>')});return}
  if(cur&&(act==='up'||act==='down'||act==='rm')&&id){const i=cur.books.indexOf(id);if(i<0)return;
    if(act==='rm')cur.books.splice(i,1);
    else{const j=act==='up'?i-1:i+1;if(j<0||j>=cur.books.length)return;[cur.books[i],cur.books[j]]=[cur.books[j],cur.books[i]]}
    touch();renderAll();return}
});
document.addEventListener('keydown',e=>{if(e.key==='Escape')closeOv();if((e.key==='Enter'||e.key===' ')&&e.target.classList&&e.target.classList.contains('ncard')){e.preventDefault();bookOv(e.target.dataset.id)}});
export function initActions(){
  window.addEventListener('hashchange',route);
(function(){const b=$('#toTop');let t=0;
  const upd=()=>{t=0;b.hidden=window.scrollY<500};
  window.addEventListener('scroll',()=>{if(!t)t=requestAnimationFrame(upd)},{passive:true});
  b.addEventListener('click',()=>window.scrollTo({top:0,behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth'}));
  upd()})();
}
