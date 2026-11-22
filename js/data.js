/* Award data and filtering, grouping and sorting. */
import {AW,AWARDS} from './config.js';
import {norm,surname,sortKey} from './util.js';
import {S,rating,ui} from './state.js';
export let BOOKS=[],BYID=new Map();
/* ---------- data prep ---------- */
let BASE=[];
export const baseCount=()=>BASE.length;
/* Rebuild the full book list: award data plus the books you added (S.custom). */
export function rebuild(){
  const mine=S.custom.map(c=>({id:c.id,title:c.title,author:c.author,entries:[],custom:true,year:c.year||0,added:c.added||0,wins:0,noms:0,first:c.year||0,last:c.year||0,_n:norm(c.title+' '+c.author),_s:surname(c.author)}));
  BOOKS=BASE.concat(mine);BYID=new Map(BOOKS.map(b=>[b.id,b]));
}
export function prep(list){
  BASE=list;
  for(const b of BASE){
    b._n=norm(b.title+' '+b.author);
    b.wins=b.entries.filter(e=>e.result==='winner').length;
    b.noms=b.entries.length;
    b.first=Math.min(...b.entries.map(e=>e.year));
    b.last=Math.max(...b.entries.map(e=>e.year));
    b.entries.sort((x,y)=>(y.result==='winner')-(x.result==='winner')||x.year-y.year);
    b._s=surname(b.author);b._k=sortKey(b.author);
  }
  rebuild();
}

/* ---------- filtering ---------- */
export function matchEntry(e){
  if(ui.awards.size&&!ui.awards.has(e.award))return false;
  if(ui.result==='winner'&&e.result!=='winner')return false;
  if(ui.decade){const d=+ui.decade;if(e.year<d||e.year>d+9)return false}
  return true;
}
/* Books you added have no awards, so award and winner filters hide them; the decade filter uses their year. */
function matchBook(b){
  if(!b.custom)return b.entries.some(matchEntry);
  if(ui.awards.size||ui.result==='winner')return false;
  if(ui.decade){const d=+ui.decade;if(!b.year||b.year<d||b.year>d+9)return false}
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
    if(ui.source==='awards'&&b.custom)return false;
    if(ui.source==='mine'&&!b.custom)return false;
    return matchBook(b);
  });
}
export function sortBooks(arr){
  const f={
    best:(a,b)=>(b.wins*3+b.noms)-(a.wins*3+a.noms)||b.last-a.last,
    newest:(a,b)=>b.last-a.last||a.title.localeCompare(b.title),
    oldest:(a,b)=>a.first-b.first||a.title.localeCompare(b.title),
    title:(a,b)=>a.title.localeCompare(b.title),
    author:(a,b)=>a._k.localeCompare(b._k)||a.title.localeCompare(b.title),
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
    if(b.custom){add(ui.group==='year'?(b.year?String(b.year):'No year'):ui.group==='decade'?(b.year?Math.floor(b.year/10)*10+'s':'No year'):'My books',b);continue}
    for(const e of b.entries){
      if(!matchEntry(e))continue;
      if(ui.group==='year')add(String(e.year),b);
      else if(ui.group==='decade')add(Math.floor(e.year/10)*10+'s',b);
      else if(ui.group==='award')add(e.award,b);
    }
  }
  let keys=[...m.keys()];
  if(ui.group==='year'||ui.group==='decade')keys.sort((a,b)=>(isNaN(parseInt(a))-isNaN(parseInt(b)))||parseInt(b)-parseInt(a));
  else if(ui.group==='award'){const ix=k=>{const i=AWARDS.findIndex(x=>x.key===k);return i<0?99:i};keys.sort((a,b)=>ix(a)-ix(b))}
  else keys.sort((a,b)=>sortKey(a).localeCompare(sortKey(b)));
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
