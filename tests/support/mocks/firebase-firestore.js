/* Test double for firebase-firestore.js. The "cloud" lives in localStorage key `fake-fs` as {"users/<uid>": {...document...}}.
   Tests can pre-seed it to simulate data from another device, and read it back to assert what the app saved.
   Hooks: window.__fakeFs.failNextWrite = 'permission-denied' | 'unavailable' | 'internal'  (next setDoc rejects with that code)
          window.__fakeFs.failNextRead  = same (next getDoc rejects)
          window.__fakeFs.writes counts setDoc calls (including failed ones).
          window.__fakeFs.push(path, obj)  simulates a change made on another device (fires the snapshot listener) */
const K='fake-fs';const all=()=>{try{return JSON.parse(localStorage.getItem(K)||'{}')}catch(e){return {}}};
const hooks=window.__fakeFs=window.__fakeFs||{failNextWrite:null,failNextRead:null,listeners:{}};
export function getFirestore(){return {}}
export function initializeFirestore(){return {}}
export function persistentLocalCache(){return {}}
export function persistentMultipleTabManager(){return {}}
export function doc(db,...p){return {path:p.join('/')}}
const snap=d=>{const v=all()[d.path];return {exists:()=>!!v,data:()=>v,metadata:{hasPendingWrites:false}}};
const err=c=>{const e=new Error(c);e.code=c;return e};
export async function getDoc(d){const f=hooks.failNextRead;if(f){hooks.failNextRead=null;throw err(f)}return snap(d)}
export async function setDoc(d,o){hooks.writes=(hooks.writes||0)+1;const f=hooks.failNextWrite;if(f){hooks.failNextWrite=null;throw err(f)}
  const a=all();a[d.path]=JSON.parse(JSON.stringify(o));localStorage.setItem(K,JSON.stringify(a))}
export function onSnapshot(d,cb){hooks.listeners[d.path]=cb;setTimeout(()=>cb(snap(d)),0);return()=>{delete hooks.listeners[d.path]}}
hooks.push=(path,obj)=>{const a=all();a[path]=obj;localStorage.setItem(K,JSON.stringify(a));const l=hooks.listeners[path];if(l)l(snap({path}))};
