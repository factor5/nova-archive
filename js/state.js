/* Shared app state (S = saved data, ui = view state) and its helpers. */
import {LS,PAGE} from './config.js';
import {applyTheme} from './theme.js';
import {THEMES} from './config.js';
export const S={read:new Set(),lists:[],reading:{},meta:{},theme:'',updatedAt:0};
export const ui={tab:'library',q:'',awards:new Set(),result:'all',read:'all',decade:'',sort:'best',group:'none',limit:PAGE,listId:null,author:'',lsort:'manual'};
export const serialize=()=>({v:2,read:[...S.read],lists:S.lists,reading:S.reading,meta:S.meta,theme:S.theme,updatedAt:S.updatedAt});
export function loadFrom(o){S.read=new Set(Array.isArray(o.read)?o.read:[]);S.lists=Array.isArray(o.lists)?o.lists:[];S.reading=(o.reading&&typeof o.reading==='object'&&!Array.isArray(o.reading))?o.reading:{};S.meta=(o.meta&&typeof o.meta==='object'&&!Array.isArray(o.meta))?o.meta:{};S.theme=THEMES.some(t=>t[0]===o.theme)?o.theme:'';S.updatedAt=o.updatedAt||0;try{if(S.theme)localStorage.setItem('nova-theme',S.theme)}catch(e){}applyTheme()}
export function loadLocal(){try{const raw=localStorage.getItem(LS);if(raw)loadFrom(JSON.parse(raw))}catch(e){}}
export const rating=id=>(S.meta[id]&&S.meta[id].r)||0;
export const hasNote=id=>!!(S.meta[id]&&S.meta[id].n);
export function setMeta(id,k,v){const m=S.meta[id]||(S.meta[id]={});if(v===''||v===0||v==null)delete m[k];else m[k]=v;if(!Object.keys(m).length)delete S.meta[id]}
