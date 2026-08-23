#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import runpy
import time
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
CFG = json.loads((SITE / 'data/locales.json').read_text(encoding='utf-8'))

requested = [x.strip() for x in os.environ.get('TRANSLATION_LOCALES', '').split(',') if x.strip()]
all_targets = [x['code'] for x in CFG.get('locales', []) if x.get('code') not in {'pt', 'en'}]
TARGETS = requested or all_targets
REPORT = SITE / 'data' / 'detected-residue-translation-report.json'

base = runpy.run_path(str(ROOT / 'scripts' / 'auto_translate_untranslated_copy.py'))
audit = runpy.run_path(str(ROOT / 'scripts' / 'check_translation_completeness.py'))

norm = base['norm']
visible_text_nodes = base['visible_text_nodes']
attr_slots = base['attr_slots']
translate_batch = base['translate_batch']
make_batches = base['make_batches']
preserve_outer_whitespace = base['preserve_outer_whitespace']
classify_residue = audit['classify_residue']
source_sets = audit['source_sets']


def collect_flagged(soup: BeautifulSoup, code: str, source_values: dict[str, set[str]]):
    """Return only nodes the final QA auditor would actually block on."""
    items = []
    for node in visible_text_nodes(soup):
        text = norm(str(node))
        reason = classify_residue('text', text, source_values, code)
        if reason:
            items.append(('text', node, text, reason))
    for tag, attr in attr_slots(soup):
        text = norm(str(tag.get(attr, '')))
        reason = classify_residue(attr, text, source_values, code)
        if reason:
            items.append(('attr', (tag, attr), text, reason))
    return items


def source_values_for(fp: Path):
    source_path = SITE / fp.name
    if not source_path.exists():
        return {'text': set(), 'aria-label': set(), 'placeholder': set(), 'title': set()}
    return source_sets(source_path)


def apply_pass(code: str):
    folder = SITE / code
    pages = {}
    unique_sources = set()
    reason_counts = {}

    for fp in sorted(folder.glob('*.html')):
        soup = BeautifulSoup(fp.read_text(encoding='utf-8'), 'html.parser')
        flagged = collect_flagged(soup, code, source_values_for(fp))
        pages[fp] = (soup, flagged)
        for _, _, text, reason in flagged:
            unique_sources.add(text)
            reason_counts[reason] = reason_counts.get(reason, 0) + 1

    strings = sorted(unique_sources, key=lambda x: (len(x), x))
    if not strings:
        return {
            'flagged_strings': 0,
            'changed_nodes': 0,
            'changed_pages': 0,
            'reasons': reason_counts,
            'failures': [],
        }

    translated_map = {}
    failures = []
    batches = make_batches(strings)
    print(f'{code}: cleanup pass has {len(strings)} QA-blocking Portuguese residue string(s) in {len(batches)} batch(es).')

    for n, batch in enumerate(batches, 1):
        try:
            translated_map.update(translate_batch(batch, code))
            print(f'  {code}: translated cleanup batch {n}/{len(batches)} ({len(batch)} strings)')
        except Exception as exc:
            failures.append({'batch': n, 'size': len(batch), 'error': str(exc)})
            print(f'  WARNING {code}: cleanup batch {n}/{len(batches)} failed: {exc}')
        time.sleep(0.18)

    changed_nodes = 0
    changed_pages = 0
    for fp, (soup, flagged) in pages.items():
        page_changed = 0
        for kind, slot, source_text, _reason in flagged:
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
            fp.write_text(str(soup), encoding='utf-8')
            changed_nodes += page_changed
            changed_pages += 1

    return {
        'flagged_strings': len(strings),
        'changed_nodes': changed_nodes,
        'changed_pages': changed_pages,
        'reasons': reason_counts,
        'failures': failures,
    }


def remaining_blocking_nodes(code: str) -> int:
    folder = SITE / code
    remaining = 0
    for fp in sorted(folder.glob('*.html')):
        soup = BeautifulSoup(fp.read_text(encoding='utf-8'), 'html.parser')
        remaining += len(collect_flagged(soup, code, source_values_for(fp)))
    return remaining


def main():
    report = {
        'version': 2,
        'method': 'cleanup uses the exact same classifier as final translation QA',
        'locales': {},
    }

    for code in TARGETS:
        folder = SITE / code
        if not folder.exists():
            continue

        passes = []
        for pass_no in range(1, 4):
            result = apply_pass(code)
            result['pass'] = pass_no
            passes.append(result)
            if result['flagged_strings'] == 0 or result['changed_nodes'] == 0:
                break

        remaining = remaining_blocking_nodes(code)
        report['locales'][code] = {'passes': passes, 'remaining_flagged_nodes': remaining}
        print(f'{code}: cleanup finished; remaining QA-blocking Portuguese nodes={remaining}')

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote {REPORT}')


if __name__ == '__main__':
    main()
