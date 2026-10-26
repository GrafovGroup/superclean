"""Complete the remaining bilingual routes using faithful source translations."""
corporate=json.loads((ROOT/'content/corporate-pages-fr.json').read_text())
for en,info in corporate.items():route_map[en]=info['route']
route_map['/contact']='/demande-de-devis'
for row in (ROOT/'content/corporate-fr.tsv').read_text().splitlines():
 a,b=row.split('|');add(a,b)
allowed.update(['.',',','Carl Nurmi','Axisadman','CC BY 3.0','CC BY-SA 3.0','get@superclean.ca','(833) 877-8737'])
unknown.clear()
for en,info in corporate.items():page(en,info['title'],info['description'],translated(en,info['title']))
if unknown:raise ValueError('Untranslated corporate text: '+repr(sorted(unknown)))
# Complete the French journey while keeping each English switch on its actual counterpart.
reverse={fr:en for en,fr in route_map.items()}
for p in list((P/'fr').rglob('*.html'))+[P/'services-de-nettoyage.html',P/'demande-de-devis.html']:
 route='/'+str(p.relative_to(P))[:-5]
 if route not in reverse:continue
 en=reverse[route];s=p.read_text()
 def local_link(m):
  tag=m.group()
  if 'language-switch' in tag:return re.sub(r'href="[^"]*"','href="'+en+'"',tag)
  match=re.search(r'href="([^"]*)"',tag)
  if not match:return tag
  u=urlsplit(html.unescape(match[1]))
  if not u.scheme and u.path in route_map:
   dest=route_map[u.path]+('?' + u.query if u.query else '')+('#'+u.fragment if u.fragment else '')
   tag=tag[:match.start(1)]+esc(dest)+tag[match.end(1):]
   tag=tag.replace(' lang="en-CA"','')
  return tag
 s=re.sub(r'<a\b[^>]*>',local_link,s)
 s=s.replace(' (en anglais)','')
 s=re.sub(r'<link rel="alternate" hreflang="(?:en-CA|fr-CA)"[^>]*>','',s)
 s=s.replace('</head>',f'<link rel="alternate" hreflang="en-CA" href="https://superclean.ca{en}"><link rel="alternate" hreflang="fr-CA" href="https://superclean.ca{route}"></head>')
 p.write_text(s)
print('Completed French homepage, corporate pages, resources, policies and error page.')
