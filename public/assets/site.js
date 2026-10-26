'use strict';
const menu=document.querySelector('.menu-toggle'),nav=document.querySelector('#main-nav'),servicesMenu=document.querySelector('.services-nav');
menu?.addEventListener('click',()=>{const open=menu.getAttribute('aria-expanded')!=='true';menu.setAttribute('aria-expanded',String(open));nav.classList.toggle('open',open);if(!open&&servicesMenu)servicesMenu.open=false});
document.addEventListener('keydown',ev=>{if(ev.key==='Escape'){if(servicesMenu?.open){servicesMenu.open=false;servicesMenu.querySelector('summary').focus()}else if(nav?.classList.contains('open')){nav.classList.remove('open');menu.setAttribute('aria-expanded','false');menu.focus()}}});
document.addEventListener('click',ev=>{if(servicesMenu?.open&&!servicesMenu.contains(ev.target))servicesMenu.open=false});
const search=document.querySelector('#service-search');
search?.addEventListener('input',()=>{let count=0;const q=search.value.toLowerCase().trim();document.querySelectorAll('.service-item').forEach(a=>{a.hidden=!a.textContent.toLowerCase().includes(q);if(!a.hidden)count++});document.querySelectorAll('#service-directory .section').forEach(s=>{s.hidden=![...s.querySelectorAll('.service-item')].some(a=>!a.hidden)});document.querySelector('#search-status').textContent=count?`${count} services found`:'No matching services. Try another term or contact us.'});
const form=document.querySelector('#quote-form');
if(form){
 document.querySelector('.mobile-contact')?.remove();
 const params=new URLSearchParams(location.search);
 for(const key of ['service','city'])if(params.has(key))form.elements[key].value=params.get(key).slice(0,form.elements[key].maxLength);
 const submit=document.querySelector('#quote-submit'),error=document.querySelector('#quote-error'),result=document.querySelector('#quote-result');
 const fr=document.documentElement.lang.startsWith('fr');
 const copy=fr?{sending:'Envoi en cours…',send:'Envoyer la demande',done:'Demande envoyée',error:'Nous ne pouvons pas confirmer l’envoi. Vos renseignements sont conservés. Réessayez ou écrivez à get@superclean.ca.',invalid:'Veuillez vérifier les champs et réessayer.'}:{sending:'Sending…',send:'Send quote request',done:'Request submitted',error:'We could not confirm your submission. Your details are still here. Please try again or email get@superclean.ca.',invalid:'Please check the fields and try again.'};
 let pending=false,completed=false;
 form.addEventListener('submit',async event=>{
  event.preventDefault();
  if(pending||completed||!form.reportValidity())return;
  error.removeAttribute('data-fs-active');
  if(form.elements._gotcha.value)return;
  const data=new FormData(form);data.delete('photos');
  pending=true;submit.disabled=true;submit.textContent=copy.sending;form.setAttribute('aria-busy','true');
  const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),20000);
  try{
   const response=await fetch(form.action,{method:'POST',body:data,headers:{Accept:'application/json'},signal:controller.signal});
   const body=await response.json();
   if(!response.ok||body.ok!==true)throw new Error('Submission not confirmed');
   completed=true;result.setAttribute('data-fs-active','');result.focus();
   form.querySelector('.form-grid').inert=true;form.querySelector('.consent').inert=true;
   window.supercleanMeasure?.('quote_submitted');
  }catch{
   error.textContent=copy.error;error.setAttribute('data-fs-active','');error.focus();window.supercleanMeasure?.('quote_error');
  }finally{clearTimeout(timer);pending=false;form.removeAttribute('aria-busy');submit.disabled=completed;submit.textContent=completed?copy.done:copy.send;}
 });
}
document.querySelectorAll('.city-finder').forEach(f=>f.addEventListener('submit',ev=>{ev.preventDefault();if(f.reportValidity())location.href='/contact?'+new URLSearchParams(new FormData(f)).toString()}));
document.querySelectorAll('.city-finder[data-local-routes]').forEach(f=>{
 const routes=JSON.parse(f.dataset.localRoutes),details=f.querySelector('.local-service-link');
 if(!details)return;
 const destination=()=>routes[f.elements.service.value]?.[f.elements.city.value];
 const update=()=>{details.hidden=!destination()};
 f.addEventListener('change',update);
 details.addEventListener('click',()=>{const path=destination();if(path)location.href=path});
 update();
});
const citySearch=document.querySelector('#city-search');
const normalizeCity=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
citySearch?.addEventListener('input',()=>{const q=normalizeCity(citySearch.value.trim());let count=0;document.querySelectorAll('.market-group').forEach(group=>{const province=normalizeCity(group.querySelector('h3').textContent);let visible=0;group.querySelectorAll('.market-link').forEach(a=>{a.hidden=!(normalizeCity(a.textContent).includes(q)||province.includes(q));if(!a.hidden){visible++;count++}});group.hidden=visible===0});document.querySelector('#city-status').textContent=count?`${count} markets found`:'No matching market. Use the contact form to enter your municipality.'});
const enquiryCity=new URLSearchParams(location.search).get('city');if(enquiryCity)document.querySelectorAll('.city-finder select[name=city]').forEach(select=>{if([...select.options].some(o=>o.value===enquiryCity))select.value=enquiryCity});
document.querySelectorAll('.city-finder[data-local-routes]').forEach(f=>f.dispatchEvent(new Event('change')));

// Preserve the visitor's selected service and municipality when changing form language.
if(form)document.querySelectorAll('.language-switch').forEach(link=>{const url=new URL(link.href);for(const key of ['service','city'])if(new URLSearchParams(location.search).has(key))url.searchParams.set(key,new URLSearchParams(location.search).get(key));link.href=url.href;});
