#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

SNAPS = Path('monitor/snapshots')
CANDS = Path('monitor/candidates')
REPORT = Path('monitor/report.json')
STATUS = Path('site/data/source-status.json')
CHANGELOG = Path('site/data/change-log.json')


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def compact_lines(text: str) -> list[str]:
    lines = [re.sub(r'\s+', ' ', x).strip() for x in (text or '').splitlines()]
    return [x for x in lines if x]


def normalize_toc_noise(lines: list[str]) -> list[str]:
    return [x for x in lines if x.casefold() not in {'guias relacionados', 'related guides'}]


def is_related_guides_only(old_text: str, new_text: str) -> bool:
    old = normalize_toc_noise(compact_lines(old_text))
    new = normalize_toc_noise(compact_lines(new_text))
    if len(new) <= len(old) or new[:len(old)] != old:
        return False
    suffix = new[len(old):]
    if not suffix or len(suffix) > 40:
        return False
    low = ' '.join(suffix).casefold()
    # gov.pt related-guide cards normally append titles/descriptions plus “Ver guia”.
    return ('ver guia' in low or 'view guide' in low) and any(
        token in low for token in ('migrantes:', 'migrants:', 'guia', 'guide')
    )


def remove_from_quarantine(source_id: str, status: dict, report: dict) -> None:
    report['changed_sources'] = [x for x in report.get('changed_sources', []) if x != source_id]
    for container in (status, report):
        blocked = container.get('blocked_pages', {})
        for page in list(blocked):
            ids = [x for x in blocked[page] if x != source_id]
            if ids:
                blocked[page] = ids
            else:
                del blocked[page]


def main() -> None:
    if not REPORT.exists() or not STATUS.exists():
        print('non-substantive gov.pt filter: report/status unavailable')
        return

    report = json.loads(REPORT.read_text(encoding='utf-8'))
    status = json.loads(STATUS.read_text(encoding='utf-8'))
    changelog = json.loads(CHANGELOG.read_text(encoding='utf-8')) if CHANGELOG.exists() else {'version': 1, 'changes': []}
    accepted = []

    for source_id in list(report.get('changed_sources', [])):
        entry = status.get('sources', {}).get(source_id, {})
        url = entry.get('url', '')
        if not (url.startswith('https://www.gov.pt/guias/') or url.startswith('https://gov.pt/guias/')):
            continue
        baseline_path = SNAPS / f'{source_id}.json'
        candidate_path = CANDS / f'{source_id}.json'
        if not baseline_path.exists() or not candidate_path.exists():
            continue

        baseline = json.loads(baseline_path.read_text(encoding='utf-8'))
        candidate = json.loads(candidate_path.read_text(encoding='utf-8'))
        if not is_related_guides_only(baseline.get('text', ''), candidate.get('text', '')):
            continue

        baseline_path.write_text(json.dumps(candidate, ensure_ascii=False), encoding='utf-8')
        candidate_path.unlink(missing_ok=True)
        entry.update({
            'state': 'healthy',
            'checked_at': candidate.get('checked_at') or entry.get('checked_at'),
            'changed_at': None,
            'candidate_sha256': None,
            'diff_excerpt': None,
            'note': 'gov.pt related-guides/navigation-only addition accepted automatically; substantive guide text unchanged',
        })
        remove_from_quarantine(source_id, status, report)
        changelog.setdefault('changes', []).insert(0, {
            'time': now(),
            'source_id': source_id,
            'url': url,
            'state': 'non_substantive_change_accepted',
            'reason': 'only gov.pt related-guide/navigation cards were appended; substantive monitored text is unchanged',
        })
        accepted.append(source_id)

    STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    CHANGELOG.write_text(json.dumps(changelog, ensure_ascii=False, indent=2), encoding='utf-8')
    print('non-substantive gov.pt filter accepted:', ', '.join(accepted) if accepted else 'none')


if __name__ == '__main__':
    main()
