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
SKIP_TAGS = {'script', 'style', 'noscript', 'svg', 'code'}

WHITELIST = {
    'Guia Migrante PT', 'AIMA', 'NIF', 'NISS', 'SNS', 'SNS 24', 'CPLP', 'CLAIM',
    'Portugal', 'Portal das Finanças', 'Segurança Social', 'Diário da República',
    'Autoridade Tributária', 'IRN', 'IMT', 'DGES', 'ACT', 'CIG', 'ERSE', 'gov.pt',
}

# Conservative Portuguese-only signals. Deliberately avoid words such as
# "para", "uma", "documentos" or "pedido", which also occur in Spanish.
STRONG_PT_RE = re.compile(
    r'\b(?:não|também|vocês|você|deve|pode|foram|serão|estão|são|'
    r'informação|informações|situação|situações|habitação|renovação|ligação|ligações|'
    r'utilização|orientação|proteção|documentação|qualificação|qualificações|condições|'
    r'ferramentas|trabalhador|trabalhadores|empregador|empregadores|regras|taxas|utente|'
    r'agendamento|morada|mudança|gratuita|gratuito)\b|'
    r'\b(?:em portugal|fontes oficiais|para quem é|antes de agir|mais pessoas|qualquer outra|'
    r'não pertence|no momento do pedido|prevalece a informação)\b',
    re.IGNORECASE,
)
POSTAL_RE = re.compile(r'\b\d{4}-\d{3}\b')


def norm(value: str) -> str:
    return ' '.join(value.split())


def visible_items(path: Path):
    soup = BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')
    out = []
    for node in soup.find_all(string=True):
        if isinstance(node, Comment):
            continue
        parent = node.parent
        if parent and parent.name in SKIP_TAGS:
            continue
        text = norm(str(node))
        if len(text) >= 2:
            out.append(('text', text))
    for tag in soup.find_all(True):
        for attr in ('aria-label', 'placeholder', 'title'):
            value = tag.get(attr)
            if value is not None:
                text = norm(str(value))
                if len(text) >= 2:
                    out.append((attr, text))
    return out


def source_sets(path: Path):
    by_kind = {'text': set(), 'aria-label': set(), 'placeholder': set(), 'title': set()}
    for kind, text in visible_items(path):
        by_kind.setdefault(kind, set()).add(text)
    return by_kind


def ignorable(text: str) -> bool:
    if text in WHITELIST:
        return True
    if not any(ch.isalpha() for ch in text):
        return True
    if POSTAL_RE.search(text) and not STRONG_PT_RE.search(text):
        return True
    if text.startswith(('http://', 'https://', 'mailto:')):
        return True
    return False


def classify_residue(kind: str, text: str, source_values: dict[str, set[str]]):
    if ignorable(text):
        return None
    if text in source_values.get(kind, set()):
        return 'exact-source-match'
    if len(text) >= 10 and STRONG_PT_RE.search(text):
        return 'strong-portuguese-signal'
    return None


problems = []
report = {'version': 3, 'strict_when_live': True, 'method': 'exact-source-match+conservative-pt-signals', 'locales': {}}

for loc in TARGETS:
    code = loc['code']
    folder = SITE / code
    if not folder.exists():
        continue

    hits = []
    page_counts = Counter()
    kind_counts = Counter()
    reason_counts = Counter()
    files = 0
    unique = set()

    for fp in sorted(folder.glob('*.html')):
        files += 1
        source_path = SITE / fp.name
        if not source_path.exists():
            continue
        source_values = source_sets(source_path)
        for kind, text in visible_items(fp):
            reason = classify_residue(kind, text, source_values)
            if not reason:
                continue
            key = (fp.name, kind, text)
            if key in unique:
                continue
            unique.add(key)
            hits.append({'page': fp.name, 'kind': kind, 'reason': reason, 'text': text})
            page_counts[fp.name] += 1
            kind_counts[kind] += 1
            reason_counts[reason] += 1

    status = loc.get('status')
    report['locales'][code] = {
        'status': status,
        'files': files,
        'portuguese_residues': len(hits),
        'pages_with_hits': len(page_counts),
        'by_reason': dict(reason_counts),
        'by_kind': dict(kind_counts),
        'worst_pages': [{'page': page, 'hits': count} for page, count in page_counts.most_common(20)],
        'examples': hits[:120],
    }

    print(f'{code}: {len(hits)} Portuguese residue(s) across {files} files [{status}]')
    if page_counts:
        print('  reasons: ' + ', '.join(f'{k}={v}' for k, v in reason_counts.items()))
        print('  worst pages: ' + ', '.join(f'{p}={n}' for p, n in page_counts.most_common(10)))
        print('  sample residues:')
        for item in hits[:20]:
            sample = item['text'].replace('\n', ' ')
            if len(sample) > 180:
                sample = sample[:177] + '...'
            print(f"    - {item['page']} [{item['kind']}/{item['reason']}]: {sample}")

    if status == 'live' and hits:
        examples = '; '.join(f"{x['page']}: {x['text'][:100]}" for x in hits[:8])
        problems.append(f'{code}: {len(hits)} Portuguese residue(s) remain. {examples}')

REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Wrote {REPORT}')

if problems:
    print('\n'.join(problems))
    print('Translation completeness FAILED for one or more live locales.')
    sys.exit(1)

print('Translation completeness audit OK (strict for live locales; reporting only for preparing locales).')
