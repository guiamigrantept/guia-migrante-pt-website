#!/usr/bin/env python3
from pathlib import Path
import json, os, sys, subprocess
from bs4 import BeautifulSoup

site=Path('site')
base='https://guia-migrante-pt.pages.dev'
source_monitor_mode=os.getenv('QA_SOURCE_MONITOR')=='1'
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
        live_locales=[x for x in locales if x.get('status')=='live']
        live={x.get('code') for x in live_locales}
        if not {'pt','en'}.issubset(live): problems.append('data/locales.json: PT and EN must remain live')
        source_pages=[p.name for p in site.glob('*.html') if p.name!='404.html' and (site/'en'/p.name).exists()]

        def localized_file(code,name):
            return site/name if code=='pt' else site/code/name

        def localized_url(code,name):
            return f'{base}/{name}' if code=='pt' else f'{base}/{code}/{name}'

        for code in sorted(live-{'pt'}):
            folder=site/code
            if not folder.exists():
                if source_monitor_mode and code!='en':
                    continue
                problems.append(f'{code}: locale marked live but folder is missing')
                continue
            missing=[name for name in source_pages if not (folder/name).exists()]
            if missing: problems.append(f'{code}: locale marked live but missing {len(missing)} mirrored pages')

        if not source_monitor_mode:
            for loc in live_locales:
                code=loc.get('code')
                for name in source_pages:
                    fp=localized_file(code,name)
                    if not fp.exists():
                        continue
                    soup=BeautifulSoup(fp.read_text(encoding='utf-8'),'html.parser')

                    if code not in {'pt','en'}:
                        robots=soup.find('meta',attrs={'name':'robots'})
                        if robots and 'noindex' in (robots.get('content') or '').lower():
                            problems.append(f'{code}/{name}: live translation is still noindex')
                        status=soup.find('meta',attrs={'name':'translation-status'})
                        if not status or status.get('content')!='live':
                            problems.append(f'{code}/{name}: missing live translation marker')
                        if soup.select_one('.review-strip') is not None:
                            problems.append(f'{code}/{name}: staging review strip still present')

                    alternates={}
                    for link in soup.find_all('link',href=True):
                        rel=link.get('rel') or []
                        if 'alternate' in rel and link.get('hreflang'):
                            alternates[link.get('hreflang')]=link.get('href')
                    for alt in live_locales:
                        expected_href=localized_url(alt['code'],name)
                        if alternates.get(alt['hreflang'])!=expected_href:
                            problems.append(f'{code}/{name}: missing/wrong hreflang {alt["hreflang"]}')
                    if alternates.get('x-default')!=localized_url('pt',name):
                        problems.append(f'{code}/{name}: missing/wrong x-default')

                    manifests=[x for x in soup.find_all('link',href=True) if 'manifest' in (x.get('rel') or [])]
                    if len(manifests)!=1:
                        problems.append(f'{code}/{name}: expected exactly one web manifest')
                    else:
                        href=manifests[0]['href'].split('?',1)[0]
                        manifest_path=site/href.lstrip('/') if href.startswith('/') else (fp.parent/href).resolve()
                        if not manifest_path.exists():
                            problems.append(f'{code}/{name}: missing web manifest {href}')

                runtime=site/'data'/f'ux-copy-{code}.json'
                search=site/'data'/f'search-{code}.json'
                if not runtime.exists():
                    problems.append(f'{code}: missing localized runtime UX copy')
                else:
                    try:
                        payload=json.loads(runtime.read_text(encoding='utf-8'))
                        for key in ['nav','search','share','progress','home','guide']:
                            if not payload.get(key): problems.append(f'{code}: runtime UX copy missing {key}')
                    except Exception as exc:
                        problems.append(f'{code}: invalid runtime UX copy ({exc})')
                if not search.exists():
                    problems.append(f'{code}: missing localized search index')
                else:
                    try:
                        payload=json.loads(search.read_text(encoding='utf-8'))
                        items=payload.get('items',[])
                        if len(items)<max(10,len(source_pages)//2): problems.append(f'{code}: search index unexpectedly small ({len(items)} items)')
                        for item in items:
                            if not item.get('title') or not item.get('url'): problems.append(f'{code}: malformed search index item')
                    except Exception as exc:
                        problems.append(f'{code}: invalid search index ({exc})')
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
if source_monitor_mode:
    print(f'QA OK — {len(files)} repository HTML files; source-monitor mode validated PT/EN and shared assets. Generated live locales remain gated by the deploy pipeline.')
else:
    print(f'QA OK — {len(files)} HTML files; live locales complete, indexable, hreflang-aligned, PWA-linked and runtime-localized.')
