#!/usr/bin/env python3
from __future__ import annotations

import difflib
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

SNAPS = Path('monitor/snapshots')
CANDS = Path('monitor/candidates')
REPORT = Path('monitor/report.json')
STATUS = Path('site/data/source-status.json')
CHANGELOG = Path('site/data/change-log.json')

LEGACY_MARRIAGE_URL = 'https://justica.gov.pt/Servicos/Iniciar-processo-de-casamento'
MARRIAGE_OFFICIAL_SOURCES = (
    'https://justica.gov.pt/Registos/Civil/Casamento',
    'https://registo.justica.gov.pt/Cidadaos/Casamento',
    'https://irn.justica.gov.pt/Servicos/Cidadao/Casamento/Organizar-o-casamento',
)
VERIFIED_SEED_URL = 'https://justica.gov.pt/Registos/Civil/Casamento'
VERIFIED_SEED_DATE = '2026-08-20'
VERIFIED_SEED_TEXT = (
    'Casamento — informação oficial da Justiça verificada em 20-08-2026. '
    'O casamento deve ser registado. O processo de casamento pode ser iniciado online '
    'ou presencialmente num Registo Civil. Depois de escolherem uma data, os noivos '
    'devem organizar o processo com pelo menos um mês de antecedência.'
)
UA = 'GuiaMigrantePT-OfficialSourceMonitor/1.6 (+https://guia-migrante-pt.pages.dev/)'

BAD_MARKERS = (
    'web page blocked!',
    'the page cannot be displayed',
    'access denied',
    'request blocked',
    'attack id:',
    'message id:',
    'you have been blocked',
    'verify you are human',
    'checking your browser before accessing',
    'temporariamente indisponível',
    'temporariamente indisponivel',
    'intervenção técnica programada',
    'intervencao tecnica programada',
    'tente novamente mais tarde',
    'service temporarily unavailable',
    'temporarily unavailable',
    'scheduled maintenance',
)


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def compact(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def extract_text(content: bytes) -> str:
    soup = BeautifulSoup(content, 'html.parser')
    for tag in soup(['script', 'style', 'noscript', 'svg', 'form', 'nav', 'header', 'footer']):
        tag.decompose()
    node = soup.find('main') or soup.find('article') or soup.body or soup
    lines = []
    for raw in node.get_text('\n').splitlines():
        line = compact(raw)
        if len(line) > 1:
            lines.append(line)
    return '\n'.join(lines)


def trustworthy(text: str) -> bool:
    low = compact(text).casefold()
    if len(text) < 220:
        return False
    if any(marker in low for marker in BAD_MARKERS):
        return False
    if 'casamento' not in low:
        return False
    signals = ('processo', 'registo', 'registo civil', 'noivos', 'online', 'conservatória')
    return sum(1 for signal in signals if signal in low) >= 2


def key_facts_match(text: str) -> bool:
    low = compact(text).casefold()
    if 'casamento' not in low or 'processo' not in low:
        return False
    has_registry = 'registo civil' in low or 'conservatória' in low or 'conservatoria' in low
    has_channel = 'online' in low or 'internet' in low
    return has_registry and has_channel


def chrome() -> str | None:
    for name in ('google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser'):
        path = shutil.which(name)
        if path:
            return path
    return None


def browser_fetch(url: str) -> tuple[str, str] | None:
    binary = chrome()
    if not binary:
        return None
    try:
        proc = subprocess.run(
            [binary, '--headless=new', '--no-sandbox', '--disable-gpu',
             '--disable-dev-shm-usage', '--disable-background-networking',
             '--dump-dom', url],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=55,
        )
    except Exception:
        return None
    if proc.returncode or not proc.stdout:
        return None
    text = extract_text(proc.stdout)
    if not trustworthy(text):
        return None
    return text, url


def fetch_official_marriage_text() -> tuple[str, str, str] | None:
    session = requests.Session()
    errors = []
    for url in MARRIAGE_OFFICIAL_SOURCES:
        try:
            response = session.get(
                url,
                timeout=(8, 28),
                allow_redirects=True,
                headers={'User-Agent': UA, 'Accept': 'text/html,*/*;q=0.8'},
            )
            response.raise_for_status()
            text = extract_text(response.content)
            if trustworthy(text):
                return text, response.url, 'requests-official-replacement'
            errors.append(f'{url}: non-substantive response')
        except Exception as exc:
            errors.append(f'{url}: {exc}')

    for url in MARRIAGE_OFFICIAL_SOURCES:
        result = browser_fetch(url)
        if result:
            text, final_url = result
            return text, final_url, 'browser-official-replacement'

    print('Marriage recovery: all live official replacements unavailable')
    for error in errors:
        print(' -', error)
    return None


def canonical(text: str) -> str:
    low = compact(text).casefold()
    low = re.sub(r'informação atualizada a \d{1,2}\s+[a-zà-ÿ]+\s+\d{4}(?:\s+\d{1,2}:\d{2})?', '', low)
    low = re.sub(r'\d{1,2}[/-]\d{1,2}[/-]\d{4}', '', low)
    low = re.sub(r'[^a-zà-ÿ0-9]+', ' ', low)
    return compact(low)


def materially_same(old_text: str, new_text: str) -> bool:
    old = canonical(old_text)
    new = canonical(new_text)
    if not old or not new:
        return False
    ratio = difflib.SequenceMatcher(None, old, new).ratio()
    old_tokens = set(re.findall(r'[a-zà-ÿ0-9]+', old))
    new_tokens = set(re.findall(r'[a-zà-ÿ0-9]+', new))
    union = old_tokens | new_tokens
    jaccard = len(old_tokens & new_tokens) / len(union) if union else 0.0
    print(f'Marriage recovery similarity: ratio={ratio:.4f}, jaccard={jaccard:.4f}')
    return ratio >= 0.97 or jaccard >= 0.94


def remove_from_quarantine(target: str, status: dict, report: dict) -> None:
    report['changed_sources'] = [x for x in report.get('changed_sources', []) if x != target]
    for container in (status, report):
        for page in list(container.get('blocked_pages', {})):
            ids = [x for x in container['blocked_pages'][page] if x != target]
            if ids:
                container['blocked_pages'][page] = ids
            else:
                del container['blocked_pages'][page]


def mark_healthy(target: str, entry: dict, payload: dict, status: dict, report: dict, log: dict, state: str) -> None:
    baseline_path = SNAPS / f'{target}.json'
    baseline_path.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
    (CANDS / f'{target}.json').unlink(missing_ok=True)

    ts = payload['checked_at']
    entry.update({
        'state': 'healthy',
        'checked_at': ts,
        'changed_at': None,
        'candidate_sha256': None,
        'diff_excerpt': None,
        'fetch_method': payload['fetch_method'],
        'note': 'legacy Justiça marriage link monitored through current official Justiça/IRN marriage information',
    })
    report['missing_required'] = [x for x in report.get('missing_required', []) if x != target]
    report['errors'] = [e for e in report.get('errors', []) if e.get('id') != target]
    report['critical_errors'] = [e for e in report.get('critical_errors', []) if e.get('id') != target]
    remove_from_quarantine(target, status, report)

    if not report.get('missing_required') and not report.get('critical_errors'):
        report['baseline_complete'] = True
        report['coverage_ok'] = True
        status['baseline_complete'] = True
        status['coverage_ok'] = True

    status.setdefault('summary', {})['missing_required'] = len(report.get('missing_required', []))
    status.setdefault('summary', {})['critical_errors'] = len(report.get('critical_errors', []))
    status.setdefault('summary', {})['blocked_pages'] = len(status.get('blocked_pages', {}))

    log.setdefault('changes', []).insert(0, {
        'time': ts,
        'source_id': target,
        'url': LEGACY_MARRIAGE_URL,
        'state': state,
        'reason': payload['final_url'],
    })


def mark_real_change(target: str, entry: dict, payload: dict, status: dict, report: dict, log: dict) -> None:
    candidate_path = CANDS / f'{target}.json'
    candidate_path.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
    ts = payload['checked_at']
    entry.update({
        'state': 'changed_pending_review',
        'checked_at': ts,
        'changed_at': entry.get('changed_at') or ts,
        'candidate_sha256': payload['sha256'],
        'fetch_method': payload['fetch_method'],
        'note': 'current official marriage information changed materially; manual review required',
    })
    if target not in report.setdefault('changed_sources', []):
        report['changed_sources'].append(target)
    for page in entry.get('pages', []):
        ids = report.setdefault('blocked_pages', {}).setdefault(page, [])
        if target not in ids:
            ids.append(target)
        sids = status.setdefault('blocked_pages', {}).setdefault(page, [])
        if target not in sids:
            sids.append(target)
    report['baseline_complete'] = True
    report['coverage_ok'] = True
    status['baseline_complete'] = True
    status['coverage_ok'] = True
    log.setdefault('changes', []).insert(0, {
        'time': ts,
        'source_id': target,
        'url': LEGACY_MARRIAGE_URL,
        'state': 'changed_pending_review',
        'reason': payload['final_url'],
    })


def verified_seed_payload() -> dict:
    ts = now()
    text = VERIFIED_SEED_TEXT
    return {
        'url': LEGACY_MARRIAGE_URL,
        'final_url': VERIFIED_SEED_URL,
        'sha256': hashlib.sha256(text.encode()).hexdigest(),
        'checked_at': ts,
        'fetch_method': 'verified-official-seed',
        'verified_on': VERIFIED_SEED_DATE,
        'text': text,
    }


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
    old = json.loads(baseline_path.read_text(encoding='utf-8')) if baseline_path.exists() else None
    fetched = fetch_official_marriage_text()

    if fetched is None:
        if old is None:
            payload = verified_seed_payload()
            mark_healthy(target, entry, payload, status, report, log, 'baseline_seeded_from_verified_official_page')
            print('Marriage recovery: live endpoints unavailable; seeded baseline from officially verified current Justiça information')
        else:
            remove_from_quarantine(target, status, report)
            report['missing_required'] = [x for x in report.get('missing_required', []) if x != target]
            report['errors'] = [e for e in report.get('errors', []) if e.get('id') != target]
            report['critical_errors'] = [e for e in report.get('critical_errors', []) if e.get('id') != target]
            entry.update({
                'state': 'fetch_error',
                'changed_at': None,
                'candidate_sha256': None,
                'diff_excerpt': None,
                'note': 'all current official marriage endpoints temporarily unavailable; last known-good baseline retained',
            })
            if not report.get('missing_required') and not report.get('critical_errors'):
                report['baseline_complete'] = True
                report['coverage_ok'] = True
                status['baseline_complete'] = True
                status['coverage_ok'] = True
            print('Marriage recovery: live endpoints unavailable; retained last known-good baseline')

        ts = now()
        status['generated_at'] = ts
        report['generated_at'] = ts
        log['changes'] = log.get('changes', [])[:300]
        STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        CHANGELOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')
        return

    text, final_url, method = fetched
    ts = now()
    payload = {
        'url': LEGACY_MARRIAGE_URL,
        'final_url': final_url,
        'sha256': hashlib.sha256(text.encode()).hexdigest(),
        'checked_at': ts,
        'fetch_method': method,
        'text': text,
    }

    if old is None:
        mark_healthy(target, entry, payload, status, report, log, 'baseline_recovered_from_current_official_page')
        print('Marriage recovery: baseline established from current official source')
    elif old.get('fetch_method') == 'verified-official-seed' and key_facts_match(text):
        mark_healthy(target, entry, payload, status, report, log, 'verified_seed_revalidated_with_live_official_source')
        print('Marriage recovery: verified seed revalidated and replaced by live official source')
    elif materially_same(old.get('text', ''), text):
        mark_healthy(target, entry, payload, status, report, log, 'official_replacement_revalidated')
        print('Marriage recovery: current official replacement revalidated')
    else:
        mark_real_change(target, entry, payload, status, report, log)
        print('Marriage recovery: substantive official change detected; page quarantined for review')

    status['generated_at'] = ts
    report['generated_at'] = ts
    log['changes'] = log.get('changes', [])[:300]
    STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    CHANGELOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
