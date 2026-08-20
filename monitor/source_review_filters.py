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
REPORT = Path('monitor/report.json')
STATUS = SITE / 'data/source-status.json'
CHANGELOG = SITE / 'data/change-log.json'

ERSE_TARGET = 'src_2b928469124c'
ERSE_MARKER = 'Compare os preços das ofertas comerciais de eletricidade e gás natural'
GOV_QUALIFICATIONS_URL = 'https://www2.gov.pt/pt/inicio/espaco-empresa/qualificacoes-profissionais'
JUSTICA_MARRIAGE_OLD = 'https://justica.gov.pt/Servicos/Iniciar-processo-de-casamento'
JUSTICA_MARRIAGE_FALLBACK = 'https://conservatoria.justica.gov.pt/pt/cidadao/casamento/processo-preliminar-casamento'
UA = 'GuiaMigrantePT-OfficialSourceMonitor/1.3 (+https://guia-migrante-pt.pages.dev/)'

ACCESS_BLOCK_MARKERS = (
    'web page blocked!',
    'the page cannot be displayed',
    'access denied',
    'request blocked',
    'attack id:',
    'message id:',
    'you have been blocked',
    'sorry, you have been blocked',
    'verify you are human',
    'checking your browser before accessing',
)

TEMPORARY_MAINTENANCE_MARKERS = (
    'temporariamente indisponível',
    'temporariamente indisponivel',
    'intervenção técnica programada',
    'intervencao tecnica programada',
    'tente novamente mais tarde',
    'service temporarily unavailable',
    'temporarily unavailable',
    'scheduled maintenance',
)


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def compact(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()


def is_access_block(text: str) -> bool:
    low = compact(text).casefold()
    return any(marker in low for marker in ACCESS_BLOCK_MARKERS)


def is_temporary_maintenance(text: str) -> bool:
    low = compact(text).casefold()
    return any(marker in low for marker in TEMPORARY_MAINTENANCE_MARKERS)


def remove_target_from_quarantine(target: str, status: dict, report: dict):
    report['changed_sources'] = [x for x in report.get('changed_sources', []) if x != target]
    for container in (status, report):
        for key in list(container.get('blocked_pages', {})):
            ids = [x for x in container['blocked_pages'][key] if x != target]
            if ids:
                container['blocked_pages'][key] = ids
            else:
                del container['blocked_pages'][key]


def record_transient(target: str, candidate: dict, status: dict, report: dict, log: dict, reason: str):
    baseline_path = SNAPS / f'{target}.json'
    candidate_path = CANDS / f'{target}.json'
    if not baseline_path.exists():
        return False

    candidate_path.unlink(missing_ok=True)
    entry = status.setdefault('sources', {}).setdefault(target, {})
    entry.update({
        'state': 'fetch_error',
        'checked_at': candidate.get('checked_at') or entry.get('checked_at'),
        'changed_at': None,
        'candidate_sha256': None,
        'diff_excerpt': None,
        'note': reason,
    })
    remove_target_from_quarantine(target, status, report)
    report.setdefault('errors', []).append({
        'id': target,
        'url': entry.get('url') or candidate.get('url'),
        'domain': entry.get('domain'),
        'risk': 'high' if entry.get('required') else 'medium',
        'required': bool(entry.get('required')),
        'had_baseline': True,
        'kind': 'temporary_source_response',
        'error': reason,
    })
    log.setdefault('changes', []).insert(0, {
        'time': now(),
        'source_id': target,
        'url': entry.get('url') or candidate.get('url'),
        'state': 'temporary_source_response_ignored',
        'reason': reason,
    })
    return True


def review_transient_candidates(status: dict, report: dict, log: dict):
    resolved = []
    for candidate_path in list(CANDS.glob('src_*.json')):
        target = candidate_path.stem
        candidate = json.loads(candidate_path.read_text(encoding='utf-8'))
        text = candidate.get('text', '')
        reason = None
        if is_access_block(text):
            reason = 'temporary anti-bot/WAF response ignored; last known-good baseline retained'
        elif is_temporary_maintenance(text):
            reason = 'temporary maintenance/unavailable page ignored; last known-good baseline retained'
        elif target == ERSE_TARGET and ERSE_MARKER not in text and 'cookie' in text.casefold():
            reason = 'ERSE cookie-only render ignored; last known-good simulator baseline retained'
        if reason and record_transient(target, candidate, status, report, log, reason):
            resolved.append(target)

    if resolved:
        print('Transient-source filter cleared:', ', '.join(sorted(set(resolved))))
    else:
        print('Transient-source filter: nothing to clear')


def review_bad_baselines(status: dict, report: dict, log: dict):
    rejected = []
    for baseline_path in list(SNAPS.glob('src_*.json')):
        target = baseline_path.stem
        baseline = json.loads(baseline_path.read_text(encoding='utf-8'))
        text = baseline.get('text', '')
        bad = is_access_block(text) or is_temporary_maintenance(text)
        if target == ERSE_TARGET and ERSE_MARKER not in text and 'cookie' in text.casefold():
            bad = True
        if not bad:
            continue

        baseline_path.unlink(missing_ok=True)
        (CANDS / f'{target}.json').unlink(missing_ok=True)
        entry = status.setdefault('sources', {}).setdefault(target, {})
        entry.update({
            'state': 'baseline_failed',
            'checked_at': baseline.get('checked_at') or entry.get('checked_at'),
            'changed_at': None,
            'candidate_sha256': None,
            'diff_excerpt': None,
            'note': 'transient/access-block page rejected as invalid baseline',
        })
        remove_target_from_quarantine(target, status, report)
        if entry.get('required'):
            missing = set(report.get('missing_required', []))
            missing.add(target)
            report['missing_required'] = sorted(missing)
            report['baseline_complete'] = False
            report['coverage_ok'] = False
        rejected.append(target)

    if rejected:
        log.setdefault('changes', []).insert(0, {
            'time': now(),
            'state': 'invalid_baselines_rejected',
            'source_ids': sorted(set(rejected)),
            'reason': 'temporary WAF/maintenance/cookie-only content cannot be a baseline',
        })
        print('Rejected invalid baselines:', ', '.join(sorted(set(rejected))))


def normalize_erse(text: str) -> str:
    if ERSE_MARKER not in text:
        return ''
    text = text[text.index(ERSE_MARKER):]
    text = re.sub(
        r'Ofertas comerciais \(CSV\) - Atualizado em \d{1,2}-\d{1,2}-\d{4}',
        'Ofertas comerciais (CSV) - Atualizado',
        text,
    )
    return compact(text)


def clear_target(target: str, note: str, candidate: dict, status: dict, report: dict, log: dict | None = None):
    baseline_path = SNAPS / f'{target}.json'
    candidate_path = CANDS / f'{target}.json'
    baseline_path.write_text(json.dumps(candidate, ensure_ascii=False), encoding='utf-8')
    candidate_path.unlink(missing_ok=True)

    entry = status.setdefault('sources', {}).setdefault(target, {})
    entry.update({
        'state': 'healthy',
        'checked_at': candidate.get('checked_at') or entry.get('checked_at'),
        'changed_at': None,
        'candidate_sha256': None,
        'diff_excerpt': None,
        'note': note,
    })
    remove_target_from_quarantine(target, status, report)

    if log is not None:
        log.setdefault('changes', []).insert(0, {
            'time': now(),
            'source_id': target,
            'url': entry.get('url'),
            'state': 'false_positive_resolved',
            'reason': note,
        })


def review_erse(status: dict, report: dict, log: dict):
    candidate_path = CANDS / f'{ERSE_TARGET}.json'
    baseline_path = SNAPS / f'{ERSE_TARGET}.json'
    if not candidate_path.exists() or not baseline_path.exists():
        return

    candidate = json.loads(candidate_path.read_text(encoding='utf-8'))
    baseline = json.loads(baseline_path.read_text(encoding='utf-8'))
    cand_norm = normalize_erse(candidate.get('text', ''))
    base_norm = normalize_erse(baseline.get('text', ''))
    if not cand_norm or not base_norm or cand_norm != base_norm:
        return

    clear_target(
        ERSE_TARGET,
        'ERSE simulator substantive content unchanged after normalization',
        candidate,
        status,
        report,
        log,
    )
    print('ERSE filter: normalized false positive cleared')


def canonical_gov_qualifications(text: str) -> str:
    low = text.casefold()
    start_marker = 'algumas profissões são regulamentadas'
    start = low.find(start_marker)
    if start < 0:
        return ''
    text = text[start:]
    low = text.casefold()
    cut_positions = []
    for marker in ('licenças de parentalidade', 'entidade responsável'):
        pos = low.find(marker)
        if pos > 0:
            cut_positions.append(pos)
    if cut_positions:
        text = text[:min(cut_positions)]
    text = text.casefold()
    text = re.sub(r'[\u2013\u2014]', '-', text)
    text = re.sub(r'[\s\.;:,]+', ' ', text)
    return text.strip()


def review_gov_qualifications(status: dict, report: dict, log: dict):
    for target, entry in list(status.get('sources', {}).items()):
        if entry.get('url') != GOV_QUALIFICATIONS_URL or entry.get('state') != 'changed_pending_review':
            continue
        candidate_path = CANDS / f'{target}.json'
        baseline_path = SNAPS / f'{target}.json'
        if not candidate_path.exists() or not baseline_path.exists():
            continue

        candidate = json.loads(candidate_path.read_text(encoding='utf-8'))
        baseline = json.loads(baseline_path.read_text(encoding='utf-8'))
        old = canonical_gov_qualifications(baseline.get('text', ''))
        new = canonical_gov_qualifications(candidate.get('text', ''))
        if not old or not new:
            continue

        ratio = difflib.SequenceMatcher(None, old, new).ratio()
        old_tokens = set(re.findall(r'[a-zà-ÿ0-9]+', old))
        new_tokens = set(re.findall(r'[a-zà-ÿ0-9]+', new))
        union = old_tokens | new_tokens
        jaccard = len(old_tokens & new_tokens) / len(union) if union else 0.0
        if ratio < 0.97 or jaccard < 0.97:
            print(f'gov.pt qualifications remains pending (ratio={ratio:.4f}, jaccard={jaccard:.4f})')
            continue

        clear_target(
            target,
            f'gov.pt migration/formatting accepted after semantic equivalence check (ratio={ratio:.4f}, jaccard={jaccard:.4f})',
            candidate,
            status,
            report,
            log,
        )
        print(f'gov.pt qualifications false positive cleared (ratio={ratio:.4f}, jaccard={jaccard:.4f})')


def extract_html_text(content: bytes) -> str:
    soup = BeautifulSoup(content, 'html.parser')
    for tag in soup(['script', 'style', 'noscript', 'svg', 'form', 'nav', 'header', 'footer']):
        tag.decompose()
    node = soup.find('main') or soup.find('article') or soup.body or soup
    return '\n'.join(
        line for line in (compact(x) for x in node.get_text('\n').splitlines())
        if len(line) > 1
    )


def review_justica_marriage_redirect(status: dict, report: dict, log: dict):
    target = None
    entry = None
    for source_id, source_entry in status.get('sources', {}).items():
        if source_entry.get('url') == JUSTICA_MARRIAGE_OLD:
            target = source_id
            entry = source_entry
            break
    if not target or not entry:
        return

    baseline_path = SNAPS / f'{target}.json'
    if baseline_path.exists():
        return

    try:
        response = requests.get(
            JUSTICA_MARRIAGE_FALLBACK,
            timeout=(10, 35),
            allow_redirects=True,
            headers={'User-Agent': UA, 'Accept': 'text/html,*/*;q=0.8'},
        )
        response.raise_for_status()
        text = extract_html_text(response.content)
        if len(text) < 100 or is_access_block(text) or is_temporary_maintenance(text):
            raise RuntimeError('fallback returned non-content/interstitial page')
    except Exception as exc:
        print('Justiça marriage fallback unavailable:', exc)
        return

    ts = now()
    payload = {
        'url': JUSTICA_MARRIAGE_OLD,
        'final_url': response.url,
        'sha256': hashlib.sha256(text.encode()).hexdigest(),
        'checked_at': ts,
        'fetch_method': 'official-redirect-fallback',
        'text': text,
    }
    baseline_path.write_text(json.dumps(payload, ensure_ascii=False), encoding='utf-8')
    (CANDS / f'{target}.json').unlink(missing_ok=True)
    entry.update({
        'state': 'healthy',
        'checked_at': ts,
        'changed_at': None,
        'candidate_sha256': None,
        'diff_excerpt': None,
        'fetch_method': 'official-redirect-fallback',
        'note': 'legacy Justiça marriage URL now redirects to official Conservatória Justiça service',
    })
    report['missing_required'] = [x for x in report.get('missing_required', []) if x != target]
    report['errors'] = [e for e in report.get('errors', []) if e.get('id') != target]
    report['critical_errors'] = [e for e in report.get('critical_errors', []) if e.get('id') != target]
    if not report.get('missing_required') and not report.get('critical_errors'):
        report['baseline_complete'] = True
        report['coverage_ok'] = True
    log.setdefault('changes', []).insert(0, {
        'time': ts,
        'source_id': target,
        'url': JUSTICA_MARRIAGE_OLD,
        'state': 'baseline_recovered_via_official_redirect',
        'reason': JUSTICA_MARRIAGE_FALLBACK,
    })
    print('Justiça marriage baseline recovered via official redirect destination')


def main():
    status = json.loads(STATUS.read_text(encoding='utf-8'))
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    log = json.loads(CHANGELOG.read_text(encoding='utf-8')) if CHANGELOG.exists() else {'version': 1, 'changes': []}

    review_transient_candidates(status, report, log)
    review_bad_baselines(status, report, log)
    review_erse(status, report, log)
    review_gov_qualifications(status, report, log)
    review_justica_marriage_redirect(status, report, log)

    status.setdefault('summary', {})['blocked_pages'] = len(status.get('blocked_pages', {}))
    status['generated_at'] = now()
    report['generated_at'] = now()
    log['changes'] = log.get('changes', [])[:300]

    STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    CHANGELOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
