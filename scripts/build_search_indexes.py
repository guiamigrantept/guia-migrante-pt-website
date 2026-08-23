#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
DATA=SITE/'data'


def clean(text):
    return re.sub(r'\s+',' ',text or '').strip()


def file_for(code,page):
    return SITE/page if code=='pt' else SITE/code/page


def code_for(page):
    stem=Path(page).stem.replace('-',' ')
    parts=[p for p in stem.split() if p]
    if not parts:
        return '•'
    return ''.join(p[0] for p in parts[:3]).upper()


def main():
    cfg=json.loads((DATA/'locales.json').read_text(encoding='utf-8'))
    locales=[x for x in cfg.get('locales',[]) if x.get('status')=='live']
    pages=sorted(p.name for p in SITE.glob('*.html') if p.name!='404.html' and (SITE/'en'/p.name).exists())
    for loc in locales:
        code=loc['code']
        items=[]
        for page in pages:
            fp=file_for(code,page)
            if not fp.exists():
                continue
            soup=BeautifulSoup(fp.read_text(encoding='utf-8'),'html.parser')
            h1=soup.find('h1')
            title=clean(h1.get_text(' ',strip=True) if h1 else '')
            if not title and soup.title:
                title=clean(soup.title.get_text(' ',strip=True).split('|')[0])
            meta=soup.find('meta',attrs={'name':'description'})
            desc=clean(meta.get('content','') if meta else '')
            if not desc:
                first=(soup.find('main') or soup).find('p')
                desc=clean(first.get_text(' ',strip=True) if first else '')
            headings=' '.join(clean(x.get_text(' ',strip=True)) for x in soup.find_all(['h2','h3'])[:12])
            keys=clean(f'{title} {desc} {headings}')
            items.append({'code':code_for(page),'title':title or page,'text':desc,'url':page,'keys':keys})
        out={'locale':code,'items':items}
        target=DATA/f'search-{code}.json'
        target.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'{code}: search index with {len(items)} pages -> {target}')


if __name__=='__main__':
    main()
