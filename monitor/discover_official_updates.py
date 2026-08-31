#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
import truststore
from bs4 import BeautifulSoup

truststore.inject_into_ssl()

OUT = Path("site/data/official-updates.json")
REPORT = Path("monitor/discovery-report.json")
UA = "GuiaMigrantePT-OfficialUpdateDiscovery/2.0 (+https://guia-migrante-pt.pages.dev/)"

SOURCES = [
    {"name": "AIMA", "index": "https://aima.gov.pt/pt/noticias", "host": "aima.gov.pt", "prefixes": ["/pt/noticias/"]},
    {"name": "gov.pt", "index": "https://www.gov.pt/noticias", "host": "www.gov.pt", "prefixes": ["/noticias/"]},
    {"name": "Justiça", "index": "https://justica.gov.pt/Noticias", "host": "justica.gov.pt", "prefixes": ["/Noticias/"]},
    {"name": "IRN", "index": "https://irn.justica.gov.pt/Noticias-do-IRN", "host": "irn.justica.gov.pt", "prefixes": ["/Noticias-do-IRN/"]},
]

RELEVANT_TERMS = {
    "aima", "residência", "residencia", "renovação", "renovacao", "cartão", "cartao", "título", "titulo",
    "familiares", "familiar", "documentos", "documento", "portal", "contacto", "loja", "nacionalidade",
    "visto", "vistos", "asilo", "proteção", "protecao", "trabalho", "emprego", "estudante", "estudantes",
    "escola", "bebé", "bebe", "menor", "menores", "integração", "integracao", "integrar", "cplp",
    "reagrupamento", "taxa", "taxas", "imigrante", "imigrantes", "migrante", "migrantes", "estrangeiro",
    "estrangeiros", "registo civil", "nascimento", "segurança social", "seguranca social", "nif", "niss", "sns"
}


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def compact(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def chrome() -> str | None:
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        path = shutil.which(name)
        if path:
            return path
    return None


def fetch_html(url: str) -> str:
    err = None
    try:
        response = requests.get(url, timeout=(10, 35), allow_redirects=True, headers={"User-Agent": UA, "Accept": "text/html,*/*;q=0.8"})
        response.raise_for_status()
        if len(response.text) >= 500:
            return response.text
        err = RuntimeError("official index returned incomplete HTML")
    except Exception as exc:
        err = exc

    browser = chrome()
    if not browser:
        raise RuntimeError(f"primary fetch failed: {err}; browser fallback unavailable")
    proc = subprocess.run(
        [browser, "--headless=new", "--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--disable-background-networking", "--dump-dom", url],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=70,
    )
    raw = proc.stdout.decode("utf-8", errors="replace")
    if proc.returncode or len(raw) < 500:
        raise RuntimeError(f"primary fetch failed: {err}; browser fallback failed")
    return raw


def nearest_container(anchor):
    node = anchor
    for _ in range(7):
        node = getattr(node, "parent", None)
        if node is None:
            break
        if getattr(node, "name", None) in {"article", "li", "section"}:
            return node
        if getattr(node, "name", None) == "div" and node.find(["h2", "h3", "h4"]):
            return node
    return anchor.parent


def extract_title(anchor, container) -> str:
    text = compact(anchor.get_text(" ", strip=True))
    if len(text) >= 8 and text.casefold() not in {"ler mais", "read more", "saber mais", "ver mais"}:
        return text
    heading = container.find(["h1", "h2", "h3", "h4"]) if container else None
    return compact(heading.get_text(" ", strip=True)) if heading else text


def extract_date(container) -> str:
    text = compact(container.get_text(" ", strip=True)) if container else ""
    for pattern in (r"\b(\d{1,2})[./-](\d{1,2})[./-](\d{4})\b", r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b"):
        match = re.search(pattern, text)
        if not match:
            continue
        a, b, c = map(int, match.groups())
        if pattern.startswith("\\b(\\d{4}"):
            year, month, day = a, b, c
        else:
            day, month, year = a, b, c
        if 2000 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
            return f"{year:04d}-{month:02d}-{day:02d}"
    return ""


def is_relevant(title: str, context: str = "") -> bool:
    low = f"{title} {context}".casefold()
    return any(term in low for term in RELEVANT_TERMS)


def mapped_pages(title: str) -> list[str]:
    low = title.casefold()
    pages = {"atualizacoes.html"}
    if any(x in low for x in ("renov", "residên", "residen", "cartão", "cartao", "título", "titulo", "portal", "visto")):
        pages.update({"legalizacao.html", "ue-familiares.html"})
    if any(x in low for x in ("familiar", "família", "familia", "reagrup")):
        pages.update({"familia.html", "ue-familiares.html"})
    if any(x in low for x in ("casamento", "menor", "bebé", "bebe", "nascid", "registo civil")):
        pages.update({"familia.html", "registos-civis.html"})
    if "nacionalidade" in low:
        pages.add("nacionalidade.html")
    if any(x in low for x in ("trabalho", "emprego", "construção", "construcao", "integrar", "integração", "integracao")):
        pages.update({"trabalho.html", "integracao.html"})
    if any(x in low for x in ("estud", "escola", "ensino")):
        pages.update({"estudantes.html", "escola-familias.html"})
    if any(x in low for x in ("asilo", "proteção internacional", "protecao internacional")):
        pages.add("asilo.html")
    if any(x in low for x in ("proteção temporária", "protecao temporaria", "ucrânia", "ucrania")):
        pages.add("protecao-temporaria.html")
    if any(x in low for x in ("loja", "contacto", "atendimento")):
        pages.add("contactos.html")
    if "cplp" in low:
        pages.add("cplp.html")
    if any(x in low for x in ("nif", "fiscal")):
        pages.add("nif.html")
    if any(x in low for x in ("niss", "segurança social", "seguranca social")):
        pages.add("niss.html")
    if "sns" in low:
        pages.add("sns.html")
    return sorted(pages)


def summaries(source: str, title: str) -> tuple[str, str]:
    return (
        f"Nova informação oficial publicada por {source} com potencial impacto em procedimentos ou direitos de pessoas migrantes em Portugal. Confirme os detalhes na fonte oficial.",
        f"New official information published by {source} that may affect procedures or rights for migrants in Portugal. Check the official source for details.",
    )


def parse_source(config: dict, html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    found, seen = [], set()
    for anchor in soup.find_all("a", href=True):
        href = urljoin(config["index"], anchor.get("href", ""))
        parsed = urlparse(href)
        if parsed.netloc.lower() != config["host"]:
            continue
        if not any(parsed.path.startswith(prefix) for prefix in config["prefixes"]):
            continue
        clean = parsed._replace(query="", fragment="").geturl()
        if clean in seen:
            continue
        container = nearest_container(anchor)
        title = extract_title(anchor, container)
        context = compact(container.get_text(" ", strip=True))[:1200] if container else ""
        if len(title) < 8 or not is_relevant(title, context):
            continue
        date = extract_date(container)
        summary_pt, summary_en = summaries(config["name"], title)
        seen.add(clean)
        found.append({
            "source": config["name"], "title": title, "date": date, "url": clean,
            "pages": mapped_pages(title), "summary_pt": summary_pt, "summary_en": summary_en,
        })
    return found


def main() -> None:
    previous = {}
    if OUT.exists():
        try:
            previous = json.loads(OUT.read_text(encoding="utf-8"))
        except Exception:
            previous = {}
    previous_items = previous.get("updates", []) or []
    previous_urls = {x.get("url") for x in previous_items if x.get("url")}
    previous_by_source: dict[str, list[dict]] = {}
    for item in previous_items:
        previous_by_source.setdefault(item.get("source") or "", []).append(item)

    all_items: list[dict] = []
    source_report = []
    successful = 0
    for config in SOURCES:
        try:
            html = fetch_html(config["index"])
            items = parse_source(config, html)
            if not items:
                raise RuntimeError("no relevant entries extracted")
            successful += 1
            all_items.extend(items)
            source_report.append({"source": config["name"], "ok": True, "count": len(items), "error": None})
        except Exception as exc:
            # Retain last known-good items for a failed index so one outage never erases the feed.
            retained = previous_by_source.get(config["name"], [])
            all_items.extend(retained)
            source_report.append({"source": config["name"], "ok": False, "count": len(retained), "error": str(exc)})

    dedup = {}
    for item in all_items:
        if item.get("url"):
            dedup[item["url"]] = item
    updates = list(dedup.values())
    updates.sort(key=lambda item: (item.get("date") or "0000-00-00", item.get("source") or ""), reverse=True)
    updates = updates[:40]

    if not successful and not updates:
        raise RuntimeError("all official update discovery sources failed and no previous feed exists")

    generated = now()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"version": 2, "generated_at": generated, "sources": [x["index"] for x in SOURCES], "updates": updates}, ensure_ascii=False, indent=2), encoding="utf-8")

    new_updates = [x for x in updates if x.get("url") not in previous_urls] if previous_urls else []
    ok = successful == len(SOURCES)
    report = {
        "generated_at": generated,
        "ok": ok,
        "partial_ok": successful > 0,
        "sources_total": len(SOURCES),
        "sources_ok": successful,
        "sources": source_report,
        "count": len(updates),
        "new_updates": new_updates,
        "error": None if ok else "one or more official update indexes failed; last known-good entries retained",
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"official update discovery: {successful}/{len(SOURCES)} indexes OK; {len(updates)} relevant entries; {len(new_updates)} new")


if __name__ == "__main__":
    main()
