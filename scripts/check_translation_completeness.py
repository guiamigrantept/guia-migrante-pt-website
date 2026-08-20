#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup, Comment

SITE = Path('site')
CFG = json.loads((SITE / 'data/locales.json').read_text(encoding='utf-8'))
TARGETS = [x for x in CFG.get('locales', []) if x.get('code') not in {'pt', 'en'}]

# Strong Portuguese signals. We deliberately avoid generic words shared with
# Spanish/French and ignore proper names/acronyms handled by the whitelist.
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
        out.append(text)
    # Also inspect accessibility labels/placeholders, because untranslated UI can
    # otherwise be invisible to a visual-only QA pass.
    for tag in soup.find_all(True):
        for attr in ('aria-label', 'placeholder', 'title'):
            value = tag.get(attr)
            if value:
                text = ' '.join(str(value).split())
                if len(text) >= 10 and text not in WHITELIST:
                    out.append(text)
    return out


def suspicious(text: str) -> bool:
    return bool(PT_RE.search(text))


problems = []
summary = []
for loc in TARGETS:
    code = loc['code']
    folder = SITE / code
    if not folder.exists():
        continue
    hits = []
    files = 0
    for fp in sorted(folder.glob('*.html')):
        files += 1
        for text in visible_strings(fp):
            if suspicious(text):
                hits.append((fp.name, text))
    summary.append((code, files, len(hits), loc.get('status')))

    # Preparing locales may legitimately contain untranslated copy while work is
    # in progress. A locale marked live, however, must not ship with obvious
    # Portuguese residue.
    if loc.get('status') == 'live' and hits:
        examples = '; '.join(f'{page}: {text[:100]}' for page, text in hits[:8])
        problems.append(f'{code}: {len(hits)} Portuguese-looking text node(s) remain. {examples}')

for code, files, hits, status in summary:
    print(f'{code}: {hits} Portuguese-looking node(s) across {files} files [{status}]')

if problems:
    print('\n'.join(problems))
    print('Translation completeness FAILED for one or more live locales.')
    sys.exit(1)

print('Translation completeness audit OK (strict for live locales; reporting only for preparing locales).')
