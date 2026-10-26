"""Executed by build-french.py with its shared page helpers and route map."""
from html.parser import HTMLParser
from urllib.parse import urlsplit, parse_qsl
products={};industries={};phrases={};allowed=set();image_titles={}
def plain(s):return html.unescape(re.sub('<[^>]+>','',s)).strip()
def add(a,b):
 a=plain(a);phrases[a]=b;phrases[a.upper()]=b.upper();allowed.add(b);allowed.add(b.upper())
def main_source(en):return re.search(r'<main[^>]*>(.*?)</main>',(P/('index.html' if en=='/' else en.lstrip('/')+'.html')).read_text(),re.S).group(1)
for line in (ROOT/'content/products-fr.tsv').read_text().splitlines():
 key,title,desc,bullets,note=line.split('|');products[key]={'title':title,'desc':desc,'bullets':bullets.split(';'),'note':note}
 en='/products/'+key;route_map[en]='/fr/produits/'+slug(title);m=main_source(en)
 for src in re.findall(r'<img[^>]+src="([^"]+)"',m):image_titles[src]=title
 add(re.search(r'<h1[^>]*>(.*?)</h1>',m,re.S).group(1),title)
 add(re.search(r'<p class="lede">(.*?)</p>',m,re.S).group(1),desc)
 lis=re.findall('<li>(.*?)</li>',re.search('<ul[^>]*>(.*?)</ul>',m,re.S).group(1),re.S)
 assert len(lis)==len(bullets.split(';')),key
 for a,b in zip(lis,bullets.split(';')):add(a,b)
 add(re.search(r'<h3>Before you order</h3><p>(.*?)</p>',m,re.S).group(1),note)
 models=re.search(r'<ul class="model-list">(.*?)</ul>',m,re.S)
 if models:allowed.update(plain(x) for x in re.findall('<li>(.*?)</li>',models.group(1),re.S))
for line in (ROOT/'content/industries-fr.tsv').read_text().splitlines():
 key,title,headline,desc,bullets=line.split('|');industries[key]={'title':title,'headline':headline,'desc':desc,'bullets':bullets.split(';')}
 en='/industries/'+key;route_map[en]='/fr/secteurs/'+slug(title);m=main_source(en)
 eyebrow=re.search('<p class="eyebrow">(.*?)</p>',m,re.S).group(1);add(eyebrow,title)
 add(re.search('<p class="lede">(.*?)</p>',m,re.S).group(1),desc)
 lis=re.findall('<li>(.*?)</li>',re.search('<ul[^>]*>(.*?)</ul>',m,re.S).group(1),re.S)
 for a,b in zip(lis,bullets.split(';')):add(a,b)
 q=re.search(r'<summary>What information should I send\?</summary><p>(.*?)</p>',m,re.S)
 add(q.group(1),'Indiquez votre adresse, la superficie et les heures d’exploitation, ainsi que les priorités suivantes : '+', '.join(b[0].lower()+b[1:] for b in bullets.split(';'))+'. Des photos et votre liste d’entretien actuelle peuvent être utiles.')
 # Text within the existing SVG is translated too, with compact labels to preserve the layout.
 svg=P/'assets'/('industry-'+key+'.svg');out=P/'assets'/('industry-'+key+'-fr.svg');s=svg.read_text();local={'SCOPE AT A GLANCE':'LES POINTS ESSENTIELS',plain(eyebrow).upper():title.upper()}
 for a,b in zip(lis,bullets.split(';')):local[plain(a)]=b
 local.update({'Class and event turnover':'Entre les cours et événements','Guest and kitchen separation':'Séparation clients / cuisine','Machinery isolation':'Isolation des machines','Height and equipment clearance':'Hauteurs et dégagements','Dust and waste characterization':'Caractérisation des poussières','Workstation privacy':'Confidentialité des postes','Tenant and landlord boundaries':'Responsabilités de chaque partie','Public access and safeguarding':'Accès et protection du public'})
 s=re.sub(r'(<text\b[^>]*>)([^<]*)(</text>)',lambda m:m[1]+esc(local.get(html.unescape(m[2]),html.unescape(m[2])))+m[3],s)
 s=s.replace('font-size="18"','font-size="16"').replace('font-size="13" letter-spacing="2"','font-size="12" letter-spacing="1"');out.write_text(s)
route_map['/products']='/fr/produits';route_map['/industries']='/fr/secteurs'
common={
'PRODUCT CATALOGUE / WASHROOM ESSENTIALS':'CATALOGUE / ESSENTIELS SANITAIRES',
'Washroom essentials':'Essentiels sanitaires','Cleaning supplies':'Fournitures de nettoyage','Entrance & footwear care':'Entrées et entretien des chaussures','Floor safety & spill control':'Signalisation et gestion des déversements','Waste & recycling':'Déchets et recyclage','Property equipment':'Équipements pour les propriétés','Surface-care products':'Produits d’entretien des surfaces','For cleaning businesses':'Pour les entreprises de nettoyage',
'PRODUCTS':'PRODUITS','Facility supplies':'Fournitures','and equipment.':'et équipements pour vos locaux.',
'Find products for your washrooms, entrances and cleaning operation. Compare catalogue options and request a specification for your order.':'Trouvez des produits pour vos salles de toilettes, vos entrées et vos activités d’entretien. Comparez les options du catalogue et demandez les caractéristiques des articles souhaités.',
'Product categories':'Catégories de produits','PRODUCT CATEGORY':'CATÉGORIE DE PRODUITS','PRODUCT SELECTION':'CHOIX DU PRODUIT','Match the product to the job.':'Choisir un produit adapté à l’usage.','Details to compare':'Points à comparer','Before you order':'Avant de commander',
'Send your quantity, delivery postal code and preferred timing. Your quote will confirm the exact product, current availability and delivery options.':'Indiquez la quantité, le code postal de livraison et le délai souhaité. Le devis précisera le produit exact, sa disponibilité et les options de livraison.',
'YOUR PRODUCT QUOTE':'VOTRE DEVIS PRODUIT','Get a specification you can approve.':'Des caractéristiques à vérifier avant de commander.',
'Ask for a written quote identifying the model or item, dimensions where relevant, quantity, pack format, price and delivery arrangements.':'Demandez un devis écrit précisant le modèle ou l’article, les dimensions pertinentes, la quantité, le conditionnement, le prix et les modalités de livraison.',
'For replacements, include a photo of the existing unit and its model or refill code.':'Pour un remplacement, joignez une photo de l’unité existante et son code de modèle ou de recharge.',
'Request a product quote':'Demander un devis produit','Request a quote':'Demander un devis','RELATED PRODUCTS':'PRODUITS CONNEXES','View the full product catalogue':'Voir tout le catalogue',
'CATALOGUE RANGE':'GAMME DU CATALOGUE','Explore the range.':'Découvrez la gamme.',
'Ask about current availability, configurations and compatible consumables for these models.':'Renseignez-vous sur la disponibilité, les configurations et les consommables compatibles avec ces modèles.',
'Superclean product catalogue. Confirm the model and specification with your quote.':'Catalogue Superclean. Confirmez le modèle et ses caractéristiques dans votre devis.',
'Frost push-button dispenser':'Distributeur Frost à bouton-poussoir',
'INDUSTRIES':'SECTEURS','Your environment.':'Votre environnement.','Our starting point.':'Notre point de départ.',
'Explore the operational details that shape a useful cleaning scope.':'Découvrez les besoins d’exploitation qui permettent de définir un mandat de nettoyage adapté.',
'SPACES WE DISCUSS':'VOS INSTALLATIONS','Find your facility type.':'Choisissez votre type d’établissement.',
'FACILITY PRIORITIES':'PRIORITÉS DE VOTRE ÉTABLISSEMENT','Start with how the space works.':'Comprendre le fonctionnement des lieux.',
'BUILD YOUR SCOPE':'DÉFINIR VOTRE MANDAT','Relevant services.':'Services adaptés.','PLANNING DETAILS':'PLANIFICATION','A useful first conversation.':'Bien préparer votre première demande.',
'What information should I send?':'Quels renseignements transmettre?','Can you quote for multiple sites?':'Pouvez-vous préparer un devis pour plusieurs sites?',
'List each site and the tasks needed at each address. Access, availability and scheduling are assessed individually.':'Dressez la liste des sites et des tâches requises à chaque adresse. Les accès, la disponibilité et le calendrier sont évalués individuellement.',
'Planning guide':'Guide de planification'
}
for a,b in list(common.items()):
 if a in ['Washroom essentials','Cleaning supplies','Entrance & footwear care','Floor safety & spill control','Waste & recycling','Property equipment','Surface-care products','For cleaning businesses']:
  common['PRODUCT CATALOGUE / '+a.upper()]='CATALOGUE / '+b.upper();common[a+'.']=b+'.'
for a,b in common.items():add(a,b)
for k,s in services.items():
 source=main_source('/services/'+k);add(re.search('<h1[^>]*>(.*?)</h1>',source,re.S).group(1),s['title'])
# Industry labels on the index may differ from their eyebrow.
for key,i in industries.items():
 src=(P/'assets'/('industry-'+key+'.svg')).read_text();label=re.findall(r'<text[^>]*>([^<]+)</text>',src)[-1]
 add(html.unescape(label),i['title'])
unknown=set()
def translate(t):
 stripped=t.strip()
 if not stripped or stripped in ['↗','↓','/'] or stripped.isdigit():return t
 arrow=' ↗' if stripped.endswith(' ↗') else ''
 key=stripped[:-2] if arrow else stripped
 if key in phrases:return phrases[key]+arrow
 if key in allowed:return key+arrow
 unknown.add(key);return t
class Translator(HTMLParser):
 def __init__(self,title):super().__init__(convert_charrefs=True);self.out=[];self.title=title
 def handle_starttag(self,tag,attrs):
  out=[]
  for k,v in attrs:
   if v is not None:
    if k=='href':
     u=urlsplit(v)
     if not u.scheme and u.path in route_map:v=route_map[u.path]+('?' + u.query if u.query else '')+('#'+u.fragment if u.fragment else '')
     elif u.path=='/contact':
      q=dict(parse_qsl(u.query));q={key:('Produit : '+self.title if key=='service' and val.startswith('Product:') else phrases.get(val,val)) for key,val in q.items()}
      v='/demande-de-devis'+('?' + urlencode(q) if q else '')
    elif k=='src' and '/assets/industry-' in v:v=v.replace('.svg','-fr.svg')
    elif k=='alt':v=image_titles.get(dict(attrs).get('src'),phrases.get(v,self.title))
    elif k=='aria-label':v=phrases.get(v,v)
   out.append(k if v is None else k+'="'+esc(v)+'"')
  self.out.append('<'+tag+(' '+ ' '.join(out) if out else '')+'>')
 def handle_endtag(self,tag):self.out.append('</'+tag+'>')
 def handle_data(self,data):
  value=translate(data)
  prefix=data[:len(data)-len(data.lstrip())];suffix=data[len(data.rstrip()):]
  self.out.append(esc(prefix+value.strip()+suffix) if data.strip() else data)
 def handle_comment(self,data):self.out.append('<!--'+data+'-->')
def translated(en,title,headline=None):
 m=main_source(en)
 if headline:
  m=re.sub('<h1[^>]*>.*?</h1>','<h1>'+esc(headline)+'</h1>',m,flags=re.S);allowed.add(headline)
 t=Translator(title);t.feed(m);return ''.join(t.out)
for k,p in products.items():page('/products/'+k,p['title'],p['desc'],translated('/products/'+k,p['title']))
for k,i in industries.items():page('/industries/'+k,i['title'],i['desc'],translated('/industries/'+k,i['title'],i['headline']))
page('/products','Produits et équipements pour vos locaux','Découvrez les fournitures sanitaires, produits de nettoyage et équipements de Superclean. Demandez un devis en français.',translated('/products','Produits et équipements pour vos locaux'))
page('/industries','Secteurs d’activité','Explorez nos services de nettoyage pour les bureaux, commerces, entrepôts, hôtels et autres établissements.',translated('/industries','Secteurs d’activité'))
if unknown:raise ValueError('Untranslated catalogue text: '+repr(sorted(unknown)))
# Core French pages now link to the translated catalogue and industries.
for p in list((P/'fr').rglob('*.html'))+[P/'services-de-nettoyage.html',P/'demande-de-devis.html']:
 s=p.read_text()
 for en,fr in route_map.items():
  if en.startswith(('/products','/industries')):s=s.replace('href="'+en+'"','href="'+fr+'"')
 s=re.sub(r'(<a[^>]*href="/fr/(?:produits|secteurs)[^"]*"[^>]*>)([^<]*?)(?: \(en anglais\))(</a>)',r'\1\2\3',s)
 s=re.sub(r'(<a[^>]*href="/fr/(?:produits|secteurs)[^"]*") lang="en-CA"',r'\1',s)
 p.write_text(s)
# Main generator writes the combined map and sitemap after this extension.
print('Added French product and industry counterparts: 23 categories, 7 industries, 2 directories.')
