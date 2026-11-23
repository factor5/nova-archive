/* One-time import of reading lists from a bundled file (import/reading-lists-2026-11.json).
   Archive books are referenced by id; unknown books become "My books" entries. Idempotent: running it again adds nothing. */
import {$,toast,uid} from './util.js';
import {S} from './state.js';
import {BYID,rebuild} from './data.js';
import {touch} from './sync.js';
import {findDuplicate,makeId} from './addbook.js';
import {renderAll} from './views.js';
const FILE='import/reading-lists-2026-11.json';
export async function runImport(){
  const say=t=>{const m=$('#importMsg');if(m)m.textContent=t};
  const btn=$('#importBtn');if(btn)btn.disabled=true;say('Importing…');
  try{
    const r=await fetch(FILE,{cache:'no-cache'});if(!r.ok)throw new Error(r.status);
    const data=await r.json();
    let addedBooks=0,newLists=0,addedToLists=0;
    for(const L of data.lists){
      const ids=[];
      for(const it of L.items){
        let id=it.id&&BYID.has(it.id)?it.id:null;
        if(!id){
          const d=findDuplicate(it.title,it.author||'');
          if(d)id=d.id;
          else{id=makeId(it.title,it.author);S.custom.push({id,title:it.title,author:it.author,year:0,added:Date.now()});rebuild();addedBooks++}
        }
        ids.push(id);
      }
      let l=S.lists.find(x=>x.name===L.name);
      if(!l){l={id:uid(),name:L.name,created:Date.now(),books:[]};S.lists.push(l);newLists++}
      for(const id of ids)if(!l.books.includes(id)){l.books.push(id);addedToLists++}
    }
    touch();renderAll();
    say(`Done: ${addedBooks} books added to My books, ${newLists} lists created, ${addedToLists} entries added to lists.`);
    toast(addedBooks||newLists||addedToLists?'Reading lists imported':'Nothing new to import');
  }catch(e){say('Import failed. Check your connection and try again.')}
  finally{const b=$('#importBtn');if(b)b.disabled=false}
}
