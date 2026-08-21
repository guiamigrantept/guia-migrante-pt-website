#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path
from bs4 import BeautifulSoup, Comment

SITE = Path('site')
REPORT = SITE / 'data' / 'translation-audit.json'
CFG = json.loads((SITE / 'data/locales.json').read_text(encoding='utf-8'))
TARGETS = [x for x in CFG.get('locales', []) if x.get('code') not in {'pt', 'en'}]

PT_PATTERNS = [
    r'\b(?:não|também|você|vocês|seu|sua|seus|suas|para|com|sem|uma|umas|uns|dos|das|pela|pelo|pelos|pelas)\b',
    r'\b(?:informação|informações|situação|situações|documentos|documento|serviço|serviços|pedido|pedidos|direitos|trabalho|saúde|habitação|nacionalidade|residência|renovação|apoio|contactos|ferramentas)\b',
    r'\b(?:antes de|depois de|em portugal|no portugal|em caso de|saiba mais|verifique|consulte|confirme|atenção|importante)\b',
]
PT_RE = re.compile('|'.join(PT_PATTERNS), re.IGNORECASE)

WHITELIST = {
    'Guia Migrante PT', 'AIMA', 'NIF', 'NISS', 'SNS', 'SNS 24', 'CPLP', 'CLAIM',
    'Portugal', 'Portal das Finanças', 'Segurança Social', 'Diário da República',
    'Autoridade Tributária', 'IRN', 'IMT', 'DGES', 'ACT', 'CIG', 'ERSE',
}
SKIP_TAGS = {'script', 'style', 'noscript', 'svg', 'code'}


def visible_strings(path: Path):
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
    out = []
    for node in soup.find_all(string=True):
        if isinstance(node, Comment):
            continue
        parent = node.parent
        if parent and parent.name in SKIP_TAGS:
            continue
        text = ' '.join(str(node).split())
        if len(text) < 10 or text in WHITELIST:
            continue
        out.append(('text', text))
    for tag in soup.find_all(True):
        for attr in ('aria-label', 'placeholder', 'title'):
            value = tag.get(attr)
            if value:
                text = ' '.join(str(value).split())
                if len(text) >= 10 and text not in WHITELIST:
                    out.append((attr, text))
    return out


def suspicious(text: str) -> bool:
    return bool(PT_RE.search(text))


problems = []
report = {'version': 2, 'strict_when_live': True, 'locales': {}}

for loc in TARGETS:
    code = loc['code']
    folder = SITE / code
    if not folder.exists():
        continue

    hits = []
    page_counts = Counter()
    attr_counts = Counter()
    files = 0
    unique = set()

    for fp in sorted(folder.glob('*.html')):
        files += 1
        for kind, text in visible_strings(fp):
            if suspicious(text):
                key = (fp.name, kind, text)
                if key in unique:
                    continue
                unique.add(key)
                hits.append({'page': fp.name, 'kind': kind, 'text': text})
                page_counts[fp.name] += 1
                attr_counts[kind] += 1

    status = loc.get('status')
    report['locales'][code] = {
        'status': status,
        'files': files,
        'portuguese_looking_nodes': len(hits),
        'pages_with_hits': len(page_counts),
        'worst_pages': [
            {'page': page, 'hits': count}
            for page, count in page_counts.most_common(20)
        ],
        'by_kind': dict(attr_counts),
        'examples': hits[:120],
    }

    print(f'{code}: {len(hits)} Portuguese-looking node(s) across {files} files [{status}]')
    if page_counts:
        print('  worst pages: ' + ', '.join(f'{p}={n}' for p, n in page_counts.most_common(10)))
        print('  sample residues:')
        for item in hits[:20]:
            sample = item['text'].replace('\n', ' ')
            if len(sample) > 180:
                sample = sample[:177] + '...'
            print(f"    - {item['page']} [{item['kind']}]: {sample}")

    if status == 'live' and hits:
        examples = '; '.join(f"{x['page']}: {x['text'][:100]}" for x in hits[:8])
        problems.append(f'{code}: {len(hits)} Portuguese-looking text node(s) remain. {examples}')

REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Wrote {REPORT}')

if problems:
    print('\n'.join(problems))
    print('Translation completeness FAILED for one or more live locales.')
    sys.exit(1)

print('Translation completeness audit OK (strict for live locales; reporting only for preparing locales).')
