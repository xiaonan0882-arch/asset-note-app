const CACHE='asset-note-app-v2';
const BASE='/asset-note-app/';
const HOME=BASE+'index.html';
self.addEventListener('install',event=>{
 event.waitUntil(caches.open(CACHE).then(async cache=>{
  for(const path of [HOME,BASE+'restore.html',BASE+'manifest.webmanifest',BASE+'icon-192.png']){
   try{await cache.add(path)}catch(err){/* Pages may still be deploying; retry on next visit */}
  }
 }));
 self.skipWaiting();
});
self.addEventListener('activate',event=>{
 event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('asset-note-app-')&&k!==CACHE).map(k=>caches.delete(k)))));
 self.clients.claim();
});
self.addEventListener('fetch',event=>{
 const request=event.request,url=new URL(request.url);
 if(request.method!=='GET'||url.origin!==self.location.origin||!url.pathname.startsWith(BASE))return;
 event.respondWith((async()=>{
  const cache=await caches.open(CACHE);
  try{
   const response=await fetch(request);
   if(response.ok){cache.put(request,response.clone()).catch(()=>{});return response}
   if(response.status===404&&request.mode==='navigate'){
    const fallback=await cache.match(HOME);
    if(fallback)return fallback;
   }
   return response;
  }catch(err){
   const cached=await cache.match(request);
   if(cached)return cached;
   if(request.mode==='navigate'){
    const fallback=await cache.match(HOME);
    if(fallback)return fallback;
   }
   return Response.error();
  }
 })());
});