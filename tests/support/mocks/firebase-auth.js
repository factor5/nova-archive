/* Test double for firebase-auth.js. The "signed-in user" lives in localStorage key `fake-auth`.
   Tests can set it to simulate an existing session: {"uid":"u1","email":"me@example.com"}.
   window.__fakeAuth.nextUser = {uid,email} chooses who the next sign-in becomes (default u1).
   window.__fakeAuth.failNext = 'auth/popup-blocked' | 'auth/popup-closed-by-user' | 'auth/network-request-failed' makes the next sign-in fail. */
const K='fake-auth';let cb=null;
const get=()=>{try{return JSON.parse(localStorage.getItem(K))}catch(e){return null}};
window.__fakeAuth=window.__fakeAuth||{failNext:null,redirected:false};
export function getAuth(){return {get currentUser(){return get()}}}
export function onAuthStateChanged(a,f){cb=f;setTimeout(()=>f(get()),0);return()=>{}}
export async function signInWithPopup(){
  const f=window.__fakeAuth.failNext;if(f){window.__fakeAuth.failNext=null;const e=new Error(f);e.code=f;throw e}
  const u=window.__fakeAuth.nextUser||{uid:'u1',email:'me@example.com'};localStorage.setItem(K,JSON.stringify(u));cb(u)}
export async function signInWithRedirect(){window.__fakeAuth.redirected=true}
export class GoogleAuthProvider{}
export async function signOut(){localStorage.removeItem(K);cb(null)}
