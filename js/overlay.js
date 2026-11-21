/* Modal dialogs: list picker, book preview, rating and notes. */
import {$,esc} from './util.js';
import {S,ui} from './state.js';
import {BYID} from './data.js';
import {card,stars} from './cards.js';
/* ---------- overlay ---------- */
export function openOv(html){const r=$('#ovRoot');r.innerHTML=`<div class="ov" data-act="ovclose"><div class="modal" role="dialog" aria-modal="true">${html}</div></div>`;const f=r.querySelector('input,button');if(f)f.focus()}
export function closeOv(){ui.bookId=null;$('#ovRoot').innerHTML=''}
export function listPicker(ids,title,sub){
  const rows=S.lists.map(l=>{
    const all=ids.every(id=>l.books.includes(id));
    return `<button class="mrow ${all?'on':''}" data-act="${ids.length>1?'bulk':'toggle'}" data-v="${l.id}"><span class="ck">${all?'✓':''}</span><span style="flex:1">${esc(l.name)}</span><small style="color:var(--muted)">${l.books.length}</small></button>`}).join('');
  openOv(`<h3>${esc(title)}</h3><p>${esc(sub)}</p>${rows||'<p>You have no lists yet — create one:</p>'}
    <div class="newl"><input type="text" id="ovNew" placeholder="New list name…" maxlength="60" aria-label="New list name"><button class="btn sm" data-act="ovnew">Create &amp; add</button></div>
    <div style="margin-top:14px;text-align:right"><button class="btn sm ghost" data-act="ovclose2">Done</button></div>`);
  $('#ovNew').addEventListener('keydown',e=>{if(e.key==='Enter')$('[data-act=ovnew]').click()});
}
export function bookOv(id){
  const b=BYID.get(id);if(!b)return;
  ui.bookId=id;
  openOv(`<div class="bookpv" style="--x:0"><div class="grid" style="grid-template-columns:1fr">${card(b)}</div><div style="margin-top:12px;display:flex;justify-content:flex-end"><button class="btn sm ghost" data-act="ovclose2">Close</button></div></div>`);
  const f=$('#ovRoot .modal button');if(f)f.blur();
}
export function refreshBookOv(){
  if(!ui.bookId||!$('#ovRoot .bookpv'))return;
  const b=BYID.get(ui.bookId);if(!b)return;
  $('#ovRoot .bookpv .grid').innerHTML=card(b);
}
export function reviewOv(id){
  const b=BYID.get(id);if(!b)return;
  const m=S.meta[id]||{};
  openOv(`<div data-id="${esc(id)}"><h3>${esc(b.title)}</h3><p>${esc(b.author)}</p>
    <div style="margin:6px 0 12px">${stars(id,true)}</div>
    <label class="f">My notes<textarea id="noteTxt" maxlength="2000" rows="6" placeholder="Thoughts, favourite quotes, who recommended it…" style="width:100%;background:var(--field);color:var(--text);border:1px solid var(--line);border-radius:10px;padding:10px;font:inherit">${esc(m.n||'')}</textarea></label>
    <div style="margin-top:14px;display:flex;gap:8px;justify-content:flex-end"><button class="btn sm" data-act="notesave">Save</button></div></div>`);
  const t=$('#noteTxt');if(t)t.focus();
}
