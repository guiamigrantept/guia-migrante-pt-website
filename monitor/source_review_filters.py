#!/usr/bin/env python3
from __future__ import annotations

import difflib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SITE = Path('site')
SNAPS = Path('monitor/snapshots')
CANDS = Path('monitor/candidates')
REPORT = Path('monitor/report.json')
STATUS = SITE / 'data/source-status.json'
CHANGELOG = SITE / 'data/change-log.json'

ERSE_TARGET = 'src_2b928469124c'
ERSE_MARKER = 'Compare os preços das ofertas comerciais de eletricidade e gás natural'
GOV_QUALIFICATIONS_URL = 'https://www2.gov.pt/pt/inicio/espaco-empresa/qualificacoes-profissionais'

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


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def is_access_block(text: str) -> bool:
    low = re.sub(r'\s+', ' ', text).casefold()
    return any(marker in low for marker in ACCESS_BLOCK_MARKERS)


def remove_target_from_quarantine(target: str, status: dict, report: dict):
    report['changed_sources'] = [x for x in report.get('changed_sources', []) if x != target]

    for container in (status, report):
        for key in list(container.get('blocked_pages', {})):
            ids = [x for x in container['blocked_pages'][key] if x != target]
            if ids:
                container['blocked_pages'][key] = ids
            else:
                del container['blocked_pages'][key]


def review_access_blocks(status: dict, report: dict, log: dict):
    resolved = []

    # A WAF/security interstitial is not an official-content change. If we already
    # have a valid baseline, discard only the blocked candidate and keep the last
    # known-good baseline. This prevents temporary anti-bot pages from quarantining
    # user-facing guidance.
    for candidate_path in list(CANDS.glob('src_*.json')):
        target = candidate_path.stem
        candidate = json.loads(candidate_path.read_text(encoding='utf-8'))
        if not is_access_block(candidate.get('text', '')):
            continue
        baseline_path = SNAPS / f'{target}.json'
        if not baseline_path.exists():
            continue

        candidate_path.unlink(missing_ok=True)
        entry = status.setdefault('sources', {}).setdefault(target, {})
        entry.update({
            'state': 'fetch_error',
            'checked_at': candidate.get('checked_at') or entry.get('checked_at'),
            'changed_at': None,
            'candidate_sha256': None,
            'diff_excerpt': None,
            'note': 'temporary access-block/WAF response ignored; last known-good baseline retained',
        })
        remove_target_from_quarantine(target, status, report)
        error = {
            'id': target,
            'url': entry.get('url') or candidate.get('url'),
            'domain': entry.get('domain'),
            'risk': 'high' if entry.get('required') else 'medium',
            'required': bool(entry.get('required')),
            'had_baseline': True,
            'kind': 'access_blocked',
            'error': 'Temporary anti-bot/WAF response ignored; previous baseline retained.',
        }
        if not any(e.get('id') == target and e.get('kind') == 'access_blocked' for e in report.setdefault('errors', [])):
            report['errors'].append(error)
        resolved.append(target)

    # Never allow a first-time WAF/interstitial page to become a baseline. If one
    # slipped through the fetch layer, remove it and force coverage to remain
    # incomplete until a genuine official page can be captured.
    for baseline_path in list(SNAPS.glob('src_*.json')):
        target = baseline_path.stem
        baseline = json.loads(baseline_path.read_text(encoding='utf-8'))
        if not is_access_block(baseline.get('text', '')):
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
            'note': 'access-block/WAF page rejected as invalid baseline',
        })
        remove_target_from_quarantine(target, status, report)
        if entry.get('required'):
            missing = set(report.get('missing_required', []))
            missing.add(target)
            report['missing_required'] = sorted(missing)
            report['baseline_complete'] = False
            report['coverage_ok'] = False
        resolved.append(target)

    if resolved:
        log.setdefault('changes', []).insert(0, {
            'time': now(),
            'state': 'access_block_false_positive_resolved',
            'source_ids': sorted(set(resolved)),
            'reason': 'temporary WAF/access-block content rejected as monitoring noise',
        })
        print('Access-block filter cleared:', ', '.join(sorted(set(resolved))))
    else:
        print('Access-block filter: no blocked-page artifacts found')


def normalize_erse(text: str) -> str:
    if ERSE_MARKER not in text:
        return ''
    text = text[text.index(ERSE_MARKER):]
    text = re.sub(r'Ofertas comerciais \(CSV\) - Atualizado em \d{1,2}-\d{1,2}-\d{4}',
                  'Ofertas comerciais (CSV) - Atualizado', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


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
    if not candidate_path.exists():
        print('ERSE filter: no candidate to review')
        return

    candidate = json.loads(candidate_path.read_text(encoding='utf-8'))
    baseline = json.loads(baseline_path.read_text(encoding='utf-8')) if baseline_path.exists() else None
    cand_norm = normalize_erse(candidate.get('text', ''))
    base_norm = normalize_erse((baseline or {}).get('text', ''))

    if not cand_norm or (base_norm and cand_norm != base_norm):
        print('ERSE filter: substantive change remains pending review')
        return

    clear_target(
        ERSE_TARGET,
        'ERSE simulator render normalized; cookie-banner/daily offer-date noise ignored',
        candidate, status, report, log,
    )
    print('ERSE filter: false positive cleared and candidate promoted to baseline')


def canonical_gov_qualifications(text: str) -> str:
    # Compare only the substantive qualifications guidance. The old www2.gov.pt
    # page and the new www.gov.pt guide have different navigation, update-date and
    # related-guide components around the same official guidance.
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

        # Deliberately narrow: exact legacy gov.pt qualifications URL and the
        # same bounded substantive guidance. Minor punctuation/layout differences
        # are accepted, but material wording changes remain quarantined.
        if ratio < 0.97 or jaccard < 0.97:
            print(f'gov.pt qualifications filter: substantive change remains pending (ratio={ratio:.4f}, jaccard={jaccard:.4f})')
            continue

        clear_target(
            target,
            f'gov.pt page migration/formatting accepted after semantic equivalence check (ratio={ratio:.4f}, jaccard={jaccard:.4f})',
            candidate, status, report, log,
        )
        print(f'gov.pt qualifications filter: false positive cleared (ratio={ratio:.4f}, jaccard={jaccard:.4f})')


def main():
    status = json.loads(STATUS.read_text(encoding='utf-8'))
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    log = json.loads(CHANGELOG.read_text(encoding='utf-8')) if CHANGELOG.exists() else {'version': 1, 'changes': []}

    review_access_blocks(status, report, log)
    review_erse(status, report, log)
    review_gov_qualifications(status, report, log)

    status.setdefault('summary', {})['blocked_pages'] = len(status.get('blocked_pages', {}))
    status['generated_at'] = now()
    report['generated_at'] = now()
    log['changes'] = log.get('changes', [])[:300]

    STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    CHANGELOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
