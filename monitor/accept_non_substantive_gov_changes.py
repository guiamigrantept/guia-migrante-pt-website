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

MANUALLY_REVIEWED_CANDIDATES = {
    'src_1b8b2c1bcde6': '9b52a805d31bdb93394a1673a8b3011215121f0a93c51c9ab49d098dd919e690',
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def compact_lines(text: str) -> list[str]:
    lines = [re.sub(r'\s+', ' ', x).strip() for x in (text or '').splitlines()]
    return [x for x in lines if x]


def normalize_toc_noise(lines: list[str]) -> list[str]:
    return [x for x in lines if x.casefold() not in {'guias relacionados', 'related guides'}]


def strip_related_guide_cards(lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(lines):
        low = lines[i].casefold()
        if low in {'guias relacionados', 'related guides'}:
            i += 1
            continue
        if low.startswith(('migrantes:', 'migrants:')):
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
    out: list[str] = []
    i = 0
    ignored_labels = {
        'realizar serviço', 'alterar dados', 'realizar servico',
        'start service', 'change data',
        'pedir niss',
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


def canonical_aima_news_article(text: str) -> list[str]:
    lines = compact_lines(text)
    for i in range(len(lines) - 2, -1, -1):
        if lines[i].casefold() == 'notícias' and lines[i + 1].casefold() == 'ver tudo':
            return lines[:i]
    return []


def is_aima_news_teasers_only(old_text: str, new_text: str) -> bool:
    old = canonical_aima_news_article(old_text)
    new = canonical_aima_news_article(new_text)
    return bool(old and new and old == new)


def canonical_erse_supplier_change(text: str) -> list[str]:
    marker = 'os consumidores têm o direito a mudar de comercializador'
    lines = compact_lines(text)
    start = next((i for i, line in enumerate(lines) if line.casefold().startswith(marker)), None)
    if start is None:
        return []
    core = lines[start:]
    out: list[str] = []
    i = 0
    while i < len(core):
        low = core[i].casefold()
        if low in {'data de atualização:', 'data de atualização', 'data de atualizacao:', 'data de atualizacao'}:
            i += 1
            if i < len(core) and re.fullmatch(r'\d{1,2}[./-]\d{1,2}[./-]\d{4}', core[i]):
                i += 1
            continue
        out.append(core[i])
        i += 1
    return out


def is_erse_supplier_change_wrapper_only(old_text: str, new_text: str) -> bool:
    old = canonical_erse_supplier_change(old_text)
    new = canonical_erse_supplier_change(new_text)
    return bool(old and new and old == new)


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
        print('non-substantive source filter: report/status unavailable')
        return

    report = json.loads(REPORT.read_text(encoding='utf-8'))
    status = json.loads(STATUS.read_text(encoding='utf-8'))
    changelog = json.loads(CHANGELOG.read_text(encoding='utf-8')) if CHANGELOG.exists() else {'version': 1, 'changes': []}
    accepted = []

    for source_id in list(report.get('changed_sources', [])):
        entry = status.get('sources', {}).get(source_id, {})
        url = entry.get('url', '')
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

        if url.startswith(('https://www.gov.pt/', 'https://gov.pt/')):
            if '/guias/' in url and is_related_guides_only(old_text, new_text):
                reason = 'only gov.pt related-guide/navigation cards changed; substantive guide text is unchanged'
                note = 'gov.pt related-guides/navigation-only change accepted automatically; substantive guide text unchanged'
            elif '/servicos/' in url and is_service_metadata_only(old_text, new_text):
                reason = 'only gov.pt service UI label/update-date metadata changed; substantive service guidance is unchanged'
                note = 'gov.pt service metadata-only change accepted automatically; substantive service guidance unchanged'

        if reason is None and url.startswith(('https://aima.gov.pt/pt/noticias/', 'https://www.aima.gov.pt/pt/noticias/')):
            if is_aima_news_teasers_only(old_text, new_text):
                reason = 'only AIMA related-news teaser cards changed; the monitored article body is unchanged'
                note = 'AIMA related-news teaser-only change accepted automatically; article body unchanged'

        if reason is None and url == 'https://www.erse.pt/consumidores-de-energia/destaques/mudanca-de-comercializador':
            if is_erse_supplier_change_wrapper_only(old_text, new_text):
                reason = 'ERSE page chrome/update-date changed; supplier-switching guidance is unchanged'
                note = 'ERSE wrapper/date-only change accepted automatically; substantive supplier-switching guidance unchanged'

        if reason is None:
            reviewed_sha = MANUALLY_REVIEWED_CANDIDATES.get(source_id)
            if reviewed_sha and candidate.get('sha256') == reviewed_sha:
                reason = (
                    'editorial review 2026-09-06: gov.pt simplified the physical complaints-book purchase page; '
                    'Guia consumer claims remain supported and no removed price/order detail is published'
                )
                note = 'manually reviewed exact official-source revision; current Guia guidance remains valid'

        if reason is None:
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
            'state': 'non_substantive_change_accepted' if source_id not in MANUALLY_REVIEWED_CANDIDATES else 'editorial_review_accepted',
            'reason': reason,
        })
        accepted.append(source_id)

    STATUS.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    CHANGELOG.write_text(json.dumps(changelog, ensure_ascii=False, indent=2), encoding='utf-8')
    print('non-substantive/review filter accepted:', ', '.join(accepted) if accepted else 'none')


if __name__ == '__main__':
    main()
