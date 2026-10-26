"""Idempotent bilingual presentation improvements; run after French generation."""
from pathlib import Path
import re,json,html,hashlib
P=Path(__file__).resolve().parent.parent/'public'
routes=json.loads((P.parent/'content/language-routes.json').read_text())
frdata={}
for line in (P.parent/'content/services-fr.tsv').read_text().splitlines():
 key,title,*_=line.split('|');frdata[key]=title
source=(P/'services.html').read_text()
services={}
for href,label in re.findall(r'<a class="service-item" href="(/services/[^"#?]+)">(.*?)</a>',source,re.S):
 services[href]=html.unescape(re.sub('<[^>]*>','',label).replace('↗','')).strip()
assert len(services)==52,len(services)
groups=[('routine','Recurring & everyday cleaning','Entretien régulier',[]),('exterior','Exterior & building cleaning','Nettoyage extérieur',[]),('specialty','Specialty & project cleaning','Nettoyage spécialisé',[]),('waste','Waste & disposal','Déchets et vidange',[]),('technical','Technical & facility services','Services techniques',[])]
routine={'commercial-janitorial','carpet-cleaning','disinfecting','residential-cleaning','gym-cleaning','mat-cleaning','post-office-cleaning','upholstery-and-mattress-cleaning','urinal-toilet-sanitizer'}
exterior={'graffiti-removal','power-washing','window-cleaning','anti-graffiti-coating-and-sealing','building-structure-cleaning','gum-removal','low-pressure-washing','bridge-and-underpass-washing','parking-lot-cleaning','window-glazing','solar-panel-cleaning','drone-cleaning'}
waste={'feminine-hygiene-disposal','portable-toilet-cleaning','septic-tank-cleaning','grease-trap-cleaning','catch-basin-cleaning-and-disposal','biomedical-waste-disposal','dumpster-bin-disposal','hazardous-waste-disposal','vape-recycling-disposal'}
special={'mobile-vehicle-cleaning-and-detailing','post-event-cleaning','post-construction-cleaning','ice-rink-cleaning','high-level-dusting','wind-turbine-cleaning','laser-cleaning'}
for route,label in services.items():
 k=route.rsplit('/',1)[-1];i=0 if k in routine else 1 if k in exterior else 3 if k in waste else 2 if k in special else 4;groups[i][3].append((route,label))
def name(route,label,fr):return frdata[route.rsplit('/',1)[-1]] if fr else label
def link(route,fr):return routes[route] if fr else route
def menu(fr):
 base='/fr/services' if fr else '/services';out='<details class="services-nav"><summary>Services <span aria-hidden="true">⌄</span></summary><div class="mega-menu"><div class="mega-head"><a href="'+base+'#service-search">'+('Rechercher parmi nos services' if fr else 'Search all services')+' ↗</a></div><div class="mega-groups">'
 for key,en,fn,items in groups:
  out+='<div><h2>'+html.escape(fn if fr else en)+'</h2>'
  for r,l in items[:3]:out+='<a href="'+link(r,fr)+'">'+html.escape(name(r,l,fr))+'</a>'
  out+='<a class="mega-view" href="'+base+'#'+key+'">'+('Voir la catégorie' if fr else 'View category')+' ↗</a></div>'
 return out+'</div></div></details>'
for path in P.rglob('*.html'):
 s=path.read_text();fr='<html lang="fr-CA"' in s
 # Match only the existing Services disclosure (other details are page content).
 s=re.sub(r'<details class="services-nav">.*?</details>',menu(fr),s,flags=re.S)
 if fr:s=s.replace('<a href="/fr/services">Services</a>',menu(True),1)
 path.write_text(s)
for fr in [False,True]:
 path=P/('fr/services.html' if fr else 'services.html');s=path.read_text();base='/fr/services' if fr else '/services'
 title='Trouvez le service adapté à vos locaux.' if fr else 'Find the right service for your space.'
 desc='Entretien récurrent, projet ponctuel ou besoin spécialisé : choisissez une catégorie ou recherchez un service.' if fr else 'Recurring cleaning, a one-time project or a specialist job. Choose a category or search for a service.'
 body='<section class="page-intro wrap directory-intro"><div><p class="eyebrow">'+('NOS SERVICES' if fr else 'OUR SERVICES')+'</p><h1>'+title+'</h1><p class="lede">'+desc+'</p></div></section><div class="wrap filter-bar"><label for="service-search">'+('Rechercher un service' if fr else 'Search services')+'</label><input id="service-search" type="search" placeholder="'+('Ex. : vitres, tapis, cuisine…' if fr else 'Try windows, floors, kitchen…')+'" aria-controls="service-directory" aria-describedby="search-status"><p id="search-status" role="status" aria-live="polite"></p><nav class="category-jumps" aria-label="'+('Catégories de services' if fr else 'Service categories')+'">'
 for key,en,fn,_ in groups:body+='<a href="#'+key+'">'+html.escape(fn if fr else en)+'</a>'
 body+='</nav></div><div id="service-directory">'
 for key,en,fn,items in groups:
  body+='<section class="section" id="'+key+'"><div class="wrap"><h2>'+html.escape(fn if fr else en)+'</h2><div class="service-list">'
  for r,l in items:body+='<a class="service-item" href="'+link(r,fr)+'"><span>'+html.escape(name(r,l,fr))+'</span><span aria-hidden="true">↗</span></a>'
  body+='</div></div></section>'
 body+='</div><section class="wrap service-help"><h2>'+('Vous hésitez sur le service à choisir?' if fr else 'Not sure which service you need?')+'</h2><p>'+('Décrivez les travaux et votre emplacement. Nous vous aiderons à préciser le mandat.' if fr else 'Tell us what needs attention and where. We’ll help define the scope.')+'</p><a class="button" href="'+('/demande-de-devis' if fr else '/contact')+'">'+('Demander un devis' if fr else 'Request a quote')+' ↗</a></section>'
 s=re.sub(r'<main[^>]*>.*?</main>','<main id="main">'+body+'</main>',s,flags=re.S);path.write_text(s)
 # Compact homepage with language-specific line breaks.
 path=P/('services-de-nettoyage.html' if fr else 'index.html');s=path.read_text()
 s=re.sub(r'(<section class="home-hero[^>]*>.*?<h1>).*?</h1>',lambda m:m[1]+('Nettoyage commercial.<br><span>Partout au Canada.</span>' if fr else 'Commercial cleaning.<br><span>Across Canada.</span>')+'</h1>',s,count=1,flags=re.S)
 if fr:s=re.sub(r'<nav class="breadcrumbs wrap".*?</nav>','',s,count=1,flags=re.S)
 path.write_text(s)
 # Six visible fields, with optional details in a native accessible disclosure.
 path=P/('demande-de-devis.html' if fr else 'contact.html');s=path.read_text()
 s=s.replace('<main id="main">','<main id="main" class="quote-page">')
 s=re.sub(r'(<section class="page-intro[^>]*>.*?<h1>).*?</h1>',lambda m:m[1]+('Demander un devis.' if fr else 'Request a quote.')+'</h1>',s,count=1,flags=re.S)
 start=s.index('<div class="form-grid">');end=s.index('<div class="form-trap"',start)
 labels={}
 for block in re.findall(r'<label\b.*?</label>',s[start:end],re.S):
  n=re.search(r'name="([^"]+)"',block)
  if n:labels[n[1]]=block
 required=['name','email','city','service','details','phone'];optional=['company','postal','facility','timing']
 assert all(k in labels for k in required+optional)
 summary='Renseignements supplémentaires (facultatif)' if fr else 'Additional details (optional)'
 grid='<div class="form-grid">'+''.join(labels[k] for k in required)+'<details class="quote-extra full"><summary>'+summary+'</summary><div class="optional-grid">'+''.join(labels[k] for k in optional)+'</div></details></div>'
 s=s[:start]+grid+s[end:]
 # Removed obsolete hidden upload controls; photos continue through the existing email path.
 s=re.sub(r'<button[^>]*id="quote-remove-photos".*?</button>','',s,flags=re.S)
 path.write_text(s)
# Version static assets consistently so repeat visitors receive new CSS and interactions.
for path in P.rglob('*.html'):
 s=path.read_text()
 for asset in ['site.css','site.js']:
  digest=hashlib.sha256((P/'assets'/asset).read_bytes()).hexdigest()[:12]
  s=re.sub(r'/assets/'+re.escape(asset)+r'(?:\?v=[a-z0-9]+)?','/assets/'+asset+'?v='+digest,s)
 path.write_text(s)
print('UX polish: bilingual navigation, five service groups, compact homepage and progressive quote form.')

# Dates identify substantive content changes, rather than every shared navigation update.
p=P/'sitemap.xml';s=p.read_text()
for route in ['/', '/services', '/contact', '/services-de-nettoyage', '/fr/services', '/demande-de-devis']:
 loc='<loc>https://superclean.ca'+route+'</loc>'
 s=re.sub(re.escape(loc)+r'(?:<lastmod>.*?</lastmod>)?',loc+'<lastmod>2026-10-26</lastmod>',s)
p.write_text(s)
