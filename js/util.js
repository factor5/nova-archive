/* Small DOM and string helpers. */

export const $=(s,r=document)=>r.querySelector(s);
export const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const norm=s=>s.normalize('NFKD').replace(/[̀-ͯ]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
export const uid=()=>Date.now().toString(36)+Math.random().toString(36).slice(2,7);
export function toast(msg){const r=$('#toastRoot');r.innerHTML='<div class="toast">'+esc(msg)+'</div>';clearTimeout(toast.t);toast.t=setTimeout(()=>r.innerHTML='',2200)}
export function surname(a){const p=a.replace(/\s*&.*$/,'').replace(/ and .*$/,'').split(' ');return p[p.length-1].toLowerCase()}
