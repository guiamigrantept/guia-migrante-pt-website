#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
DATA=SITE/'data'
problems=[]

for required in [
    SITE/'contact-form.js',SITE/'contact-form.css',SITE/'admin-mensagens.html',
    ROOT/'functions/api/contact.js',ROOT/'functions/api/admin/messages.js',
    DATA/'contact-copy-pt.json'
]:
    if not required.exists(): problems.append(f'missing contact-channel asset: {required}')

for js in [SITE/'contact-form.js',ROOT/'functions/api/contact.js',ROOT/'functions/api/admin/messages.js']:
    if js.exists():
        r=subprocess.run(['node','--check',str(js)],capture_output=True,text=True)
        if r.returncode: problems.append(f'{js}: JavaScript syntax error: {r.stderr.strip()}')

cfg=json.loads((DATA/'locales.json').read_text(encoding='utf-8'))
live=[x['code'] for x in cfg.get('locales',[]) if x.get('status')=='live']
for code in live:
    page=SITE/'contactos.html' if code=='pt' else SITE/code/'contactos.html'
    if not page.exists():
        problems.append(f'{code}: missing contactos.html')
        continue
    soup=BeautifulSoup(page.read_text(encoding='utf-8'),'html.parser')
    css=[x.get('href') for x in soup.find_all('link',attrs={'data-contact-channel-asset':True})]
    js=[x.get('src') for x in soup.find_all('script',attrs={'data-contact-channel-asset':True})]
    if '/contact-form.css' not in css: problems.append(f'{code}: contact form stylesheet not injected')
    if '/contact-form.js' not in js: problems.append(f'{code}: contact form runtime not injected')
    copy=DATA/f'contact-copy-{code}.json'
    if not copy.exists():
        problems.append(f'{code}: missing localized contact copy')
    else:
        try:
            payload=json.loads(copy.read_text(encoding='utf-8'))
            for key in ['title','lead','privacy','consent','submit','success','topics']:
                if not payload.get(key): problems.append(f'{code}: contact copy missing {key}')
            if len(payload.get('topics',[]))<5: problems.append(f'{code}: contact topic list incomplete')
        except Exception as exc:
            problems.append(f'{code}: invalid contact copy ({exc})')

admin=SITE/'admin-mensagens.html'
if admin.exists():
    soup=BeautifulSoup(admin.read_text(encoding='utf-8'),'html.parser')
    robots=soup.find('meta',attrs={'name':'robots'})
    if not robots or 'noindex' not in (robots.get('content') or '').lower(): problems.append('admin-mensagens.html: missing noindex')

sitemap_script=(ROOT/'scripts/build_sitemap.py').read_text(encoding='utf-8')
if 'admin-mensagens.html' not in sitemap_script: problems.append('build_sitemap.py does not explicitly exclude admin inbox')
robots=(SITE/'robots.txt').read_text(encoding='utf-8')
if 'Disallow: /admin-mensagens.html' not in robots: problems.append('robots.txt does not disallow admin inbox')

if problems:
    print('\n'.join(problems[:200]))
    sys.exit(1)
print(f'Contact channel QA OK — public form + D1 API + protected admin inbox across {len(live)} live locales.')
