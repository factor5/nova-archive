/* Add your own books (not in the award lists), edit and delete them. Stored in S.custom and synced like the rest. */
import {$,esc,norm,surname,toast} from './util.js';
import {S} from './state.js';
import {BYID,BOOKS,rebuild} from './data.js';
import {openOv,closeOv} from './overlay.js';
import {touch} from './sync.js';
import {enrichOn,searchBooks} from './enrich.js';
import {renderAll} from './views.js';
const slug=s=>norm(s).replace(/ /g,'-').slice(0,60);
let found=[],timer=null;
const thisYear=()=>new Date().getFullYear();
export function parseYear(v){v=String(v||'').trim();if(!v)return 0;const n=+v;return(/^\d{4}$/.test(v)&&n>=1000&&n<=thisYear()+1)?n:NaN}
export function findDuplicate(title,author,exceptId){
  const t=norm(title),s=surname(author);
  return BOOKS.find(b=>b.id!==exceptId&&norm(b.title)===t&&b._s===s)||null;
}
export function makeId(t,a){const base='my--'+slug(t)+'--'+slug(surname(a));let id=base,n=2;while(BYID.has(id))id=base+'-'+n++;return id}
export function openAddBook(){
  found=[];
  openOv(`<h3>Add a book</h3><p>Not in the award lists? Add it to your library.</p>
    ${enrichOn()?`<label class="f">Search Open Library<input type="text" id="abQ" placeholder="Title or author…" autocomplete="off"></label><div id="abRes" aria-live="polite"></div>`:''}
    <label class="f">Title<input type="text" id="abT" maxlength="120" autocomplete="off"></label>
    <label class="f">Author<input type="text" id="abA" maxlength="80" autocomplete="off"></label>
    <label class="f">First published (year, optional)<input type="text" id="abY" inputmode="numeric" maxlength="4" autocomplete="off"></label>
    <div class="abmsg" id="abMsg" role="status"></div>
    <div style="margin-top:12px;display:flex;gap:8px;justify-content:flex-end"><button class="btn sm ghost" data-act="ovclose2">Cancel</button><button class="btn sm" data-act="absave">Add book</button></div>`);
  const q=$('#abQ');
  if(q)q.addEventListener('input',()=>{
    clearTimeout(timer);const v=q.value.trim();
    if(v.length<3){$('#abRes').innerHTML='';return}
    timer=setTimeout(async()=>{
      try{found=await searchBooks(v)}catch(e){if($('#abRes'))$('#abRes').innerHTML='<small>Search unavailable. You can still type the details below.</small>';return}
      if(!$('#abRes')||q.value.trim()!==v)return;
      $('#abRes').innerHTML=found.length?found.map((r,i)=>`<button type="button" class="mrow" data-act="abpick" data-v="${i}"><span style="flex:1">${esc(r.title)} <small>${esc(r.author)}${r.year?' · '+r.year:''}</small></span></button>`).join(''):'<small>No matches. You can still type the details below.</small>';
    },450);
  });
  const t=$('#abT');if(t)t.focus();
}
export function pickResult(i){
  const r=found[+i];if(!r)return;
  $('#abT').value=r.title;$('#abA').value=r.author;$('#abY').value=r.year||'';
  $('#abRes').innerHTML='';const q=$('#abQ');if(q)q.value='';$('#abMsg').textContent='';
}
export function saveNew(){
  const t=$('#abT').value.trim(),a=$('#abA').value.trim(),y=parseYear($('#abY').value),m=$('#abMsg');
  if(!t||!a){m.textContent='Please enter a title and an author.';return}
  if(Number.isNaN(y)){m.textContent='Year should be four digits, for example 1984.';return}
  const d=findDuplicate(t,a);
  if(d){m.innerHTML=`Already in your library: <a class="lk" href="#book/${esc(encodeURIComponent(d.id))}" data-act="gobook" data-v="${esc(d.id)}">${esc(d.title)}</a>`;return}
  S.custom.push({id:makeId(t,a),title:t,author:a,year:y,added:Date.now()});
  rebuild();touch();closeOv();renderAll();toast('Added “'+t+'”');
}
/* Used by the book page. */
export function updateCustom(id,t,a,yRaw){
  const c=S.custom.find(x=>x.id===id);if(!c)return 'Book not found.';
  t=t.trim();a=a.trim();const y=parseYear(yRaw);
  if(!t||!a)return 'Please enter a title and an author.';
  if(Number.isNaN(y))return 'Year should be four digits, for example 1984.';
  const d=findDuplicate(t,a,id);if(d)return 'Another book with this title and author already exists.';
  c.title=t;c.author=a;c.year=y;rebuild();touch();renderAll();toast('Saved');return '';
}
export function deleteCustom(id){
  S.custom=S.custom.filter(c=>c.id!==id);
  S.read.delete(id);delete S.reading[id];delete S.meta[id];
  for(const l of S.lists)l.books=l.books.filter(x=>x!==id);
  rebuild();touch();
}
