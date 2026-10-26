import http from 'node:http';
import fs from 'node:fs/promises';
import path from 'node:path';
import worker from '../dist/server/index.js';
const types={'.css':'text/css','.js':'application/javascript','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.webp':'image/webp','.ttf':'font/ttf'};
http.createServer(async(req,res)=>{try{
 if(req.url==='/__qa'){res.setHeader('Content-Type','text/html');res.end('<h1>French responsive review</h1><iframe title="French product 320" src="/services-de-nettoyage" width="320" height="900"></iframe><iframe title="French industry 375" src="/demande-de-devis" width="375" height="900"></iframe><iframe title="French catalogue 768" src="/fr/services" width="768" height="900"></iframe>');return;}
 const origin='http://'+req.headers.host;
 const request=new Request(new URL(req.url,origin),{method:req.method});
 const response=await worker.fetch(request,{ASSETS:{fetch:async(r)=>{const p=path.resolve('public','.'+new URL(r.url).pathname);if(!p.startsWith(path.resolve('public/assets')+'/'))return new Response('',{status:404});try{return new Response(await fs.readFile(p),{headers:{'Content-Type':types[path.extname(p)]||'application/octet-stream'}})}catch{return new Response('',{status:404})}}}});
 const headers=new Headers(response.headers);headers.delete('X-Frame-Options');headers.set('Content-Security-Policy',(headers.get('Content-Security-Policy')||'').replace("frame-ancestors 'none'","frame-ancestors 'self'"));res.writeHead(response.status,Object.fromEntries(headers));res.end(Buffer.from(await response.arrayBuffer()));
}catch{res.writeHead(500);res.end('Preview error')}}).listen(Number(process.argv[process.argv.indexOf('--port')+1])||Number(process.env.PORT)||3000,'0.0.0.0');
