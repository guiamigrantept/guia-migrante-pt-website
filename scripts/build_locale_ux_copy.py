#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

from auto_translate_untranslated_copy import translate_batch

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
DATA = SITE / 'data'
SOURCE = DATA / 'ux-copy-pt.json'
SKIP_KEYS = {'url', 'value', 'icon'}
PLACEHOLDER_RE = re.compile(r'\{[^{}]+\}')


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
        if key in SKIP_KEYS:
            return out
        if not text or not any(ch.isalpha() for ch in text):
            return out
        if len(text) <= 4 and text.upper() == text:
            return out
        out.append(value)
    return out


def protect(text: str):
    placeholders=[]
    def repl(match):
        placeholders.append(match.group(0))
        return f'§P{len(placeholders)-1}§'
    return PLACEHOLDER_RE.sub(repl,text),placeholders


def restore(text: str, placeholders):
    for i,p in enumerate(placeholders):
        text=text.replace(f'§P{i}§',p)
    return text


def translate_strings(strings, target):
    protected={}
    reverse={}
    for s in strings:
        p,slots=protect(s)
        protected[s]=p
        reverse[p]=slots
    unique=sorted(set(protected.values()),key=lambda x:(len(x),x))
    translated={}
    for start in range(0,len(unique),35):
        batch=unique[start:start+35]
        translated.update(translate_batch(batch,target))
    out={}
    for source,p in protected.items():
        result=translated.get(p,p)
        out[source]=restore(result,reverse[p])
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
    strings=collect_strings(source)
    for code in live:
        target=DATA/f'ux-copy-{code}.json'
        if code=='pt':
            payload=source
        else:
            mapping=translate_strings(strings,code)
            payload=apply(copy.deepcopy(source),mapping)
        target.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
        print(f'Generated runtime UX copy: {target}')


if __name__=='__main__':
    main()
