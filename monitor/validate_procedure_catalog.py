#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

SITE = Path("site")
CATALOG = SITE / "data/procedure-catalog.json"
FACTS = SITE / "data/facts.json"
SOURCES = Path("monitor/sources.json")
OUT = Path("monitor/procedure-coverage.json")


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    facts = json.loads(FACTS.read_text(encoding="utf-8"))
    sources = json.loads(SOURCES.read_text(encoding="utf-8"))

    known_facts = set((facts.get("facts") or {}).keys())
    by_page: dict[str, list[dict]] = {}
    for src in sources.get("sources", []):
        for page in src.get("pages", []):
            # Source registry contains translated pages too; policy catalogue is canonical PT.
            canonical = page.split("/", 1)[-1] if "/" in page else page
            by_page.setdefault(canonical, []).append(src)

    errors: list[str] = []
    warnings: list[str] = []
    coverage: dict[str, dict] = {}

    for proc_id, proc in (catalog.get("procedures") or {}).items():
        pages = proc.get("pages") or []
        domains = set(proc.get("official_domains") or [])
        auto_fact_ids = proc.get("auto_fact_ids") or []
        if not pages:
            errors.append(f"{proc_id}: no pages configured")
            continue

        missing_facts = [fid for fid in auto_fact_ids if fid not in known_facts]
        if missing_facts:
            errors.append(f"{proc_id}: unknown auto facts: {', '.join(missing_facts)}")

        page_rows = []
        for page in pages:
            path = SITE / page
            if not path.exists():
                errors.append(f"{proc_id}: missing canonical page {page}")
                page_rows.append({"page": page, "exists": False, "official_sources": 0})
                continue

            linked = by_page.get(page, [])
            matching = [
                s for s in linked
                if urlparse(s.get("url", "")).netloc.lower() in domains
            ]
            if not matching:
                errors.append(f"{proc_id}: {page} has no monitored official source from its approved domains")
            elif len(matching) < 2 and proc.get("priority") == "critical":
                warnings.append(f"{proc_id}: {page} has only one approved monitored source")

            page_rows.append({
                "page": page,
                "exists": True,
                "official_sources": len(matching),
                "source_ids": sorted({s.get("id") for s in matching if s.get("id")}),
            })

        coverage[proc_id] = {
            "priority": proc.get("priority"),
            "pages": page_rows,
            "auto_fact_ids": auto_fact_ids,
            "review_required_for": proc.get("review_required_for") or [],
        }

    payload = {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "procedures": coverage,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"procedure catalogue: {len(coverage)} procedures, {len(errors)} errors, {len(warnings)} warnings")
    for item in errors:
        print("ERROR:", item)
    for item in warnings:
        print("WARNING:", item)

    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
