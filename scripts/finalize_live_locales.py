#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from bs4 import BeautifulSoup

SITE = Path('site')
BASE = 'https://guia-migrante-pt.pages.dev'


def page_path(code: str, page: str) -> Path:
    return SITE / page if code == 'pt' else SITE / code / page


def page_url(code: str, page: str) -> str:
    return f'{BASE}/{page}' if code == 'pt' else f'{BASE}/{code}/{page}'


def make_link(soup: BeautifulSoup, rel: str, href: str, hreflang: str | None = None):
    tag = soup.new_tag('link')
    tag['rel'] = rel
    tag['href'] = href
    if hreflang:
        tag['hreflang'] = hreflang
    return tag


def main() -> None:
    cfg = json.loads((SITE / 'data/locales.json').read_text(encoding='utf-8'))
    locales = [x for x in cfg.get('locales', []) if x.get('status') == 'live']
    by_code = {x['code']: x for x in locales}
    new_codes = [c for c in by_code if c not in {'pt', 'en'}]

    source_pages = sorted(
        p.name for p in SITE.glob('*.html')
        if p.name != '404.html' and (SITE / 'en' / p.name).exists()
    )

    changed = 0
    for code in new_codes:
        folder = SITE / code
        if not folder.exists():
            raise SystemExit(f'{code}: live locale folder missing')

        # Remove staging treatment from the localized 404 too, but keep it noindex.
        candidates = source_pages + (['404.html'] if (folder / '404.html').exists() else [])
        for page in candidates:
            fp = folder / page
            if not fp.exists():
                raise SystemExit(f'{code}: missing live page {page}')

            soup = BeautifulSoup(fp.read_text(encoding='utf-8'), 'html.parser')
            head = soup.head
            if head is None:
                raise SystemExit(f'{code}/{page}: missing <head>')

            # The translation builders deliberately emit a staging banner and noindex.
            # Once the locale is marked live, remove those staging-only controls.
            strip = soup.select_one('.review-strip')
            if strip is not None:
                strip.decompose()

            robots = head.find('meta', attrs={'name': 'robots'})
            if page != '404.html' and robots is not None and 'noindex' in (robots.get('content') or '').lower():
                robots.decompose()

            # Keep one explicit marker so QA and future tooling can distinguish
            # live translations from staged output.
            marker = head.find('meta', attrs={'name': 'translation-status'})
            if marker is None:
                marker = soup.new_tag('meta')
                marker['name'] = 'translation-status'
                head.append(marker)
            marker['content'] = 'live'

            # Replace the limited PT/EN alternates emitted during staging with the
            # complete set of published languages for this exact page.
            for alt in list(head.find_all('link', rel=lambda v: v and 'alternate' in v)):
                alt.decompose()

            available = [loc for loc in locales if page_path(loc['code'], page).exists()]
            for loc in available:
                head.append(make_link(soup, 'alternate', page_url(loc['code'], page), loc['hreflang']))
            if 'pt' in by_code and page_path('pt', page).exists():
                head.append(make_link(soup, 'alternate', page_url('pt', page), 'x-default'))

            fp.write_text(str(soup), encoding='utf-8')
            changed += 1

    print(f'Finalized {changed} localized pages across {len(new_codes)} live locales.')


if __name__ == '__main__':
    main()
