#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[1]
SITE=ROOT/'site'
DATA=SITE/'data'
ASSET_VERSION='20260824-2'


def file_for(code):
    return SITE/'contactos.html' if code=='pt' else SITE/code/'contactos.html'


def main():
    cfg=json.loads((DATA/'locales.json').read_text(encoding='utf-8'))
    live=[x['code'] for x in cfg.get('locales',[]) if x.get('status')=='live']
    changed=0
    for code in live:
        fp=file_for(code)
        if not fp.exists():
            raise SystemExit(f'{code}: contactos.html missing before contact-channel injection')
        soup=BeautifulSoup(fp.read_text(encoding='utf-8'),'html.parser')
        for old in list(soup.find_all(attrs={'data-contact-channel-asset':True})):
            old.decompose()
        if soup.head is None or soup.body is None:
            raise SystemExit(f'{fp}: missing head/body')
        css=soup.new_tag('link')
        css['rel']='stylesheet';css['href']=f'/contact-form.css?v={ASSET_VERSION}';css['data-contact-channel-asset']=''
        soup.head.append(css)
        js=soup.new_tag('script')
        js['src']=f'/contact-form.js?v={ASSET_VERSION}';js['defer']='';js['data-contact-channel-asset']=''
        soup.body.append(js)
        fp.write_text(str(soup),encoding='utf-8')
        changed+=1
    print(f'Administration contact channel injected into {changed} live locale page(s).')


if __name__=='__main__':
    main()
