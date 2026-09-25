#!/usr/bin/env python3
from pathlib import Path
from html import escape
import re

SITE=Path("site")
BASE="https://guia-migrante-pt.pages.dev"
PRIVATE_NAMES={"admin-mensagens.html","admin-estatisticas.html","404.html"}

def extract(pattern, text):
    m=re.search(pattern,text,re.I|re.S)
    return re.sub(r"<[^>]+>","",m.group(1)).strip() if m else ""

def upsert_tag(html, matcher, tag):
    rx=re.compile(matcher,re.I|re.S)
    if rx.search(html):
        return rx.sub(tag,html,count=1)
    return html.replace("</head>",f"{tag}\n</head>",1)

def meta_property(html,key,value):
    tag=f'<meta property="{key}" content="{escape(value,quote=True)}">'
    return upsert_tag(html,rf'<meta\b(?=[^>]*\bproperty=["\']{re.escape(key)}["\'])[^>]*>',tag)

def meta_name(html,key,value):
    tag=f'<meta name="{key}" content="{escape(value,quote=True)}">'
    return upsert_tag(html,rf'<meta\b(?=[^>]*\bname=["\']{re.escape(key)}["\'])[^>]*>',tag)

changed=0
for fp in SITE.rglob("*.html"):
    html=fp.read_text(encoding="utf-8")
    original=html
    title=extract(r"<title[^>]*>(.*?)</title>",html)
    desc=extract(r'<meta\b(?=[^>]*\bname=["\']description["\'])[^>]*\bcontent=["\']([^"\']*)["\'][^>]*>',html)
    if not desc:
        desc=extract(r'<meta\b(?=[^>]*\bcontent=["\']([^"\']*)["\'])[^>]*\bname=["\']description["\'][^>]*>',html)
    canonical=extract(r'<link\b(?=[^>]*\brel=["\']canonical["\'])[^>]*\bhref=["\']([^"\']+)["\'][^>]*>',html)
    if not canonical:
        canonical=extract(r'<link\b(?=[^>]*\bhref=["\']([^"\']+)["\'])[^>]*\brel=["\']canonical["\'][^>]*>',html)

    if title:
        html=meta_property(html,"og:title",title)
        html=meta_name(html,"twitter:title",title)
    if desc:
        html=meta_property(html,"og:description",desc)
        html=meta_name(html,"twitter:description",desc)
    if canonical:
        html=meta_property(html,"og:url",canonical)
    html=meta_property(html,"og:type","website")
    html=meta_property(html,"og:site_name","Guia Migrante PT")
    html=meta_property(html,"og:image",f"{BASE}/logo-guia-migrante.png")
    html=meta_name(html,"twitter:card","summary")
    html=meta_name(html,"twitter:image",f"{BASE}/logo-guia-migrante.png")

    if fp.name in PRIVATE_NAMES:
        html=meta_name(html,"robots","noindex,nofollow")

    if html!=original:
        fp.write_text(html,encoding="utf-8")
        changed+=1

print(f"SEO/social metadata normalized on {changed} HTML files.")
