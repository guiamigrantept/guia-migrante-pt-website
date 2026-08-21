#!/usr/bin/env python3
from __future__ import annotations

import json
import runpy
import time
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
CFG = json.loads((SITE / 'data/locales.json').read_text(encoding='utf-8'))
TARGETS = [x['code'] for x in CFG.get('locales', []) if x.get('code') not in {'pt', 'en'}]
REPORT = SITE / 'data' / 'exact-residue-translation-report.json'

base = runpy.run_path(str(ROOT / 'scripts' / 'auto_translate_untranslated_copy.py'))
norm = base['norm']
visible_text_nodes = base['visible_text_nodes']
attr_slots = base['attr_slots']
translate_batch = base['translate_batch']
make_batches = base['make_batches']
preserve_outer_whitespace = base['preserve_outer_whitespace']
DO_NOT_TRANSLATE_ALONE = base['DO_NOT_TRANSLATE_ALONE']


def translatable(text: str) -> bool:
    text = norm(text)
    return bool(
        text
        and text not in DO_NOT_TRANSLATE_ALONE
        and len(text) >= 2
        and any(ch.isalpha() for ch in text)
    )


def collect_exact_matches(source_soup: BeautifulSoup, target_soup: BeautifulSoup):
    pairs = []

    # Do not zip text nodes: translated markup can introduce/remove text nodes
    # without changing page structure. Match by exact Portuguese source value.
    source_texts = {norm(str(node)) for node in visible_text_nodes(source_soup)}
    for dst in visible_text_nodes(target_soup):
        current = norm(str(dst))
        if current in source_texts and translatable(current):
            pairs.append(('text', dst, current))

    source_attrs = {}
    for tag, attr in attr_slots(source_soup):
        source_attrs.setdefault(attr, set()).add(norm(str(tag.get(attr, ''))))
    for tag, attr in attr_slots(target_soup):
        current = norm(str(tag.get(attr, '')))
        if current in source_attrs.get(attr, set()) and translatable(current):
            pairs.append(('attr', (tag, attr), current))

    return pairs


def main():
    report = {'version': 1, 'method': 'exact-source-value matching', 'locales': {}}

    for code in TARGETS:
        folder = SITE / code
        if not folder.exists():
            continue

        pages = {}
        unique_sources = set()
        for target_path in sorted(folder.glob('*.html')):
            source_path = SITE / target_path.name
            if not source_path.exists():
                continue
            source_soup = BeautifulSoup(source_path.read_text(encoding='utf-8'), 'html.parser')
            target_soup = BeautifulSoup(target_path.read_text(encoding='utf-8'), 'html.parser')
            pairs = collect_exact_matches(source_soup, target_soup)
            pages[target_path] = (target_soup, pairs)
            unique_sources.update(source for _, _, source in pairs)

        strings = sorted(unique_sources, key=lambda x: (len(x), x))
        translated_map = {}
        failures = []
        batches = make_batches(strings)
        print(f'{code}: {len(strings)} exact Portuguese source string(s) in {len(batches)} batch(es).')

        for n, batch in enumerate(batches, 1):
            try:
                translated_map.update(translate_batch(batch, code))
                print(f'  {code}: translated batch {n}/{len(batches)} ({len(batch)} strings)')
            except Exception as exc:
                failures.append({'batch': n, 'size': len(batch), 'error': str(exc)})
                print(f'  WARNING {code}: batch {n}/{len(batches)} failed: {exc}')
            time.sleep(0.18)

        changed_nodes = 0
        changed_pages = 0
        for target_path, (target_soup, pairs) in pages.items():
            page_changed = 0
            for kind, slot, source_text in pairs:
                translated = translated_map.get(source_text)
                if not translated or norm(translated) == source_text:
                    continue
                if kind == 'text':
                    original = str(slot)
                    slot.replace_with(preserve_outer_whitespace(original, translated))
                else:
                    tag, attr = slot
                    tag[attr] = translated.strip()
                page_changed += 1

            if page_changed:
                target_path.write_text(str(target_soup), encoding='utf-8')
                changed_pages += 1
                changed_nodes += page_changed

        report['locales'][code] = {
            'unique_exact_source_strings': len(strings),
            'translated_strings': len(translated_map),
            'changed_nodes': changed_nodes,
            'changed_pages': changed_pages,
            'failed_batches': failures,
        }
        print(f'{code}: replaced {changed_nodes} exact Portuguese field(s) across {changed_pages} page(s); failures={len(failures)}')

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote {REPORT}')


if __name__ == '__main__':
    main()
