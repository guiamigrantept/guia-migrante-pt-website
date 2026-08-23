#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path

from auto_translate_untranslated_copy import translate_batch

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
DATA = SITE / 'data'
SOURCE = DATA / 'contact-copy-pt.json'
SKIP_KEYS = {'value'}


def collect_strings(value, key=''):
    out=[]
    if isinstance(value, dict):
        for k,v in value.items():
            out.extend(collect_strings(v,k))
    elif isinstance(value, list):
        for item in value:
            out.extend(collect_strings(item,key))
    elif isinstance(value, str):
        text=value.strip()
        if key in SKIP_KEYS or not text or not any(ch.isalpha() for ch in text):
            return out
        out.append(value)
    return out


def apply(value, translations, key=''):
    if isinstance(value, dict):
        return {k:apply(v,translations,k) for k,v in value.items()}
    if isinstance(value, list):
        return [apply(v,translations,key) for v in value]
    if isinstance(value, str) and key not in SKIP_KEYS:
        return translations.get(value,value)
    return value


def main():
    source=json.loads(SOURCE.read_text(encoding='utf-8'))
    cfg=json.loads((DATA/'locales.json').read_text(encoding='utf-8'))
    live=[x['code'] for x in cfg.get('locales',[]) if x.get('status')=='live']
    strings=sorted(set(collect_strings(source)),key=lambda x:(len(x),x))
    for code in live:
        target=DATA/f'contact-copy-{code}.json'
        if code=='pt':
            payload=source
        else:
            translated={}
            for start in range(0,len(strings),30):
                batch=strings[start:start+30]
                translated.update(translate_batch(batch,code))
            payload=apply(copy.deepcopy(source),translated)
        target.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'Generated contact copy: {target}')


if __name__=='__main__':
    main()
