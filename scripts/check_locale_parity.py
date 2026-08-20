#!/usr/bin/env python3
from pathlib import Path
import json, sys
from bs4 import BeautifulSoup

SITE = Path('site')
CFG = json.loads((SITE / 'data/locales.json').read_text(encoding='utf-8'))
LIVE = [x['code'] for x in CFG.get('locales', []) if x.get('status') == 'live']
NEW_LIVE = [c for c in LIVE if c not in {'pt', 'en'}]

# These elements represent content blocks and user-facing functionality that must
# not disappear merely because the language changes.
COUNT_SELECTORS = [
    'section', 'form', 'input', 'select', 'textarea', 'button', 'details',
    'table', '[role="button"]', '[data-tool]', '[data-action]'
]


def soup_for(path: Path) -> BeautifulSoup:
    return BeautifulSoup(path.read_text(encoding='utf-8'), 'html.parser')


def structural_ids(soup: BeautifulSoup):
    # Ignore language-switcher-only ids if they are ever added server-side.
    return {x.get('id') for x in soup.find_all(id=True) if x.get('id') and not x.get('id').startswith('gm-')}


def counts(soup: BeautifulSoup):
    return {sel: len(soup.select(sel)) for sel in COUNT_SELECTORS}


problems = []
source_pages = sorted(
    p.name for p in SITE.glob('*.html')
    if p.name != '404.html' and (SITE / 'en' / p.name).exists()
)

for code in NEW_LIVE:
    for page in source_pages:
        src = SITE / page
        dst = SITE / code / page
        if not dst.exists():
            problems.append(f'{code}/{page}: missing page')
            continue

        src_soup = soup_for(src)
        dst_soup = soup_for(dst)

        src_ids = structural_ids(src_soup)
        dst_ids = structural_ids(dst_soup)
        missing_ids = sorted(src_ids - dst_ids)
        if missing_ids:
            problems.append(
                f'{code}/{page}: structural parity failed; missing {len(missing_ids)} ids '
                f'(examples: {missing_ids[:8]})'
            )

        src_counts = counts(src_soup)
        dst_counts = counts(dst_soup)
        for sel in COUNT_SELECTORS:
            # A translation may add accessibility helpers, but it must never have
            # fewer functional/content elements than the Portuguese source.
            if dst_counts[sel] < src_counts[sel]:
                problems.append(
                    f'{code}/{page}: selector {sel!r} dropped from '
                    f'{src_counts[sel]} to {dst_counts[sel]}'
                )

        # Preserve major navigation destinations. External official links may be
        # localized or updated separately, so only internal HTML destinations are checked.
        def internal_pages(soup):
            out = set()
            for a in soup.find_all('a', href=True):
                href = a['href'].split('#', 1)[0].split('?', 1)[0]
                if not href or href.startswith(('http://', 'https://', 'mailto:', 'tel:', '#')):
                    continue
                name = Path(href).name
                if name.endswith('.html'):
                    out.add(name)
            return out

        src_links = internal_pages(src_soup)
        dst_links = internal_pages(dst_soup)
        missing_links = sorted(src_links - dst_links)
        if missing_links:
            problems.append(
                f'{code}/{page}: internal navigation parity failed; missing '
                f'{missing_links[:10]}'
            )

if problems:
    print('\n'.join(problems[:250]))
    print(f'Locale parity FAILED with {len(problems)} problem(s).')
    sys.exit(1)

print(f'Locale parity OK for {len(NEW_LIVE)} newly published locale(s) across {len(source_pages)} source pages.')
