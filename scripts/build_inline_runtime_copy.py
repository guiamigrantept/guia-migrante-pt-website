#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup
from langdetect import detect

from auto_translate_untranslated_copy import make_batches, translate_batch

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
DATA = SITE / 'data'

QUOTE_RE = re.compile(r"(['\"])((?:\\.|(?!\1).)*)\1", re.S)
TEMPLATE_RE = re.compile(r"`((?:\\.|[^`])*)`", re.S)
EXPR_RE = re.compile(r"\$\{[^{}]*\}")

STRONG_PT = {
    'apagar','abrir','ajuda','alterar','atividade','ativado','aumentado','cancelar','checklist',
    'concluir','contacto','continuar','contraste','copiado','dados','data','datas','dispositivo',
    'documentos','encontrámos','escolha','expira','expirado','fechar','fonte','fontes','guardar',
    'informação','início','instalar','mensagem','nacionalidade','navegação','normal','obter','opção',
    'passos','pesquisar','pesquisa','portuguesa','procure','renovação','residência','resultado','rever',
    'roteiro','segurança','selecionar','situação','social','tamanho','texto','tratar','utente','validade',
    'voltar','dias','meses','anos','hoje','amanhã','faltam','local','locais','oficial','oficiais'
}

CODEISH_RE = re.compile(
    r"(^[.#\[\]/]|\.html(?:[#?]|$)|https?://|mailto:|tel:|^[a-z0-9_-]+(?:\.[a-z0-9_-]+)+$|"
    r"^(click|input|change|submit|open|close|show|hidden|active|selected|loading|error|success)$)",
    re.I,
)


def clean_js_text(value: str) -> str:
    value = value.replace('\\n', ' ').replace('\\t', ' ')
    value = value.replace('\\"', '"').replace("\\'", "'")
    value = html.unescape(value)
    return ' '.join(value.split()).strip()


def looks_human_portuguese(text: str) -> bool:
    text = clean_js_text(text)
    if len(text) < 3 or not any(ch.isalpha() for ch in text):
        return False
    if CODEISH_RE.search(text):
        return False
    if any(token in text for token in ('querySelector', 'getElementById', 'localStorage', 'dataset.', 'classList')):
        return False
    low = text.casefold()
    words = set(re.findall(r"[a-záàâãéêíóôõúç]+", low))
    if words & STRONG_PT:
        return True
    if re.search(r'[áàâãéêíóôõúç]', low):
        return True
    if len(text) >= 18 and ' ' in text:
        try:
            return detect(text) == 'pt'
        except Exception:
            return False
    return False


def visible_fragments(raw: str) -> list[str]:
    raw = EXPR_RE.sub(' ', raw)
    if '<' in raw and '>' in raw:
        soup = BeautifulSoup(raw, 'html.parser')
        parts = [clean_js_text(x) for x in soup.stripped_strings]
    else:
        parts = [clean_js_text(x) for x in re.split(r'[\r\n]+', raw)]
    return [x for x in parts if looks_human_portuguese(x)]


def collect_script_phrases() -> list[str]:
    phrases = set()
    for page in sorted(SITE.glob('*.html')):
        soup = BeautifulSoup(page.read_text(encoding='utf-8'), 'html.parser')
        for script in soup.find_all('script'):
            if script.get('src'):
                continue
            code = script.string or script.get_text('\n')
            if not code.strip():
                continue
            for match in QUOTE_RE.finditer(code):
                for part in visible_fragments(match.group(2)):
                    phrases.add(part)
            for match in TEMPLATE_RE.finditer(code):
                for part in visible_fragments(match.group(1)):
                    phrases.add(part)
    return sorted(phrases, key=lambda x: (len(x), x))


def translate_all(strings: list[str], target: str) -> dict[str, str]:
    out = {}
    for batch in make_batches(strings, max_chars=2200):
        out.update(translate_batch(batch, target))
    return {k: v.strip() for k, v in out.items() if v and v.strip()}


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    cfg = json.loads((DATA / 'locales.json').read_text(encoding='utf-8'))
    targets = [x['code'] for x in cfg.get('locales', []) if x.get('status') == 'live' and x.get('code') not in {'pt', 'en'}]
    phrases = collect_script_phrases()
    if len(phrases) < 10:
        raise SystemExit(f'Inline runtime phrase extraction unexpectedly small: {len(phrases)}')
    print(f'Collected {len(phrases)} human-facing Portuguese inline-script phrase(s).')

    for code in targets:
        translated = translate_all(phrases, code)
        missing = [x for x in phrases if x not in translated]
        if missing:
            raise SystemExit(f'{code}: missing {len(missing)} inline runtime translation(s)')
        payload = {
            'version': 1,
            'source_locale': 'pt',
            'locale': code,
            'phrases': translated,
        }
        target = DATA / f'inline-runtime-{code}.json'
        target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
        print(f'Generated {target} with {len(translated)} phrase(s).')


if __name__ == '__main__':
    main()
