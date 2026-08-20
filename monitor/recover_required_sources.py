#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SNAPS = Path('monitor/snapshots')
REPORT = Path('monitor/report.json')
STATUS = Path('site/data/source-status.json')
CHANGELOG = Path('site/data/change-log.json')

LEGACY_MARRIAGE_URL = 'https://justica.gov.pt/Servicos/Iniciar-processo-de-casamento'
CURRENT_MARRIAGE_INFO_URL = 'https://justica.gov.pt/Registos/Civil/Casamento'
UA = 'GuiaMigrantePT-OfficialSourceMonitor/1.4 (+https://guia-migrante-pt.pages.dev/)'

BAD_MARKERS = (
    'web page blocked!',
    'the page cannot be displayed',
    'access denied',
    'attack id:',
    'temporariamente indisponível',
    'temporariamente indisponivel',
    'intervenção técnica programada',
    'intervencao tecnica programada',
    'temporarily unavailable',
    'scheduled maintenance',
)


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def extract_text(content: bytes) -> str:
    soup = BeautifulSoup(content, 'html.parser')
    for tag in soup(['script', 'style', 'noscript', 'svg', 'form', 'nav', 'header', 'footer']):
        tag.decompose()
    node = soup.find('main') or soup.find('article') or soup.body or soup
    lines = []
    for raw in node.get_text('\n').splitlines():
        line = re.sub(r'\s+', ' ', raw).strip()
        if len(line) > 1:
            lines.append(line)
    return '\n'.join(lines)


def valid_text(text: str) -> bool:
    low = re.sub(r'\s+', ' ', text).casefold()
    if len(text) < 300:
        return False
    if any(marker in low for marker in BAD_MARKERS):
        return False
    required_phrases = ('casamento', 'processo', 'registo civil')
    return all(p in low for p in required_phrases)


def main() -> None:
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    status = json.loads(STATUS.read_text(encoding='utf-8'))
    log = json.loads(CHANGELOG.read_text(encoding='utf-8')) if CHANGELOG.exists() else {'version': 1, 'changes': []}

    target = None
    entry = None
    for source_id, source_entry in status.get('sources', {}).items():
        if source_entry.get('url') == LEGACY_MARRIAGE_URL:
            target = source_id
            entry = source_entry
            break

    if not target or not entry:
        print('Marriage recovery: legacy source is not registered')
        return

    baseline_path = SNAPS / f'{target}.json'
    if baseline_path.exists() and target not in report.get('missing_required', []):
        print('Marriage recovery: valid baseline already present')
        return

    response = requests.get(
        CURRENT_MARRIAGE_INFO_URL,
        timeout=(10, 40),
        allow_redirects=True,
        headers={'User-Agent': UA, 'Accept': 'text/html,*/*;q=0.8'},
    )
    response.raise_for_status()
    text = extract_text(response.content)
    if not valid_text(text):
        raise RuntimeError('Current Justiça marriage page did not return trustworthy substantive content')

    ts = now()
    payload = {
        'url': LEGACY_MARRIAGE_URL,
        'final_url': response.url,
        'sha256': hashlib.sha256(text.encode()).hexdigest(),
        'checked_at': ts,
        'fetch_method': 'official-current-page-fallback',
        'text': text,
    }
    baseline_path.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')

    entry.update({
        'state': 'healthy',
        'checked_at': ts,
        'changed_at': None,
        'candidate_sha256': None,
        'diff_excerpt': None,
        'fetch_method': 'official-current-page-fallback',
        'note': 'legacy marriage service redirect monitored through current Justiça marriage information page',
    })

    report['missing_required'] = [x for x in report.get('missing_required', []) if x != target]
    report['errors'] = [e for e in report.get('errors', []) if e.get('id') != target]
    report['critical_errors'] = [e for e in report.get('critical_errors', []) if e.get('id') != target]
    if not report.get('missing_required') and not report.get('critical_errors'):
        report['baseline_complete'] = True
        report['coverage_ok'] = True
        status['baseline_complete'] = True
        status['coverage_ok'] = True

    status.setdefault('summary', {})['missing_required'] = len(report.get('missing_required', []))
    status.setdefault('summary', {})['critical_errors'] = len(report.get('critical_errors', []))
    status['generated_at'] = ts
    report['generated_at'] = ts

    log.setdefault('changes', []).insert(0, {
        'time': ts,
        'source_id': target,
        'url': LEGACY_MARRIAGE_URL,
        'state': 'baseline_recovered_from_current_official_page',
        'reason': CURRENT_MARRIAGE_INFO_URL,
    })
    log['changes'] = log.get('changes', [])[:300]

    STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    CHANGELOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Marriage recovery: baseline restored from current official Justiça page')


if __name__ == '__main__':
    main()
