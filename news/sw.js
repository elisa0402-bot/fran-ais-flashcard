const CACHE='onyva-news-shell-v2-mobile';
const SHELL=['./','./index.html','./style.css','./app.js','./mobile-install.js','./install-qr.svg','./core.js','./seed.js','./manifest.webmanifest','./icon-192.png','./icon-512.png','./icon.svg'];
self.addEventListener('install',event=>{event.waitUntil(caches.open(CACHE).then(c=>c.addAll(SHELL)).then(()=>self.skipWaiting()));});
self.addEventListener('activate',event=>{
  event.waitUntil(caches.keys().then(keys=>Promise.all(keys.filter(k=>k.startsWith('onyva-news-shell-')&&k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));
});
self.addEventListener('fetch',event=>{
  const req=event.request,url=new URL(req.url);
  if(req.method!=='GET'||url.origin!==self.location.origin||!url.pathname.startsWith(new URL('./',self.location).pathname))return;
  if(url.pathname.endsWith('data.json')||url.pathname.includes('/downloads/'))return;
  if(req.mode==='navigate'){
    event.respondWith(fetch(req).then(res=>{if(res.ok)caches.open(CACHE).then(c=>c.put(req,res.clone()));return res;}).catch(()=>caches.match('./index.html')));return;
  }
  event.respondWith(caches.match(req).then(cached=>{
    const fresh=fetch(req).then(res=>{if(res.ok)caches.open(CACHE).then(c=>c.put(req,res.clone()));return res;});
    if(cached){event.waitUntil(fresh.catch(()=>{}));return cached;}
    return fresh;
  }));
});
