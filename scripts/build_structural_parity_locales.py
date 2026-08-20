#!/usr/bin/env python3
from __future__ import annotations

import copy
import json
from pathlib import Path
from urllib.parse import urlsplit

from bs4 import BeautifulSoup

SITE = Path('site')
BASE = 'https://guia-migrante-pt.pages.dev'


def page_url(code: str, page: str) -> str:
    return f'{BASE}/{page}' if code == 'pt' else f'{BASE}/{code}/{page}'


def is_external(value: str) -> bool:
    return value.startswith(('http://', 'https://', 'mailto:', 'tel:', 'data:', 'javascript:', '#', '//'))


def rewrite_local_url(value: str, page: str) -> str:
    if not value or is_external(value):
        return value
    parts = urlsplit(value)
    path = parts.path
    suffix = ''
    if parts.query:
        suffix += '?' + parts.query
    if parts.fragment:
        suffix += '#' + parts.fragment

    # Portuguese pages live at the site root. In a locale folder, shared assets
    # must go one level up, while HTML navigation should remain inside the locale.
    if path.startswith('../'):
        return value
    if path.startswith('en/'):
        return '../' + path + suffix
    if path.endswith('.html') or path == '':
        return path + suffix
    if path.startswith('/'):
        return value
    return '../' + path + suffix


def prepare_page(source: Path, code: str, hreflang: str) -> str:
    page = source.name
    soup = BeautifulSoup(source.read_text(encoding='utf-8'), 'html.parser')
    if soup.html:
        soup.html['lang'] = code

    head = soup.head
    if head is None:
        raise SystemExit(f'{source}: missing head')

    # Keep staged translations out of search until the text translation itself
    # is complete. Structural parity is validated separately.
    robots = head.find('meta', attrs={'name': 'robots'})
    if robots is None:
        robots = soup.new_tag('meta')
        robots['name'] = 'robots'
        head.append(robots)
    robots['content'] = 'noindex,nofollow'

    status = head.find('meta', attrs={'name': 'translation-status'})
    if status is None:
        status = soup.new_tag('meta')
        status['name'] = 'translation-status'
        head.append(status)
    status['content'] = 'structural-parity-staging'

    canonical = head.find('link', rel=lambda v: v and 'canonical' in v)
    if canonical is None:
        canonical = soup.new_tag('link')
        canonical['rel'] = 'canonical'
        head.append(canonical)
    canonical['href'] = page_url(code, page)

    og = head.find('meta', attrs={'property': 'og:url'})
    if og is not None:
        og['content'] = page_url(code, page)

    for alt in list(head.find_all('link', rel=lambda v: v and 'alternate' in v)):
        alt.decompose()
    for alt_code, alt_hreflang in [('pt', 'pt-PT'), ('en', 'en')]:
        fp = SITE / page if alt_code == 'pt' else SITE / alt_code / page
        if fp.exists():
            link = soup.new_tag('link')
            link['rel'] = 'alternate'
            link['hreflang'] = alt_hreflang
            link['href'] = page_url(alt_code, page)
            head.append(link)

    # Rewrite local links/assets because the target page moves from / to /<locale>/.
    for tag in soup.find_all(True):
        for attr in ('href', 'src'):
            if tag.has_attr(attr):
                tag[attr] = rewrite_local_url(str(tag[attr]), page)

    # Restore navigation between translated pages after generic asset rewriting.
    for a in soup.find_all('a', href=True):
        href = str(a['href'])
        path = urlsplit(href).path
        name = Path(path).name
        if name.endswith('.html') and not path.startswith('../en/') and not is_external(href):
            # Same-language internal page.
            suffix = ''
            parts = urlsplit(href)
            if parts.query:
                suffix += '?' + parts.query
            if parts.fragment:
                suffix += '#' + parts.fragment
            a['href'] = name + suffix

    # Provide a safe non-JS language fallback matching the current target folder.
    site_lang = soup.select_one('.site-lang')
    if site_lang is not None:
        site_lang.clear()
        entries = [
            ('PT', f'../{page}', False),
            ('EN', f'../en/{page}', False),
            (code.upper(), page, True),
        ]
        for label, href, current in entries:
            a = soup.new_tag('a')
            a['href'] = href
            a.string = label
            if current:
                a['class'] = ['active']
                a['aria-current'] = 'page'
            site_lang.append(a)

    return str(soup)


def main() -> None:
    cfg = json.loads((SITE / 'data/locales.json').read_text(encoding='utf-8'))
    targets = [x for x in cfg.get('locales', []) if x.get('code') not in {'pt', 'en'}]
    source_pages = sorted(
        p for p in SITE.glob('*.html')
        if p.name != '404.html' and (SITE / 'en' / p.name).exists()
    )
    if (SITE / '404.html').exists():
        source_pages.append(SITE / '404.html')

    total = 0
    for loc in targets:
        code = loc['code']
        folder = SITE / code
        folder.mkdir(parents=True, exist_ok=True)
        for source in source_pages:
            (folder / source.name).write_text(
                prepare_page(source, code, loc.get('hreflang', code)),
                encoding='utf-8',
            )
            total += 1

    print(f'Built full-structure staging pages: {total} pages across {len(targets)} locales.')


if __name__ == '__main__':
    main()
