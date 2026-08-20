#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import requests

SITE = Path('site')
SOURCES = Path('monitor/sources.json')
REPORT = Path('monitor/report.json')
STATUS = SITE / 'data/source-status.json'
CHANGELOG = SITE / 'data/change-log.json'
RSS_STATE = Path('monitor/dre-rss.json')
RSS_URL = 'https://files.diariodarepublica.pt/rss/serie1-html.xml'

KEYWORDS = (
    'nacionalidade', 'estrangeir', 'imigra', 'migrante', 'aima',
    'autorização de residência', 'autorizacao de residencia',
    'título de residência', 'titulo de residencia', 'visto',
    'reagrupamento familiar', 'cplp', 'asilo', 'refugi',
    'proteção temporária', 'protecao temporaria',
    'discriminação racial', 'discriminacao racial',
)


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def norm(value: str | None) -> str:
    return re.sub(r'\s+', ' ', value or '').strip()


def item_key(item: dict) -> str:
    raw = item.get('guid') or item.get('link') or (item.get('title', '') + '|' + item.get('pubDate', ''))
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def parse_rss(content: bytes) -> list[dict]:
    root = ET.fromstring(content)
    items = []
    for node in root.findall('.//item'):
        row = {}
        for tag in ('title', 'link', 'guid', 'pubDate', 'description'):
            el = node.find(tag)
            row[tag] = norm(el.text if el is not None else '')
        if row['title'] or row['link']:
            row['key'] = item_key(row)
            items.append(row)
    if not items:
        raise RuntimeError('official DRE RSS returned no items')
    return items


def fetch_rss() -> list[dict]:
    r = requests.get(
        RSS_URL,
        timeout=(8, 30),
        headers={
            'User-Agent': 'GuiaMigrantePT-OfficialSourceMonitor/1.4 (+https://guia-migrante-pt.pages.dev/)',
            'Accept': 'application/rss+xml,application/xml,text/xml;q=0.9,*/*;q=0.5',
        },
    )
    r.raise_for_status()
    return parse_rss(r.content)


def is_relevant(item: dict) -> bool:
    text = (item.get('title', '') + ' ' + item.get('description', '')).lower()
    return any(k in text for k in KEYWORDS)


def main() -> None:
    sources = json.loads(SOURCES.read_text(encoding='utf-8')).get('sources', [])
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    status = json.loads(STATUS.read_text(encoding='utf-8'))
    log = json.loads(CHANGELOG.read_text(encoding='utf-8'))

    items = fetch_rss()
    current_keys = {x['key'] for x in items}
    previous = json.loads(RSS_STATE.read_text(encoding='utf-8')) if RSS_STATE.exists() else None
    previous_keys = set(previous.get('keys', [])) if previous else set()

    alerts = []
    if previous is not None:
        for item in items:
            if item['key'] not in previous_keys and is_relevant(item):
                alerts.append({
                    'title': item.get('title'),
                    'url': item.get('link'),
                    'published': item.get('pubDate'),
                    'source': RSS_URL,
                })

    RSS_STATE.write_text(json.dumps({
        'version': 1,
        'checked_at': now(),
        'url': RSS_URL,
        'keys': sorted(current_keys),
        'items': items[:250],
    }, ensure_ascii=False, indent=2), encoding='utf-8')

    # Individual DRE pages can be difficult for automated clients because the
    # public portal is heavily client-rendered. Future legal changes are therefore
    # covered by the official Series I RSS, which is designed for automated updates.
    dre_required = [s for s in sources if s.get('required') and s.get('domain') == 'diariodarepublica.pt']
    dre_ids = {s['id'] for s in dre_required}

    remaining_missing = [i for i in report.get('missing_required', []) if i not in dre_ids]
    remaining_critical = [e for e in report.get('critical_errors', []) if e.get('id') not in dre_ids]
    coverage = not remaining_missing and not remaining_critical

    for src in dre_required:
        i = src['id']
        prev = status.get('sources', {}).get(i, {})
        status.setdefault('sources', {})[i] = {
            'url': src['url'],
            'domain': src['domain'],
            'state': 'covered_by_official_rss',
            'checked_at': now(),
            'changed_at': None,
            'pages': src.get('pages', []),
            'required': True,
            'coverage_via': RSS_URL,
            'note': 'Future changes covered through the official Diário da República Series I RSS feed.',
            'last_direct_error': prev.get('error'),
        }

    if alerts:
        for alert in alerts:
            log.setdefault('changes', []).insert(0, {
                'time': now(),
                'source_id': 'dre-series1-rss',
                'url': alert.get('url') or RSS_URL,
                'state': 'new_legislation_pending_review',
                'pages': [],
                'title': alert.get('title'),
                'published': alert.get('published'),
            })

    status['baseline_complete'] = coverage
    status['coverage_ok'] = coverage
    status['generated_at'] = now()
    summary = status.setdefault('summary', {})
    summary['missing_required'] = len(remaining_missing)
    summary['critical_errors'] = len(remaining_critical)
    summary['dre_rss_ok'] = True
    summary['dre_sources_covered_by_rss'] = len(dre_required)
    summary['dre_rss_alerts'] = len(alerts)

    report['generated_at'] = now()
    report['baseline_complete'] = coverage
    report['coverage_ok'] = coverage
    report['missing_required'] = remaining_missing
    report['critical_errors'] = remaining_critical
    report['dre_rss_ok'] = True
    report['dre_rss_url'] = RSS_URL
    report['dre_sources_covered_by_rss'] = sorted(dre_ids)
    report['dre_rss_alerts'] = alerts

    log['changes'] = log.get('changes', [])[:300]
    STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    CHANGELOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')

    print(json.dumps({
        'dre_rss_ok': True,
        'dre_sources_covered_by_rss': len(dre_required),
        'dre_rss_alerts': len(alerts),
        'missing_required': len(remaining_missing),
        'critical_errors': len(remaining_critical),
        'coverage_ok': coverage,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
