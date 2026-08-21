#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup, Comment

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
CFG = json.loads((SITE / 'data/locales.json').read_text(encoding='utf-8'))
ALL_TARGETS = [x['code'] for x in CFG.get('locales', []) if x.get('code') not in {'pt', 'en'}]
REQUESTED = [x.strip() for x in os.getenv('TRANSLATION_LOCALES', '').split(',') if x.strip()]
TARGETS = [x for x in ALL_TARGETS if not REQUESTED or x in REQUESTED]
SKIP_TAGS = {'script', 'style', 'noscript', 'svg', 'code'}
REPORT = SITE / 'data' / 'auto-translation-report.json'

DO_NOT_TRANSLATE_ALONE = {
    'Guia Migrante PT', 'AIMA', 'NIF', 'NISS', 'SNS', 'SNS 24', 'CPLP', 'CLAIM',
    'Portugal', 'Portal das Finanças', 'Segurança Social', 'Diário da República',
    'Autoridade Tributária', 'IRN', 'IMT', 'DGES', 'ACT', 'CIG', 'ERSE', 'gov.pt',
}

MARKER_RE = re.compile(r'§§(\d{4})§§')


def norm(value: str) -> str:
    return ' '.join(value.split())


def should_translate(source: str, current: str) -> bool:
    s = norm(source)
    c = norm(current)
    if not s or not c or s != c:
        return False
    if s in DO_NOT_TRANSLATE_ALONE:
        return False
    if len(s) < 2:
        return False
    if not any(ch.isalpha() for ch in s):
        return False
    return True


def visible_text_nodes(soup: BeautifulSoup):
    nodes = []
    for node in soup.find_all(string=True):
        if isinstance(node, Comment):
            continue
        parent = node.parent
        if parent and parent.name in SKIP_TAGS:
            continue
        if norm(str(node)):
            nodes.append(node)
    return nodes


def attr_slots(soup: BeautifulSoup):
    slots = []
    for tag in soup.find_all(True):
        for attr in ('aria-label', 'placeholder', 'title'):
            value = tag.get(attr)
            if value is not None and norm(str(value)):
                slots.append((tag, attr))
    return slots


def post_translate(text: str, target: str, attempts: int = 4) -> str:
    endpoint = 'https://translate.googleapis.com/translate_a/single'
    payload = urlencode({
        'client': 'gtx',
        'sl': 'pt',
        'tl': target,
        'dt': 't',
        'q': text,
    }).encode('utf-8')
    last_error = None
    for attempt in range(attempts):
        try:
            req = Request(
                endpoint,
                data=payload,
                headers={
                    'User-Agent': 'Mozilla/5.0 GuiaMigrantePT/1.0',
                    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                },
                method='POST',
            )
            with urlopen(req, timeout=30) as response:
                data = json.loads(response.read().decode('utf-8'))
            chunks = data[0] if data and isinstance(data[0], list) else []
            result = ''.join((part[0] or '') for part in chunks if isinstance(part, list) and part)
            if result.strip():
                return result
            last_error = RuntimeError('empty translation response')
        except (URLError, HTTPError, TimeoutError, ValueError, OSError) as exc:
            last_error = exc
        time.sleep(2.0 * (attempt + 1))
    raise RuntimeError(f'translation request failed: {last_error}')


def make_batches(strings: list[str], max_chars: int = 2400):
    batches = []
    current = []
    total = 0
    for text in strings:
        extra = len(text) + 18
        if current and total + extra > max_chars:
            batches.append(current)
            current = []
            total = 0
        current.append(text)
        total += extra
    if current:
        batches.append(current)
    return batches


def translate_batch(strings: list[str], target: str) -> dict[str, str]:
    if not strings:
        return {}
    payload_parts = []
    for i, text in enumerate(strings):
        payload_parts.append(f'§§{i:04d}§§\n{text}')
    payload = '\n'.join(payload_parts)
    translated = post_translate(payload, target)
    matches = list(MARKER_RE.finditer(translated))
    if len(matches) != len(strings):
        out = {}
        for text in strings:
            out[text] = post_translate(text, target)
            time.sleep(0.15)
        return out

    out = {}
    for pos, match in enumerate(matches):
        idx = int(match.group(1))
        start = match.end()
        end = matches[pos + 1].start() if pos + 1 < len(matches) else len(translated)
        value = translated[start:end].strip()
        if 0 <= idx < len(strings) and value:
            out[strings[idx]] = value
    if len(out) != len(strings):
        missing = [s for s in strings if s not in out]
        for text in missing:
            out[text] = post_translate(text, target)
            time.sleep(0.15)
    return out


def preserve_outer_whitespace(original: str, translated: str) -> str:
    prefix = original[: len(original) - len(original.lstrip())]
    suffix = original[len(original.rstrip()):]
    return prefix + translated.strip() + suffix


def collect_page_pairs(source_soup: BeautifulSoup, target_soup: BeautifulSoup):
    pairs = []
    src_nodes = visible_text_nodes(source_soup)
    dst_nodes = visible_text_nodes(target_soup)
    for src, dst in zip(src_nodes, dst_nodes):
        if should_translate(str(src), str(dst)):
            pairs.append(('text', src, dst, norm(str(src))))

    src_attrs = attr_slots(source_soup)
    dst_attrs = attr_slots(target_soup)
    for (src_tag, src_attr), (dst_tag, dst_attr) in zip(src_attrs, dst_attrs):
        if src_attr != dst_attr:
            continue
        src_value = str(src_tag.get(src_attr, ''))
        dst_value = str(dst_tag.get(dst_attr, ''))
        if should_translate(src_value, dst_value):
            pairs.append(('attr', (src_tag, src_attr), (dst_tag, dst_attr), norm(src_value)))
    return pairs


def main():
    if REQUESTED and not TARGETS:
        raise SystemExit(f'No supported locale selected: {REQUESTED}')
    print('Translation worker locales: ' + ', '.join(TARGETS))
    report = {'version': 2, 'provider': 'Google Translate draft fallback', 'locales': {}}

    for code in TARGETS:
        folder = SITE / code
        if not folder.exists():
            continue

        page_pairs = {}
        unique_sources = set()
        for target_path in sorted(folder.glob('*.html')):
            source_path = SITE / target_path.name
            if not source_path.exists():
                continue
            source_soup = BeautifulSoup(source_path.read_text(encoding='utf-8'), 'html.parser')
            target_soup = BeautifulSoup(target_path.read_text(encoding='utf-8'), 'html.parser')
            pairs = collect_page_pairs(source_soup, target_soup)
            page_pairs[target_path] = (target_soup, pairs)
            for _, _, _, source_text in pairs:
                unique_sources.add(source_text)

        strings = sorted(unique_sources, key=lambda x: (len(x), x))
        translated_map = {}
        failures = []
        batches = make_batches(strings)
        print(f'{code}: {len(strings)} unique untranslated source string(s) in {len(batches)} batch(es).')

        for n, batch in enumerate(batches, 1):
            try:
                translated_map.update(translate_batch(batch, code))
                print(f'  {code}: translated batch {n}/{len(batches)} ({len(batch)} strings)')
            except Exception as exc:
                failures.append({'batch': n, 'size': len(batch), 'error': str(exc)})
                print(f'  WARNING {code}: batch {n}/{len(batches)} failed: {exc}')
            time.sleep(0.25)

        changed_nodes = 0
        changed_pages = 0
        for target_path, (target_soup, pairs) in page_pairs.items():
            page_changed = 0
            for kind, _src_slot, dst_slot, source_text in pairs:
                translated = translated_map.get(source_text)
                if not translated or norm(translated) == source_text:
                    continue
                if kind == 'text':
                    original = str(dst_slot)
                    dst_slot.replace_with(preserve_outer_whitespace(original, translated))
                    page_changed += 1
                else:
                    dst_tag, dst_attr = dst_slot
                    dst_tag[dst_attr] = translated.strip()
                    page_changed += 1
            if page_changed:
                target_path.write_text(str(target_soup), encoding='utf-8')
                changed_pages += 1
                changed_nodes += page_changed

        report['locales'][code] = {
            'unique_source_strings': len(strings),
            'translated_strings': len(translated_map),
            'changed_nodes': changed_nodes,
            'changed_pages': changed_pages,
            'failed_batches': failures,
        }
        print(f'{code}: filled {changed_nodes} untranslated field(s) across {changed_pages} page(s); failures={len(failures)}')
        if failures:
            raise SystemExit(f'{code}: translation provider failed for {len(failures)} batch(es)')

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Wrote {REPORT}')


if __name__ == '__main__':
    main()
