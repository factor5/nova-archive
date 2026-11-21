/* Page views: library, lists, about, now-reading row. */
import {enrichOn,setEnrich} from './enrich.js';
import {renderBookPage} from './bookpage.js';
import {AWARDS,PAGE} from './config.js';
import {$,esc,surname} from './util.js';
import {S,hasNote,rating,ui} from './state.js';
import {touch} from './sync.js';
import {BOOKS,BYID,groups,visible} from './data.js';
import {badge,card,linkRow,stars,stateBtns} from './cards.js';
import {refreshBookOv} from './overlay.js';
export function decades(){const s=new Set();BOOKS.forEach(b=>b.entries.forEach(e=>s.add(Math.floor(e.year/10)*10)));return [...s].sort((a,b)=>b-a)}
export function shellLibrary(){
  const app=$('#app');
  app.innerHTML=`
  <section class="panel filters" aria-label="Filters">
    <div class="row">
      <label class="f">Search<input type="text" id="q" placeholder="Title or author…" value="${esc(ui.q)}"></label>
      <label class="f">Show<select id="result"><option value="all">Winners &amp; finalists</option><option value="winner">Winners only</option></select></label>
      <label class="f">Status<select id="read"><option value="all">All books</option><option value="unread">Not read yet</option><option value="reading">Reading now</option><option value="read">Already read</option><option value="rated">Rated by me</option></select></label>
      <label class="f">Decade<select id="decade"><option value="">All years</option>${decades().map(d=>`<option value="${d}">${d}s</option>`).join('')}</select></label>
      <label class="f">Group by<select id="group"><option value="none">No grouping</option><option value="year">Year</option><option value="decade">Decade</option><option value="award">Award</option><option value="author">Author</option></select></label>
      <label class="f">Sort<select id="sort"><option value="best">Most honoured</option><option value="newest">Newest first</option><option value="oldest">Oldest first</option><option value="title">Title A–Z</option><option value="author">Author A–Z</option><option value="wins">Most wins</option><option value="rating">My rating</option></select></label>
    </div>
    <div><div class="f" style="margin-bottom:6px;font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)">Award <span style="text-transform:none;letter-spacing:0">(none selected = all)</span></div>
      <div class="pills" id="awardPills">${AWARDS.map(a=>`<button class="pill" data-aw="${esc(a.key)}" style="--c:${a.color}" aria-pressed="false"><i></i>${esc(a.short)}</button>`).join('')}</div></div>
    <div class="row" id="authorRow"></div>
  </section>
  <div class="summary"><div id="count"></div><div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn sm" data-act="surprise">🎲 Surprise me</button><button class="btn sm" data-act="addall">＋ Add all results to a list</button><button class="btn sm ghost" data-act="reset">Reset filters</button></div></div>
  <div id="results"></div>`;
  $('#result').value=ui.result;$('#read').value=ui.read;$('#decade').value=ui.decade;$('#group').value=ui.group;$('#sort').value=ui.sort;
  $('#q').addEventListener('input',e=>{ui.q=e.target.value;ui.limit=PAGE;renderResults()});
  for(const id of ['result','read','decade','group','sort'])$('#'+id).addEventListener('change',e=>{ui[id]=e.target.value;ui.limit=PAGE;renderResults()});
}
export function renderResults(){
  if(ui.tab!=='library')return;
  document.querySelectorAll('#awardPills .pill').forEach(p=>{const on=ui.awards.has(p.dataset.aw);p.classList.toggle('on',on);p.setAttribute('aria-pressed',on)});
  $('#authorRow').innerHTML=ui.author?`<span class="chip">Author: <b>${esc(ui.author)}</b></span><button class="btn sm" data-act="clearauthor">✕ Clear author</button>`:'';
  const vis=visible();const gs=groups(vis);
  $('#count').innerHTML=`<b>${vis.length}</b> book${vis.length===1?'':'s'} match`;
  if(!vis.length){$('#results').innerHTML=`<div class="panel empty"><h3>No signals found</h3><p>Nothing matches these filters. Try widening them or hit “Reset filters”.</p></div>`;return}
  let shown=0,html='',more=false;
  for(const g of gs){
    if(shown>=ui.limit){more=true;break}
    const take=g.books.slice(0,ui.limit-shown);
    if(take.length<g.books.length)more=true;
    shown+=take.length;
    if(g.label)html+=`<div class="group"><h2>${esc(g.label)}</h2><span>${g.books.length} book${g.books.length===1?'':'s'}</span></div>`;
    html+=`<div class="grid">${take.map(card).join('')}</div>`;
  }
  if(more)html+=`<div class="more"><button class="btn" data-act="more">Show more (${shown} of ${ui.group==='none'?vis.length:'many'})</button></div>`;
  $('#results').innerHTML=html;
}
export function renderLists(){
  const app=$('#app');
  if(!S.lists.length){ui.listId=null}
  else if(!S.lists.find(l=>l.id===ui.listId))ui.listId=S.lists[0].id;
  const cur=S.lists.find(l=>l.id===ui.listId);
  const side=`<aside class="panel lside" aria-label="Your lists">
    ${S.lists.map(l=>`<button class="litem ${l.id===ui.listId?'on':''}" data-act="pick" data-v="${l.id}"><span>${esc(l.name)}</span><small>${l.books.filter(id=>S.read.has(id)).length}/${l.books.length}</small></button>`).join('')||'<p style="margin:0;color:var(--muted);font-size:14px">No lists yet. Create your first reading list below.</p>'}
    <div class="newl"><input type="text" id="newListName" placeholder="New list name…" maxlength="60" aria-label="New list name"><button class="btn sm" data-act="newlist">Create</button></div>
  </aside>`;
  let main;
  if(!cur){main=`<section class="panel lmain empty"><h3>Mission board empty</h3><p>Create a list, then add books from the Library with the “＋ List” button.</p></section>`}
  else{
    let books=cur.books.map(id=>BYID.get(id)).filter(Boolean);
    const manual=ui.lsort==='manual';
    const yr=b=>Math.min(...b.entries.map(e=>e.year));
    if(!manual){const F={title:(a,b)=>a.title.localeCompare(b.title),author:(a,b)=>surname(a.author).localeCompare(surname(b.author))||a.title.localeCompare(b.title),oldest:(a,b)=>yr(a)-yr(b),newest:(a,b)=>yr(b)-yr(a),unread:(a,b)=>(S.read.has(a.id)-S.read.has(b.id))}[ui.lsort];books=books.slice().sort(F)}
    const done=books.filter(b=>S.read.has(b.id)).length;
    main=`<section class="panel lmain">
      <div class="lhead"><input type="text" id="listName" value="${esc(cur.name)}" maxlength="60" aria-label="List name">
        <div style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn sm" data-act="copylist">Copy as text</button><button class="btn sm warn" data-act="dellist">Delete list</button></div></div>
      <div style="display:flex;align-items:center;gap:12px;color:var(--muted);font-size:14px"><span><b style="color:var(--text)">${done}</b> of ${books.length} read</span><span class="bar" style="width:160px"><i style="width:${books.length?done/books.length*100:0}%"></i></span>
        <label style="margin-left:auto;display:flex;align-items:center;gap:6px">Sort <select id="lsort" aria-label="Sort list"><option value="manual">My order</option><option value="title">Title A–Z</option><option value="author">Author A–Z</option><option value="oldest">Oldest first</option><option value="newest">Newest first</option><option value="unread">Unread first</option></select></label></div>
      ${books.length?`<div class="items">${books.map((b,i)=>`<div class="item ${S.read.has(b.id)?'is-read':''}" data-id="${esc(b.id)}">
        <div class="n">${i+1}</div><div><div class="t"><a class="bl" href="#book/${esc(encodeURIComponent(b.id))}" data-act="gobook" data-v="${esc(b.id)}">${esc(b.title)}</a></div><div class="a">${esc(b.author)}</div><div class="badges" style="margin-top:4px">${b.entries.filter(e=>e.result==='winner').slice(0,4).map(badge).join('')}</div><div style="margin-top:6px">${linkRow(b)}</div></div>
        <div class="ib">${stateBtns(b.id)}${S.read.has(b.id)?stars(b.id)+`<button class="btn sm ghost" data-act="note">✎</button>`:''}
        ${manual?`<button class="btn sm ghost" data-act="up" aria-label="Move up">↑</button><button class="btn sm ghost" data-act="down" aria-label="Move down">↓</button>`:''}<button class="btn sm ghost warn" data-act="rm" aria-label="Remove from list">✕</button></div></div>`).join('')}</div>`
      :`<div class="empty"><h3>This list is empty</h3><p>Go to the Library and use “＋ List” on any book, or “Add all results to a list”.</p><a class="btn" href="#library">Open Library</a></div>`}
    </section>`;
  }
  app.innerHTML=`<div class="lists">${side}${main}</div>`;
  const ls=$('#lsort');if(ls){ls.value=ui.lsort;ls.addEventListener('change',()=>{ui.lsort=ls.value;renderLists()})}
  const ln=$('#listName');
  if(ln)ln.addEventListener('change',()=>{const v=ln.value.trim();if(v&&cur.name!==v){cur.name=v;touch();renderAll()}else ln.value=cur.name});
  const nl=$('#newListName');
  nl.addEventListener('keydown',e=>{if(e.key==='Enter')$('[data-act=newlist]').click()});
}
export function renderAbout(){
  const counts=AWARDS.map(a=>{const w=BOOKS.reduce((n,b)=>n+b.entries.filter(e=>e.award===a.key&&e.result==='winner').length,0);const t=BOOKS.reduce((n,b)=>n+b.entries.filter(e=>e.award===a.key).length,0);return `<li><b style="color:${a.color}">${esc(a.short)}</b> — ${esc(a.key)}: ${w} winners, ${t-w} finalists recorded</li>`}).join('');
  $('#app').innerHTML=`<section class="panel about">
    <h2>What’s in here</h2>
    <p>${BOOKS.length} distinct novels across seven science-fiction awards. Category covered: <b>Best Novel</b> only (the closest equivalent for each award).</p>
    <ul>${counts}</ul>
    <h2>Known gaps &amp; quirks</h2>
    <ul>
      <li><b>Locus</b>: winners for 1980–2026 only; the full finalist list is included for 2026 only. Locus awards before 1980 are not included.</li>
      <li><b>Campbell Memorial</b>: the award was cancelled in 2020 and 2021 and has not resumed, so data ends at 2019. It had no winner in 1976 and 1994 (finalists only).</li>
      <li><b>Years</b> follow the source lists: Hugo, Clarke, Campbell, Locus and Philip K. Dick use the year of the ceremony; Nebula and (recently) BSFA list the eligibility year, so the ceremony is usually the following year.</li>
      <li><b>Philip K. Dick</b> is for original paperbacks and sometimes honours collections or anthologies, which are listed as given. Special citations are omitted.</li>
      <li>Some early years have no finalists on record (Hugo 1953, 1955, 1958; several BSFA years). Ties and joint winners are each marked as winners.</li>
      <li>Data was compiled from Wikipedia award lists and the Science Fiction Awards Database (sfadb.com) in November 2026. It was transcribed automatically, so a few errors are possible — please sanity-check anything important.</li>
    </ul>
    <h2>Install on your phone</h2>
    <p>In Chrome on Android, open the menu (⋮) and choose <b>Install app</b> or <b>Add to Home screen</b>. It then opens full screen like a normal app and starts even without a connection.</p>
    <h2>Your data</h2>
    <p>“Read” marks and reading lists are saved in your own Firebase project (Cloud Firestore) once you sign in with Google, and sync across your devices. Only the account allowed by your Firestore security rules can read or write them. Without signing in, they are kept in this browser only (the indicator at the top shows which).</p>
    <h2>Covers and descriptions</h2>
    <p>Book pages can look up a cover, description and subjects on <a class="lk" href="https://openlibrary.org" target="_blank" rel="noopener noreferrer">Open Library</a>. This happens only when you open a book page, and sends just the title and author to Open Library. Results are cached in this browser.</p>
    <label style="display:flex;gap:8px;align-items:center"><input type="checkbox" id="olToggle"${enrichOn()?' checked':''}> Look up covers and descriptions</label>
    <p style="color:var(--muted);font-size:13px">App version ${esc((document.querySelector('meta[name=app-version]')||{}).content||'?')}</p>
  </section>`;
  const ol=$('#olToggle');if(ol)ol.addEventListener('change',()=>setEnrich(ol.checked));
}
export function renderNow(){
  const el=$('#nowReading');const ids=Object.keys(S.reading).filter(id=>BYID.has(id)).sort((a,b)=>S.reading[a]-S.reading[b]);
  if(!ids.length){el.hidden=true;el.innerHTML='';return}
  el.hidden=false;
  el.innerHTML=`<div class="nowhead"><span class="pulse"></span>Now reading <small>${ids.length}${ids.length>1?' · swipe →':''}</small></div><div class="nowrow">${ids.map(id=>{
    const b=BYID.get(id);const d=Math.max(0,Math.floor((Date.now()-S.reading[id])/864e5));
    return `<div class="ncard" data-id="${esc(id)}" data-act="openbook" role="button" tabindex="0" aria-label="Open ${esc(b.title)}"><div class="ntx"><div class="nt">${esc(b.title)}</div><div class="na">${esc(b.author)} · <span class="nd">Day ${d+1}</span></div></div><span class="chev" aria-hidden="true">${hasNote(id)?'✎ ':''}›</span></div>`}).join('')}</div>`;
}
export function renderAll(){
  renderNow();refreshBookOv();
  $('#hudRead').textContent=S.read.size;$('#hudTotal').textContent=BOOKS.length;
  $('#hudBar').style.width=(BOOKS.length?S.read.size/BOOKS.length*100:0)+'%';
  $('#listCount').textContent=S.lists.length?'('+S.lists.length+')':'';
  document.querySelectorAll('nav.tabs a').forEach(a=>a.classList.toggle('on',a.dataset.tab===ui.tab));
  if(ui.tab==='library'){if(!$('#results'))shellLibrary();renderResults()}
  else if(ui.tab==='lists')renderLists();
  else if(ui.tab==='book')renderBookPage();
  else renderAbout();
}
export function route(){
  const h=(location.hash||'#library').slice(1);
  const bm=h.match(/^book\/(.+)$/);
  const t=bm?'book':(['library','lists','about'].includes(h)?h:'library');
  const page=bm?decodeURIComponent(bm[1]):null;
  if(t!==ui.tab||page!==ui.page||!$('#app').children.length){ui.tab=t;ui.page=page;$('#app').innerHTML='';if(t==='book')window.scrollTo(0,0)}
  renderAll();
}
