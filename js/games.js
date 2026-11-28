/* Book games: registry, beta switch, best scores, and opening or closing the game screen.
   Kept small because it is precached; the shell, engine and games live in js/games/ and js/vendor/ and load on Play. */
import {esc,toast} from './util.js';

/* status 'beta': shown only with "Show games (beta)" on (About page). 'released': shown to everyone. */
export const GAMES=[
  {bookId:'dune--frank-herbert',slug:'dune',title:'Spice Run',genre:'Top-down survival',
   blurb:'Gather spice on the open sand. Running is fast but loud, and noise draws the worm.',status:'beta'}
];
const BETA='nova-games-beta',BEST='nova-games-best';
export function betaOn(){try{return localStorage.getItem(BETA)==='1'}catch(e){return false}}
export function setBeta(on){try{on?localStorage.setItem(BETA,'1'):localStorage.removeItem(BETA)}catch(e){}}
export const gameFor=id=>GAMES.find(g=>g.bookId===id&&(g.status==='released'||betaOn()))||null;
function bests(){try{const o=JSON.parse(localStorage.getItem(BEST)||'{}');return o&&typeof o==='object'?o:{}}catch(e){return {}}}
export const best=slug=>Math.max(0,Math.floor(+bests()[slug]||0));
function saveBest(slug,n){if(n<=best(slug))return false;const o=bests();o[slug]=n;try{localStorage.setItem(BEST,JSON.stringify(o))}catch(e){}return true}

const playHref=id=>'#play/'+encodeURIComponent(id);
/* Panel on the book page; empty when the book has no (visible) game. */
export function gamePanel(id){
  const g=gameFor(id);if(!g)return '';
  const b=best(g.slug);
  return `<section class="panel bgame" id="bookGame"><h3>Game</h3>
    <div class="gname"><b>${esc(g.title)}</b> <span class="by">${esc(g.genre)}${g.status==='beta'?' · beta':''}</span></div>
    <p>${esc(g.blurb)}</p>
    <div class="acts"><a class="btn sm" id="playBtn" href="${esc(playHref(id))}">Play</a>${b?`<span class="by" id="bookBest">Best: ${b}</span>`:''}</div></section>`;
}

/* The router calls syncGame(bookId) for #play/<id> and syncGame(null) for every other page. */
let cur=null,fromBook=false;
document.addEventListener('click',e=>{if(e.target.closest&&e.target.closest('#playBtn'))fromBook=true},true);
export function syncGame(id){
  const g=id?gameFor(id):null;
  if(!g){if(cur)closeNow();return}
  if(cur&&cur.id===id)return;
  if(cur)closeNow();
  openNow(g,id);
}
async function openNow(g,id){
  const me={g,id,h:null};cur=me;
  try{
    const shell=await import('./games/shell.js');
    if(cur!==me)return;
    const h=await shell.open(g,{best:best(g.slug),saveBest:n=>saveBest(g.slug,n),back:()=>back(id)});
    if(cur!==me){h.close();return}
    me.h=h;
  }catch(err){
    if(cur!==me)return;
    cur=null;fromBook=false;
    toast('Could not load the game. Check your connection and try again.');
    location.replace('#book/'+encodeURIComponent(id));
  }
}
function closeNow(){const c=cur;cur=null;fromBook=false;if(c&&c.h)c.h.close()}
function back(id){if(fromBook){fromBook=false;history.back()}else location.replace('#book/'+encodeURIComponent(id))}
