#!/usr/bin/env python3
from __future__ import annotations

import difflib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SNAPS = Path('monitor/snapshots')
CANDS = Path('monitor/candidates')
REPORT = Path('monitor/report.json')
STATUS = Path('site/data/source-status.json')
CHANGELOG = Path('site/data/change-log.json')

TARGET_URL = 'https://www2.gov.pt/pt/inicio/espaco-empresa/qualificacoes-profissionais'


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def canonical(text: str) -> str:
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


def main():
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    status = json.loads(STATUS.read_text(encoding='utf-8'))
    log = json.loads(CHANGELOG.read_text(encoding='utf-8'))
    resolved = []

    for source_id, entry in list(status.get('sources', {}).items()):
        if entry.get('url') != TARGET_URL or entry.get('state') != 'changed_pending_review':
            continue
        baseline_path = SNAPS / f'{source_id}.json'
        candidate_path = CANDS / f'{source_id}.json'
        if not baseline_path.exists() or not candidate_path.exists():
            continue

        baseline = json.loads(baseline_path.read_text(encoding='utf-8'))
        candidate = json.loads(candidate_path.read_text(encoding='utf-8'))
        old = canonical(baseline.get('text', ''))
        new = canonical(candidate.get('text', ''))
        if not old or not new:
            continue

        ratio = difflib.SequenceMatcher(None, old, new).ratio()
        old_tokens = set(re.findall(r'[a-zà-ÿ0-9]+', old))
        new_tokens = set(re.findall(r'[a-zà-ÿ0-9]+', new))
        union = old_tokens | new_tokens
        jaccard = len(old_tokens & new_tokens) / len(union) if union else 0.0

        # This rule is deliberately narrow: exact legacy gov.pt qualifications URL,
        # same substantive text after stripping migration UI/related-guide noise.
        if ratio < 0.985 or jaccard < 0.985:
            continue

        baseline_path.write_text(candidate_path.read_text(encoding='utf-8'), encoding='utf-8')
        candidate_path.unlink(missing_ok=True)
        ts = now()
        status['sources'][source_id] = {
            **entry,
            'state': 'healthy',
            'checked_at': ts,
            'changed_at': None,
            'candidate_sha256': None,
            'diff_excerpt': None,
            'note': 'gov.pt page migration/formatting change accepted after semantic equivalence check',
        }
        resolved.append(source_id)
        log.setdefault('changes', []).insert(0, {
            'time': ts,
            'source_id': source_id,
            'url': TARGET_URL,
            'state': 'false_positive_resolved',
            'reason': 'gov.pt migration/formatting; substantive content equivalent',
            'similarity': round(ratio, 6),
            'token_jaccard': round(jaccard, 6),
        })

    if resolved:
        changed = [x for x in report.get('changed_sources', []) if x not in resolved]
        blocked = {}
        for page, ids in report.get('blocked_pages', {}).items():
            keep = [x for x in ids if x not in resolved]
            if keep:
                blocked[page] = keep
        report['changed_sources'] = changed
        report['blocked_pages'] = blocked
        status['blocked_pages'] = blocked
        status.setdefault('summary', {})['blocked_pages'] = len(blocked)
        report['known_false_positives_resolved'] = resolved
        report['generated_at'] = now()
        status['generated_at'] = now()
        log['changes'] = log.get('changes', [])[:300]
        REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
        CHANGELOG.write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding='utf-8')

    print(json.dumps({'resolved': resolved}, ensure_ascii=False))


if __name__ == '__main__':
    main()
