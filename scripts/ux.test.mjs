import {test} from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import worker from '../dist/server/index.js';
test('both quote forms keep optional detail fields separate and retain required intake',()=>{
 for(const file of ['contact','demande-de-devis']){
  const s=fs.readFileSync('public/'+file+'.html','utf8');
  const optional=s.match(/<details class="quote-extra full">([\s\S]*?)<\/details>/)[1];
  for(const name of ['company','postal','facility','timing'])assert.ok(optional.includes(`name="${name}"`));
  assert.ok(!optional.includes(' required'));
  for(const name of ['name','email','city','service','details'])assert.match(s,new RegExp(`name="${name}"[^>]*required`));
  assert.ok(s.includes('action="https://formspree.io/f/xvkovbqq"'));assert.ok(s.includes('class="quote-page"'));
 }
});
test('both service directories expose exactly 52 unique services in five categories',()=>{
 for(const file of ['services','fr/services']){
  const s=fs.readFileSync('public/'+file+'.html','utf8');
  const links=[...s.matchAll(/class="service-item" href="([^"]+)"/g)].map(m=>m[1]);
  assert.equal(links.length,52);assert.equal(new Set(links).size,52);
  for(const id of ['routine','exterior','specialty','waste','technical'])assert.ok(s.includes(`id="${id}"`));
 }
});
test('IndexNow ownership proof is publicly served as plain text',async()=>{
 const {keyFile}=JSON.parse(fs.readFileSync('content/indexnow.json','utf8'));
 const response=await worker.fetch(new Request('https://superclean.ca/'+keyFile),{});
 assert.equal(response.status,200);assert.ok(response.headers.get('Content-Type').startsWith('text/plain'));
 assert.equal(await response.text(),fs.readFileSync('public/'+keyFile,'utf8'));
});
