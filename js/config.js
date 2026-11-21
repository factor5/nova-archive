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
export const THEMES=[['dark','☾','Nova (dark)'],['paper','☀','Paper (light)'],['auto','◐','Auto (follows phone)']];
