'use strict';
// Provider-neutral conversion events. No cookies, identifiers or form values.
// Attach the chosen analytics adapter to `superclean:conversion` at launch.
(()=>{
 const allowed=new Set(['quote_started','quote_submitted','quote_error','quote_cta_click','phone_click','email_click']);
 const canonical=document.querySelector('link[rel=canonical]')?.href;
 const pagePath=canonical?new URL(canonical).pathname:'/';
 window.supercleanMeasure=(event,placement='main')=>{
  if(!allowed.has(event))return;
  const detail=Object.freeze({event,page_path:pagePath,placement:['header','footer','mobile','main'].includes(placement)?placement:'main'});
  document.dispatchEvent(new CustomEvent('superclean:conversion',{detail}));
 };
 document.addEventListener('click',event=>{
  const anchor=event.target.closest?.('a[href]');if(!anchor)return;
  const href=anchor.getAttribute('href');
  const placement=anchor.closest('.mobile-contact')?'mobile':anchor.closest('header,.utility')?'header':anchor.closest('footer')?'footer':'main';
  if(href.startsWith('tel:'))window.supercleanMeasure('phone_click',placement);
  else if(href.startsWith('mailto:'))window.supercleanMeasure('email_click',placement);
  else if(new URL(anchor.href,location.href).origin===location.origin&&['/contact','/demande-de-devis'].includes(new URL(anchor.href,location.href).pathname))window.supercleanMeasure('quote_cta_click',placement);
 });
 document.querySelector('#quote-form')?.addEventListener('input',()=>window.supercleanMeasure('quote_started'),{once:true});
})();
