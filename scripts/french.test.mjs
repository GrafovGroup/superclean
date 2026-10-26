import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import worker from '../dist/server/index.js';
const routes=JSON.parse(fs.readFileSync('content/language-routes.json','utf8'));
const read=p=>fs.readFileSync('public'+p+'.html','utf8');
test('all 292 French counterparts resolve with reciprocal language metadata and equivalent indexing',async()=>{
 assert.equal(Object.keys(routes).length,292);const sitemap=fs.readFileSync('public/sitemap.xml','utf8');
 for(const [en,fr] of Object.entries(routes)){
  const english=read(en),french=read(fr);const response=await worker.fetch(new Request('https://superclean.ca'+fr),{});
  assert.equal(response.status,200,fr);assert.ok(french.includes('<html lang="fr-CA">'),fr);
  for(const h of [english,french]){assert.ok(h.includes(`hreflang="en-CA" href="https://superclean.ca${en}"`),en);assert.ok(h.includes(`hreflang="fr-CA" href="https://superclean.ca${fr}"`),fr)}
  assert.ok(french.includes(`rel="canonical" href="https://superclean.ca${fr}"`));
  const robots=english.match(/name="robots" content="([^"]+)"/)[1];assert.ok(french.includes(`name="robots" content="${robots}"`));assert.equal(sitemap.includes(`<loc>https://superclean.ca${fr}</loc>`),robots.startsWith('index'),fr);
  assert.ok(french.includes('href="/demande-de-devis'),fr);assert.ok(!french.includes('Reference photo'),fr);
 }
});
test('French city finder routes use translated service names and existing French destinations',()=>{
 for(const fr of Object.values(routes)){
  const h=read(fr);for(const [,raw] of h.matchAll(/data-local-routes="([^"]+)"/g)){
   const map=JSON.parse(raw.replaceAll('&quot;','"').replaceAll('&amp;','&').replaceAll('&#x27;',"'"));
   for(const cities of Object.values(map))for(const dest of Object.values(cities))assert.ok(fs.existsSync('public'+dest+'.html'),dest);
  }
  for(const [,action] of h.matchAll(/<form[^>]+action="([^"]+)"/g))assert.equal(action,'/demande-de-devis');
 }
 const regions=read('/fr/regions');assert.equal((regions.match(/class="market-link"/g)||[]).length,84);
});
