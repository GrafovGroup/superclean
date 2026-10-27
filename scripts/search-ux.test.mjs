import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const routes=JSON.parse(fs.readFileSync('content/language-routes.json','utf8'));
const read=r=>fs.readFileSync('public'+(r==='/'?'/index':r)+'.html','utf8');
const schema=h=>[...h.matchAll(/<script type="application\/ld\+json">(.*?)<\/script>/gs)].flatMap(m=>JSON.parse(m[1]));
test('French service markup and breadcrumbs match their English counterparts',()=>{
 let count=0;
 for(const [en,fr] of Object.entries(routes)){
  const a=read(en),b=read(fr),sa=schema(a),sb=schema(b);
  if(sa.some(x=>x['@type']==='Service')){
   count++;const service=sb.find(x=>x['@type']==='Service');assert.ok(service,fr);
   assert.equal(service.url,'https://superclean.ca'+fr);assert.ok(b.includes(service.name.replaceAll('&','&amp;'))||b.includes(service.name),fr);
  }
  const breadcrumb=b.match(/<nav class="breadcrumbs.*?<\/nav>/s)?.[0];
  if(breadcrumb){assert.ok(!breadcrumb.includes('<details'),fr);assert.ok(sb.some(x=>x['@type']==='BreadcrumbList'),fr);}
 }
 assert.equal(count,268);
});
test('priority service answers and multi-location intake exist in both languages',()=>{
 const answers=JSON.parse(fs.readFileSync('content/service-answers.json','utf8'));assert.equal(Object.keys(answers).length,10);
 for(const key of Object.keys(answers))for(const route of ['/services/'+key,routes['/services/'+key]]){
  const h=read(route);assert.equal((h.match(/id="service-answers"/g)||[]).length,1,route);
 }
 for(const route of ['/contact','/demande-de-devis']){
  const h=read(route);assert.ok(h.includes('name="locations"'));assert.ok(h.includes('id="quote-next-steps"'));
  assert.ok(!h.includes('name="locations" required'));
 }
});
