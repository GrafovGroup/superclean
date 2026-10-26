"""Build the French service/location counterparts from reviewed French content."""
from pathlib import Path
import html,json,re,unicodedata,hashlib
from urllib.parse import urlencode
ROOT=Path(__file__).resolve().parent.parent
P=ROOT/'public'
def esc(v):return html.escape(str(v),quote=True)
def slug(s):return re.sub(r'[^a-z0-9]+','-',unicodedata.normalize('NFD',s).encode('ascii','ignore').decode().lower()).strip('-')
services={}
for row in (ROOT/'content/services-fr.tsv').read_text().splitlines():
 key,title,desc,scope,caution,requirements=row.split('|');services[key]=dict(title=title,desc=desc,scope=scope.split(';'),caution=caution,requirements=requirements,slug=slug(title))
regions=json.loads((ROOT/'content/regions-fr.json').read_text())
cities=json.loads((ROOT/'content/cities-fr.json').read_text())
route_map={'/services':'/fr/services','/locations':'/fr/regions'}
for key,s in services.items():route_map['/services/'+key]='/fr/services/'+s['slug']
for key,r in regions.items():route_map['/locations/'+key]='/fr/regions/'+slug(r['name'])
for key,c in cities.items():route_map['/locations/'+c['region']+'/'+key]=route_map['/locations/'+c['region']]+'/'+key
for key,s in services.items():
 for p in (P/'services'/key).glob('*.html'):
  route_map['/services/'+key+'/'+p.stem]=route_map['/services/'+key]+'/'+p.stem
aliases={
 'toronto-night-cleaning':('commercial-janitorial','toronto','Nettoyage de nuit'),
 'toronto-office-cleaning':('commercial-janitorial','toronto','Nettoyage de bureaux'),
 'newmarket-night-cleaning':('commercial-janitorial','newmarket','Nettoyage de nuit'),
 'newmarket-office-cleaning':('commercial-janitorial','newmarket','Nettoyage de bureaux'),
 'aurora-night-cleaning':('commercial-janitorial','aurora','Nettoyage de nuit'),
 'barrie-office-cleaning':('commercial-janitorial','barrie','Nettoyage de bureaux'),
 'vancouver-commercial-cleaning':('commercial-janitorial','vancouver','Nettoyage commercial'),
 'commercial-kitchen-exhaust-vent-and-hood-cleaning-in-nanaimo':('exhaust-hood-cleaning','nanaimo','Nettoyage de hottes et de systèmes d’extraction de cuisine')}
for key,(base,city,title) in aliases.items():route_map['/services/'+key]='/fr/services/'+slug(title)+'-'+city
css=hashlib.sha256((P/'assets/site.css').read_bytes()).hexdigest()[:12]
js=hashlib.sha256((P/'assets/site.js').read_bytes()).hexdigest()[:12]
# Keep the original indexing policy. Thin/local variants are not newly promoted into search.
def policy(en):
 h=(P/('index.html' if en=='/' else en.lstrip('/')+'.html')).read_text()
 return re.search(r'<meta name="robots" content="([^"]+)"',h).group(1)
def button(service='',city='',label='Demander un devis'):
 q={k:v for k,v in [('service',service),('city',city)] if v}
 return f'<a class="button" href="/demande-de-devis{esc("?"+urlencode(q)) if q else ""}">{esc(label)} <span aria-hidden="true">↗</span></a>'
def links(items,cls='linkrows'):
 return '<div class="'+cls+'">'+''.join(f'<a href="{esc(url)}">{esc(label)} <span aria-hidden="true">↗</span></a>' for url,label in items)+'</div>'
def section(eyebrow,title,body):return f'<section class="section wrap"><p class="eyebrow">{esc(eyebrow)}</p><h2>{esc(title)}</h2>{body}</section>'
def page(en,title,description,body):
 fr=route_map[en]; robots=policy(en)
 category,category_name=('/fr/produits','Produits') if en.startswith('/products') else ('/fr/secteurs','Secteurs') if en.startswith('/industries') else ('/fr/services','Services') if en.startswith('/services') else ('/fr/regions','Régions') if en.startswith('/locations') else ('/fr/ressources','Ressources') if en.startswith('/resources') else ('/fr/solutions-entreprises','Solutions pour entreprises') if en.startswith('/business-solutions') else ('/services-de-nettoyage','Superclean')
 schema=[{'@context':'https://schema.org','@type':'Organization','@id':'https://superclean.ca/#organization','name':'Superclean Canada Inc.','url':'https://superclean.ca','telephone':'+18338778737','email':'get@superclean.ca'},{'@context':'https://schema.org','@type':'WebPage','name':title,'url':'https://superclean.ca'+fr,'inLanguage':'fr-CA'}]
 content=f'''<!doctype html><html lang="fr-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{esc(title)} | Superclean Canada</title><meta name="description" content="{esc(description)}"><meta name="robots" content="{esc(robots)}"><link rel="canonical" href="https://superclean.ca{fr}"><link rel="alternate" hreflang="en-CA" href="https://superclean.ca{en}"><link rel="alternate" hreflang="fr-CA" href="https://superclean.ca{fr}"><meta property="og:title" content="{esc(title)} | Superclean Canada"><meta property="og:description" content="{esc(description)}"><meta property="og:type" content="website"><meta property="og:locale" content="fr_CA"><meta property="og:url" content="https://superclean.ca{fr}"><meta property="og:image" content="https://superclean.ca/assets/social-card.png"><meta name="twitter:card" content="summary_large_image"><meta name="theme-color" content="#1D3450"><link rel="icon" href="/assets/original-favicon.svg" type="image/svg+xml"><link rel="preload" href="/assets/dm-sans.ttf" as="font" type="font/ttf" crossorigin><link rel="stylesheet" href="/assets/site.css?v={css}"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script><script src="/assets/measurement.js" defer></script><script src="/assets/site.js?v={js}" defer></script></head><body>
<a class="skip" href="#main">Aller au contenu</a><div class="utility"><div class="wrap"><span>SUPERCLEAN CANADA INC.</span><a href="tel:+18338778737">Parlons-en <span class="phone">(833) 877-8737</span> ↗</a></div></div>
<header class="header wrap"><a class="wordmark" href="/services-de-nettoyage" aria-label="Accueil Superclean"><img src="/assets/original-logo.png" width="1680" height="280" alt="Superclean"></a><button class="menu-toggle" aria-expanded="false" aria-controls="main-nav">Menu <span>☰</span></button><nav id="main-nav" aria-label="Navigation principale"><a class="language-switch" lang="en-CA" hreflang="en-CA" href="{en}">English</a><a href="/fr/services">Services</a><a href="/fr/regions">Régions</a><a href="/fr/produits">Produits</a><a href="/fr/secteurs">Secteurs</a>{button()}</nav></header>
<nav class="breadcrumbs wrap" aria-label="Fil d’Ariane"><a href="/services-de-nettoyage">Accueil</a><span aria-hidden="true">/</span><a href="{category}">{category_name}</a><span aria-hidden="true">/</span><span>{esc(title)}</span></nav><main id="main">{body}</main>
<section class="cta"><div class="wrap"><div><p class="eyebrow">PARLONS DE VOS BESOINS</p><h2>Un devis adapté<br>à votre établissement.</h2></div>{button()}</div></section>
<footer class="wrap"><div class="footer-top"><div><a class="wordmark" href="/services-de-nettoyage"><img src="/assets/original-logo.png" width="1680" height="280" alt="Superclean"></a><p>Nettoyage commercial, services spécialisés<br>et fournitures pour vos locaux.</p><a href="tel:+18338778737">(833) 877-8737 ↗</a><br><a href="mailto:get@superclean.ca">get@superclean.ca ↗</a></div><div><h3>Découvrir</h3><a href="/fr/services">Services</a><a href="/fr/regions">Régions</a><a href="/fr/produits">Produits</a><a href="/fr/secteurs">Secteurs</a><a href="/demande-de-devis">Demander un devis</a></div><div><h3>Autres renseignements</h3><a href="/fr/a-propos">À propos</a><a href="/fr/references-de-projets">Références de projets</a><a href="/fr/securite-et-conformite">Sécurité</a><a href="/fr/ressources">Ressources</a><a href="/fr/solutions-entreprises">Solutions pour entreprises</a></div><div><h3>Votre établissement</h3><p>La disponibilité, la méthode et le calendrier sont confirmés pour chaque adresse.</p></div></div><div class="footer-bottom"><span>© 2026 Superclean Canada Inc.</span><div><a href="/fr/confidentialite">Confidentialité</a><a href="/fr/conditions">Conditions</a><a href="/fr/preferences-de-communication">Préférences de communication</a></div></div></footer><div class="mobile-contact" aria-label="Contact rapide"><a href="tel:+18338778737">Appeler Superclean</a><a href="/demande-de-devis">Demander un devis ↗</a></div></body></html>'''
 dest=P/(fr.lstrip('/')+'.html');dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(content)
 # Equivalent EN page links directly to its French counterpart.
 old=P/('index.html' if en=='/' else en.lstrip('/')+'.html');s=old.read_text();s=re.sub(r'<link rel="alternate" hreflang="(?:en-CA|fr-CA)"[^>]*>','',s)
 s=s.replace('</head>',f'<link rel="alternate" hreflang="en-CA" href="https://superclean.ca{en}"><link rel="alternate" hreflang="fr-CA" href="https://superclean.ca{fr}"></head>')
 s=re.sub(r'(<a class="language-switch"[^>]*href=")[^"]+',lambda m:m[1]+fr,s);old.write_text(s)
def intro(title,desc,service='',city='',en=None):
 figure=''
 if en:
  h=(P/('index.html' if en=='/' else en.lstrip('/')+'.html')).read_text();hero=re.search(r'<section class="page-intro.*?</section>',h,re.S)
  f=re.search(r'<figure.*?</figure>',hero.group(),re.S) if hero else None
  if f:
   figure=f.group();figure=re.sub(r'alt="[^"]*"','alt="'+esc(service or title)+'"',figure)
   figure=figure.replace('Reference photo (cropped)','Photo illustrative (recadrée)').replace('Public domain','Domaine public').replace('Reference photo','Photo illustrative').replace('Service reference image','Illustration du service').replace('Service reference photo','Illustration du service').replace('resized/cropped','redimensionnée et recadrée').replace('Photo:','Photo :')
 return f'<section class="page-intro wrap{ " split" if figure else ""}"><div><p class="eyebrow">SUPERCLEAN CANADA</p><h1>{esc(title)}</h1><p class="lede">{esc(desc)}</p>{button(service,city)}</div>{figure}</section>'
def service_body(en,key,city=None,special=None):
 s=services[key];c=cities.get(city);name=c['name'] if c else '';title=(special or s['title'])+(f' à {name}' if c else '')
 desc=s['desc']+(f' Pour votre établissement à {name}, la méthode et la disponibilité sont confirmées selon l’adresse et les besoins.' if c else '')
 body=intro(title,desc,special or s['title'],name,en)
 body+=section('PORTÉE DU SERVICE','Définir les travaux à réaliser.',f'<div class="two-col"><div><h3>Points à préciser</h3><ul>'+''.join('<li>'+esc(x)+'</li>' for x in s['scope'])+'</ul></div><div><h3>À évaluer séparément</h3><p>'+esc(s['caution'])+'</p><p>Votre devis écrit précise les tâches incluses, les exclusions et les responsabilités.</p></div></div>')
 if c:body+=section('VOTRE ÉTABLISSEMENT',f'Préparer l’intervention à {name}.',f'<div class="two-col"><div><h3>Accès et exploitation</h3><p>{esc(c["access"])}</p></div><div><h3>Planification saisonnière</h3><p>{esc(c["season"])}</p></div></div>')
 if special=='Nettoyage de nuit':body+=section('ACCÈS APRÈS LES HEURES D’OUVERTURE','Convenir de l’entrée et de la fermeture.','<p>Précisez l’heure de départ du personnel, la réouverture, les consignes d’alarme et la personne autorisant l’entrée. Identifiez les locaux occupés et les tâches incompatibles avec le travail de nuit. L’horaire et les responsabilités de fermeture sont convenus avant les travaux.</p>')
 body+=section('PRÉPARER VOTRE DEVIS','Les renseignements qui changent le plan.',f'<p class="large">{esc(s["requirements"])}</p><p>Ajoutez l’adresse complète{esc(" à "+name) if c else ""}, les dates souhaitées et les coordonnées du responsable sur place. Les accès, les qualifications requises et les documents attendus sont examinés avant de convenir des travaux.</p>{button(special or s["title"],name)}')
 body+=section('QUESTIONS PRATIQUES','Avant de planifier les travaux.',f'<div class="faqs"><details><summary>Quels éléments influencent le devis?</summary><p>{esc(s["requirements"])} La superficie, l’état, l’accès et les tâches retenues déterminent la portée du travail.</p></details><details><summary>Les travaux connexes sont-ils inclus?</summary><p>{esc(s["caution"])}</p></details><details><summary>Puis-je faire une demande pour plusieurs adresses?</summary><p>Oui. Prévoyez une liste de tâches, un contact et un créneau d’accès pour chaque propriété. La disponibilité et les modalités sont confirmées séparément pour chaque site.</p></details></div>')
 if c:body+=section('PLANIFIER LES TRAVAUX','Services et renseignements connexes.',links([(route_map['/services/'+key],s['title']),(route_map['/locations/'+c['region']+'/'+city],f'Nettoyage à {name}'),('/fr/services','Tous les services')]))
 else:
  routes=[(route_map['/services/'+key+'/'+k],c['name']) for k,c in cities.items() if '/services/'+key+'/'+k in route_map]
  body+=section('CHOISIR UN EMPLACEMENT','Votre service, votre ville.',links(routes)+finder(key))
 return title,desc,body
# Build French city choices from the existing market list, keeping original service area scope.
source=(P/'locations.html').read_text()
select=re.search(r'<select[^>]+name="city".*?</select>',source,re.S).group()
province_names={'British Columbia':'Colombie-Britannique','Quebec':'Québec','Nova Scotia':'Nouvelle-Écosse','New Brunswick':'Nouveau-Brunswick','Prince Edward Island':'Île-du-Prince-Édouard','Newfoundland and Labrador':'Terre-Neuve-et-Labrador','Northwest Territories':'Territoires du Nord-Ouest'}
select=select.replace('Choose your city','Choisissez une ville').replace('Québec City','Québec').replace('Greater Sudbury','Grand Sudbury')
for a,b in province_names.items():select=select.replace(a,b)
def finder(key=None):
 options=''.join(f'<option value="{esc(s["title"])}">{esc(s["title"])}</option>' for s in services.values())
 field=f'<input type="hidden" name="service" value="{esc(services[key]["title"])}">' if key else '<label>Service<select name="service" required><option value="">Choisissez un service</option>'+options+'</select></label>'
 routes={s['title']:{cities[c]['name']:route_map['/services/'+k+'/'+c] for c in cities if '/services/'+k+'/'+c in route_map} for k,s in services.items() if key is None or k==key}
 return f'<form class="city-finder" action="/demande-de-devis" data-local-routes="{esc(json.dumps(routes,ensure_ascii=False))}">{field}<label>Ville / municipalité{select}</label><button class="button" type="submit">Demander un devis ↗</button><button class="text-link local-service-link" type="button" hidden>Voir le service dans cette ville</button><p>La disponibilité et le calendrier sont confirmés pour votre adresse et votre service.</p></form>'
for key in services:
 en='/services/'+key;page(en,*service_body(en,key))
 for city in cities:
  en='/services/'+key+'/'+city
  if en in route_map:page(en,*service_body(en,key,city))
for alias,(key,city,special) in aliases.items():
 en='/services/'+alias;page(en,*service_body(en,key,city,special))
# Full French service directory.
body=intro('Services de nettoyage commercial','Entretien régulier, nettoyage spécialisé et services techniques pour vos établissements au Canada.')
body+='<div class="wrap"><label for="service-search">Trouver un service</label><input id="service-search" type="search" placeholder="Ex. : tapis, vitres, puisards" aria-describedby="search-status"><p id="search-status" role="status" aria-live="polite"></p></div><div id="service-directory">'
groups=[('Entretien des installations',list(services)[:10]),('Entretien extérieur et bâtiments',list(services)[10:20]),('Nettoyage spécialisé',list(services)[20:25]),('Services techniques et environnementaux',list(services)[25:])]
for title,keys in groups:body+=section('NOS SERVICES',title,'<div class="service-list">'+''.join(f'<a class="service-item" href="{route_map["/services/"+k]}">{esc(services[k]["title"])} <span aria-hidden="true">↗</span></a>' for k in keys)+'</div>')
body+='</div>'+section('VOTRE ÉTABLISSEMENT','Choisissez un service et une ville.',finder())
page('/services','Services de nettoyage commercial','Explorez les 52 catégories de services de Superclean et préparez votre demande de devis en français.',body)
# Province and territory pages, preserving their existing child guides.
for key,r in regions.items():
 en='/locations/'+key
 title='Services de nettoyage — '+r['name'];desc='Nettoyage commercial et services spécialisés : '+r['name']+'. Disponibilité et calendrier confirmés pour chaque adresse.'
 body=intro(title,desc,city=r['name'])
 body+=section('PLANIFICATION RÉGIONALE','Un mandat précis pour chaque adresse.',f'<p class="large">{esc(r["note"])}</p><p>Indiquez la municipalité, le code postal, le type de bâtiment et l’horaire souhaité. Pour plusieurs propriétés, joignez une liste distincte des tâches par adresse.</p><p>Les déplacements, l’accès aux équipements et les besoins spécialisés peuvent influencer la disponibilité. Aucun bureau local ni délai d’intervention n’est présumé.</p>')
 guides=[(route_map['/locations/'+key+'/'+k],c['name']) for k,c in cities.items() if c['region']==key]
 if guides:body+=section('GUIDES LOCAUX','Préparer votre demande dans votre ville.',links(guides))
 body+=section('AVANT LES TRAVAUX','Les points à confirmer.','<ul><li>Services disponibles pour la propriété exacte</li><li>Accès, déplacements et mobilisation</li><li>Consignes de sécurité et qualifications requises</li><li>Tâches incluses et créneau d’intervention</li></ul>')+section('DEMANDER UN DEVIS','Votre service et votre municipalité.',finder())
 page(en,title,desc,body)
for key,c in cities.items():
 en='/locations/'+c['region']+'/'+key;title='Nettoyage commercial à '+c['name'];desc='Services de nettoyage pour votre établissement à '+c['name']+'. Précisez les tâches, les accès et les dates souhaitées.'
 body=intro(title,desc,city=c['name'])
 body+=section('VOTRE PROPRIÉTÉ','Planifier selon vos locaux.',f'<div class="two-col"><div><h3>Accès et exploitation</h3><p>{esc(c["access"])}</p></div><div><h3>Conditions saisonnières</h3><p>{esc(c["season"])}</p></div></div>')
 local=[(route_map['/services/'+k+'/'+key],s['title']) for k,s in services.items() if '/services/'+k+'/'+key in route_map]
 local += [(route_map['/services/'+a],special) for a,(_,city,special) in aliases.items() if city==key]
 if local:body+=section('SERVICES DANS VOTRE VILLE','Choisir les travaux à prévoir.',links(local,'service-list'))
 body+=section('COORDINATION','Confirmer le plan pour votre adresse.','<div class="two-col"><div><h3>Un établissement ou plusieurs</h3><p>Indiquez une adresse, une superficie, un responsable et une liste de tâches pour chaque site. Les besoins des occupants et les restrictions d’accès sont examinés avant de convenir du mandat.</p></div><div><h3>Dates et documents</h3><p>Précisez votre échéance et les documents requis : assurance, qualifications, méthode ou références de projets. Le calendrier et les exigences propres aux travaux sont confirmés après examen.</p></div></div>')
 body+=section('VOTRE DEMANDE','Préparer les renseignements utiles.',f'<p>Joignez l’adresse complète à {esc(c["name"])}, le type de bâtiment, les superficies, les horaires d’accès et les tâches souhaitées. Des photos et votre liste d’entretien actuelle permettent de mieux définir les besoins.</p>{button(city=c["name"])}')
 body+=section('POUR ALLER PLUS LOIN','Explorer les services et la région.',links([('/fr/services','Tous les services'),(route_map['/locations/'+c['region']],regions[c['region']]['name'])]))
 page(en,title,desc,body)
body=intro('Nettoyage commercial au Canada','Commencez par votre adresse. Les besoins, la disponibilité et les modalités d’intervention sont évalués pour chaque établissement.')
body+=section('PROVINCES ET TERRITOIRES','Trouvez votre région.',links([(route_map['/locations/'+k],r['name']) for k,r in regions.items()],'service-list'))
body+=section('GUIDES LOCAUX','Les détails propres à votre ville.',links([(route_map['/locations/'+c['region']+'/'+k],c['name']) for k,c in cities.items()],'service-list'))
body+=section('VOTRE SERVICE, VOTRE VILLE','Préparez votre demande.',finder())
# Existing full market list, translated, keeps all other municipalities accessible as inquiries.
market_body='<label for="city-search">Rechercher une ville ou une province</label><input id="city-search" type="search" placeholder="Ex. : Montréal, Québec, Ottawa" aria-describedby="city-status"><p id="city-status" role="status" aria-live="polite"></p>'
for group,options in re.findall(r'<optgroup label="([^"]+)"[^>]*>(.*?)</optgroup>',select,re.S):
 items=[]
 for value,name in re.findall(r'<option value="([^"]+)"[^>]*>([^<]+)</option>',options):
  name=html.unescape(name);city_key=next((k for k,c in cities.items() if c['name']==name),None)
  dest=route_map['/locations/'+cities[city_key]['region']+'/'+city_key] if city_key else '/demande-de-devis?'+urlencode({'city':name})
  items.append(f'<a class="market-link" href="{esc(dest)}">{esc(name)} ↗</a>')
 market_body+=f'<div class="market-group"><h3>{esc(html.unescape(group))}</h3><div class="market-links">'+''.join(items)+'</div></div>'
body+=section('AUTRES MUNICIPALITÉS','Trouvez votre municipalité.',market_body)
page('/locations','Services de nettoyage par région','Trouvez les régions, villes et services de Superclean au Canada. Faites une demande de devis en français.',body)
# Update the French entry and quote pages so the core journey stays in French.
for name in ['services-de-nettoyage','demande-de-devis']:
 p=P/(name+'.html');s=p.read_text()
 for a,b in sorted(route_map.items(),key=lambda x:-len(x[0])):s=s.replace('href="'+a+'"','href="'+b+'"')
 s=s.replace('href="/"','href="/services-de-nettoyage"')
 s=re.sub(r'<nav id="main-nav".*?</nav>', '<nav id="main-nav" aria-label="Navigation principale"><a class="language-switch" lang="en-CA" hreflang="en-CA" href="/">English</a><a href="/fr/services">Services</a><a href="/fr/regions">Régions</a><a href="/fr/produits">Produits</a><a href="/fr/secteurs">Secteurs</a><a class="button" href="/demande-de-devis">Demander un devis ↗</a></nav>',s,flags=re.S)

 s=s.replace('Entretien de bureaux — détails en anglais','Entretien de bureaux').replace('Consulter les services en anglais','Consulter tous les services')
 # English equivalent is intentional, even though the French home points to the overview.
 target='/contact' if name=='demande-de-devis' else '/'
 s=re.sub(r'(<a class="language-switch"[^>]*href=")[^"]+',lambda m:m[1]+target,s)
 s=re.sub(r'(<a[^>]*href="/(?:products|industries|about|case-studies|safety|resources|business-solutions|privacy|terms|consent)"[^>]*>)([^<]+)(</a>)',lambda m:m[1]+m[2]+(' (en anglais)' if '(en anglais)' not in m[2] else '')+m[3],s)
 p.write_text(s)
exec(compile((ROOT/'scripts/build-french-catalogue.py').read_text(), 'build-french-catalogue.py', 'exec'))
exec(compile((ROOT/'scripts/build-french-corporate.py').read_text(), 'build-french-corporate.py', 'exec'))
# Sitemap: append only indexable French equivalents, never the noindex variants.
p=P/'sitemap.xml';s=p.read_text();s=re.sub(r'<url>\s*<loc>https://superclean.ca/fr/.*?</url>','',s,flags=re.S)
urls=''.join(f'<url><loc>https://superclean.ca{fr}</loc></url>' for en,fr in route_map.items() if policy(en).split(',')[0]=='index')
s=s.replace('</urlset>',urls+'</urlset>')
seen=set()
def unique_url(m):
 loc=re.search(r'<loc>(.*?)</loc>',m[0]).group(1)
 if loc in seen:return ''
 seen.add(loc);return m[0]
s=re.sub(r'<url>.*?</url>',unique_url,s,flags=re.S);p.write_text(s)
(ROOT/'content/language-routes.json').write_text(json.dumps(route_map,ensure_ascii=False,indent=2)+'\n')
print(f'Built {len(route_map)} French pages, including {len(services)} service categories, {len(regions)} regions and {len(cities)} city guides.')
