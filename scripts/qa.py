#!/usr/bin/env python3
from pathlib import Path
import json, sys, subprocess
from bs4 import BeautifulSoup

site=Path('site')
files=list(site.rglob('*.html'))
relmap={str(f.relative_to(site)).replace('\\','/'):f for f in files}
ids={}
problems=[]

for rel,f in relmap.items():
    soup=BeautifulSoup(f.read_text(encoding='utf-8'),'html.parser')
    vals=[x.get('id') for x in soup.find_all(id=True)]
    ids[rel]=set(vals)
    dup=sorted({v for v in vals if vals.count(v)>1})
    if dup: problems.append(f'{rel}: duplicate IDs {dup}')
    if f.name!='404.html':
        if len(soup.find_all('main'))!=1: problems.append(f'{rel}: expected one <main>')
        if len(soup.find_all('h1'))!=1: problems.append(f'{rel}: expected one <h1>')
    for img in soup.find_all('img'):
        if not img.has_attr('alt'): problems.append(f'{rel}: image without alt')
    for b in soup.find_all('button'):
        if not (b.get('aria-label') or b.get_text(' ',strip=True)): problems.append(f'{rel}: button without accessible name')

for rel,f in relmap.items():
    soup=BeautifulSoup(f.read_text(encoding='utf-8'),'html.parser')
    for a in soup.find_all('a',href=True):
        h=a['href']
        if h.startswith(('http://','https://','mailto:','tel:')): continue
        fp,sep,anchor=h.partition('#')
        try:
            target=rel if not fp else str(((f.parent/fp).resolve()).relative_to(site.resolve())).replace('\\','/')
        except Exception:
            problems.append(f'{rel}: bad href {h}'); continue
        if fp and fp.endswith('.html') and target not in relmap:
            problems.append(f'{rel}: missing page {h}'); continue
        if sep and anchor and target in ids and anchor not in ids[target]:
            problems.append(f'{rel}: missing anchor {h}')

for p in site.glob('*.html'):
    ep=site/'en'/p.name
    if p.name=='404.html' or not ep.exists(): continue
    pt=p.read_text(encoding='utf-8'); en=ep.read_text(encoding='utf-8')
    if f'href="en/{p.name}"' not in pt: problems.append(f'{p.name}: missing PT→EN')
    if f'href="../{p.name}"' not in en: problems.append(f'en/{p.name}: missing EN→PT')

# Multilingual rollout guard: a locale cannot be marked live until it mirrors all
# public PT pages that already have an English counterpart. This prevents a
# half-translated language from becoming selectable by mistake.
locale_file=site/'data/locales.json'
if not locale_file.exists():
    problems.append('data/locales.json: missing locale configuration')
else:
    try:
        locale_data=json.loads(locale_file.read_text(encoding='utf-8'))
        locales=locale_data.get('locales',[])
        expected={'pt','en','fr','es','uk','ru','hi','bn'}
        codes=[x.get('code') for x in locales]
        if set(codes)!=expected: problems.append(f'data/locales.json: locale set mismatch {codes}')
        if len(codes)!=len(set(codes)): problems.append('data/locales.json: duplicate locale code')
        live={x.get('code') for x in locales if x.get('status')=='live'}
        if not {'pt','en'}.issubset(live): problems.append('data/locales.json: PT and EN must remain live')
        source_pages=[p.name for p in site.glob('*.html') if p.name!='404.html' and (site/'en'/p.name).exists()]
        for code in sorted(live-{'pt'}):
            folder=site/code
            if not folder.exists():
                problems.append(f'{code}: locale marked live but folder is missing')
                continue
            missing=[name for name in source_pages if not (folder/name).exists()]
            if missing: problems.append(f'{code}: locale marked live but missing {len(missing)} mirrored pages')
    except Exception as exc:
        problems.append(f'data/locales.json: invalid JSON/configuration ({exc})')

for required in ['language-switcher.js','language-switcher.css']:
    if not (site/required).exists(): problems.append(f'{required}: missing multilingual asset')

for js in ['ux.js','ux-en.js','sw.js','ops-v12.js','source-guard.js','language-switcher.js']:
    fp=site/js
    if fp.exists():
        r=subprocess.run(['node','--check',str(fp)],capture_output=True,text=True)
        if r.returncode: problems.append(f'{js}: JS syntax error')

if problems:
    print('\n'.join(problems[:200]))
    sys.exit(1)
print(f'QA OK — {len(files)} HTML files; multilingual rollout guard active.')
