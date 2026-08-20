#!/usr/bin/env python3
from pathlib import Path
import json

SITE=Path('site')
SOURCES=Path('monitor/sources.json')
LOCALES=SITE/'data/locales.json'

config=json.loads(LOCALES.read_text(encoding='utf-8'))
live=[x['code'] for x in config.get('locales',[]) if x.get('status')=='live' and x.get('code')!='pt']
data=json.loads(SOURCES.read_text(encoding='utf-8'))
changed=0

for source in data.get('sources',[]):
    pages=list(source.get('pages',[]))
    root_pages=[]
    for page in pages:
        parts=page.split('/',1)
        if len(parts)==1 and page.endswith('.html'):
            root_pages.append(page)
    for root in root_pages:
        for code in live:
            translated=f'{code}/{root}'
            if (SITE/translated).exists() and translated not in pages:
                pages.append(translated)
                changed+=1
    source['pages']=sorted(set(pages))

SOURCES.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Locale source coverage: {len(live)} translated locales live; {changed} page mappings added.')
