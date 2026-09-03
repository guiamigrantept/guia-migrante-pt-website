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


def strip_related_guide_cards(lines: list[str]) -> list[str]:
    """Remove gov.pt related-guide cards wherever they appear in the extracted text."""
    out: list[str] = []
    i = 0
    while i < len(lines):
        low = lines[i].casefold()
        if low in {'guias relacionados', 'related guides'}:
            i += 1
            continue
        if low.startswith(('migrantes:', 'migrants:')):
            # A related guide card is normally title + short description + 'Ver guia'.
            j = i + 1
            found = False
            while j < min(i + 5, len(lines)):
                if lines[j].casefold() in {'ver guia', 'view guide'}:
                    found = True
                    j += 1
                    break
                j += 1
            if found:
                i = j
                continue
        out.append(lines[i])
        i += 1
    return out


def normalize_service_metadata(lines: list[str]) -> list[str]:
    """Ignore gov.pt service UI labels and the displayed 'Atualizado em' date."""
    out: list[str] = []
    i = 0
    ignored_labels = {
        'realizar serviço', 'alterar dados', 'realizar servico', 'alterar dados',
        'start service', 'change data'
    }
    while i < len(lines):
        low = lines[i].casefold()
        if low in ignored_labels:
            i += 1
            continue
        if low in {'atualizado em', 'updated on'}:
            i += 1
            if i < len(lines) and re.fullmatch(r'\d{1,2}[./-]\d{1,2}[./-]\d{4}', lines[i]):
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return out


def is_related_guides_only(old_text: str, new_text: str) -> bool:
    old = strip_related_guide_cards(normalize_toc_noise(compact_lines(old_text)))
    new = strip_related_guide_cards(normalize_toc_noise(compact_lines(new_text)))
    return old == new


def is_service_metadata_only(old_text: str, new_text: str) -> bool:
    old = normalize_service_metadata(compact_lines(old_text))
    new = normalize_service_metadata(compact_lines(new_text))
    return old == new


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
        if not (url.startswith('https://www.gov.pt/') or url.startswith('https://gov.pt/')):
            continue
        baseline_path = SNAPS / f'{source_id}.json'
        candidate_path = CANDS / f'{source_id}.json'
        if not baseline_path.exists() or not candidate_path.exists():
            continue

        baseline = json.loads(baseline_path.read_text(encoding='utf-8'))
        candidate = json.loads(candidate_path.read_text(encoding='utf-8'))
        old_text = baseline.get('text', '')
        new_text = candidate.get('text', '')

        reason = None
        note = None
        if '/guias/' in url and is_related_guides_only(old_text, new_text):
            reason = 'only gov.pt related-guide/navigation cards changed; substantive guide text is unchanged'
            note = 'gov.pt related-guides/navigation-only change accepted automatically; substantive guide text unchanged'
        elif '/servicos/' in url and is_service_metadata_only(old_text, new_text):
            reason = 'only gov.pt service UI label/update-date metadata changed; substantive service guidance is unchanged'
            note = 'gov.pt service metadata-only change accepted automatically; substantive service guidance unchanged'
        else:
            continue

        baseline_path.write_text(json.dumps(candidate, ensure_ascii=False), encoding='utf-8')
        candidate_path.unlink(missing_ok=True)
        entry.update({
            'state': 'healthy',
            'checked_at': candidate.get('checked_at') or entry.get('checked_at'),
            'changed_at': None,
            'candidate_sha256': None,
            'diff_excerpt': None,
            'note': note,
        })
        remove_from_quarantine(source_id, status, report)
        changelog.setdefault('changes', []).insert(0, {
            'time': now(),
            'source_id': source_id,
            'url': url,
            'state': 'non_substantive_change_accepted',
            'reason': reason,
        })
        accepted.append(source_id)

    STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    CHANGELOG.write_text(json.dumps(changelog, ensure_ascii=False, indent=2), encoding='utf-8')
    print('non-substantive gov.pt filter accepted:', ', '.join(accepted) if accepted else 'none')


if __name__ == '__main__':
    main()
