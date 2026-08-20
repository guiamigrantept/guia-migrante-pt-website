#!/usr/bin/env python3
from __future__ import annotations

import difflib
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SITE = Path('site')
SNAPS = Path('monitor/snapshots')
CANDS = Path('monitor/candidates')
SOURCES = Path('monitor/sources.json')
REPORT = Path('monitor/report.json')
STATUS = SITE / 'data/source-status.json'
CHANGELOG = SITE / 'data/change-log.json'

ALIASES = {
    'https://diariodarepublica.pt/dr/detalhe/lei-organica/1-2026-1123539996':
        'https://data.dre.pt/eli/leiorg/1/2026/05/18/p/dre/pt/html',
    'https://diariodarepublica.pt/dr/detalhe/lei/3-2024-836604892':
        'https://data.dre.pt/eli/lei/3/2024/01/15/p/dre/pt/html',
    'https://diariodarepublica.pt/dr/legislacao-consolidada/lei/1981-34536975-115625158':
        'https://data.dre.pt/eli/lei/37/1981/p/cons/20260518/pt/html',
}


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def norm(s):
    return re.sub(r'\s+', ' ', s).strip()


def extract_text(content):
    soup = BeautifulSoup(content, 'html.parser')
    for t in soup(['script', 'style', 'noscript', 'svg', 'form', 'nav', 'header', 'footer']):
        t.decompose()
    node = soup.find('main') or soup.find('article') or soup.body or soup
    return '\n'.join(x for x in (norm(v) for v in node.get_text('\n').splitlines()) if len(x) > 1)


def discover_consolidated_alias(original, fallback):
    try:
        r = requests.get(original, timeout=(8, 20), headers={'User-Agent': 'GuiaMigrantePT-OfficialSourceMonitor/1.3'})
        raw = r.text
        m = re.search(r'https?://data\.dre\.pt/eli/lei/37/1981/p/cons/(\d{8})/pt/html', raw, re.I)
        if m:
            return m.group(0)
    except Exception:
        pass
    return fallback


def fetch(alias):
    r = requests.get(alias, timeout=(8, 30), allow_redirects=True, headers={
        'User-Agent': 'GuiaMigrantePT-OfficialSourceMonitor/1.3',
        'Accept': 'text/html,*/*;q=0.5',
    })
    r.raise_for_status()
    text = extract_text(r.content)
    if len(text) < 100:
        raise RuntimeError('official ELI text too short')
    return text, r.url


def write_snapshot(path, src, final_url, text, sha, ts):
    path.write_text(json.dumps({
        'url': src['url'],
        'final_url': final_url,
        'sha256': sha,
        'checked_at': ts,
        'fetch_method': 'official-eli-fallback',
        'text': text,
    }, ensure_ascii=False), encoding='utf-8')


def diff_text(old, new):
    return '\n'.join(
        x for x in difflib.unified_diff(old.splitlines(), new.splitlines(), n=1)
        if x.startswith(('+', '-')) and not x.startswith(('+++', '---'))
    )[:6000]


def main():
    sources_doc = json.loads(SOURCES.read_text(encoding='utf-8'))
    sources = sources_doc.get('sources', [])
    by_url = {s['url']: s for s in sources}
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    status = json.loads(STATUS.read_text(encoding='utf-8'))
    log = json.loads(CHANGELOG.read_text(encoding='utf-8'))
    changed = set(report.get('changed_sources', []))
    recovered = []

    for original, configured_alias in ALIASES.items():
        src = by_url.get(original)
        if not src:
            continue
        alias = configured_alias
        if '/legislacao-consolidada/' in original:
            alias = discover_consolidated_alias(original, configured_alias)
        i = src['id']
        bp = SNAPS / f'{i}.json'
        cp = CANDS / f'{i}.json'
        old = json.loads(bp.read_text(encoding='utf-8')) if bp.exists() else None
        prev = status.get('sources', {}).get(i, {})
        try:
            text, final = fetch(alias)
            sha = hashlib.sha256(text.encode()).hexdigest()
            ts = now()
            if old is None:
                write_snapshot(bp, src, final, text, sha, ts)
                cp.unlink(missing_ok=True)
                state = 'healthy'
                recovered.append(i)
            elif old.get('sha256') == sha:
                cp.unlink(missing_ok=True)
                state = 'healthy'
            else:
                d = diff_text(old.get('text', ''), text)
                write_snapshot(cp, src, final, text, sha, ts)
                state = 'changed_pending_review'
                changed.add(i)
                if prev.get('candidate_sha256') != sha:
                    log.setdefault('changes', []).insert(0, {
                        'time': ts,
                        'source_id': i,
                        'url': original,
                        'state': state,
                        'pages': src.get('pages', []),
                        'candidate_sha256': sha,
                        'diff_excerpt': d[:1200],
                    })
            entry = {
                'url': original,
                'domain': src.get('domain'),
                'state': state,
                'checked_at': ts,
                'changed_at': (prev.get('changed_at') or ts) if state == 'changed_pending_review' else None,
                'pages': src.get('pages', []),
                'required': src.get('required', False),
                'fetch_method': 'official-eli-fallback',
                'fallback_url': final,
            }
            if state == 'changed_pending_review':
                entry['candidate_sha256'] = sha
                entry['diff_excerpt'] = d
            status.setdefault('sources', {})[i] = entry
            report['errors'] = [e for e in report.get('errors', []) if e.get('id') != i]
            report['critical_errors'] = [e for e in report.get('critical_errors', []) if e.get('id') != i]
        except Exception as exc:
            print(f'DRE fallback failed for {original}: {exc}')

    blocked = {}
    for src in sources:
        st = status.get('sources', {}).get(src['id'], {})
        if st.get('state') in {'changed_pending_review', 'source_removed'}:
            for pg in src.get('pages', []):
                blocked.setdefault(pg, []).append(src['id'])

    required = [s for s in sources if s.get('required')]
    missing = [s['id'] for s in required if not (SNAPS / f"{s['id']}.json").exists()]
    critical = [e for e in report.get('errors', []) if e.get('required') and not e.get('had_baseline')]
    coverage = not missing and not critical

    status['blocked_pages'] = {k: sorted(set(v)) for k, v in blocked.items()}
    status['baseline_complete'] = not missing
    status['coverage_ok'] = coverage
    status['generated_at'] = now()
    summary = status.setdefault('summary', {})
    summary['missing_required'] = len(missing)
    summary['critical_errors'] = len(critical)
    summary['blocked_pages'] = len(blocked)
    summary['dre_eli_recovered'] = len(recovered)

    report['generated_at'] = now()
    report['baseline_complete'] = not missing
    report['coverage_ok'] = coverage
    report['missing_required'] = missing
    report['critical_errors'] = critical
    report['changed_sources'] = sorted(changed)
    report['blocked_pages'] = status['blocked_pages']
    report['dre_eli_recovered'] = recovered

    log['changes'] = log.get('changes', [])[:300]
    STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    CHANGELOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({
        'dre_eli_recovered': len(recovered),
        'missing_required': len(missing),
        'critical_errors': len(critical),
        'coverage_ok': coverage,
    }, ensure_ascii=False))


if __name__ == '__main__':
    main()
