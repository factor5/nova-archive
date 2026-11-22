/* HTML builders for book cards and their buttons. */
import {AW} from './config.js';
import {$,esc} from './util.js';
import {S,hasNote,rating} from './state.js';
export function badge(e){
  const a=AW[e.award]||{short:e.award,color:'#999'};
  return `<span class="b ${e.result==='winner'?'w':'dim'}" style="--c:${a.color}" title="${esc(e.award)} ${e.year} — ${e.result}">${e.result==='winner'?'★ ':''}${esc(a.short)} ${e.year}</span>`;
}
export function wiki(q){return 'https://en.wikipedia.org/wiki/Special:Search?go=Go&search='+encodeURIComponent(q)}
export function linkRow(b){
  const L=(href,txt,tip)=>`<a class="lk" href="${esc(href)}" target="_blank" rel="noopener noreferrer" title="${esc(tip)} (opens in a new tab)">${txt}<span aria-hidden="true"> ↗</span></a>`;
  return `<div class="links" aria-label="Learn more">
    <div class="lr"><span class="lkh">Book</span>${L(wiki(b.title+' '+b.author+' novel'),'Wikipedia','Search Wikipedia for this book')}${L('https://www.goodreads.com/search?q='+encodeURIComponent(b.title+' '+b.author),'Goodreads','Search Goodreads for this book')}</div>
    <div class="lr"><span class="lkh">Author</span>${L(wiki(b.author+' author'),'Wikipedia','Search Wikipedia for this author')}${L('https://www.isfdb.org/cgi-bin/se.cgi?type=Name&arg='+encodeURIComponent(b.author),'ISFDB','Search the Internet Speculative Fiction Database for this author')}</div>
  </div>`;
}
export function stars(id,big){
  const r=rating(id);
  return `<span class="rate ${big?'big':''}" role="group" aria-label="Your rating">${[1,2,3,4,5].map(n=>`<button type="button" class="st ${n<=r?'on':''}" data-act="star" data-v="${n}" aria-label="${n} star${n>1?'s':''}" aria-pressed="${n<=r}">★</button>`).join('')}</span>`;
}
export function stateBtns(id){
  const r=S.read.has(id),g=!!S.reading[id];
  if(g)return `<button class="btn sm go" data-act="finish">✓ Finish</button><button class="btn sm ghost" data-act="stop" title="Stop reading (not finished)">Stop</button>`;
  if(r)return `<button class="btn sm on" data-act="read" aria-pressed="true">✓ Read</button>`;
  return `<button class="btn sm" data-act="read" aria-pressed="false">Mark read</button><button class="btn sm ghost" data-act="start">▶ Start</button>`;
}
export function myBits(id){
  const r=S.read.has(id);
  if(S.reading[id])return `<div class="mine"><button class="btn sm ghost" data-act="note">✎ ${hasNote(id)?'Notes':'Add note'}</button></div>`;
  if(!r)return '';
  return `<div class="mine">${stars(id)}<button class="btn sm ghost" data-act="note">✎ ${hasNote(id)?'Notes':'Add note'}</button></div>`;
}
export function card(b){
  const r=S.read.has(b.id);
  const hasWin=b.wins>0;
  const inLists=S.lists.filter(l=>l.books.includes(b.id)).length;
  return `<article class="card ${hasWin?'win':''} ${r?'is-read':''} ${S.reading[b.id]?'is-reading':''}" data-id="${esc(b.id)}">
    <h3><a class="bl" href="#book/${esc(encodeURIComponent(b.id))}" data-act="gobook" data-v="${esc(b.id)}">${esc(b.title)}</a></h3>
    <button class="author" data-act="author" data-v="${esc(b.author)}" title="Show all books by this author">${esc(b.author)}</button>
    <div class="badges">${b.custom?`<span class="b mine">My book${b.year?' · '+b.year:''}</span>`:b.entries.map(badge).join('')}</div>
    ${linkRow(b)}
    ${myBits(b.id)}
    <div class="acts">
      ${stateBtns(b.id)}
      <button class="btn sm ghost" data-act="addlist">＋ List${inLists?' ('+inLists+')':''}</button>
    </div></article>`;
}
