import fs from 'node:fs';
import assert from 'node:assert/strict';
const files=fs.readdirSync('public',{recursive:true}).filter(p=>p.endsWith('.html'));
for(const p of files){const html=fs.readFileSync('public/'+p,'utf8');assert.equal((html.match(/<h1[ >]/g)||[]).length,1,p);assert.ok(html.includes('/assets/original-favicon.svg'),p);
for(const [,value] of html.matchAll(/(?:href|src)="([^"]+)"/g)){const url=new URL(value.replaceAll('&amp;','&'),'https://superclean.ca');if(url.origin!=='https://superclean.ca')continue;const route=decodeURIComponent(url.pathname);assert.ok(route==='/'||fs.existsSync('public'+route)||fs.existsSync('public'+route+'.html'),p+' -> '+route);}}
for(const p of ['contact','demande-de-devis']){const h=fs.readFileSync('public/'+p+'.html','utf8');assert.ok(h.includes('id="quote-form"'));assert.ok(!h.includes('unpkg.com'));assert.ok(h.includes('hreflang="fr-CA"'));}
console.log(`Audited ${files.length} pages: internal destinations, favicon and heading checks pass; both quote forms present.`);
