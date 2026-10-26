import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import worker from '../dist/server/index.js';
const routes=JSON.parse(fs.readFileSync('content/language-routes.json','utf8'));
const read=p=>fs.readFileSync('public'+(p==='/'?'/index':p)+'.html','utf8');
test('all 343 French counterparts resolve with reciprocal language metadata and equivalent indexing',async()=>{
 assert.equal(Object.keys(routes).length,343);const sitemap=fs.readFileSync('public/sitemap.xml','utf8');
 for(const [en,fr] of Object.entries(routes)){
  const english=read(en),french=read(fr);const response=await worker.fetch(new Request('https://superclean.ca'+fr),{});
  assert.equal(response.status,en==='/404'?404:200,fr);assert.ok(french.includes('<html lang="fr-CA">'),fr);
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
  for(const [,action] of h.matchAll(/<form[^>]+action="([^"]+)"/g))assert.ok(['/demande-de-devis','https://formspree.io/f/xvkovbqq'].includes(action));
 }
 const regions=read('/fr/regions');assert.equal((regions.match(/class="market-link"/g)||[]).length,84);
});


test('French catalogue preserves model ranges and product imagery with translated quote context',()=>{
 const productRoutes=Object.entries(routes).filter(([en])=>en.startsWith('/products/'));
 assert.equal(productRoutes.length,23);
 for(const [en,fr] of productRoutes){
  const a=read(en),b=read(fr);
  const models=h=>(h.match(/<ul class="model-list">([\s\S]*?)<\/ul>/)?.[1]||'').replace('Frost push-button dispenser','Distributeur Frost à bouton-poussoir');
  assert.equal(models(a),models(b),en);
  const images=h=>[...h.matchAll(/<img[^>]+src="([^"]+)"/g)].map(x=>x[1]);
  for(const src of images(a))assert.ok(images(b).includes(src),src);
  const query=b.match(/href="(\/demande-de-devis\?[^"]+)"/)[1];
  const u=new URL(query.replaceAll('&amp;','&'),'https://superclean.ca');
  assert.ok(u.searchParams.get('service').startsWith('Produit : '),fr);
 }
 const industryRoutes=Object.entries(routes).filter(([en])=>en.startsWith('/industries/'));
 assert.equal(industryRoutes.length,7);
 for(const [en,fr] of industryRoutes){
  const h=read(fr);assert.ok(h.includes('/assets/industry-'+en.split('/').pop()+'-fr.svg'));
  const svg=fs.readFileSync('public/assets/industry-'+en.split('/').pop()+'-fr.svg','utf8');
  assert.ok(svg.includes('LES POINTS ESSENTIELS'));assert.ok(!svg.includes('SCOPE AT A GLANCE'));
  for(const [,url] of h.matchAll(/href="([^"]+)"/g))assert.ok(!url.startsWith('/services/'),fr+' -> '+url);
 }
});

test('language switches return to the corresponding English page and French links stay French',()=>{
 for(const [en,fr] of Object.entries(routes)){
  for(const [path,target] of [[en,fr],[fr,en]]){
   const tag=read(path).match(/<a[^>]*class="[^"]*language-switch[^>]*>/)?.[0];
   assert.ok(tag?.includes(`href="${target}"`),path+' switch '+tag);
  }
  for(const tag of read(fr).matchAll(/<a\b[^>]*>/g)){
   if(tag[0].includes('language-switch'))continue;
   const dest=tag[0].match(/href="([^"?#]+)/)?.[1];
   assert.ok(!Object.hasOwn(routes,dest),fr+' English link '+dest);
  }
 }
});
test('unknown French routes retain French error recovery',async()=>{
 const response=await worker.fetch(new Request('https://superclean.ca/fr/inconnue'),{});
 assert.equal(response.status,404);assert.ok((await response.text()).includes('<html lang="fr-CA">'));
});
