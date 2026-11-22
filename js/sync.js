/* Persistence: local storage copy plus Firebase (Google sign-in + Firestore) sync. */
import {FB_VER,LS} from './config.js';
import {$,toast} from './util.js';
import {S,loadFrom,serialize} from './state.js';
import {renderAll} from './views.js';
export let ref=null,saving=false,dirty=false,timer=null,syncMode='loading',fb=null,unsub=null;
export function setSync(mode){
  syncMode=mode;const el=$('#sync');const was=el.classList.contains('show');el.className='chip s-'+((mode==='signin'||mode==='offline')?'local':mode)+(was?' show':'');
  $('#syncTxt').textContent={synced:'Cloud synced',saving:'Saving…',local:'Saved in this browser only',signin:'Sign in to sync',error:'Sync problem – kept in this browser',denied:'Access denied for this account',loading:'Connecting…',offline:'Offline – will sync when connected'}[mode];
  if(mode==='denied')el.className='chip s-error'+(was?' show':'');
  el.setAttribute('aria-label',$('#syncTxt').textContent);el.title=$('#syncTxt').textContent;
}
export function touch(){
  S.updatedAt=Date.now();
  try{localStorage.setItem(LS,JSON.stringify(serialize()))}catch(e){}
  if(!ref){setSync(fb?(fb.auth.currentUser?'offline':'signin'):'local');return}
  dirty=true;setSync('saving');clearTimeout(timer);timer=setTimeout(flush,700);
}
export async function flush(){
  if(saving||!ref||!dirty)return;
  if(!navigator.onLine){setSync('offline');return}
  saving=true;dirty=false;
  try{await ref.set(serialize());if(!dirty)setSync('synced')}catch(e){setSync(e&&e.code==='permission-denied'?'denied':'error')}
  saving=false;
  if(dirty){clearTimeout(timer);timer=setTimeout(flush,300)}
}
export function fbConfigured(){
  const c=window.NOVA_FIREBASE;
  return !!(c&&c.apiKey&&c.projectId&&!/^PASTE/i.test(c.apiKey)&&!/^PASTE/i.test(c.projectId));
}
export function showAuth(u){
  const b=$('#authBtn');if(!fb){b.hidden=true;return}
  b.hidden=false;const ic=u?'<path d="M9 4H5v16h4M16 8l4 4-4 4M20 12H9" />':'<path d="M15 4h4v16h-4M8 8l-4 4 4 4M4 12h11" />';
  b.innerHTML='<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'+ic+'</svg><span class="lbl">'+(u?'Sign out':'Sign in')+'</span>';
  b.setAttribute('aria-label',u?'Sign out':'Sign in with Google');
  b.title=u?('Signed in as '+(u.email||u.uid)):'Sign in to save your progress in the cloud';
}
export async function connect(){
  if(!fbConfigured()){setSync('local');return}
  try{
    const base='https://www.gstatic.com/firebasejs/'+FB_VER+'/';
    const [A,Au,F]=await Promise.all([import(base+'firebase-app.js'),import(base+'firebase-auth.js'),import(base+'firebase-firestore.js')]);
    const app=A.initializeApp(window.NOVA_FIREBASE);
    let db;
    try{db=F.initializeFirestore(app,{localCache:F.persistentLocalCache({tabManager:F.persistentMultipleTabManager()})})}
    catch(e){db=F.getFirestore(app)}
    fb={Au,F,auth:Au.getAuth(app),db};
    showAuth(null);setSync('signin');
    Au.onAuthStateChanged(fb.auth,onUser);
  }catch(e){fb=null;showAuth(null);setSync('error')}
}
export async function onUser(u){
  if(unsub){unsub();unsub=null}
  ref=null;showAuth(u);
  if(!u){setSync('signin');return}
  setSync('loading');
  try{
    const {F,db}=fb;const d=F.doc(db,'users',u.uid);
    const snap=await Promise.race([F.getDoc(d),new Promise((_,j)=>setTimeout(()=>j(new Error('timeout')),10000))]);
    ref={set:o=>F.setDoc(d,o)};
    if(snap.exists()){
      const x=snap.data();
      if((x.updatedAt||0)>=S.updatedAt){loadFrom(x);try{localStorage.setItem(LS,JSON.stringify(serialize()))}catch(e){}}
      else{dirty=true}
    }else if(S.read.size||S.lists.length||Object.keys(S.reading).length||Object.keys(S.meta).length||S.custom.length){dirty=true}
    setSync('synced');renderAll();
    if(dirty){setSync('saving');flush()}
    unsub=F.onSnapshot(d,s=>{
      if(s.metadata.hasPendingWrites||saving||dirty||!s.exists())return;
      const x=s.data();
      if((x.updatedAt||0)>S.updatedAt){loadFrom(x);renderAll()}
    },()=>{});
  }catch(e){ref=null;setSync(e&&e.code==='permission-denied'?'denied':(!navigator.onLine||(e&&(e.code==='unavailable'||e.message==='timeout')))?'offline':'error')}
}
export async function authClick(){
  if(!fb)return;
  try{
    if(fb.auth.currentUser){await fb.Au.signOut(fb.auth);return}
    const prov=new fb.Au.GoogleAuthProvider();
    try{await fb.Au.signInWithPopup(fb.auth,prov)}
    catch(e){if(e&&(e.code==='auth/popup-blocked'||e.code==='auth/operation-not-supported-in-this-environment'))await fb.Au.signInWithRedirect(fb.auth,prov);else if(!e||e.code!=='auth/popup-closed-by-user')toast('Sign-in failed'+(e&&e.code?' ('+e.code+')':''))}
  }catch(e){toast('Sign-in failed')}
}
export function initOnline(){
  window.addEventListener('online',()=>{if(ref&&dirty)flush();else if(fb&&!ref&&fb.auth.currentUser)onUser(fb.auth.currentUser)});
  window.addEventListener('offline',()=>{if(ref)setSync('offline')});
}
