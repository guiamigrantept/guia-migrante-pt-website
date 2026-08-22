#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup, Comment
from langdetect import DetectorFactory, LangDetectException, detect_langs

DetectorFactory.seed = 0

SITE = Path('site')
REPORT = SITE / 'data' / 'translation-audit.json'
CFG = json.loads((SITE / 'data/locales.json').read_text(encoding='utf-8'))
TARGETS = [x for x in CFG.get('locales', []) if x.get('code') not in {'pt', 'en'}]
SKIP_TAGS = {'script', 'style', 'noscript', 'svg', 'code'}

WHITELIST = {
    'Guia Migrante PT', 'AIMA', 'NIF', 'NISS', 'SNS', 'SNS 24', 'CPLP', 'CLAIM',
    'Portugal', 'Portal das Finanças', 'Segurança Social', 'Diário da República',
    'Autoridade Tributária', 'IRN', 'IMT', 'DGES', 'ACT', 'CIG', 'ERSE', 'gov.pt',
    'EN', 'PT', 'html', 'HTML',
}

# Short expressions that are strongly Portuguese even without enough context for
# reliable statistical language detection. Avoid shared Spanish words such as
# para, portal, contactos, idioma, documentos or información/informação-like
# cognates unless they contain Portuguese-specific spelling.
DISTINCTIVE_PT_RE = re.compile(
    r'\b(?:não|também|vocês|você|deve|foram|serão|estão|são|morada|utente|'
    r'agendamento|qualquer|prevalece|ligações|utilização|orientação|proteção|'
    r'habitação|renovação|qualificações|condições|trabalhadores|empregadores)\b|'
    r'\b(?:para quem é|antes de agir|mais pessoas|não pertence|no momento do pedido)\b',
    re.IGNORECASE,
)
POSTAL_RE = re.compile(r'\b\d{4}-\d{3}\b')
EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]+$')
URLISH_RE = re.compile(r'^(?:https?://|mailto:|www\.|[\w.-]+\.(?:pt|com|org|eu))(?:\b|/)', re.I)
TECH_TOKEN_RE = re.compile(r'^(?:html?|pt|en|fr|es|uk|ru|hi|bn|aima|nif|niss|sns|cplp|claim|irn|imt|dges|act|cig|erse)(?:\s*[↗→])?$', re.I)
COPYRIGHT_RE = re.compile(r'^©\s*\d{4}\s+Guia Migrante PT\.?$', re.I)


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
    cleaned = text.strip().rstrip('↗→').strip()
    if cleaned in WHITELIST:
        return True
    if not any(ch.isalpha() for ch in text):
        return True
    if POSTAL_RE.search(text) and not DISTINCTIVE_PT_RE.search(text):
        return True
    if EMAIL_RE.match(cleaned) or URLISH_RE.match(cleaned):
        return True
    if TECH_TOKEN_RE.match(text.strip()) or COPYRIGHT_RE.match(text.strip()):
        return True
    # Common proper-name / venue fragments are not evidence of untranslated copy.
    if len(text.split()) <= 4 and ('–' in text or '-' in text) and not DISTINCTIVE_PT_RE.search(text):
        return True
    return False


def detected_portuguese(text: str) -> bool:
    # Language ID is useful only with enough lexical context. This deliberately
    # ignores short shared labels such as "Contactos" or "Portal".
    words = re.findall(r"[^\W\d_]+", text, flags=re.UNICODE)
    if len(words) < 5 or len(text) < 24:
        return False
    try:
        guesses = detect_langs(text)
    except LangDetectException:
        return False
    for guess in guesses:
        if guess.lang == 'pt' and guess.prob >= 0.80:
            return True
    return False


def meaningful_portuguese(text: str) -> bool:
    if ignorable(text):
        return False
    if DISTINCTIVE_PT_RE.search(text):
        return True
    return detected_portuguese(text)


def classify_residue(kind: str, text: str, source_values: dict[str, set[str]]):
    if not meaningful_portuguese(text):
        return None
    if text in source_values.get(kind, set()):
        return 'exact-portuguese-source-match'
    return 'detected-portuguese'


problems = []
report = {
    'version': 4,
    'strict_when_live': True,
    'method': 'meaningful-exact-source-match+language-detection',
    'locales': {},
}

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

    print(f'{code}: {len(hits)} meaningful Portuguese residue(s) across {files} files [{status}]')
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
        problems.append(f'{code}: {len(hits)} meaningful Portuguese residue(s) remain. {examples}')

REPORT.parent.mkdir(parents=True, exist_ok=True)
REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'Wrote {REPORT}')

if problems:
    print('\n'.join(problems))
    print('Translation completeness FAILED for one or more live locales.')
    sys.exit(1)

print('Translation completeness audit OK (strict for live locales; reporting only for preparing locales).')
