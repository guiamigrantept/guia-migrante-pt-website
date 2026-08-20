#!/usr/bin/env python3
from __future__ import annotations

import runpy
from pathlib import Path
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
SCRIPTS = ROOT / 'scripts'
TARGETS = ['fr','es','uk','ru','hi','bn']

NAV_EXTRA = {
    'fr': {'index.html':'Accueil','percursos.html':'Parcours','viver-em-portugal.html':'Vivre au Portugal','nacionalidade.html':'Nationalité','ferramentas.html':'Outils','contactos.html':'Contacts','faq.html':'FAQ','seguranca.html':'Éviter les arnaques','legalizacao.html':'Séjour / AIMA'},
    'es': {'index.html':'Inicio','percursos.html':'Rutas','viver-em-portugal.html':'Vivir en Portugal','nacionalidade.html':'Nacionalidad','ferramentas.html':'Herramientas','contactos.html':'Contactos','faq.html':'Preguntas frecuentes','seguranca.html':'Evitar estafas','legalizacao.html':'Residencia / AIMA'},
    'uk': {'index.html':'Головна','percursos.html':'Маршрути','viver-em-portugal.html':'Життя в Португалії','nacionalidade.html':'Громадянство','ferramentas.html':'Інструменти','contactos.html':'Контакти','faq.html':'Поширені питання','seguranca.html':'Уникнення шахрайства','legalizacao.html':'Проживання / AIMA'},
    'ru': {'index.html':'Главная','percursos.html':'Маршруты','viver-em-portugal.html':'Жизнь в Португалии','nacionalidade.html':'Гражданство','ferramentas.html':'Инструменты','contactos.html':'Контакты','faq.html':'Частые вопросы','seguranca.html':'Как избежать мошенничества','legalizacao.html':'Проживание / AIMA'},
    'hi': {'index.html':'मुखपृष्ठ','percursos.html':'मार्ग','viver-em-portugal.html':'पुर्तगाल में जीवन','nacionalidade.html':'नागरिकता','ferramentas.html':'उपकरण','contactos.html':'संपर्क','faq.html':'सामान्य प्रश्न','seguranca.html':'धोखाधड़ी से बचें','legalizacao.html':'निवास / AIMA'},
    'bn': {'index.html':'হোম','percursos.html':'পথসমূহ','viver-em-portugal.html':'পর্তুগালে জীবন','nacionalidade.html':'নাগরিকত্ব','ferramentas.html':'টুলস','contactos.html':'যোগাযোগ','faq.html':'সাধারণ প্রশ্ন','seguranca.html':'প্রতারণা এড়ান','legalizacao.html':'বাসস্থান / AIMA'},
}


def load(path: str):
    return runpy.run_path(str(SCRIPTS / path))


def merge_payloads():
    core = {}
    commons = {}
    for script in ['build_locales.py','build_locales_uk_ru.py','build_locales_hi_bn.py']:
        ns = load(script)
        for code, pages in ns.get('PAGES', {}).items():
            core.setdefault(code, {}).update(pages)
        for code, data in ns.get('COMMON', {}).items():
            commons.setdefault(code, {}).update(data)

    routes_ns = load('build_route_locales.py')
    routes = routes_ns.get('P', {})
    route_common = routes_ns.get('COMMON', {})

    living_ns = load('build_living_locales.py')
    living = living_ns.get('DATA', {})
    living_ui = living_ns.get('UI', {})

    remaining_ns = load('build_remaining_locales.py')
    remaining = remaining_ns.get('DATA', {})
    remaining_ui = remaining_ns.get('UI', {})

    return core, commons, routes, route_common, living, living_ui, remaining, remaining_ui


def basename(href: str) -> str:
    if not href:
        return ''
    path = urlsplit(href).path
    return Path(path).name


def set_plain_text(el, text: str | None):
    if not el or not text:
        return False
    # Preserve nested icons/spans whenever present; replace the first direct text node.
    direct = [n for n in el.find_all(string=True, recursive=False) if n.strip()]
    if direct:
        direct[0].replace_with(text)
    elif not el.find(True):
        el.string = text
    else:
        el.insert(0, text)
    return True


def set_meta(soup, name=None, prop=None, value=None):
    if not value:
        return False
    attrs = {'name': name} if name else {'property': prop}
    tag = soup.head.find('meta', attrs=attrs) if soup.head else None
    if tag is None and soup.head:
        tag = soup.new_tag('meta')
        if name:
            tag['name'] = name
        else:
            tag['property'] = prop
        soup.head.append(tag)
    if tag is not None:
        tag['content'] = value
        return True
    return False


def translate_common_ui(soup, code, common, ui):
    changed = 0
    navmap = dict(NAV_EXTRA.get(code, {}))
    if isinstance(common, dict):
        navmap.update(common.get('nav', {}) or {})

    for nav in soup.select('.desktop-nav, .mobile-nav'):
        for a in nav.find_all('a', href=True):
            label = navmap.get(basename(a['href']))
            if label and set_plain_text(a, label):
                changed += 1

    skip = soup.select_one('.skip-link')
    skip_text = (common or {}).get('skip') or (ui or {}).get('skip')
    if skip_text and set_plain_text(skip, skip_text):
        changed += 1

    menu = soup.select_one('.menu-btn')
    menu_text = (common or {}).get('menu') or (ui or {}).get('menu')
    if menu is not None and menu_text:
        menu['aria-label'] = menu_text
        changed += 1

    brand_small = soup.select_one('.brand-name small') or soup.select_one('.brand small')
    brand_text = (common or {}).get('brand_sub') or (common or {}).get('brand')
    if brand_text and set_plain_text(brand_small, brand_text):
        changed += 1

    topbar = soup.select_one('.topbar-inner') or soup.select_one('.topbar .container')
    independent = (common or {}).get('independent') or (common or {}).get('ind') or (ui or {}).get('independent')
    if topbar is not None and independent:
        # Keep decorative dot/icon and replace only visible text nodes.
        direct = [n for n in topbar.find_all(string=True, recursive=False) if n.strip()]
        if direct:
            direct[-1].replace_with(independent)
            changed += 1

    # Translate short internal navigation links outside the main nav when their destination is known.
    for a in soup.find_all('a', href=True):
        label = navmap.get(basename(a['href']))
        current = a.get_text(' ', strip=True)
        if label and current and len(current) <= 28 and set_plain_text(a, label):
            changed += 1

    return changed


def hero_parts(soup):
    main = soup.find('main') or soup
    hero = main.select_one('.hero') or main.find('section') or main
    h1 = hero.find('h1') or main.find('h1')
    lead = hero.find('p')
    kicker = hero.select_one('.eyebrow, .kicker, .section-kicker')
    return hero, h1, lead, kicker


def translate_core_page(soup, payload):
    changed = 0
    if not isinstance(payload, dict):
        return changed
    if soup.title and payload.get('title'):
        soup.title.string = payload['title']; changed += 1
    if payload.get('description'):
        changed += set_meta(soup, name='description', value=payload['description'])

    _, h1, lead, kicker = hero_parts(soup)
    if payload.get('h1') and set_plain_text(h1, payload['h1']): changed += 1
    if payload.get('lead') and set_plain_text(lead, payload['lead']): changed += 1
    if payload.get('kicker') and set_plain_text(kicker, payload['kicker']): changed += 1

    translated_sections = payload.get('sections') or []
    candidates = [s for s in (soup.find('main') or soup).find_all('section') if s.find('h2')]
    used = 0
    for sec_title, sec_intro, cards in translated_sections:
        if used >= len(candidates):
            break
        sec = candidates[used]; used += 1
        h2 = sec.find('h2')
        if set_plain_text(h2, sec_title): changed += 1
        head = sec.select_one('.section-head')
        p = head.find('p') if head else sec.find('p')
        if set_plain_text(p, sec_intro): changed += 1
        h3s = sec.find_all('h3')
        for i, card in enumerate(cards or []):
            if i >= len(h3s): break
            title, body, *_ = card
            h3 = h3s[i]
            if set_plain_text(h3, title): changed += 1
            parent = h3.parent
            body_p = parent.find('p') if parent else None
            if set_plain_text(body_p, body): changed += 1
    return changed


def translate_tuple_page(soup, payload, common):
    changed = 0
    if not isinstance(payload, (tuple, list)) or len(payload) < 2:
        return changed
    title, lead = payload[0], payload[1]
    cards = payload[2] if len(payload) > 2 and isinstance(payload[2], (list, tuple)) else []

    if soup.title:
        soup.title.string = f'{title} | Guia Migrante PT'; changed += 1
    set_meta(soup, name='description', value=lead)
    _, h1, hero_lead, _ = hero_parts(soup)
    if set_plain_text(h1, title): changed += 1
    if set_plain_text(hero_lead, lead): changed += 1

    main = soup.find('main') or soup
    sections = [s for s in main.find_all('section') if s.find('h2')]
    if sections:
        sec = sections[0]
        heading = (common or {}).get('section') or (common or {}).get('practical')
        intro = (common or {}).get('intro') or (common or {}).get('check')
        if heading and set_plain_text(sec.find('h2'), heading): changed += 1
        head = sec.select_one('.section-head')
        p = head.find('p') if head else sec.find('p')
        if intro and set_plain_text(p, intro): changed += 1

        h3s = sec.find_all('h3')
        source_cards = cards or (common or {}).get('cards') or []
        for i, card in enumerate(source_cards):
            if i >= len(h3s): break
            ct, cb = card[0], card[1]
            h3 = h3s[i]
            if set_plain_text(h3, ct): changed += 1
            parent = h3.parent
            cp = parent.find('p') if parent else None
            if set_plain_text(cp, cb): changed += 1
    return changed


def ensure_draft_marker(soup):
    if not soup.head:
        return
    tag = soup.head.find('meta', attrs={'name':'translation-copy'})
    if tag is None:
        tag = soup.new_tag('meta')
        tag['name'] = 'translation-copy'
        soup.head.append(tag)
    tag['content'] = 'partial-reviewed-draft'


def main():
    core, commons, routes, route_common, living, living_ui, remaining, remaining_ui = merge_payloads()
    total_files = 0
    total_changes = 0
    coverage = {}

    for code in TARGETS:
        folder = SITE / code
        if not folder.exists():
            continue
        coverage[code] = {'files':0,'translated_fields':0}
        common = commons.get(code, {})
        for fp in sorted(folder.glob('*.html')):
            page = fp.name
            soup = BeautifulSoup(fp.read_text(encoding='utf-8'), 'html.parser')
            changes = translate_common_ui(soup, code, common, living_ui.get(code) or remaining_ui.get(code) or {})

            if page in core.get(code, {}):
                changes += translate_core_page(soup, core[code][page])
            elif page in routes.get(code, {}):
                changes += translate_tuple_page(soup, routes[code][page], route_common.get(code, {}))
            elif page in living.get(code, {}):
                changes += translate_tuple_page(soup, living[code][page], living_ui.get(code, {}))
            elif page in remaining.get(code, {}):
                changes += translate_tuple_page(soup, remaining[code][page], remaining_ui.get(code, {}))

            ensure_draft_marker(soup)
            fp.write_text(str(soup), encoding='utf-8')
            total_files += 1
            total_changes += changes
            coverage[code]['files'] += 1
            coverage[code]['translated_fields'] += changes

    print(f'Applied full-structure translation copy: {total_changes} translated fields across {total_files} files.')
    for code in TARGETS:
        if code in coverage:
            print(f"  {code}: {coverage[code]['translated_fields']} translated fields / {coverage[code]['files']} files")


if __name__ == '__main__':
    main()
