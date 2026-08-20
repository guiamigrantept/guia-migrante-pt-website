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


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


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

    for key in list(status.get('blocked_pages', {})):
        ids = [x for x in status['blocked_pages'][key] if x != target]
        if ids:
            status['blocked_pages'][key] = ids
        else:
            del status['blocked_pages'][key]

    report['changed_sources'] = [x for x in report.get('changed_sources', []) if x != target]
    for key in list(report.get('blocked_pages', {})):
        ids = [x for x in report['blocked_pages'][key] if x != target]
        if ids:
            report['blocked_pages'][key] = ids
        else:
            del report['blocked_pages'][key]

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
    out = []
    skip_exact = {
        'voltar ao índice de conteúdos',
        'guias práticos',
        'nesta página',
        'acesso a profissões regulamentadas',
        'entidade responsável',
    }
    lines = [re.sub(r'\s+', ' ', x).strip() for x in text.splitlines()]
    i = 0
    while i < len(lines):
        s = lines[i]
        low = s.casefold()
        if low == 'guias relacionados':
            break
        if low in skip_exact:
            i += 1
            continue
        if low == 'atualizado em':
            i += 2
            continue
        if re.fullmatch(r'\d{1,2}/\d{1,2}/\d{4}', s):
            i += 1
            continue
        s = re.sub(r'[\s\.;:,]+$', '', s).casefold()
        if s:
            out.append(s)
        i += 1
    return '\n'.join(out)


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

        # Deliberately narrow: this exact legacy gov.pt page moved to the new gov.pt
        # guide layout. Only accept automatically when the substantive text remains
        # virtually identical after stripping layout headings, related-guide cards,
        # punctuation-only changes and the page's own update date.
        if ratio < 0.985 or jaccard < 0.985:
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
