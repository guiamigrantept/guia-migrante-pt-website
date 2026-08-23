#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from bs4 import BeautifulSoup

SITE = Path('site')
BASE = 'https://guia-migrante-pt.pages.dev'

MANIFEST_COPY = {
    'fr': 'Informations indépendantes et outils gratuits pour les migrants au Portugal.',
    'es': 'Información independiente y herramientas gratuitas para migrantes en Portugal.',
    'uk': 'Незалежна інформація та безкоштовні інструменти для мігрантів у Португалії.',
    'ru': 'Независимая информация и бесплатные инструменты для мигрантов в Португалии.',
    'hi': 'पुर्तगाल में प्रवासियों के लिए स्वतंत्र जानकारी और निःशुल्क उपकरण।',
    'bn': 'পর্তুগালে অভিবাসীদের জন্য স্বাধীন তথ্য ও বিনামূল্যের সরঞ্জাম।',
}


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


def manifest_href(code: str) -> str:
    if code == 'pt':
        return '/manifest.webmanifest'
    if code == 'en':
        return '/manifest-en.webmanifest'
    return f'/manifest-{code}.webmanifest'


def write_generated_manifest(code: str, native_name: str) -> None:
    if code in {'pt', 'en'}:
        return
    payload = {
        'name': f'Guia Migrante PT — {native_name}',
        'short_name': 'Guia Migrante',
        'start_url': f'/{code}/index.html',
        'scope': f'/{code}/',
        'display': 'standalone',
        'background_color': '#f7faf9',
        'theme_color': '#09315c',
        'description': MANIFEST_COPY.get(code, 'Guia Migrante PT'),
        'icons': [
            {'src': '/icon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any maskable'},
            {'src': '/icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any maskable'},
        ],
    }
    (SITE / f'manifest-{code}.webmanifest').write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )


def main() -> None:
    cfg = json.loads((SITE / 'data/locales.json').read_text(encoding='utf-8'))
    locales = [x for x in cfg.get('locales', []) if x.get('status') == 'live']
    by_code = {x['code']: x for x in locales}

    source_pages = sorted(
        p.name for p in SITE.glob('*.html')
        if p.name != '404.html' and (SITE / 'en' / p.name).exists()
    )

    for loc in locales:
        write_generated_manifest(loc['code'], loc.get('native_name') or loc.get('name') or loc['code'])

    changed = 0
    for loc in locales:
        code = loc['code']
        if code != 'pt' and not (SITE / code).exists():
            raise SystemExit(f'{code}: live locale folder missing')

        candidates = list(source_pages)
        if code not in {'pt'} and (SITE / code / '404.html').exists():
            candidates.append('404.html')
        elif code == 'pt' and (SITE / '404.html').exists():
            candidates.append('404.html')

        for page in candidates:
            fp = page_path(code, page)
            if not fp.exists():
                raise SystemExit(f'{code}: missing live page {page}')

            soup = BeautifulSoup(fp.read_text(encoding='utf-8'), 'html.parser')
            head = soup.head
            if head is None:
                raise SystemExit(f'{code}/{page}: missing <head>')

            # Generated locales are staged before final publication.
            if code not in {'pt', 'en'}:
                strip = soup.select_one('.review-strip')
                if strip is not None:
                    strip.decompose()

                robots = head.find('meta', attrs={'name': 'robots'})
                if page != '404.html' and robots is not None and 'noindex' in (robots.get('content') or '').lower():
                    robots.decompose()

                marker = head.find('meta', attrs={'name': 'translation-status'})
                if marker is None:
                    marker = soup.new_tag('meta')
                    marker['name'] = 'translation-status'
                    head.append(marker)
                marker['content'] = 'live'

                # Do not publish Portuguese FAQ structured data on translated pages.
                # The visible page remains available; schema can be restored when a
                # locale-specific FAQ JSON-LD payload is generated.
                for script in list(head.find_all('script', attrs={'type': 'application/ld+json'})):
                    if 'FAQPage' in script.get_text():
                        script.decompose()

            # Every published version of the page must expose the same complete
            # hreflang cluster, including PT, EN and all generated live locales.
            for alt in list(head.find_all('link', rel=lambda v: v and 'alternate' in v)):
                alt.decompose()

            available = [item for item in locales if page_path(item['code'], page).exists()]
            for alt in available:
                head.append(make_link(soup, 'alternate', page_url(alt['code'], page), alt['hreflang']))
            if 'pt' in by_code and page_path('pt', page).exists():
                head.append(make_link(soup, 'alternate', page_url('pt', page), 'x-default'))

            # Keep PWA installation in the current language instead of falling back
            # to the Portuguese manifest on generated locale pages.
            for tag in list(head.find_all('link', rel=lambda v: v and 'manifest' in v)):
                tag.decompose()
            manifest = soup.new_tag('link')
            manifest['rel'] = 'manifest'
            manifest['href'] = manifest_href(code)
            head.append(manifest)

            fp.write_text(str(soup), encoding='utf-8')
            changed += 1

    print(f'Finalized {changed} pages across {len(locales)} live locales.')


if __name__ == '__main__':
    main()
