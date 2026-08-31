#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPORT = Path("monitor/report.json")
DISCOVERY = Path("monitor/discovery-report.json")
COVERAGE = Path("monitor/procedure-coverage.json")
OUT = Path("site/data/monitor-health.json")


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load(path: Path, fallback: dict) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def main() -> None:
    report = load(REPORT, {})
    discovery = load(DISCOVERY, {"ok": False, "error": "missing discovery report"})
    coverage = load(COVERAGE, {"ok": False, "errors": ["missing procedure coverage report"]})

    critical_errors = report.get("critical_errors") or []
    blocked_pages = report.get("blocked_pages") or {}
    errors = report.get("errors") or []
    repeated_failures = [e for e in errors if int(e.get("failure_count") or 0) >= 3]

    if not report.get("coverage_ok") or not coverage.get("ok") or critical_errors:
        state = "critical"
    elif not discovery.get("ok") or blocked_pages or repeated_failures:
        state = "degraded"
    else:
        state = "healthy"

    payload = {
        "version": 1,
        "generated_at": now(),
        "state": state,
        "schedule_hours": 3,
        "warning_after_hours": 6,
        "critical_after_hours": 12,
        "source_coverage_ok": bool(report.get("coverage_ok")),
        "procedure_coverage_ok": bool(coverage.get("ok")),
        "required_sources": int(report.get("required_sources") or 0),
        "missing_required": report.get("missing_required") or [],
        "blocked_pages": sorted(blocked_pages.keys()),
        "critical_error_count": len(critical_errors),
        "source_error_count": len(errors),
        "repeated_source_failure_count": len(repeated_failures),
        "discovery_ok": bool(discovery.get("ok")),
        "discovery_error": discovery.get("error"),
        "dre_rss_ok": bool(report.get("dre_rss_ok")),
        "dre_alert_count": len(report.get("dre_rss_alerts") or []),
        "fact_updates": report.get("fact_updates") or [],
        "policy": {
            "objective_facts": "automatic",
            "ambiguous_legal_or_procedural_changes": "quarantine_and_review",
            "publication": "qa_before_deploy"
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"monitor health: {state}; blocked={len(blocked_pages)}; errors={len(errors)}; repeated={len(repeated_failures)}")


if __name__ == "__main__":
    main()
