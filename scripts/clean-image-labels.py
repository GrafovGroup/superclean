"""Keep production captions off sales pages; retain photo licenses in linked credits."""
from pathlib import Path
import json,re,html
P=Path(__file__).resolve().parent.parent/'public'
credits=json.loads((P.parent/'content/image-credits.json').read_text())
for fr in [False,True]:
 route='/fr/credits-photos' if fr else '/image-credits';title='Crédits photos' if fr else 'Image credits';other='/image-credits' if fr else '/fr/credits-photos'
 source=P/('fr/conditions.html' if fr else 'terms.html');s=source.read_text()
 body='<section class="page-intro wrap"><div><h1>'+title+'</h1><p class="lede">'+('Sources, auteurs et licences des photographies utilisées sur ce site.' if fr else 'Sources, creators and licenses for photographs used on this website.')+'</p></div></section><section class="wrap section"><div class="two-col">'
 for c in credits:
  e=lambda x:html.escape(x,quote=True)
  body+='<article style="margin-bottom:32px"><img src="'+e(c['image'])+'" alt="" loading="lazy" width="240" style="width:240px;max-width:100%;height:150px;object-fit:cover"><h2 style="font-size:22px">'+e(c['author'])+'</h2><p><a href="'+e(c['source'])+'">'+('Photographie originale' if fr else 'Original photograph')+'</a> · <a href="'+e(c['licenseUrl'])+'">'+e(c['license'])+'</a></p><p>'+('Images redimensionnées et recadrées pour la mise en page.' if fr else 'Images resized and cropped for page layout.')+'</p></article>'
 body+='</div></section>'
 s=re.sub(r'<main[^>]*>.*?</main>','<main id="main">'+body+'</main>',s,flags=re.S)
 s=re.sub(r'<title>.*?</title>','<title>'+title+' | Superclean Canada</title>',s)
 s=re.sub(r'<script type="application/ld\+json">.*?</script>','',s,flags=re.S)
 s=re.sub(r'<nav class="breadcrumbs wrap".*?</nav>','',s,flags=re.S)
 s=re.sub(r'(<meta name="robots" content=")[^"]+',r'\g<1>noindex,follow',s)
 s=re.sub(r'(<meta (?:name="description"|property="og:title"|property="og:description") content=")[^"]+',lambda m:m[1]+title,s)
 s=re.sub(r'(<link rel="canonical" href=")[^"]+',lambda m:m[1]+'https://superclean.ca'+route,s)
 s=re.sub(r'(<meta property="og:url" content=")[^"]+',lambda m:m[1]+'https://superclean.ca'+route,s)
 s=re.sub(r'<link rel="alternate"[^>]*>','',s)
 s=s.replace('</head>','<link rel="alternate" hreflang="en-CA" href="https://superclean.ca/image-credits"><link rel="alternate" hreflang="fr-CA" href="https://superclean.ca/fr/credits-photos"></head>')
 s=re.sub(r'(<a class="language-switch"[^>]*href=")[^"]+',lambda m:m[1]+other,s)
 (P/(route.lstrip('/')+'.html')).write_text(s)
for p in P.rglob('*.html'):
 s=p.read_text();fr='<html lang="fr-CA"' in s
 s=re.sub(r'<p class="home-image-note">.*?</p>','',s,flags=re.S)
 def caption(m):
  return '' if re.search(r'reference (?:image|photo)|Photo illustrative|Illustration (?:du service|de nettoyage)',m[0],re.I) else m[0]
 s=re.sub(r'<figcaption\b[^>]*>.*?</figcaption>',caption,s,flags=re.S)
 if 'class="image-credits-link"' not in s:
  dest='/fr/credits-photos' if fr else '/image-credits';label='Crédits photos' if fr else 'Image credits'
  s=s.replace('</footer>','<p class="image-credits-link small"><a href="'+dest+'">'+label+'</a></p></footer>')
 p.write_text(s)
print('Removed production image labels; photo attribution retained on bilingual credits pages.')
# Keep the language switch alongside contact details, outside the main navigation.
for p in P.rglob('*.html'):
 s=p.read_text();fr='<html lang="fr-CA"' in s
 m=re.search(r'<a class="language-switch"[^>]*>.*?</a>',s,re.S)
 if not m:continue
 tag=m[0];tag=re.sub(r'>[^<]*</a>$','>'+('EN' if fr else 'FR')+'</a>',tag)
 tag=re.sub(r' aria-label="[^"]*"','',tag)
 tag=tag.replace('class="language-switch"','class="language-switch" aria-label="'+('View this page in English' if fr else 'Voir cette page en français')+'"')
 s=re.sub(r'<a class="language-switch"[^>]*>.*?</a>','',s,flags=re.S)
 s=re.sub(r'(<div class="utility"><div class="wrap">.*?)(</div></div>)',lambda x:x[1]+tag+x[2],s,count=1,flags=re.S)
 p.write_text(s)
