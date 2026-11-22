/* Small DOM and string helpers. */

export const $=(s,r=document)=>r.querySelector(s);
export const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
export const norm=s=>s.normalize('NFKD').replace(/[̀-ͯ]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim();
export const uid=()=>Date.now().toString(36)+Math.random().toString(36).slice(2,7);
export function toast(msg){const r=$('#toastRoot');r.innerHTML='<div class="toast">'+esc(msg)+'</div>';clearTimeout(toast.t);toast.t=setTimeout(()=>r.innerHTML='',2200)}
/* Key for "Author A–Z": surname first (Le Guin, not Guin; Miller, not Jr.), then the given names. First listed author only. */
export function sortKey(a){
  const f=a.replace(/\s*&.*$/,'').replace(/ and .*$/,'').replace(/,?\s+(Jr|Sr)\.?$/i,'').replace(/\s+(II|III|IV)$/,'');
  const p=f.split(' ');let i=p.length-1;
  while(i>0&&/^(le|la|van|von|der|den|ten|du|del|della|di|da)$/i.test(p[i-1]))i--;
  return (p.slice(i).join(' ')+' '+p.slice(0,i).join(' ')).toLowerCase();
}
export function surname(a){const p=a.replace(/\s*&.*$/,'').replace(/ and .*$/,'').split(' ');return p[p.length-1].toLowerCase()}
