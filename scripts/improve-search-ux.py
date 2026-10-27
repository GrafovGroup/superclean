"""Idempotent bilingual search content, breadcrumb and quote improvements."""
from pathlib import Path
import json, re, html, hashlib

ROOT=Path(__file__).resolve().parent.parent
P=ROOT/'public'
routes=json.loads((ROOT/'content/language-routes.json').read_text())
routes.update({'/':'/services-de-nettoyage','/contact':'/demande-de-devis'})
esc=lambda s: html.escape(s,quote=True)
plain=lambda s: html.unescape(re.sub('<[^>]+>','',s)).strip()
def file(route): return P/('index.html' if route=='/' else route.lstrip('/')+'.html')
def heading(s):
 m=re.search(r'<h1[^>]*>(.*?)</h1>',s,re.S)
 return plain(m[1]) if m else ''

answers=json.loads((ROOT/'content/service-answers.json').read_text())
for key,data in answers.items():
 en='/services/'+key
 for language,route in [('en',en),('fr',routes[en])]:
  p=file(route);s=p.read_text();a=data[language]
  s=re.sub(r'<section id="service-answers".*?</section>','',s,flags=re.S)
  s=re.sub(r'(<p class="lede">).*?</p>',lambda m:m[1]+esc(a[0])+'</p>',s,count=1,flags=re.S)
  block='<section id="service-answers" class="section"><div class="wrap"><p class="eyebrow">'+('PLAN YOUR SERVICE' if language=='en' else 'PLANIFIER VOTRE SERVICE')+'</p><h2>'+('Practical answers before you request a quote.' if language=='en' else 'Des réponses utiles avant votre demande de devis.')+'</h2><div class="three-col">'
  for i in range(1,len(a),2):block+='<article><h3>'+esc(a[i])+'</h3><p>'+esc(a[i+1])+'</p></article>'
  block+='</div></div></section>'
  start=s.index('<main');at=s.index('</section>',start)+len('</section>');s=s[:at]+block+s[at:]
  if language=='en':
   def update_schema(m):
    objects=json.loads(m[1]);objects=objects if isinstance(objects,list) else [objects]
    for obj in objects:
     if obj.get('@type')=='Service':obj['description']=a[0]
    return '<script type="application/ld+json">'+json.dumps(objects,ensure_ascii=False)+'</script>'
   s=re.sub(r'<script type="application/ld\+json">(.*?)</script>',update_schema,s,flags=re.S)
  p.write_text(s)

# A straightforward provider description, without invented offices or credentials.
about={
 '/about': 'Superclean Canada Inc. provides commercial cleaning, specialist facility services and facility products for businesses across Canada. Projects are scoped and coordinated through Superclean, with qualified execution partners where needed. Availability, access requirements and the work included are confirmed for each location.',
 '/fr/a-propos': 'Superclean Canada Inc. fournit des services de nettoyage commercial, des services spécialisés aux installations et des produits pour les entreprises partout au Canada. Superclean définit et coordonne les projets, avec des partenaires d’exécution qualifiés au besoin. La disponibilité, les accès et les travaux inclus sont confirmés pour chaque établissement.'
}
for route,copy in about.items():
 p=file(route);s=p.read_text();s=re.sub(r'(<p class="lede">).*?</p>',lambda m:m[1]+esc(copy)+'</p>',s,count=1,flags=re.S);p.write_text(s)

for route,fr in [('/contact',False),('/demande-de-devis',True)]:
 p=file(route);s=p.read_text()
 if 'name="locations"' not in s:
  label='Plusieurs établissements (facultatif)' if fr else 'Multiple locations (optional)'
  hint='Indiquez les adresses ou municipalités et les besoins de chaque site.' if fr else 'List the addresses or municipalities and the needs at each site.'
  field='<label class="full">'+label+'<textarea name="locations" rows="3" maxlength="6000" aria-describedby="locations-help"></textarea><span id="locations-help" class="small">'+hint+'</span></label>'
  s=s.replace('<div class="optional-grid">','<div class="optional-grid">'+field,1)
 if 'id="quote-next-steps"' not in s:
  copy='Après réception, nous examinons votre demande, précisons les renseignements manquants et déterminons si une visite est nécessaire. Le devis écrit confirme la portée des travaux et les modalités proposées.' if fr else 'After receiving your request, we review the scope, clarify missing details and assess whether a site visit is needed. The written quote confirms the proposed work and arrangements.'
  s=s.replace('<div class="form-grid">','<p id="quote-next-steps">'+copy+'</p><div class="form-grid">',1)
 p.write_text(s)

# Match French structured data to the equivalent English page, translating visible labels.
titles={en:heading(file(fr).read_text()) for en,fr in routes.items() if file(fr).exists()}
for en,fr in routes.items():
 if not file(en).exists() or not file(fr).exists():continue
 p=file(fr);s=p.read_text();source=file(en).read_text();schemas=[]
 for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',source,re.S):
  data=json.loads(raw);schemas+=data if isinstance(data,list) else [data]
 own=[]
 for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S):
  data=json.loads(raw);own+=data if isinstance(data,list) else [data]
 own=[x for x in own if x.get('@type') not in ['Service','BreadcrumbList']]
 crumbs=[]
 for item in schemas:
  if item.get('@type')=='Service':
   item=json.loads(json.dumps(item));item['name']=heading(s);item['url']='https://superclean.ca'+fr;item['@id']=item['url']+'#service'
   base='/services/'+en.split('/')[2] if en.startswith('/services/') else en
   item['serviceType']=titles.get(base,heading(s))
   lede=re.search(r'<p class="lede">(.*?)</p>',s,re.S)
   if lede:item['description']=plain(lede[1])
   own.append(item)
  elif item.get('@type')=='BreadcrumbList':
   for entry in item['itemListElement']:
    route=entry['item'].removeprefix('https://superclean.ca') or '/'
    if route not in routes:continue
    label={'/':'Accueil','/services':'Services','/industries':'Secteurs','/locations':'Zones desservies'}.get(route,titles.get(route,entry['name']))
    crumbs.append({'@type':'ListItem','position':len(crumbs)+1,'name':label,'item':'https://superclean.ca'+routes[route]})
   if crumbs:own.append({'@context':'https://schema.org','@type':'BreadcrumbList','itemListElement':crumbs})
 if crumbs and re.search(r'<nav class="breadcrumbs',s):
  links=[]
  for entry in crumbs:
   route=entry['item'].removeprefix('https://superclean.ca')
   links.append('<span aria-current="page">'+esc(entry['name'])+'</span>' if route==fr else '<a href="'+esc(route)+'">'+esc(entry['name'])+'</a>')
  nav='<nav class="breadcrumbs wrap" aria-label="Fil d’Ariane">'+'<span aria-hidden="true">/</span>'.join(links)+'</nav>'
  s=re.sub(r'<nav class="breadcrumbs.*?</nav>',lambda m:nav,s,count=1,flags=re.S)
 s=re.sub(r'<script type="application/ld\+json">.*?</script>','',s,flags=re.S)
 s=s.replace('</head>','<script type="application/ld+json">'+json.dumps(own,ensure_ascii=False).replace('</','<\\/')+'</script></head>')
 p.write_text(s)
digest=hashlib.sha256((P/'assets/site.css').read_bytes()).hexdigest()[:12]
for p in P.rglob('*.html'):
 s=p.read_text();updated=re.sub(r'/assets/site\.css(?:\?v=[a-z0-9]+)?','/assets/site.css?v='+digest,s)
 if updated!=s:p.write_text(updated)
print('Search/UX: French service and breadcrumb parity; 20 enriched service pages; bilingual quote guidance and multi-site intake.')
