/* Per-book page (#book/<id>): awards, your shelf (status, rating, dates, notes), author and same-year books. */
import {AW} from './config.js';
import {$,esc} from './util.js';
import {S,ui,setMeta} from './state.js';
import {BOOKS,BYID} from './data.js';
import {linkRow,stars,stateBtns} from './cards.js';
import {touch} from './sync.js';
import {cached,fetchInfo,enrichOn,coverUrl,workUrl} from './enrich.js';
const href=id=>'#book/'+encodeURIComponent(id);
const link=(b,extra='')=>`<a class="bl" href="${esc(href(b.id))}" data-act="gobook" data-v="${esc(b.id)}">${esc(b.title)}</a>${extra}`;
const mark=id=>S.read.has(id)?'<span class="mk ok" title="Read">✓</span>':S.reading[id]?'<span class="mk go" title="Reading now">▶</span>':'';
const day=ts=>new Date(ts).toLocaleDateString(undefined,{year:'numeric',month:'short',day:'numeric'});
const iso=ts=>{const d=new Date(ts);return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')};
function infoHTML(d){
  if(!d)return '';
  return `<div class="oinfo">${d.cover?`<img class="ocover" src="${esc(coverUrl(d.cover))}" alt="Cover of the book" loading="lazy" referrerpolicy="no-referrer" onerror="this.remove()">`:''}
    <div class="otext">${d.desc?`<p>${esc(d.desc).replace(/\n/g,'<br>')}</p>`:''}
    ${d.year?`<div class="bsum">First published ${d.year}</div>`:''}
    ${d.subjects.length?`<div class="bl2">${d.subjects.map(s=>`<span class="chip">${esc(s)}</span>`).join(' ')}</div>`:''}
    <div class="by">Source: <a class="lk" href="${esc(workUrl(d.key))}" target="_blank" rel="noopener noreferrer">Open Library</a></div></div></div>`;
}
function loadInfo(b){
  const box=$('#bookInfo');if(!box||!enrichOn())return;
  const c=cached(b.id);
  if(c!==undefined){box.innerHTML=infoHTML(c);box.hidden=!c;return}
  if(!navigator.onLine)return;
  box.hidden=false;box.innerHTML='<div class="by">Looking up cover and description…</div>';
  fetchInfo(b).then(d=>{if(ui.page===b.id&&$('#bookInfo')){const x=$('#bookInfo');x.innerHTML=infoHTML(d);x.hidden=!d}},
    ()=>{if(ui.page===b.id&&$('#bookInfo'))$('#bookInfo').hidden=true});
}
export function renderBookPage(){
  const ae=document.activeElement;if(ae&&ae.id==='pageNote')return;      // don't wipe notes being typed
  const id=ui.page,b=BYID.get(id),app=$('#app');
  if(!b){app.innerHTML=`<div class="panel empty"><h3>Book not found</h3><p>This book is not in the archive.</p><a class="btn" href="#library" data-act="back">Back to Library</a></div>`;return}
  const m=S.meta[id]||{};
  const rows=[...b.entries].sort((x,y)=>y.year-x.year||(y.result==='winner')-(x.result==='winner')).map(e=>{
    const a=AW[e.award]||{short:e.award,color:'#999'};
    return `<tr><td><span class="dotc" style="--c:${a.color}"></span>${esc(e.award)}</td><td>${e.year}</td><td class="${e.result==='winner'?'wn':'fn'}">${e.result==='winner'?'★ Winner':'Finalist'}</td></tr>`}).join('');
  const lists=S.lists.filter(l=>l.books.includes(id));
  const same=[...new Map(b.entries.map(e=>[e.award+'|'+e.year,e])).values()].sort((x,y)=>y.year-x.year).map(e=>{
    const others=BOOKS.filter(x=>x.id!==id&&x.entries.some(y=>y.award===e.award&&y.year===e.year))
      .sort((x,y)=>(y.entries.some(z=>z.award===e.award&&z.year===e.year&&z.result==='winner')-x.entries.some(z=>z.award===e.award&&z.year===e.year&&z.result==='winner'))||x.title.localeCompare(y.title));
    if(!others.length)return '';
    const a=AW[e.award]||{short:e.award};
    return `<div class="sy"><h4>${esc(a.short)} ${e.year}</h4><ul>${others.slice(0,12).map(o=>{const w=o.entries.some(z=>z.award===e.award&&z.year===e.year&&z.result==='winner');return `<li>${link(o,` <span class="by">${esc(o.author)}</span>`)}${w?' <span class="wn">★</span>':''} ${mark(o.id)}</li>`}).join('')}</ul></div>`}).join('');
  const mine=BOOKS.filter(x=>x.author===b.author&&x.id!==id).sort((x,y)=>x.first-y.first||x.title.localeCompare(y.title));
  const status=S.reading[id]?`Reading since ${day(S.reading[id])} (day ${Math.floor((Date.now()-S.reading[id])/864e5)+1})`:S.read.has(id)?'Read':'Not read yet';
  app.innerHTML=`<div class="bpage" data-id="${esc(id)}">
    <a class="btn sm ghost" data-act="back" href="#library">← Back</a>
    <section class="panel bhead">
      <h2>${esc(b.title)}</h2>
      <button class="author" data-act="author" data-v="${esc(b.author)}" title="Show all books by this author">${esc(b.author)}</button>
      <div class="bsum">${b.wins} win${b.wins===1?'':'s'} · ${b.noms} nomination${b.noms===1?'':'s'} · ${b.first===b.last?b.first:b.first+'–'+b.last}</div>
      ${linkRow(b)}
      <div id="bookInfo" hidden></div>
      <div class="acts">${stateBtns(id)}<button class="btn sm ghost" data-act="addlist">＋ List${lists.length?' ('+lists.length+')':''}</button></div>
    </section>
    <div class="bcols">
      <section class="panel"><h3>My shelf</h3>
        <div class="bst">${esc(status)}</div>
        ${S.read.has(id)?`<div class="brow">${stars(id,true)}</div><label class="f">Finished on<input type="date" id="pageFin" value="${m.f?iso(m.f):''}" max="${iso(Date.now())}"></label>`:''}
        <label class="f">My notes<textarea id="pageNote" maxlength="2000" rows="5" placeholder="Thoughts, favourite quotes, who recommended it…">${esc(m.n||'')}</textarea></label>
        ${lists.length?`<div class="bl2">On lists: ${lists.map(l=>`<button class="chip" data-act="gotolist" data-v="${esc(l.id)}">${esc(l.name)}</button>`).join(' ')}</div>`:''}
      </section>
      <section class="panel"><h3>Awards</h3>
        <table class="aw"><thead><tr><th>Award</th><th>Year</th><th></th></tr></thead><tbody>${rows}</tbody></table>
      </section>
    </div>
    ${mine.length?`<section class="panel"><h3>More by ${esc(b.author)}</h3><ul class="blist">${mine.map(o=>`<li>${link(o,` <span class="by">${o.first===o.last?o.first:o.first+'–'+o.last}</span>`)}${o.wins?` <span class="wn">${'★'.repeat(Math.min(o.wins,5))}</span>`:''} ${mark(o.id)}</li>`).join('')}</ul></section>`:''}
    ${same?`<section class="panel"><h3>Same awards, same year</h3><div class="sygrid">${same}</div></section>`:''}
  </div>`;
  loadInfo(b);
  const nt=$('#pageNote');
  if(nt)nt.addEventListener('change',()=>{setMeta(id,'n',nt.value.trim());touch()});
  const fin=$('#pageFin');
  if(fin)fin.addEventListener('change',()=>{setMeta(id,'f',fin.value?new Date(fin.value+'T12:00:00').getTime():0);touch()});
}
