#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

SITE = Path('site')
SNAPS = Path('monitor/snapshots')
CANDS = Path('monitor/candidates')
REPORT = Path('monitor/report.json')
STATUS = SITE / 'data/source-status.json'

TARGET = 'src_2b928469124c'  # ERSE price simulator
MARKER = 'Compare os preços das ofertas comerciais de eletricidade e gás natural'


def normalize(text: str) -> str:
    if MARKER not in text:
        return ''
    text = text[text.index(MARKER):]
    text = re.sub(r'Ofertas comerciais \(CSV\) - Atualizado em \d{1,2}-\d{1,2}-\d{4}',
                  'Ofertas comerciais (CSV) - Atualizado', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def main():
    candidate_path = CANDS / f'{TARGET}.json'
    baseline_path = SNAPS / f'{TARGET}.json'
    if not candidate_path.exists():
        print('ERSE filter: no candidate to review')
        return

    candidate = json.loads(candidate_path.read_text(encoding='utf-8'))
    baseline = json.loads(baseline_path.read_text(encoding='utf-8')) if baseline_path.exists() else None
    cand_norm = normalize(candidate.get('text', ''))
    base_norm = normalize((baseline or {}).get('text', ''))

    # Accept only when the candidate contains the stable ERSE simulator content and
    # either the original baseline was only cookie-banner noise or the normalized
    # substantive content is unchanged (for example only the daily CSV update date changed).
    if not cand_norm or (base_norm and cand_norm != base_norm):
        print('ERSE filter: substantive change remains pending review')
        return

    baseline_path.write_text(json.dumps(candidate, ensure_ascii=False), encoding='utf-8')
    candidate_path.unlink(missing_ok=True)

    status = json.loads(STATUS.read_text(encoding='utf-8'))
    report = json.loads(REPORT.read_text(encoding='utf-8'))

    entry = status.setdefault('sources', {}).setdefault(TARGET, {})
    entry.update({
        'state': 'healthy',
        'changed_at': None,
        'candidate_sha256': None,
        'diff_excerpt': None,
        'note': 'ERSE simulator render normalized; cookie-banner/daily offer-date noise ignored',
    })

    for key in list(status.get('blocked_pages', {})):
        ids = [x for x in status['blocked_pages'][key] if x != TARGET]
        if ids:
            status['blocked_pages'][key] = ids
        else:
            del status['blocked_pages'][key]

    report['changed_sources'] = [x for x in report.get('changed_sources', []) if x != TARGET]
    for key in list(report.get('blocked_pages', {})):
        ids = [x for x in report['blocked_pages'][key] if x != TARGET]
        if ids:
            report['blocked_pages'][key] = ids
        else:
            del report['blocked_pages'][key]

    STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print('ERSE filter: false positive cleared and candidate promoted to baseline')


if __name__ == '__main__':
    main()
