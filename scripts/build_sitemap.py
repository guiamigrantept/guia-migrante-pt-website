#!/usr/bin/env python3
from pathlib import Path
import json
from xml.sax.saxutils import escape

SITE=Path('site')
BASE='https://guia-migrante-pt.pages.dev'
PRIVATE_PAGES={'admin-mensagens.html','admin-estatisticas.html'}
config=json.loads((SITE/'data/locales.json').read_text(encoding='utf-8'))
locales=[x for x in config.get('locales',[]) if x.get('status')=='live']

root_pages=sorted(p.name for p in SITE.glob('*.html') if p.name!='404.html' and p.name not in PRIVATE_PAGES)

def file_for(code,page):
    return SITE/page if code=='pt' else SITE/code/page

def url_for(code,page):
    return f'{BASE}/{page}' if code=='pt' else f'{BASE}/{code}/{page}'

rows=[]
for page in root_pages:
    available=[loc for loc in locales if file_for(loc['code'],page).exists()]
    if not available:
        continue
    for current in available:
        links=[]
        for alt in available:
            links.append(f'<xhtml:link rel="alternate" hreflang="{escape(alt["hreflang"])}" href="{escape(url_for(alt["code"],page))}"/>')
        if any(x['code']=='pt' for x in available):
            links.append(f'<xhtml:link rel="alternate" hreflang="x-default" href="{escape(url_for("pt",page))}"/>')
        rows.append(f'  <url><loc>{escape(url_for(current["code"],page))}</loc>{"".join(links)}</url>')

xml='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'+'\n'.join(rows)+'\n</urlset>\n'
(SITE/'sitemap.xml').write_text(xml,encoding='utf-8')
print(f'Sitemap generated: {len(rows)} URLs across {len(locales)} live locales.')
