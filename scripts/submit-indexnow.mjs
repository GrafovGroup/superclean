// Run after publishing; only canonical, indexable sitemap URLs are submitted.
import fs from 'node:fs';
const {host,keyFile}=JSON.parse(fs.readFileSync('content/indexnow.json','utf8'));
const key=fs.readFileSync('public/'+keyFile,'utf8').trim();
const keyLocation='https://'+host+'/'+keyFile;
const proof=await fetch(keyLocation);
if(!proof.ok || (await proof.text()).trim()!==key)throw new Error('Live ownership proof is not available; no URLs submitted.');
const urlList=[...fs.readFileSync('public/sitemap.xml','utf8').matchAll(/<loc>(.*?)<\/loc>/g)].map(m=>m[1]);
const response=await fetch('https://www.bing.com/indexnow',{method:'POST',headers:{'Content-Type':'application/json; charset=utf-8'},body:JSON.stringify({host,key,keyLocation,urlList})});
console.log(JSON.stringify({engine:'Bing / IndexNow',status:response.status,urlCount:urlList.length,result:await response.text()}));
if(![200,202].includes(response.status))process.exitCode=1;
