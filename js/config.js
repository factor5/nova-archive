/* Constants shared across modules. */

export const AWARDS=[
 {key:'Hugo Award',short:'Hugo',color:'#3be8ff'},
 {key:'Nebula Award',short:'Nebula',color:'#a98bff'},
 {key:'Arthur C. Clarke Award',short:'Clarke',color:'#5dffb0'},
 {key:'John W. Campbell Memorial Award',short:'Campbell',color:'#ff9f45'},
 {key:'Locus Award (SF Novel)',short:'Locus',color:'#ff4bd8'},
 {key:'Philip K. Dick Award',short:'PKD',color:'#ffd84a'},
 {key:'BSFA Award',short:'BSFA',color:'#6aa8ff'}
];
export const AW=Object.fromEntries(AWARDS.map(a=>[a.key,a]));
export const LS='nova-archive-v1';
export const PAGE=60;
export const FB_VER='11.10.0';
/* [id, icon, label, browser-bar colour, swatch colour]. Add a theme here and as css/theme-<id>.css. */
export const THEMES=[
  ['dark','☾','Nova (dark)','#04060d','#3be8ff'],
  ['paper','☀','Paper (light)','#f3eee1','#0f6b73'],
  ['terminal','>_','Terminal (green on black)','#000000','#39ff7a'],
  ['dune','≋','Dune (sand and spice)','#1b120b','#e8a24a'],
  ['auto','◐','Auto (light or dark, follows phone)','','#93a8d0']
];
export const AUTO_LIGHT='paper',AUTO_DARK='dark';
