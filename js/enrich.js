/* Optional extra info for the book page from Open Library (cover, description, first published, subjects).
   Fetched only when a book page is opened, cached in this browser, and can be switched off on the About page. */
import {norm,surname} from './util.js';
const KEY='nova-ol-v1',OFF='nova-ol-off',HIT_MS=30*864e5,MISS_MS=864e5,API='https://openlibrary.org';
export const enrichOn=()=>{try{return localStorage.getItem(OFF)!=='1'}catch(e){return true}};
export function setEnrich(on){try{on?localStorage.removeItem(OFF):localStorage.setItem(OFF,'1')}catch(e){}}
const load=()=>{try{return JSON.parse(localStorage.getItem(KEY)||'{}')}catch(e){return {}}};
const save=m=>{try{
  const ks=Object.keys(m);if(ks.length>400){ks.sort((a,b)=>m[a].t-m[b].t).slice(0,ks.length-300).forEach(k=>delete m[k])}
  localStorage.setItem(KEY,JSON.stringify(m))}catch(e){}};
/* Cached info for a book: object, null (known miss) or undefined (not fetched / expired). */
export function cached(id){
  const e=load()[id];if(!e)return undefined;
  if(Date.now()-e.t>(e.d?HIT_MS:MISS_MS))return undefined;
  return e.d||null;
}
async function getJSON(url){
  const ac=new AbortController(),t=setTimeout(()=>ac.abort(),8000);
  try{const r=await fetch(url,{signal:ac.signal});if(!r.ok)throw new Error(r.status);return await r.json()}
  finally{clearTimeout(t)}
}
function clean(d){
  let s=typeof d==='string'?d:(d&&d.value)||'';
  s=s.replace(/\r/g,'').split(/\n-{3,}|\n\s*\[?Source|\n\s*Contains:/i)[0];            // drop source footers and contents lists
  s=s.split('\n').filter(l=>!/^\s*\[\d+\]:/.test(l)).join('\n');
  s=s.replace(/\[([^\]]+)\]\([^)]*\)/g,'$1').replace(/\(\[source\][^)]*\)/ig,'').replace(/[*_`#>]/g,'').replace(/\n{2,}/g,'\n').trim();
  if(s.length>900){s=s.slice(0,900);s=s.slice(0,Math.max(s.lastIndexOf('. ')+1,600))+(s.length>=900&&!s.endsWith('.')?'…':'')}
  return s;
}
function pick(docs,b){
  const nt=norm(b.title),sn=surname(b.author);
  const au=d=>(d.author_name||[]).some(a=>norm(a).split(' ').pop()===norm(sn).split(' ').pop());
  return docs.find(d=>norm(d.title||'')===nt&&au(d))||docs.find(d=>au(d)&&(norm(d.title||'').includes(nt)||nt.includes(norm(d.title||''))))||null;
}
/* Fetch (and cache) info for one book. Resolves to an object, or null when nothing was found. Rejects on network errors. */
export async function fetchInfo(b){
  const c=cached(b.id);if(c!==undefined)return c;
  const q=`${API}/search.json?title=${encodeURIComponent(b.title)}&author=${encodeURIComponent(b.author.replace(/\s*&.*$/,''))}&limit=8&fields=key,title,author_name,cover_i,first_publish_year,subject`;
  const res=await getJSON(q);
  const hit=pick(res.docs||[],b);
  let d=null;
  if(hit){
    d={key:hit.key,cover:hit.cover_i||0,year:hit.first_publish_year||0,subjects:(hit.subject||[]).filter(x=>x.length<32).slice(0,6),desc:''};
    try{const w=await getJSON(API+hit.key+'.json');d.desc=clean(w.description)}catch(e){}
    if(!d.cover&&!d.desc&&!d.year&&!d.subjects.length)d=null;
  }
  const m=load();m[b.id]={t:Date.now(),d};save(m);
  return d;
}
export const coverUrl=n=>`https://covers.openlibrary.org/b/id/${n}-M.jpg`;
export const workUrl=k=>API+k;
/* Free-text search for the "Add a book" form. Resolves to [{title,author,year}]. Rejects on network errors. */
export async function searchBooks(q){
  const r=await getJSON(`${API}/search.json?q=${encodeURIComponent(q)}&limit=6&fields=key,title,author_name,first_publish_year`);
  return (r.docs||[]).filter(d=>d.title&&d.author_name&&d.author_name.length).map(d=>({title:d.title,author:d.author_name[0],year:d.first_publish_year||0}));
}
