/* Award data and filtering, grouping and sorting. */
import {AW,AWARDS} from './config.js';
import {norm,surname} from './util.js';
import {S,rating,ui} from './state.js';
export let BOOKS=[],BYID=new Map();
/* ---------- data prep ---------- */
export function prep(list){
  BOOKS=list;BYID=new Map();
  for(const b of BOOKS){
    BYID.set(b.id,b);
    b._n=norm(b.title+' '+b.author);
    b.wins=b.entries.filter(e=>e.result==='winner').length;
    b.noms=b.entries.length;
    b.first=Math.min(...b.entries.map(e=>e.year));
    b.last=Math.max(...b.entries.map(e=>e.year));
    b.entries.sort((x,y)=>(y.result==='winner')-(x.result==='winner')||x.year-y.year);
    b._s=surname(b.author);
  }
}

/* ---------- filtering ---------- */
export function matchEntry(e){
  if(ui.awards.size&&!ui.awards.has(e.award))return false;
  if(ui.result==='winner'&&e.result!=='winner')return false;
  if(ui.decade){const d=+ui.decade;if(e.year<d||e.year>d+9)return false}
  return true;
}
export function visible(){
  const q=norm(ui.q);const au=ui.author;
  return BOOKS.filter(b=>{
    if(au&&b.author!==au)return false;
    if(q&&!b._n.includes(q))return false;
    const r=S.read.has(b.id);
    if(ui.read==='read'&&!r)return false;
    if(ui.read==='unread'&&r)return false;
    if(ui.read==='reading'&&!S.reading[b.id])return false;
    if(ui.read==='rated'&&!rating(b.id))return false;
    return b.entries.some(matchEntry);
  });
}
export function sortBooks(arr){
  const f={
    best:(a,b)=>(b.wins*3+b.noms)-(a.wins*3+a.noms)||b.last-a.last,
    newest:(a,b)=>b.last-a.last||a.title.localeCompare(b.title),
    oldest:(a,b)=>a.first-b.first||a.title.localeCompare(b.title),
    title:(a,b)=>a.title.localeCompare(b.title),
    author:(a,b)=>a._s.localeCompare(b._s)||a.title.localeCompare(b.title),
    wins:(a,b)=>b.wins-a.wins||b.noms-a.noms,
    rating:(a,b)=>rating(b.id)-rating(a.id)||(b.wins*3+b.noms)-(a.wins*3+a.noms)
  }[ui.sort];
  return arr.slice().sort(f);
}
export function groups(arr){
  if(ui.group==='none')return [{label:'',books:sortBooks(arr)}];
  const m=new Map();
  const add=(k,b)=>{if(!m.has(k))m.set(k,[]);const a=m.get(k);if(!a.includes(b))a.push(b)};
  for(const b of arr){
    if(ui.group==='author'){add(b.author,b);continue}
    for(const e of b.entries){
      if(!matchEntry(e))continue;
      if(ui.group==='year')add(String(e.year),b);
      else if(ui.group==='decade')add(Math.floor(e.year/10)*10+'s',b);
      else if(ui.group==='award')add(e.award,b);
    }
  }
  let keys=[...m.keys()];
  if(ui.group==='year'||ui.group==='decade')keys.sort((a,b)=>parseInt(b)-parseInt(a));
  else if(ui.group==='award')keys.sort((a,b)=>AWARDS.findIndex(x=>x.key===a)-AWARDS.findIndex(x=>x.key===b));
  else keys.sort((a,b)=>surname(a).localeCompare(surname(b)));
  const rev=ui.sort==='oldest';
  return keys.map(k=>{
    let books=m.get(k);
    if(ui.group==='author')books=sortBooks(books);
    else books=books.slice().sort((a,b)=>{
      const wa=a.entries.some(e=>e.result==='winner'&&gk(e)===k),wb=b.entries.some(e=>e.result==='winner'&&gk(e)===k);
      return (wb-wa)||a.title.localeCompare(b.title)});
    return {label:ui.group==='award'?(AW[k]?AW[k].short+' — '+k:k):k,books};
  });
  function gk(e){return ui.group==='year'?String(e.year):ui.group==='decade'?Math.floor(e.year/10)*10+'s':e.award}
}
