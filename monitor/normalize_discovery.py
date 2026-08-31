#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

REPORT = Path('monitor/discovery-report.json')
UPDATES = Path('site/data/official-updates.json')

STOP = {
    'a','o','os','as','de','do','da','dos','das','e','em','no','na','nos','nas','por','para','com','ao','aos','à','às',
    'um','uma','uns','umas','que','já','mais','novo','nova','novos','novas','oficial','oficiais','pt','gov','noticias','notícia',
    'notícias','pedido','pedidos','sobre','em','portugal','aima','irn','justiça','justica'
}


def fold(text: str) -> str:
    text = unicodedata.normalize('NFKD', text or '')
    text = ''.join(ch for ch in text if not unicodedata.combining(ch)).casefold()
    return re.sub(r'[^a-z0-9]+', ' ', text).strip()


def tokens(text: str) -> set[str]:
    return {x for x in fold(text).split() if len(x) >= 4 and x not in STOP}


def slug_tokens(url: str) -> set[str]:
    path = urlparse(url or '').path.rstrip('/').split('/')[-1]
    return tokens(path.replace('-', ' '))


def title_url_match(item: dict) -> bool:
    title = tokens(item.get('title') or '')
    slug = slug_tokens(item.get('url') or '')
    if not title or not slug:
        return True
    overlap = title & slug
    union = title | slug
    score = len(overlap) / max(len(union), 1)
    # Official article slugs are descriptive. Requiring either two shared meaningful
    # words or a modest token-overlap prevents a neighbouring card title being paired
    # with the wrong URL on complex index pages.
    return len(overlap) >= 2 or score >= 0.24


def no_relevant_only(error: str) -> bool:
    if not error:
        return False
    parts = [x.strip() for x in error.split('|') if x.strip()]
    return bool(parts) and all('no relevant entries extracted' in x for x in parts)


def main() -> None:
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    feed = json.loads(UPDATES.read_text(encoding='utf-8'))

    normalized_sources = []
    for source in report.get('sources', []):
        source = dict(source)
        if not source.get('ok') and no_relevant_only(source.get('error') or ''):
            source['ok'] = True
            source['error'] = None
            source['note'] = 'official index reachable; no migration-relevant entries found in this cycle'
        normalized_sources.append(source)

    rejected_urls: set[str] = set()
    kept_updates = []
    for item in feed.get('updates', []):
        if title_url_match(item):
            kept_updates.append(item)
        else:
            if item.get('url'):
                rejected_urls.add(item['url'])

    feed['updates'] = kept_updates
    UPDATES.write_text(json.dumps(feed, ensure_ascii=False, indent=2), encoding='utf-8')

    report['sources'] = normalized_sources
    report['sources_ok'] = sum(1 for x in normalized_sources if x.get('ok'))
    report['sources_total'] = len(normalized_sources)
    report['ok'] = report['sources_total'] > 0 and report['sources_ok'] == report['sources_total']
    report['partial_ok'] = report['sources_ok'] > 0
    report['new_updates'] = [
        x for x in report.get('new_updates', [])
        if x.get('url') not in rejected_urls and title_url_match(x)
    ]
    report['count'] = len(kept_updates)
    report['rejected_mismatched_updates'] = sorted(rejected_urls)
    report['error'] = None if report['ok'] else report.get('error')
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')

    print(
        f"discovery normalization: {report['sources_ok']}/{report['sources_total']} sources healthy; "
        f"{len(rejected_urls)} mismatched update(s) rejected; {len(kept_updates)} update(s) retained"
    )


if __name__ == '__main__':
    main()
