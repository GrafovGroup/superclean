import {test} from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import fs from 'node:fs';
const source=fs.readFileSync(new URL('../public/assets/site.js',import.meta.url),'utf8');
function setup(fetch,lang='en-CA'){
 const listeners={};const el=()=>({textContent:'',disabled:false,inert:false,attrs:{},setAttribute(k,v){this.attrs[k]=v},removeAttribute(k){delete this.attrs[k]},focus(){this.focused=true}});
 const submit=el(),error=el(),result=el(),grid=el(),consent=el();
 const form={action:'https://formspree.io/f/xvkovbqq',elements:{_gotcha:{value:''}},reportValidity:()=>true,addEventListener:(n,f)=>listeners[n]=f,setAttribute(){},removeAttribute(){},querySelector:s=>s==='.form-grid'?grid:consent};
 const context={document:{documentElement:{lang},querySelector:s=>({'#quote-form':form,'#quote-submit':submit,'#quote-error':error,'#quote-result':result}[s]||null),querySelectorAll:()=>[],addEventListener(){}},location:{search:''},URL,URLSearchParams,AbortController,setTimeout,clearTimeout,fetch,FormData:class{delete(){}},window:{}};
 vm.runInNewContext(source,context);return {submit,error,result,form,run:()=>listeners.submit({preventDefault(){}})};
}
test('confirmed success locks the form and prevents duplicate submissions',async()=>{let calls=0;const x=setup(async()=>{calls++;return{ok:true,json:async()=>({ok:true})}});await x.run();assert.equal(x.submit.disabled,true);assert.ok('data-fs-active' in x.result.attrs);await x.run();assert.equal(calls,1)});
test('network, rejected, invalid JSON and unconfirmed responses retain a retryable form',async()=>{
 for(const fetch of [async()=>{throw Error('offline')},async()=>({ok:false,json:async()=>({error:'blocked'})}),async()=>({ok:true,json:async()=>{throw Error('invalid')}}),async()=>({ok:true,json:async()=>({})})]){const x=setup(fetch);await x.run();assert.equal(x.submit.disabled,false);assert.ok('data-fs-active' in x.error.attrs);assert.ok(!('data-fs-active' in x.result.attrs));}
});
test('French errors and honeypot handling',async()=>{const x=setup(async()=>{throw Error()},'fr-CA');await x.run();assert.match(x.error.textContent,/Vos renseignements/);let calls=0;const y=setup(async()=>calls++);y.form.elements._gotcha.value='spam';await y.run();assert.equal(calls,0)});
